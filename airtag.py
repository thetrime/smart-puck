import aioble
import utime

APPLE = 0x004c
STATUS_PAIRED = 0x12

def format_date(timestamp):
    time_tuple = utime.gmtime(timestamp)
    return "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}".format(time_tuple[0], time_tuple[1], time_tuple[2], time_tuple[3], time_tuple[4], time_tuple[5])

async def handle_airtag(address, data, rssi):
    timestamp = utime.time()
    
    print("Found apple device at address: " + address.hex())
    first_byte = address[0] & 0b00111111
    key_prefix = address[1:].hex()
    if data[3] == 25:
       # Full key. Rest of the key is in val[8:..]
       # but we don't really need it - just the prefix
       special_bits = data[27]
    elif data[3] == 2:  # Partial key
       special_bits = data[5]
    else:
      print(f"Bad special bits {data[5]}")
    first_byte |= ((special_bits << 6) & 0b11000000)
    first_byte &= 0xff
    if first_byte < 0x10:
        key_prefix = "0x0" + hex(first_byte)[2] + key_prefix
    else:
        key_prefix = hex(first_byte) + key_prefix
    # To do: Look up key in array to see if it is for a device we know
    print(f"Unknown Apple device with prefix {key_prefix} detected at strength {rssi} dBm at {format_date(timestamp)}Z")
       

async def handle_device(result):
    # The data looks something like 07ff4c0012029401
    for manufacturer_id, manufacturer_data in result.manufacturer():
        if manufacturer_id == APPLE and manufacturer_data[0] == STATUS_PAIRED:
            # We found ourselves an airtag!
            print("Airtag. Payload is " + result.adv_data.hex())
            # Drop the first two bytes. The code expects to see the body of the advertisement
            # adv_data is the header+body, and manufacturer_data has part of the header removed.
            # Annoying
            await handle_airtag(result.device.addr, result.adv_data[2:], result.rssi)

async def scan_devices():
    print("Starting continuous BLE scan...")
    async with aioble.scan(duration_ms=0) as scanner:  # 0 means scan indefinitely
        async for result in scanner:
            await handle_device(result)
