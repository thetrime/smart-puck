import asyncio
from scanner import scan_devices
import airtag

async def main():
    # To do: set up IO, check LED status source
    airtag.setup("keys")

    # Start scanning
    scan_task = asyncio.create_task(scan_devices())

    # Down here we can control the LEDs
    while True:
        print("Main program running...")  
        await asyncio.sleep(5)  # Placeholder for other tasks to run concurrently

asyncio.run(main())