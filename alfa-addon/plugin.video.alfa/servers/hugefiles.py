# -*- coding: utf-8 -*-

import re
import urllib

from core import logger
from core import scrapertools
from lib import jsunpack


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    # Submit
    post = {}
    r = re.findall(r'type="hidden" name="(.+?)"\s* value="?(.+?)">', data)
    for name, value in r:
        post[name] = value
        post.update({'method_free': 'Free Download'})
    data = scrapertools.cache_page(page_url, post=urllib.urlencode(post))

    # Get link
    sPattern = '''<div id="player_code">.*?<script type='text/javascript'>(eval.+?)</script>'''
    r = re.findall(sPattern, data, re.DOTALL | re.I)
    mediaurl = ""
    if r:
        sUnpacked = jsunpack.unpack(r[0])
        sUnpacked = sUnpacked.replace("\\'", "")
        r = re.findall('file,(.+?)\)\;s1', sUnpacked)
        if not r:
            r = re.findall('"src"value="(.+?)"/><embed', sUnpacked)

        mediaurl = r[0]

    video_urls = []
    video_urls.append([scrapertools.get_filename_from_url(mediaurl)[-4:] + " [hugefiles]", mediaurl])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
