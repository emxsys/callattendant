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
from __future__ import division

import logging
import os
import re
import random
import string
import _thread
from datetime import datetime, timedelta
from pprint import pformat

import sqlite3
from flask import Flask, request, g, current_app, render_template, redirect, \
    jsonify, flash
from flask_paginate import Pagination, get_page_args
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from screening.query_db import query_db
from screening.blacklist import Blacklist
from screening.whitelist import Whitelist
from messaging.voicemail import Message

# Create the Flask micro web-framework application
app = Flask(__name__)
app.config.from_pyfile('webapp.cfg')


@app.before_request
def before_request():
    """
    Establish a database connection for the current request
    """
    master_config = current_app.config.get("MASTER_CONFIG")
    g.conn = sqlite3.connect(master_config.get("DB_FILE"))
    g.conn.row_factory = sqlite3.Row
    g.cur = g.conn.cursor()


@app.teardown_request
def teardown(error):
    """
    Closes the database connection for the last request
    """
    if hasattr(g, 'conn'):
        g.conn.close()


@app.route('/')
def dashboard():
    """
    Display the dashboard, i.e,, the home page
    """
    # Count totals calls
    sql = "SELECT COUNT(*) FROM CallLog"
    g.cur.execute(sql)
    total_calls = g.cur.fetchone()[0]

    # Count blocked calls
    sql = "SELECT COUNT(*) FROM CallLog WHERE `Action` = 'Blocked'"
    g.cur.execute(sql)
    total_blocked = g.cur.fetchone()[0]

    # Compute percentage blocked
    percent_blocked = 0
    if total_calls > 0:
        percent_blocked = total_blocked / total_calls * 100

    # Get the number of unread messages
    sql = "SELECT COUNT(*) FROM Message WHERE Played = 0"
    g.cur.execute(sql)
    new_messages = g.cur.fetchone()[0]

    # Get the Recent Calls subset
    max_num_rows = 10
    sql = """SELECT
        a.CallLogID,
        CASE
            WHEN b.PhoneNo is not null then b.Name
            WHEN c.PhoneNo is not null then c.Name
            ELSE a.Name
        END Name,
        a.Number,
        a.Date,
        a.Time,
        a.Action,
        a.Reason,
        CASE WHEN b.PhoneNo is null THEN 'N' ELSE 'Y' END Whitelisted,
        CASE WHEN c.PhoneNo is null THEN 'N' ELSE 'Y' end Blacklisted,
        d.MessageID,
        d.Played,
        d.Filename,
        a.SystemDateTime
    FROM CallLog as a
    LEFT JOIN Whitelist AS b ON a.Number = b.PhoneNo
    LEFT JOIN Blacklist AS c ON a.Number = c.PhoneNo
    LEFT JOIN Message AS d ON a.CallLogID = d.CallLogID
    ORDER BY a.SystemDateTime DESC
    LIMIT {}""".format(max_num_rows)
    g.cur.execute(sql)
    result_set = g.cur.fetchall()
    recent_calls = []
    for row in result_set:
        # Flask pages use the static folder to get resources.
        # In the static folder we have created a soft-link to the
        # data/messsages folder containing the actual messages.
        # We'll use the static-based path for the wav-file urls
        # in the web app
        filepath = row[11]
        if filepath is not None:
            basename = os.path.basename(filepath)
            filepath = os.path.join("../static/messages", basename)

        # Create a date object from the date time string
        date_time = datetime.strptime(row[12][:19], '%Y-%m-%d %H:%M:%S')

        recent_calls.append(dict(
            call_no=row[0],
            name=row[1],
            phone_no=format_phone_no(row[2]),
            date=date_time.strftime('%d-%b-%y'),
            time=date_time.strftime('%I:%M %p'),
            action=row[5],
            reason=row[6],
            whitelisted=row[7],
            blacklisted=row[8],
            msg_no=row[9],
            msg_played=row[10],
            wav_file=filepath))

    # Get top permitted callers
    sql = """SELECT COUNT(Number), Number, Name
        FROM CallLog
        WHERE Action IN ('Permitted', 'Screened')
        GROUP BY Number
        ORDER BY COUNT(Number) DESC LIMIT 10"""
    g.cur.execute(sql)
    result_set = g.cur.fetchall()
    top_permitted = []
    for row in result_set:
        top_permitted.append(dict(
            count=row[0],
            phone_no=format_phone_no(row[1]),
            name=row[2]))

    # Get top blocked callers
    sql = """SELECT COUNT(Number), Number, Name
        FROM CallLog
        WHERE Action = 'Blocked'
        GROUP BY Number
        ORDER BY COUNT(Number) DESC LIMIT 10"""
    g.cur.execute(sql)
    result_set = g.cur.fetchall()
    top_blocked = []
    for row in result_set:
        top_blocked.append(dict(
            count=row[0],
            phone_no=format_phone_no(row[1]),
            name=row[2]))

    # Get num calls per day for graphing
    num_days = current_app.config.get("GRAPH_NUM_DAYS", 30)

    # Query num blocked calls
    sql = """SELECT COUNT(DATE(SystemDateTime)) Count, DATE(SystemDateTime) CallDate
        FROM CallLog
        WHERE SystemDateTime > DATETIME('now','-{} day') AND Action = 'Blocked'
        GROUP BY CallDate
        ORDER BY CallDate""".format(num_days)
    g.cur.execute(sql)
    result_set = g.cur.fetchall()
    blocked_per_day = {}
    for row in result_set:
        # key value = date, count
        blocked_per_day[row[1]] = row[0]

    # Query number of allowed calls
    sql = """SELECT COUNT(DATE(SystemDateTime)) Count, DATE(SystemDateTime) CallDate
        FROM CallLog
        WHERE SystemDateTime > DATETIME('now','-{} day') AND Action = 'Permitted'
        GROUP BY CallDate
        ORDER BY CallDate""".format(num_days)
    g.cur.execute(sql)
    result_set = g.cur.fetchall()
    allowed_per_day = {}
    for row in result_set:
        # key value = date, count
        allowed_per_day[row[1]] = row[0]

    # Query number of screened calls
    sql = """SELECT COUNT(DATE(SystemDateTime)) Count, DATE(SystemDateTime) CallDate
        FROM CallLog
        WHERE SystemDateTime > DATETIME('now','-{} day') AND Action = 'Screened'
        GROUP BY CallDate
        ORDER BY CallDate""".format(num_days)
    g.cur.execute(sql)
    result_set = g.cur.fetchall()
    screened_per_day = {}
    for row in result_set:
        # key value = date, count
        screened_per_day[row[1]] = row[0]

    # Conflate the results
    base_date = datetime.today()
    date_list = [base_date - timedelta(days=x) for x in range(num_days)]
    date_list.reverse()
    calls_per_day = []
    for date in date_list:
        date_key = date.strftime("%Y-%m-%d")
        calls_per_day.append(dict(
            date=date_key,
            blocked=blocked_per_day.get(date_key, 0),
            allowed=allowed_per_day.get(date_key, 0),
            screened=screened_per_day.get(date_key, 0)))

    # Render the resullts
    return render_template(
        'dashboard.html',
        active_nav_item="dashboard",
        recent_calls=recent_calls,
        top_permitted=top_permitted,
        top_blocked=top_blocked,
        calls_per_day=calls_per_day,
        new_messages=new_messages,
        total_calls='{:,}'.format(total_calls),
        blocked_calls='{:,}'.format(total_blocked),
        percent_blocked='{0:.0f}%'.format(percent_blocked))


@app.route('/calls', methods=['GET'])
def calls():
    """
    Display the call history from the call log table.
    """

    # Get GET request args, if available
    number = request.args.get('number')
    search_text = request.args.get('search')
    search_type = request.args.get('submit')

    # Get search criteria, if applicable
    search_criteria = ""
    if search_text:
        if search_type == "phone":
            num_list = re.findall('[0-9]+', search_text)
            number = "".join(num_list)  # override GET arg if we're searching
            search_criteria = "WHERE Number='{}'".format(number)
        else:
            search_criteria = "WHERE Caller LIKE '%{}%'".format(search_text)

    # Get values used for pagination of the call log
    sql = "SELECT COUNT(*), Number, Name Caller FROM CallLog {}".format(search_criteria)
    g.cur.execute(sql)
    total = g.cur.fetchone()[0]
    page, per_page, offset = get_page_args(
        page_parameter="page",
        per_page_parameter="per_page")

    # Get the call log subset, limited to the pagination settings
    sql = """SELECT
        a.CallLogID,
        CASE
            WHEN b.PhoneNo is not null then b.Name
            WHEN c.PhoneNo is not null then c.Name
            ELSE a.Name
        END Caller,
        a.Number Number,
        a.Date,
        a.Time,
        a.Action,
        a.Reason,
        CASE WHEN b.PhoneNo is null THEN 'N' ELSE 'Y' END Whitelisted,
        CASE WHEN c.PhoneNo is null THEN 'N' ELSE 'Y' end Blacklisted,
        d.MessageID,
        d.Played,
        d.Filename,
        a.SystemDateTime
    FROM CallLog as a
    LEFT JOIN Whitelist AS b ON a.Number = b.PhoneNo
    LEFT JOIN Blacklist AS c ON a.Number = c.PhoneNo
    LEFT JOIN Message AS d ON a.CallLogID = d.CallLogID
    {}
    ORDER BY a.SystemDateTime DESC
    LIMIT {}, {}""".format(search_criteria, offset, per_page)
    g.cur.execute(sql)
    result_set = g.cur.fetchall()

    # Create a formatted list of records including some derived values
    calls = []
    for row in result_set:
        number = row[2]
        phone_no = '{}-{}-{}'.format(number[0:3], number[3:6], number[6:])
        # Flask pages use the static folder to get resources.
        # In the static folder we have created a soft-link to the
        # data/messsages folder containing the actual messages.
        # We'll use the static-based path for the wav-file urls
        filepath = row[11]
        if filepath is not None:
            basename = os.path.basename(filepath)
            filepath = os.path.join("../static/messages", basename)

        # Create a date object from the date time string
        date_time = datetime.strptime(row[12][:19], '%Y-%m-%d %H:%M:%S')

        calls.append(dict(
            call_no=row[0],
            phone_no=phone_no,
            name=row[1],
            date=date_time.strftime('%d-%b-%y'),
            time=date_time.strftime('%I:%M %p'),
            action=row[5],
            reason=row[6],
            whitelisted=row[7],
            blacklisted=row[8],
            msg_no=row[9],
            msg_played=row[10],
            wav_file=filepath))

    # Create a pagination object for the page
    pagination = get_pagination(
        page=page,
        per_page=per_page,
        total=total,
        record_name="calls",
        format_total=True,
        format_number=True)

    # Render the resullts with pagination
    return render_template(
        'calls.html',
        active_nav_item='calls',
        calls=calls,
        search_criteria=search_criteria,
        page=page,
        per_page=per_page,
        pagination=pagination)


@app.route('/calls/view/<int:call_no>', methods=['GET'])
def calls_view(call_no):
    """
    Display the call details
    """

    # Get the call log subset, limited to the pagination settings
    sql = """SELECT
        a.CallLogID,
        CASE
            WHEN b.PhoneNo is not null then b.Name
            WHEN c.PhoneNo is not null then c.Name
            ELSE a.Name
        END Name,
        a.Number Number,
        a.Date,
        a.Time,
        a.Action,
        a.Reason,
        CASE WHEN b.PhoneNo is null THEN 'N' ELSE 'Y' END Whitelisted,
        CASE WHEN c.PhoneNo is null THEN 'N' ELSE 'Y' end Blacklisted,
        d.MessageID,
        d.Played,
        d.Filename,
        a.SystemDateTime
    FROM CallLog as a
    LEFT JOIN Whitelist AS b ON a.Number = b.PhoneNo
    LEFT JOIN Blacklist AS c ON a.Number = c.PhoneNo
    LEFT JOIN Message AS d ON a.CallLogID = d.CallLogID
    WHERE a.CallLogID={}""".format(call_no)
    g.cur.execute(sql)
    row = g.cur.fetchone()

    caller = {}
    if len(row) > 0:
        number = row[2]
        phone_no = '{}-{}-{}'.format(number[0:3], number[3:6], number[6:])
        # Flask pages use the static folder to get resources.
        # In the static folder we have created a soft-link to the
        # data/messsages folder containing the actual messages.
        # We'll use the static-based path for the wav-file urls
        filepath = row[11]
        if filepath is not None:
            basename = os.path.basename(filepath)
            filepath = os.path.join("../../static/messages", basename)

        # Create a date object from the date time string
        date_time = datetime.strptime(row[12][:19], '%Y-%m-%d %H:%M:%S')

        caller.update(dict(
            call_no=row[0],
            phone_no=phone_no,
            name=row[1],
            date=date_time.strftime('%d-%b-%y'),
            time=date_time.strftime('%I:%M %p'),
            action=row[5],
            reason=row[6],
            whitelisted=row[7],
            blacklisted=row[8],
            msg_no=row[9],
            msg_played=row[10],
            wav_file=filepath))
    else:
        # ~ Flash and return to referer
        pass

    return render_template(
        'calls_view.html',
        caller=caller)


@app.route('/callers/manage/<int:call_no>', methods=['GET', 'POST'])
def callers_manage(call_no):
    """
    Display the Manage Caller form
    """

    post_count = None

    # Post changes to the blacklist or whitelist table before rendering
    if request.method == 'POST':
        number = request.form['phone_no'].replace('-', '')
        if request.form['action'] == 'add-permit':
            caller = {}
            caller['NMBR'] = number
            caller['NAME'] = request.form['name']
            print(" >> Adding " + caller['NAME'] + " to whitelist")
            whitelist = Whitelist(get_db(), current_app.config)
            whitelist.add_caller(caller, request.form['reason'])

        elif request.form['action'] == 'remove-permit':
            print(" >> Removing " + number + " from whitelist")
            whitelist = Whitelist(get_db(), current_app.config)
            whitelist.remove_number(number)

        elif request.form['action'] == 'add-block':
            caller = {}
            caller['NMBR'] = number
            caller['NAME'] = request.form['name']
            print(" >> Adding " + caller['NAME'] + " to blacklist")
            blacklist = Blacklist(get_db(), current_app.config)
            blacklist.add_caller(caller, request.form['reason'])

        elif request.form['action'] == 'remove-block':
            print(" >> Removing " + number + " from blacklist")
            blacklist = Blacklist(get_db(), current_app.config)
            blacklist.remove_number(number)
        # Keep track of the number of posts so we can to unwind the history
        # to bo "back" the original referrer
        post_count = int(request.form['post_count'])
        post_count += 1
    else:
        post_count = 0

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
    arguments = {"call_log_id": call_no}
    result_set = query_db(get_db(), query, arguments)
    # Prepare a caller dictionary object for the form
    caller = {}
    if len(result_set) > 0:
        record = result_set[0]
        number = record[2]
        caller.update(dict(
            call_no=record[0],
            phone_no='{}-{}-{}'.format(number[0:3], number[3:6], number[6:]),
            name=record[1],
            whitelisted=record[3],
            blacklisted=record[4],
            whitelist_reason=record[5],
            blacklist_reason=record[6]))
    else:
        caller.update(dict(
            call_no=call_no,
            phone_no='Number Not Found',
            name='',
            whitelisted='N',
            blacklisted='N',
            whitelist_reason='',
            blacklist_reason=''))

    # Re-render the same page to show the updated content
    return render_template(
        'callers_manage.html',
        caller=caller,
        post_count=post_count)


@app.route('/callers/blocked')
def callers_blocked():
    """
    Display the blocked numbers from the blacklist table
    """
    # Get values used for pagination of the blacklist
    total = get_row_count('Blacklist')
    page, per_page, offset = get_page_args(
        page_parameter="page", per_page_parameter="per_page"
    )

    # Get the blacklist subset, limited to the pagination settings
    sql = 'SELECT * FROM Blacklist ORDER BY datetime(SystemDateTime) DESC LIMIT {}, {}'.format(offset, per_page)
    g.cur.execute(sql)
    result_set = g.cur.fetchall()
    records = []
    for record in result_set:
        number = record[0]
        phone_no = '{}-{}-{}'.format(number[0:3], number[3:6], number[6:])
        records.append(dict(
            Phone_Number=phone_no,
            Name=record[1],
            Reason=record[2],
            System_Date_Time=record[3][:19]))

    # Create a pagination object for the page
    pagination = get_pagination(
        page=page,
        per_page=per_page,
        total=total,
        record_name="blocked numbers",
        format_total=True,
        format_number=True,
    )
    # Render the resullts with pagination
    return render_template(
        'callers_blocked.html',
        active_nav_item='blocked',
        blacklist=records,
        page=page,
        per_page=per_page,
        pagination=pagination,
    )


@app.route('/callers/blocked/add', methods=['POST'])
def callers_blocked_add():
    """
    Add a new blacklist entry
    """
    caller = {}
    # TODO: Strip all none digits from phone via regex
    number = request.form["phone"].replace('-', '')
    caller['NMBR'] = number
    caller['NAME'] = request.form["name"]
    print("Adding " + number + " to blacklist")
    blacklist = Blacklist(get_db(), current_app.config)
    success = blacklist.add_caller(caller, request.form["reason"])
    if success:
        return redirect("/callers/blocked", code=303)
    else:
        # Probably already exists... attempt to update with original form data
        return redirect('/callers/blocked/update/{}'.format(number), code=307)


@app.route('/callers/blocked/update/<string:phone_no>', methods=['POST'])
def callers_blocked_update(phone_no):
    """
    Update the blacklist entry associated with the phone number.
    """
    number = phone_no.replace('-', '')
    print("Updating " + number + " in blacklist")
    blacklist = Blacklist(get_db(), current_app.config)
    blacklist.update_number(number, request.form['name'], request.form['reason'])

    return redirect("/callers/blocked", code=303)


@app.route('/callers/blocked/delete/<string:phone_no>', methods=['GET'])
def callers_blocked_delete(phone_no):
    """
    Delete the blacklist entry associated with the phone number.
    """
    number = phone_no.replace('-', '')

    print("Removing " + number + " from blacklist")
    blacklist = Blacklist(get_db(), current_app.config)
    blacklist.remove_number(number)

    return redirect("/callers/blocked", code=301)  # (re)moved permamently


@app.route('/callers/permitted')
def callers_permitted():
    """
    Display the permitted numbers from the whitelist table
    """
    # Get values used for pagination of the blacklist
    total = get_row_count('Whitelist')
    page, per_page, offset = get_page_args(
        page_parameter="page", per_page_parameter="per_page"
    )
    # Get the whitelist subset, limited to the pagination settings
    sql = 'SELECT * FROM Whitelist ORDER BY datetime(SystemDateTime) DESC LIMIT {}, {}'.format(offset, per_page)
    g.cur.execute(sql)
    result_set = g.cur.fetchall()
    # Build a list of formatted dict items
    records = []
    for record in result_set:
        number = record[0]
        phone_no = '{}-{}-{}'.format(number[0:3], number[3:6], number[6:])
        records.append(dict(
            Phone_Number=phone_no,
            Name=record[1],
            Reason=record[2],
            System_Date_Time=record[3][:19]))  # Strip the decimal secs
    # Create a pagination object for the page
    pagination = get_pagination(
        page=page,
        per_page=per_page,
        total=total,
        record_name="permitted numbers",
        format_total=True,
        format_number=True,
    )
    # Render the results with pagination
    return render_template(
        'callers_permitted.html',
        active_nav_item='permitted',
        whitelist=records,
        total_calls=total,
        page=page,
        per_page=per_page,
        pagination=pagination,
    )


@app.route('/callers/permitted/add', methods=['POST'])
def callers_permitted_add():
    """
    Add a new whitelist entry
    """
    caller = {}
    # TODO: Strip all none digits from phone via regex
    number = request.form['phone'].replace('-', '')
    caller['NMBR'] = number
    caller['NAME'] = request.form['name']
    print("Adding " + number + " to whitelist")
    whitelist = Whitelist(get_db(), current_app.config)
    success = whitelist.add_caller(caller, request.form['reason'])
    if success:
        return redirect("/callers/permitted", code=303)
    else:
        # Probably already exists... attempt to update with POST form data
        return redirect('/callers/permitted/update/{}'.format(number), code=307)


@app.route('/callers/permitted/update/<string:phone_no>', methods=['POST'])
def callers_permitted_update(phone_no):
    """
    Update the whitelist entry associated with the phone number.
    """
    number = phone_no.replace('-', '')
    print("Updating " + number + " in whitelist")
    whitelist = Whitelist(get_db(), current_app.config)
    whitelist.update_number(number, request.form['name'], request.form['reason'])

    return redirect("/callers/permitted", code=303)


@app.route('/callers/permitted/delete/<string:phone_no>', methods=['GET'])
def callers_permitted_delete(phone_no):
    """
    Delete the whitelist entry associated with the phone number.
    """
    number = phone_no.replace('-', '')

    print("Removing " + number + " from whitelist")
    whitelist = Whitelist(get_db(), current_app.config)
    whitelist.remove_number(number)

    return redirect("/callers/permitted", code=301)  # (re)moved permamently


@app.route('/messages')
def messages():
    """
    Display the voice messages for playback and/or deletion.
    """
    # Get values used for the pagination of the messages page
    total = get_row_count('Message')
    page, per_page, offset = get_page_args(
        page_parameter="page", per_page_parameter="per_page"
    )
    # Get the number of unread messages
    sql = "SELECT COUNT(*) FROM Message WHERE Played = 0"
    g.cur.execute(sql)
    unplayed_count = g.cur.fetchone()[0]

    # Get the messages subset, limited to the pagination settings
    sql = """SELECT
        a.MessageID,
        b.CallLogID,
        b.Name,
        b.Number,
        a.Filename,
        a.Played,
        a.DateTime,
        CASE WHEN c.PhoneNo is null THEN 'N' ELSE 'Y' END Whitelisted,
        CASE WHEN d.PhoneNo is null THEN 'N' ELSE 'Y' END Blacklisted
    FROM Message AS a
    INNER JOIN CallLog AS b ON a.CallLogID = b.CallLogID
    LEFT JOIN Whitelist AS c ON b.Number = c.PhoneNo
    LEFT JOIN Blacklist AS d ON b.Number = d.PhoneNo
    ORDER BY a.DateTime DESC
    LIMIT {}, {}""".format(offset, per_page)
    g.cur.execute(sql)
    result_set = g.cur.fetchall()

    # Create an array of messages that we'll supply to the rendered page
    messages = []
    for row in result_set:
        # Flask pages use the static folder to get resources.
        # In the static folder we have created a soft-link to the
        # data/messsages folder containing the actual messages.
        # We'll use the static-based path for the wav-file urls
        # in the web apge
        basename = os.path.basename(row[4])
        filepath = os.path.join("../static/messages", basename)
        number = row[3]
        # Create a date object from the date time string
        date_time = datetime.strptime(row[6][:19], '%Y-%m-%d %H:%M:%S')

        messages.append(dict(
            msg_no=row[0],
            call_no=row[1],
            name=row[2],
            phone_no='{}-{}-{}'.format(number[0:3], number[3:6], number[6:]),
            wav_file=filepath,
            msg_played=row[5],
            date=date_time.strftime('%d-%b-%y'),
            time=date_time.strftime('%I:%M %p'),
            whitelisted=row[7],
            blacklisted=row[8]
        ))

    # Create a pagination object for the page
    pagination = get_pagination(
        page=page,
        per_page=per_page,
        total=total,
        record_name="messages",
        format_total=True,
        format_number=True,
    )
    # Render the results with pagination
    return render_template(
        "messages.html",
        active_nav_item='messages',
        messages=messages,
        total_messages=total,
        total_unplayed=unplayed_count,
        page=page,
        per_page=per_page,
        pagination=pagination,
    )


@app.route('/messages/delete/<int:msg_no>', methods=['GET'])
def messages_delete(msg_no):
    """
    Delete the voice message associated with call number.
    """
    print("Removing message")
    message = Message(get_db(), current_app.config.get("MASTER_CONFIG"))
    success = message.delete(msg_no)
    # Redisplay the messages page
    if success:
        return redirect(request.referrer, code=301)  # (re)moved permamently
    else:
        flash('Delete message failed. Check the log.')
        return redirect(request.referrer, code=303)  # Other


@app.route('/messages/played', methods=['POST'])
def messages_played():
    """
    Update the played status for the message.
    Called by JQuery in messages view.
    """
    msg_no = request.form["msg_no"]
    played = request.form["status"]
    message = Message(get_db(), current_app.config.get("MASTER_CONFIG"))
    success = message.update_played(msg_no, played)

    # Get the number of unread messages
    sql = "SELECT COUNT(*) FROM Message WHERE Played = 0"
    g.cur.execute(sql)
    unplayed_count = g.cur.fetchone()[0]

    # Return the results as JSON
    return jsonify(success=success, msg_no=msg_no, unplayed_count=unplayed_count)


@app.route('/settings', methods=['GET'])
def settings():
    """
    Display the current settings.

    CSS: pygmentize -S colorful -f html > pygments.css
    """
    # Get the application-wide config object
    config = current_app.config.get("MASTER_CONFIG")

    # Read the current config into a str for display
    config_contents = pformat(config)

    # Read the config file contents into a buffer for display
    file_contents = ""
    file_path = ""
    file_name = config.get("CONFIG_FILE")
    if file_name:
        file_path = os.path.join(config.data_path, file_name)
        with open(file_path, mode="r") as f:
            file_contents += f.read()

    # Convert the strings to pretty HTML
    curr_settings = highlight(config_contents, PythonLexer(), HtmlFormatter())
    file_settings = highlight(file_contents, PythonLexer(), HtmlFormatter())

    return render_template(
        "settings.html",
        active_nav_item='settings',
        config_file=file_path,
        curr_settings=curr_settings,
        file_settings=file_settings)


def format_phone_no(number):
    return'{}-{}-{}'.format(number[0:3], number[3:6], number[6:])


def get_db():
    '''Get a connection to the database'''
    # Flask template for database connections
    if 'db' not in g:
        master_config = current_app.config.get("MASTER_CONFIG")
        g.db = sqlite3.connect(
            master_config.get("DB_FILE"),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    '''Clost the connection to the database'''
    # Flask template for database connections
    db = g.pop('db', None)

    if db is not None:
        db.close()


def get_row_count(table_name):
    '''Returns the row count for the given table'''
    # Using the current request's db connection
    sql = 'select count(*) from {}'.format(table_name)
    g.cur.execute(sql)
    total = g.cur.fetchone()[0]
    return total


def get_random_string(length=10):
    # Random string with the combination of lower and upper case
    chars = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(chars) for i in range(length))
    # print("Random string is:", result_str)
    return result_str


def get_css_framework():
    return current_app.config.get("CSS_FRAMEWORK", "bootstrap4")


def get_link_size():
    return current_app.config.get("LINK_SIZE", "sm")


def get_alignment():
    return current_app.config.get("LINK_ALIGNMENT", "")


def show_single_page_or_not():
    return current_app.config.get("SHOW_SINGLE_PAGE", False)


def get_pagination(**kwargs):
    kwargs.setdefault("record_name", "records")
    return Pagination(
        css_framework=get_css_framework(),
        link_size=get_link_size(),
        alignment=get_alignment(),
        show_single_page=show_single_page_or_not(),
        **kwargs
    )


def run_flask(config):
    '''
    Runs the Flask webapp.
        :param database: full path to the callattendant database file
    '''
    app.secret_key = get_random_string()
    with app.app_context():
        # Application-wide config dict
        app.config["MASTER_CONFIG"] = config
        # Override Flask settings with CallAttendant config settings
        app.config["DEBUG"] = config["DEBUG"]
        app.config["TESTING"] = config["TESTING"]

    # Turn off the HTML GET/POST logging
    if not app.config["DEBUG"]:
        log = logging.getLogger('werkzeug')
        log.disabled = True

    print("Running Flask webapp")
    # debug mode prevents app from running in separate thread
    app.run(host='0.0.0.0', debug=False)


def start(config):
    '''
    Starts the Flask webapp in a separate thread.
        :param database: full path to the callattendant database file
    '''
    _thread.start_new_thread(run_flask, (config,))
