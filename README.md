QaikuBackup
===========

Basic idea is to make a simple lib for recusively fetching Qaiku data
via the [REST API][apidoc] and dump it basically as-is to JSON structure.

Then tools for dumping personal/channel streams using said lib.

After we have a mostly reliable way to get all that data out and to our 
own safekeeping we can worry about making a tool that renders our backup into
something else (HTML, RSS, whatever)

[apidoc]: http://www.qaiku.com/api/usage/

## Support

None, get your local python coder to help you.

Sorry but this is a very quick-and-dirty collection of utility functions and even dirtier wrappers to make them
into CLI utilities. There is very little regard for end-user usability and so far the only coder I need to consider is me...

## Python versions

I have been developing this on OSX with Python2.7 from [Homebrew][hb], it probably works on slightly older versions
and might event work on Windows (but I give no guarantees, at least I try to use proper cross-platform path handling etc)

[hb]: http://mxcl.github.com/homebrew/

## Screenscraping

Unfortunately the REST api only provides access to image thumbnails, to get the original images
some unsavory techniques are needed and for those [BeautifulSoup4][bs4].

[bs4]: http://www.crummy.com/software/BeautifulSoup/
