# -*- coding: utf-8 -*-

import re
import urllib

from core import logger
from core import scrapertools


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    # Busca el ID en la URL
    id = extract_id(page_url)

    # Si no lo tiene, lo extrae de la página
    if id == "":
        # La descarga
        data = scrapertools.cache_page(page_url)
        patron = '<link rel="video_src" href="([^"]+)"/>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if len(matches) > 0:
            id = extract_id(matches[0])
        else:
            id = ""

    if id == "":
        id = scrapertools.get_match(page_url, "tu.tv/iframe/(\d+)")

    # Descarga el descriptor
    url = "http://tu.tv/visualizacionExterna2.php?web=undefined&codVideo=" + id
    data = scrapertools.cache_page(url)

    # Obtiene el enlace al vídeo
    patronvideos = 'urlVideo0=([^\&]+)\&'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    # scrapertools.printMatches(matches)
    url = urllib.unquote_plus(matches[0])
    video_urls = [["[tu.tv]", url]]

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls


def extract_id(text):
    patron = "xtp\=([a-zA-Z0-9]+)"
    matches = re.compile(patron, re.DOTALL).findall(text)
    if len(matches) > 0:
        devuelve = matches[0]
    else:
        devuelve = ""

    return devuelve
