# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    if "File was deleted" in data or "Page Cannot Be Found" in data:
        return False, "[thevideo.me] El archivo ha sido eliminado o no existe"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    if not "embed" in page_url:
        page_url = page_url.replace("http://thevideo.me/", "http://thevideo.me/embed-") + ".html"

    data = httptools.downloadpage(page_url).data

    mpri_Key = scrapertools.find_single_match(data, "lets_play_a_game='([^']+)'")
    data_vt = httptools.downloadpage("https://thevideo.me/vsign/player/%s" % mpri_Key).data
    vt = scrapertools.find_single_match(data_vt, 'function\|([^\|]+)\|')
    if "fallback" in vt:
        vt = scrapertools.find_single_match(data_vt, 'jwConfig\|([^\|]+)\|')

    media_urls = scrapertools.find_multiple_matches(data, '\{"file"\s*\:\s*"([^"]+)"\s*,\s*"label"\s*\:\s*"([^"]+)"')
    video_urls = []

    for media_url, label in media_urls:
        media_url += "?direct=false&ua=1&vt=%s" % vt
        video_urls.append(
            [scrapertools.get_filename_from_url(media_url)[-4:] + " (" + label + ") [thevideo.me]", media_url])

    return video_urls
