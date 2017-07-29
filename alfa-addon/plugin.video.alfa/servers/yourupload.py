# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    if ("File was deleted" or "File not found") in data:
        return False, "[Yourupload] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []
    data = httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data, '<meta property="og:video" content="([^"]+)"')
    if not url:
        url = scrapertools.find_single_match(data, "file:\s*'([^']+)'")
    if url:
        url = "https://www.yourupload.com%s" % url
        referer = {'Referer': page_url}
        location = httptools.downloadpage(url, headers=referer, follow_redirects=False, only_headers=True)
        media_url = location.headers["location"].replace("?start=0", "").replace("https", "http")
        media_url += "|Referer=%s" % url
        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [yourupload]", media_url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
