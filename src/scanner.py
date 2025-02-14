"""
Scan for bluetooth devices and call the callback if we find an Apple device reporting it is paired
"""
import aioble
from airtag import handle_airtag

APPLE = 0x004c
STATUS_PAIRED = 0x12

def handle_device(result, then):
    for manufacturer_id, manufacturer_data in result.manufacturer():
        if manufacturer_id == APPLE:
            #print(f"Found apple device at distance {result.rssi} with {manufacturer_data}")
            if manufacturer_data[0] == STATUS_PAIRED:
                #print("Found apple device")
                # We found an Apple device
                # Drop the first two bytes. The code expects to see the body of the advertisement
                # adv_data is the header+body, and manufacturer_data has part of the header removed.
                # Annoying
                handle_airtag(result.device.addr, result.adv_data[2:], result.rssi, then)

async def scan_devices(then):
    print("Starting continuous BLE scan...")
    async with aioble.scan(duration_ms=0, interval_us=11250, window_us=11250) as scanner:  # 0 means scan indefinitely
        async for result in scanner:
            handle_device(result, then)
    