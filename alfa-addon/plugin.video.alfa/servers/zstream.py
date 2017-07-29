# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    if "File was deleted" in data:
        return False, "[Zstream] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=%s" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    matches = scrapertools.find_multiple_matches(data, '\{file:"([^"]+)",label:"([^"]+)"')
    for media_url, calidad in matches:
        calidad = "." + media_url.rsplit('.', 1)[1] + " " + calidad
        video_urls.append([calidad + ' [zstream]', media_url])

    return video_urls
