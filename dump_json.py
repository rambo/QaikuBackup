#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""This tool will fetch a given url and pretty-print the JSON"""
import json, urllib2

def dumper(url):
    fp = urllib2.urlopen(url)
    parsed = json.load(fp)
    print json.dumps(parsed, sort_keys=True, indent=4)

if __name__ == '__main__':
    import sys,os
    dumper(sys.argv[1])
