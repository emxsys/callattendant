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
import screening.utils
import sqlite3
import thread

# Create the Flask micro web-framework application
app = Flask(__name__)
app.config.from_object(__name__)
app.debug = False  # debug mode prevents app from running in separate thread

@app.route('/call_details')
def call_details():
    query = 'SELECT * from CallLog ORDER BY datetime(SystemDateTime) DESC'
    arguments = []
    result_set = screening.utils.query_db(get_db(), query, arguments)
    call_records = []
    for record in result_set:
        number = record[2]
        phone_no = '{}-{}-{}'.format(number[0:3], number[3:6], number[6:])
        call_records.append(dict(Call_No=record[0], Phone_Number=phone_no, Name=record[1], Modem_Date=record[3], Modem_Time=record[4], System_Date_Time=record[5]))
    #print call_records
    return render_template('call_details.htm',call_records=call_records)

@app.route('/blacklist')
def blacklist():
    query = 'SELECT * from Blacklist ORDER BY datetime(SystemDateTime) DESC'
    arguments = []
    result_set = screening.utils.query_db(get_db(), query, arguments)
    records = []
    for record in result_set:
        number = record[0]
        phone_no = '{}-{}-{}'.format(number[0:3], number[3:6], number[6:])
        records.append(dict(
            Phone_Number=phone_no,
            Name=record[1],
            Reason=record[2],
            System_Date_Time=record[3]))
    return render_template('blacklist.htm', blacklist=records)

@app.route('/whitelist')
def whitelist():
    query = 'SELECT * from Whitelist ORDER BY datetime(SystemDateTime) DESC'
    arguments = []
    result_set = screening.utils.query_db(get_db(), query, arguments)
    records = []
    for record in result_set:
        number = record[0]
        phone_no = '{}-{}-{}'.format(number[0:3], number[3:6], number[6:])
        records.append(dict(
            Phone_Number=phone_no,
            Name=record[1],
            Reason=record[2],
            System_Date_Time=record[3]))
    return render_template('whitelist.htm', whitelist=records)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('callattendant.db')
    return db

def flaskThread():
    with app.app_context():
        call_details()

    # debug mode prevents app from running in separate thread
    app.run(host='0.0.0.0',  debug=False)

def start():

    thread.start_new_thread(flaskThread,())

