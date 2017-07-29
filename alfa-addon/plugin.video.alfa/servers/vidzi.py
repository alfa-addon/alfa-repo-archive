# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from lib import jsunpack


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)
    if not response.sucess:
        return False, "[Vidzi] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    if not "embed" in page_url:
        page_url = page_url.replace("http://vidzi.tv/", "http://vidzi.tv/embed-") + ".html"

    data = httptools.downloadpage(page_url).data
    media_urls = scrapertools.find_multiple_matches(data, 'file\s*:\s*"([^"]+)"')

    if not media_urls:
        data = scrapertools.find_single_match(data,
                                              "<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
        data = jsunpack.unpack(data)
        media_urls = scrapertools.find_multiple_matches(data, 'file\s*:\s*"([^"]+)"')

    video_urls = []
    for media_url in media_urls:
        ext = scrapertools.get_filename_from_url(media_url)[-4:]
        if not media_url.endswith("vtt"):
            video_urls.append(["%s [vidzi]" % ext, media_url])

    return video_urls
