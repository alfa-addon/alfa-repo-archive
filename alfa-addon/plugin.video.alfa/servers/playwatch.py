# -*- coding: utf-8 -*-

import base64
import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    response = httptools.downloadpage(page_url, follow_redirects=False)

    if not response.sucess or response.headers.get("location"):
        return False, "[Playwatch] El fichero no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = httptools.downloadpage(page_url, follow_redirects=False).data

    code = scrapertools.find_single_match(data, ' tracker:\s*"([^"]+)"')
    media_url = base64.b64decode(code)
    ext = scrapertools.get_filename_from_url(media_url)[-4:]
    video_urls = [["%s  [playwatch]" % ext, media_url]]

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
