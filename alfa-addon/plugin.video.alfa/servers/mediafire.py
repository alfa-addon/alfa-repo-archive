# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data

    if "Invalid or Deleted File" in data:
        return False, "[Mediafire] El archivo no existe o ha sido borrado"
    elif "File Removed for Violation" in data:
        return False, "[Mediafire] Archivo eliminado por infracción"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    patron = 'kNO \= "([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) > 0:
        video_urls.append([matches[0][-4:] + " [mediafire]", matches[0]])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
