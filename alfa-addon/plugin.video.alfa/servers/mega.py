# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools
from platformcode import platformtools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    from megaserver import Client

    c = Client(url=page_url, is_playing_fnc=platformtools.is_playing)

    files = c.get_files()

    # si hay mas de 5 archivos crea un playlist con todos
    if len(files) > 5:
        media_url = c.get_play_list()
        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [mega]", media_url])
    else:
        for f in files:
            media_url = f["url"]
            video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [mega]", media_url])

    return video_urls
