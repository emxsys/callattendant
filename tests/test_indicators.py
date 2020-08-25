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
import sys
import time
from pprint import pprint

import pytest

from callattendant.hardware.indicators import RingIndicator, ApprovedIndicator, BlockedIndicator, MessageIndicator


# Skip the test when running under continous integraion
pytestmark = pytest.mark.skipif(os.getenv("CI")=="true", reason="Hardware not installed")


def test_multiple():

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

    # Release GPIO pins
    ring.close()
    approved.close()
    blocked.close()
    message.close()
