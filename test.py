from dali2iot import Client
from dali2iot.api.devices import get_devices_devices_get

dali_client = Client(base_url="http://192.168.1.41")

async def run():
    async with dali_client as client:
        devices = get_devices_devices_get.sync(client=client)

        for device in devices.devices:
            print(device.name)


