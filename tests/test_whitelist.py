#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_whitelist.py
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

import sqlite3
from pprint import pprint

import pytest

from callattendant.screening.whitelist import Whitelist


@pytest.fixture(scope='module')
def whitelist():

    # Create the test db in RAM
    db = sqlite3.connect(":memory:")

    # Mock the application config, which is a dict-based object
    config = {}
    config['DEBUG'] = True
    config['TESTING'] = True

    # Create the whitelist to be tested
    whitelist = Whitelist(db, config)

    return whitelist


def test_add_caller(whitelist):
    # Add a record
    callerid = {"NAME": "Bruce", "NMBR": "1234567890", "DATE": "1012", "TIME": "0600"}
    assert whitelist.add_caller(callerid, "Test")


def test_check_number(whitelist):
    number = "1234567890"

    is_whitelisted, reason = whitelist.check_number(number)

    assert is_whitelisted
    assert reason == "Test"

    number = "1111111111"

    is_whitelisted, reason = whitelist.check_number(number)

    assert not is_whitelisted


def test_get_number(whitelist):
    number = "1234567890"

    caller = whitelist.get_number(number)
    pprint(caller)

    assert caller[0][0] == number


def test_multiple(whitelist):
    new_caller = {"NAME": "New Caller", "NMBR": "12312351234", "DATE": "1012", "TIME": "0600"}
    number = new_caller["NMBR"]
    name = new_caller["NAME"]
    reason = "Test"
    pprint(new_caller)

    assert whitelist.add_caller(new_caller, reason)

    caller = whitelist.get_number(number)
    pprint(caller)

    assert caller[0][0] == number
    assert caller[0][1] == name
    assert caller[0][2] == reason

    name = "Joe"
    reason = "Confirm"

    assert whitelist.update_number(number, name, reason)

    caller = whitelist.get_number(number)
    pprint(caller)

    assert caller[0][0] == number
    assert caller[0][1] == name
    assert caller[0][2] == reason

    assert whitelist.remove_number(number)

    is_whitelisted, reason = whitelist.check_number(number)
    assert not is_whitelisted

    caller = whitelist.get_number(number)
    pprint(caller)
