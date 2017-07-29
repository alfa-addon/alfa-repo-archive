# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    # No existe / borrado: http://allmyvideos.net/8jcgbrzhujri
    data = scrapertools.cache_page("http://anonymouse.org/cgi-bin/anon-www.cgi/" + page_url)
    if "<b>File Not Found</b>" in data or "<b>Archivo no encontrado</b>" in data or '<b class="err">Deleted' in data \
            or '<b class="err">Removed' in data or '<font class="err">No such' in data:
        return False, "No existe o ha sido borrado de allmyvideos"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=%s" % page_url)

    # Normaliza la URL
    videoid = scrapertools.get_match(page_url, "http://allmyvideos.net/([a-z0-9A-Z]+)")
    page_url = "http://amvtv.net/embed-" + videoid + "-728x400.html"
    data = scrapertools.cachePage(page_url)
    if "Access denied" in data:
        geobloqueo = True
    else:
        geobloqueo = False

    if geobloqueo:
        # url = "http://www.anonymousbrowser.xyz/hide.php"
        # post = "go=%s" % page_url
        url = "http://www.videoproxy.co/hide.php"
        post = "go=%s" % page_url
        location = scrapertools.get_header_from_response(url, post=post, header_to_get="location")
        # url = "http://www.anonymousbrowser.xyz/" + location
        url = "http://www.videoproxy.co/" + location
        data = scrapertools.cachePage(url)

    # Extrae la URL
    media_url = scrapertools.find_single_match(data, '"file" : "([^"]+)",')

    video_urls = []

    if media_url != "":
        if geobloqueo:
            # url = "http://www.anonymousbrowser.xyz/hide.php"
            url = "http://www.videoproxy.co/hide.php"
            post = "go=%s" % media_url
            location = scrapertools.get_header_from_response(url, post=post, header_to_get="location")
            # media_url = "http://www.anonymousbrowser.xyz/" + location + "&direct=false"
            media_url = "http://www.videoproxy.co/" + location + "&direct=false"
        else:
            media_url += "&direct=false"

        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [allmyvideos]", media_url])

        for video_url in video_urls:
            logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
