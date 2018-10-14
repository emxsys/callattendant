#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  blacklist.py
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

# ==============================================================================
# This code was inspired by and contains code snippets from Pradeep Singh:
# https://github.com/pradeesi/Incoming_Call_Detail_Logger
# https://iotbytes.wordpress.com/incoming-call-details-logger-with-raspberry-pi/
# ==============================================================================

import utils
from datetime import datetime

class Blacklist(object):

    def add_caller(self, callerid, reason=""):
        query = '''INSERT INTO Blacklist(
            PhoneNo,
            Name,
            Reason,
            SystemDateTime) VALUES(?,?,?,?)'''
        arguments = [
            callerid['NMBR'],
            callerid['NAME'],
            reason,
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
            ]
        self.db.execute(query, arguments)
        self.db.commit()

        print "New blacklist entry added"

    def check_number(self, number):
        query = "SELECT COUNT(*) FROM Blacklist WHERE PhoneNo=:number"
        args = {"number": number}
        result = utils.query_db(self.db, query, args, True)
        return result[0] > 0

    def get_number(self, number):
        query = "SELECT * FROM Blacklist WHERE PhoneNo = ?"
        args = (number,)
        results = utils.query_db(self.db, query, args, False)
        return results

    def __init__(self, db):
        """Ensures database access to the Blacklist table"""
        self.db = db
        sql = '''
            CREATE TABLE IF NOT EXISTS Blacklist (
                PhoneNo TEXT PRIMARY KEY,
                Name TEXT,
                Reason TEXT,
                SystemDateTime TEXT);

            CREATE TABLE IF NOT EXISTS Cache (
                PhoneNo TEXT PRIMARY KEY,
                SpamScore INTEGER,
                Reason TEXT,
                SystemDateTime TEXT);

            '''
        curs = self.db.cursor()
        curs.executescript(sql)
        curs.close()

        print "Blacklist initialized"


def test(args):
    import sqlite3

    # Create the test db in RAM
    db = sqlite3.connect(":memory:")
    #db.text_factory = str

    # Create the blacklist to be tested
    blacklist = Blacklist(db)

    # Add a record
    callerid = {"NAME":"Bruce", "NMBR":"1234567890", "DATE":"1012", "TIME":"0600"}
    blacklist.add_caller(callerid)

    # List the records
    query = 'select * from Blacklist'
    results = utils.query_db(db, query)
    print "Query results:"
    print results

    number = "1234567890"
    print "Check number: " + number
    print blacklist.check_number(number)
    print "Check wrong number:"
    print blacklist.check_number("1111111111")
    print "Get number:"
    print blacklist.get_number(number)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(test(sys.argv))
    print("Done")

