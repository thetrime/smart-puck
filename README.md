# Smart Puck
> But what if we went _smaller_?

# Configuration
You need three config files to run smart-puck. See the README.md file in the `config` directory

# Prerequisites
Obviously you need the hardware. 
FIXME: Details to be filled in once I work out what the hardware is ^^

You also need:
   * python
   * pip

# Installation
A shell script is available for bash users. (`mpremote cp *.py :` doesn't work on Windows). A workaround is to stop using Windows.

You can install it by just running `./install.sh` after plugging in your pico. Note that you also have to flash the Micropython firmware to it first.

That's it. Reboot and it's ready!

# To do list
## Code
   * We never stash the keys. Change the logic to stash them once a day, instead of every time we roll them
   * The window is probably way too big. Reducing it will massively speed up the startup
   * The deque has a fixed length. We don't need to manage it explicitly like we did in the full version

## Hardware
Finish the schematic and PCB design
Create a STL for the case
