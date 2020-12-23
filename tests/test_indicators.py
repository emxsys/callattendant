#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_indicators.py
#
#  Copyright 2020 Bruce Schubert  <bruce@emxsys.com>
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

import os
import time

import pytest

from config import Config
from callattendant.hardware.indicators import RingIndicator, ApprovedIndicator, BlockedIndicator, \
    MessageIndicator, MessageCountIndicator

# Skip the test when running under continous integraion
pytestmark = pytest.mark.skipif(os.getenv("CI") == "true", reason="Hardware not installed")


def test_multiple():

    config = Config()

    ringer = RingIndicator(config["GPIO_LED_RING_PIN"], brightness=100)
    approved = ApprovedIndicator(config["GPIO_LED_APPROVED_PIN"], brightness=25)
    blocked = BlockedIndicator(config["GPIO_LED_BLOCKED_PIN"], brightness=25)
    message = MessageIndicator(config["GPIO_LED_MESSAGE_PIN"], brightness=100)

    pins_tuple = config["GPIO_LED_MESSAGE_COUNT_PINS"]
    kwargs_dict = config["GPIO_LED_MESSAGE_COUNT_KWARGS"]
    message_count = MessageCountIndicator(*pins_tuple, **kwargs_dict)

    # ~ ringer = RingIndicator()
    # ~ approved = ApprovedIndicator()
    # ~ blocked = BlockedIndicator()
    # ~ message = MessageIndicator()
    # ~ message_count = MessageCountIndicator()

    for i in range(0, 16):
        message_count.display_hex(i)
        time.sleep(.5)

    print("[Visual Tests]")

    print("Turning on all LEDs for 5 seconds...")
    ringer.turn_on()
    approved.turn_on()
    blocked.turn_on()
    message.turn_on()
    time.sleep(5)

    print("Blinking on all LEDs for 5 seconds...")
    ringer.blink()
    time.sleep(.1)
    approved.blink()
    time.sleep(.1)
    blocked.blink()
    time.sleep(.1)
    message.blink()
    time.sleep(5)

    print("Turning off all LEDs...")
    ringer.turn_off()
    approved.turn_off()
    blocked.turn_off()
    message.turn_off()
    time.sleep(2)

    print("Test normal status")
    ringer.ring()
    message.pulse(),
    message_count.display(2)
    time.sleep(10)

    # Release GPIO pins
    ringer.close()
    approved.close()
    blocked.close()
    message.close()
