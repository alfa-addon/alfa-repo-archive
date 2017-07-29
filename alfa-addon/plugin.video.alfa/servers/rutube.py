# -*- coding: utf-8 -*-

import re

from core import jsontools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cachePage(page_url)
    if ("File was deleted" or "Not Found") in data: return False, "[rutube] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = scrapertools.cachePage(page_url)
    if "embed" in page_url:
        link = scrapertools.find_single_match(data, '<link rel="canonical" href="https://rutube.ru/video/([\da-z]{32})')
        url = "http://rutube.ru/api/play/options/%s/?format=json" % link
        data = scrapertools.cachePage(url)

    data = jsontools.load(data)
    m3u8 = data['video_balancer']['m3u8']
    data = scrapertools.downloadpageGzip(m3u8)
    video_urls = []
    mediaurls = scrapertools.find_multiple_matches(data, '(http://.*?)\?i=(.*?)_')
    for media_url, label in mediaurls:
        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " (" + label + ") [rutube]", media_url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
