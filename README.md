# Lunatone Dali-2 IoT

Typed Python client for the [Lunatone DALI-2 IoT](https://www.lunatone.com/en/products/dali-control-equipment/dali-2-iot/) gateway, covering both the REST API and the streaming WebSocket API.

📘 **[Full API documentation](https://kiralt.github.io/lunatone-dali2-iot/)**

## Features

- Sync (`Client`) and async (`AsyncClient`) HTTP clients — one method per OpenAPI operation, all 71 of them.
- Async streaming `WebSocketClient` with one typed dataclass per wire event (devices, zones, sequences, schedulers, circadians, trigger actions, DALI bus traffic, datetime, ping, message flash).
- Typed dataclasses for every request body and response (`Device`, `Zone`, `Scheduler`, `ControlData`, `Info`, `EthernetSettings`, …) — no `Any`, no dict guessing.
- Single source of truth: the REST shapes mirror [`openapi.json`](openapi.json); the WebSocket shapes mirror the streaming JSON protocol the gateway emits on its root `ws://` endpoint.

## Installation

```bash
pip install lunatone-dali2-iot
```

## REST API

### Synchronous

```python
from dali2iot import Client, ControlData, Kelvin, RGB

with Client(base_url="http://192.168.1.41") as client:
    for device in client.list_devices():
        print(f"#{device.id} {device.name} — {device.dali_types}")

    client.update_device(1, name="Hall light", groups=[0, 1])

    # Apply RGB at 100 % brightness
    client.control_device(1, ControlData(dimmable_rgb=RGB(r=1, g=0, b=0, dimmable=100)))

    # Or warm white at 30 %
    client.control_device(1, ControlData(dimmable_kelvin=Kelvin(kelvin=2700, dimmable=30)))
```

### Asynchronous

```python
import asyncio
from dali2iot import AsyncClient, ControlData

async def main() -> None:
    async with AsyncClient(base_url="http://192.168.1.41") as client:
        for device in await client.list_devices():
            print(device.id, device.name)

        await client.control_device(1, ControlData(dimmable=50))

asyncio.run(main())
```

### Coverage

Every operation in [`openapi.json`](openapi.json) has a method on both clients, grouped by tag:

| Tag | Methods |
| --- | --- |
| `devices` | `list_devices`, `get_device`, `update_device`, `delete_device`, `delete_all_devices` |
| `control` | `control_device`, `control_group`, `control_zone`, `control_broadcast` |
| `zones` | `list_zones`, `get_zone`, `create_zone`, `update_zone`, `delete_zone`, `delete_all_zones` |
| `dali` (scan) | `get_scan`, `start_scan`, `cancel_scan` |
| `link` | `enable_linking`, `disable_linking` |
| `info / system` | `get_info`, `update_info`, `reset`, `reboot` |
| `datetime / location` | `get_datetime`, `set_datetime`, `get_timezones`, `get_location`, `set_location`, `detect_location` |
| `settings / ethernet` | `get_settings`, `update_settings`, `get_ethernet`, `update_ethernet` |
| `email` | `get_email_settings`, `update_email_settings`, `test_email_settings` |
| `sensors` | `list_sensors`, `get_sensor`, `refresh_sensors`, `refresh_sensor` |
| `sequencer` | `list_sequences`, `get_sequence`, `create_sequence`, `update_sequence`, `delete_sequence`, `start_sequence`, `stop_sequence`, `get_test_sequence`, `update_test_sequence` |
| `circadian` | `list_circadians`, `get_circadian`, `create_circadian`, `update_circadian`, `delete_circadian`, `start_circadian`, `stop_circadian` |
| `scheduler` | `list_schedules`, `get_scheduler`, `create_scheduler`, `update_scheduler`, `delete_scheduler`, `start_scheduler`, `stop_scheduler` |
| `trigger-actions` | `list_trigger_actions`, `get_trigger_action`, `create_trigger_action`, `update_trigger_action`, `delete_trigger_action`, `start_trigger_action`, `stop_trigger_action` |

## WebSocket API

The gateway streams JSON events covering device updates, automation changes, raw DALI bus traffic, and connection health. Every wire event has a typed class — use `match`/`isinstance` to dispatch.

```python
import asyncio
from dali2iot import (
    DevicesEvent,
    DevicesDeletedEvent,
    PingEvent,
    ScanProgressEvent,
    WebSocketClient,
)

async def main() -> None:
    async with WebSocketClient(base_url="http://192.168.1.41") as ws:
        async for event in ws:
            match event:
                case DevicesEvent(devices=devs):
                    for d in devs:
                        print("device update:", d.id, d.features)
                case DevicesDeletedEvent(deleted=ids):
                    print("forgotten:", ids)
                case ScanProgressEvent(scan=scan):
                    print(f"scan {scan.progress * 100:.0f}% — {scan.status}")
                case PingEvent(echo=msg):
                    print("ping", msg)

asyncio.run(main())
```

### Filtering noisy events

```python
from dali2iot import Filter, WebSocketClient

async with WebSocketClient(base_url="http://192.168.1.41") as ws:
    await ws.set_filter(Filter(dali_monitor=True))   # suppress DaliMonitorEvent
```

### Direct DALI bus access

```python
from dali2iot import DaliFrame, DaliFrameMode, WebSocketClient, DaliAnswerEvent

async with WebSocketClient(base_url="http://192.168.1.41") as ws:
    # QUERY CONTROL GEAR PRESENT to address 0
    await ws.send_dali_frame(DaliFrame(
        line=0, number_of_bits=16,
        mode=DaliFrameMode(wait_for_answer=True, priority=3),
        dali_data=[1, 145],
    ))

    async for event in ws:
        if isinstance(event, DaliAnswerEvent):
            print("bus replied:", event.dali_data)
            break
```

### Event types

`InfoEvent`, `PingEvent`, `MessageFlashEvent`, `DateTimeEvent`, `DaliStatusEvent`, `DaliMonitorEvent`, `DaliFrameEvent`, `DaliAnswerEvent`, `ScanProgressEvent`, `DevicesEvent` / `DevicesDeletedEvent`, `ZonesEvent` / `ZonesDeletedEvent`, `SequencesEvent` / `SequencesDeletedEvent`, `SchedulersEvent` / `SchedulersDeletedEvent`, `CircadiansEvent` / `CircadiansDeletedEvent`, `TriggerActionsEvent` / `TriggerActionsDeletedEvent`, plus `UnknownEvent` for anything new.

## Project layout

```
dali2iot/
  __init__.py     # public re-exports
  client.py       # Client + AsyncClient (REST)
  websocket.py    # WebSocketClient + 21 event classes
  models.py       # typed dataclasses for every entity / request body
  errors.py       # ApiError, DaliIotError
openapi.json      # REST schema reference
```

## License

MIT
