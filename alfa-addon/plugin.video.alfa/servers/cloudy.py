# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "This video is being prepared" in data:
        return False, "[Cloudy] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []
    data = httptools.downloadpage(page_url).data

    media_urls = scrapertools.find_multiple_matches(data, '<source src="([^"]+)"')
    for mediaurl in media_urls:
        title = "%s [cloudy]" % scrapertools.get_filename_from_url(mediaurl)[-4:]
        mediaurl += "|User-Agent=Mozilla/5.0"
        video_urls.append([title, mediaurl])

    return video_urls
