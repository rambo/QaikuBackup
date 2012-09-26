#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import fetcherparser,json

# Done this way allow gracefull degradation
can_scrape = False
try:
    from bs4 import BeautifulSoup
    can_scrape = True
except ImportError:
    pass

def fill_image_urls(message_id):
    if not can_scrape:
        return False
    if (    not fetcherparser.objectcache.has_key(message_id)
        and not fetcherparser.recursive_fetch_message(message_id)):
        print "Fail"
        return False
    obj = fetcherparser.fetch_message(message_id)
    
    # TODO implement
    
    return True

def fill_and_fetch_image_urls(message_id):
    if not fill_image_urls(message_id):
        return False

    obj = fetcherparser.fetch_message(message_id)

    for prop in ['QaikuBackup_image_url_view', 'QaikuBackup_image_url_orig']:
        if not obj.has_key(prop):
            continue
        res = fetcherparser.fetch_resource(obj[prop])
        if res:
            obj[prop] = res

    return True

if __name__ == '__main__':
    import sys,os
    msgid = sys.argv[1]
    if fill_image_urls(msgid):
        print json.dumps(fetcherparser.objectcache[msgid], sort_keys=True, indent=4)
    else:
        sys.exit(1)
