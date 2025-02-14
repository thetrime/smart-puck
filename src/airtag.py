"""
Find AirTags that you own without involving Apple in the process
"""
from binascii import unhexlify
from time import time
from collections import deque
import nist224p
from udatetime import format_date, iso8601_to_timestamp, timestamp_to_iso8601
import x963
import asyncio

keys = []
debugging = True
ENDIANNESS = "big"
WINDOW_SIZE = 8

def debug(string):
    if (debugging):
        print(string)

def handle_airtag(address, data, rssi, then):
    timestamp = time()
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

    # Ok, look to see if this corresponds to one of our devices
    for index, key in enumerate(keys):
        for pindex, candidate in enumerate(list(key['advertised_prefixes'])):
            if candidate.startswith(key_prefix):
                print(f"Tag {key['name']} detected with prefix {key_prefix} (index {pindex}) at distance {rssi} at {format_date(timestamp)}Z")
                then(key['name'], index, rssi)
                return

    # print(f"Unknown Apple device with prefix {key_prefix} detected at strength {rssi} dBm at {format_date(timestamp)}Z")

def update_key(key, update_advertised):
    """
    Update a given key to the next key period
    """
    t_i = key['time'] + 15*60

    # Derive SK_1 from SK_0
    sk_1 = x963.kdf(key['shared_key'], 32, "update")
    
    print(f"Updating key {key['name']} to be current from {timestamp_to_iso8601(t_i)}Z")
    if update_advertised:
        
        # Derive AT_1 from SK_1
        at_1 = x963.kdf(sk_1, 72, "diversify")

        # Derive u_1 and v_1 from this
        u_1 = int.from_bytes(at_1[:36], ENDIANNESS)
        v_1 = int.from_bytes(at_1[36:], ENDIANNESS)

        # Reduce u and v into P-224 scalars
        u_1 = nist224p.reduce(u_1)
        v_1 = nist224p.reduce(v_1)

        # Compute P_1
        p_1 = nist224p.compute_result(u_1, key['p_0'], v_1)

        # The deque is initially empty
        if len(key['advertised_times']) == WINDOW_SIZE:
            debug(f"At {timestamp_to_iso8601(time())}Z we are dropping old key for {key['name']} that was valid at {timestamp_to_iso8601(key['advertised_times'][0])}Z: ${key['advertised_prefixes'][0]}")
        # We only really care about the first 6 bytes of the key.
        # In the near-to-owner case, this is all that is advertised..
        # The full key is only needed if we want to upload a finding-report to Apple
        new_prefix = hex(p_1[0])[0:14]
        print(f"Expecting prefix for {key['name']} to be {new_prefix} at {timestamp_to_iso8601(t_i)}Z (it is currently {timestamp_to_iso8601(time())}Z)")
        key['advertised_prefixes'].append(new_prefix)
        key['advertised_times'].append(t_i)
        print(f"We now have prefixes for {key['name']} from {timestamp_to_iso8601(key['advertised_times'][0])}Z to {timestamp_to_iso8601(key['advertised_times'][-1])}Z")

    # Regardless of the prefix stuff, we need to update these values
    key['time'] = t_i
    key['shared_key'] = sk_1


def parse_key_line(line):
    chunks = line.split(" ")
    sync_time = chunks[0]
    t_0 = iso8601_to_timestamp(sync_time)
    pkx = chunks[2][2:58]
    pky = chunks[2][58:]
    
    # Micropython doesnt have ecdsa support so I cannot just construct a Point.
    # Store p_0 as a tuple. We know which curve it is.
    p_0 = (int.from_bytes(unhexlify(pkx), ENDIANNESS), int.from_bytes(unhexlify(pky), ENDIANNESS))

    
    return {
        'time': t_0,
        'shared_key': unhexlify(chunks[1]),
        'p_0': p_0,
        'public_key': chunks[2],
        'name': " ".join(chunks[3:]),
        'advertised_prefixes': deque([], WINDOW_SIZE),
        'advertised_times': deque([], WINDOW_SIZE),
        'trace': unhexlify(chunks[1]),
        'trace_time': t_0
    }


def load_keys(filename):
    """
    Load stashed keys
    """
    keyfile = open(filename, "r", encoding="utf-8")
    min_t = time() - 12*60*60
    key_lines = keyfile.read().splitlines()
    for line in key_lines:
        if line.startswith("#"):
            continue
        key = parse_key_line(line)
        if key['time'] < min_t:
            min_t = key['time']
        keys.append(key)
    keyfile.close()


def rehydrate_keys():
    """
    Refresh all keys until they are at most 4 hours old
    """
    # Get all the keys up to date as of 4 hours ago
    oldest = time()
    for key in keys:
        i = 0
        original_time = key['time']
        if original_time < oldest:
            oldest = original_time
        print(f"Rehydrating key {key['name']} which was last stashed with timestamp {timestamp_to_iso8601(key['time'])}Z\n")
        while key['time'] < time() - 4 * 60 * 60:
            p = 100 * ((key['time'] - original_time) /
                       (time() - 4 * 60 * 60 - original_time))
            i += 1
            if i == 96:
                # Provide a periodic update in case this is going to take a long time
                i = 0
                print(f"{p:.2f}% {key['name']}")
                print(f"Key {key['name']} is at {timestamp_to_iso8601(key['time'])}Z")
            update_key(key, False)
        print(f"{100}% {key['name']}")
    return time() - oldest


def stash_keys(filename):
    """
    Save current key state
    """
    # Save keys so we dont have to do this next time
    print("Stashing keys")
    out = open(filename, "w", encoding="utf-8")
    for key in keys:
        out.write(
            timestamp_to_iso8601(key['trace_time']) +
            "Z " +
            key['trace'].hex() +
            " " +
            key['public_key'] +
            " " +
            key['name'] +
            "\n"
        )
    out.close()



def update_keys():
    for key in keys:
        while key['time'] < time() + (WINDOW_SIZE/2) * 15 * 60:
            print(f"Key {key['name']} needs updating because it has time {format_date(key['time'])}Z but the end window is {format_date(int(time() + (WINDOW_SIZE/2) * 15 * 60))}Z\n")
            update_key(key, True)
    print("Key schedule is current")


async def keyroller():
    """
    Update keys until there are WINDOW_SIZE advertised keys available, with the current time
    being the middle of the array
    """
    last_stash = time()
    while True:
        update_keys()
        await asyncio.sleep(60)
        # If more than 24 hours has passed since we last stashed the keys then stash them again
        # This is safe in general because only this thread ever updates the key structure (once the boot is finished)
        if time() - last_stash > 86400:
            stash_keys("keys")
            last_stash = time()


def airtag_setup(filename):
    """
    Prepare the key data in filename
    """
    print("Loading keys")
    load_keys(filename)
    print(f"Loaded {len(keys)} keys. Rehydrating...")
    key_age = rehydrate_keys()
    print(f"Keys rehydrated. They had been frozen for {key_age} seconds")
    if key_age > 86400:
        print("Keys are older than 24 hours. Stashing rehydrated keys")
        stash_keys(filename)
    # Now bring them up to date
    update_keys()


if __name__ == "__main__":
    setup('keys')