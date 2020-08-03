#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  calllogger.py
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
# https://iotbytes.wordpress.com/incoming-call-details-logger-with-raspberry-pi/
# https://github.com/pradeesi/Incoming_Call_Detail_Logger
# ==============================================================================

from datetime import datetime
from pprint import pprint


class CallLogger(object):

    def log_caller(self, callerid):
        query = """INSERT INTO CallLog(
            Name,
            Number,
            Date,
            Time,
            SystemDateTime)
            VALUES(?,?,?,?,?)"""
        arguments = [callerid['NAME'],
                     callerid['NMBR'],
                     datetime.strptime(callerid['DATE'], '%m%d'). strftime('%d-%b'),
                     datetime.strptime(callerid['TIME'], '%H%M'). strftime('%I:%M %p'),
                     (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])]

        self.db.execute(query, arguments)
        self.db.commit()

        if self.config["DEBUG"]:
            print "New log entry added"
            pprint(arguments)

    def __init__(self, db, config):
        self.db = db
        self.config = config

        if self.config["DEBUG"]:
            print "Initializing CallLogger"

        # Create the Call_History table if it does not exist
        sql = """CREATE TABLE IF NOT EXISTS CallLog (
            CallLogID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Number TEXT,
            Date TEXT,
            Time TEXT,
            SystemDateTime TEXT);"""

        curs = self.db.cursor()
        curs.executescript(sql)
        curs.close()

        if self.config["DEBUG"]:
            print "CallLogger initialized"


def test(db, config):
    ''' Unit Tests '''
    import utils

    # Create the logger to be tested
    logger = CallLogger(db, config)

    # Add a record
    callerid = {"NAME": "Bruce", "NMBR": "1234567890", "DATE": "1012", "TIME": "0600"}
    print("Adding CID:")
    pprint(callerid)
    logger.log_caller(callerid)

    # List the records
    query = "SELECT * FROM CallLog"
    results = utils.query_db(db, query)
    print(query + " results:")
    pprint(results)

    return 0


if __name__ == '__main__':
    '''
    Run the unit tests
    '''
    # Create the test db in RAM
    import sqlite3
    db = sqlite3.connect(":memory:")

    # Add the parent directory to the path so callattendant can be found
    import os
    import sys
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

    # Create and tweak a default config suitable for unit testing
    from callattendant import make_config, print_config
    config = make_config()
    config['DEBUG'] = True
    print_config(config)

    # Run the tests
    sys.exit(test(db, config))

    print("Tests complete")
