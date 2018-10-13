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

from blacklist import Blacklist
from whitelist import Whitelist
from nomorobo import NomoroboService


class CallScreener(object):
    '''The CallScreener provides provides blacklist and whitelist checks'''

    def is_whitelisted(self, callerid):
        '''Returns true if the number is on a whitelist'''
        return self._whitelist.check_number(callerid['NMBR'])

    def is_blacklisted(self, callerid):
        '''Returns true if the number is on a blacklist'''
        number = callerid['NMBR']
        if self._blacklist.check_number(number):
            print "Caller is blacklisted"
            return True
        else:
            print "Checking nomorobo..."
            result = self._nomorobo.lookup_number(number)
            if result["spam"]:
                print "Caller is robocaller"
                self.blacklist_caller(callerid, "Nomorobo")
                return True
            print ""
            return False

    def whitelist_caller(self, callerid):
        self._whitelist.add_caller(callerid)

    def blacklist_caller(self, callerid, reason):
        self._blacklist.add_caller(callerid, reason)

    def __init__(self, db):
        self._db = db
        self._blacklist = Blacklist(db)
        self._whitelist = Whitelist(db)
        self._nomorobo = NomoroboService()
