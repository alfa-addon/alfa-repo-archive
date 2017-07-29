# -*- coding: utf-8 -*-

import re

from core import httptools
from core import jsontools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = jsontools.load(httptools.downloadpage("http://www.vidgg.to/api-v2/alive.php?link=" + page_url).data)
    if data["data"] == "NOT_FOUND" or data["data"] == "FAILED":
        return False, "[Vidgg] El archivo no existe o ha sido borrado"
    elif data["data"] == "CONVERTING":
        return False, "[Vidgg] El archivo se está procesando"
    else:
        return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []
    data = httptools.downloadpage(page_url).data

    mediaurls = scrapertools.find_multiple_matches(data, '<source src="([^"]+)"')
    if not mediaurls:
        id_file = page_url.rsplit("/", 1)[1]
        key = scrapertools.find_single_match(data, 'flashvars\.filekey\s*=\s*"([^"]+)"')
        if not key:
            varkey = scrapertools.find_single_match(data, 'flashvars\.filekey\s*=\s*([^;]+);')
            key = scrapertools.find_single_match(data, varkey + '\s*=\s*"([^"]+)"')

        # Primera url, se extrae una url erronea necesaria para sacar el enlace
        url = "http://www.vidgg.to//api/player.api.php?cid2=undefined&cid=undefined&numOfErrors=0&user=undefined&cid3=undefined&key=%s&file=%s&pass=undefined" % (
            key, id_file)
        data = httptools.downloadpage(url).data

        url_error = scrapertools.find_single_match(data, 'url=([^&]+)&')
        url = "http://www.vidgg.to//api/player.api.php?cid2=undefined&cid=undefined&numOfErrors=1&errorUrl=%s&errorCode=404&user=undefined&cid3=undefined&key=%s&file=%s&pass=undefined" % (
            url_error, key, id_file)
        data = httptools.downloadpage(url).data
        mediaurls = scrapertools.find_multiple_matches(data, 'url=([^&]+)&')

    for i, mediaurl in enumerate(mediaurls):
        title = scrapertools.get_filename_from_url(mediaurl)[-4:] + " Mirror %s [vidgg]" % str(i + 1)
        mediaurl += "|User-Agent=Mozilla/5.0"
        video_urls.append([title, mediaurl])

    for video_url in video_urls:
        logger.info(" %s - %s" % (video_url[0], video_url[1]))

    return video_urls
