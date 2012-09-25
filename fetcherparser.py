#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""This module will handle fetching the JSON and parsing it to do recursive fetches
of messages and their resources (images etc)"""
import json, urllib2
debug = True


def read_api_key():
    fp = open('qaiku_api_key.txt')
    return fp.readline().strip()

apikey = read_api_key()
objectcache = {}


def json_parse_url(url):
    if debug:
        print "Fetching %s" % url
    try:
        fp = urllib2.urlopen(url)
        parsed = json.load(fp)
    except Exception,e:
        print "Got exception %s" % e
        return None
    return parsed
    

def fetch_message(object_id):
    if objectcache.has_key(object_id):
        obj = objectcache[object_id]
        # only return object from cache if it is fully defined
        if (   (not obj.has_key('truncated'))
            or (    obj.has_key('truncated')
                and not obj['truncated'])
            ):
            return objectcache[object_id]
    url = "http://www.qaiku.com/api/statuses/show/%s.json?apikey=%s" % (object_id, apikey)
    parsed = json_parse_url(url)
    objectcache[parsed['id']] = parsed
    return objectcache[parsed['id']]

def recursive_fetch_message(object_id):
    obj = fetch_message(object_id)
    if not obj:
        return False
    # Retvieve parent message is any (and other link properties ?)
    for k in ['in_reply_to_status_id',]:
        if (    obj.has_key(k)
            and obj[k]):
            if debug:
                print "Recursing %s->%s(=%s)" % (obj['id'], k, obj[k])
            recursive_fetch_message(obj[k])
# Causes infinite loop, figure out later
#    # Get replies
#    if debug:
#        print "Checking replies for %s" % (obj['id'])
#    replies = fetch_replies(obj['id'])
    return True

def fetch_paged(urlbase):
    """This will loop through page numbers until no more results are returned"""
    resultlist = []
    page = 0
    while (True):
        url = "%s?apikey=%s&page=%d" % (urlbase, apikey, page)
        parsed = json_parse_url(url)
        if (   not parsed
            or len(parsed) == 0):
            break
        resultlist = resultlist+parsed
    return resultlist

def fetch_replies(object_id):
    """Get full list of replies to a message"""
    replies = fetch_paged("http://www.qaiku.com/api/statuses/replies/%s.json" % object_id)
    # Cache all the messages while at it
    for qaiku_message in replies:
        insert_and_recurse(qaiku_message)
    return replies

def insert_and_recurse(qaiku_message):
    if not objectcache.has_key(qaiku_message['id']):
        objectcache[qaiku_message['id']] = qaiku_message
    return recursive_fetch_message(qaiku_message['id'])


if __name__ == '__main__':
    import sys,os
    recursive_fetch_message(sys.argv[1])
    print json.dumps(objectcache, sort_keys=True, indent=4)
