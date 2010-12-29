#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
#
# Written by Albin Stjerna and placed in the Public Domain. Use any
# way you like, don't complain if it breaks. Or do, and suggest
# improvements.
#
# Will read the JSON output of notmuch on stdin and produce a list of
# absolute search paths to the matching mail files on stdout. Useful
# for cleaning up and archiving mail.
# usage: notmuch-get-filenames <query>

import json
import sys
import commands as cm
import string

def parse_filename(js_mail):
    "returns the filename string from a parsed json mail entry"
    return js_mail[0][0]['filename']


query=string.join(sys.argv[1:], sep=' ') # get all arguments, except
# the program name, and concatenate them into a string separated by
# space, that is, return the entire argument list as it was entered.

notmuch_out = cm.getstatusoutput('notmuch show --format=json %s' % query)
status=notmuch_out[0] # exit status
message=notmuch_out[1] # actual JSON output

if(status != 0):
    exit("error from notmuch, exit status" + str(status) + "message: " + message)
    
mails = json.loads(message)
for mail in mails:
    print parse_filename(mail)
