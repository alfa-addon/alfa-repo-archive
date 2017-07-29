# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if "This video doesn't exist." in data:
        return False, 'The requested video was not found.'

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)
    text_encode = scrapertools.find_single_match(data, "(eval\(function\(p,a,c,k,e,d.*?)</script>")

    from aadecode import decode as aadecode
    text_decode = aadecode(text_encode)

    # URL del vídeo
    patron = "'([^']+)'"
    media_url = scrapertools.find_single_match(text_decode, patron)

    video_urls.append([media_url[-4:] + " [Videowood]", media_url])

    return video_urls
