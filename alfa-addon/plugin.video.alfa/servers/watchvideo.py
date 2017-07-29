# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data

    if "Not Found" in data or "File was deleted" in data:
        return False, "[Watchvideo] El fichero no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = httptools.downloadpage(page_url).data

    video_urls = []
    media_urls = scrapertools.find_multiple_matches(data, '\{file\s*:\s*"([^"]+)",label\s*:\s*"([^"]+)"\}')
    for media_url, label in media_urls:
        ext = scrapertools.get_filename_from_url(media_url)[-4:]
        video_urls.append(["%s %sp [watchvideo]" % (ext, label), media_url])

    video_urls.reverse()
    m3u8 = scrapertools.find_single_match(data, '\{file\:"(.*?.m3u8)"\}')
    if m3u8:
        title = video_urls[-1][0].split(" ", 1)[1]
        video_urls.insert(0, [".m3u8 %s" % title, m3u8])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
