"""
Entry point for the smart-puck application
"""

import asyncio
import network
from time import sleep
from scanner import scan_devices
from bins import bin_updater
from illuminated_switch import IlluminatedSwitch
from picozero import LED, Button, Buzzer
import airtag


binLEDs = {
    "Blue": LED(1),
    "Green": LED(2),
    "Brown": LED(3),
    "Black": LED(4)
}

doorbell = Buzzer(9)

def ring_doorbell():
    doorbell.on(1, 1, False)

# The order of these has to match the order of the keys in the keys file
airtags = {
    IlluminatedSwitch(LED(5), Button(7), ring_doorbell),
    IlluminatedSwitch(LED(6), Button(8), ring_doorbell)
}

async def bins_updated(to):
    for colour, state in to:
        binLEDs[colour].value = state

async def airtag_found(_name, index, rssi):
    airtags[index].found(rssi)


async def main():
    with open('wifi', 'r') as file:
        ssid = file.readline().strip()
        password = file.readline().strip()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print("Connected!")

    # To do: set up IO, check LED status source
    airtag.setup("keys")

    # Start scanning
    asyncio.create_task(scan_devices(airtag_found))

    # Start updating bins
    asyncio.create_task(bin_updater(bins_updated))

    # Wait forever
    await asyncio.Event().wait()

asyncio.run(main())