#!/usr/bin/env python
# -*- coding: UTF-8 -*-

debug = True


import json, urllib2, hashlib, os, re
import traceback, sys

def read_api_key():
    """Helper to read the API key, later will ask for it if the file is missing"""
    fp = open('qaiku_api_key.txt')
    return fp.readline().strip()

apikey = read_api_key()
objectcache = {}

def update(obj):
    """Re-inserts the object to the cache dict, maybe this will help with weird cow/pointer issues"""
    object_id = str(obj['id'])
    if debug:
        print "update called from"
        traceback.print_stack()
        if objectcache.has_key(object_id):
            print "Before update objectcache[%s] is" % object_id
            print json.dumps(objectcache[object_id], sort_keys=True, indent=4)
    objectcache[object_id] = obj
    if debug:
        print "After update objectcache[%s] is" % object_id
        print json.dumps(objectcache[object_id], sort_keys=True, indent=4)
        
def in_cache(obj):
    """Normalized way to check for object presence in cache"""
    object_id = str(obj['id'])
    return objectcache.has_key(object_id)

def in_cache_byid(object_id):
    object_id = str(object_id)
    return objectcache.has_key(object_id)

def get_byid(object_id):
    object_id = str(object_id)
    return objectcache[object_id]
    

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
