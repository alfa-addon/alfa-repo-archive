# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    ogger.info("(page_url='%s')" % page_url)

    # Existe: http://bitshare.com/files/v1ehsvu3/Nikita.S02E15.HDTV.XviD-ASAP.avi.html
    # No existe: http://bitshare.com/files/tn74w9tm/Rio.2011.DVDRip.LATiNO.XviD.by.Glad31.avi.html
    data = scrapertools.cache_page(page_url)
    patron = '<h1>Descargando([^<]+)</h1>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        return True, ""

    patron = '<h1>(Error - Archivo no disponible)</h1>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) > 0:
        return False, "File not found"

    patron = '<b>(Por favor seleccione el archivo a cargar)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) > 0:
        return False, "Enlace no válido"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    return video_urls
