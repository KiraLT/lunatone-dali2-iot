"""WebSocket client for the Lunatone DALI 2 IoT gateway.

Once a TCP connection is opened to ``ws://<gateway>``, the gateway streams
JSON event frames covering device state changes, automation updates, raw
DALI bus traffic, and connection health. This module wraps that stream
with typed event classes and a small async client.

Quick start
-----------

::

    import asyncio
    from dali2iot.websocket import WebSocketClient, DevicesEvent, PingEvent

    async def main() -> None:
        async with WebSocketClient(base_url="http://192.168.1.41") as ws:
            async for event in ws:
                match event:
                    case DevicesEvent(devices=devs):
                        for d in devs:
                            print("device update", d.id, d.features)
                    case PingEvent(echo=msg):
                        print("ping", msg)

    asyncio.run(main())

Event filtering
---------------

The gateway lets a connection mask out event types it doesn't want. Send
a :class:`Filter` once after connecting to suppress noisy types::

    await ws.set_filter(Filter(dali_monitor=True))

Direct DALI access
------------------

Send raw DALI frames with :meth:`WebSocketClient.send_dali_frame`. The
gateway answers with a :class:`DaliFrameEvent` (send-confirmation /
result code) and, when ``mode.wait_for_answer`` is ``True``, a follow-up
:class:`DaliAnswerEvent` carrying the bus reply.

Off-loop construction
---------------------

``WebSocketClient`` also accepts an injected ``websocket`` (a
pre-connected :class:`websockets.ClientConnection`) so event-loop-
sensitive callers can do the connect off-loop and pass the result
in. The wrapper does not close connections it didn't open.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import ClassVar

import websockets
from websockets.asyncio.client import ClientConnection

from .models import (
    Circadian,
    DateTime,
    Device,
    Info,
    Model,
    Scan,
    Scheduler,
    Sequence,
    Signature,
    TriggerAction,
    Zone,
)

__all__ = [
    "CircadiansDeletedEvent",
    "CircadiansEvent",
    "DaliAnswerEvent",
    "DaliFrame",
    "DaliFrameEvent",
    "DaliFrameMode",
    "DaliMonitorEvent",
    "DaliStatusEvent",
    "DateTimeEvent",
    "DevicesDeletedEvent",
    "DevicesEvent",
    "Event",
    "Filter",
    "InfoEvent",
    "MessageFlashEvent",
    "PingEvent",
    "ScanProgressEvent",
    "SchedulersDeletedEvent",
    "SchedulersEvent",
    "SequencesDeletedEvent",
    "SequencesEvent",
    "TriggerActionsDeletedEvent",
    "TriggerActionsEvent",
    "UnknownEvent",
    "WebSocketClient",
    "ZonesDeletedEvent",
    "ZonesEvent",
    "parse_event",
]


# ---------- request-side models ----------


@dataclass(kw_only=True)
class Filter:
    """Server-side event filter — types set to ``True`` are suppressed.

    Sent via :meth:`WebSocketClient.set_filter`. ``daliMonitor`` and
    ``fileUpload`` are documented as explicit toggles; arbitrary
    additional event types can be passed through :attr:`extra`.
    """

    dali_monitor: bool | None = None
    """Suppress :class:`DaliMonitorEvent` frames."""

    file_upload: bool | None = None
    """Suppress file-upload progress events."""

    extra: dict[str, bool] = field(default_factory=dict)
    """Additional event types to filter, keyed by camelCase event name."""

    def to_dict(self) -> dict[str, bool]:
        """Render as the ``data`` payload of a ``filtering`` message."""
        out: dict[str, bool] = dict(self.extra)
        if self.dali_monitor is not None:
            out["daliMonitor"] = self.dali_monitor
        if self.file_upload is not None:
            out["fileUpload"] = self.file_upload
        return out


@dataclass(kw_only=True)
class DaliFrameMode(Model):
    """Send-mode flags carried inside a :class:`DaliFrame` request."""

    send_twice: bool | None = None
    """``True`` = transmit the command twice (required for some commands)."""

    wait_for_answer: bool | None = None
    """``True`` = wait for the bus reply, surfaced as a :class:`DaliAnswerEvent`."""

    priority: int | None = None
    """DALI command priority (1 = highest, 5 = lowest)."""


@dataclass(kw_only=True)
class DaliFrame(Model):
    """Body of a ``daliFrame`` send request — a raw DALI command.

    Sent via :meth:`WebSocketClient.send_dali_frame`. The gateway echoes a
    :class:`DaliFrameEvent` (send confirmation) for every dispatched
    frame and, when ``mode.wait_for_answer`` is ``True``, follows up
    with a :class:`DaliAnswerEvent`.
    """

    line: int = 0
    """DALI line index to send on."""

    number_of_bits: int = 16
    """16 = DALI command, 24 = DALI-2, 25 = eDALI."""

    mode: DaliFrameMode | None = None
    """Send mode — twice / wait-for-answer / priority."""

    dali_data: list[int] = field(default_factory=list)
    """Raw command bytes (e.g. ``[address, opcode]`` for a 16-bit DALI command)."""


# ---------- event base ----------


def _signature(env: dict[str, object]) -> Signature | None:
    ts = env.get("timeSignature")
    return Signature.from_dict(ts) if isinstance(ts, dict) else None


def _data(env: dict[str, object]) -> dict[str, object]:
    raw = env.get("data")
    return raw if isinstance(raw, dict) else {}


def _list_of(cls: type[Model], data: dict[str, object], key: str) -> list:
    items = data.get(key, [])
    if not isinstance(items, list):
        return []
    return [cls.from_dict(i) for i in items if isinstance(i, dict)]


def _list_of_int(data: dict[str, object], key: str) -> list[int]:
    items = data.get(key, [])
    if not isinstance(items, list):
        return []
    return [int(i) for i in items if isinstance(i, (int, float))]


@dataclass(kw_only=True)
class Event:
    """Base class for every typed websocket event from the gateway.

    All events carry the gateway's :class:`Signature` (timestamp + counter)
    in :attr:`time_signature`. Concrete subclasses add the type-specific
    fields lifted out of the JSON ``data`` envelope.
    """

    TYPE: ClassVar[str] = ""
    """Wire type tag — overridden by each concrete subclass."""

    time_signature: Signature | None = None
    """Echo of the gateway's monotonic state token at event time."""


@dataclass(kw_only=True)
class UnknownEvent(Event):
    """Fallback event for ``type`` values this version doesn't recognise."""

    TYPE: ClassVar[str] = ""

    type: str = ""
    """The unrecognised wire type tag."""

    data: dict[str, object] = field(default_factory=dict)
    """Raw ``data`` payload, untouched."""


# ---------- general communication events ----------


@dataclass(kw_only=True)
class InfoEvent(Event):
    """Greeting frame — pushed once when the connection is established.

    The ``data`` payload mirrors :class:`dali2iot.Info` (``GET /info``).
    """

    TYPE: ClassVar[str] = "info"

    info: Info | None = None
    """Snapshot of gateway information at connect time."""


@dataclass(kw_only=True)
class PingEvent(Event):
    """Connectivity-test event — fired when ``POST /ping/echo`` is hit."""

    TYPE: ClassVar[str] = "ping"

    echo: str | None = None
    """Echo string supplied with the original ``POST /ping/echo`` body."""


@dataclass(kw_only=True)
class MessageFlashEvent(Event):
    """Status / error message intended to be flashed to the user."""

    TYPE: ClassVar[str] = "messageFlash"

    message: str | None = None
    """Human-readable message text."""

    seconds: float | None = None
    """How long the message should remain visible."""

    user_dismissible: bool | None = None
    """``True`` if the user is allowed to clear the message early."""


@dataclass(kw_only=True)
class DateTimeEvent(Event):
    """System time / timezone changed — payload mirrors :class:`dali2iot.DateTime`."""

    TYPE: ClassVar[str] = "datetime"

    datetime: DateTime | None = None
    """New date/time configuration."""


# ---------- direct DALI access events ----------


@dataclass(kw_only=True)
class DaliStatusEvent(Event):
    """DALI bus status changed (power, buffer, macro lifecycle).

    Status code reference: ``0`` no power, ``1`` system failure,
    ``2`` powered, ``3`` buffer full, ``4`` buffer empty, ``5`` low
    power, ``60``-``63`` macro lifecycle (stopped / intermediate /
    failed / succeeded).
    """

    TYPE: ClassVar[str] = "daliStatus"

    status: int | None = None
    """Status code (see class docstring)."""

    line: int | None = None
    """DALI line the status applies to."""


@dataclass(kw_only=True)
class DaliMonitorEvent(Event):
    """Raw DALI bus traffic — every command and answer the gateway sees."""

    TYPE: ClassVar[str] = "daliMonitor"

    tick_us: int | None = None
    """Hardware tick at the time of the event."""

    timestamp: float | None = None
    """Wall-clock timestamp recorded by the gateway."""

    bits: int | None = None
    """Frame length: 8 (answer), 16 (DALI), 24 (DALI-2), 25 (eDALI)."""

    data: list[int] = field(default_factory=list)
    """Raw frame bytes (or a single answer byte)."""

    line: int | None = None
    """DALI line the event was observed on."""

    framing_error: bool | None = None
    """Set on 8-bit answer frames; ``True`` indicates a framing error."""


@dataclass(kw_only=True)
class DaliFrameEvent(Event):
    """Send-confirmation for a :class:`DaliFrame` request.

    Result code reference (notable values): ``0`` sent, ``1`` voltage
    error, ``4`` buffer full, ``61`` collision, ``63`` interface
    timeout, ``100`` no answer.
    """

    TYPE: ClassVar[str] = "daliFrame"

    line: int | None = None
    """DALI line the frame was sent on."""

    result: int | None = None
    """Result code (see class docstring)."""


@dataclass(kw_only=True)
class DaliAnswerEvent(Event):
    """Bus reply to a :class:`DaliFrame` sent with ``wait_for_answer=True``."""

    TYPE: ClassVar[str] = "daliAnswer"

    line: int | None = None
    """DALI line the answer was received on."""

    result: int | None = None
    """``0`` no answer, ``8`` 8-bit value, ``63`` framing error."""

    dali_data: int | None = None
    """The 8-bit value returned by the device (when ``result == 8``)."""


# ---------- entity events (devices / zones / sequences / schedulers / ...) ----------


@dataclass(kw_only=True)
class ScanProgressEvent(Event):
    """Progress update for an ongoing DALI bus scan.

    Payload mirrors :class:`dali2iot.Scan` (``GET /dali/scan``).
    """

    TYPE: ClassVar[str] = "scanProgress"

    scan: Scan | None = None
    """Current scan state."""


@dataclass(kw_only=True)
class DevicesEvent(Event):
    """One or more :class:`Device` records were added or updated.

    Updates contain only the changed fields; an addition contains the
    full record. Use ``device.id`` to merge with local state.
    """

    TYPE: ClassVar[str] = "devices"

    devices: list[Device] = field(default_factory=list)
    """The added or updated devices."""


@dataclass(kw_only=True)
class DevicesDeletedEvent(Event):
    """One or more devices were forgotten by the gateway."""

    TYPE: ClassVar[str] = "devicesDeleted"

    deleted: list[int] = field(default_factory=list)
    """Identifiers of the devices that were removed."""


@dataclass(kw_only=True)
class ZonesEvent(Event):
    """One or more :class:`Zone` records were added or updated."""

    TYPE: ClassVar[str] = "zones"

    zones: list[Zone] = field(default_factory=list)
    """The added or updated zones."""


@dataclass(kw_only=True)
class ZonesDeletedEvent(Event):
    """One or more zones were deleted."""

    TYPE: ClassVar[str] = "zonesDeleted"

    deleted: list[int] = field(default_factory=list)
    """Identifiers of the zones that were removed."""


@dataclass(kw_only=True)
class SequencesEvent(Event):
    """One or more :class:`Sequence` records were added or updated."""

    TYPE: ClassVar[str] = "sequences"

    sequences: list[Sequence] = field(default_factory=list)
    """The added or updated sequences."""


@dataclass(kw_only=True)
class SequencesDeletedEvent(Event):
    """One or more sequences were deleted."""

    TYPE: ClassVar[str] = "sequencesDeleted"

    deleted: list[int] = field(default_factory=list)
    """Identifiers of the sequences that were removed."""


@dataclass(kw_only=True)
class SchedulersEvent(Event):
    """One or more :class:`Scheduler` records were added or updated."""

    TYPE: ClassVar[str] = "schedulers"

    schedulers: list[Scheduler] = field(default_factory=list)
    """The added or updated schedulers."""


@dataclass(kw_only=True)
class SchedulersDeletedEvent(Event):
    """One or more schedulers were deleted."""

    TYPE: ClassVar[str] = "schedulersDeleted"

    deleted: list[int] = field(default_factory=list)
    """Identifiers of the schedulers that were removed."""


@dataclass(kw_only=True)
class CircadiansEvent(Event):
    """One or more :class:`Circadian` rhythms were added or updated."""

    TYPE: ClassVar[str] = "circadians"

    circadians: list[Circadian] = field(default_factory=list)
    """The added or updated circadian rhythms."""


@dataclass(kw_only=True)
class CircadiansDeletedEvent(Event):
    """One or more circadian rhythms were deleted."""

    TYPE: ClassVar[str] = "circadiansDeleted"

    deleted: list[int] = field(default_factory=list)
    """Identifiers of the rhythms that were removed."""


@dataclass(kw_only=True)
class TriggerActionsEvent(Event):
    """One or more :class:`TriggerAction` rules were added or updated."""

    TYPE: ClassVar[str] = "triggerActions"

    trigger_actions: list[TriggerAction] = field(default_factory=list)
    """The added or updated trigger-action rules."""


@dataclass(kw_only=True)
class TriggerActionsDeletedEvent(Event):
    """One or more trigger-action rules were deleted."""

    TYPE: ClassVar[str] = "triggerActionsDeleted"

    deleted: list[int] = field(default_factory=list)
    """Identifiers of the rules that were removed."""


# ---------- envelope dispatch ----------


def _build_info(env: dict[str, object]) -> InfoEvent:
    return InfoEvent(info=Info.from_dict(_data(env)), time_signature=_signature(env))


def _build_ping(env: dict[str, object]) -> PingEvent:
    d = _data(env)
    echo = d.get("echo")
    return PingEvent(
        echo=echo if isinstance(echo, str) else None,
        time_signature=_signature(env),
    )


def _build_message_flash(env: dict[str, object]) -> MessageFlashEvent:
    d = _data(env)
    return MessageFlashEvent(
        message=_str_or_none(d.get("message")),
        seconds=_float_or_none(d.get("seconds")),
        user_dismissible=_bool_or_none(d.get("userDismissible")),
        time_signature=_signature(env),
    )


def _build_datetime(env: dict[str, object]) -> DateTimeEvent:
    return DateTimeEvent(
        datetime=DateTime.from_dict(_data(env)),
        time_signature=_signature(env),
    )


def _build_dali_status(env: dict[str, object]) -> DaliStatusEvent:
    d = _data(env)
    return DaliStatusEvent(
        status=_int_or_none(d.get("status")),
        line=_int_or_none(d.get("line")),
        time_signature=_signature(env),
    )


def _build_dali_monitor(env: dict[str, object]) -> DaliMonitorEvent:
    d = _data(env)
    raw_data = d.get("data")
    payload: list[int] = [int(v) for v in raw_data if isinstance(v, (int, float))] if isinstance(raw_data, list) else []
    return DaliMonitorEvent(
        tick_us=_int_or_none(d.get("tick_us")),
        timestamp=_float_or_none(d.get("timestamp")),
        bits=_int_or_none(d.get("bits")),
        data=payload,
        line=_int_or_none(d.get("line")),
        framing_error=_bool_or_none(d.get("framingError")),
        time_signature=_signature(env),
    )


def _build_dali_frame(env: dict[str, object]) -> DaliFrameEvent:
    d = _data(env)
    return DaliFrameEvent(
        line=_int_or_none(d.get("line")),
        result=_int_or_none(d.get("result")),
        time_signature=_signature(env),
    )


def _build_dali_answer(env: dict[str, object]) -> DaliAnswerEvent:
    d = _data(env)
    return DaliAnswerEvent(
        line=_int_or_none(d.get("line")),
        result=_int_or_none(d.get("result")),
        dali_data=_int_or_none(d.get("daliData")),
        time_signature=_signature(env),
    )


def _build_scan_progress(env: dict[str, object]) -> ScanProgressEvent:
    return ScanProgressEvent(
        scan=Scan.from_dict(_data(env)),
        time_signature=_signature(env),
    )


def _build_devices(env: dict[str, object]) -> DevicesEvent:
    return DevicesEvent(
        devices=_list_of(Device, _data(env), "devices"),
        time_signature=_signature(env),
    )


def _build_devices_deleted(env: dict[str, object]) -> DevicesDeletedEvent:
    return DevicesDeletedEvent(
        deleted=_list_of_int(_data(env), "deleted"),
        time_signature=_signature(env),
    )


def _build_zones(env: dict[str, object]) -> ZonesEvent:
    return ZonesEvent(
        zones=_list_of(Zone, _data(env), "zones"),
        time_signature=_signature(env),
    )


def _build_zones_deleted(env: dict[str, object]) -> ZonesDeletedEvent:
    return ZonesDeletedEvent(
        deleted=_list_of_int(_data(env), "deleted"),
        time_signature=_signature(env),
    )


def _build_sequences(env: dict[str, object]) -> SequencesEvent:
    return SequencesEvent(
        sequences=_list_of(Sequence, _data(env), "sequences"),
        time_signature=_signature(env),
    )


def _build_sequences_deleted(env: dict[str, object]) -> SequencesDeletedEvent:
    return SequencesDeletedEvent(
        deleted=_list_of_int(_data(env), "deleted"),
        time_signature=_signature(env),
    )


def _build_schedulers(env: dict[str, object]) -> SchedulersEvent:
    return SchedulersEvent(
        schedulers=_list_of(Scheduler, _data(env), "schedulers"),
        time_signature=_signature(env),
    )


def _build_schedulers_deleted(env: dict[str, object]) -> SchedulersDeletedEvent:
    return SchedulersDeletedEvent(
        deleted=_list_of_int(_data(env), "deleted"),
        time_signature=_signature(env),
    )


def _build_circadians(env: dict[str, object]) -> CircadiansEvent:
    return CircadiansEvent(
        circadians=_list_of(Circadian, _data(env), "circadians"),
        time_signature=_signature(env),
    )


def _build_circadians_deleted(env: dict[str, object]) -> CircadiansDeletedEvent:
    return CircadiansDeletedEvent(
        deleted=_list_of_int(_data(env), "deleted"),
        time_signature=_signature(env),
    )


def _build_trigger_actions(env: dict[str, object]) -> TriggerActionsEvent:
    return TriggerActionsEvent(
        trigger_actions=_list_of(TriggerAction, _data(env), "triggerActions"),
        time_signature=_signature(env),
    )


def _build_trigger_actions_deleted(env: dict[str, object]) -> TriggerActionsDeletedEvent:
    return TriggerActionsDeletedEvent(
        deleted=_list_of_int(_data(env), "deleted"),
        time_signature=_signature(env),
    )


# Map wire ``type`` tag to its envelope-building helper.
_BUILDERS: dict[str, object] = {
    InfoEvent.TYPE: _build_info,
    PingEvent.TYPE: _build_ping,
    MessageFlashEvent.TYPE: _build_message_flash,
    DateTimeEvent.TYPE: _build_datetime,
    DaliStatusEvent.TYPE: _build_dali_status,
    DaliMonitorEvent.TYPE: _build_dali_monitor,
    DaliFrameEvent.TYPE: _build_dali_frame,
    DaliAnswerEvent.TYPE: _build_dali_answer,
    ScanProgressEvent.TYPE: _build_scan_progress,
    DevicesEvent.TYPE: _build_devices,
    DevicesDeletedEvent.TYPE: _build_devices_deleted,
    ZonesEvent.TYPE: _build_zones,
    ZonesDeletedEvent.TYPE: _build_zones_deleted,
    SequencesEvent.TYPE: _build_sequences,
    SequencesDeletedEvent.TYPE: _build_sequences_deleted,
    SchedulersEvent.TYPE: _build_schedulers,
    SchedulersDeletedEvent.TYPE: _build_schedulers_deleted,
    CircadiansEvent.TYPE: _build_circadians,
    CircadiansDeletedEvent.TYPE: _build_circadians_deleted,
    TriggerActionsEvent.TYPE: _build_trigger_actions,
    TriggerActionsDeletedEvent.TYPE: _build_trigger_actions_deleted,
}


def parse_event(envelope: dict[str, object]) -> Event:
    """Turn one decoded JSON envelope into the matching typed :class:`Event`.

    Unknown event types map to :class:`UnknownEvent` so callers always get
    a typed object back.
    """
    type_ = envelope.get("type")
    builder = _BUILDERS.get(type_) if isinstance(type_, str) else None
    if builder is None:
        return UnknownEvent(
            type=type_ if isinstance(type_, str) else "",
            data=_data(envelope),
            time_signature=_signature(envelope),
        )
    return builder(envelope)  # type: ignore[no-any-return,operator]


# ---------- coercion helpers ----------


def _str_or_none(v: object) -> str | None:
    return v if isinstance(v, str) else None


def _int_or_none(v: object) -> int | None:
    return int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _float_or_none(v: object) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _bool_or_none(v: object) -> bool | None:
    return v if isinstance(v, bool) else None


# ---------- URL helpers ----------


def _to_ws_url(url: str) -> str:
    """Normalise a base URL to a ``ws://`` / ``wss://`` form for ``websockets.connect``."""
    if url.startswith("ws://") or url.startswith("wss://"):
        return url.rstrip("/")
    if url.startswith("http://"):
        return ("ws://" + url[len("http://") :]).rstrip("/")
    if url.startswith("https://"):
        return ("wss://" + url[len("https://") :]).rstrip("/")
    return f"ws://{url.rstrip('/')}"


# ---------- the client ----------


class WebSocketClient:
    """Async WebSocket client for the Lunatone DALI 2 IoT gateway.

    The instance is an async iterator of :class:`Event`. Use either as
    a context manager (recommended)::

        async with WebSocketClient(base_url="http://192.168.1.41") as ws:
            async for event in ws:
                ...

    or by injecting a pre-connected ``websockets.ClientConnection``::

        conn = await websockets.connect("ws://192.168.1.41")
        ws = WebSocketClient(websocket=conn)
        async for event in ws:
            ...

    Args:
        base_url: Gateway URL. ``http://``/``https://`` are auto-rewritten
            to ``ws://``/``wss://``. Ignored when ``websocket`` is given.
        path: Optional path appended to ``base_url`` (default ``""``).
            The Lunatone gateway uses the root path so this is rarely needed.
        websocket: Optional pre-connected :class:`websockets.asyncio.client.ClientConnection`
            to use instead of opening a new one. The wrapper does not close
            connections it didn't open.
        connect_kwargs: Extra kwargs forwarded to :func:`websockets.connect`
            when the wrapper opens its own connection (e.g. ``open_timeout``,
            ``ping_interval``).
    """

    def __init__(
        self,
        base_url: str = "",
        *,
        path: str = "",
        websocket: ClientConnection | None = None,
        connect_kwargs: dict[str, object] | None = None,
    ):
        self._url = _to_ws_url(base_url) + (path if path.startswith("/") else "")
        self._connect_kwargs = connect_kwargs or {}
        self._ws: ClientConnection | None = websocket
        self._owns_ws: bool = websocket is None

    async def __aenter__(self) -> WebSocketClient:
        """Open the connection (no-op when ``websocket`` was injected)."""
        if self._owns_ws:
            self._ws = await websockets.connect(self._url, **self._connect_kwargs)
        return self

    async def __aexit__(self, *args: object) -> None:
        """Close the connection (no-op when ``websocket`` was injected)."""
        if self._owns_ws and self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def close(self) -> None:
        """Close the underlying websocket (no-op when injected)."""
        if self._owns_ws and self._ws is not None:
            await self._ws.close()
            self._ws = None

    def __aiter__(self) -> AsyncIterator[Event]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[Event]:
        ws = self._require_ws()
        async for raw in ws:
            try:
                envelope = json.loads(raw)
            except (TypeError, ValueError):
                continue
            if isinstance(envelope, dict):
                yield parse_event(envelope)

    async def recv(self) -> Event:
        """Receive and parse a single event (lower level than ``async for``)."""
        ws = self._require_ws()
        raw = await ws.recv()
        envelope = json.loads(raw)
        if not isinstance(envelope, dict):
            raise ValueError(f"Expected a JSON object, got {type(envelope).__name__}")
        return parse_event(envelope)

    async def set_filter(self, filter: Filter) -> None:
        """Send a ``filtering`` message — suppress unwanted event types on this connection."""
        await self._send({"type": "filtering", "data": filter.to_dict()})

    async def send_dali_frame(self, frame: DaliFrame) -> None:
        """Send a ``daliFrame`` message — directly inject a raw DALI command on the bus.

        The gateway answers with a :class:`DaliFrameEvent` (send confirmation)
        and, when ``frame.mode.wait_for_answer`` is ``True``, follows up with
        a :class:`DaliAnswerEvent` carrying the bus reply.
        """
        await self._send({"type": "daliFrame", "data": frame.to_dict()})

    async def _send(self, message: dict[str, object]) -> None:
        ws = self._require_ws()
        await ws.send(json.dumps(message))

    def _require_ws(self) -> ClientConnection:
        if self._ws is None:
            raise RuntimeError("WebSocketClient is not connected. Use 'async with' or pass websocket=…")
        return self._ws
