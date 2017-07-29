# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    try:
        response = httptools.downloadpage(page_url)
    except:
        pass

    if not response.data or "urlopen error [Errno 1]" in str(response.code):
        from core import config
        if config.is_xbmc():
            return False, "[Rapidvideo] Este conector solo funciona a partir de Kodi 17"
        elif config.get_platform() == "plex":
            return False, "[Rapidvideo] Este conector no funciona con tu versión de Plex, intenta actualizarla"
        elif config.get_platform() == "mediaserver":
            return False, "[Rapidvideo] Este conector requiere actualizar python a la versión 2.7.9 o superior"

    if "Object not found" in response.data:
        return False, "[Rapidvideo] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    urls = scrapertools.find_multiple_matches(data, '"file":"([^"]+)","label":"[^"]*","res":"([^"]+)"')
    for mediaurl, res in urls:
        ext = scrapertools.get_filename_from_url(mediaurl)[-4:]
        video_urls.append(['%s %sp [rapidvideo]' % (ext, res), mediaurl.replace("\\", "")])

    return video_urls
