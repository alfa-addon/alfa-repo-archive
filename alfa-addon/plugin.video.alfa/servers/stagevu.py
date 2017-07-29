# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    # Descarga la página del vídeo
    data = scrapertools.cache_page(page_url)

    # Busca el vídeo de dos formas distintas
    patronvideos = '<param name="src" value="([^"]+)"'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        video_urls = [["[stagevu]", matches[0]]]
    else:
        patronvideos = 'src="([^"]+stagevu.com/[^i][^"]+)"'  # Forma src="XXXstagevu.com/ y algo distinto de i para evitar images e includes
        matches = re.findall(patronvideos, data)
        if len(matches) > 0:
            video_urls = [["[stagevu]", matches[0]]]

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
