# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    # if '<meta property="og:title" content=""/>' in data:
    # return False,"The video has been cancelled from Backin.net"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    headers = []
    headers.append(["User-Agent",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17"])

    # First access
    data = scrapertools.cache_page(page_url, headers=headers)
    logger.info("data=" + data)

    # URL
    url = scrapertools.find_single_match(data, 'type="video/mp4" src="([^"]+)"')
    logger.info("url=" + url)

    # URL del vídeo
    video_urls.append([".mp4" + " [backin]", url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
