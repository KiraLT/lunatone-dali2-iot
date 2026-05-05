"""Client library for the Lunatone Dali-2 IoT gateway.

`dali2iot` is a small typed wrapper around the gateway's REST and
WebSocket APIs. The public surface is:

- :class:`Client` and :class:`AsyncClient` — sync and async HTTP clients
  with a method per OpenAPI operation.
- :class:`WebSocketClient` (in :mod:`dali2iot.websocket`) — async client
  for the streaming event API, with a typed :class:`Event` per wire type.
- :mod:`dali2iot.models` — dataclasses for every request body and
  response shape (devices, zones, sequences, schedulers, circadians,
  trigger actions, info, settings, ethernet, mail, …).
- :class:`ApiError` / :class:`DaliIotError` — exceptions raised on
  non-2xx responses.

The HTTP shapes mirror ``openapi.json`` at the repo root; consult that
file when you need the underlying schema. The websocket events mirror
the streaming JSON protocol the gateway emits on its root ``ws://``
endpoint.

Example
-------

::

    from dali2iot import Client, ControlData, RGB

    with Client(base_url="http://192.168.1.41") as c:
        for device in c.list_devices():
            print(device.id, device.name)

        c.update_device(1, name="Hall")
        c.control_device(1, ControlData(dimmable_rgb=RGB(r=1, g=0, b=0, dimmable=80)))

Streaming events::

    import asyncio
    from dali2iot import WebSocketClient, DevicesEvent

    async def main() -> None:
        async with WebSocketClient(base_url="http://192.168.1.41") as ws:
            async for event in ws:
                if isinstance(event, DevicesEvent):
                    for d in event.devices:
                        print("update", d.id, d.features)

    asyncio.run(main())
"""

from .client import AsyncClient, Client
from .errors import ApiError, DaliIotError
from .models import (
    RGB,
    WAF,
    XY,
    ActionTypes,
    ActiveDays,
    ActiveMonths,
    ActivePeriod,
    ActiveWeekDays,
    Circadian,
    CircadianCurve,
    CircadianStep,
    ControlData,
    DaliBus,
    DateTime,
    Device,
    DeviceTarget,
    DeviceType,
    Ethernet,
    EthernetSettings,
    Info,
    InfoUpdate,
    Kelvin,
    LineStatus,
    Location,
    MailConfig,
    MailConfigInput,
    MailSettings,
    MailSettingsInput,
    Model,
    NotificationSettings,
    Scan,
    ScanState,
    Scheduler,
    SchedulerAction,
    SchedulerRecallModes,
    SchedulerTime,
    Sequence,
    SequencerAction,
    SequenceStep,
    Settings,
    Signature,
    SmtpSecurity,
    StartScan,
    TestNotificationSettings,
    TimeZones,
    TriggerAction,
    TriggerActionSource,
    TriggerActionSourceType,
    YnDescriptor,
    YnDeviceInfo,
    Zone,
)
from .websocket import (
    CircadiansDeletedEvent,
    CircadiansEvent,
    DaliAnswerEvent,
    DaliFrame,
    DaliFrameEvent,
    DaliFrameMode,
    DaliMonitorEvent,
    DaliStatusEvent,
    DateTimeEvent,
    DevicesDeletedEvent,
    DevicesEvent,
    Event,
    Filter,
    InfoEvent,
    MessageFlashEvent,
    PingEvent,
    ScanProgressEvent,
    SchedulersDeletedEvent,
    SchedulersEvent,
    SequencesDeletedEvent,
    SequencesEvent,
    TriggerActionsDeletedEvent,
    TriggerActionsEvent,
    UnknownEvent,
    WebSocketClient,
    ZonesDeletedEvent,
    ZonesEvent,
    parse_event,
)

__version__ = "1.1.0"

__all__ = (
    "RGB",
    "WAF",
    "XY",
    "ActionTypes",
    "ActiveDays",
    "ActiveMonths",
    "ActivePeriod",
    "ActiveWeekDays",
    "ApiError",
    "AsyncClient",
    "Circadian",
    "CircadianCurve",
    "CircadianStep",
    "CircadiansDeletedEvent",
    "CircadiansEvent",
    "Client",
    "ControlData",
    "DaliAnswerEvent",
    "DaliBus",
    "DaliFrame",
    "DaliFrameEvent",
    "DaliFrameMode",
    "DaliIotError",
    "DaliMonitorEvent",
    "DaliStatusEvent",
    "DateTime",
    "DateTimeEvent",
    "Device",
    "DeviceTarget",
    "DeviceType",
    "DevicesDeletedEvent",
    "DevicesEvent",
    "Ethernet",
    "EthernetSettings",
    "Event",
    "Filter",
    "Info",
    "InfoEvent",
    "InfoUpdate",
    "Kelvin",
    "LineStatus",
    "Location",
    "MailConfig",
    "MailConfigInput",
    "MailSettings",
    "MailSettingsInput",
    "MessageFlashEvent",
    "Model",
    "NotificationSettings",
    "PingEvent",
    "Scan",
    "ScanProgressEvent",
    "ScanState",
    "Scheduler",
    "SchedulerAction",
    "SchedulerRecallModes",
    "SchedulerTime",
    "SchedulersDeletedEvent",
    "SchedulersEvent",
    "Sequence",
    "SequencerAction",
    "SequenceStep",
    "SequencesDeletedEvent",
    "SequencesEvent",
    "Settings",
    "Signature",
    "SmtpSecurity",
    "StartScan",
    "TestNotificationSettings",
    "TimeZones",
    "TriggerAction",
    "TriggerActionSource",
    "TriggerActionSourceType",
    "TriggerActionsDeletedEvent",
    "TriggerActionsEvent",
    "UnknownEvent",
    "WebSocketClient",
    "YnDescriptor",
    "YnDeviceInfo",
    "Zone",
    "ZonesDeletedEvent",
    "ZonesEvent",
    "parse_event",
)
