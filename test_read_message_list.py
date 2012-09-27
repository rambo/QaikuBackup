#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import fetcherparser,json
import sys,os

listid = sys.argv[1]

messages = storage.read_message_list(listid)
print json.dumps(messages, sort_keys=True, indent=4)
print "%d messages in list" % len(messages)

