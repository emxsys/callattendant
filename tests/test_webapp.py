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
import sys
import unittest

currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(currentdir, "../src"))
sys.path.append(os.path.join(currentdir, "../src/hardware"))
sys.path.append(os.path.join(currentdir, "../src/messaging"))
sys.path.append(os.path.join(currentdir, "../src/screening"))

from userinterface.webapp import app
from hardware.indicators import MessageIndicator

class TestFlask(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        # Add addtional settings from callattendant config
        app.config["ROOT_PATH"] = os.path.dirname(os.path.realpath(__file__))
        app.config["DATABASE"] = "../data/callattendant.db"
        app.config["VOICE_MAIL_MESSAGE_FOLDER"] = "../data/messages"
        #app.config["MESSAGE_INDICATOR_LED"] = MessageIndicator(10)
        app.config["DB_PATH"] = os.path.join(app.config["ROOT_PATH"], app.config["DATABASE"])

        self.app = app.test_client()

        self.assertEqual(app.debug, True)

    def test_dashboard(self):
        response = self.app.get('/', follow_redirects = True)
        self.assertEqual(response.status_code, 200)

    def test_calls(self):
        response = self.app.get('/calls', follow_redirects = True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
