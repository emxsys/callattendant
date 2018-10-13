#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  whitelist.py
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

class Whitelist(object):

    def __init__(self, db):
        """Ensures database access to the Whitelist table"""

        self.db = db

        sql = '''CREATE TABLE IF NOT EXISTS Whitelist (
            PhoneNo TEXT PRIMARY KEY,
            Name TEXT,
            SystemDateTime TEXT)'''
        curs = self.db.cursor()
        curs.executescript(sql)
        curs.close()

        print "Whitelist initialized"

    def add_caller(self, call_record):
        query = '''INSERT INTO Whitelist(
            PhoneNo,
            Name,
            SystemDateTime) VALUES(?,?,?)'''
        arguments = [
            call_record['NMBR'],
            call_record['NAME'],
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
            ]
        self.db.execute(query, arguments)
        self.db.commit()

        print "New whitelist record added"

    def check_number(self, number):
        query = "SELECT COUNT(*) FROM Whitelist WHERE PhoneNo=:number"
        args = {"number": number}
        result = utils.query_db(self.db, query, args, True)
        return result[0] > 0

    def get_number(self, number):
        query = "SELECT * FROM Whitelist WHERE PhoneNo = ?"
        args = (number,)
        results = utils.query_db(self.db, query, args, False)
        return results


def test(args):
    import sqlite3

    # Create the test db in RAM
    db = sqlite3.connect(":memory:")
    #db.text_factory = str

    # Create the whitelist to be tested
    whitelist = Whitelist(db)

    # Add a record
    call_record = {"NAME":"Bruce", "NMBR":"1234567890", "DATE":"1012", "TIME":"0600"}
    whitelist.add_caller(call_record)

    # List the records
    query = 'SELECT * from Whitelist'
    results = utils.query_db(db, query)
    print "Query results:"
    print results

    number = "1234567890"
    print "Check number: " + number
    print whitelist.check_number(number)
    print "Check wrong number:"
    print whitelist.check_number("1111111111")
    print "Get number:"
    print whitelist.get_number(number)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(test(sys.argv))
    print("Done")

