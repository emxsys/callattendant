#!/usr/bin/python
#
# file: callattendant.py
#
# Copyright 2018 Bruce Schubert <bruce@emxsys.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sqlite3
from Queue import Queue
from telephony.calllogger import CallLogger
from telephony.callscreener import CallScreener
from hardware.modem import Modem
from hardware.indicators import RingIndicator, ApprovedIndicator, \
    BlockedIndicator
import userinterface.webapp as webapp


class CallAttendant(object):
    """The CallAttendant provides call logging and call screening services."""

    def handler_caller(self, caller):
        """Places the caller record in synchronized queue for processing"""
        self._caller_queue.put(caller)

    def phone_ringing(self, enabled):
        """Controls the phone ringing status indicator."""
        if enabled:
            self.ring_indicator.turn_on()
        else:
            self.ring_indicator.turn_off()

    def __init__(self):
        """The constructor initializes and starts the Call Attendant"""
        self.settings = {}
        self.settings["db_name"] = "callattendant.db"  # SQLite3 DB to store incoming call log, whitelist and blacklist
        self.settings["screening_mode"] = "whitelist_and_blacklist"  # no_screening, whitelist_only, whitelist_and_blacklist, blacklist_only
        self.settings["bad_cid_patterns"] = ""  # regex name patterns to ignore
        self.settings["ignore_private_numbers"] = False # Ignore "P" CID names
        self.settings["ignore_unknown_numbers"] = True # Ignore "O" CID names
        self.settings["block_calls"] = True

        self.db = sqlite3.connect(self.settings["db_name"])

        # The current/last caller id
        self._caller_queue = Queue()

        # Visual indicators (LEDs)
        self.approved_indicator = ApprovedIndicator()
        self.blocked_indicator = BlockedIndicator()
        self.ring_indicator = RingIndicator()

        # Telephony subsystems
        self.logger = CallLogger(self.db)
        self.screener = CallScreener(self.db)
        self.modem = Modem(self)

        # User Interface subsystem
        webapp.start()

        # Run the app
        while 1:
            """Processes incoming callers with logging and screening."""

            # Wait (blocking) for a caller
            caller = self._caller_queue.get()

            # Perform the call screening
            mode = self.settings["screening_mode"]
            whitelisted = False
            blacklisted = False
            if mode in ["whitelist_only", "whitelist_and_blacklist"]:
                print "Checking whitelist(s)"
                if self.screener.is_whitelisted(caller):
                    whitelisted = True
                    caller["NOTE"] = "Whitelisted"
                    self.approved_indicator.turn_on()

            if not whitelisted and mode in ["blacklist_only", "whitelist_and_blacklist"]:
                print "Checking blacklist(s)"
                if self.screener.is_blacklisted(caller):
                    blacklisted = True
                    caller["NOTE"] = "Blacklisted"
                    self.blocked_indicator.turn_on()
                    if self.settings["block_calls"]:
                        self.modem.block_call()

            # Log every call to the database
            self.logger.log_caller(caller)


def main(args):
    """Create and run the call attendent"""
    call_attendant = CallAttendant()
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
    print("Done")
