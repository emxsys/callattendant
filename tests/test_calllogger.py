#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_calllogger.py
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

from callattendant.screening.calllogger import CallLogger


@pytest.fixture(scope='module')
def calllogger():

    # Create the test db in RAM
    db = sqlite3.connect(":memory:")

    # Mock the application config, which is a dict-based object
    config = {}
    config['DEBUG'] = True
    config['TESTING'] = True

    # Create the CallLogger to be tested
    calllogger = CallLogger(db, config)

    return calllogger


def test_add_caller(calllogger):

    # Caller to be added
    callerid = {
        "NAME": "Bruce",
        "NMBR": "1234567890",
        "DATE": "1012",
        "TIME": "0600",
    }

    assert calllogger.log_caller(callerid, "Permitted", "Test1") == 1

    assert calllogger.log_caller(callerid) == 2
