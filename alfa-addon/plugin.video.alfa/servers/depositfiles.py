# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    # Existe: http://depositfiles.com/files/vmhjug6t7
    # No existe: 
    data = scrapertools.cache_page(page_url)
    patron = 'Nombre del Archivo: <b title="([^"]+)">([^<]+)</b>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        return True, ""
    else:
        patron = '<div class="no_download_msg">([^<]+)<'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if len(matches) > 0:
            return False, "El archivo ya no está disponible<br/>en depositfiles o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    return video_urls
