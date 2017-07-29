# -*- coding: utf-8 -*-

import base64
import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []

    data = scrapertools.cachePage(page_url)

    codif = scrapertools.find_single_match(data, 'var [a-z]+ = ([0-9]+);')
    link = scrapertools.find_single_match(data, 'linkfile ="([^"]+)"')
    numero = int(codif)

    # Decrypt link base64 // python version of speedvideo's base64_decode() [javascript]

    link1 = link[:numero]
    link2 = link[numero + 10:]
    link = link1 + link2
    media_url = base64.b64decode(link)

    video_urls.append(["." + media_url.rsplit('.', 1)[1] + ' [speedvideo]', media_url])

    return video_urls
