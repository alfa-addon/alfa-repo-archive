# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if "404 Page no found" in data:
        return False, "[nosvideo] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    # Lee la URL
    data = scrapertools.cache_page(page_url)
    urls = scrapertools.find_multiple_matches(data, ":'(http:\/\/.+?(?:v.mp4|.smil))")
    urls = set(urls)

    for media_url in urls:
        if ".smil" in media_url:
            data = scrapertools.downloadpage(media_url)
            rtmp = scrapertools.find_single_match(data, '<meta base="([^"]+)"')
            playpath = scrapertools.find_single_match(data, '<video src="([^"]+)"')
            media_url = rtmp + " playpath=" + playpath
            filename = "rtmp"
        else:
            filename = scrapertools.get_filename_from_url(media_url)[-4:]
        video_urls.append([filename + " [nosvideo]", media_url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
