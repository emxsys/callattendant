#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_modem.py
#
#  Copyright 2020 Bruce Schubert  <bruce@emxsys.com>
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
import tempfile
import queue
import time
from pprint import pprint
from tempfile import gettempdir

import pytest

from callattendant.config import Config
from callattendant.hardware.modem import Modem, RESET, \
    GET_MODEM_PRODUCT_CODE, GET_MODEM_SETTINGS, \
    ENTER_VOICE_MODE, TELEPHONE_ANSWERING_DEVICE_OFF_HOOK, \
    ENTER_VOICE_TRANSMIT_DATA_STATE, DTE_END_VOICE_DATA_TX, \
    ENTER_VOICE_RECIEVE_DATA_STATE, DTE_END_VOICE_DATA_RX, \
    TERMINATE_CALL, ETX_CODE, DLE_CODE, \
    SET_VOICE_COMPRESSION, SET_VOICE_COMPRESSION_CONEXANT

global SET_VOICE_COMPRESSION

# Skip the test when running under continous integraion
pytestmark = pytest.mark.skipif(os.getenv("CI") == "true", reason="Hardware not installed")


@pytest.fixture(scope='module')
def modem():

    # Create a config object with default settings
    config = Config()
    config['DEBUG'] = True
    config['TESTING'] = True
    config['VOICE_MAIL_MESSAGE_FOLDER'] = gettempdir()

    modem = Modem(config)

    yield modem

    modem.stop()


def test_modem_online(modem):
    assert modem.is_open


def test_profile_reset(modem):
    assert modem._send(RESET)


def test_get_modem_settings(modem):
    assert modem._send(GET_MODEM_SETTINGS)


def test_put_modem_into_voice_mode(modem):
    assert modem._send(ENTER_VOICE_MODE)


def test_set_compression_method_and_sampling_rate_specifications(modem):
    assert modem._send(
        SET_VOICE_COMPRESSION_CONEXANT if modem.model == "CONEXANT" else SET_VOICE_COMPRESSION
    )


def test_put_modem_into_TAD_mode(modem):
    assert modem._send(TELEPHONE_ANSWERING_DEVICE_OFF_HOOK)


def test_put_modem_into_voice_transmit_data_state(modem):
    assert modem._send(ENTER_VOICE_TRANSMIT_DATA_STATE, "CONNECT")


def test_cancel_voice_data_transmit_state(modem):
    assert modem._send(DTE_END_VOICE_DATA_TX)


def test_put_modem_into_voice_recieve_data_state(modem):
    assert modem._send(ENTER_VOICE_RECIEVE_DATA_STATE, "CONNECT")


def test_cancel_data_receive_state(modem):
    response = "OK" if modem.model == "CONEXANT" else ETX_CODE
    assert modem._send(DTE_END_VOICE_DATA_RX, response)


def test_terminate_call(modem):
    assert modem._send(TERMINATE_CALL)


def test_pick_up(modem):
    assert modem.pick_up()


def test_hang_up(modem):
    assert modem.hang_up()


def test_playing_audio(modem):
    currentdir = os.path.dirname(os.path.realpath(__file__))
    assert modem.play_audio(os.path.join(currentdir, "../callattendant/resources/sample.wav"))


def test_recording_audio(modem):
    filename = os.path.join(modem.config["DATA_PATH"], "message.wav")
    assert modem.record_audio(filename, detect_silence=False)


def test_recording_audio_detect_silence(modem):
    filename = os.path.join(modem.config["DATA_PATH"], "message.wav")
    assert not modem.record_audio(filename)


def test_call_handler(modem, mocker):
    # Incoming caller id test data: valid numbers are sequential 10 digit repeating nums,
    # plus some spurious call data intermixed between caller ids
    call_data = [
        b"RING", b"DATE=0101", b"TIME=0101", b"NMBR=1111111111", b"NAME=Test1",
        b"RING", b"DATE=0202", b"TIME=0202", b"NMBR=2222222222",  # Test2 - no name
        b"RING", b"NMBR=3333333333",                              # Test3 - number only
        b"RING", b"DATE=0404", b"TIME=0404", b"NMBR=4444444444", b"NAME=Test4",
        b"RING", b"RING", b"NAME=TestNoNumber", b"RING", b"RING",  # Partial data w/o number
        b"RING", b"DATE=0505", b"TIME=0505", b"NMBR=5555555555", b"NAME=Test5",
    ]
    data_queue = queue.Queue()
    caller_queue = queue.Queue()

    # Mock Serial.readline() with a 1 sec timeout
    def mock_readline():
        try:
            return data_queue.get(True, 1)
        except queue.Empty:
            return b''
    mocker.patch.object(modem._serial, "readline", mock_readline)

    # Define the _call_handler callback and start the call handler thread
    def handle_call(call_record):
        caller_queue.put(call_record)
    modem.start(handle_call)

    # Roughly simulate incoming calls
    for x in call_data:
        if x == b"RING":
            time.sleep(3)
        data_queue.put(x)

    # Wait for last call to be processed, then stop the modem thread
    time.sleep(3)
    modem._stop_event.set()
    modem._thread.join()

    # Put the call records into an array for asserts in a loop
    calls_rcvd = []
    while not caller_queue.empty():
        call_record = caller_queue.get_nowait()
        calls_rcvd.append(call_record)
        print(call_record)

    # Run the asserts
    n = 1
    for call in calls_rcvd:
        # Assert all four data elements are present
        assert all(k in call for k in ("DATE", "TIME", "NAME", "NMBR"))

        # Assert the number and name matches the inputs or defaults
        assert call["NMBR"] == str(n) * 10
        if n in [1, 4, 5]:
            assert call["NAME"] == "Test{}".format(n)
        else:
            assert call["NAME"] == "Unknown"
        n += 1
