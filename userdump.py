#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""This tool will fetch users Qaiku stream and dump it using the fetcherparser"""
import fetcherparser

def fetch_api_user_messages():
    """Messages only by the user (and comments etc because this all goes to the recursive fetching system)"""
    messages = fetcherparser.fetch_paged("http://www.qaiku.com/api/statuses/user_timeline.json")
    fetcherparser.mass_insert_and_recurse(messages)
    return [ o['id'] for o in messages ] # Return a list of message ids
    return messages

def fetch_api_user_stream():
    """Messages in the users stream (and comments etc because this all goes to the recursive fetching system)"""
    messages = fetcherparser.fetch_paged("http://www.qaiku.com/api/statuses/friends_timeline.json")
    fetcherparser.mass_insert_and_recurse(messages)

if __name__ == '__main__':
    import sys,os,json
    fetch_api_user_messages()
    print json.dumps(fetcherparser.objectcache, sort_keys=True, indent=4)
    print "%d messages in cache" % len(fetcherparser.objectcache)


