#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  messenger.py
#
#  Copyright 2018  <bruce@emxsys.com>
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

import os
import threading
from pprint import pprint
from datetime import datetime


global unplayed_count
unplayed_count = 0

class Message:

    def __init__(self, db, config):
        """
        Initialize the database tables for voice messages.
            :param db:
                The database used within a single thread.
            :config:
                The applicaiton-wide config object.
        """
        if config["DEBUG"]:
            print("Initializing Message")

        self.db = db
        self.config = config

        # Get the message event object set by the VoiceMail class
        self.message_event = self.config["MESSAGE_EVENT"]

        # Create the message table if it does not exist
        if self.db:
            sql = """
                CREATE TABLE IF NOT EXISTS Message (
                    MessageID INTEGER PRIMARY KEY AUTOINCREMENT,
                    CallLogID INTEGER,
                    Played BOOLEAN DEFAULT 0 NOT NULL CHECK (Played IN (0,1)),
                    Filename TEXT,
                    DateTime TEXT,
                    FOREIGN KEY(CallLogID) REFERENCES CallLog(CallLogID));"""
            curs = self.db.cursor()
            curs.executescript(sql)
            curs.close()

        self._update_unplayed_count()

        if config["DEBUG"]:
            print("Message initialized")

    def add(self, call_no, filepath):
        """
        Adds a message to the table.
            :param call_no:
                The unique ID of the call this message is associated with.
            :param filepath:
                The name and path for the message .wav file that was recorded.
            :return:
                The unique ID of the new row
        """

        sql = """
            INSERT INTO Message(
                CallLogID,
                Filename,
                DateTime)
            VALUES(?,?,?)
        """
        arguments = [
            call_no,
            filepath,
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:19])
        ]
        self.db.execute(sql, arguments)
        self.db.commit()

        # Return the MessageID
        query = "SELECT last_insert_rowid()"
        curs = self.db.cursor()
        curs.execute(query)
        msg_no = curs.fetchone()[0]
        curs.close()

        self._update_unplayed_count()

        return msg_no

    def delete(self, msg_no):
        """
        Removes the message record and associated wav file.
        """
        # Get the filename to delete
        sql = "SELECT Filename FROM Message WHERE MessageID=:msg_no"
        arguments = {'msg_no': msg_no}
        curs = self.db.execute(sql, arguments)
        results = curs.fetchone()
        curs.close()

        # Now do the deletes
        success = True
        if len(results) > 0:

            # Delete the .wav file
            # Build a filename using the config instead of the filepath
            # stored in the db, in case the files have been moved
            basename = os.path.basename(results[0])
            filepath = os.path.join(self.config["VOICE_MAIL_MESSAGE_FOLDER"], basename)
            print("Deleting message: {}".format(filepath))
            try:
                os.remove(filepath)
            except Exception as error:
                pprint(error)
                print("{} cannot be removed".format(filepath))
                success = False

            # Delete the row
            if success:
                sql = "DELETE FROM Message WHERE MessageID=:msg_no"
                arguments = {'msg_no': msg_no}
                self.db.execute(sql, arguments)
                self.db.commit()

                if self.config["DEBUG"]:
                    print("Message entry removed")
                    pprint(arguments)

            self._update_unplayed_count()

        return success

    def update_played(self, msg_no, played=1):
        """
        Updates the played status of the given message
        """
        try:
            sql = "UPDATE Message SET Played=:played WHERE MessageID=:msg_no"
            arguments = {'msg_no': msg_no, 'played': played}
            self.db.execute(sql, arguments)
            self.db.commit()
        except Exception as e:
            print("** Error updating message played status:")
            pprint(e)
            return False

        self._update_unplayed_count()
        return True

    def get_unplayed_count(self):
        # Return the global
        global unplayed_count
        return unplayed_count

    def _update_unplayed_count(self):
        # Get the number of unread messages
        sql = "SELECT COUNT(*) FROM Message WHERE Played = 0"
        curs = self.db.execute(sql)
        global unplayed_count
        unplayed_count = curs.fetchone()[0]

        if self.config["DEBUG"]:
            print("Unplayed message count is {}".format(unplayed_count))

        self.message_event.set()
        self.message_event.clear()
