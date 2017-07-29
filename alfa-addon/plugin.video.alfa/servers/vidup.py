# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data

    if "Not Found" in data:
        return False, "[Vidup.me] El fichero no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = httptools.downloadpage(page_url).data

    key = scrapertools.find_single_match(data, "var mpri_Key\s*=\s*'([^']+)'")
    data_vt = httptools.downloadpage("http://vidup.me/jwv/%s" % key).data
    vt = scrapertools.find_single_match(data_vt, 'direct\|([^\|]+)\|')

    # Extrae la URL
    video_urls = []
    media_urls = scrapertools.find_multiple_matches(data, '\{"file"\:"([^"]+)","label"\:"([^"]+)"\}')
    for media_url, label in media_urls:
        ext = scrapertools.get_filename_from_url(media_url)[-4:]
        media_url += "?direct=false&ua=1&vt=%s" % vt
        video_urls.append(["%s (%s) [vidup.me]" % (ext, label), media_url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
