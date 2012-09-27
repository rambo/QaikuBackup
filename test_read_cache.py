#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import fetcherparser,json
import sys,os

print storage.read_object_cache()
print json.dumps(storage.objectcache, sort_keys=True, indent=4)
print "%d messages in cache" % len(storage.objectcache)

