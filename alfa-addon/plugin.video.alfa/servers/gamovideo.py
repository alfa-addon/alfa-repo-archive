# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from lib import jsunpack

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url, headers=headers).data

    if "File was deleted" in data or "Not Found" in data or "File was locked by administrator" in data:
        return False, "[Gamovideo] El archivo no existe o ha sido borrado"
    if "Video is processing now" in data:
        return False, "[Gamovideo] El video está procesándose en estos momentos. Inténtelo mas tarde."

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url, headers=headers).data

    packer = scrapertools.find_single_match(data,
                                            "<script type='text/javascript'>(eval.function.p,a,c,k,e,d..*?)</script>")
    if packer != "":
        data = jsunpack.unpack(packer)

    data = re.sub(r'\n|\t|\s+', '', data)

    host = scrapertools.find_single_match(data, '\[\{image:"(http://[^/]+/)')
    mediaurl = scrapertools.find_single_match(data, ',\{file:"([^"]+)"')
    if not mediaurl.startswith(host):
        mediaurl = host + mediaurl

    rtmp_url = scrapertools.find_single_match(data, 'file:"(rtmp[^"]+)"')
    playpath = scrapertools.find_single_match(rtmp_url, 'mp4:.*$')
    rtmp_url = rtmp_url.split(playpath)[
                   0] + " playpath=" + playpath + " swfUrl=http://gamovideo.com/player61/jwplayer.flash.swf"

    video_urls = []
    video_urls.append(["RTMP [gamovideo]", rtmp_url])
    video_urls.append([scrapertools.get_filename_from_url(mediaurl)[-4:] + " [gamovideo]", mediaurl])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
