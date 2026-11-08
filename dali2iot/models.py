"""Typed data models for the Lunatone Dali-2 IoT gateway API.

Every entity returned or accepted by the gateway is a `dataclass`
mixed with :class:`Model`, which gives it an automatic JSON
:meth:`~Model.to_dict` / :meth:`~Model.from_dict` round-trip.

**Naming conventions**

- Python field names are ``snake_case``; JSON keys default to ``camelCase``
  (so ``dali_types`` ↔ ``daliTypes``).
- The auto-converter doesn't know about acronyms, so the few fields that
  embed RGB / WAF / XY (in :class:`ControlData`) carry an explicit
  ``field(metadata={"json": "..."})`` override.
- A small number of API endpoints use ``snake_case`` JSON keys
  (``automatic_time``, ``dali_ping``, ``ip_address``, etc.). Those fields
  also carry an override so they round-trip verbatim.

**Read- vs write-side**

OpenAPI splits some entities into multiple schemas (e.g. ``ZoneModel``,
``ZoneResponse``, ``UpdateZoneModel``). Where the fields overlap heavily
they are merged into a single class with optional fields; where the
shapes genuinely differ (mail config), the read and write classes are
kept separate (e.g. :class:`MailConfig` vs :class:`MailConfigInput`).

**Firmware versions**

The models follow ``openapi.json`` from gateway firmware v1.18.7/1.4.6.
Fields and models that only older firmware returns (:attr:`Device.scenes`,
the mail settings) are kept so the library still works against it.
"""

from __future__ import annotations

import dataclasses
import types
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Self, Union, cast, get_args, get_origin, get_type_hints

__all__ = [
    "RGB",
    "WAF",
    "XY",
    "ActionTypes",
    "ActiveDays",
    "ActiveMonths",
    "ActivePeriod",
    "ActiveWeekDays",
    "Circadian",
    "CircadianCurve",
    "CircadianStep",
    "ControlData",
    "Dali16Command",
    "Dali24Command",
    "DaliBus",
    "DaliLineStatus",
    "DaliSensorAddress",
    "DateTime",
    "Device",
    "DeviceStatus",
    "DeviceTarget",
    "DeviceType",
    "DiagnosticsMaintenance",
    "DimmableWithFade",
    "EnergyReport",
    "Ethernet",
    "EthernetSettings",
    "EventTriggerAction",
    "Info",
    "InfoUpdate",
    "Kelvin",
    "KelvinWithFade",
    "LineScan",
    "LineScanState",
    "LineStatus",
    "Location",
    "MailConfig",
    "MailConfigInput",
    "MailSettings",
    "MailSettingsInput",
    "Model",
    "NotificationSettings",
    "RGBWithFade",
    "Scan",
    "ScanState",
    "SceneWithFade",
    "Scheduler",
    "SchedulerAction",
    "SchedulerRecallModes",
    "SchedulerTime",
    "Sensor",
    "SensorAddressType",
    "SensorType",
    "Sequence",
    "SequenceStep",
    "SequencerAction",
    "Settings",
    "Signature",
    "SmtpSecurity",
    "StartScan",
    "StartupMode",
    "StatusQueryConfig",
    "TestNotificationSettings",
    "TimeZones",
    "TriggerAction",
    "TriggerActionSource",
    "TriggerActionSourceType",
    "WAFWithFade",
    "WithFadeTime",
    "XYWithFade",
    "YnDescriptor",
    "YnDeviceInfo",
    "Zone",
]

_NONE_TYPE = type(None)


def _to_camel(name: str) -> str:
    """Convert a ``snake_case`` Python attribute name to ``camelCase`` JSON.

    Trailing underscores (used to escape Python keywords) are stripped.
    Acronyms aren't capitalised — fields that need that (e.g. ``colorRGB``)
    must use a ``json`` metadata override.
    """
    name = name.rstrip("_")
    head, *rest = name.split("_")
    return head + "".join(p[:1].upper() + p[1:] for p in rest)


def _json_name(f: dataclasses.Field[object]) -> str:
    """Return the JSON key for a dataclass field, honouring ``metadata={"json": ...}``."""
    override = f.metadata.get("json")
    return cast(str, override) if isinstance(override, str) else _to_camel(f.name)


def _serialize(value: object) -> object:
    """Recursively convert a Python value into something JSON-serialisable.

    Handles :class:`Model` instances, :class:`enum.Enum` members, and
    nested lists / dicts. Other values pass through unchanged.
    """
    if value is None:
        return None
    if isinstance(value, Model):
        return value.to_dict()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _serialize(v) for k, v in value.items()}
    return value


def _deserialize(annotation: object, value: object) -> object:
    """Recursively coerce ``value`` into the type described by ``annotation``.

    Resolves ``Optional[X]`` / ``X | None``, ``list[X]``, ``dict[str, X]``,
    enums and nested :class:`Model` subclasses. Anything that can't be
    matched is returned unchanged so the caller gets predictable types.
    """
    if value is None:
        return None
    origin = get_origin(annotation)
    if origin is Union or origin is types.UnionType:
        non_none = [a for a in get_args(annotation) if a is not _NONE_TYPE]
        if non_none:
            return _deserialize(non_none[0], value)
        return value
    if origin in (list, tuple):
        args = get_args(annotation)
        item_t: object = args[0] if args else object
        if isinstance(value, list):
            return [_deserialize(item_t, v) for v in value]
        return value
    if origin is dict:
        args = get_args(annotation)
        if len(args) == 2 and isinstance(value, dict):
            val_t = args[1]
            return {str(k): _deserialize(val_t, v) for k, v in value.items()}
        return value
    if isinstance(annotation, type):
        if issubclass(annotation, Enum):
            return annotation(value)
        if dataclasses.is_dataclass(annotation) and isinstance(value, dict):
            from_dict = getattr(annotation, "from_dict", None)
            if callable(from_dict):
                return from_dict(value)
    return value


class Model:
    """Mixin that gives any ``@dataclass`` JSON serialisation against the API.

    Subclasses get :meth:`to_dict` and :meth:`from_dict` for free. The
    conversion uses :func:`dataclasses.fields` and :func:`typing.get_type_hints`
    at runtime, so nested :class:`Model` subclasses, enums, lists and dicts
    are handled recursively.

    The serializer drops ``None`` and empty collections so partial-update
    bodies don't accidentally clear server-side fields. A field whose
    metadata sets ``"keep_empty": True`` sends an empty collection anyway,
    for the few places where ``[]`` or ``{}`` means something.
    """

    def to_dict(self) -> dict[str, object]:
        """Render this dataclass as the JSON payload the gateway expects.

        Fields whose value is ``None`` or an empty collection are omitted,
        except empty collections in fields marked ``keep_empty``.
        Returns:
            A new ``dict`` with camelCase keys (or the override from each
            field's metadata) and recursively serialised values.
        """
        out: dict[str, object] = {}
        for f in fields(cast(object, self)):  # type: ignore[arg-type]
            value = getattr(self, f.name)
            if value is None:
                continue
            if isinstance(value, (list, dict)) and not value and not f.metadata.get("keep_empty"):
                continue
            out[_json_name(f)] = _serialize(value)
        return out

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """Build an instance from a parsed JSON object.

        Unknown keys are ignored; missing keys keep the dataclass default.
        Nested types are constructed recursively via :func:`_deserialize`.

        Args:
            data: Parsed JSON object as returned by :mod:`httpx`.

        Returns:
            A populated instance of the calling subclass.
        """
        hints = get_type_hints(cls)
        kwargs: dict[str, object] = {}
        for f in fields(cls):  # type: ignore[arg-type]
            for key in (_json_name(f), f.name):
                if key in data:
                    kwargs[f.name] = _deserialize(hints[f.name], data[key])
                    break
        return cls(**kwargs)


# ---------- enums ----------


class DeviceType(str, Enum):
    """Kind of target a control or trigger refers to."""

    BROADCAST = "broadcast"
    """Every device on the bus."""

    GROUP = "group"
    """A configured DALI group."""

    DEVICE = "device"
    """A single addressable device."""

    ZONE = "zone"
    """A zone (logical collection of devices)."""

    DALI_GEAR = "daliGear"
    """DALI control gear. Added in firmware 1.18; the spec doesn't describe it further."""


class TriggerActionSourceType(str, Enum):
    """Source kinds that can fire a :class:`TriggerAction`."""

    DEVICE = "device"
    """Trigger from a device known to the gateway (use ``id``)."""

    GROUP = "group"
    """Trigger from a gateway-managed group (use ``id``)."""

    BROADCAST = "broadcast"
    """Trigger from broadcast commands."""

    D16GEAR = "d16gear"
    """Trigger from raw DALI gear addressed on the bus (use ``address`` + ``line``)."""

    D16GROUP = "d16group"
    """Trigger from a raw DALI group on the bus (use ``address`` + ``line``)."""


class ActionTypes(str, Enum):
    """The kind of action a sequence step or scheduler action carries."""

    FEATURES = "features"
    """A feature payload (dim level, color, scene recall, etc.)."""


class SchedulerRecallModes(str, Enum):
    """How a :class:`Scheduler` interprets its ``recall_time``."""

    TIME_OF_DAY = "timeOfDay"
    """Fire at a fixed wall-clock time."""

    BEFORE_SUNRISE = "beforeSunrise"
    """Fire ``recall_time`` before local sunrise."""

    AFTER_SUNRISE = "afterSunrise"
    """Fire ``recall_time`` after local sunrise."""

    BEFORE_SUNSET = "beforeSunset"
    """Fire ``recall_time`` before local sunset."""

    AFTER_SUNSET = "afterSunset"
    """Fire ``recall_time`` after local sunset."""


class ScanState(str, Enum):
    """Lifecycle state of a DALI bus scan (see :class:`Scan`)."""

    NOT_STARTED = "not started"
    """No scan has been started since the gateway booted."""

    CANCELLED = "cancelled"
    """A scan was running and was aborted via ``cancel_scan``."""

    DONE = "done"
    """The most recent scan completed successfully."""

    ADDRESSING = "addressing"
    """Devices are being addressed (mid-scan)."""

    IN_PROGRESS = "in progress"
    """A scan is currently running."""

    BUS_ERROR = "bus error"
    """The scan stopped because of a bus error."""


class LineScanState(str, Enum):
    """Scan state of one DALI line, reported in :attr:`LineScan.scan_state`."""

    IDLE = "idle"
    """The line isn't being scanned."""

    CANCELLED = "cancelled"
    """The scan was cancelled."""

    SCANNING = "scanning"
    """The line is being scanned."""

    ADDRESSING = "addressing"
    """Devices on the line are being addressed."""

    DONE = "done"
    """The line's scan finished."""

    SKIPPED = "skipped"
    """The line was left out of the scan."""

    ERROR = "error"
    """The line's scan failed."""


class LineStatus(str, Enum):
    """Health of a DALI bus line, reported in :class:`DaliBus` and :class:`DaliLineStatus`."""

    OK = "ok"
    """Line is operating normally."""

    LOW_POWER = "lowPower"
    """The line is power-starved — devices may be unreliable."""

    NO_POWER = "noPower"
    """The line has lost power; no devices are reachable."""

    NOT_REACHABLE = "notReachable"
    """The gateway can't reach the line."""


class StartupMode(str, Enum):
    """Mode the gateway application started in, reported in :attr:`Info.startup_mode`."""

    NORMAL = "normal"
    """Normal operation."""

    MINIMAL = "minimal"
    """Reduced start-up mode."""


class SensorType(str, Enum):
    """What a :class:`Sensor` measures."""

    UNKNOWN = "unknown"
    """Not identified."""

    TEMPERATURE = "temperature"
    """Temperature."""

    AIR_HUMIDITY = "airHumidity"
    """Relative air humidity."""

    AIR_PRESSURE = "airPressure"
    """Air pressure."""

    E_CO2 = "eCO2"
    """Equivalent CO₂."""

    VOC = "VOC"
    """Volatile organic compounds."""

    AIR_QUALITY = "airQuality"
    """Air quality index."""

    LIGHT = "light"
    """Illuminance."""

    OCCUPANCY = "occupancy"
    """Occupancy / presence."""


class SensorAddressType(str, Enum):
    """Where a :class:`Sensor` lives."""

    INTERNAL = "internal"
    """Built into the gateway."""

    DALI = "dali"
    """A DALI input device; see :attr:`Sensor.dali_sensor_address`."""


class SmtpSecurity(str, Enum):
    """SMTP transport security used by mail notifications."""

    NONE = "none"
    """Plain SMTP, no encryption."""

    SSL_TLS = "sslTls"
    """SMTPS — TLS established before the SMTP handshake."""

    START_TLS = "startTls"
    """STARTTLS — TLS upgraded during the SMTP handshake."""


# ---------- core ----------


@dataclass
class Signature(Model):
    """Optimistic-concurrency token returned with most read responses.

    Echoes the gateway's view of the resource at fetch time so clients can
    detect when state has moved on.
    """

    timestamp: float = 0.0
    """Server-side wall-clock timestamp (seconds since epoch)."""

    counter: int = 0
    """Monotonically increasing counter; bumps on every state change."""


@dataclass
class DeviceTarget(Model):
    """Reference to a target — ``{"type": ..., "id": ...}``.

    Used by :class:`Zone`, :class:`Scheduler`, :class:`Circadian` and
    :class:`TriggerAction` to point at the things they affect. The
    OpenAPI spec calls this ``DeviceModel``.
    """

    type: DeviceType | None = None
    """Kind of thing this target points at."""

    id: int | None = None
    """Identifier of the device / group / zone, scoped to ``type``."""


@dataclass
class DeviceStatus(Model):
    """DALI status flags of a device, as last read by the gateway (``DeviceStatusModel``).

    The flags reflect the gateway's last status query, so they can be stale
    when periodic status queries are off (see :class:`StatusQueryConfig`).
    """

    raw: int | None = None
    """The raw DALI status byte."""

    control_gear_failure: bool | None = None
    """The control gear reports a failure."""

    lamp_failure: bool | None = None
    """The lamp (light source) reports a failure."""

    lamp_on: bool | None = None
    """The lamp is on."""

    limit_error: bool | None = None
    """The last requested level was outside the min/max limits."""

    fade_running: bool | None = None
    """A fade is in progress."""

    reset_state: bool | None = None
    """The device is in its reset state."""

    is_unaddressed: bool | None = None
    """The device has no short address."""

    power_cycle_seen: bool | None = None
    """The device has been power-cycled since this flag was last cleared."""


@dataclass
class Device(Model):
    """A DALI device known to the gateway.

    Merges the OpenAPI ``DeviceBaseModel`` (returned in lists) and
    ``DeviceResponseModel`` (returned for a single device) into one type.
    :attr:`time_signature` is only populated by the latter.
    """

    id: int = 0
    """Stable numeric identifier assigned at discovery time."""

    name: str = ""
    """Human-readable label, editable via :meth:`Client.update_device`."""

    type: str = ""
    """Gear type string (``"led"``, ``"emergency"``, etc.)."""

    features: dict[str, object] = field(default_factory=dict)
    """Feature map keyed by feature name (``dimmable``, ``colorRGB`` …).

    Values are heterogeneous — consult the gateway's feature reference for
    each one's payload.
    """

    scenes: list[dict[str, object]] = field(default_factory=list)
    """Stored DALI scenes — feature/value snapshots indexed by scene number.

    Only older firmware includes this; firmware 1.18 dropped it from device
    responses. Use :meth:`Client.get_device_scenes` instead.
    """

    groups: list[int] = field(default_factory=list)
    """DALI group IDs this device belongs to."""

    address: int = 0
    """DALI short address on the bus."""

    line: int = 0
    """DALI line (bus index) the device sits on."""

    dali_types: list[int] = field(default_factory=list)
    """DALI device types this gear implements (DALI-2 part numbers)."""

    time_signature: Signature | None = None
    """Concurrency token, only populated on single-device fetches."""

    available: bool | None = None
    """Whether the device answered the gateway recently."""

    status: DeviceStatus | None = None
    """DALI status flags from the gateway's last status query."""


# ---------- color shapes (shared across color* / dimmable* control fields) ----------


@dataclass
class RGB(Model):
    """RGB color triple. Set :attr:`dimmable` to also send brightness.

    Reused for both the ``colorRGB`` (no dimmable) and ``dimmableRGB``
    (with brightness) variants on :class:`ControlData`.
    """

    r: float = 0.0
    """Red channel, ``0.0``–``1.0``."""

    g: float = 0.0
    """Green channel, ``0.0``–``1.0``."""

    b: float = 0.0
    """Blue channel, ``0.0``–``1.0``."""

    dimmable: float | None = None
    """Brightness in percent (``0.0``–``100.0``). ``None`` = colour-only."""

    activate: bool | None = None
    """Colour-only variants: ``False`` = store the colour without activating it.

    The gateway defaults to ``True``. Not used with :attr:`dimmable`.
    """


@dataclass
class WAF(Model):
    """White / Amber / Free-color triple for tunable-white-plus fixtures.

    Like :class:`RGB`, the same shape covers ``colorWAF`` and
    ``dimmableWAF`` — set :attr:`dimmable` to switch.
    """

    w: float = 0.0
    """White channel, ``0.0``–``1.0``."""

    a: float = 0.0
    """Amber channel, ``0.0``–``1.0``."""

    f: float = 0.0
    """Free-color channel, ``0.0``–``1.0``."""

    dimmable: float | None = None
    """Brightness in percent. ``None`` = colour-only."""

    activate: bool | None = None
    """Colour-only variants: ``False`` = store the colour without activating it.

    The gateway defaults to ``True``. Not used with :attr:`dimmable`.
    """


@dataclass
class XY(Model):
    """CIE x/y chromaticity coordinates."""

    x: float = 0.0
    """CIE 1931 x coordinate."""

    y: float = 0.0
    """CIE 1931 y coordinate."""

    dimmable: float | None = None
    """Brightness in percent. ``None`` = colour-only."""


@dataclass
class Kelvin(Model):
    """Color temperature with optional brightness (``dimmableKelvin``)."""

    kelvin: float = 4000.0
    """Color temperature in kelvin."""

    dimmable: float | None = None
    """Brightness in percent. ``None`` = colour-only."""


# ---------- one-off fades (the ``*WithFade`` control fields) ----------
#
# The spec presents these as a fade for that one command. Whether the
# gateway leaves the device's stored fade time unchanged afterwards isn't
# documented.


@dataclass
class DimmableWithFade(Model):
    """Brightness with a one-off fade (``dimmableWithFade``)."""

    dim_value: float = 0.0
    """Brightness in percent (``0.0``–``100.0``)."""

    fade_time: float | None = None
    """Fade time for this command, in seconds."""


@dataclass
class WithFadeTime(Model):
    """Just a one-off fade time (``gotoLastActiveWithFade``)."""

    fade_time: float | None = None
    """Fade time for this command, in seconds."""


@dataclass
class SceneWithFade(Model):
    """Scene recall with a one-off fade (``sceneWithFade``)."""

    scene: int = 0
    """Scene number (``0``–``15``)."""

    fade_time: float | None = None
    """Fade time for this command, in seconds."""


@dataclass
class RGBWithFade(Model):
    """RGB colour with a one-off fade (``colorRGBWithFade``)."""

    color: RGB = field(default_factory=RGB)
    """The colour. Leave :attr:`RGB.dimmable` unset."""

    fade_time: float | None = None
    """Fade time for this command, in seconds."""


@dataclass
class WAFWithFade(Model):
    """WAF colour with a one-off fade (``colorWAFWithFade``)."""

    color: WAF = field(default_factory=WAF)
    """The colour. Leave :attr:`WAF.dimmable` unset."""

    fade_time: float | None = None
    """Fade time for this command, in seconds."""


@dataclass
class KelvinWithFade(Model):
    """Colour temperature with a one-off fade (``colorKelvinWithFade``)."""

    color: float = 4000.0
    """Colour temperature in kelvin."""

    fade_time: float | None = None
    """Fade time for this command, in seconds."""


@dataclass
class XYWithFade(Model):
    """CIE chromaticity with a one-off fade (``colorXYWithFade``)."""

    color: XY = field(default_factory=XY)
    """The coordinates. Leave :attr:`XY.dimmable` unset."""

    fade_time: float | None = None
    """Fade time for this command, in seconds."""


@dataclass
class ControlData(Model):
    """Body of a control request (``POST /device/{id}/control`` and friends).

    Set exactly the fields you want the gateway to apply; everything else
    is omitted from the JSON body. The matching colour shapes are reused
    between the ``color*`` (no brightness) and ``dimmable*`` (with
    brightness) variants — pass through whichever kwarg you want.
    """

    switchable: bool | None = None
    """``True`` = switch on, ``False`` = switch off."""

    dimmable: float | None = None
    """Set brightness in percent (``0.0``–``100.0``)."""

    goto_last_active: bool | None = None
    """``True`` = recall the last active level."""

    scene: int | None = None
    """Recall a stored scene (``0``–``15``)."""

    fade_time: float | None = None
    """Store a new fade time in the device, in seconds.

    This is a device setting, not a fade for this request: the gateway
    writes it into the DALI gear, and the gear uses it for every later
    fading command. For a one-off fade use :attr:`dimmable_with_fade` and
    the other ``*_with_fade`` fields.
    """

    fade_rate: float | None = None
    """Store a new fade rate in the device, in steps per second (a device setting, like :attr:`fade_time`)."""

    save_to_scene: int | None = None
    """Save the current state into the given scene number."""

    color_rgb: RGB | None = field(default=None, metadata={"json": "colorRGB"})
    """Set RGB colour (no brightness change)."""

    dimmable_rgb: RGB | None = field(default=None, metadata={"json": "dimmableRGB"})
    """Set RGB colour together with a brightness level."""

    color_waf: WAF | None = field(default=None, metadata={"json": "colorWAF"})
    """Set white/amber/free colour (no brightness change)."""

    dimmable_waf: WAF | None = field(default=None, metadata={"json": "dimmableWAF"})
    """Set WAF colour together with a brightness level."""

    color_xy: XY | None = field(default=None, metadata={"json": "colorXY"})
    """Set CIE chromaticity (no brightness change)."""

    dimmable_xy: XY | None = field(default=None, metadata={"json": "dimmableXY"})
    """Set CIE chromaticity together with a brightness level."""

    color_kelvin: float | None = None
    """Set colour temperature in kelvin (no brightness change)."""

    dimmable_kelvin: Kelvin | None = None
    """Set colour temperature together with a brightness level."""

    dim_up: int | None = None
    """Send DALI UP this many times (``1``–``5``)."""

    dim_down: int | None = None
    """Send DALI DOWN this many times (``1``–``5``)."""

    dimmable_with_fade: DimmableWithFade | None = None
    """Set brightness with a one-off fade time."""

    goto_last_active_with_fade: WithFadeTime | None = None
    """Recall the last active level with a one-off fade time."""

    scene_with_fade: SceneWithFade | None = None
    """Recall a scene with a one-off fade time."""

    color_rgb_with_fade: RGBWithFade | None = field(default=None, metadata={"json": "colorRGBWithFade"})
    """Set RGB colour with a one-off fade time."""

    color_waf_with_fade: WAFWithFade | None = field(default=None, metadata={"json": "colorWAFWithFade"})
    """Set WAF colour with a one-off fade time."""

    color_kelvin_with_fade: KelvinWithFade | None = None
    """Set colour temperature with a one-off fade time."""

    color_xy_with_fade: XYWithFade | None = field(default=None, metadata={"json": "colorXYWithFade"})
    """Set CIE chromaticity with a one-off fade time."""


# ---------- zones ----------


@dataclass
class Zone(Model):
    """A logical zone — a named collection of :class:`DeviceTarget` references.

    Used both as the read-side response (``ZoneModel`` / ``ZoneResponse``)
    and as the create/update body (``UpdateZoneModel``). For create calls
    the server assigns :attr:`id`; clients should leave it ``None``.
    """

    id: int | None = None
    """Server-assigned zone identifier (read-only)."""

    name: str | None = None
    """Human-readable zone label."""

    targets: list[DeviceTarget] = field(default_factory=list)
    """Devices, groups and broadcasts that make up the zone."""

    features: dict[str, object] = field(default_factory=dict)
    """Aggregate feature map for the zone (read-side; opaque payload)."""

    time_signature: Signature | None = None
    """Concurrency token returned on single-zone fetches."""


# ---------- sequencer ----------


@dataclass
class SequencerAction(Model):
    """The action payload for one :class:`SequenceStep`."""

    targets: list[DeviceTarget] = field(default_factory=list)
    """Targets the action applies to."""

    features: dict[str, object] = field(default_factory=dict)
    """Feature payload to apply (same shape as :attr:`Device.features`)."""


@dataclass
class SequenceStep(Model):
    """One step inside a :class:`Sequence`.

    A step waits :attr:`delay` seconds (when present) and then applies
    :attr:`data` to its targets.
    """

    type: ActionTypes | None = None
    """Kind of action this step performs."""

    data: SequencerAction | None = None
    """Action payload — targets plus features to set."""

    enabled: bool | None = None
    """``False`` = skip this step. Defaults to true on the gateway."""

    delay: float | None = None
    """Delay before this step fires, in seconds."""


@dataclass
class Sequence(Model):
    """A user-defined sequence of feature updates run by the sequencer.

    Merges ``Sequence`` (write), ``SequenceResponse`` (read), and
    ``SequenceUpdate`` (partial write) into one type. Server-managed
    fields like :attr:`id` and :attr:`active` are unset on create.
    """

    id: int | None = None
    """Server-assigned sequence identifier."""

    name: str | None = None
    """Human-readable sequence label."""

    enabled: bool | None = None
    """``False`` = paused."""

    loop: bool | None = None
    """If ``True`` the sequence restarts when it ends."""

    repeat: int | None = None
    """How many times to repeat (mutually exclusive with :attr:`loop`)."""

    steps: list[SequenceStep] = field(default_factory=list)
    """Ordered steps that make up the sequence."""

    is_macro: bool | None = None
    """``True`` for sequences implemented as DALI macros (read-only)."""

    active: bool | None = None
    """Whether the sequence is currently running (read-only)."""


# ---------- circadian ----------


@dataclass
class CircadianStep(Model):
    """One waypoint inside a :class:`CircadianCurve` (per-hour state)."""

    hour: int = 0
    """Hour of the day (``0``–``23``)."""

    dimmable: float | None = None
    """Target brightness in percent at this hour."""

    enable_dimmable: bool | None = None
    """``False`` = leave brightness unchanged at this hour."""

    color_kelvin: float | None = None
    """Target colour temperature in kelvin."""

    enable_kelvin: bool | None = None
    """``False`` = leave colour temperature unchanged at this hour."""


@dataclass
class CircadianCurve(Model):
    """A 24-hour curve, anchored to a calendar date.

    Two curves frame a :class:`Circadian` — :attr:`Circadian.longest` and
    :attr:`Circadian.shortest`. Other days interpolate between them.
    """

    day: int = 0
    """Day of the month the curve applies to."""

    month: int = 0
    """Month (``1``–``12``) the curve applies to."""

    steps: list[CircadianStep] = field(default_factory=list)
    """Hourly waypoints (typically 24)."""


@dataclass
class Circadian(Model):
    """A circadian rhythm configuration: brightness / colour over the day.

    Defined by two curves (longest and shortest day); the gateway
    interpolates between them on intermediate dates.
    """

    id: int | None = None
    """Server-assigned identifier."""

    name: str | None = None
    """Human-readable label."""

    enabled: bool | None = None
    """``False`` = paused."""

    targets: list[DeviceTarget] = field(default_factory=list)
    """Devices and groups the rhythm controls."""

    longest: CircadianCurve | None = None
    """Curve for the longest day of the year."""

    shortest: CircadianCurve | None = None
    """Curve for the shortest day of the year."""

    time_signature: Signature | None = None
    """Concurrency token (read-side)."""


# ---------- scheduler ----------


@dataclass
class SchedulerTime(Model):
    """Wall-clock time used by :class:`Scheduler.recall_time`."""

    hour: int | None = None
    """Hours (``0``–``23``)."""

    minute: int | None = None
    """Minutes (``0``–``59``)."""

    second: int | None = None
    """Seconds (``0``–``59``)."""


@dataclass
class SchedulerAction(Model):
    """The action a :class:`Scheduler` fires."""

    type: ActionTypes | None = None
    """Kind of action."""

    data: dict[str, object] = field(default_factory=dict)
    """Feature payload — same shape as :attr:`Device.features`."""


@dataclass
class ActiveDays(Model):
    """Whitelist of calendar days (``1``–``31``) the scheduler may fire on."""

    days: list[int] = field(default_factory=list)
    """Day numbers; empty = every day."""


@dataclass
class ActiveMonths(Model):
    """Per-month enabled flags. ``None`` for a field means "default" (active)."""

    january: bool | None = None
    """Whether January is active."""

    february: bool | None = None
    """Whether February is active."""

    march: bool | None = None
    """Whether March is active."""

    april: bool | None = None
    """Whether April is active."""

    may: bool | None = None
    """Whether May is active."""

    june: bool | None = None
    """Whether June is active."""

    july: bool | None = None
    """Whether July is active."""

    august: bool | None = None
    """Whether August is active."""

    september: bool | None = None
    """Whether September is active."""

    october: bool | None = None
    """Whether October is active."""

    november: bool | None = None
    """Whether November is active."""

    december: bool | None = None
    """Whether December is active."""


@dataclass
class ActiveWeekDays(Model):
    """Per-weekday enabled flags. ``None`` for a field means "default" (active)."""

    monday: bool | None = None
    """Whether Monday is active."""

    tuesday: bool | None = None
    """Whether Tuesday is active."""

    wednesday: bool | None = None
    """Whether Wednesday is active."""

    thursday: bool | None = None
    """Whether Thursday is active."""

    friday: bool | None = None
    """Whether Friday is active."""

    saturday: bool | None = None
    """Whether Saturday is active."""

    sunday: bool | None = None
    """Whether Sunday is active."""


@dataclass
class ActivePeriod(Model):
    """Yearly date range the scheduler is allowed to fire in."""

    start_month: int | None = None
    """First active month (``1``–``12``)."""

    end_month: int | None = None
    """Last active month (``1``–``12``); inclusive."""

    start_day: int | None = None
    """First active day-of-month."""

    end_day: int | None = None
    """Last active day-of-month; inclusive."""


@dataclass
class Scheduler(Model):
    """A time- or sun-based trigger that runs an action against targets.

    Combines ``SchedulerModel`` (write), ``SchedulerResponse`` (read), and
    ``SchedulerUpdate`` (partial write). The various ``active_*`` fields
    constrain when the scheduler may fire.
    """

    id: int | None = None
    """Server-assigned identifier."""

    name: str | None = None
    """Human-readable label."""

    enabled: bool | None = None
    """``False`` = paused."""

    targets: list[DeviceTarget] = field(default_factory=list)
    """Targets the action is applied to."""

    active_period: ActivePeriod | None = None
    """Yearly date window in which the scheduler may fire."""

    active_months: ActiveMonths | None = None
    """Per-month enabled flags."""

    active_weekdays: ActiveWeekDays | None = None
    """Per-weekday enabled flags."""

    active_days: ActiveDays | None = None
    """Per-day-of-month allow-list."""

    recall_mode: SchedulerRecallModes | None = None
    """How :attr:`recall_time` is interpreted (clock vs. sun-relative)."""

    recall_time: SchedulerTime | None = None
    """The clock or sun offset that triggers the action."""

    action: SchedulerAction | None = None
    """The action to apply when the scheduler fires."""


# ---------- trigger actions ----------


@dataclass
class TriggerActionSource(Model):
    """One source that can fire a :class:`TriggerAction`.

    Use :attr:`id` for ``device``/``group`` sources, and
    :attr:`address`/:attr:`line` for raw ``d16gear``/``d16group`` sources.
    """

    type: TriggerActionSourceType | None = None
    """Kind of source."""

    id: int | None = None
    """Device or group identifier (for ``device``/``group`` sources)."""

    address: int | None = None
    """DALI bus address (for ``d16gear``/``d16group`` sources)."""

    line: int | None = None
    """DALI line index (for ``d16gear``/``d16group`` sources)."""


@dataclass
class TriggerAction(Model):
    """A "when X happens, do Y" rule routed by the gateway."""

    id: int | None = None
    """Server-assigned identifier."""

    name: str | None = None
    """Human-readable label."""

    enabled: bool | None = None
    """``False`` = paused."""

    sources: list[TriggerActionSource] = field(default_factory=list)
    """Things that, when they change state, fire this trigger."""

    targets: list[DeviceTarget] = field(default_factory=list)
    """Things the trigger acts on."""


# ---------- DALI bus scan ----------


@dataclass
class StartScan(Model):
    """Optional body for :meth:`Client.start_scan`."""

    new_installation: bool | None = None
    """``True`` = forget existing addresses and re-address from scratch."""

    no_addressing: bool | None = None
    """``True`` = enumerate the bus without assigning addresses."""

    use_lines: list[int] = field(default_factory=list)
    """Restrict the scan to the given DALI lines (empty = all lines)."""


@dataclass
class LineScan(Model):
    """Scan progress for one DALI line, inside :attr:`Scan.lines` (``LineScanResult``)."""

    line: int = 0
    """DALI line index."""

    scan_state: LineScanState | None = None
    """The line's scan state."""

    found: int | None = None
    """Devices found on the line."""

    found_sensors: int | None = None
    """Sensors found on the line."""

    addressed: int | None = None
    """Devices addressed on the line."""

    scanned: int | None = None
    """Addresses scanned so far."""

    progress: float | None = None
    """Completion for the line."""


@dataclass
class Scan(Model):
    """Result of a DALI bus scan, returned from the scan endpoints."""

    id: str | None = None
    """Identifier of the current scan."""

    progress: float | None = None
    """Completion fraction (``0.0``–``1.0``)."""

    found: int | None = None
    """Number of devices discovered so far."""

    found_sensors: int | None = None
    """Number of sensors discovered so far."""

    status: ScanState | None = None
    """High-level lifecycle state."""

    lines: list[LineScan] = field(default_factory=list)
    """Per-line progress."""


# ---------- info / system ----------


@dataclass
class DaliBus(Model):
    """Live status of one DALI bus line, returned inside :attr:`Info.lines`."""

    send_blocked_initialize: bool | None = None
    """``True`` = sends are blocked because the line is initialising."""

    send_blocked_quiescent: bool | None = None
    """``True`` = sends are blocked because the line is quiescent."""

    send_blocked_macro_running: bool | None = None
    """``True`` = sends are blocked because a DALI macro is running."""

    send_buffer_full: bool | None = None
    """``True`` = the line's send buffer is full."""

    line_status: LineStatus | None = None
    """Power / health of the line."""

    device: YnDeviceInfo | None = None
    """Hardware identity of the interface serving this line."""


@dataclass
class YnDescriptor(Model):
    """YN-protocol capability descriptor reported by the gateway hardware."""

    lines: int = 0
    """Number of DALI lines on the device."""

    buffer_size: int = 0
    """Size of the device's frame buffer."""

    tick_resolution: int = 0
    """Tick resolution in microseconds."""

    max_yn_frame_size: int = 0
    """Largest YN frame the device accepts."""

    implemented_macros: list[int] = field(default_factory=list)
    """DALI macro IDs the firmware implements."""

    device_list_specifier: int = 0
    """YN device list specifier."""

    protocol_version_major: int = 0
    """YN protocol major version."""

    protocol_version_minor: int = 0
    """YN protocol minor version."""

    power_supply_implemented: bool = False
    """``True`` if the gateway has an integrated DALI power supply."""


@dataclass
class YnDeviceInfo(Model):
    """Hardware identity, reported under :attr:`Info.device` and :attr:`DaliBus.device`.

    The 1.18 spec names this schema ``dali_iot__utils__info__DeviceModel``.
    """

    serial: int = 0
    """Manufacturer-assigned serial number."""

    gtin: int = 0
    """GTIN / EAN of the product."""

    pcb: str = ""
    """PCB revision string."""

    article_number: int = 0
    """Manufacturer article number."""

    article_info: str = ""
    """Free-form article description."""

    production_year: int = 0
    """Year of manufacture."""

    production_week: int = 0
    """ISO week of manufacture."""

    device_type: int = 0
    """Numeric hardware type code."""


@dataclass
class Info(Model):
    """Gateway-wide information returned from ``GET /info``."""

    name: str | None = None
    """Operator-chosen device name."""

    version: str | None = None
    """Firmware / API version string."""

    tier: str | None = None
    """Licensing tier (``"basic"``, ``"pro"`` …)."""

    emergency_light: bool | None = None
    """``True`` if the emergency-light feature is licensed."""

    node_red: bool | None = None
    """``True`` if Node-RED is bundled / available."""

    errors: dict[str, str] = field(default_factory=dict)
    """Active error codes mapped to short human-readable details."""

    descriptor: YnDescriptor | None = None
    """Hardware capability descriptor."""

    device: YnDeviceInfo | None = None
    """Hardware identity (serial, article …)."""

    lines: dict[str, DaliBus] = field(default_factory=dict)
    """Per-line bus status, keyed by line ID (``"0"``, ``"1"`` …)."""

    uid: str | None = None
    """Unique identifier of the gateway."""

    startup_mode: StartupMode | None = None
    """Mode the application started in."""


@dataclass
class InfoUpdate(Model):
    """Body for :meth:`Client.update_info` — only the device name is editable."""

    name: str = ""
    """New operator-chosen device name."""


# ---------- date/time + location ----------


@dataclass
class DateTime(Model):
    """Wall-clock state of the gateway. Used for both ``GET`` and ``POST /datetime``."""

    timezone: str | None = None
    """IANA time-zone string (e.g. ``"Europe/Vilnius"``)."""

    automatic_time: bool | None = field(default=None, metadata={"json": "automatic_time"})
    """``True`` = sync from NTP; ``False`` = honour :attr:`date` / :attr:`time`."""

    date: str | None = None
    """ISO ``YYYY-MM-DD`` date (used when :attr:`automatic_time` is ``False``)."""

    time: str | None = None
    """ISO ``HH:MM:SS`` time-of-day (used when :attr:`automatic_time` is ``False``)."""


@dataclass
class TimeZones(Model):
    """List of time-zone names accepted by :class:`DateTime.timezone`."""

    timezones: list[str] = field(default_factory=list)
    """All IANA time-zone identifiers known to the gateway."""


@dataclass
class Location(Model):
    """Geographic location used to compute sunrise / sunset for schedulers."""

    lat: float = 0.0
    """Latitude in decimal degrees."""

    lon: float = 0.0
    """Longitude in decimal degrees."""


# ---------- settings + ethernet ----------


@dataclass
class Settings(Model):
    """Protocol-level settings for the gateway."""

    dali_ping: bool | None = field(default=None, metadata={"json": "dali_ping"})
    """``True`` = periodically ping the DALI bus to keep gear awake."""

    log_file_enabled: bool | None = field(default=None, metadata={"json": "log_file_enabled"})
    """``True`` = write troubleshooting logs to files on the gateway.

    Per the spec this slows the application and uses storage, should only be
    on when support asks for it, and turns itself off after 30 days.
    """


@dataclass
class EthernetSettings(Model):
    """Configurable ethernet parameters (used as the ``POST /ethernet`` body)."""

    dhcp: bool | None = None
    """``True`` = obtain configuration from DHCP."""

    ip_address: str | None = field(default=None, metadata={"json": "ip_address"})
    """Static IPv4 address (used when :attr:`dhcp` is ``False``)."""

    subnet_mask: str | None = field(default=None, metadata={"json": "subnet_mask"})
    """Static IPv4 subnet mask."""

    gateway: str | None = None
    """Static IPv4 default gateway."""

    nameservers: list[str] = field(default_factory=list)
    """Static DNS nameserver IPs."""

    static_fallback_retries: int | None = field(default=None, metadata={"json": "static_fallback_retries"})
    """DHCP attempts (``0``–``60``, 10 s each) before falling back to ``169.254.0.1/16``.

    ``0`` falls back after a single 10 s timeout.
    """


@dataclass
class Ethernet(Model):
    """Live ethernet status returned from ``GET /ethernet``."""

    mac_address: str | None = field(default=None, metadata={"json": "mac_address"})
    """Hardware MAC address of the interface."""

    settings: EthernetSettings | None = None
    """Currently active settings."""

    dhcp_lease: str | None = field(default=None, metadata={"json": "dhcp_lease"})
    """Remaining DHCP lease time as a human-readable string."""


# ---------- device data (energy, diagnostics) ----------


@dataclass
class EnergyReport(Model):
    """Energy readings of one device (``GET /device/{id}/energyReporting``, ``EnergyData``).

    Only devices implementing DALI part 252 (energy reporting) have this.
    """

    active_energy_watt_hours: float | None = None
    """Active energy consumed, in Wh."""

    active_power_watt: float | None = None
    """Active power, in W."""

    apparent_energy_volt_ampere_hours: float | None = None
    """Apparent energy, in VAh."""

    apparent_power_volt_ampere: float | None = None
    """Apparent power, in VA."""

    active_energy_loadside_watt_hours: float | None = None
    """Active energy on the load side, in Wh."""

    active_power_loadside_watt: float | None = None
    """Active power on the load side, in W."""


@dataclass
class DiagnosticsMaintenance(Model):
    """Diagnostics of one device (``GET /device/{id}/diagnosticsMaintenance``, ``DiagnosticsMaintenanceData``).

    Only devices implementing DALI part 253 (diagnostics and maintenance)
    have this. Field names follow the spec; units are in the names.
    """

    control_gear_operating_time_seconds: int | None = None
    control_gear_start_counter: int | None = None
    control_gear_external_supply_voltage_volt_rms: float | None = None
    control_gear_external_supply_voltage_frequency_hertz: int | None = None
    control_gear_power_factor: float | None = None
    control_gear_overall_failure_condition: bool | None = None
    control_gear_overall_failure_condition_counter: int | None = None
    control_gear_external_supply_undervoltage: bool | None = None
    control_gear_external_supply_undervoltage_counter: int | None = None
    control_gear_external_supply_overvoltage: bool | None = None
    control_gear_external_supply_overvoltage_counter: int | None = None
    control_gear_output_power_limitation: bool | None = None
    control_gear_output_power_limitation_counter: int | None = None
    control_gear_thermal_derating: bool | None = None
    control_gear_thermal_derating_counter: int | None = None
    control_gear_thermal_shutdown: bool | None = None
    control_gear_thermal_shutdown_counter: int | None = None
    control_gear_temperature_celsius: int | None = None
    control_gear_output_current_percent: int | None = None
    light_source_start_counter_resettable: int | None = None
    light_source_start_counter: int | None = None
    light_source_on_time_resettable_seconds: int | None = None
    light_source_on_time_seconds: int | None = None
    light_source_voltage_volt: float | None = None
    light_source_current_ampere: float | None = None
    light_source_overall_failure_condition: bool | None = None
    light_source_overall_failure_condition_counter: int | None = None
    light_source_short_circuit: bool | None = None
    light_source_short_circuit_counter: int | None = None
    light_source_open_circuit: bool | None = None
    light_source_open_circuit_counter: int | None = None
    light_source_thermal_derating: bool | None = None
    light_source_thermal_derating_counter: int | None = None
    light_source_thermal_shutdown: bool | None = None
    light_source_thermal_shutdown_counter: int | None = None
    light_source_temperature_celsius: int | None = None
    rated_median_useful_life_of_luminaire_hours: int | None = None
    internal_control_gear_reference_temperature_celsius: int | None = None
    rated_median_useful_light_source_starts: int | None = None


# ---------- raw DALI access ----------


@dataclass
class Dali16Command(Model):
    """One 16-bit forward frame for control gear (IEC 62386-102), for :meth:`Client.send_dali16`."""

    address: int = 0
    """Address byte (``0``–``255``)."""

    command: int = 0
    """Opcode byte (``0``–``255``)."""


@dataclass
class Dali24Command(Model):
    """One 24-bit forward frame for control devices (IEC 62386-103), for :meth:`Client.send_dali24`.

    24-bit events can be sent too: split the event source and event info
    across the three bytes.
    """

    address: int = 0
    """Address byte (``0``–``255``)."""

    instance: int = 0
    """Instance byte (``0``–``255``)."""

    command: int = 0
    """Opcode byte (``0``–``255``)."""


@dataclass
class DaliLineStatus(Model):
    """Interface status of one DALI line (``GET /dali/readStatus/{line}``, ``LineStatusResponse``)."""

    line: int = 0
    """DALI line index."""

    bus_voltage_down: bool | None = None
    """``True`` = no bus voltage."""

    initialize_mode: bool | None = None
    """``True`` = the line is in initialise mode."""

    quiescent_mode: bool | None = None
    """``True`` = the line is in quiescent mode."""

    line_status: LineStatus | None = None
    """Power / health of the line."""


# ---------- sensors ----------


@dataclass
class DaliSensorAddress(Model):
    """Bus address of a DALI sensor, inside :attr:`Sensor.dali_sensor_address`."""

    line: int = 0
    """DALI line index."""

    address: int = 0
    """Short address of the input device."""

    instance_number: int = 0
    """Instance number within the input device."""


@dataclass
class Sensor(Model):
    """A sensor and its last reading (``GET /sensors``, ``SensorModel``)."""

    id: int = 0
    """Gateway-assigned identifier."""

    name: str = ""
    """Human-readable label."""

    unit: str = ""
    """Unit of :attr:`value` (``"°C"``, ``"lx"`` …)."""

    type: SensorType | None = None
    """What the sensor measures."""

    value: float | None = None
    """Last reading."""

    timestamp: str | None = None
    """When :attr:`value` was read, as an ISO 8601 string."""

    address_type: SensorAddressType | None = None
    """Internal to the gateway, or on the DALI bus."""

    dali_sensor_address: DaliSensorAddress | None = None
    """Bus address, for DALI sensors."""


# ---------- periodic status queries ----------


@dataclass
class StatusQueryConfig(Model):
    """Periodic query settings for one DALI line (``/automations/statusQueries/{line}``, ``LineConfigModel``).

    Each query is DALI bus traffic, one device at a time.
    """

    delay_between_queries: float | None = None
    """Seconds between consecutive queries."""

    query_status: bool | None = None
    """``True`` = periodically query each device's status (see :attr:`Device.status`)."""

    query_actual_level: bool | None = None
    """``True`` = periodically query each device's actual level."""


# ---------- event trigger actions ----------


@dataclass
class EventTriggerAction(Model):
    """Forwards DALI event frames from one line to others (``/automations/eventTriggerAction``).

    Merges ``EventTriggerActionInputModel`` (create), ``…ResponseModel``
    (read) and ``…UpdateModel`` (partial update). Creating one requires
    :attr:`target_lines` and :attr:`filters`.
    """

    id: int | None = None
    """Server-assigned identifier."""

    name: str | None = None
    """Human-readable label."""

    enabled: bool | None = None
    """``False`` = paused. Defaults to ``True`` on create."""

    source_line: int | None = field(default=None, metadata={"json": "source_line"})
    """Line whose events are forwarded."""

    target_lines: list[int] | None = field(default=None, metadata={"json": "target_lines", "keep_empty": True})
    """Lines that receive the forwarded events."""

    filters: dict[str, list[int]] | None = field(default=None, metadata={"keep_empty": True})
    """Only forward events matching every category, e.g. ``{"shortAddress": [1, 2], "instanceType": [1]}``.

    Categories are ``shortAddress``, ``deviceGroup``, ``instanceType`` and
    ``instanceNumber``. ``{}`` forwards every event frame. The gateway
    rejects impossible combinations; per the spec the allowed pairs are
    shortAddress + instanceType, shortAddress + instanceNumber,
    deviceGroup + instanceType and instanceType + instanceNumber.
    """


# ---------- email (firmware before 1.18 only) ----------
#
# Firmware 1.18.7 no longer has ``/email`` (it answers 404), and its spec
# dropped these schemas. They stay for older firmware.


@dataclass
class MailConfigInput(Model):
    """SMTP configuration used to *write* mail settings.

    The ``password`` field carries the plaintext secret; pair with
    :class:`MailSettingsInput` for ``PUT /email``.
    """

    server: str | None = None
    """SMTP server hostname."""

    port: int | None = None
    """SMTP server port."""

    security: SmtpSecurity | None = None
    """Transport security policy."""

    username: str | None = None
    """SMTP username."""

    password: str | None = None
    """SMTP password (write-only)."""

    sender_name: str | None = None
    """Display name used in outgoing mails."""

    sender_email: str | None = None
    """Envelope sender address."""


@dataclass
class MailConfig(Model):
    """SMTP configuration as *returned* from the gateway.

    The ``password`` field is a presence flag, not the secret — the
    plaintext is never echoed back.
    """

    server: str | None = None
    """SMTP server hostname."""

    port: int | None = None
    """SMTP server port."""

    security: SmtpSecurity | None = None
    """Transport security policy."""

    password: bool | None = None
    """``True`` = a password is stored on the gateway."""

    username: str | None = None
    """SMTP username."""

    sender_name: str | None = None
    """Display name used in outgoing mails."""

    sender_email: str | None = None
    """Envelope sender address."""


@dataclass
class TestNotificationSettings(Model):
    """Per-test notification preferences."""

    send_on_success: bool | None = None
    """``True`` = mail when the test passes."""

    send_on_failure: bool | None = None
    """``True`` = mail when the test fails."""


@dataclass
class NotificationSettings(Model):
    """Which test outcomes generate emails, and to whom."""

    function_test: TestNotificationSettings | None = None
    """Preferences for the periodic functional test."""

    duration_test: TestNotificationSettings | None = None
    """Preferences for the periodic duration test."""

    communication_test: TestNotificationSettings | None = None
    """Preferences for the bus communication test."""

    mail_receivers: list[str] = field(default_factory=list)
    """Email addresses to send notifications to."""


@dataclass
class MailSettingsInput(Model):
    """Body for ``PUT /email`` — wraps :class:`MailConfigInput`."""

    mail_config: MailConfigInput | None = None
    """SMTP sender configuration (with plaintext password)."""

    notifications: NotificationSettings | None = None
    """Notification preferences."""


@dataclass
class MailSettings(Model):
    """Response from ``GET /email`` — wraps :class:`MailConfig`."""

    mail_config: MailConfig | None = None
    """SMTP sender configuration (with password presence flag)."""

    notifications: NotificationSettings | None = None
    """Notification preferences."""
