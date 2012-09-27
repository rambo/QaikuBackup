#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Screenscraper routines to get the URLs of images in messages (the proper images, not the tiny thumbnail the API provides)"""
import urllib_cached
import storage, fetcherparser

debug = True

# Done this way allow gracefull degradation
can_scrape = False
try:
    from bs4 import BeautifulSoup
    can_scrape = True
except ImportError:
    pass

def fill_image_urls(message_id):
    """Loads the object, then tries to figure out the web URL for it and scrape said url for the images"""
    if not can_scrape:
        return False
    if (    not storage.in_cache_byid(message_id)
        and not fetcherparser.recursive_fetch_message(message_id)):
        return False
    obj = fetcherparser.fetch_message(message_id)

    # There is no image, don't bother...
    if (   not obj.has_key('image_url')
        or not obj['image_url']):
        return False

    # Already processed this one
    for prop in ['QaikuBackup_image_url_view', 'QaikuBackup_image_url_orig']:
        if obj.has_key(prop):
            return True

    # Try to figure the shortest way to the canonical message HTML view
    url = None
    if obj.has_key('in_reply_to_status_url'):
        url = obj['in_reply_to_status_url'] # This is a redirect but urllib has no problem following it
    if (    not url
        and obj.has_key('channel')
        and obj['channel']):
        url = "http://www.qaiku.com/channels/show/%s/view/%s/" % (obj['channel'], obj['id']) # Channel message
    if (    not url
        and obj.has_key('user')
        and obj['user'].has_key('url')
        and obj['user']['url']):
        url = "%s/show/%s/" % (obj['user']['url'], obj['id']) # non-Channel message
    # Are there other possible combinations ?
    if not url:
        return False

    if debug:
        print "Soupifying %s" % url
    try:
        soup = BeautifulSoup(urllib_cached.urlopen(url))
    except Exception,e:
        print "Got exception %s" % e
        return False

    msg_div = soup.find(id="qaiku_%s" % message_id)
    if not msg_div:
        return False
    view_img = msg_div.find('img', class_='multimediaurl')
    if not view_img:
        return False
    obj['QaikuBackup_image_url_view'] = view_img['src']
    orig_link = view_img.find_parent('a')
    if not orig_link:
        return False
    obj['QaikuBackup_image_url_orig'] = orig_link['href']
    
#    if debug:
#        for prop in ['id', 'QaikuBackup_image_url_view', 'QaikuBackup_image_url_orig']:
#            print "obj['%s']=%s" % (prop, obj[prop])

    # Force objectcache update to make sure we don't have funky COW issues
    storage.update(obj)
    return True

def fill_and_fetch_image_urls(message_id):
    """Loads the given object, hits the screenscraper to fill the extra image properties and then fetches those images"""
    if not fill_image_urls(message_id):
        return False

    obj = fetcherparser.fetch_message(message_id)

    for prop in ['QaikuBackup_image_url_view', 'QaikuBackup_image_url_orig']:
        if not obj.has_key(prop):
            continue
        res = fetcherparser.fetch_resource(obj[prop])
        if res:
            obj[prop] = res

    # Force objectcache update to make sure we don't have funky COW issues
    storage.update(obj)
    return True

if __name__ == '__main__':
    import sys,os,json
    msgid = sys.argv[1]
    print "*** STARTING ***"
    if fill_image_urls(msgid):
        urllib_cached.clean()
        print "*** DONE ***"
        print "message %s contents:" % msgid
        print json.dumps(storage.get_byid(msgid), sort_keys=True, indent=4)
    else:
        urllib_cached.clean()
        print "*** FAILED ***"
        sys.exit(1)
