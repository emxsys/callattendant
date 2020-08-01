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

import os
import sqlite3
from config import Config
from Queue import Queue
from screening.calllogger import CallLogger
from screening.callscreener import CallScreener
from hardware.modem import Modem
from hardware.indicators import RingIndicator, ApprovedIndicator, BlockedIndicator
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

        database = os.path.join(config['ROOT_PATH'], config['DATABASE'])
        self.db = sqlite3.connect(database)

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
        self.modem.handle_calls()

        # User Interface subsystem
        webapp.start()

        # Get relevant config settings
        mode = config['SCREENING_MODE']
        block = config.get_namespace("BLOCK_")
        blocked = config.get_namespace("BLOCKED_")
        blocked_message_file = os.path.join(config['ROOT_PATH'], blocked['message_file'])

        # Run the app
        while 1:
            """Processes incoming callers with logging and screening."""

            # Wait (blocking) for a caller
            caller = self._caller_queue.get()

            # Perform the call screening
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
                    if block['enabled']:
                        self.modem.block_call()

            # Log every call to the database
            self.logger.log_caller(caller)

def make_config(filename = None):
    '''Creates the config dictionary for this application/module.
        :param filename: the filename of a python configuration file.
            This can either be an absolute filename or a filename
            relative to this module's location.
        :return: a config dict'''

    # Establish the default configuration settings
    root_path = os.path.dirname(os.path.realpath(__file__))
    default_config = {
        "ENV": 'production',
        "DEBUG": False,
        "TESTING": False,
        "ROOT_PATH": root_path,
        "DATABASE": "callattendant.db",
        "SCREENING_MODE": "whitelist_and_blacklist",
        "BLOCK_ENABED": True,
        "BLOCK_NAME_PATTERNS": {"V[0-9]{15}": "Telemarketer Caller ID",},
        "BLOCK_NUMBER_PATTERNS": { },
        "BLOCKED_MESSAGE_ENABLED": True,
        "BLOCKED_MESSAGE_FILE": "hardware/sample.wav",
    }
    cfg = Config(root_path, default_config)

    # Load the config file, which may overwrite defaults
    if not filename == None:
        cfg.from_pyfile(filename)

    # Validate


    return cfg


def main(argv):
    """Create and run the call attendent"""

    # Process command line arguments
    import sys, getopt
    syntax = 'Usage: python callattendant.py -c [FILE]'
    configfile = None
    try:
        opts, args = getopt.getopt(argv,"hc:",["help","config="])
    except getopt.GetoptError:
        print syntax
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print syntax
            print '-c, --config=[FILE]\tload a python configuration file'
            print '-h, --help\t\tdisplays this help text'
            sys.exit()
        elif opt in ("-c", "--config"):
            configfile = arg

    # Create the global config dict
    global config
    config = make_config(configfile)

    # Start the application
    app = CallAttendant()
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]))
    print("Done")
