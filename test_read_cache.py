#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import fetcherparser,json
import sys,os

print fetcherparser.read_object_cache()
print json.dumps(fetcherparser.objectcache, sort_keys=True, indent=4)
print "%d messages in cache" % len(fetcherparser.objectcache)

