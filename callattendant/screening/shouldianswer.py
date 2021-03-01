#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  ShouldIAnswer.py
#
#  Copyright 2021 Thomas BARDET <thomas.bardet@cloud-forge.net>
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


import urllib.request
from bs4 import BeautifulSoup


class ShouldIAnswer(object):

    def lookup_number(self, number):
        #number = '{}-{}-{}'.format(number[0:3], number[3:6], number[6:])
        url = "https://www.doisjerepondre.fr/numero-de-telephone/%s" % number
        # print(url)
        headers = {}
        allowed_codes = [404]  # allow not found response
        content = self.http_get(url, headers, allowed_codes)
        soup = BeautifulSoup(content, "lxml")  # lxml HTML parser: fast

        score = 0  # = no spam

        scoreContainer = soup.find(class_="scoreContainer")

        #print(positions)
        if len(scoreContainer) > 0:
            divScore = scoreContainer.select("div > .negative")
            #print(divScore)
            if(divScore):
                #print("Spammer!")
                score = 2

            reason = ""
            numbers = soup.find(class_="number")
            #print(numbers)
            if len(numbers) > 0:
                spanReason = numbers.select("div > span")
                reason = spanReason[0].get_text()
                reason = reason.replace("\n", "").strip(" ")
                #print(reason)
            #review = soup.find(class_="review reviewNew")
            #print(review)
            #if len(review) > 0:
                #bouton = review.select("div > #nf1ButYes ")
                #print(bouton)

        spam = False if score < self.spam_threshold else True

        result = {
            "spam": spam,
            "score": score,
            "reason": reason
        }
        print(result)
        return result

    def http_get(self, url, add_headers={}, allowed_codes=[]):
        data = ""
        try:
            request = urllib.request.Request(url, headers=add_headers)
            response = urllib.request.urlopen(request, timeout=5)
            data = response.read()
        except urllib.error.HTTPError as e:
            code = e.getcode()
            if code not in allowed_codes:
                raise
            data = e.read()
        return data

    def __init__(self, spam_threshold=2):

        self.spam_threshold = spam_threshold


