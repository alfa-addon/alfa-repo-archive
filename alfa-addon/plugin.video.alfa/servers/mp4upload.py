# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    logger.info("data=" + data)
    media_url = scrapertools.find_single_match(data, '"file": "(.+?)"')
    logger.info("media_url=" + media_url)
    media_url = media_url.replace("?start=0", "")
    logger.info("media_url=" + media_url)

    video_urls = list()
    video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [mp4upload]", media_url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
