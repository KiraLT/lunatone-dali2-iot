# Lunatone Dali-2 IOT

A client library for accessing Lunatone Dali IoT gateway.

Read [Documentation 📘](https://kiralt.github.io/lunatone-dali2-iot/)

## Installation

```bash
pip install lunatone-dali2-iot
```

## Usage

Synchronous:

```python
from dali2iot import Client, ControlData, RGB

with Client(base_url="http://192.168.1.41") as client:
    for device in client.list_devices():
        print(f"#{device.id} {device.name}")

    client.update_device(1, name="WC RGBW Led")
    client.control_device(1, ControlData(dimmable_rgb=RGB(r=0, g=0, b=1, dimmable=100)))
```

Asynchronous:

```python
from dali2iot import AsyncClient

async with AsyncClient(base_url="http://192.168.1.41") as client:
    devices = await client.list_devices()
    for device in devices:
        print(device.name)
```

## Reference

The HTTP surface mirrors `openapi.json` (kept at the repo root). Add new
methods to `dali2iot/client.py` as you need them — one per OpenAPI
operation. Models live in `dali2iot/models.py`.
