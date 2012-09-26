#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""This module will handle fetching the JSON and parsing it to do recursive fetches
of messages and their resources (images etc)"""
import json, urllib2, hashlib, os, re
# some global config values
debug = True
fetch_profile_images = True

import screenscraper

def read_api_key():
    """Helper to read the API key, later will ask for it if the file is missing"""
    fp = open('qaiku_api_key.txt')
    return fp.readline().strip()

apikey = read_api_key()
objectcache = {}
replycache = {}
recursion_loop_detector = {}

def json_parse_url(url):
    """Trivial helper to avoid copy-pasting same code all over"""
    if debug:
        print "Fetching (JSON) %s" % url
    try:
        fp = urllib2.urlopen(url)
        parsed = json.load(fp)
        fp.close()
    except Exception,e:
        print "Got exception %s" % e
        return None
    return parsed

def update(obj):
    """Re-inserts the object to the cache dict, maybe this will help with weird cow/pointer issues"""
    object_id = str(obj['id'])
    objectcache[object_id] = obj
    if debug:
        print "After update objectcache[%s] is" % object_id
        print json.dumps(objectcache[object_id], sort_keys=True, indent=4)
        
def in_cache(obj):
    """Normalized way to check for object presence in cache"""
    object_id = str(obj['id'])
    return objectcache.has_key(object_id)
    

def write_message_list(identifier, messages):
    """Writes a list of messages ids to a file, basically used to dump the lists from channeldump and userdump modules"""
    local_path = os.path.join('resources', identifier + '.json')
    if not os.path.isdir(os.path.dirname(local_path)):
        os.makedirs(os.path.dirname(local_path))
    fp_to = open(local_path, 'wb')
    json.dump([ o['id'] for o in messages ], fp_to, sort_keys=False, indent=4)
    fp_to.close()
    return True

def read_message_list(identifier):
    """Read a list dumped with write_message_list, returns the full messages"""
    local_path = os.path.join('resources', identifier + '.json')
    fp = open(local_path, 'rb')
    parsed = json.load(fp)
    fp.close()
    for k in range(len(parsed)):
        message_id = parsed[k]
        if not recursive_fetch_message(message_id):
            # remove the message if it could not be expanded
            del(parsed[k])
            continue
        parsed[k] = fetch_message(message_id) # This will be returned from the cache properly expanded by the previous fetch
    return parsed

def write_object_cache():
    """Writes the current objectcache to disk, will simply overwrite the previous one so use with caution..."""
    local_path = os.path.join('resources', 'objectcache.json')
    if not os.path.isdir(os.path.dirname(local_path)):
        os.makedirs(os.path.dirname(local_path))
    fp_to = open(local_path, 'wb')
    json.dump(objectcache, fp_to, sort_keys=True, indent=4)
    fp_to.close()
    return True
    
def read_object_cache(mark_stale=True):
    """Reads the object cache from disk (and marks every object stale by default)"""
    local_path = os.path.join('resources', 'objectcache.json')
    if not os.path.isfile(local_path):
        return False
    fp = open(local_path)
    parsed = json.load(fp)
    fp.close()
    for msg_id in parsed:
        qaiku_message = parsed[msg_id]
        if not in_cache(qaiku_message):
            update(qaiku_message)
            if mark_stale:
                qaiku_message['QaikuBackup_stale'] = True
    return True

# compile this just once, it's used by fetch_resource()
getparams_re = re.compile('\?.*$')
local_resource_re = re.compile('^' + os.path.join('resources', '').replace('\\', '\\\\') + '[0-9a-f]{2}')
def fetch_resource(url):
    """Fetches and stores locally remote resources and returns the local filepath"""
    if local_resource_re.match(url):
        # This is already a local resource
        return url
    local_id = hashlib.md5(url).hexdigest()
    extension = ""
    # Try to figure out a file extension just to make things nicer to file browsers
    try:
        filename = getparams_re.sub('', os.path.basename(url))
        extension = filename.rsplit('.', 1)[1] # get the last extension.
    except Exception,e:
        print "Got exception %s when trying to figure out file extension for %s" % (e, url)
    local_path = os.path.join('resources', local_id[0:2], local_id + "." + extension)
    # If we already have the file just return it
    if os.path.isfile(local_path):
        return local_path
    # Create the container dir if it's not there
    if not os.path.isdir(os.path.dirname(local_path)):
        os.makedirs(os.path.dirname(local_path))
    if debug:
        print "Fetching (BIN) %s to %s" % (url, local_path)
    try:
        fp_from = urllib2.urlopen(url)
        fp_to = open(local_path, 'wb')
        # TODO: use a sensibly sized buffer ?
        fp_to.write(fp_from.read())
        fp_from.close()
        fp_to.close()
    except Exception,e:
        print "Got exception %s" % e
        return None
    return local_path


def fetch_message(object_id):
    """Returns a message, from local cache if available, otherwise loads via REST API, you probably should be calling recursive_fetch_message first"""
    object_id = str(object_id) # cast to normal str
    if objectcache.has_key(object_id):
        obj = objectcache[object_id]
        if (   (    obj.has_key('truncated')
                and obj['truncated'])
            or (    obj.has_key('QaikuBackup_stale')
                and obj['QaikuBackup_stale'])
            ):
            # Object is stale, do not return from cache
            pass
        else:
            if debug:
                print "message %s returned from cache" % object_id
            return objectcache[object_id]
    url = "http://www.qaiku.com/api/statuses/show/%s.json?apikey=%s" % (object_id, apikey)
    parsed = json_parse_url(url)
    if not parsed:
        # parse failed, return stale object if we have one
        if objectcache.has_key(object_id):
            return objectcache[object_id]
        else:
            return None
    update(parsed)
    return objectcache[object_id]

def clear_recursion_loop_detector():
    for k in recursion_loop_detector.keys():
        del(recursion_loop_detector[k])

# TODO: rethink this and fetch_message
def recursive_fetch_message(object_id, recursion_level = 0):
    """Fetches a message and all it's dependendies/replies/etc"""
    if debug:
        print "recursive_fetch_message(%s, %d)" % (object_id, recursion_level)
        #print "recursion_loop_detector=%s" % repr(recursion_loop_detector)
    if recursion_loop_detector.has_key(object_id):
        return False
    obj = fetch_message(object_id)
    if not obj:
        return False
    # Keep track of recursion so we do not get trapped in an infinite loop
    recursion_loop_detector[object_id] = True

    # Cache and rewrite profile image url
    if (    fetch_profile_images
        and obj.has_key('user')
        and obj['user'].has_key('profile_image_url')):
        res = fetch_resource(obj['user']['profile_image_url'])
        if res:
            obj['user']['profile_image_url'] = res
    
    # Fetch the message image if any, however this is the tiny thumbnail :..(
    if (    obj.has_key('image_url')
        and obj['image_url']):
        res = fetch_resource(obj['image_url'])
        if res:
            obj['image_url'] = res
        # Force objectcache update to make sure we don't have funky COW issues
        update(obj)
        # Fetch the real image, this will take some screen-scraping unless Rohea is kind enough to add the URL to the API in these last times...
        screenscraper.fill_and_fetch_image_urls(obj['id'])

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
        # TODO: Remove this temp page limit when satisfied with the workings of the rest of the code. (here to prevent 1. unneccessary hammering of the API during testing 2. quicker testing, dumping years worth of messages is going to take a while...)
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
    # Cache all the messages while at it
    mass_insert_and_recurse(replies, recursion_level)
    replycache[object_id] = map(lambda o: fetch_message(str(o['id'])), replies) # refresh the objects before placing them as pointers to the replycache
    # And put a list of the replies to the object we fetched them for
    obj = fetch_message(object_id)
    if in_cache(obj): # this should not fail, not at this point anymore
        obj['QaikuBackup_replies'] = [ o['id'] for o in replies ] # Map a list of the reply IDs to the object (using python pointers we could just point to the list of objects but that would cause no end of headache for the JSON serialization we plane to do)
        # Force objectcache update to make sure we don't have funky COW issues
        update(obj)
    return replycache[object_id]

def insert_and_recurse(qaiku_message, recursion_level = 0):
    """Insert a message to cache and get all it's resources/replies/etc"""
    if not in_cache(qaiku_message):
        update(qaiku_message)
    return recursive_fetch_message(qaiku_message['id'], recursion_level)

def mass_insert_and_recurse(list_of_messages, recursion_level = 0):
    for qaiku_message in list_of_messages:
        if not in_cache(qaiku_message):
            update(qaiku_message)
    # And then handle the recursions
    for qaiku_message in list_of_messages:
        recursive_fetch_message(qaiku_message['id'], recursion_level)

if __name__ == '__main__':
    import sys,os
    recursive_fetch_message(sys.argv[1])
    print json.dumps(objectcache, sort_keys=True, indent=4)
