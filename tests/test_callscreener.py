#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_callscreener.py
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
import pytest

from callattendant.config import Config
from callattendant.screening.callscreener import CallScreener


# Create a blocked caller
caller1 = {"NAME": "CALLER1", "NMBR": "1234567890", "DATE": "1012", "TIME": "0600"}
# Create a permitted caller
caller2 = {"NAME": "CALLER2", "NMBR": "1111111111", "DATE": "1012", "TIME": "0600"}
# Create a V123456789012345 Telemarketer caller (blocked name pattern match)
caller3 = {"NAME": "V123456789012345", "NMBR": "80512345678", "DATE": "1012", "TIME": "0600"}
# Create a robocaller
caller4 = {"NAME": "CALLER4", "NMBR": "3105241189", "DATE": "1012", "TIME": "0600"}
# Create a Private Number (blocked number pattern match)
caller5 = {"NAME": "CALLER5", "NMBR": "P", "DATE": "1012", "TIME": "0600"}
# Create a John Doe name (permitted name pattern match)
caller6 = {"NAME": "JOHN DOE", "NMBR": "0987654321", "DATE": "1012", "TIME": "0600"}
# Create a unique number (permitted number pattern match)
caller7 = {"NAME": "CALLER7", "NMBR": "09876543210", "DATE": "1012", "TIME": "0600"}


@pytest.fixture(scope='module')
def screener():

    # Create the test db in RAM
    db = sqlite3.connect(":memory:")

    # Create a config object with default settings
    config = Config()
    config['DEBUG'] = True
    config['TESTING'] = True
    config['BLOCK_NAME_PATTERNS'] = {
        "V[0-9]{15}": "Telemarketer Caller ID",
    }
    config['BLOCK_NUMBER_PATTERNS'] = {
        "P": "Private number",
    }
    config['PERMIT_NAME_PATTERNS'] = {
        ".*DOE": "Anyone",
    }
    config['PERMIT_NUMBER_PATTERNS'] = {
        "987654": "Anyone",
    }
    # Create the blacklist to be tested
    screener = CallScreener(db, config)
    # Add a record to the blacklist
    screener._blacklist.add_caller(caller1)
    # Add a record to the whitelist
    screener._whitelist.add_caller(caller2)

    return screener


def test_is_blacklisted(screener):
    is_blacklisted, reason = screener.is_blacklisted(caller1)
    assert is_blacklisted


def test_not_is_whitelisted(screener):
    is_whitelisted, reason = screener.is_whitelisted(caller1)
    assert not is_whitelisted, "caller1 should not be permitted"


def test_not_is_blacklisted(screener):
    is_blacklisted, reason = screener.is_blacklisted(caller2)
    assert not is_blacklisted, "caller2 should not be blocked"


def test_is_whitelisted(screener):
    is_whitelisted, reason = screener.is_whitelisted(caller2)
    assert is_whitelisted, "caller2 should be permitted"


def test_blocked_name_pattern(screener):
    is_blacklisted, reason = screener.is_blacklisted(caller3)
    assert is_blacklisted, "caller3 should be blocked by name pattern"


def test_is_blacklisted_by_nomorobo(screener):
    is_blacklisted, reason = screener.is_blacklisted(caller4)
    assert is_blacklisted, "caller4 should be blocked by nomorobo"


def test_blocked_number_pattern(screener):
    is_blacklisted, reason = screener.is_blacklisted(caller5)
    assert is_blacklisted, "caller1 should be blocked by number pattern"


def test_permitted_name_pattern(screener):
    is_whitelisted, reason = screener.is_whitelisted(caller6)
    assert is_whitelisted, "caller6 should be permiteed by name pattern"


def test_permitted_number_pattern(screener):
    is_whitelisted, reason = screener.is_whitelisted(caller7)
    assert is_whitelisted, "caller7 should be permiteed by number pattern"
