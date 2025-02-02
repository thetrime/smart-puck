import aioble

async def handle_device(result):
    print(f"Device: {result.address}, Name: {result.name()}, RSSI: {result.rssi}, Services: {result.services()}")

async def scan_devices():
    print("Starting continuous BLE scan...")
    async with aioble.scan(duration_ms=0) as scanner:  # 0 means scan indefinitely
        async for result in scanner:
            await handle_device(result)
