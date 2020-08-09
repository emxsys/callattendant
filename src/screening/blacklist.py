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
from pprint import pprint


class Blacklist(object):

    def add_caller(self, callerid, reason=""):
        """
        Add a caller to the blocked list.
            :param caller: a dict with caller ID information
            :param reason: an optional string indicating the
                reason this caller was added
            :return: True if successful
        """
        query = '''INSERT INTO Blacklist(
            PhoneNo,
            Name,
            Reason,
            SystemDateTime) VALUES(?,?,?,?)'''
        arguments = [
            callerid['NMBR'],
            callerid['NAME'],
            reason,
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:19])
        ]
        try:
            self.db.execute(query, arguments)
            self.db.commit()
            if self.config["DEBUG"]:
                print("New blacklist entry added")
                pprint(arguments)
        except Exception as e:
            print("** Failed to add caller to blacklist:")
            pprint(e)
            return False
        return True

    def update_number(self, phone_no, name, reason):
        """
        Updates the record for the given number
        :param phone_no: phone number (key) without dashes or formatting
        :param name: new name
        :param reason: new reason
        """
        sql = """UPDATE Blacklist
            SET Name=:name, Reason=:reason
            WHERE PhoneNo=:phone_no"""
        arguments = {'phone_no': phone_no, "name": name, "reason": reason}
        self.db.execute(sql, arguments)
        self.db.commit()

        if self.config["DEBUG"]:
            print("Blacklist entry updated")
            pprint(arguments)

    def remove_number(self, phone_no):
        '''Removes records for the given number (without dashes or formatting)'''
        query = 'DELETE FROM Blacklist WHERE PhoneNo=:phone_no'
        arguments = {'phone_no': phone_no}
        self.db.execute(query, arguments)
        self.db.commit()

        if self.config["DEBUG"]:
            print("blacklist entry removed")
            pprint(arguments)

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

    def __init__(self, db, config):
        """Ensures database access to the Blacklist table"""
        self.db = db
        self.config = config

        if self.config["DEBUG"]:
            print("Initializing Blacklist")

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

        if self.config["TESTING"]:
            # Add a record to the test db;
            # The number should match a value in the Modem's TEST_DATA
            caller = {
                "NAME": "Bruce",
                "NMBR": "3605554567",
                "DATE": "0801",
                "TIME": "1802",
                "REASON": "Blacklist test",
            }
            self.add_caller(caller)

        if self.config["DEBUG"]:
            print("Blacklist initialized")


def test(db, config):
    """ Unit Tests """

    print("*** Running Blacklist Unit Tests ***")

    # Create the blacklist to be tested
    blacklist = Blacklist(db, config)

    # Add a record
    callerid = {"NAME": "Bruce", "NMBR": "1234567890", "DATE": "1012", "TIME": "0600",}
    blacklist.add_caller(callerid, "Test")

    # List the records
    query = 'select * from Blacklist'
    results = utils.query_db(db, query)
    print(query + " results:")
    pprint(results)

    try:
        number = "1234567890"
        print("Assert is blacklisted: " + number)
        assert blacklist.check_number(number), number + " should be blacklisted"

        number = "1111111111"
        print("Assert not blacklisted: " + number)
        assert not blacklist.check_number(number), number + " should not be blacklisted"

        number = "1234567890"
        print("Get number: " + number)
        caller = blacklist.get_number(number)
        pprint(caller)
        assert caller[0][0] == number, number + " should match get_number "+ caller[0][0]

        new_caller = {"NAME": "New Caller", "NMBR": "12312351234", "DATE": "1012", "TIME": "0600"}
        number = new_caller["NMBR"]
        name = new_caller["NAME"]
        reason = "Test"
        print("Assert add caller:")
        pprint(new_caller)
        blacklist.add_caller(new_caller, reason)
        caller = blacklist.get_number(number)
        pprint(caller)
        assert caller[0][0] == number, number + " != "+ caller[0][0]
        assert caller[0][1] == name, name + " !=  "+ caller[0][1]
        assert caller[0][2] == reason, reason + " != "+ caller[0][2]

        name = "Joe"
        reason = "Confirm"
        print("Assert update number: " + number)
        blacklist.update_number(number, name, reason)
        caller = blacklist.get_number(number)
        pprint(caller)
        assert caller[0][0] == number, number + " != "+ caller[0][0]
        assert caller[0][1] == name, name + " !=  "+ caller[0][1]
        assert caller[0][2] == reason, reason + " != "+ caller[0][2]

    except AssertionError as e:
        print("*** Unit Test FAILED ***")
        pprint(e)
        return 1

    print("*** Unit Tests PASSED ***")
    return 0


if __name__ == '__main__':
    """ Run the unit tests """

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
