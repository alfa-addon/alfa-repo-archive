# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools
from lib import jsunpack


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = scrapertools.cache_page(page_url)
    if "File Not Found" in data:
        return False, "[Idowatch] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    mediaurl = scrapertools.find_single_match(data, ',{file:(?:\s+|)"([^"]+)"')
    if not mediaurl:
        matches = scrapertools.find_single_match(data,
                                                 "<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
        matchjs = jsunpack.unpack(matches).replace("\\", "")
        mediaurl = scrapertools.find_single_match(matchjs, ',{file:(?:\s+|)"([^"]+)"')

    video_urls = []
    video_urls.append([scrapertools.get_filename_from_url(mediaurl)[-4:] + " [idowatch]", mediaurl])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
