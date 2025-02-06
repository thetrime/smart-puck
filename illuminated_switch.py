"""
A class representing an illuminated switch to control an Airtag
"""

from machine import Timer

OFF = 0
PRIMING = 1
ARMED = 2

class IlluminatedSwitch:
    def __init__(self, led, switch, trigger):
        self.led = led
        self.switch = switch
        self.state = OFF
        self.timer = Timer(-1)
        self.trigger = trigger
        self.led.value = 0
        self.switch.when_pressed(self.__handle_press)

    def __prime(self):
        # Stop any previous timers, to avoid leaking one
        self.timer.deinit()
        self.timer = Timer(period = 120_000, mode = Timer.ONE_SHOT, callback = self.__arm)

    def __handle_press(self):
        if self.state == OFF:
            self.state = PRIMING
            self.led.blink()
            self.__prime()
        elif self.state == PRIMING:
            self.timer.deinit()
            self.state = OFF
            self.led.off()
        elif self.state == ARMED:
            self.timer.deinit()
            self.state = OFF
            self.led.off()

    def __arm(self):
        self.state = ARMED
        self.timer.deinit()
        self.led.on()

    def found(self):
        if self.state == ARMED:
            self.trigger()
            self.state = OFF
            self.led.off()
        if self.state == PRIMING:
            self.__prime()

    def __str__(self):
        return f"IlluminatedSwitch(led={self.led}, switch={self.switch})"