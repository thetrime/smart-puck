First, install the aioble package onto the pico using Thonny or with this:
```
import network
import mip
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(<your wifi SSID>, <your wifi password>)
mip.install('aioble')
```


