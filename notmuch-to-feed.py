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
import notmuch
from email.parser import Parser
from email.mime.text import MIMEText


# def strip_mail_crap(mail):
#     "skip some uninteresting data"
#     return mail[0][0]

# def body(mail):
#     "return the body of the mail"
#     return strip_mail_crap(mail)['body']

# def content(mail):
#     "return raw, unformatted mail content"
# #    print mail
# #    return
#     return notmuch_get_mime_part("1", notmuch_id(mail))
#     #return body(mail)[0]['content']

# def timestamp(mail):
#     "return the UNIX timestamp of mail"
#     return strip_mail_crap(mail)['timestamp']

# def title(mail):
#     "get the mail subject/title"
#     return strip_mail_crap(mail)['headers']['Subject']

def find_url(s):
    "find a feed2imap-style formatted URL (<URL>) in an arbitrary string"
    t = s[s.find("http://"):]
    t = t[:t.find(">")]
    return t


def find_url_in_mail(mail):
    "try finding an URL in a sluk header, fall back to using regular expressions"
    url = mail.get("X-Entry-URL")
    return url

# def notmuch_id(mail):
#     """return the notmuch internal ID for a given mail"""
#     return strip_mail_crap(mail)['id']

# def html(mail):
#     """return the HTML multipart of a given mail (or the plain text
#     version if it fails)"""
#     # notmuch part --part=2 id:"Tusenpekpinnar-6477@nyx"
#     def find_html_part(mail):
#         for part in body(mail):
#             if part['content-type'] == "text/html":
#                 return part['id']
#         return 1 # we didn't find any text/html, using plain text.
#     return cm.getstatusoutput("notmuch part --part=" +
#                               str(find_html_part(mail)) + " id:" +
#                               notmuch_id(mail))[1]

# def strip_feed2imap_table(html):
#     return html #FIXME

# def notmuch_get_mime_part(mime_id, message_id):
#     return cm.getstatusoutput('notmuch part --part=' + mime_id + 'id:' + message_id)[1]


config = ConfigParser.ConfigParser()
conf_file = os.path.expanduser('~/.notmuch-to-feedrc')
if os.path.exists(conf_file):
    config.readfp(open(conf_file))

db = notmuch.Database()
mails = notmuch.Query(db, 'tag:' + config.get("entries", "tag")).search_messages()

maillist = []

for m in mails:
    maillist.append(m)

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
        # if not mailfile.is_multipart():
        #     url = find_url(mailfile.get_payload())
        # else:
        #     url = find_url(mailfile.get_payload()[1].get_payload())
        url = find_url(get_html_multipart(mailfile))

    content = get_html_multipart(mailfile)

    fp.close()


    return PyRSS2Gen.RSSItem(
        title = mail.get_header("Subject"),
        link = url,
        description = content,
        guid = PyRSS2Gen.Guid(url),
        pubDate = datetime.datetime.utcfromtimestamp(mail.get_date()))



#for mail in mails:
#    print gen_item(mail)


# get all with the tag, filter later. until notmuch has this feature built in..
# notmuch_out = cm.getstatusoutput('notmuch show --format=json tag:' + config.get("entries", "tag"))
# status=notmuch_out[0] # exit status
# message=notmuch_out[1] # actual JSON output

# if(status != 0):
#     exit("error from notmuch, exit status" + str(status) + "message: " + message)

# mails = json.loads(message)[:config.getint("entries", "number")]

rss = PyRSS2Gen.RSS2(
    title         = config.get("feed", "title"),
    link          = config.get("feed", "link"),
    description   = config.get("feed", "description"),
    lastBuildDate = datetime.datetime.utcnow(),
    items = map(gen_item, maillist))

rss.write_xml(sys.stdout, encoding = "utf-8")
