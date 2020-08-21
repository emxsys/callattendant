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

from datetime import datetime
from pprint import pprint
from screening.query_db import query_db


class Blacklist(object):

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
            SET Name=:name, Reason=:reason, SystemDateTime=:time
            WHERE PhoneNo=:phone_no"""
        arguments = {
            'phone_no': phone_no,
            "name": name,
            "reason": reason,
            "time": (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:19])
            }
        try:
            self.db.execute(sql, arguments)
            self.db.commit()
        except Exception as e:
            print("** Failed to update caller in blacklist:")
            pprint(e)
            return False

        if self.config["DEBUG"]:
            print("Blacklist entry updated")
            pprint(arguments)
        return True

    def remove_number(self, phone_no):
        '''Removes records for the given number (without dashes or formatting)'''
        query = 'DELETE FROM Blacklist WHERE PhoneNo=:phone_no'
        arguments = {'phone_no': phone_no}
        try:
            self.db.execute(query, arguments)
            self.db.commit()
        except Exception as e:
            print("** Failed to delete caller from blacklist:")
            pprint(e)
            return False
        if self.config["DEBUG"]:
            print("blacklist entry removed")
            pprint(arguments)
        return True

    def check_number(self, number):
        """
        Checks if the number is in the blacklist
            :parma number: the number to look for
            :returns: True if found; and a string containing the reason
        """
        query = "SELECT Reason FROM Blacklist WHERE PhoneNo=:number"
        args = {"number": number}
        results = query_db(self.db, query, args, False)
        if len(results) > 0:
            return True, results[0][0]
        else:
            return False, ""

    def get_number(self, number):
        query = "SELECT * FROM Blacklist WHERE PhoneNo = ?"
        args = (number,)
        results = query_db(self.db, query, args, False)
        return results
