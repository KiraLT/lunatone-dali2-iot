"""Client library for the Lunatone Dali-2 IoT gateway.

`dali2iot` is a small typed wrapper around the gateway's REST API. The
public surface is:

- :class:`Client` and :class:`AsyncClient` — sync and async HTTP clients
  with a method per OpenAPI operation.
- :mod:`dali2iot.models` — dataclasses for every request body and
  response shape (devices, zones, sequences, schedulers, circadians,
  trigger actions, info, settings, ethernet, mail, …).
- :class:`ApiError` / :class:`DaliIotError` — exceptions raised on
  non-2xx responses.

The HTTP shapes mirror ``openapi.json`` at the repo root; consult that
file when you need the underlying schema.

Example
-------

::

    from dali2iot import Client, ControlData, RGB

    with Client(base_url="http://192.168.1.41") as c:
        for device in c.list_devices():
            print(device.id, device.name)

        c.update_device(1, name="Hall")
        c.control_device(1, ControlData(dimmable_rgb=RGB(r=1, g=0, b=0, dimmable=80)))
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
    "Client",
    "ControlData",
    "DaliBus",
    "DaliIotError",
    "DateTime",
    "Device",
    "DeviceTarget",
    "DeviceType",
    "Ethernet",
    "EthernetSettings",
    "Info",
    "InfoUpdate",
    "Kelvin",
    "LineStatus",
    "Location",
    "MailConfig",
    "MailConfigInput",
    "MailSettings",
    "MailSettingsInput",
    "Model",
    "NotificationSettings",
    "Scan",
    "ScanState",
    "Scheduler",
    "SchedulerAction",
    "SchedulerRecallModes",
    "SchedulerTime",
    "Sequence",
    "SequencerAction",
    "SequenceStep",
    "Settings",
    "Signature",
    "SmtpSecurity",
    "StartScan",
    "TestNotificationSettings",
    "TimeZones",
    "TriggerAction",
    "TriggerActionSource",
    "TriggerActionSourceType",
    "YnDescriptor",
    "YnDeviceInfo",
    "Zone",
)
