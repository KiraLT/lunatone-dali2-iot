"""Sync and async HTTP clients for the Lunatone Dali-2 IoT gateway.

Every operation in ``openapi.json`` has a method on both :class:`Client`
and :class:`AsyncClient`. Bodies and responses are typed via
:mod:`dali2iot.models`. A handful of endpoints are documented in the spec
with empty inline schemas (``link``, ``reset``, ``reboot``,
``test_email_settings``, ``start_*`` / ``stop_*``, sensor refresh) — those
return ``None``. The ``GET /sensors`` and ``GET /sensors/{id}`` endpoints
aren't schematised either, so they pass through as ``dict[str, object]``.

All methods raise :class:`dali2iot.errors.ApiError` if the gateway returns
a non-2xx status code.

Example
-------

::

    from dali2iot import Client, ControlData, RGB

    with Client(base_url="http://192.168.1.41") as c:
        for device in c.list_devices():
            print(device.id, device.name)

        c.update_device(1, name="Hall light")
        c.control_device(1, ControlData(dimmable_rgb=RGB(r=1, g=0, b=0, dimmable=80)))
"""

from typing import TypeVar

import httpx

from .errors import ApiError
from .models import (
    Circadian,
    ControlData,
    DateTime,
    Device,
    Ethernet,
    EthernetSettings,
    Info,
    InfoUpdate,
    Location,
    MailSettings,
    MailSettingsInput,
    Model,
    Scan,
    Scheduler,
    Sequence,
    Settings,
    StartScan,
    TimeZones,
    TriggerAction,
    Zone,
)

__all__ = ["AsyncClient", "Client"]

M = TypeVar("M", bound=Model)


def _device_update_body(name: str | None, groups: list[int] | None) -> dict[str, object]:
    """Build a ``PUT /device/{id}`` body from optional kwargs.

    Mirrors the OpenAPI ``DeviceUpdateModel`` schema: only fields the
    caller explicitly set are sent, so a ``PUT`` with just ``name``
    leaves ``groups`` untouched.
    """
    body: dict[str, object] = {}
    if name is not None:
        body["name"] = name
    if groups is not None:
        body["groups"] = list(groups)
    return body


def _parse(response: httpx.Response) -> dict[str, object] | None:
    """Turn an ``httpx.Response`` into a parsed JSON object.

    Args:
        response: The raw response from :mod:`httpx`.

    Returns:
        The parsed JSON object (a ``dict``), or ``None`` when the response
        has no body (status 204 or empty content) or its body is not a
        JSON object.

    Raises:
        ApiError: When the response status is ``>= 400``.
    """
    if response.status_code >= 400:
        raise ApiError(response.status_code, response.content)
    if response.status_code == 204 or not response.content:
        return None
    parsed = response.json()
    return parsed if isinstance(parsed, dict) else None


def _model(cls: type[M], data: dict[str, object] | None) -> M:
    """Build a :class:`Model` subclass instance from optional JSON data.

    Falls back to a default-constructed instance when ``data`` is ``None``,
    so the caller always gets a typed object back.
    """
    return cls.from_dict(data) if data is not None else cls()


def _model_list(cls: type[M], data: dict[str, object] | None, key: str) -> list[M]:
    """Unwrap a list of :class:`Model` instances from a JSON envelope.

    The Dali-2 IoT API always wraps list responses in an envelope (``{
    "devices": [...] }``, ``{ "zones": [...] }``, …); this helper hides
    that detail and returns just the typed elements.
    """
    items = (data or {}).get(key, [])
    return [cls.from_dict(item) for item in items if isinstance(item, dict)]


def _build_http_kwargs(
    base_url: str,
    timeout: float | None,
    headers: dict[str, str] | None,
    verify_ssl: bool,
    token: str | None,
) -> dict[str, object]:
    """Assemble the keyword arguments shared by ``httpx.Client`` and ``httpx.AsyncClient``."""
    merged = dict(headers or {})
    if token:
        merged["Authorization"] = f"Bearer {token}"
    return {"base_url": base_url, "timeout": timeout, "headers": merged, "verify": verify_ssl}


class Client:
    """Synchronous client for the Lunatone Dali-2 IoT gateway.

    Construct it with the gateway's HTTP base URL and either use it as a
    context manager (recommended — closes the underlying connection pool
    when you're done) or call methods directly on the instance.

    Example::

        from dali2iot import Client

        with Client(base_url="http://192.168.1.41") as c:
            devices = c.list_devices()

    Args:
        base_url: Root URL of the gateway, e.g. ``"http://192.168.1.41"``.
        timeout: Request timeout in seconds. ``None`` = httpx default.
        headers: Extra request headers merged into every call.
        verify_ssl: Pass ``False`` to skip TLS verification (lab use only).
        token: Optional bearer token sent as ``Authorization: Bearer …``.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float | None = None,
        headers: dict[str, str] | None = None,
        verify_ssl: bool = True,
        token: str | None = None,
    ):
        self._http = httpx.Client(**_build_http_kwargs(base_url, timeout, headers, verify_ssl, token))

    def __enter__(self) -> "Client":
        """Enter the underlying ``httpx.Client`` context."""
        self._http.__enter__()
        return self

    def __exit__(self, *args: object) -> None:
        """Exit the underlying ``httpx.Client`` context (closes the connection pool)."""
        self._http.__exit__(*args)

    def close(self) -> None:
        """Close the underlying ``httpx.Client`` connection pool."""
        self._http.close()

    def _json(self, method: str, path: str, body: dict[str, object] | None = None) -> dict[str, object] | None:
        """Issue a JSON request and return the parsed body (or ``None`` on 204)."""
        return _parse(self._http.request(method, path, json=body))

    # ----- devices -----

    def list_devices(self) -> list[Device]:
        """Return every DALI :class:`Device` known to the gateway (``GET /devices``)."""
        return _model_list(Device, self._json("GET", "/devices"), "devices")

    def delete_all_devices(self) -> None:
        """Delete every device (``DELETE /devices``).

        Removes the gateway's view of the bus; the physical gear keeps its
        configuration.
        """
        self._json("DELETE", "/devices")

    def get_device(self, device_id: int) -> Device:
        """Fetch a single :class:`Device` by id (``GET /device/{id}``)."""
        return _model(Device, self._json("GET", f"/device/{device_id}"))

    def update_device(
        self,
        device_id: int,
        *,
        name: str | None = None,
        groups: list[int] | None = None,
    ) -> Device:
        """Update a device's name and/or DALI groups (``PUT /device/{id}``).

        Args:
            device_id: Identifier of the device to update.
            name: New human-readable name; ``None`` = leave unchanged.
            groups: New DALI group membership; ``None`` = leave unchanged.

        Returns:
            The updated :class:`Device`.
        """
        return _model(Device, self._json("PUT", f"/device/{device_id}", _device_update_body(name, groups)))

    def delete_device(self, device_id: int) -> None:
        """Forget a single device (``DELETE /device/{id}``)."""
        self._json("DELETE", f"/device/{device_id}")

    # ----- control -----

    def control_device(self, device_id: int, data: ControlData) -> None:
        """Apply a :class:`ControlData` payload to one device (``POST /device/{id}/control``)."""
        self._json("POST", f"/device/{device_id}/control", data.to_dict())

    def control_group(self, group_id: int, data: ControlData) -> None:
        """Apply a :class:`ControlData` payload to a DALI group (``POST /group/{id}/control``)."""
        self._json("POST", f"/group/{group_id}/control", data.to_dict())

    def control_zone(self, zone_id: int, data: ControlData) -> None:
        """Apply a :class:`ControlData` payload to a :class:`Zone` (``POST /zone/{id}/control``)."""
        self._json("POST", f"/zone/{zone_id}/control", data.to_dict())

    def control_broadcast(self, data: ControlData) -> None:
        """Broadcast a :class:`ControlData` payload to every device (``POST /broadcast/control``)."""
        self._json("POST", "/broadcast/control", data.to_dict())

    # ----- link -----

    def enable_linking(self) -> None:
        """Enable the gateway's linking (DALI commissioning) mode (``POST /link/enable``)."""
        self._json("POST", "/link/enable")

    def disable_linking(self) -> None:
        """Disable the gateway's linking mode (``POST /link/disable``)."""
        self._json("POST", "/link/disable")

    # ----- DALI bus scan -----

    def get_scan(self) -> Scan:
        """Return the current bus-scan progress (``GET /dali/scan``)."""
        return _model(Scan, self._json("GET", "/dali/scan"))

    def start_scan(self, options: StartScan | None = None) -> Scan:
        """Start a DALI bus scan (``POST /dali/scan``).

        Args:
            options: Scan parameters (re-address, lines to scan, etc.).
                ``None`` triggers a default scan.

        Returns:
            The initial :class:`Scan` state. Poll :meth:`get_scan` for progress.
        """
        body = options.to_dict() if options else {}
        return _model(Scan, self._json("POST", "/dali/scan", body))

    def cancel_scan(self) -> Scan:
        """Cancel the running bus scan (``POST /dali/scan/cancel``)."""
        return _model(Scan, self._json("POST", "/dali/scan/cancel"))

    # ----- info / system -----

    def get_info(self) -> Info:
        """Return gateway-wide :class:`Info` (firmware, hardware, bus health) (``GET /info``)."""
        return _model(Info, self._json("GET", "/info"))

    def update_info(self, info: InfoUpdate) -> Info:
        """Update editable :class:`Info` fields, currently just the device name (``PUT /info``)."""
        return _model(Info, self._json("PUT", "/info", info.to_dict()))

    def reset(self) -> None:
        """Factory-reset the gateway (``DELETE /reset``).

        Wipes configuration. Use with care — there's no confirmation step.
        """
        self._json("DELETE", "/reset")

    def reboot(self) -> None:
        """Reboot the gateway (``POST /reboot``). Configuration is preserved."""
        self._json("POST", "/reboot")

    # ----- date/time + location -----

    def get_datetime(self) -> DateTime:
        """Return the gateway's current wall-clock state (``GET /datetime``)."""
        return _model(DateTime, self._json("GET", "/datetime"))

    def set_datetime(self, datetime: DateTime) -> DateTime:
        """Set the gateway's date/time and time-zone (``POST /datetime``)."""
        return _model(DateTime, self._json("POST", "/datetime", datetime.to_dict()))

    def get_timezones(self) -> TimeZones:
        """Return every time-zone identifier the gateway accepts (``GET /datetime/timezones``)."""
        return _model(TimeZones, self._json("GET", "/datetime/timezones"))

    def get_location(self) -> Location:
        """Return the gateway's configured :class:`Location` (``GET /location``)."""
        return _model(Location, self._json("GET", "/location"))

    def set_location(self, location: Location) -> Location:
        """Set the gateway's location, used for sunrise/sunset schedulers (``POST /location``)."""
        return _model(Location, self._json("POST", "/location", location.to_dict()))

    def detect_location(self) -> Location:
        """Auto-detect the gateway's location via its public IP (``POST /location/detect``)."""
        return _model(Location, self._json("POST", "/location/detect"))

    # ----- settings + ethernet -----

    def get_settings(self) -> Settings:
        """Return protocol-level :class:`Settings` (``GET /settings``)."""
        return _model(Settings, self._json("GET", "/settings"))

    def update_settings(self, settings: Settings) -> Settings:
        """Update protocol-level :class:`Settings` (``PUT /settings``)."""
        return _model(Settings, self._json("PUT", "/settings", settings.to_dict()))

    def get_ethernet(self) -> Ethernet:
        """Return live :class:`Ethernet` status (MAC, settings, lease) (``GET /ethernet``)."""
        return _model(Ethernet, self._json("GET", "/ethernet"))

    def update_ethernet(self, settings: EthernetSettings) -> Ethernet:
        """Apply new :class:`EthernetSettings` (``POST /ethernet``).

        Note: changing the IP address may sever the connection — the
        request itself succeeds, but follow-up calls will need the new URL.
        """
        return _model(Ethernet, self._json("POST", "/ethernet", settings.to_dict()))

    # ----- zones -----

    def list_zones(self) -> list[Zone]:
        """Return every configured :class:`Zone` (``GET /zones``)."""
        return _model_list(Zone, self._json("GET", "/zones"), "zones")

    def delete_all_zones(self) -> None:
        """Delete every zone (``DELETE /zones``). Devices themselves are untouched."""
        self._json("DELETE", "/zones")

    def get_zone(self, zone_id: int) -> Zone:
        """Fetch a single :class:`Zone` by id (``GET /zone/{id}``)."""
        return _model(Zone, self._json("GET", f"/zone/{zone_id}"))

    def create_zone(self, zone: Zone) -> Zone:
        """Create a new :class:`Zone` (``POST /zone``).

        Leave :attr:`Zone.id` unset; the gateway assigns it.
        """
        return _model(Zone, self._json("POST", "/zone", zone.to_dict()))

    def update_zone(self, zone_id: int, zone: Zone) -> Zone:
        """Update an existing :class:`Zone` (``PUT /zone/{id}``)."""
        return _model(Zone, self._json("PUT", f"/zone/{zone_id}", zone.to_dict()))

    def delete_zone(self, zone_id: int) -> None:
        """Delete a single zone (``DELETE /zone/{id}``)."""
        self._json("DELETE", f"/zone/{zone_id}")

    # ----- email -----

    def get_email_settings(self) -> MailSettings:
        """Return the configured :class:`MailSettings` (``GET /email``).

        The returned :attr:`MailSettings.mail_config.password` is a
        boolean presence flag, not the secret.
        """
        return _model(MailSettings, self._json("GET", "/email"))

    def update_email_settings(self, settings: MailSettingsInput) -> MailSettings:
        """Update :class:`MailSettings` (``PUT /email``).

        Pass plaintext SMTP credentials via :class:`MailSettingsInput`;
        the response (typed as :class:`MailSettings`) replaces the password
        with a presence flag.
        """
        return _model(MailSettings, self._json("PUT", "/email", settings.to_dict()))

    def test_email_settings(self) -> None:
        """Send a test email using the current configuration (``POST /email``)."""
        self._json("POST", "/email")

    # ----- sensors -----

    def list_sensors(self) -> dict[str, object] | None:
        """Return all sensors known to the gateway (``GET /sensors``).

        The OpenAPI spec doesn't define a schema for the response body, so
        the raw JSON dict is returned unchanged.
        """
        return self._json("GET", "/sensors")

    def refresh_sensors(self) -> None:
        """Trigger a re-poll of every sensor (``POST /sensors``)."""
        self._json("POST", "/sensors")

    def get_sensor(self, sensor_id: int) -> dict[str, object] | None:
        """Return the latest reading for one sensor (``GET /sensors/{id}``).

        The OpenAPI spec doesn't define a schema for the response body, so
        the raw JSON dict is returned unchanged.
        """
        return self._json("GET", f"/sensors/{sensor_id}")

    def refresh_sensor(self, sensor_id: int) -> None:
        """Trigger a re-poll of one sensor (``POST /sensors/{id}``)."""
        self._json("POST", f"/sensors/{sensor_id}")

    # ----- sequencer -----

    def get_test_sequence(self) -> Sequence:
        """Return the gateway's "test" sequence — a sandbox slot (``GET /automations/sequence/test``)."""
        return _model(Sequence, self._json("GET", "/automations/sequence/test"))

    def update_test_sequence(self, sequence: Sequence) -> Sequence:
        """Replace the test sequence (``PUT /automations/sequence/test``)."""
        return _model(Sequence, self._json("PUT", "/automations/sequence/test", sequence.to_dict()))

    def create_sequence(self, sequence: Sequence) -> Sequence:
        """Create a new :class:`Sequence` (``POST /automations/sequence``)."""
        return _model(Sequence, self._json("POST", "/automations/sequence", sequence.to_dict()))

    def list_sequences(self) -> list[Sequence]:
        """Return every saved :class:`Sequence` (``GET /automations/sequences``)."""
        return _model_list(Sequence, self._json("GET", "/automations/sequences"), "sequences")

    def get_sequence(self, sequence_id: int) -> Sequence:
        """Fetch one :class:`Sequence` by id (``GET /automations/sequence/{id}``)."""
        return _model(Sequence, self._json("GET", f"/automations/sequence/{sequence_id}"))

    def update_sequence(self, sequence_id: int, sequence: Sequence) -> Sequence:
        """Update a saved :class:`Sequence` (``PUT /automations/sequence/{id}``)."""
        return _model(Sequence, self._json("PUT", f"/automations/sequence/{sequence_id}", sequence.to_dict()))

    def delete_sequence(self, sequence_id: int) -> None:
        """Delete one sequence (``DELETE /automations/sequence/{id}``)."""
        self._json("DELETE", f"/automations/sequence/{sequence_id}")

    def start_sequence(self, sequence_id: int) -> None:
        """Begin executing a sequence (``POST /automations/sequence/{id}/start``)."""
        self._json("POST", f"/automations/sequence/{sequence_id}/start")

    def stop_sequence(self, sequence_id: int) -> None:
        """Stop a running sequence (``POST /automations/sequence/{id}/stop``)."""
        self._json("POST", f"/automations/sequence/{sequence_id}/stop")

    # ----- circadian -----

    def list_circadians(self) -> list[Circadian]:
        """Return every :class:`Circadian` rhythm (``GET /automations/circadians``)."""
        return _model_list(Circadian, self._json("GET", "/automations/circadians"), "circadians")

    def create_circadian(self, circadian: Circadian) -> Circadian:
        """Create a new :class:`Circadian` rhythm (``POST /automations/circadian``)."""
        return _model(Circadian, self._json("POST", "/automations/circadian", circadian.to_dict()))

    def get_circadian(self, circadian_id: int) -> Circadian:
        """Fetch one :class:`Circadian` by id (``GET /automations/circadian/{id}``)."""
        return _model(Circadian, self._json("GET", f"/automations/circadian/{circadian_id}"))

    def update_circadian(self, circadian_id: int, circadian: Circadian) -> Circadian:
        """Update a saved :class:`Circadian` rhythm (``PUT /automations/circadian/{id}``)."""
        return _model(
            Circadian,
            self._json("PUT", f"/automations/circadian/{circadian_id}", circadian.to_dict()),
        )

    def delete_circadian(self, circadian_id: int) -> None:
        """Delete one circadian rhythm (``DELETE /automations/circadian/{id}``)."""
        self._json("DELETE", f"/automations/circadian/{circadian_id}")

    def start_circadian(self, circadian_id: int) -> None:
        """Activate a circadian rhythm (``POST /automations/circadian/{id}/start``)."""
        self._json("POST", f"/automations/circadian/{circadian_id}/start")

    def stop_circadian(self, circadian_id: int) -> None:
        """Deactivate a circadian rhythm (``POST /automations/circadian/{id}/stop``)."""
        self._json("POST", f"/automations/circadian/{circadian_id}/stop")

    # ----- scheduler -----

    def list_schedules(self) -> list[Scheduler]:
        """Return every :class:`Scheduler` (``GET /automations/schedules``)."""
        return _model_list(Scheduler, self._json("GET", "/automations/schedules"), "schedulers")

    def create_scheduler(self, scheduler: Scheduler) -> Scheduler:
        """Create a new :class:`Scheduler` (``POST /automations/scheduler``)."""
        return _model(Scheduler, self._json("POST", "/automations/scheduler", scheduler.to_dict()))

    def get_scheduler(self, scheduler_id: int) -> Scheduler:
        """Fetch one :class:`Scheduler` by id (``GET /automations/scheduler/{id}``)."""
        return _model(Scheduler, self._json("GET", f"/automations/scheduler/{scheduler_id}"))

    def update_scheduler(self, scheduler_id: int, scheduler: Scheduler) -> Scheduler:
        """Update a saved :class:`Scheduler` (``PUT /automations/scheduler/{id}``)."""
        return _model(
            Scheduler,
            self._json("PUT", f"/automations/scheduler/{scheduler_id}", scheduler.to_dict()),
        )

    def delete_scheduler(self, scheduler_id: int) -> None:
        """Delete one scheduler (``DELETE /automations/scheduler/{id}``)."""
        self._json("DELETE", f"/automations/scheduler/{scheduler_id}")

    def start_scheduler(self, scheduler_id: int) -> None:
        """Activate a scheduler (``POST /automations/scheduler/{id}/start``)."""
        self._json("POST", f"/automations/scheduler/{scheduler_id}/start")

    def stop_scheduler(self, scheduler_id: int) -> None:
        """Deactivate a scheduler (``POST /automations/scheduler/{id}/stop``)."""
        self._json("POST", f"/automations/scheduler/{scheduler_id}/stop")

    # ----- trigger actions -----

    def list_trigger_actions(self) -> list[TriggerAction]:
        """Return every :class:`TriggerAction` (``GET /automations/triggerActions``)."""
        return _model_list(TriggerAction, self._json("GET", "/automations/triggerActions"), "triggerActions")

    def create_trigger_action(self, trigger_action: TriggerAction) -> TriggerAction:
        """Create a new :class:`TriggerAction` (``POST /automations/triggerAction``)."""
        return _model(TriggerAction, self._json("POST", "/automations/triggerAction", trigger_action.to_dict()))

    def get_trigger_action(self, trigger_action_id: int) -> TriggerAction:
        """Fetch one :class:`TriggerAction` by id (``GET /automations/triggerAction/{id}``)."""
        return _model(TriggerAction, self._json("GET", f"/automations/triggerAction/{trigger_action_id}"))

    def update_trigger_action(self, trigger_action_id: int, trigger_action: TriggerAction) -> TriggerAction:
        """Update a saved :class:`TriggerAction` (``PUT /automations/triggerAction/{id}``)."""
        return _model(
            TriggerAction,
            self._json("PUT", f"/automations/triggerAction/{trigger_action_id}", trigger_action.to_dict()),
        )

    def delete_trigger_action(self, trigger_action_id: int) -> None:
        """Delete one trigger action (``DELETE /automations/triggerAction/{id}``)."""
        self._json("DELETE", f"/automations/triggerAction/{trigger_action_id}")

    def start_trigger_action(self, trigger_action_id: int) -> None:
        """Activate a trigger action (``POST /automations/triggerAction/{id}/start``)."""
        self._json("POST", f"/automations/triggerAction/{trigger_action_id}/start")

    def stop_trigger_action(self, trigger_action_id: int) -> None:
        """Deactivate a trigger action (``POST /automations/triggerAction/{id}/stop``)."""
        self._json("POST", f"/automations/triggerAction/{trigger_action_id}/stop")


class AsyncClient:
    """Asynchronous client for the Lunatone Dali-2 IoT gateway.

    Mirrors :class:`Client` method-for-method, with every operation
    declared ``async``. Use as ``async with AsyncClient(...) as c:`` to
    get a connection pool that's torn down cleanly on exit, or call
    methods directly on the instance.

    Example::

        import asyncio
        from dali2iot import AsyncClient, ControlData

        async def main() -> None:
            async with AsyncClient(base_url="http://192.168.1.41") as c:
                for device in await c.list_devices():
                    print(device.id, device.name)
                await c.control_device(1, ControlData(dimmable=50))

        asyncio.run(main())

    Args:
        base_url: Root URL of the gateway, e.g. ``"http://192.168.1.41"``.
        timeout: Request timeout in seconds. ``None`` = httpx default.
        headers: Extra request headers merged into every call.
        verify_ssl: Pass ``False`` to skip TLS verification (lab use only).
        token: Optional bearer token sent as ``Authorization: Bearer …``.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float | None = None,
        headers: dict[str, str] | None = None,
        verify_ssl: bool = True,
        token: str | None = None,
    ):
        self._http = httpx.AsyncClient(**_build_http_kwargs(base_url, timeout, headers, verify_ssl, token))

    async def __aenter__(self) -> "AsyncClient":
        """Enter the underlying ``httpx.AsyncClient`` context."""
        await self._http.__aenter__()
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit the underlying ``httpx.AsyncClient`` context."""
        await self._http.__aexit__(*args)

    async def close(self) -> None:
        """Close the underlying ``httpx.AsyncClient`` connection pool."""
        await self._http.aclose()

    async def _json(self, method: str, path: str, body: dict[str, object] | None = None) -> dict[str, object] | None:
        """Issue a JSON request and return the parsed body (or ``None`` on 204)."""
        return _parse(await self._http.request(method, path, json=body))

    # ----- devices -----

    async def list_devices(self) -> list[Device]:
        """Return every DALI :class:`Device` known to the gateway (``GET /devices``).

        Async version of :meth:`Client.list_devices`.
        """
        return _model_list(Device, await self._json("GET", "/devices"), "devices")

    async def delete_all_devices(self) -> None:
        """Delete every device (``DELETE /devices``).

        Removes the gateway's view of the bus; the physical gear keeps its
        configuration.

        Async version of :meth:`Client.delete_all_devices`.
        """
        await self._json("DELETE", "/devices")

    async def get_device(self, device_id: int) -> Device:
        """Fetch a single :class:`Device` by id (``GET /device/{id}``).

        Async version of :meth:`Client.get_device`.
        """
        return _model(Device, await self._json("GET", f"/device/{device_id}"))

    async def update_device(
        self,
        device_id: int,
        *,
        name: str | None = None,
        groups: list[int] | None = None,
    ) -> Device:
        """Update a device's name and/or DALI groups (``PUT /device/{id}``).

        Args:
            device_id: Identifier of the device to update.
            name: New human-readable name; ``None`` = leave unchanged.
            groups: New DALI group membership; ``None`` = leave unchanged.

        Returns:
            The updated :class:`Device`.

        Async version of :meth:`Client.update_device`.
        """
        data = await self._json("PUT", f"/device/{device_id}", _device_update_body(name, groups))
        return _model(Device, data)

    async def delete_device(self, device_id: int) -> None:
        """Forget a single device (``DELETE /device/{id}``).

        Async version of :meth:`Client.delete_device`.
        """
        await self._json("DELETE", f"/device/{device_id}")

    # ----- control -----

    async def control_device(self, device_id: int, data: ControlData) -> None:
        """Apply a :class:`ControlData` payload to one device (``POST /device/{id}/control``).

        Async version of :meth:`Client.control_device`.
        """
        await self._json("POST", f"/device/{device_id}/control", data.to_dict())

    async def control_group(self, group_id: int, data: ControlData) -> None:
        """Apply a :class:`ControlData` payload to a DALI group (``POST /group/{id}/control``).

        Async version of :meth:`Client.control_group`.
        """
        await self._json("POST", f"/group/{group_id}/control", data.to_dict())

    async def control_zone(self, zone_id: int, data: ControlData) -> None:
        """Apply a :class:`ControlData` payload to a :class:`Zone` (``POST /zone/{id}/control``).

        Async version of :meth:`Client.control_zone`.
        """
        await self._json("POST", f"/zone/{zone_id}/control", data.to_dict())

    async def control_broadcast(self, data: ControlData) -> None:
        """Broadcast a :class:`ControlData` payload to every device (``POST /broadcast/control``).

        Async version of :meth:`Client.control_broadcast`.
        """
        await self._json("POST", "/broadcast/control", data.to_dict())

    # ----- link -----

    async def enable_linking(self) -> None:
        """Enable the gateway's linking (DALI commissioning) mode (``POST /link/enable``).

        Async version of :meth:`Client.enable_linking`.
        """
        await self._json("POST", "/link/enable")

    async def disable_linking(self) -> None:
        """Disable the gateway's linking mode (``POST /link/disable``).

        Async version of :meth:`Client.disable_linking`.
        """
        await self._json("POST", "/link/disable")

    # ----- DALI bus scan -----

    async def get_scan(self) -> Scan:
        """Return the current bus-scan progress (``GET /dali/scan``).

        Async version of :meth:`Client.get_scan`.
        """
        return _model(Scan, await self._json("GET", "/dali/scan"))

    async def start_scan(self, options: StartScan | None = None) -> Scan:
        """Start a DALI bus scan (``POST /dali/scan``).

        Args:
            options: Scan parameters (re-address, lines to scan, etc.).
                ``None`` triggers a default scan.

        Returns:
            The initial :class:`Scan` state. Poll :meth:`get_scan` for progress.

        Async version of :meth:`Client.start_scan`.
        """
        body = options.to_dict() if options else {}
        return _model(Scan, await self._json("POST", "/dali/scan", body))

    async def cancel_scan(self) -> Scan:
        """Cancel the running bus scan (``POST /dali/scan/cancel``).

        Async version of :meth:`Client.cancel_scan`.
        """
        return _model(Scan, await self._json("POST", "/dali/scan/cancel"))

    # ----- info / system -----

    async def get_info(self) -> Info:
        """Return gateway-wide :class:`Info` (firmware, hardware, bus health) (``GET /info``).

        Async version of :meth:`Client.get_info`.
        """
        return _model(Info, await self._json("GET", "/info"))

    async def update_info(self, info: InfoUpdate) -> Info:
        """Update editable :class:`Info` fields, currently just the device name (``PUT /info``).

        Async version of :meth:`Client.update_info`.
        """
        return _model(Info, await self._json("PUT", "/info", info.to_dict()))

    async def reset(self) -> None:
        """Factory-reset the gateway (``DELETE /reset``).

        Wipes configuration. Use with care — there's no confirmation step.

        Async version of :meth:`Client.reset`.
        """
        await self._json("DELETE", "/reset")

    async def reboot(self) -> None:
        """Reboot the gateway (``POST /reboot``). Configuration is preserved.

        Async version of :meth:`Client.reboot`.
        """
        await self._json("POST", "/reboot")

    # ----- date/time + location -----

    async def get_datetime(self) -> DateTime:
        """Return the gateway's current wall-clock state (``GET /datetime``).

        Async version of :meth:`Client.get_datetime`.
        """
        return _model(DateTime, await self._json("GET", "/datetime"))

    async def set_datetime(self, datetime: DateTime) -> DateTime:
        """Set the gateway's date/time and time-zone (``POST /datetime``).

        Async version of :meth:`Client.set_datetime`.
        """
        return _model(DateTime, await self._json("POST", "/datetime", datetime.to_dict()))

    async def get_timezones(self) -> TimeZones:
        """Return every time-zone identifier the gateway accepts (``GET /datetime/timezones``).

        Async version of :meth:`Client.get_timezones`.
        """
        return _model(TimeZones, await self._json("GET", "/datetime/timezones"))

    async def get_location(self) -> Location:
        """Return the gateway's configured :class:`Location` (``GET /location``).

        Async version of :meth:`Client.get_location`.
        """
        return _model(Location, await self._json("GET", "/location"))

    async def set_location(self, location: Location) -> Location:
        """Set the gateway's location, used for sunrise/sunset schedulers (``POST /location``).

        Async version of :meth:`Client.set_location`.
        """
        return _model(Location, await self._json("POST", "/location", location.to_dict()))

    async def detect_location(self) -> Location:
        """Auto-detect the gateway's location via its public IP (``POST /location/detect``).

        Async version of :meth:`Client.detect_location`.
        """
        return _model(Location, await self._json("POST", "/location/detect"))

    # ----- settings + ethernet -----

    async def get_settings(self) -> Settings:
        """Return protocol-level :class:`Settings` (``GET /settings``).

        Async version of :meth:`Client.get_settings`.
        """
        return _model(Settings, await self._json("GET", "/settings"))

    async def update_settings(self, settings: Settings) -> Settings:
        """Update protocol-level :class:`Settings` (``PUT /settings``).

        Async version of :meth:`Client.update_settings`.
        """
        return _model(Settings, await self._json("PUT", "/settings", settings.to_dict()))

    async def get_ethernet(self) -> Ethernet:
        """Return live :class:`Ethernet` status (MAC, settings, lease) (``GET /ethernet``).

        Async version of :meth:`Client.get_ethernet`.
        """
        return _model(Ethernet, await self._json("GET", "/ethernet"))

    async def update_ethernet(self, settings: EthernetSettings) -> Ethernet:
        """Apply new :class:`EthernetSettings` (``POST /ethernet``).

        Note: changing the IP address may sever the connection — the
        request itself succeeds, but follow-up calls will need the new URL.

        Async version of :meth:`Client.update_ethernet`.
        """
        return _model(Ethernet, await self._json("POST", "/ethernet", settings.to_dict()))

    # ----- zones -----

    async def list_zones(self) -> list[Zone]:
        """Return every configured :class:`Zone` (``GET /zones``).

        Async version of :meth:`Client.list_zones`.
        """
        return _model_list(Zone, await self._json("GET", "/zones"), "zones")

    async def delete_all_zones(self) -> None:
        """Delete every zone (``DELETE /zones``). Devices themselves are untouched.

        Async version of :meth:`Client.delete_all_zones`.
        """
        await self._json("DELETE", "/zones")

    async def get_zone(self, zone_id: int) -> Zone:
        """Fetch a single :class:`Zone` by id (``GET /zone/{id}``).

        Async version of :meth:`Client.get_zone`.
        """
        return _model(Zone, await self._json("GET", f"/zone/{zone_id}"))

    async def create_zone(self, zone: Zone) -> Zone:
        """Create a new :class:`Zone` (``POST /zone``).

        Leave :attr:`Zone.id` unset; the gateway assigns it.

        Async version of :meth:`Client.create_zone`.
        """
        return _model(Zone, await self._json("POST", "/zone", zone.to_dict()))

    async def update_zone(self, zone_id: int, zone: Zone) -> Zone:
        """Update an existing :class:`Zone` (``PUT /zone/{id}``).

        Async version of :meth:`Client.update_zone`.
        """
        return _model(Zone, await self._json("PUT", f"/zone/{zone_id}", zone.to_dict()))

    async def delete_zone(self, zone_id: int) -> None:
        """Delete a single zone (``DELETE /zone/{id}``).

        Async version of :meth:`Client.delete_zone`.
        """
        await self._json("DELETE", f"/zone/{zone_id}")

    # ----- email -----

    async def get_email_settings(self) -> MailSettings:
        """Return the configured :class:`MailSettings` (``GET /email``).

        The returned :attr:`MailSettings.mail_config.password` is a
        boolean presence flag, not the secret.

        Async version of :meth:`Client.get_email_settings`.
        """
        return _model(MailSettings, await self._json("GET", "/email"))

    async def update_email_settings(self, settings: MailSettingsInput) -> MailSettings:
        """Update :class:`MailSettings` (``PUT /email``).

        Pass plaintext SMTP credentials via :class:`MailSettingsInput`;
        the response (typed as :class:`MailSettings`) replaces the password
        with a presence flag.

        Async version of :meth:`Client.update_email_settings`.
        """
        return _model(MailSettings, await self._json("PUT", "/email", settings.to_dict()))

    async def test_email_settings(self) -> None:
        """Send a test email using the current configuration (``POST /email``).

        Async version of :meth:`Client.test_email_settings`.
        """
        await self._json("POST", "/email")

    # ----- sensors -----

    async def list_sensors(self) -> dict[str, object] | None:
        """Return all sensors known to the gateway (``GET /sensors``).

        The OpenAPI spec doesn't define a schema for the response body, so
        the raw JSON dict is returned unchanged.

        Async version of :meth:`Client.list_sensors`.
        """
        return await self._json("GET", "/sensors")

    async def refresh_sensors(self) -> None:
        """Trigger a re-poll of every sensor (``POST /sensors``).

        Async version of :meth:`Client.refresh_sensors`.
        """
        await self._json("POST", "/sensors")

    async def get_sensor(self, sensor_id: int) -> dict[str, object] | None:
        """Return the latest reading for one sensor (``GET /sensors/{id}``).

        The OpenAPI spec doesn't define a schema for the response body, so
        the raw JSON dict is returned unchanged.

        Async version of :meth:`Client.get_sensor`.
        """
        return await self._json("GET", f"/sensors/{sensor_id}")

    async def refresh_sensor(self, sensor_id: int) -> None:
        """Trigger a re-poll of one sensor (``POST /sensors/{id}``).

        Async version of :meth:`Client.refresh_sensor`.
        """
        await self._json("POST", f"/sensors/{sensor_id}")

    # ----- sequencer -----

    async def get_test_sequence(self) -> Sequence:
        """Return the gateway's "test" sequence — a sandbox slot (``GET /automations/sequence/test``).

        Async version of :meth:`Client.get_test_sequence`.
        """
        return _model(Sequence, await self._json("GET", "/automations/sequence/test"))

    async def update_test_sequence(self, sequence: Sequence) -> Sequence:
        """Replace the test sequence (``PUT /automations/sequence/test``).

        Async version of :meth:`Client.update_test_sequence`.
        """
        return _model(Sequence, await self._json("PUT", "/automations/sequence/test", sequence.to_dict()))

    async def create_sequence(self, sequence: Sequence) -> Sequence:
        """Create a new :class:`Sequence` (``POST /automations/sequence``).

        Async version of :meth:`Client.create_sequence`.
        """
        return _model(Sequence, await self._json("POST", "/automations/sequence", sequence.to_dict()))

    async def list_sequences(self) -> list[Sequence]:
        """Return every saved :class:`Sequence` (``GET /automations/sequences``).

        Async version of :meth:`Client.list_sequences`.
        """
        return _model_list(Sequence, await self._json("GET", "/automations/sequences"), "sequences")

    async def get_sequence(self, sequence_id: int) -> Sequence:
        """Fetch one :class:`Sequence` by id (``GET /automations/sequence/{id}``).

        Async version of :meth:`Client.get_sequence`.
        """
        return _model(Sequence, await self._json("GET", f"/automations/sequence/{sequence_id}"))

    async def update_sequence(self, sequence_id: int, sequence: Sequence) -> Sequence:
        """Update a saved :class:`Sequence` (``PUT /automations/sequence/{id}``).

        Async version of :meth:`Client.update_sequence`.
        """
        return _model(Sequence, await self._json("PUT", f"/automations/sequence/{sequence_id}", sequence.to_dict()))

    async def delete_sequence(self, sequence_id: int) -> None:
        """Delete one sequence (``DELETE /automations/sequence/{id}``).

        Async version of :meth:`Client.delete_sequence`.
        """
        await self._json("DELETE", f"/automations/sequence/{sequence_id}")

    async def start_sequence(self, sequence_id: int) -> None:
        """Begin executing a sequence (``POST /automations/sequence/{id}/start``).

        Async version of :meth:`Client.start_sequence`.
        """
        await self._json("POST", f"/automations/sequence/{sequence_id}/start")

    async def stop_sequence(self, sequence_id: int) -> None:
        """Stop a running sequence (``POST /automations/sequence/{id}/stop``).

        Async version of :meth:`Client.stop_sequence`.
        """
        await self._json("POST", f"/automations/sequence/{sequence_id}/stop")

    # ----- circadian -----

    async def list_circadians(self) -> list[Circadian]:
        """Return every :class:`Circadian` rhythm (``GET /automations/circadians``).

        Async version of :meth:`Client.list_circadians`.
        """
        return _model_list(Circadian, await self._json("GET", "/automations/circadians"), "circadians")

    async def create_circadian(self, circadian: Circadian) -> Circadian:
        """Create a new :class:`Circadian` rhythm (``POST /automations/circadian``).

        Async version of :meth:`Client.create_circadian`.
        """
        return _model(Circadian, await self._json("POST", "/automations/circadian", circadian.to_dict()))

    async def get_circadian(self, circadian_id: int) -> Circadian:
        """Fetch one :class:`Circadian` by id (``GET /automations/circadian/{id}``).

        Async version of :meth:`Client.get_circadian`.
        """
        return _model(Circadian, await self._json("GET", f"/automations/circadian/{circadian_id}"))

    async def update_circadian(self, circadian_id: int, circadian: Circadian) -> Circadian:
        """Update a saved :class:`Circadian` rhythm (``PUT /automations/circadian/{id}``).

        Async version of :meth:`Client.update_circadian`.
        """
        return _model(
            Circadian,
            await self._json("PUT", f"/automations/circadian/{circadian_id}", circadian.to_dict()),
        )

    async def delete_circadian(self, circadian_id: int) -> None:
        """Delete one circadian rhythm (``DELETE /automations/circadian/{id}``).

        Async version of :meth:`Client.delete_circadian`.
        """
        await self._json("DELETE", f"/automations/circadian/{circadian_id}")

    async def start_circadian(self, circadian_id: int) -> None:
        """Activate a circadian rhythm (``POST /automations/circadian/{id}/start``).

        Async version of :meth:`Client.start_circadian`.
        """
        await self._json("POST", f"/automations/circadian/{circadian_id}/start")

    async def stop_circadian(self, circadian_id: int) -> None:
        """Deactivate a circadian rhythm (``POST /automations/circadian/{id}/stop``).

        Async version of :meth:`Client.stop_circadian`.
        """
        await self._json("POST", f"/automations/circadian/{circadian_id}/stop")

    # ----- scheduler -----

    async def list_schedules(self) -> list[Scheduler]:
        """Return every :class:`Scheduler` (``GET /automations/schedules``).

        Async version of :meth:`Client.list_schedules`.
        """
        return _model_list(Scheduler, await self._json("GET", "/automations/schedules"), "schedulers")

    async def create_scheduler(self, scheduler: Scheduler) -> Scheduler:
        """Create a new :class:`Scheduler` (``POST /automations/scheduler``).

        Async version of :meth:`Client.create_scheduler`.
        """
        return _model(Scheduler, await self._json("POST", "/automations/scheduler", scheduler.to_dict()))

    async def get_scheduler(self, scheduler_id: int) -> Scheduler:
        """Fetch one :class:`Scheduler` by id (``GET /automations/scheduler/{id}``).

        Async version of :meth:`Client.get_scheduler`.
        """
        return _model(Scheduler, await self._json("GET", f"/automations/scheduler/{scheduler_id}"))

    async def update_scheduler(self, scheduler_id: int, scheduler: Scheduler) -> Scheduler:
        """Update a saved :class:`Scheduler` (``PUT /automations/scheduler/{id}``).

        Async version of :meth:`Client.update_scheduler`.
        """
        return _model(
            Scheduler,
            await self._json("PUT", f"/automations/scheduler/{scheduler_id}", scheduler.to_dict()),
        )

    async def delete_scheduler(self, scheduler_id: int) -> None:
        """Delete one scheduler (``DELETE /automations/scheduler/{id}``).

        Async version of :meth:`Client.delete_scheduler`.
        """
        await self._json("DELETE", f"/automations/scheduler/{scheduler_id}")

    async def start_scheduler(self, scheduler_id: int) -> None:
        """Activate a scheduler (``POST /automations/scheduler/{id}/start``).

        Async version of :meth:`Client.start_scheduler`.
        """
        await self._json("POST", f"/automations/scheduler/{scheduler_id}/start")

    async def stop_scheduler(self, scheduler_id: int) -> None:
        """Deactivate a scheduler (``POST /automations/scheduler/{id}/stop``).

        Async version of :meth:`Client.stop_scheduler`.
        """
        await self._json("POST", f"/automations/scheduler/{scheduler_id}/stop")

    # ----- trigger actions -----

    async def list_trigger_actions(self) -> list[TriggerAction]:
        """Return every :class:`TriggerAction` (``GET /automations/triggerActions``).

        Async version of :meth:`Client.list_trigger_actions`.
        """
        return _model_list(TriggerAction, await self._json("GET", "/automations/triggerActions"), "triggerActions")

    async def create_trigger_action(self, trigger_action: TriggerAction) -> TriggerAction:
        """Create a new :class:`TriggerAction` (``POST /automations/triggerAction``).

        Async version of :meth:`Client.create_trigger_action`.
        """
        return _model(
            TriggerAction,
            await self._json("POST", "/automations/triggerAction", trigger_action.to_dict()),
        )

    async def get_trigger_action(self, trigger_action_id: int) -> TriggerAction:
        """Fetch one :class:`TriggerAction` by id (``GET /automations/triggerAction/{id}``).

        Async version of :meth:`Client.get_trigger_action`.
        """
        return _model(TriggerAction, await self._json("GET", f"/automations/triggerAction/{trigger_action_id}"))

    async def update_trigger_action(self, trigger_action_id: int, trigger_action: TriggerAction) -> TriggerAction:
        """Update a saved :class:`TriggerAction` (``PUT /automations/triggerAction/{id}``).

        Async version of :meth:`Client.update_trigger_action`.
        """
        return _model(
            TriggerAction,
            await self._json("PUT", f"/automations/triggerAction/{trigger_action_id}", trigger_action.to_dict()),
        )

    async def delete_trigger_action(self, trigger_action_id: int) -> None:
        """Delete one trigger action (``DELETE /automations/triggerAction/{id}``).

        Async version of :meth:`Client.delete_trigger_action`.
        """
        await self._json("DELETE", f"/automations/triggerAction/{trigger_action_id}")

    async def start_trigger_action(self, trigger_action_id: int) -> None:
        """Activate a trigger action (``POST /automations/triggerAction/{id}/start``).

        Async version of :meth:`Client.start_trigger_action`.
        """
        await self._json("POST", f"/automations/triggerAction/{trigger_action_id}/start")

    async def stop_trigger_action(self, trigger_action_id: int) -> None:
        """Deactivate a trigger action (``POST /automations/triggerAction/{id}/stop``).

        Async version of :meth:`Client.stop_trigger_action`.
        """
        await self._json("POST", f"/automations/triggerAction/{trigger_action_id}/stop")
