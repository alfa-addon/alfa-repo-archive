# -*- coding: utf-8 -*-

import re

from core import jsontools
from core import logger
from core import scrapertools


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    headers = [['User-Agent', 'Mozilla/5.0']]
    if "|" in page_url:
        page_url, referer = page_url.split("|", 1)
        headers.append(['Referer', referer])

    if not page_url.endswith("/config"):
        page_url = find_videos(page_url)[0][1]

    video_urls = []
    data = scrapertools.downloadpage(page_url, headers=headers)
    json_object = jsontools.load(data)

    url_data = json_object['request']['files']['progressive']
    for data_media in url_data:
        media_url = data_media['url']
        title = "%s (%s) [vimeo]" % (data_media['mime'].replace("video/", "."), data_media['quality'])
        video_urls.append([title, media_url, data_media['height']])

    video_urls.sort(key=lambda x: x[2])
    try:
        video_urls.insert(0, [".m3u8 (SD) [vimeo]", json_object['request']['files']['hls']['cdns']
        ["akfire_interconnect"]["url"].replace("master.m3u8", "playlist.m3u8"), 0])
    except:
        pass
    for video_url in video_urls:
        video_url[2] = 0
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
