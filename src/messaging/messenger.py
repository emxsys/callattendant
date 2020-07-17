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


class Messenger:

    def __init__(self, db, modem):
        self.db = db
        self.modem = modem

        # Create the voice messages table if it does not exist
        if self.db:
            sql = """CREATE TABLE IF NOT EXISTS Message (
                MessageID INTEGER PRIMARY KEY AUTOINCREMENT,
                CallLogID INTEGER,
                Audio BLOB,
                SystemDateTime TEXT);"""

            curs = self.db.cursor()
            curs.executescript(sql)
            curs.close()

        print "Messenger initialized"

    def record_message(self):
        self._modem.play_audio(sample.wav)
        self._modem.beep()
        voice_message = self._modem.record_audio()
        # TODO: save message to DB


def test(args):

    from modem import Modem

    # TODO: decouple CallAttendant from modem
    modem = Modem(None)
    messenger = Messenger(None, modem)

    return 0


if __name__ == '__main__':

    import sys
    sys.path.append('../hardware')
    sys.exit(test(sys.argv))
