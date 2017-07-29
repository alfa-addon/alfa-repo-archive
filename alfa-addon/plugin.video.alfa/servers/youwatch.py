# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "File Not Found" in data:
        return False, "[Youwatch] El archivo no existe o ha sido borrado"

    url_redirect = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
    data = httptools.downloadpage(url_redirect).data
    if "We're sorry, this video is no longer available" in data:
        return False, "[Youwatch] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    url_redirect = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
    data = httptools.downloadpage(url_redirect).data

    url = scrapertools.get_match(data, '{file:"([^"]+)"')
    video_url = "%s|Referer=%s" % (url, url_redirect)
    video_urls = [[scrapertools.get_filename_from_url(url)[-4:] + " [youwatch]", video_url]]

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
