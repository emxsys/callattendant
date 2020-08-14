#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  indicators.py
#
#  Copyright 2018 Bruce Schubert <bruce@emxsys.com>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

# See: https://gpiozero.readthedocs.io/en/stable/
# See: https://gpiozero.readthedocs.io/en/stable/api_output.html#led
from gpiozero import LED, PWMLED
from pprint import pprint
import time

GPIO_RING = 2       # pin 3
GPIO_APPROVED = 3   # pin 5
GPIO_BLOCKED = 4    # pin 7
GPIO_MESSAGE = 5    # pin 27


class LEDIndicator(object):
    def turn_on(self):
        self.led.on()

    def blink(self, max_times=10):
        # blink in a separate thread
        self.led.blink(0.5, 0.2, max_times)

    def turn_off(self):
        self.led.off()

    def __init__(self, gpio_pin):
        self.led = LED(gpio_pin)


class PWMLEDIndicator(LEDIndicator):
    def turn_on(self):
        self.led.on()

    def blink(self, max_times=10):
        # blink in a separate thread
        self.led.pulse(n=max_times)

    def turn_off(self):
        self.led.off()

    def __init__(self, gpio_pin):
        self.led = PWMLED(gpio_pin)


class RingIndicator(LEDIndicator):

    def __init__(self, gpio_pin=GPIO_RING):
        LEDIndicator.__init__(self, gpio_pin)


class ApprovedIndicator(LEDIndicator):

    def __init__(self, gpio_pin=GPIO_APPROVED):
        LEDIndicator.__init__(self, gpio_pin)


class BlockedIndicator(LEDIndicator):

    def __init__(self, gpio_pin=GPIO_BLOCKED):
        LEDIndicator.__init__(self, gpio_pin)


class MessageIndicator(PWMLEDIndicator):

    def blink(self, max_times=None):
        # blink in a separate thread
        self.led.pulse(n=max_times)

    def __init__(self, gpio_pin=GPIO_MESSAGE):
        PWMLEDIndicator.__init__(self, gpio_pin)


def test():
    """ Unit Tests """
    import os

    print("*** Running Indicator Unit Tests ***")

    try:
        print("[Constructing Indicators]")
        ring = RingIndicator()
        approved = ApprovedIndicator()
        blocked = BlockedIndicator()
        message = MessageIndicator()

        print("[Visual Tests]")

        print("Turning on all LEDs for 5 seconds...")
        ring.turn_on()
        approved.turn_on()
        blocked.turn_on()
        message.turn_on()
        time.sleep(5)

        print("Blinking on all LEDs for 5 seconds...")
        ring.blink()
        time.sleep(.1)
        approved.blink()
        time.sleep(.1)
        blocked.blink()
        time.sleep(.1)
        message.blink()
        time.sleep(5)

        print("Turning off all LEDs...")
        ring.turn_off()
        approved.turn_off()
        blocked.turn_off()
        message.turn_off()
        time.sleep(5)

    except Exception as e:
        print("*** Unit test FAILED ***")
        pprint(e)
        return 1

    print("*** Unit tests PASSED ***")
    return 0


if __name__ == '__main__':
    """ Run the Unit Tests """
    import sys
    # Run the tests
    sys.exit(test())
