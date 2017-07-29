# -*- coding: utf-8 -*-

import re
import xml.etree.ElementTree as ET

from core import jsontools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cachePage(page_url)
    if ("File was deleted" or "Not Found") in data: return False, "[playwire] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = scrapertools.cachePage(page_url)
    data = jsontools.load(data)
    f4m = data['content']['media']['f4m']

    video_urls = []
    data = scrapertools.downloadpageGzip(f4m)

    xml = ET.fromstring(data)
    base_url = xml.find('{http://ns.adobe.com/f4m/1.0}baseURL').text
    for media in xml.findall('{http://ns.adobe.com/f4m/1.0}media'):
        if ".m3u8" in media.get('url'): continue
        media_url = base_url + "/" + media.get('url')
        try:
            height = media.get('height')
            width = media.get('width')
            label = "(" + width + "x" + height + ")"
        except:
            label = ""
        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " " + label + " [playwire]", media_url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
