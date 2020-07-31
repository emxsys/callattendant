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
from flask import Flask, request, g, current_app, render_template
from flask_paginate import Pagination, get_page_args
from screening.blacklist import Blacklist
from screening.whitelist import Whitelist
import screening.utils
import sqlite3
import thread

# Create the Flask micro web-framework application
app = Flask(__name__)
app.config.from_pyfile('webapp.cfg')
app.debug = False  # debug mode prevents app from running in separate thread


@app.before_request
def before_request():
    '''Establish a database connection for the current request'''
    g.conn = sqlite3.connect(current_app.config.get('DATABASE', 'callattendant.db'))
    g.conn.row_factory = sqlite3.Row
    g.cur = g.conn.cursor()


@app.teardown_request
def teardown(error):
    '''Closes the database connection for the last request'''
    if hasattr(g, 'conn'):
        g.conn.close()


@app.route('/')
def call_details():
    '''Display the call details from the call log table'''

    # Get values used for pagination of the call log
    total = get_row_count('CallLog')
    page, per_page, offset = get_page_args(
        page_parameter="page", per_page_parameter="per_page"
    )
    # Get the call log subset, limited to the pagination settings
    sql = '''select a.CallLogID, a.Name, a.Number, a.Date, a.Time,
      case when b.PhoneNo is null then 'N' else 'Y' end Whitelisted,
      case when c.PhoneNo is null then 'N' else 'Y' end Blacklisted,
      case when b.PhoneNo is not null then b.Reason else c.Reason end Reason
    from CallLog as a
    left join Whitelist as b ON a.Number = b.PhoneNo
    left join Blacklist as c ON a.Number = c.PhoneNo
    order by a.SystemDateTime desc limit {}, {}'''.format(offset, per_page)
    g.cur.execute(sql)
    result_set = g.cur.fetchall()

    # Create a formatted list of records including some derived values
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
    sql = '''select count(*)
        from CallLog as a
        left join Whitelist as b ON a.Number = b.PhoneNo
        left join Blacklist as c ON a.Number = c.PhoneNo
        where b.PhoneNo is null and c.PhoneNo is not null'''
    g.cur.execute(sql)
    blocked = g.cur.fetchone()[0]
    percent_blocked = blocked / total * 100
    # Render the resullts with pagination
    return render_template(
        'call_details.htm',
        calls=records,
        total_calls='{:,}'.format(total),
        blocked_calls='{:,}'.format(blocked),
        percent_blocked='{0:.0f}%'.format(percent_blocked),
        page=page,
        per_page=per_page,
        pagination=pagination,
    )


@app.route('/blocked')
def blacklist():
    '''Display the blocked numbers from the blacklist table'''
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
            System_Date_Time=record[3]))

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



@app.route('/permitted')
def whitelist():
    '''Display the permitted numbers from the whitelist table'''
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
            System_Date_Time=record[3]))
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
            print "Adding " + caller['NAME'] + " to whitelist"
            whitelist = Whitelist(get_db())
            whitelist.add_caller(caller, request.form['reason'])

        elif request.form['action'] == 'RemovePermit':
            print "Removing " + number + " from whitelist"
            whitelist = Whitelist(get_db())
            whitelist.remove_number(number)

        elif request.form['action'] == 'Block':
            caller = {}
            caller['NMBR'] = number
            caller['NAME'] = request.form['name']
            print "Adding " + caller['NAME'] + " to blacklist"
            blacklist = Blacklist(get_db())
            blacklist.add_caller(caller, request.form['reason'])

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
    '''Get a connection to the database'''
    # Flask template for database connections
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config.get('DATABASE', 'callattendant.db'),
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


def runFlask():
    #with app.app_context():
    #    call_details()

    print "calling app.run()"
    # debug mode prevents app from running in separate thread
    app.run(host='0.0.0.0', debug=False)


def start():
    '''Start the Flask webapp in a separate thread'''
    thread.start_new_thread(runFlask, ())
