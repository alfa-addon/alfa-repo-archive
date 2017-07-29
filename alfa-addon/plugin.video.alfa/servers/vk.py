# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if "This video has been removed from public access" in data:
        return False, "El archivo ya no esta disponible<br/>en VK (ha sido borrado)"
    else:
        return True, ""


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []
    try:
        oid, id = scrapertools.find_single_match(page_url, 'oid=([^&]+)&id=(\d+)')
    except:
        oid, id = scrapertools.find_single_match(page_url, 'video(\d+)_(\d+)')

    from core import httptools
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "http://vk.com/al_video.php?act=show_inline&al=1&video=%s_%s" % (oid, id)
    data = httptools.downloadpage(url, headers=headers).data

    matches = scrapertools.find_multiple_matches(data, '<source src="([^"]+)" type="video/(\w+)')
    for media_url, ext in matches:
        calidad = scrapertools.find_single_match(media_url, '(\d+)\.%s' % ext)
        video_urls.append(["." + ext + " [vk:" + calidad + "]", media_url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
