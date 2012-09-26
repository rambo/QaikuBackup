QaikuBackup
===========

Basic idea is to make a simple lib for recusively fetching Qaiku data
via the [REST API][1] and dump it basically as-is to JSON structure.

Then tools for dumping personal/channel streams using said lib.

After we have a mostly reliable way to get all that data out and to our 
own safekeeping we can worry about making a tool that renders our backup into
something else (HTML, RSS, whatever)

[1]: http://www.qaiku.com/api/usage/

## Screenscraping

Unfortunately the REST api only provides access to image thumbnails, to get the original images
some unsavory techniques are needed and for those [BeautifulSoup4][2].

[2]: http://www.crummy.com/software/BeautifulSoup/
