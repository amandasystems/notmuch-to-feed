#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
#
# Written by Albin Stjerna and placed in the Public Domain. Use any
# way you like, don't complain if it breaks. Or do, and suggest
# improvements.
#
# Will (at present state) produce an RSS feed with the last weeks's
# mail tagged with "rek" in notmuch.

import os
import datetime
import PyRSS2Gen
import sys
import time
import ConfigParser
import notmuch
from email.parser import Parser
from email.mime.text import MIMEText

def find_url(s):
    "find a feed2imap-style formatted URL (<URL>) in an arbitrary string"
    t = s[s.find("http://"):]
    t = t[:t.find("\"")]
    return t


def find_url_in_mail(mail):
    "try finding an URL in a sluk header, fall back to using regular expressions"
    url = mail.get("X-Entry-URL")
    return url

config = ConfigParser.ConfigParser()
conf_file = os.path.expanduser('~/.notmuch-to-feedrc')
if os.path.exists(conf_file):
    config.readfp(open(conf_file))

db = notmuch.Database()
nm_query = notmuch.Query(db, 'tag:' + config.get("entries", "tag"))
nm_query.set_sort(notmuch.Query.SORT.NEWEST_FIRST)
mails = nm_query.search_messages()

maillist = []

max_entries = config.getint("entries", "number")

iterator = 0
for m in mails:
    if iterator < max_entries:
        maillist.append(m)
        iterator +=1
    else:
        break


def get_html_multipart(mail):
    "Return the text/html part of a multipart mail, or simply the first part if not multipart"
    if not mail.is_multipart():
        return mail.get_payload()
    else:
        payload = mail.get_payload()
        for load in payload:
            if load.get_content_type() == "text/html":
                return load.get_payload()
            elif load.is_multipart():
                return get_html_multipart(load)
        # if we got here we're screwed


def gen_item (mail):
    fp = open(mail.get_filename(), 'r')
    mailfile = Parser().parse(fp)
    url = find_url_in_mail(mailfile)
    
    if url == None:
        url = find_url(get_html_multipart(mailfile))

    content = get_html_multipart(mailfile)

    fp.close()


    return PyRSS2Gen.RSSItem(
        title = mail.get_header("Subject"),
        link = url,
        description = content,
        guid = PyRSS2Gen.Guid(url),
        pubDate = datetime.datetime.utcfromtimestamp(mail.get_date()))

rss = PyRSS2Gen.RSS2(
    title         = config.get("feed", "title"),
    link          = config.get("feed", "link"),
    description   = config.get("feed", "description"),
    lastBuildDate = datetime.datetime.utcnow(),
    items = map(gen_item, maillist))

rss.write_xml(sys.stdout, encoding = "utf-8")
