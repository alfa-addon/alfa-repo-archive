# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from lib import jsunpack


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    if "File Not Found" in data:
        return False, "[Watchers] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=%s" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    packed = scrapertools.find_single_match(data, '(eval\(function\(p,a,c,k,e.*?)</script>').strip()
    unpack = jsunpack.unpack(packed)

    bloque = scrapertools.find_single_match(unpack, 'sources:\[(.*?)\}\]')
    matches = scrapertools.find_multiple_matches(bloque, 'file:"([^"]+)"(?:,label:"([^"]+)"|\})')
    for media_url, calidad in matches:
        ext = scrapertools.get_filename_from_url(media_url)[-4:]
        if calidad:
            ext += " " + calidad + "p"
        media_url += "|Referer=%s" % page_url
        video_urls.append([ext + ' [watchers]', media_url])

    return video_urls
