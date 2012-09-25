#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""This tool will fetch a given url and pretty-print the JSON"""
import json, urllib2

def dumper(url, python_repr=False):
    fp = urllib2.urlopen(url)
    parsed = json.load(fp)
    if python_repr:
        import pprint
        pprint.pprint(parsed, indent=4)
        return
    print json.dumps(parsed, sort_keys=True, indent=4)

if __name__ == '__main__':
    import sys,os
    if (   len(sys.argv) > 2
        and sys.argv[2]):
        dumper(sys.argv[1], True)
        sys.exit(0)
    dumper(sys.argv[1])
