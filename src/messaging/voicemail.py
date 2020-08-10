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
from datetime import datetime

class VoiceMail:

    def __init__(self, db, config, modem):
        self.db = db
        self.config = config
        self.modem = modem

        if self.config["DEBUG"]:
            print("Initializing VoiceMail")

        # Create the message table if it does not exist
        if self.db:
            sql = """
                CREATE TABLE IF NOT EXISTS Message (
                    MessageID INTEGER PRIMARY KEY AUTOINCREMENT,
                    CallLogID INTEGER,
                    PlayedStatus BOOLEAN default 0,
                    AudioFilename TEXT,
                    Audio BLOB default null,
                    SystemDateTime TEXT,
                    FOREIGN KEY(CallLogID) REFERENCES CallLog(CallLogID));"""

            curs = self.db.cursor()
            curs.executescript(sql)
            curs.close()
        if self.config["DEBUG"]:
            print("VoiceMail initialized")

    def voice_messaging_menu(self, call_no, caller):

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

        if self.modem.record_audio(filepath):
            # TODO: Save to Message table
            sql = """
                INSERT INTO Message(
                    CallLogID,
                    AudioFilename,
                    SystemDateTime)
                VALUES(?,?,?)
            """
            arguments = [
                call_no,
                filepath,
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:19])
            ]
            self.db.execute(sql, arguments)
            self.db.commit()


def test(args):

    from modem import Modem

    modem = Modem(None)
    messenger = Messenger(None, modem)

    return 0


if __name__ == '__main__':

    import sys
    sys.path.append('../hardware')
    sys.exit(test(sys.argv))
