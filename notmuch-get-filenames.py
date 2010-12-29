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

import sys
import notmuch
import string

query=string.join(sys.argv[1:], sep=' ') # get all arguments, except
# the program name, and concatenate them into a string separated by
# space, that is, return the entire argument list as it was entered.

q = notmuch.Database().create_query(query)
for m in q.search_messages():
    print m.get_filename()
