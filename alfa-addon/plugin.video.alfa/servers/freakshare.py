# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    # Existe: http://freakshare.com/files/wy6vs8zu/4x01-mundo-primitivo.avi.html
    # No existe: 
    data = scrapertools.cache_page(page_url)
    patron = '<h1 class="box_heading" style="text-align:center;">([^<]+)</h1>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        return True, ""
    else:
        patron = '<div style="text-align:center;"> (Este archivo no existe)'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if len(matches) > 0:
            return False, matches[0]

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    return video_urls
