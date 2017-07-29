# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url, follow_redirects=False)

    if data.headers.get("location"):
        return False, "[filez] El archivo ha sido eliminado o no existe"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = httptools.downloadpage(page_url).data

    video_urls = []
    media_urls = scrapertools.find_multiple_matches(data, 'file\s*:\s*"([^"]+)",\s*type\s*:\s*"([^"]+)"')
    for media_url, ext in media_urls:
        video_urls.append([".%s [filez]" % ext, media_url])

    if not video_urls:
        media_urls = scrapertools.find_multiple_matches(data, '<embed.*?src="([^"]+)"')
        for media_url in media_urls:
            media_url = media_url.replace("https:", "http:")
            ext = httptools.downloadpage(media_url, only_headers=True).headers.get("content-disposition", "")
            ext = scrapertools.find_single_match(ext, 'filename="([^"]+)"')
            if ext:
                ext = ext[-4:]
            video_urls.append(["%s [filez]" % ext, media_url])

    return video_urls
