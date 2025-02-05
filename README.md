# Smart Puck
> But what if we went _smaller_?

Details to follow. For now, this is just some notes on setting it up.

First, install the aioble and urequests package onto the pico using Thonny or with this:
```
import network
import mip
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(<your wifi SSID>, <your wifi password>)
mip.install('aioble')
mip.install('urequests')
```


