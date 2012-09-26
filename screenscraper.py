#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import fetcherparser,urllib2

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
    if (    not fetcherparser.objectcache.has_key(message_id)
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
    soup = BeautifulSoup(urllib2.urlopen(url))

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
    
    if debug:
        for prop in ['id', 'QaikuBackup_image_url_view', 'QaikuBackup_image_url_orig']:
            print "obj['%s']=%s" % (prop, obj[prop])

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

    return True

if __name__ == '__main__':
    import sys,os,json
    msgid = sys.argv[1]
    if fill_image_urls(msgid):
        print json.dumps(fetcherparser.objectcache[msgid], sort_keys=True, indent=4)
    else:
        sys.exit(1)
