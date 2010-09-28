#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
#
# Written by Albin Stjerna and placed in the Public Domain. Use any
# way you like, don't complain if it breaks. Or do, and suggest
# improvements.
#
# Will (at present state) produce an RSS feed with the last weeks's
# mail tagged with "rek" in notmuch.

import commands as cm
import os
import json
import datetime
import PyRSS2Gen
import sys
import time
import ConfigParser

def strip_mail_crap(mail):
    "skip some uninteresting data"
    return mail[0][0]

def body(mail):
    "return the body of the mail"
    return strip_mail_crap(mail)['body']

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

def notmuch_id(mail):
    """return the notmuch internal ID for a given mail"""
    return strip_mail_crap(mail)['id']

def html(mail):
    """return the HTML multipart of a given mail (or the plain text
    version if it fails)"""
    # notmuch part --part=2 id:"Tusenpekpinnar-6477@nyx"
    def find_html_part(mail):
        for part in body(mail):
            if part['content-type'] == "text/html":
                return part['id']
        return 1 # we didn't find any text/html, using plain text.
    return cm.getstatusoutput("notmuch part --part=" +
                              str(find_html_part(mail)) + " id:" +
                              notmuch_id(mail))[1]

def strip_feed2imap_table(html):
    return html #FIXME

config = ConfigParser.ConfigParser()
conf_file = os.path.expanduser('~/.notmuch-to-feedrc')
if os.path.exists(conf_file):
    config.readfp(open(conf_file))

# get all with the tag, filter later. until notmuch has this feature built in..
notmuch_out = cm.getstatusoutput('notmuch show --format=json tag:' + config.get("entries", "tag"))
status=notmuch_out[0] # exit status
message=notmuch_out[1] # actual JSON output

if(status != 0):
    exit("error from notmuch, exit status" + str(status) + "message: " + message)

mails = json.loads(message)[:config.getint("entries", "number")]

def gen_item (mail):
    return PyRSS2Gen.RSSItem(
        title = title(mail),
        link = find_url(content(mail)),
        description = strip_feed2imap_table(html(mail)),
        guid = PyRSS2Gen.Guid(find_url(content(mail))),
        pubDate = datetime.datetime.utcfromtimestamp(timestamp(mail)))

rss = PyRSS2Gen.RSS2(
    title         = config.get("feed", "title"),
    link          = config.get("feed", "link"),
    description   = config.get("feed", "description"),
    lastBuildDate = datetime.datetime.utcnow(),
    items = map(gen_item, mails))

rss.write_xml(sys.stdout, encoding = "utf-8")
