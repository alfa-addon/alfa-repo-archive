# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    # Saca el código del vídeo
    if page_url.startswith("http://"):
        try:
            code = scrapertools.get_match(page_url, "http\://www.adnstream.com/video/([a-zA-Z]+)/")
        except:
            code = scrapertools.get_match(page_url, "http\://www.adnstream.tv/video/([a-zA-Z]+)/")
    else:
        code = page_url

    # Lee la playlist    
    url = "http://www.adnstream.com/get_playlist.php?lista=video&param=" + code + "&c=463"
    data = scrapertools.cache_page(url)

    # Extrae la URL
    media_url = scrapertools.get_match(data, "<jwplayer:file>([^<]+)</jwplayer:file>")
    video_urls = [[scrapertools.get_filename_from_url(media_url)[-4:] + ' [adnstream]', media_url]]

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
