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
import threading
from datetime import datetime
from messaging.message import Message
from hardware.indicators import MessageIndicator, MessageCountIndicator, \
        GPIO_MESSAGE, GPIO_MESSAGE_COUNT_PINS, GPIO_MESSAGE_COUNT_KWARGS


class VoiceMail:

    def __init__(self, db, config, modem):
        """
        Initialize the database tables for voice messages.
        """
        if config["DEBUG"]:
            print("Initializing VoiceMail")

        self.db = db
        self.config = config
        self.modem = modem

        # Create a message event shared with the Message class used to monitor changes
        self.message_event = threading.Event()
        self.config["MESSAGE_EVENT"] = self.message_event

        # Initialize the message indicators (LEDs)
        self.message_indicator = MessageIndicator(
                self.config.get("GPIO_LED_MESSAGE_PIN", GPIO_MESSAGE),
                self.config.get("GPIO_LED_MESSAGE_BRIGHTNESS", 100))
        pins = self.config.get("GPIO_LED_MESSAGE_COUNT_PINS", GPIO_MESSAGE_COUNT_PINS)
        kwargs = self.config.get("GPIO_LED_MESSAGE_COUNT_KWARGS", GPIO_MESSAGE_COUNT_KWARGS)
        self.message_count_indicator = MessageCountIndicator(*pins, **kwargs)

        # Create the Message object used to interface with the DB
        self.messages = Message(db, config)

        # Start the thread that monitors the message events and updates the indicators
        self.event_thread = threading.Thread(target=self._event_handler)
        self.event_thread.name = "voice_mail_event_handler"
        self.event_thread.start()

        # Pulse the indicator if an unplayed msg is waiting
        self.reset_message_indicator()

        if self.config["DEBUG"]:
            print("VoiceMail initialized")

    def _event_handler(self):
        """
        Thread function that updates the message indicators upon a message event.
        """
        while 1:
            # Get the number of unread messages
            if self.message_event.wait():
                if self.config["DEBUG"]:
                    print("Message Event triggered")
                self.reset_message_indicator()

    def voice_messaging_menu(self, call_no, caller):
        """
        Play a voice message menu and respond to the choices.
        """
        # Build some common paths
        voice_mail = self.config.get_namespace("VOICE_MAIL_")
        voice_mail_menu_file = voice_mail['menu_file']
        invalid_response_file = voice_mail['invalid_response_file']
        goodbye_file = voice_mail['goodbye_file']

        # Indicate the user is in the menu
        self.message_indicator.blink()

        tries = 0
        wait_secs = 8   # Candidate for configuration
        rec_msg = False
        while tries < 3:
            self.modem.play_audio(voice_mail_menu_file)
            success, digit = self.modem.wait_for_keypress(wait_secs)
            if not success:
                break
            if digit == '1':
                self.record_message(call_no, caller)
                rec_msg = True  # prevent a duplicate reset_message_indicator
                break
            elif digit == '0':
                # End this call
                break
            else:
                # Try again--up to a limit
                self.modem.play_audio(invalid_response_file)
                tries += 1
        self.modem.play_audio(goodbye_file)
        if not rec_msg:
            self.reset_message_indicator()

    def record_message(self, call_no, caller):
        """
        Records a message.
        """
        # Build the filename used for a potential message
        path = self.config["VOICE_MAIL_MESSAGE_FOLDER"]
        filepath = os.path.join(path, "{}_{}_{}_{}.wav".format(
            call_no,
            caller["NMBR"],
            caller["NAME"].replace('_', '-'),
            datetime.now().strftime("%m%d%y_%H%M")))

        # Play instructions to caller
        leave_msg_file = self.config["VOICE_MAIL_LEAVE_MESSAGE_FILE"]
        self.modem.play_audio(leave_msg_file)

        # Show recording in progress
        self.message_indicator.turn_on()

        if self.modem.record_audio(filepath):
            # Save to Message table (message.add will update the indicator)
            msg_no = self.messages.add(call_no, filepath)
            # Return the messageID on success
            return msg_no
        else:
            self.reset_message_indicator()
            # Return failure
            return None

    def delete_message(self, msg_no):
        """
        Removes the message record and associated wav file.
        """
        # Remove  message and file (message.delete will update the indicator)
        return self.messages.delete(msg_no)

    def reset_message_indicator(self):
        unplayed_count = self.messages.get_unplayed_count()
        if self.config["DEBUG"]:
            print("Resetting Message Indicator to show {} unplayed messages".format(unplayed_count))
        if unplayed_count > 0:
            self.message_indicator.pulse()
            if unplayed_count < 10:
                self.message_count_indicator.display(unplayed_count)
                self.message_count_indicator.decimal_point = False
            else:
                self.message_count_indicator.display(9)
                self.message_count_indicator.decimal_point = True
        else:
            self.message_indicator.turn_off()
            self.message_count_indicator.display(' ')
            self.message_count_indicator.decimal_point = False
