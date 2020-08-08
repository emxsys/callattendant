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
            self.db = sqlite3.connect(os.path.join(
                self.config['ROOT_PATH'],
                self.config['DATABASE']))

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
            webapp.start(config)

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

    def leave_voice_message(self, call_no, caller, voice_mail_menu=False):

        # Build some common paths
        root_path = self.config['ROOT_PATH']
        voice_mail = self.config.get_namespace("VOICE_MAIL_")
        goodbye_file = os.path.join(root_path, voice_mail['goodbye_file'])
        invalid_response_file = os.path.join(root_path, voice_mail['invalid_response_file'])
        leave_message_file = os.path.join(root_path, voice_mail['leave_message_file'])
        voice_mail_menu_file = os.path.join(root_path, voice_mail['menu_file'])
        # Build the filename used for a potential message
        message_path = os.path.join(root_path, voice_mail["message_folder"])
        message_file = os.path.join(message_path, "{}_{}_{}_{}.wav".format(
            call_no,
            caller["NMBR"],
            caller["NAME"].replace('_', '-'),
            datetime.now().strftime("%m%d%y_%H%M")))

        if voice_mail_menu:
            tries = 0
            while tries < 3:
                self.modem.play_audio(voice_mail_menu_file)
                success, digit = self.modem.wait_for_keypress(5)
                if not success:
                    break
                if digit == '1':
                    # Leave a message
                    self.modem.play_audio(leave_message_file)
                    self.modem.record_audio(message_file)
                    break
                elif digit == '0':
                    # End this call
                    break
                else:
                    # Try again--up to a limit
                    self.modem.play_audio(invalid_response_file)
                    tries += 1
        else:
            self.modem.play_audio(leave_message_file)
            self.modem.record_audio(message_file)

        self.modem.play_audio(goodbye_file)

    def run(self):
        """
        Processes incoming callers by logging, screening, blocking
        and/or recording messages.
        """
        # Get relevant config settings
        root_path = self.config['ROOT_PATH']
        screening_mode = self.config['SCREENING_MODE']
        block = self.config.get_namespace("BLOCK_")
        blocked = self.config.get_namespace("BLOCKED_")
        blocked_greeting_file = os.path.join(root_path, blocked['greeting_file'])

        # Instruct the modem to start feeding calls into the caller queue
        self.modem.handle_calls()

        # Process incoming calls
        while 1:
            try:
                # Wait (blocking) for a caller
                caller = self._caller_queue.get()

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

                    # Go "off-hook" - Acquires a lock on the modem - MUST follow with hang_up()
                    if self.modem.pick_up():
                        try:
                            # Play greeting
                            if "greeting" in blocked["actions"]:
                                self.modem.play_audio(blocked_greeting_file)

                            # Record message
                            if "record_message" in blocked["actions"]:
                                self.leave_voice_message(call_no, caller, False)
                            elif "voice_mail" in blocked["actions"]:
                                self.leave_voice_message(call_no, caller, True)

                        except RuntimeError as e:
                            print("** Error handling a blocked caller: {}".format(e))

                        finally:
                            # Go "on-hook"
                            self.modem.hang_up()

            except Exception as e:
                pprint(e)
                print("** Error running callattendant. Exiting.")
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
        "DATABASE": "../data/callattendant.db",
        "SCREENING_MODE": ("whitelist", "blacklist"),
        "BLOCK_ENABLED": True,
        "BLOCK_NAME_PATTERNS": {"V[0-9]{15}": "Telemarketer Caller ID", },
        "BLOCK_NUMBER_PATTERNS": {},
        "BLOCKED_ACTIONS": ("play_message", ),
        "BLOCKED_GREETING_FILE": "resources/blocked_greeting.wav",
        "VOICE_MAIL_GREETING_FILE": "resources/general_greeting.wav",
        "VOICE_MAIL_GOODBYE_FILE": "resources/goodbye.wav",
        "VOICE_MAIL_INVALID_RESPONSE_FILE": "resources/invalid_response.wav",
        "VOICE_MAIL_LEAVE_MESSAGE_FILE": "resources/please_leave_message.wav",
        "VOICE_MAIL_MENU_FILE": "resources/voice_mail_menu.wav",
        "VOICE_MAIL_MESSAGE_FOLDER": "../data/messages",
    }
    # Create the default configuration
    cfg = Config(root_path, default_config)
    # Load the config file, which may overwrite defaults
    if filename is not None:
        cfg.from_pyfile(filename)
    # Always print the configuration
    print_config(cfg)

    return cfg


def validate_config(config):
    success = True

    if config["ENV"] not in ("production", "development"):
        print("* ENV is incorrect: {}".format(config["ENV"]))
        success = False

    if not isinstance(config["DEBUG"], bool):
        print("* DEBUG should be a bool: {}".format(type(config["DEBUG"])))
        success = False
    if not isinstance(config["TESTING"], bool):
        print("* TESTING should be bool: {}".format(type(config["TESTING"])))
        success = False
    if not isinstance(config["BLOCK_ENABLED"], bool):
        print("* BLOCK_ENABLED should be a bool: {}".format(type(config["BLOCK_ENABLED"])))
        success = False

    for mode in config["SCREENING_MODE"]:
        if mode not in ("whitelist", "blacklist"):
            print("* SCREENING_MODE option is invalid: {}".format(mode))
            success = False
    for mode in config["BLOCKED_ACTIONS"]:
        if mode not in ("greeting", "record_message", "voice_mail"):
            print("* BLOCKED_ACTIONS option is invalid: {}".format(mode))
            success = False

    if not config["DATABASE"] == "../data/callattendant.db":
        print("* DATABASE is not '../data/callattendant.db', are you sure this is right?")
        print("  Path is {}".format(config["DATABASE"]))
        if config["ENV"] == "production":
            success = False
    if not config["VOICE_MAIL_MESSAGE_FOLDER"] == "../data/messages":
        print("* VOICE_MAIL_MESSAGE_FOLDER is not '../data/messages', are you sure this is right?")
        print("  Path is {}".format(config["VOICE_MAIL_MESSAGE_FOLDER"]))
        if config["ENV"] == "production":
            success = False

    rootpath = config["ROOT_PATH"]
    filepath = os.path.join(rootpath, config["BLOCKED_GREETING_FILE"])
    if not os.path.exists(filepath):
        print("* BLOCKED_GREETING_FILE not found: {}".format(filepath))
        success = False
    filepath = os.path.join(rootpath, config["VOICE_MAIL_GREETING_FILE"])
    if not os.path.exists(filepath):
        print("* VOICE_MAIL_GREETING_FILE not found: {}".format(filepath))
        success = False
    filepath = os.path.join(rootpath, config["VOICE_MAIL_GOODBYE_FILE"])
    if not os.path.exists(filepath):
        print("* VOICE_MAIL_GOODBYE_FILE not found: {}".format(filepath))
        success = False
    filepath = os.path.join(rootpath, config["VOICE_MAIL_LEAVE_MESSAGE_FILE"])
    if not os.path.exists(filepath):
        print("* VOICE_MAIL_LEAVE_MESSAGE_FILE not found: {}".format(filepath))
        success = False
    filepath = os.path.join(rootpath, config["VOICE_MAIL_MENU_FILE"])
    if not os.path.exists(filepath):
        print("* VOICE_MAIL_MENU_FILE not found: {}".format(filepath))
        success = False
    filepath = os.path.join(rootpath, config["VOICE_MAIL_MESSAGE_FOLDER"])
    if not os.path.exists(filepath):
        print("* VOICE_MAIL_MESSAGE_FOLDER not found: {}".format(filepath))
        success = False

    return success


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
    config_file = get_args(argv)

    # Create the application config dict
    config = make_config(config_file)
    if not validate_config(config):
        print("Configuration is invalid. Please check {}".format(config_file))
        return 1

    # Create and start the application
    app = CallAttendant(config)
    app.run()

    return 0


if __name__ == '__main__':

    sys.exit(main(sys.argv))
    print("Done")
