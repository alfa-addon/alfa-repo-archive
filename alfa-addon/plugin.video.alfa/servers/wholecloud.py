# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data

    if "This file no longer exists on our servers" in data:
        return False, "[wholecloud] El archivo ha sido eliminado o no existe"
    if "This video is not yet ready" in data:
        return False, "[wholecloud] El archivo no está listo, se está subiendo o convirtiendo"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = httptools.downloadpage(page_url).data

    video_urls = []
    media_urls = scrapertools.find_multiple_matches(data, '<source src="([^"]+)"')
    if not media_urls:
        media_url = scrapertools.find_single_match(data, 'src="/api/toker.php\?f=([^"]+)"')
        ext = scrapertools.get_filename_from_url(media_url)[-4:]
        media_url = "http://wholecloud.net/download.php?file=%s|User-Agent=Mozilla/5.0" % media_url
        video_urls.append([ext + " [wholecloud]", media_url])
    else:
        for media_url in media_urls:
            ext = scrapertools.get_filename_from_url(media_url)[-4:]
            media_url += "|User-Agent=Mozilla/5.0"
            video_urls.append([ext + " [wholecloud]", media_url])

    return video_urls
