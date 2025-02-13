"""
Entry point for the smart-puck application
"""

import asyncio
import network
import ntptime
from time import sleep
from scanner import scan_devices
from bins import bin_updater
from illuminated_switch import IlluminatedSwitch
from picozero import LED, Button, Buzzer
from airtag import airtag_setup, keyroller


binLEDs = {
    "Blue": LED(18),
    "Green": LED(19),
    "Brown": LED(20),
    "Black": LED(21)
}

doorbell = Buzzer(9)

def ring_doorbell():
    doorbell.on(1, 1, False)

# The order of these has to match the order of the keys in the keys file
airtags = {
    IlluminatedSwitch(LED(1), Button(2), ring_doorbell),
    IlluminatedSwitch(LED(8), Button(9), ring_doorbell)
}

async def bins_updated(to):
    for colour, state in to:
        binLEDs[colour].value = state

async def airtag_found(_name, index, rssi):
    airtags[index].found(rssi)


async def main():
    binLEDs['Blue'].blink(1)
    with open('wifi', 'r') as file:
        ssid = file.readline().strip()
        password = file.readline().strip()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for wifi connection...')
        sleep(1)
    print("Connected!")
    binLEDs['Blue'].on()
    binLEDs['Green'].blink()

    # Now we have internet, set the time
    ntptime.settime()

    # To do: set up IO, check LED status source
    airtag_setup("keys")
    binLEDs['Green'].on()


    for led in binLEDs:
        binLEDs[led].off()

    # Start scanning
    asyncio.create_task(scan_devices(airtag_found))

    # Start updating bins
    asyncio.create_task(bin_updater(bins_updated))

    # Start keyroller
    asyncio.create_task(keyroller())

    # Wait forever
    await asyncio.Event().wait()

asyncio.run(main())