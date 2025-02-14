"""
A class representing an illuminated switch to control an Airtag
"""

from machine import Timer
import time

OFF = 0
PRIMING = 1
ARMED = 2

TIMEOUT = 120_000
#TIMEOUT = 30_000

class IlluminatedSwitch:
    def __init__(self, led, switch, trigger):
        self.led = led
        self.switch = switch
        self.state = OFF
        self.timer = Timer(-1)
        self.trigger = trigger
        self.led.value = 0
        self.switch.when_pressed = self.__handle_press

    def __prime(self):
        print("Priming")
        # Stop any previous timers, to avoid leaking one
        self.timer.deinit()
        self.timer = Timer(period = TIMEOUT, mode = Timer.ONE_SHOT, callback = self.__arm)

    def __handle_press(self):
        if self.state == OFF:
            self.state = PRIMING
            time.sleep_ms(1000 - (time.ticks_ms() % 1000))
            self.led.blink(0.5)
            self.__prime()
        elif self.state == PRIMING:
            self.timer.deinit()
            self.state = OFF
            self.led.off()
        elif self.state == ARMED:
            self.timer.deinit()
            self.state = OFF
            self.led.off()
    
    def __arm(self, t):
        print("Arming")
        self.state = ARMED
        self.timer.deinit()
        self.led.on()

    def found(self):
        print("Detected")
        if self.state == ARMED:
            self.trigger()
            self.state = OFF
            self.led.off()
        if self.state == PRIMING:
            print("Re-priming")
            self.__prime()

    def __str__(self):
        return f"IlluminatedSwitch(led={self.led}, switch={self.switch})"