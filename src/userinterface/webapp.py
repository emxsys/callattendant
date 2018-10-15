#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  webapp.py
#
#  Copyright 2018 Bruce Schubert  <bruce@emxsys.com>
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

# ==============================================================================
# This code was inspired by and contains code snippets from Pradeep Singh:
# https://github.com/pradeesi/Incoming_Call_Detail_Logger
# https://iotbytes.wordpress.com/incoming-call-details-logger-with-raspberry-pi/
# ==============================================================================

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, send_from_directory, jsonify
import telephony.utils
import sqlite3
import thread

# Create application
app = Flask(__name__)
app.config.from_object(__name__)
app.debug = False  # debug mode prevents app from running in separate thread

@app.route('/call_details')
def call_details():
    query = 'SELECT * from CallLog ORDER BY datetime(SystemDateTime) DESC'
    arguments = []
    result_set = telephony.utils.query_db(get_db(), query, arguments)
    call_records = []
    for record in result_set:
        call_records.append(dict(Call_No=record[0], Phone_Number=record[1], Name=record[2], Modem_Date=record[3], Modem_Time=record[4], System_Date_Time=record[5]))
    #print call_records
    return render_template('call_details.htm',call_records=call_records)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('callattendant.db')
    return db

def flaskThread():
    with app.app_context():
        call_details()
    app.run(host='0.0.0.0')

def start():
    thread.start_new_thread(flaskThread,())

