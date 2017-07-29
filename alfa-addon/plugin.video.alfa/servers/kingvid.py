# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from lib import jsunpack


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    if "<title>watch </title>" in data.lower():
        return False, "[kingvid] El archivo no existe o  ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    match = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")
    data = jsunpack.unpack(match)

    matches = scrapertools.find_multiple_matches(data, 'file\s*:\s*"([^"]+)"\}')
    video_urls = []
    for video_url in matches:
        filename = scrapertools.get_filename_from_url(video_url)[-4:]
        if video_url.endswith("smil"):
            playpath = video_url.rsplit("/", 1)[1].replace(".smil", "")
            rtmp = scrapertools.find_single_match(data, 'image\s*:\s*"([^"]+)"')
            rtmp = scrapertools.find_single_match(rtmp, 'i/(.*?)_')
            video_url = "rtmp://kingvid.tv:1935/vod/ playpath=mp4:%s_n?h=%s " \
                        "swfUrl=http://kingvid.tv/player7/jwplayer.flash.swf pageUrl=%s" % \
                        (rtmp, playpath, page_url)
            filename = "RTMP"
            video_urls.append([filename + " [kingvid]", video_url])
        elif video_url[-4:] in ['.mp4', 'm3u8']:
            video_urls.append([filename + " [kingvid]", video_url])

    video_urls.sort(key=lambda x: x[0], reverse=True)
    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
