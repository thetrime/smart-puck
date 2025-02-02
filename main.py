import asyncio
from airtag import scan_devices

async def main():
    # To do: Hydrate keys, set up IO, configure wifi

    # Start scanning
    scan_task = asyncio.create_task(scan_devices())

    # Down here we can control the LEDs based on internet data
    while True:
        print("TODO: Something useful here")  
        await asyncio.sleep(5) 

asyncio.run(main())