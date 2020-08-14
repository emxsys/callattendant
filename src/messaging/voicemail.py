#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  messenger.py
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

import os
from pprint import pprint
from datetime import datetime

class VoiceMail:

    def __init__(self, db, config, modem, message_indicator):
        """
        Initialize the database tables for voice messages.
        """
        self.db = db
        self.config = config
        self.modem = modem
        self.message_indicator = message_indicator

        if self.config["DEBUG"]:
            print("Initializing VoiceMail")

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

        if self.get_unplayed_count() > 0:
            self.message_indicator.blink()

        if self.config["DEBUG"]:
            print("VoiceMail initialized")

    def voice_messaging_menu(self, call_no, caller):
        """
        Play a voice message menu and respond to the choices.
        """
        # Build some common paths
        root_path = self.config['ROOT_PATH']
        voice_mail = self.config.get_namespace("VOICE_MAIL_")
        voice_mail_menu_file = os.path.join(root_path, voice_mail['menu_file'])
        invalid_response_file = os.path.join(root_path, voice_mail['invalid_response_file'])
        goodbye_file = os.path.join(root_path, voice_mail['goodbye_file'])

        tries = 0
        while tries < 3:
            self.modem.play_audio(voice_mail_menu_file)
            success, digit = self.modem.wait_for_keypress(5)
            if not success:
                break
            if digit == '1':
                self.record_message(call_no, caller)
                break
            elif digit == '0':
                # End this call
                break
            else:
                # Try again--up to a limit
                self.modem.play_audio(invalid_response_file)
                tries += 1

        self.modem.play_audio(goodbye_file)

    def record_message(self, call_no, caller):
        """
        Records a message.
        """
        # Build the filename used for a potential message
        path = os.path.join(
            self.config['ROOT_PATH'],
            self.config["VOICE_MAIL_MESSAGE_FOLDER"])
        filepath = os.path.join(path, "{}_{}_{}_{}.wav".format(
            call_no,
            caller["NMBR"],
            caller["NAME"].replace('_', '-'),
            datetime.now().strftime("%m%d%y_%H%M")))

        self.modem.play_audio(self.config["VOICE_MAIL_LEAVE_MESSAGE_FILE"])

        # Recording in progress
        self.message_indicator.turn_on()
        if self.modem.record_audio(filepath):

            # Save to Message table
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
            query = "select last_insert_rowid()"
            curs = self.db.cursor()
            curs.execute(query)
            msg_no = curs.fetchone()[0]
            curs.close()

            # Indicate a new message is waiting
            self.message_indicator.blink()

            return msg_no
        else:
            if self.get_unplayed_count() > 0:
                self.message_indicator.blink()
            else:
                self.message_indicator.turn_off()
            return None

    def delete_message(self, msg_no):
        """
        Removes the message record and associated wav file.
        """
        sql = "SELECT Filename FROM Message WHERE MessageID=:msg_no"
        arguments = {'msg_no': msg_no}
        curs = self.db.execute(sql, arguments)
        results = curs.fetchone()
        curs.close()

        success = True
        if len(results) > 0:
            # Remove the wav file
            filename = results[0]
            print("Deleting message: {}".format(filename))
            try:
                os.remove(filename)
            except OSError as error:
                pprint(error)
                print("{} cannot be removed".format(filename))
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

        if self.get_unplayed_count() > 0:
            self.message_indicator.blink()

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
        return True

    def get_unplayed_count(self):
        # Get the number of unread messages
        sql = "SELECT COUNT(*) FROM Message WHERE Played = 0"
        curs = self.db.execute(sql)
        unplayed_count = curs.fetchone()[0]
        if self.config["DEBUG"]:
            print("Unplayed message count is {}".format(unplayed_count))
        return unplayed_count


def test(db, config):
    """
     Unit Tests
    """

    print("*** Running VoiceMail Unit Tests ***")

    # Create dependencies
    from hardware.modem import Modem
    from screening.calllogger import CallLogger
    modem = Modem(config, lambda arg: arg, lambda arg: arg)
    modem.open_serial_port()
    logger = CallLogger(db, config)
    # Create the object to be tested
    voicemail = VoiceMail(db, config, modem)

    # Test data
    caller = {"NAME": "Bruce", "NMBR": "1234567890", "DATE": "1012", "TIME": "0600"}

    try:
        call_no = logger.log_caller(caller)

        msg_no = voicemail.record_message(call_no, caller)

        count = voicemail.get_unplayed_count()
        assert count == 1, "Unplayed count should be 1"

        # List the records
        query = 'select * from Message'
        curs = db.execute(query)
        print(query + " results:")
        pprint(curs.fetchall())

        voicemail.delete_message(msg_no)

    except AssertionError as e:
        print("*** Unit Test FAILED ***")
        pprint(e)
        return 1

    print("*** Unit Tests PASSED ***")
    return 0


if __name__ == '__main__':

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
