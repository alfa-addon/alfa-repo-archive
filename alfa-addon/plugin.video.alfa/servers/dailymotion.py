# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    response = httptools.downloadpage(page_url)
    if response.code == 404:
        return False, "[Dailymotion] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    response = httptools.downloadpage(page_url, cookies=False)
    cookie = {'Cookie': response.headers["set-cookie"]}
    data = response.data.replace("\\", "")

    '''
    "240":[{"type":"video/mp4","url":"http://www.dailymotion.com/cdn/H264-320x240/video/x33mvht.mp4?auth=1441130963-2562-u49z9kdc-84796332ccab3c7ce84e01c67a18b689"}]
    '''

    subtitle = scrapertools.find_single_match(data, '"subtitles":.*?"es":.*?urls":\["([^"]+)"')
    qualities = scrapertools.find_multiple_matches(data, '"([^"]+)":(\[\{"type":".*?\}\])')
    for calidad, urls in qualities:
        if calidad == "auto":
            continue
        patron = '"type":"(?:video|application)/([^"]+)","url":"([^"]+)"'
        matches = scrapertools.find_multiple_matches(urls, patron)
        for stream_type, stream_url in matches:
            stream_type = stream_type.replace('x-mpegURL', 'm3u8')
            if stream_type == "mp4":
                stream_url = httptools.downloadpage(stream_url, headers=cookie, only_headers=True,
                                                    follow_redirects=False).headers.get("location", stream_url)
            else:
                data_m3u8 = httptools.downloadpage(stream_url).data
                stream_url = scrapertools.find_single_match(data_m3u8, '(http:.*?\.m3u8)')
            video_urls.append(["%sp .%s [dailymotion]" % (calidad, stream_type), stream_url, 0, subtitle])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
