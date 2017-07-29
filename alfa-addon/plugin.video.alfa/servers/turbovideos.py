# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools
from lib import jsunpack


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    if "embed" not in page_url:
        page_url = page_url.replace("http://turbovideos.net/", "http://turbovideos.net/embed-") + ".html"

    data = scrapertools.cache_page(page_url)
    logger.info("data=" + data)

    data = scrapertools.find_single_match(data,
                                          "<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
    logger.info("data=" + data)

    data = jsunpack.unpack(data)
    logger.info("data=" + data)

    video_urls = []
    # {file:"http://ultra.turbovideos.net/73ciplxta26xsbj2bqtkqcd4rtyxhgx5s6fvyzed7ocf4go2lxjnd6e5kjza/v.mp4",label:"360"
    media_urls = scrapertools.find_multiple_matches(data, 'file:"([^"]+)",label:"([^"]+)"')
    for media_url, label in media_urls:

        if not media_url.endswith("srt"):
            video_urls.append(
                [scrapertools.get_filename_from_url(media_url)[-4:] + " " + label + " [turbovideos]", media_url])

    return video_urls
