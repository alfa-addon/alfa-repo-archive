# -*- coding: utf-8 -*-

import re
import urllib

from core import logger
from core import scrapertools


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    page_url = page_url.replace("amp;", "")
    data = scrapertools.cache_page(page_url)
    logger.info("data=" + data)

    video_urls = []

    patron = "video_src.*?(http.*?)%22%2C%22video_timestamp"
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for match in matches:
        videourl = match
        logger.info(match)
        videourl = videourl.replace('%5C', '')
        videourl = urllib.unquote(videourl)
        video_urls.append(["[facebook]", videourl])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
