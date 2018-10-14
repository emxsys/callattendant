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

from gpiozero import LED


def turn_all_off():
    pass


class RingIndicator(object):
    def turn_on(self):
        self.led.blink(0.5, 0.2, 10)

    def turn_off(self):
        pass

    def __init__(self):
        self.led = LED(2)


class ApprovedIndicator(object):
    def turn_on(self):
        self.led.blink(0.5, 0.2, 10)

    def turn_off(self):
        pass

    def __init__(self):
        self.led = LED(3)


class BlockedIndicator(object):
    def turn_on(self):
        self.led.blink(0.5, 0.2, 10)

    def turn_off(self):
        pass

    def __init__(self):
        self.led = LED(4)
