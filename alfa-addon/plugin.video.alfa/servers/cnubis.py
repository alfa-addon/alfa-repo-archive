# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("page_url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)
    media_url = scrapertools.find_single_match(data, 'file: "([^"]+)",.*?type: "([^"]+)"')
    logger.info("media_url=" + media_url[0])

    # URL del vídeo
    video_urls.append(["." + media_url[1] + " [cnubis]", media_url[0].replace("https", "http")])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
