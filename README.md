# Smart Puck
> But what if we went _smaller_?

# Configuration
You need three config files to run smart-puck:

## wifi
This is a file with two lines. The first is your SSID. The second is your password. Easy.

## uprn
This is the unique property reference number. You can find yours at https://www.findmyaddress.co.uk/search
Note that the bin lights only work for Fife. If you live outside of Fife, a simple workaround is to move here.

## keys
These can be generated using the code in the knock-knock project. Eventually I will duplicate that code in here

# Prerequisites
Obviously you need the hardware. 
FIXME: Details to be filled in once I work out what the hardware is ^^

You also need:
   * python
   * pip

# Installation

First copy in the code and the config. According to sources online, wildcards can be passed. In practise, mpremote seems to think they can't

```shell
pip install mpremote
mpremote cp main.py :
mpremote cp airtag.py :
mpremote cp bins.py :
mpremote cp illuminated_switch.py :
mpremote cp nist224p.py :
mpremote cp scanner.py : 
mpremote cp udatetime.py :
mpremote cp x963.py :
mpremote cp install.py :
mpremote cp keys :
mpremote cp uprn :
mpremote cp wifi :
```

Now install the packages we need:
```shell
mpremote run install.py
```

That's it. Reboot and it's ready!