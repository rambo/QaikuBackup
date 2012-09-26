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
replycache = {}
recursion_loop_detector = {}

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
    """Returns a message, from local cache if available, otherwise loads via REST API"""
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

def clear_recursion_loop_detector():
    for k in recursion_loop_detector.keys():
        del(recursion_loop_detector[k])

def recursive_fetch_message(object_id, recursion_level = 0):
    """Fetches a message and all it's dependendies/replies/etc"""
    if debug:
        print "recursive_fetch_message(%s, %d)" % (object_id, recursion_level)
        print "recursion_loop_detector=%s" % repr(recursion_loop_detector)
    if recursion_loop_detector.has_key(object_id):
        return False
    obj = fetch_message(object_id)
    if not obj:
        return False
    # Keep track of recursion so we do not get trapped in an infinite loop
    recursion_loop_detector[object_id] = True
    # Retvieve parent message is any (and other link properties ?)
    for k in ['in_reply_to_status_id',]:
        if (    obj.has_key(k)
            and obj[k]):
            if debug:
                print "Recursing %s->%s(=%s)" % (obj['id'], k, obj[k])
            recursive_fetch_message(obj[k], recursion_level+1)
    # Get replies
    if debug:
        print "Checking replies for %s" % (obj['id'])
    replies = fetch_replies(obj['id'], recursion_level+1)
    # Clear the recursion tracker
    if recursion_level == 0:
        clear_recursion_loop_detector()
    return True

def fetch_paged(urlbase):
    """This will loop through page numbers until no more results are returned"""
    resultlist = []
    page = 0
    loop = True
    while (loop):
        url = "%s?apikey=%s&page=%d" % (urlbase, apikey, page)
        parsed = json_parse_url(url)
        if (   not parsed
            or len(parsed) == 0):
            loop = False
        resultlist = resultlist+parsed
        page = page+1
        #temp page limit
        if page > 5:
            loop = False
    return resultlist

def fetch_replies(object_id, recursion_level = 0):
    """Get full list of replies to a message (and insert them to cache, recursing)"""
    if replycache.has_key(object_id):
        return replycache[object_id]
    replies = fetch_paged("http://www.qaiku.com/api/statuses/replies/%s.json" % object_id)
    if not replies:
        replies = []
    replycache[object_id] = replies
    # Cache all the messages while at it
    mass_insert_and_recurse(replies, recursion_level)
    # And put a list of the replies to the object we fetched them for
    if objectcache.has_key(object_id): # this should not fail, not at this point anymore
        objectcache[object_id]['QaikuBackup_replies'] = [ o['id'] for o in replies ] # Map a list of the reply IDs to the object (using python pointers we could just point to the list of objects but that would cause no end of headache for the JSON serialization we plane to do)
    return replycache[object_id]

def insert_and_recurse(qaiku_message, recursion_level = 0):
    """Insert a message to cache and get all it's resources/replies/etc"""
    if not objectcache.has_key(qaiku_message['id']):
        objectcache[qaiku_message['id']] = qaiku_message
    return recursive_fetch_message(qaiku_message['id'], recursion_level)

def mass_insert_and_recurse(list_of_messages, recursion_level = 0):
    for qaiku_message in list_of_messages:
        if not objectcache.has_key(qaiku_message['id']):
            objectcache[qaiku_message['id']] = qaiku_message
    # And then handle the recursions
    for qaiku_message in list_of_messages:
        recursive_fetch_message(qaiku_message['id'], recursion_level)

if __name__ == '__main__':
    import sys,os
    recursive_fetch_message(sys.argv[1])
    print json.dumps(objectcache, sort_keys=True, indent=4)
