import asyncio
from airtag import scan_devices

async def main():
    # To do: Hydrate keys, set up IO, check LED status source

    # Start scanning
    scan_task = asyncio.create_task(scan_devices())

    # Down here we can control the LEDs
    while True:
        print("Main program running...")  
        await asyncio.sleep(5)  # Placeholder for other tasks to run concurrently

asyncio.run(main())