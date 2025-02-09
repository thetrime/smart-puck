import network
import mip
from time import sleep

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

mip.install('aioble')
mip.install('urequests')
mip.install('https://raw.githubusercontent.com/RaspberryPiFoundation/picozero/master/picozero/picozero.py')