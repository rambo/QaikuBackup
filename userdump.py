#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""This tool will fetch users Qaiku stream and dump it using the fetcherparser"""
import storage, fetcherparser, urllib_cached

def fetch_api_user_messages():
    """Messages only by the user (and comments etc because this all goes to the recursive fetching system)"""
    messages = fetcherparser.fetch_paged("http://www.qaiku.com/api/statuses/user_timeline.json")
    fetcherparser.mass_insert_and_recurse(messages)
    return messages

def fetch_api_user_stream():
    """Messages in the users stream (and comments etc because this all goes to the recursive fetching system)"""
    messages = fetcherparser.fetch_paged("http://www.qaiku.com/api/statuses/friends_timeline.json")
    fetcherparser.mass_insert_and_recurse(messages)
    return messages

if __name__ == '__main__':
    import sys,os
    print "*** STARTING ***"
    storage.read_object_cache()
    messages = fetch_api_user_messages()
    storage.write_message_list('user_' + storage.apikey, messages)
    storage.write_object_cache()
    urllib_cached.clean()
    print "*** DONE ***"
    print "%d messages in cache" % len(storage.objectcache)


