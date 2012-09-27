#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""This tool will fetch a channel stream and dump it using the fetcherparser"""
import fetcherparser

def fetch_channel_messages(channel):
    """Messages in the channel (and comments etc because this all goes to the recursive fetching system)"""
    messages = fetcherparser.fetch_paged("http://www.qaiku.com/api/statuses/channel_timeline/%s.json" % channel)
    fetcherparser.mass_insert_and_recurse(messages)
    return messages

if __name__ == '__main__':
    import sys,os
    channel = sys.argv[1]
    storage.read_object_cache()
    messages = fetch_channel_messages(channel)
    storage.write_message_list('channel_' + channel, messages)
    storage.write_object_cache()
    print "%d messages in cache" % len(storage.objectcache)
