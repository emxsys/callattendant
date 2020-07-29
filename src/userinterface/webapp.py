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
from screening.blacklist import Blacklist
from screening.whitelist import Whitelist
import screening.utils
import sqlite3
import thread

# Create the Flask micro web-framework application
app = Flask(__name__)
app.config.from_object(__name__)
app.debug = False  # debug mode prevents app from running in separate thread


@app.route('/')
def call_details():
    '''Display the call details from the calllog table'''

    query = """SELECT
      a.CallLogID,
      a.Name,
      a.Number,
      a.Date,
      a.Time,
      CASE WHEN b.PhoneNo IS NULL THEN 'N' ELSE 'Y' END Whitelisted,
      CASE WHEN c.PhoneNo IS NULL THEN 'N' ELSE 'Y' END Blacklisted,
      CASE WHEN b.PhoneNo IS NOT NULL THEN b.Reason ELSE c.Reason END Reason
    FROM calllog AS a
    LEFT JOIN whitelist AS b ON a.Number = b.PhoneNo
    LEFT JOIN blacklist AS c ON a.Number = c.PhoneNo
    ORDER BY a.SystemDateTime DESC"""
    arguments = []
    result_set = screening.utils.query_db(get_db(), query, arguments)

    records = []
    for record in result_set:
        number = record[2]
        phone_no = '{}-{}-{}'.format(number[0:3], number[3:6], number[6:])
        action = ""
        if record[5] == 'Y':
            action = "Permitted"
        elif record[6] == 'Y':
            action = "Blocked"
        else:
            action = "Screened"

        records.append(dict(
            Call_No=record[0],
            Phone_Number=phone_no,
            Name=record[1],
            Date=record[3],
            Time=record[4],
            Whitelisted=record[5],
            Blacklisted=record[6],
            Action=action,
            Reason=record[7]))
    return render_template('call_details.htm', calls=records)


@app.route('/blacklist')
def blacklist():
    '''Display the blocked numbers from the blacklist table'''
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
    '''Display the permitted numbers from the whitelist table'''
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


@app.route('/manage_caller/<int:call_log_id>', methods=['GET', 'POST'])
def manage_caller(call_log_id):
    '''Display the Manage Caller form'''

    # Post changes to the blacklist or whitelist table before rendering
    if request.method == 'POST':
        number = request.form['phone_no'].replace('-', '')
        if request.form['action'] == 'Permit':
            caller = {}
            caller['NMBR'] = number
            caller['NAME'] = request.form['name']
            caller['REASON'] = request.form['reason']
            print "Adding " + caller['NAME'] + " to whitelist"
            whitelist = Whitelist(get_db())
            whitelist.add_caller(caller)

        elif request.form['action'] == 'RemovePermit':
            print "Removing " + number + " from whitelist"
            whitelist = Whitelist(get_db())
            whitelist.remove_number(number)

        elif request.form['action'] == 'Block':
            caller = {}
            caller['NMBR'] = number
            caller['NAME'] = request.form['name']
            caller['REASON'] = request.form['reason']
            print "Adding " + caller['NAME'] + " to blacklist"
            blacklist = Blacklist(get_db())
            blacklist.add_caller(caller)

        elif request.form['action'] == 'RemoveBlock':
            print "Removing " + number + " from blacklist"
            blacklist = Blacklist(get_db())
            blacklist.remove_number(number)

    # Retrieve the caller information for the given call log entry
    query = """SELECT
      a.CallLogID,
      a.Name,
      a.Number,
      CASE WHEN b.PhoneNo IS NULL THEN 'N' ELSE 'Y' END Whitelisted,
      CASE WHEN c.PhoneNo IS NULL THEN 'N' ELSE 'Y' END Blacklisted,
      CASE WHEN b.PhoneNo IS NOT NULL THEN b.Reason ELSE '' END WhitelistReason,
      CASE WHEN c.PhoneNo IS NOT NULL THEN c.Reason ELSE '' END BlacklistReason
    FROM calllog AS a
    LEFT JOIN whitelist AS b ON a.Number = b.PhoneNo
    LEFT JOIN blacklist AS c ON a.Number = c.PhoneNo
    WHERE a.CallLogID=:call_log_id"""
    arguments = {"call_log_id": call_log_id}
    result_set = screening.utils.query_db(get_db(), query, arguments)
    # Prepare a caller dictionary object for the form
    caller = {}
    if len(result_set) > 0:
        record = result_set[0]
        number = record[2]
        caller.update(dict(
            Call_ID=record[0],
            Phone_Number='{}-{}-{}'.format(number[0:3], number[3:6], number[6:]),
            Name=record[1],
            Whitelisted=record[3],
            Blacklisted=record[4],
            WhitelistReason=record[5],
            BlacklistReason=record[6]))
    else:
        caller.update(dict(
            Call_ID=call_log_id,
            Phone_Number='Number Not Found',
            Name='',
            Whitelisted='N',
            Blacklisted='N',
            WhitelistReason='',
            BlacklistReason=''))
    return render_template('manage_caller.htm', caller=caller)


def get_db():
    '''Returns the callattendant database'''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('callattendant.db')
    return db


def flaskThread():
    with app.app_context():
        call_details()

    # debug mode prevents app from running in separate thread
    app.run(host='0.0.0.0', debug=False)


def start():
    thread.start_new_thread(flaskThread, ())
