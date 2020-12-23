#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_voicemail.py
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
import sqlite3
from tempfile import gettempdir

import pytest

from callattendant.config import Config
from callattendant.hardware.modem import Modem
from callattendant.screening.calllogger import CallLogger
from callattendant.messaging.voicemail import VoiceMail

# Test data
caller = {"NAME": "Bruce", "NMBR": "1234567890", "DATE": "1012", "TIME": "0600"}


@pytest.fixture(scope='module')
def db():

    # Create the test db in RAM
    db = sqlite3.connect(":memory:")
    return db


@pytest.fixture(scope='module')
def config():

    # Use a config object with defaults
    config = Config()
    config['DEBUG'] = True
    config['TESTING'] = True
    config['VOICE_MAIL_MESSAGE_FOLDER'] = gettempdir()

    return config


@pytest.fixture(scope='module')
def logger(db, config):

    logger = CallLogger(db, config)
    return logger


@pytest.fixture(scope='module')
def modem(db, config):

    modem = Modem(config)
    yield modem
    modem.stop()


@pytest.fixture(scope='module')
def voicemail(db, config, modem):

    voicemail = VoiceMail(db, config, modem)
    yield voicemail
    voicemail.stop()


# Skip the test when running under continous integraion
@pytest.mark.skipif(os.getenv("CI") == "true", reason="Hardware not installed")
def test_multiple(voicemail, logger):

    call_no = logger.log_caller(caller)
    msg_no = voicemail.record_message(call_no, caller, detect_silence=False)
    assert msg_no > 0

    count = voicemail.messages.get_unplayed_count()
    assert count == 1

    assert voicemail.delete_message(msg_no)
