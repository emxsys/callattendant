#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_webapp.py
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

import pytest

# ~ from hardware.indicators import MessageIndicator
from callattendant.userinterface.webapp import app, get_random_string, get_db


# Read in SQL for populating test data
with open(os.path.join(os.path.dirname(__file__), "callattendant.db.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def myapp():
    """Create and configure a new app instance for each test."""

    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()

    app.secret_key = get_random_string()
    with app.app_context():

        master_config = {
            "DB_FILE": db_path,
            "PHONE_DISPLAY_FORMAT": "###-###-####",
            "PHONE_DISPLAY_SEPARATOR": "-",
        }

        app.config['MASTER_CONFIG'] = master_config
        app.config["TESTING"] = True
        app.config["DEBUG"] = True

        get_db().executescript(_data_sql)

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(myapp):
    """A test client for the app."""
    return app.test_client()


def test_dashboard(client):
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Statistics" in response.data
    assert b"Recent Calls" in response.data
    assert b"Calls per Day" in response.data
