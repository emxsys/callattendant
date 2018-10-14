#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  nomorobo.py
#
#  Copyright 2018 Bruce Schubert <bruce@emxsys.com>
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


import sys
import argparse
import urllib2
from BeautifulSoup import BeautifulSoup


class NomoroboService(object):

    def lookup_number(self, number):
        number = '{}-{}-{}'.format(number[0:3], number[3:6], number[6:])
        url = "https://www.nomorobo.com/lookup/%s" % number
        headers = {}
        allowed_codes = [404]  # allow not found response
        content = self.http_get(url, headers, allowed_codes)
        soup = BeautifulSoup(content)

        score = 0  # = no spam
        positions = soup.findAll(class_="profile-position")
        if len(positions) > 0:
            position = positions[0].get_text()
            if position.upper().find("DO NOT ANSWER") > -1:
                score = 2  # = is spam
            else:
                score = 1  # = might be spam (caller is "Political", "Charity", or "Debt Collector")

        caller_name = ""
        titles = soup.findAll(class_="profile-title")
        if len(titles) > 0:
            caller_name = titles[0].get_text()
            caller_name = caller_name.replace("\n", "").strip(" ")
            # TODO: if score == 1, check for "Political", "Charity", and/or "Debt Collector"
            # in the caller_name and adjust the score if appropriate

        spam = False if score < self.spam_threshold else True

        result = {
            "spam": spam,
            "score": score,
            "name": caller_name
        }
        return result

    def http_get(self, url, add_headers={}, allowed_codes=[]):
        try:
            request = urllib2.Request(url, headers=add_headers)
            response = urllib2.urlopen(request, timeout=5)
            data = response.read()
        except urllib2.HTTPError, e:
            code = e.getcode()
            if code not in allowed_codes:
                raise
            data = e.read()
        return data

    def __init__(self, spam_threshold=2):

        self.spam_threshold = spam_threshold
