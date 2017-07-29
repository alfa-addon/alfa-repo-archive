# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from lib import jsunpack


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = httptools.downloadpage(page_url).data

    match = scrapertools.find_single_match(data, "<script type='text/javascript'>(.*?)</script>")
    if match.startswith("eval"):
        match = jsunpack.unpack(match)

    # Extrae la URL
    # {file:"http://95.211.81.229/kj2vy4rle46vtaw52bsj4ooof6meikcbmwimkrthrahbmy4re3eqg3buhoza/v.mp4",label:"240p"
    video_urls = []
    media_urls = scrapertools.find_multiple_matches(match, '\{file\:"([^"]+)",label:"([^"]+)"')
    subtitle = scrapertools.find_single_match(match, 'tracks: \[\{file: "([^"]+)", label: "Spanish"')
    for media_url, quality in media_urls:
        video_urls.append([media_url[-4:] + " [thevideos] " + quality, media_url, 0, subtitle])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
