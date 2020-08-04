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
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(currentdir,"screening"))
sys.path.append(os.path.join(currentdir,"hardware"))

import queue
import sqlite3
from pprint import pprint
from config import Config
from screening.calllogger import CallLogger
from screening.callscreener import CallScreener
from hardware.modem import Modem
from hardware.indicators import RingIndicator, ApprovedIndicator, BlockedIndicator
import userinterface.webapp as webapp

class CallAttendant(object):
    """The CallAttendant provides call logging and call screening services."""

    def handle_caller(self, caller):
        """Places the caller record in synchronized queue for processing"""
        if self.config["DEBUG"]:
            print("Adding to caller queue:")
            pprint(caller)
        self._caller_queue.put(caller)

    def phone_ringing(self, enabled):
        """Controls the phone ringing status indicator."""
        if enabled:
            self.ring_indicator.turn_on()
        else:
            self.ring_indicator.turn_off()

    def __init__(self, config):
        """
        The constructor initializes and starts the Call Attendant
            :param config: the application config dict
        """
        self.config = config
        db_path = None
        if self.config["TESTING"]:
            self.db = sqlite3.connect(":memory:")
        else:
            db_path = os.path.join(self.config['ROOT_PATH'], self.config['DATABASE'])
            self.db = sqlite3.connect(db_path)

        # The current/last caller id
        self._caller_queue = queue.Queue()

        # Visual indicators (LEDs)
        self.approved_indicator = ApprovedIndicator()
        self.blocked_indicator = BlockedIndicator()
        self.ring_indicator = RingIndicator()

        # Screening subsystems
        self.logger = CallLogger(self.db, self.config)
        self.screener = CallScreener(self.db, self.config)

        # Hardware subsystem
        self.modem = Modem(self.config, self.phone_ringing, self.handle_caller)

        # Start User Interface subsystem if we're not running functional tests
        # When testing, we're using a memory database, which can't be shared
        if not self.config["TESTING"]:
            webapp.start(db_path)

    def run(self):
        """Processes incoming callers with logging and screening."""
        # Get relevant config settings
        screening_mode = self.config['SCREENING_MODE']
        block = self.config.get_namespace("BLOCK_")
        blocked = self.config.get_namespace("BLOCKED_")
        blocked_message_file = os.path.join(self.config['ROOT_PATH'], blocked['message_file'])

        # Instruct the modem to feed calls into the caller queue
        self.modem.handle_calls()

        # Process incoming calls
        while 1:
            try:
                # Wait (blocking) for a caller
                caller = self._caller_queue.get()

                # Perform the call screening
                whitelisted = False
                blacklisted = False
                if "whitelist" in screening_mode:
                    print("Checking whitelist(s)")
                    if self.screener.is_whitelisted(caller):
                        whitelisted = True
                        caller["NOTE"] = "Whitelisted"
                        self.approved_indicator.turn_on()

                if not whitelisted and "blacklist" in screening_mode:
                    print("Checking blacklist(s)")
                    if self.screener.is_blacklisted(caller):
                        blacklisted = True
                        caller["NOTE"] = "Blacklisted"
                        self.blocked_indicator.turn_on()
                        if block['enabled']:
                            print("Blocking {}".format(caller["NMBR"]))
                            self.modem.block_call()

                # Log every call to the database
                self.logger.log_caller(caller)
            except Exception as e:
                print(e)
                return 1


def make_config(filename=None):
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
        "SCREENING_MODE": ("whitelist", "blacklist"),
        "BLOCK_ENABLED": True,
        "BLOCK_NAME_PATTERNS": {"V[0-9]{15}": "Telemarketer Caller ID", },
        "BLOCK_NUMBER_PATTERNS": {},
        "BLOCKED_ACTIONS": ("play_message", ),
        "BLOCKED_MESSAGE_FILE": "hardware/blocked.wav",
    }
    # Create the default configuration
    cfg = Config(root_path, default_config)
    # Load the config file, which may overwrite defaults
    if filename is not None:
        cfg.from_pyfile(filename)

    if cfg["DEBUG"]:
        print_config(cfg)

    return cfg


def print_config(config):
    """ Pretty print the given configuration dict """
    print("[Configuration]")
    keys = sorted(config.keys())
    for key in keys:
        print("  {} = {}".format(key, config[key]))


def get_args(argv):
    """Get arguments from the command line
        :param argv: sys.argv
        :return: configfile
    """
    import sys
    import getopt
    syntax = 'Usage: python callattendant.py -c [FILE]'
    configfile = None
    try:
        opts, args = getopt.getopt(argv[1:], "hc:", ["help", "config="])
    except getopt.GetoptError:
        print(syntax)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(syntax)
            print("-c, --config=[FILE]\tload a python configuration file")
            print("-h, --help\t\tdisplays this help text")
            sys.exit()
        elif opt in ("-c", "--config"):
            configfile = arg
    return configfile


def main(argv):
    """Create and run the call attendent application"""

    # Process command line arguments
    configfile = get_args(argv)

    # Create the application config dict
    config = make_config(configfile)

    # Create and start the application
    app = CallAttendant(config)
    app.run()

    return 0


if __name__ == '__main__':

    sys.exit(main(sys.argv))
    print("Done")
