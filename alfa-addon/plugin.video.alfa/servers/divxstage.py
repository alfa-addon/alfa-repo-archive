# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools

host = "http://www.cloudtime.to"


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url.replace('/embed/?v=', '/video/')).data

    if "This file no longer exists" in data:
        return False, "El archivo no existe<br/>en divxstage o ha sido borrado."

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    if "divxstage.net" in page_url:
        page_url = page_url.replace("divxstage.net", "cloudtime.to")

    data = httptools.downloadpage(page_url).data

    video_urls = []
    videourls = scrapertools.find_multiple_matches(data, 'src\s*:\s*[\'"]([^\'"]+)[\'"]')
    if not videourls:
        videourls = scrapertools.find_multiple_matches(data, '<source src=[\'"]([^\'"]+)[\'"]')
    for videourl in videourls:
        if videourl.endswith(".mpd"):
            id = scrapertools.find_single_match(videourl, '/dash/(.*?)/')
            videourl = "http://www.cloudtime.to/download.php%3Ffile=mm" + "%s.mp4" % id

        videourl = re.sub(r'/dl(\d)*/', '/dl/', videourl)
        ext = scrapertools.get_filename_from_url(videourl)[-4:]
        videourl = videourl.replace("%3F", "?") + \
                   "|User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
        video_urls.append([ext + " [cloudtime]", videourl])

    return video_urls
