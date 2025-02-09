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
A shell script is available for bash users. `mpremote cp *.py :` doesn't work on Windows. A workaround is to stop using Windows.

That's it. Reboot and it's ready!

# To do list
## Code
   * We never stash the keys. Change the logic to stash them once a day, instead of every time we roll them
   * The window is probably way too big. Reducing it will massively speed up the startup
   * The deque has a fixed length. We don't need to manage it explicitly like we did in the full version

## Hardware
Finish the schematic and PCB design
Create a STL for the case
