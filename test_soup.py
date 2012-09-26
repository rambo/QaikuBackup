#!/usr/bin/env python -i
# -*- coding: UTF-8 -*-
import urllib2
from bs4 import BeautifulSoup

soup = BeautifulSoup(urllib2.urlopen('http://www.qaiku.com/go/ewyu/'))
msg_div = soup.find(id="qaiku_%s" % 'b8c2a38660b711e195659dc22204a487a487') # use the string formatter since we will be having this in a variable
view_img = msg_div.find('img', class_='multimediaurl')
orig_link = view_img.find_parent('a')

print "View url %s" % view_img['src']
print "Orig url %s" % orig_link['href']

