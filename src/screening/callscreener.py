#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  callscreener.py
#
#  Copyright 2018  <pi@rhombus1>
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

# Add the parent directory to the path so config.py can be found during tests
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import config
from screening.blacklist import Blacklist
from screening.whitelist import Whitelist
from screening.nomorobo import NomoroboService
import re
import sys


class CallScreener(object):
    '''The CallScreener provides provides blacklist and whitelist checks'''

    def is_whitelisted(self, callerid):
        '''Returns true if the number is on a whitelist'''
        return self._whitelist.check_number(callerid['NMBR'])

    def is_blacklisted(self, callerid):
        '''Returns true if the number is on a blacklist'''
        number = callerid['NMBR']
        name = callerid["NAME"]
        try:
            if self._blacklist.check_number(number):
                print("Caller is blacklisted")
                return True
            else:
                print("Checking nomorobo...")
                result = self._nomorobo.lookup_number(number)
                if result["spam"]:
                    print("Caller is robocaller")
                    self.blacklist_caller(callerid, "{} with score {}".format(result["reason"], result["score"]))
                    return True
                print("Checking CID patterns...")
                for key in config.IGNORE_NAME_PATTERNS.keys():
                    match = re.search(key, name)
                    if match:
                        print("CID ignore name pattern detected")
                        reason = config.IGNORE_NAME_PATTERNS[key]
                        self.blacklist_caller(callerid, reason)
                        return True
                for key in config.IGNORE_NUMBER_PATTERNS.keys():
                    match = re.search(key, number)
                    if match:
                        print("CID ignore number pattern detected")
                        reason = config.IGNORE_NUMBER_PATTERNS[key]
                        self.blacklist_caller(callerid, reason)
                        return True
                print("Caller has been screened")
                return False
        finally:
            sys.stdout.flush()

    def whitelist_caller(self, callerid, reason):
        self._whitelist.add_caller(callerid, reason)

    def blacklist_caller(self, callerid, reason):
        self._blacklist.add_caller(callerid, reason)

    def __init__(self, db):
        self._db = db
        self._blacklist = Blacklist(db)
        self._whitelist = Whitelist(db)
        self._nomorobo = NomoroboService()


def test(args):
    import sqlite3

    # Create the test db in RAM
    db = sqlite3.connect(":memory:")
    # db.text_factory = str

    # Create the screener to be tested
    screener = CallScreener(db)

    # Add a record to the blacklist
    caller1 = {"NAME": "Bruce", "NMBR": "1234567890", "DATE": "1012", "TIME": "0600"}
    screener._blacklist.add_caller(caller1)
    # Add a record to the whitelist
    caller2 = {"NAME": "Frank", "NMBR": "1111111111", "DATE": "1012", "TIME": "0600", "REASON": "Test"}
    screener._whitelist.add_caller(caller2)
    # Create a V123456789012345 Telemarketer caller
    caller3 = {"NAME": "V123456789012345", "NMBR": "80512345678", "DATE": "1012", "TIME": "0600"}
    # Create a robocaller
    caller4 = {"NAME": "Robocaller", "NMBR": "3105241189", "DATE": "1012", "TIME": "0600"}

    # Perform tests
    print("Assert is blacklisted: " + caller1['NMBR'])
    assert screener.is_blacklisted(caller1)

    print("Assert not is whitelisted: " + caller1['NMBR'])
    assert not screener.is_whitelisted(caller1)

    print("Assert not is blacklisted: " + caller2['NMBR'])
    assert not screener.is_blacklisted(caller2)

    print("Assert is whitelisted: " + caller2['NMBR'])
    assert screener.is_whitelisted(caller2)

    print("Assert a bad name pattern: " + caller3['NMBR'])
    assert screener.is_blacklisted(caller3)

    print("Assert is blacklisted by nomorobo: " + caller4['NMBR'])
    assert screener.is_blacklisted(caller4)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(test(sys.argv))
    print("Done")
