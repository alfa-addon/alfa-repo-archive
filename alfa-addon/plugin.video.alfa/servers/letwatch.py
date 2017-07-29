# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools
from lib import jsunpack


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    if ("File was deleted" or "Not Found") in data:
        return False, "[Letwatch] El archivo no existe o ha sido borrado"
    if "Video is processing now" in data:
        return False, "El vídeo está siendo procesado todavía"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = scrapertools.cache_page(page_url)

    video_urls = []
    media_urls = scrapertools.find_multiple_matches(data, '\{file\:"([^"]+)",label\:"([^"]+)"\}')
    if len(media_urls) > 0:
        for media_url, label in media_urls:
            video_urls.append(
                [scrapertools.get_filename_from_url(media_url)[-4:] + " (" + label + ") [letwatch]", media_url])
    else:
        matches = scrapertools.find_single_match(data, "<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)"
                                                       "</script>")
        matchjs = jsunpack.unpack(matches).replace("\\", "")
        media_urls = scrapertools.find_multiple_matches(matchjs, '\{file\:"([^"]+)",label\:"([^"]+)"\}')
        for media_url, label in media_urls:
            video_urls.append(
                [scrapertools.get_filename_from_url(media_url)[-4:] + " (" + label + ") [letwatch]", media_url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
