"""
Scan for bluetooth devices
"""
import aioble
import time
from airtag import handle_airtag

APPLE = 0x004c
STATUS_PAIRED = 0x12

async def handle_device(result):
    # The data looks something like 07ff4c0012029401
    for manufacturer_id, manufacturer_data in result.manufacturer():
        if manufacturer_id == APPLE and manufacturer_data[0] == STATUS_PAIRED:
            # We found an Apple device
            # Drop the first two bytes. The code expects to see the body of the advertisement
            # adv_data is the header+body, and manufacturer_data has part of the header removed.
            # Annoying
            await handle_airtag(result.device.addr, result.adv_data[2:], result.rssi)

async def scan_devices():
    print("Starting continuous BLE scan...")
    async with aioble.scan(duration_ms=0) as scanner:  # 0 means scan indefinitely
        async for result in scanner:
            await handle_device(result)
