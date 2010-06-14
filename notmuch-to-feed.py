#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
#
# Written by Albin Stjerna. Not licenced at all. Use any way you like,
# don't complain if it breaks. Or do, and suggest improvements.
#
# Will (at present state) produce an RSS feed with the last weeks's
# mail tagged with "rek" in notmuch.

import commands as cm
import json
import datetime
import PyRSS2Gen
import sys
import time

def strip_mail_crap(mail):
    "skip some uninteresting data"
    return mail[0][0]

def body(mail):
    "return the body of the mail"
    return strip_mail_crap(mail)['body']

def content_clean(mail):
    "Trim and strip away feed2imap footer and notmuch URL index. Hopefully, don't touch other emails."
    def find_start(str):
        inurl=False
        foundurl=False
        start = 0
        for a in s:
            if a == '<' and not inurl and not foundurl:
                inurl=True
                start += 1
            elif a == '>':
                inurl=False
                foundurl=True
                start += 1
            elif a == '\n':
                if inurl: # URLs do not span multiple lines!
                    error("parse error")
                    break
                elif foundurl: 
                    return start + 1 # We've found our URL and now a \n -- we're home.
            else: 
                start += 1
        return start

    def find_end(str):
        hyphens_found=0 # we want to find two in a row and then a newline
        end=0
        for a in str:
            if a == '\n' and hyphens_found==2:
                return end # skip both hyphens and newlines
            if a == ' ' and hyphens_found==2: #jump trailing ' '
                end += 1
            elif a == '-':
                hyphens_found += 1
            else:
                hyphens_found = 0
                end += 1
        print end
        return end

    def strip_url_index(s):
        return s[:s.find("] \nhttp://")-2] #

    s = content(mail)
    begin = find_start(mail)
    end = find_end(s)
    if end == 0:
        end = len(s)
    
    return strip_url_index(s[begin:end]).lstrip().rstrip()

def content(mail):
    "return raw, unformatted mail content"
    return body(mail)[0]['content']

def timestamp(mail):
    "return the UNIX timestamp of mail"
    return strip_mail_crap(mail)['timestamp']

def title(mail):
    "get the mail subject/title"
    return strip_mail_crap(mail)['headers']['Subject']

def find_url(s):
    "find a feed2imap-style formatted URL (<URL>) in an arbitrary string"
    t = s[s.find("http://"):]
    t = t[:t.find(">")]
    return t

end_time=time.time() # now
start_time=time.time() - (7 * 24 * 60 * 60) # 1 w earlier
# this will output all mails matching tag "rek" recieved the last week:
notmuch_out = cm.getstatusoutput('notmuch show --format=json tag:rek and ' + str(start_time) + '..' + str(end_time)) 
status=notmuch_out[0] # exit status
message=notmuch_out[1] # actual JSON output

if(status != 0):
    exit("error from notmuch, exit status" + str(status) + "message: " + message)

mails = json.loads(message)

def gen_item (mail):
    return PyRSS2Gen.RSSItem(
        title = title(mail),
        link = find_url(content(mail)),
        description = content_clean(mail),
        guid = PyRSS2Gen.Guid(find_url(content(mail))),
        pubDate = datetime.datetime.fromtimestamp(timestamp(mail)))

rss = PyRSS2Gen.RSS2(
    title = "Albins rekommenderatflöde",
    link = "http://eval.nu/rekommenderat.rss",
    description = "Ett flöde med rekommenderad läsning",
    lastBuildDate = datetime.datetime.now(),
    items = map(gen_item, mails))

rss.write_xml(sys.stdout)
