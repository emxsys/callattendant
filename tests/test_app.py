#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_app.py
#
#  Copyright 2020 Bruce Schubert <bruce@emxsys.com>

#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest
import threading
import time

from callattendant.app import CallAttendant
from callattendant.config import Config

# Globals
call_no = 0
play_audio_called = False
record_message_called = False
voice_messaging_menu_called = False
answer_call_called = False
ignore_call_called = False
caller1 = {"NAME": "CALLER1", "NMBR": "1111111111", "DATE": "0101", "TIME": "0101"}
caller2 = {"NAME": "CALLER2", "NMBR": "2222222222", "DATE": "0202", "TIME": "0202"}
caller3 = {"NAME": "CALLER3", "NMBR": "3333333333", "DATE": "0303", "TIME": "0303"}
caller4 = {"NAME": "CALLER4", "NMBR": "4444444444", "DATE": "0404", "TIME": "0404"}


@pytest.fixture()
def app(mocker):

    # Create a config object with default settings
    config = Config()
    config['DEBUG'] = False
    config['TESTING'] = True
    config["BLOCKED_ACTIONS"] = ("answer", "greeting", "voice_mail")
    config["BLOCKED_RINGS_BEFORE_ANSWER"] = 0
    config["SCREENED_ACTIONS"] = ("answer", "greeting", "record_message")
    config["SCREENED_RINGS_BEFORE_ANSWER"] = 0
    config["PERMITTED_ACTIONS"] = ("ignore",)
    config["PERMITTED_RINGS_BEFORE_ANSWER"] = 4

    # Mock the hardware interfaces
    mocker.patch("hardware.modem.Modem._open_serial_port", return_value=True)
    mocker.patch("hardware.modem.Modem.start", return_value=True)
    mocker.patch("hardware.modem.Modem.pick_up", return_value=True)
    mocker.patch("hardware.modem.Modem.hang_up", return_value=True)
    mocker.patch("hardware.modem.Modem.play_audio", return_value=True)
    mocker.patch("hardware.indicators.ApprovedIndicator.__init__", return_value=None)
    mocker.patch("hardware.indicators.ApprovedIndicator.blink")
    mocker.patch("hardware.indicators.ApprovedIndicator.close")
    mocker.patch("hardware.indicators.BlockedIndicator.__init__", return_value=None)
    mocker.patch("hardware.indicators.BlockedIndicator.blink")
    mocker.patch("hardware.indicators.BlockedIndicator.close")
    mocker.patch("hardware.indicators.MessageIndicator.__init__", return_value=None)
    mocker.patch("hardware.indicators.MessageIndicator.pulse")
    mocker.patch("hardware.indicators.MessageIndicator.turn_on")
    mocker.patch("hardware.indicators.MessageIndicator.turn_off")
    mocker.patch("hardware.indicators.MessageIndicator.close")
    mocker.patch("hardware.indicators.MessageCountIndicator.__init__", return_value=None)
    mocker.patch("hardware.indicators.MessageCountIndicator.display")
    mocker.patch("hardware.indicators.MessageCountIndicator.decimal_point")
    mocker.patch("hardware.indicators.MessageCountIndicator.close")
    mocker.patch("hardware.indicators.RingIndicator.__init__", return_value=None)
    mocker.patch("hardware.indicators.RingIndicator.blink")
    mocker.patch("hardware.indicators.RingIndicator.close")

    def mock_is_whitelisted(caller):
        if caller["NAME"] in ["CALLER1", "CALLER3"]:
            return (True, "whitelisted")
        else:
            return (False, None)

    def mock_is_blacklisted(caller):
        if caller["NAME"] in ["CALLER2", "CALLER3"]:
            return True, "blacklisted"
        else:
            return False, None

    def assert_log_caller_action(caller, action, reason):
        name = caller["NAME"]
        print("{} {}".format(name, action))
        # Assertions
        if name == "CALLER1":
            # Whitelisted
            assert action == "Permitted"
        elif name == "CALLER2":
            # Blacklisted
            assert action == "Blocked"
        elif name == "CALLER3":
            # Whitelisted and blacklisted; whitelist takes precedence
            assert action == "Permitted"
        else:
            # Not whitelisted or blacklisted
            assert action == "Screened"

        global call_no
        call_no += 1  # Generate a unique call # for return value
        return call_no

    def mock_ignore_call(caller):
        print("Ignoring call")
        global ignore_call_called
        ignore_call_called = True

    def mock_pick_up():
        print("Answering call")
        global answer_call_called
        answer_call_called = True
        return True

    def mock_play_audio(audio_file):
        print("Playing audio")
        global play_audio_called
        play_audio_called = True
        return True

    def mock_record_message(call_no, caller, detect_silence=True):
        print("Recording audio")
        global record_message_called
        record_message_called = True
        return True

    def mock_voice_messaging_menu(call_no, caller):
        print("Entering voice mail system")
        global voice_messaging_menu_called
        voice_messaging_menu_called = True
        return True

    # Create and start the application
    app = CallAttendant(config)

    mocker.patch.object(app.modem, "pick_up", mock_pick_up)
    mocker.patch.object(app, "ignore_call", mock_ignore_call)
    mocker.patch.object(app.screener, "is_whitelisted", mock_is_whitelisted)
    mocker.patch.object(app.screener, "is_blacklisted", mock_is_blacklisted)
    mocker.patch.object(app.logger, "log_caller", assert_log_caller_action)
    mocker.patch.object(app.modem, "play_audio", mock_play_audio)
    mocker.patch.object(app.voice_mail, "record_message", mock_record_message)
    mocker.patch.object(app.voice_mail, "voice_messaging_menu", mock_voice_messaging_menu)

    yield app

    app.shutdown()


def test_ignore_permitted(app):
    """
    Tests that permitted calls are ignored (per config)
    """
    thread = threading.Thread(target=app.run)
    thread.start()

    global ignore_call_called
    ignore_call_called = False

    app.handle_caller(caller1)   # Queue a permitted caller with 4 rings
    time.sleep(15)

    assert ignore_call_called

    # Stop the run thread
    app._stop_event.set()


def test_answer_blocked(app):
    """
    Tests that blocked calls are answered (per config)
    """
    thread = threading.Thread(target=app.run)
    thread.start()

    global answer_call_called
    answer_call_called = False

    app.handle_caller(caller2)   # Queue a blocked caller with zero rings
    time.sleep(2)

    assert answer_call_called

    # Stop the run thread
    app._stop_event.set()


def test_answer_screened(app):
    """
    Tests that screened calls are answered (per config)
    """
    thread = threading.Thread(target=app.run)
    thread.start()

    global answer_call_called
    answer_call_called = False

    app.handle_caller(caller4)   # Queue a screend caller with zero rings
    time.sleep(2)

    assert answer_call_called

    # Stop the run thread
    app._stop_event.set()


def test_queued_call(app):
    """
    Test that a call is ignored because a second call is already in the queue
    """
    # Queue the test data
    app.handle_caller(caller2)  # an answerable call that should be ignored
    app.handle_caller(caller3)  # an answerable call that will be answered

    global ignore_call_called
    global answer_call_called
    ignore_call_called = False
    answer_call_called = False

    # Process the queued test data
    thread = threading.Thread(target=app.run)
    thread.start()

    # Wait here until the queue has been processed
    time.sleep(15)

    assert ignore_call_called
    assert answer_call_called

    # Stop the run thread
    app._stop_event.set()


def test_answer_call_no_actions(app, mocker):
    """
    Tests the call answering options used in the answer_call method.
    """
    # Test no additional actions
    global play_audio_called
    global record_message_called
    global voice_messaging_menu_called
    play_audio_called = False
    record_message_called = False
    voice_messaging_menu_called = False

    app.answer_call(("answer"), "greeting.wav", 1, caller1)

    assert not play_audio_called
    assert not record_message_called
    assert not voice_messaging_menu_called


def test_answer_call_greeting(app):

    global play_audio_called
    global record_message_called
    global voice_messaging_menu_called
    play_audio_called = False
    record_message_called = False
    voice_messaging_menu_called = False

    # Test greeting
    app.answer_call(("answer", "greeting",), "greeting.wav", 2, caller2)

    assert play_audio_called
    assert not record_message_called
    assert not voice_messaging_menu_called


def test_answer_call_record_message(app):

    global play_audio_called
    global record_message_called
    global voice_messaging_menu_called
    play_audio_called = False
    record_message_called = False
    voice_messaging_menu_called = False

    # Test recording a message
    app.answer_call(("answer", "record_message"), None, 3, caller4)

    assert not play_audio_called
    assert record_message_called
    assert not voice_messaging_menu_called


def test_answer_call_voice_mail(app):

    global play_audio_called
    global record_message_called
    global voice_messaging_menu_called
    play_audio_called = False
    record_message_called = False
    voice_messaging_menu_called = False

    # Test invoking the voice mail menu
    app.answer_call(("answer", "voice_mail"), None, 4, caller4)

    assert not play_audio_called
    assert not record_message_called
    assert voice_messaging_menu_called
