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
import sys
import tempfile
from pprint import pprint

import pytest

from src.callattendant import make_config
from src.hardware.modem import Modem, FACTORY_RESET, RESET, DISPLAY_MODEM_SETTINGS, \
    ENTER_VOICE_MODE, SET_VOICE_COMPRESSION_8BIT_SAMPLING_8K, ENTER_TELEPHONE_ANSWERING_DEVICE_OFF_HOOK, \
    ENTER_VOICE_TRANSMIT_DATA_STATE, DTE_END_VOICE_DATA_TX, ENTER_VOICE_RECIEVE_DATA_STATE, \
    DTE_END_RECIEVE_DATA_STATE, TERMINATE_CALL, ETX_CODE


def dummy_handle_caller(caller):
    # Dummy callback function
    pprint(caller)
    pass


@pytest.fixture(scope='module')
def modem():

    # Load and tweak the default config
    from callattendant import make_config, print_config
    config = make_config()
    config['DEBUG'] = True
    config['TESTING'] = True

    modem = Modem(config, dummy_handle_caller)
    # modem.open_serial_port()
    modem._init_modem()

    return modem


def test_factory_reset(modem):
    assert modem._send(FACTORY_RESET)


def test_profile_reset(modem):
    assert modem._send(RESET)


def test_display_modem_settings(modem):
    assert modem._send(DISPLAY_MODEM_SETTINGS)


def test_put_modem_into_voice_mode(modem):
    assert modem._send(ENTER_VOICE_MODE)


def test_set_compression_method_and_sampling_rate_specifications(modem):
    assert modem._send(SET_VOICE_COMPRESSION_8BIT_SAMPLING_8K)


def test_put_modem_into_TAD_mode(modem):
    assert modem._send(ENTER_TELEPHONE_ANSWERING_DEVICE_OFF_HOOK)


def test_put_modem_into_voice_transmit_data_state(modem):
    assert modem._send(ENTER_VOICE_TRANSMIT_DATA_STATE, "CONNECT")


def test_cancel_voice_data_transmit_state(modem):
    assert modem._send(DTE_END_VOICE_DATA_TX)


def test_put_modem_into_voice_recieve_data_state(modem):
    assert modem._send(ENTER_VOICE_RECIEVE_DATA_STATE, "CONNECT")


def test_cancel_data_transmit_state(modem):
    assert modem._send(DTE_END_RECIEVE_DATA_STATE, ETX_CODE)


def test_terminate_call(modem):
    assert modem._send(TERMINATE_CALL)


def test_pick_up(modem):
    assert modem.pick_up()


def test_hang_up(modem):
    assert modem.hang_up()


def test_playing_audio(modem):
    currentdir = os.path.dirname(os.path.realpath(__file__))
    assert modem.play_audio(os.path.join(currentdir, "../src/resources/sample.wav"))


def test_recording_audio(modem):
    assert modem.record_audio("message.wav")
