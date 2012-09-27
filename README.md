QaikuBackup
===========

Basic idea is to make a simple lib for recusively fetching Qaiku data
via the [REST API][apidoc] and dump it basically as-is to JSON structure.

Then tools for dumping personal/channel streams using said lib.

After we have a mostly reliable way to get all that data out and to our 
own safekeeping we can worry about making a tool that renders our backup into
something else (HTML, RSS, whatever)

[apidoc]: http://www.qaiku.com/api/usage/

## Usage

  1. Checkout the repo and change directory there.
  2. Create qaiku_api_key.txt containing your [Qaiku API Key][apikey] on the first line.
  3. Look at fetcherparser.py and test with a single message id from your stream.
  4. Look at userdump.py and channeldump.py if you want to make huge (and time-consuming) dumps of channel/user streams.

[apikey]: http://www.qaiku.com/settings/api/

## Support

None, get your local Python coder to help you (or spend a bit of time learning the basics of the language [my code is not exactly "Pythonic", 
it's polluted by idioms from other languages I have to work with]).

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
