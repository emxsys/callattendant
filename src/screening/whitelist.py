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
from pprint import pprint
from datetime import datetime


class Whitelist(object):

    def __init__(self, db, config):
        """Ensures database access to the Whitelist table"""
        self.db = db
        self.config = config

        if self.config["DEBUG"]:
            print("Initializing Whitelist")

        sql = '''CREATE TABLE IF NOT EXISTS Whitelist (
            PhoneNo TEXT PRIMARY KEY,
            Name TEXT,
            Reason TEXT,
            SystemDateTime TEXT)'''
        curs = self.db.cursor()
        curs.executescript(sql)
        curs.close()

        if self.config["TESTING"]:
            # Add a record to the test db;
            # The number should match a value in the Modem's TEST_DATA
            caller = {
                "NAME": "Bruce",
                "NMBR": "8055554567",
                "DATE": "0801",
                "TIME": "1801",
                "REASON": "Whitelist test",
            }
            self.add_caller(caller)

        if self.config["DEBUG"]:
            print("Whitelist initialized")

    def add_caller(self, call_record, reason=""):
        query = '''INSERT INTO Whitelist(
            PhoneNo,
            Name,
            Reason,
            SystemDateTime) VALUES(?,?,?,?)'''
        arguments = [
            call_record['NMBR'],
            call_record['NAME'],
            reason,
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        ]
        self.db.execute(query, arguments)
        self.db.commit()

        if self.config["DEBUG"]:
            print("New whitelist entry added")
            pprint(arguments)

    def remove_number(self, phone_no):
        '''Removes records for the given number (without dashes or formatting)'''
        query = 'DELETE FROM Whitelist WHERE PhoneNo=:phone_no'
        arguments = {'phone_no': phone_no}
        self.db.execute(query, arguments)
        self.db.commit()

        if self.config["DEBUG"]:
            print("whitelist entry removed")
            pprint(arguments)

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


def test(db, config):
    """ Unit Tests """

    # Create the whitelist to be tested
    whitelist = Whitelist(db, config)

    # Add a record
    call_record = {"NAME": "Bruce", "NMBR": "1234567890", "REASON": "some reason", "DATE": "1012", "TIME": "0600"}
    whitelist.add_caller(call_record)

    # List the records
    query = 'SELECT * from Whitelist'
    results = utils.query_db(db, query)
    print(query + " results:")
    pprint(results)

    number = "1234567890"
    print("Assert is whitelisted: " + number)
    assert whitelist.check_number(number)

    number = "1111111111"
    print("Assert not whitelisted: " + number)
    assert not whitelist.check_number(number)

    number = "1234567890"
    print("Get number: " + number)
    pprint(whitelist.get_number(number))

    return 0


if __name__ == '__main__':
    """  Run the unit tests """

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
