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
sys.path.append(os.path.join(currentdir, "screening"))
sys.path.append(os.path.join(currentdir, "hardware"))

import queue
import sqlite3
import time
from pprint import pprint
from datetime import datetime
from config import Config
from screening.calllogger import CallLogger
from screening.callscreener import CallScreener
from hardware.modem import Modem
from hardware.indicators import RingIndicator, ApprovedIndicator, BlockedIndicator
import userinterface.webapp as webapp


class CallAttendant(object):
    """The CallAttendant provides call logging and call screening services."""

    def __init__(self, config):
        """
        The constructor initializes and starts the Call Attendant.
            :param config: the application config dict
        """
        # The application-wide configuration
        self.config = config

        # Open the database
        db_path = None
        if self.config["TESTING"]:
            self.db = sqlite3.connect(":memory:")
        else:
            db_path = os.path.join(self.config['ROOT_PATH'], self.config['DATABASE'])
            self.db = sqlite3.connect(db_path)

        # Create a synchronized queue for incoming callers from the modem
        self._caller_queue = queue.Queue()

        # Screening subsystem
        self.logger = CallLogger(self.db, self.config)
        self.screener = CallScreener(self.db, self.config)

        # Hardware subsystem
        # Create the modem with the callback functions that it invokes
        # when incoming calls are received.
        self.modem = Modem(self.config, self.phone_ringing, self.handle_caller)
        # Initialize the visual indicators (LEDs)
        self.approved_indicator = ApprovedIndicator()
        self.blocked_indicator = BlockedIndicator()
        self.ring_indicator = RingIndicator()

        # Start the User Interface subsystem (Flask)
        # Skip if we're running functional tests, because when testing
        # we use a memory database which can't be shared between threads.
        if not self.config["TESTING"]:
            print("Staring the Flask webapp")
            webapp.start(db_path)

    def handle_caller(self, caller):
        """
        A callback function used by the modem that places the given
        caller object into the synchronized queue for processing by the
        run method.
            :param caller: a dict object with caller ID information
        """
        if self.config["DEBUG"]:
            print("Adding to caller queue:")
            pprint(caller)
        self._caller_queue.put(caller)

    def phone_ringing(self, enabled):
        """
        A callback fucntion used by the modem to signal if the phone
        is ringing. It controls the phone ringing status indicator.
            :param enabled: If True, signals the phone is ringing
        """
        if enabled:
            self.ring_indicator.turn_on()
        else:
            self.ring_indicator.turn_off()

    def run(self):
        """
        Processes incoming callers by logging, screening, blocking
        and/or recording messages.
        """
        # Get relevant config settings
        root_path = self.config['ROOT_PATH']
        screening_mode = self.config['SCREENING_MODE']
        # Get configuration subsets
        block = self.config.get_namespace("BLOCK_")
        blocked = self.config.get_namespace("BLOCKED_")
        voice_mail = self.config.get_namespace("VOICE_MAIL_")
        # Build some common paths
        blocked_greeting_file = os.path.join(root_path, blocked['greeting_file'])
        general_greeting_file = os.path.join(root_path, voice_mail['greeting_file'])
        leave_message_file = os.path.join(root_path, voice_mail['leave_message_file'])
        voice_mail_menu_file = os.path.join(root_path, voice_mail['menu_file'])
        message_path = os.path.join(root_path, voice_mail["message_folder"])
        # Ensure the message path exists
        if not os.path.exists(message_path):
            os.makedirs(message_path)

        # Instruct the modem to start feeding calls into the caller queue
        self.modem.handle_calls()

        # Process incoming calls
        while 1:
            try:
                # Wait (blocking) for a caller
                caller = self._caller_queue.get()

                # ======================================================
                # DEVELOPMENT code block
                # ======================================================
                if self.config["ENV"] == "development":

                    # Perform the call screening
                    caller_permitted = False
                    caller_blocked = False

                    # Check the whitelist
                    if "whitelist" in screening_mode:
                        print("Checking whitelist(s)")
                        if self.screener.is_whitelisted(caller):
                            permitted_caller = True
                            caller["ACTION"] = "Permitted"
                            self.approved_indicator.turn_on()

                    # Now check the blacklist if not preempted by whitelist
                    if not caller_permitted and "blacklist" in screening_mode:
                        print("Checking blacklist(s)")
                        if self.screener.is_blacklisted(caller):
                            caller_blocked = True
                            caller["ACTION"] = "Blocked"
                            self.blocked_indicator.turn_on()

                    if not caller_permitted and not caller_blocked:
                        caller["ACTION"] = "Screened"

                    # Log every call to the database
                    call_no = self.logger.log_caller(caller)

                    # Apply the configured actions to blocked callers
                    if caller_blocked:

                        # Build a filename for a potential message
                        phone_no = caller["NMBR"]
                        message_file = os.path.join(message_path,
                            "{}_{}-{}-{}_{}.wav".format(
                                call_no,
                                phone_no[0:3], phone_no[3:6], phone_no[6:],
                                datetime.now().strftime("%Y%m%d-%H%M%S")
                            )
                        )
                        # Go "off-hook"
                        # - Acquires a lock on the modem
                        # - MUST be followed by hang_up()
                        if self.modem.pick_up():
                            try:
                                # Play greeting
                                if "greeting" in blocked["actions"]:
                                    self.modem.play_audio(blocked_greeting_file)

                                # Record message
                                if "record_message" in blocked["actions"]:
                                    self.modem.play_audio(leave_message_file)
                                    self.modem.record_audio(message_file)

                                # Enter voice mail
                                elif "voice_mail" in blocked["actions"]:
                                    tries = 0
                                    while tries < 3:
                                        self.modem.play_audio(voice_mail_menu_file)
                                        digit = self.modem.wait_for_keypress(5)
                                        if digit == '1':
                                            self.modem.record_audio(message_file)
                                            time.sleep(1)
                                            # play goodbye
                                            break
                                        elif digit == '0':
                                            # play goodbye
                                            break
                                        else:
                                            # play invalid response
                                            tries += 1
                            finally:
                                # Go "on-hook"
                                self.modem.hang_up()

                # ======================================================
                # End DEVELOPMENT code block
                # ======================================================
                else:  # PRODUCTION code block

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
                                self.modem.block_call(caller)

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

    # Always print the configuration
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
