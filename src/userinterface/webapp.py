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
from flask import Flask, request, g, current_app, render_template, redirect, \
    jsonify, url_for
from flask_paginate import Pagination, get_page_args
from screening.blacklist import Blacklist
from screening.whitelist import Whitelist
from messaging.voicemail import VoiceMail
from datetime import datetime
from glob import glob
import os
import screening.utils
import sqlite3
import _thread

# Create the Flask micro web-framework application
app = Flask(__name__)
app.config.from_pyfile('webapp.cfg')
app.debug = False  # debug mode prevents app from running in separate thread


@app.before_request
def before_request():
    """
    Establish a database connection for the current request
    """
    g.conn = sqlite3.connect(current_app.config.get("DB_PATH"))
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
    num_days = 30
    sql = """SELECT COUNT(DATE(SystemDateTime)) Count, DATE(SystemDateTime) CallDate
        FROM CallLog
        WHERE SystemDateTime > DATETIME('now','-{} day') AND Action = 'Blocked'
        GROUP BY CallDate
        ORDER BY CallDate""".format(num_days)
    g.cur.execute(sql)
    result_set = g.cur.fetchall()
    blocked_per_day = []
    for row in result_set:
        blocked_per_day.append(dict(
            count=row[0],
            call_date=row[1]))

    # Render the resullts
    return render_template(
        'dashboard.htm',
        recent_calls=recent_calls,
        top_permitted=top_permitted,
        top_blocked=top_blocked,
        blocked_per_day=blocked_per_day,
        new_messages=new_messages,
        total_calls='{:,}'.format(total_calls),
        blocked_calls='{:,}'.format(total_blocked),
        percent_blocked='{0:.0f}%'.format(percent_blocked),
    )


@app.route('/calls')
def call_log():
    """
    Display the call details from the call log table
    """

    # Get values used for pagination of the call log
    total = get_row_count('CallLog')
    page, per_page, offset = get_page_args(
        page_parameter="page", per_page_parameter="per_page"
    )
    # Get the call log subset, limited to the pagination settings
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
    LIMIT {}, {}""".format(offset, per_page)
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
        # in the web app
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
        format_number=True,
    )
    # Gather some metrics
    sql = "select count(*) from CallLog where `Action` = 'Blocked'"""
    g.cur.execute(sql)
    blocked = g.cur.fetchone()[0]
    if total == 0:
        percent_blocked = 0
    else:
        percent_blocked = blocked / total * 100
    # Render the resullts with pagination
    return render_template(
        'call_log.htm',
        calls=calls,
        total_calls='{:,}'.format(total),
        blocked_calls='{:,}'.format(blocked),
        percent_blocked='{0:.0f}%'.format(percent_blocked),
        page=page,
        per_page=per_page,
        pagination=pagination,
    )


@app.route('/blocked')
def blacklist():
    """
    Display the blocked numbers from the blacklist table
    """
    # Get values used for pagination of the blacklist
    total = get_row_count('Blacklist')
    page, per_page, offset = get_page_args(
        page_parameter="page", per_page_parameter="per_page"
    )
    # Get the blacklist subset, limited to the pagination settings
    sql = 'SELECT * from Blacklist ORDER BY datetime(SystemDateTime) DESC limit {}, {}'.format(offset, per_page)
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
        'blacklist.htm',
        blacklist=records,
        page=page,
        per_page=per_page,
        pagination=pagination,
    )


@app.route('/blocked/add', methods=['POST'])
def add_blocked():
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
        return redirect("/blocked", code=303)
    else:
        # Probably already exists... attempt to update with original form data
        return redirect('/blocked/update/{}'.format(number), code=307)

@app.route('/blocked/update/<string:phone_no>', methods=['POST'])
def update_blocked(phone_no):
    """
    Update the blacklist entry associated with the phone number.
    """
    number = phone_no.replace('-', '')
    print("Updating " + number + " in blacklist")
    blacklist = Blacklist(get_db(), current_app.config)
    blacklist.update_number(number, request.form['name'], request.form['reason'])

    return redirect("/blocked", code=303)


@app.route('/blocked/delete/<string:phone_no>', methods=['GET'])
def delete_blocked(phone_no):
    """
    Delete the blacklist entry associated with the phone number.
    """
    number = phone_no.replace('-', '')

    print("Removing " + number + " from blacklist")
    blacklist = Blacklist(get_db(), current_app.config)
    blacklist.remove_number(number)

    return redirect("/blocked", code=301)  # (re)moved permamently


@app.route('/permitted')
def whitelist():
    """
    Display the permitted numbers from the whitelist table
    """
    # Get values used for pagination of the blacklist
    total = get_row_count('Whitelist')
    page, per_page, offset = get_page_args(
        page_parameter="page", per_page_parameter="per_page"
    )
    # Get the whitelist subset, limited to the pagination settings
    sql = 'select * from Whitelist ORDER BY datetime(SystemDateTime) DESC limit {}, {}'.format(offset, per_page)
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
        'whitelist.htm',
        whitelist=records,
        total_calls=total,
        page=page,
        per_page=per_page,
        pagination=pagination,
    )


@app.route('/permitted/add', methods=['POST'])
def add_permitted():
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
        return redirect("/permitted", code=303)
    else:
        # Probably already exists... attempt to update with POST form data
        return redirect('/permitted/update/{}'.format(number), code=307)


@app.route('/permitted/update/<string:phone_no>', methods=['POST'])
def update_permitted(phone_no):
    """
    Update the whitelist entry associated with the phone number.
    """
    number = phone_no.replace('-', '')
    print("Updating " + number + " in whitelist")
    whitelist = Whitelist(get_db(), current_app.config)
    whitelist.update_number(number, request.form['name'], request.form['reason'])

    return redirect("/permitted", code=303)


@app.route('/permitted/delete/<string:phone_no>', methods=['GET'])
def delete_permitted(phone_no):
    """
    Delete the whitelist entry associated with the phone number.
    """
    number = phone_no.replace('-', '')

    print("Removing " + number + " from whitelist")
    whitelist = Whitelist(get_db(), current_app.config)
    whitelist.remove_number(number)

    return redirect("/permitted", code=301)  # (re)moved permamently


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
    sql = "select count(*) from message where Played = 0"
    g.cur.execute(sql)
    unplayed_count = g.cur.fetchone()[0]

    # Get the messages subset, limited to the pagination settings
    sql = """SELECT
        b.MessageID,
        a.CallLogID,
        a.Name,
        a.Number,
        b.Filename,
        b.Played,
        b.DateTime
    FROM CallLog as a
    INNER JOIN Message AS b ON a.CallLogID = b.CallLogID
    ORDER BY b.DateTime DESC
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
            time=date_time.strftime('%I:%M %p')
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
        "messages.htm",
        messages=messages,
        total_messages=total,
        total_unplayed=unplayed_count,
        page=page,
        per_page=per_page,
        pagination=pagination,
    )

@app.route('/messages/delete/<int:msg_no>', methods=['GET'])
def message_delete(msg_no):
    """
    Delete the voice message associated with call number.
    """
    print("Removing message")
    voicemail = VoiceMail(get_db(), current_app.config, None)
    success = voicemail.delete_message(msg_no)
    # Redisplay the messages page
    if success:
        return redirect("/messages", code=301)  # (re)moved permamently
    else:
        return redirect("/messages", code=303)  # Other


@app.route('/messages/played', methods=['POST'])
def message_played():
    """
    Update the played status for the message.
    Called by JQuery in messages view.
    """
    msg_no = request.form["msg_no"]
    played = request.form["status"]
    voicemail = VoiceMail(get_db(), current_app.config, None)
    success = voicemail.update_played(msg_no, played)

    # Get the number of unread messages
    sql = "select count(*) from message where Played = 0"
    g.cur.execute(sql)
    unplayed_count = g.cur.fetchone()[0]

    # Return the results as JSON
    return jsonify(success=success, msg_no=msg_no, unplayed_count=unplayed_count)


@app.route('/manage_caller/<int:call_log_id>', methods=['GET', 'POST'])
def manage_caller(call_log_id):
    """
    Display the Manage Caller form
    """
    # Post changes to the blacklist or whitelist table before rendering
    if request.method == 'POST':
        number = request.form['phone_no'].replace('-', '')
        if request.form['action'] == 'Permit':
            caller = {}
            caller['NMBR'] = number
            caller['NAME'] = request.form['name']
            print("Adding " + caller['NAME'] + " to whitelist")
            whitelist = Whitelist(get_db(), current_app.config)
            whitelist.add_caller(caller, request.form['reason'])

        elif request.form['action'] == 'RemovePermit':
            print("Removing " + number + " from whitelist")
            whitelist = Whitelist(get_db(), current_app.config)
            whitelist.remove_number(number)

        elif request.form['action'] == 'Block':
            caller = {}
            caller['NMBR'] = number
            caller['NAME'] = request.form['name']
            print("Adding " + caller['NAME'] + " to blacklist")
            blacklist = Blacklist(get_db(), current_app.config)
            blacklist.add_caller(caller, request.form['reason'])

        elif request.form['action'] == 'RemoveBlock':
            print("Removing " + number + " from blacklist")
            blacklist = Blacklist(get_db(), current_app.config)
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
    '''Get a connection to the database'''
    # Flask template for database connections
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config.get("DATABASE"),
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

def format_phone_no(number):
    return'{}-{}-{}'.format(number[0:3], number[3:6], number[6:])


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
    with app.app_context():
        # Override Flask settings with CallAttendant config settings
        app.config["DEBUG"] = config["DEBUG"]
        app.config["TESTING"] = config["TESTING"]
        # Add addtional settings from callattendant config
        app.config["ROOT_PATH"] = config["ROOT_PATH"]
        app.config["DATABASE"] = config["DATABASE"]
        app.config["VOICE_MAIL_MESSAGE_FOLDER"] = config["VOICE_MAIL_MESSAGE_FOLDER"]
        # Add a new derived setting
        app.config["DB_PATH"] = os.path.join(config["ROOT_PATH"], config["DATABASE"])

    print("Running Flask webapp")
    # debug mode prevents app from running in separate thread
    app.run(host='0.0.0.0', debug=False)


def start(config):
    '''
    Starts the Flask webapp in a separate thread.
        :param database: full path to the callattendant database file
    '''
    _thread.start_new_thread(run_flask, (config,))
