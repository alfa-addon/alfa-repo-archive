# -*- coding: utf-8 -*-

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    if "tusfiles.net" in page_url:
        data = httptools.downloadpage(page_url).data

        if "File Not Found" in data:
            return False, "[Tusfiles] El archivo no existe o ha sido borrado"
        if "download is no longer available" in data:
            return False, "[Tusfiles] El archivo ya no está disponible"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("page_url='%s'" % page_url)

    # Saca el código del vídeo
    data = httptools.downloadpage(page_url).data.replace("\\", "")
    video_urls = []

    if "tusfiles.org" in page_url:
        matches = scrapertools.find_multiple_matches(data,
                                                     '"label"\s*:\s*(.*?),"type"\s*:\s*"([^"]+)","file"\s*:\s*"([^"]+)"')
        for calidad, tipo, video_url in matches:
            tipo = tipo.replace("video/", "")
            video_urls.append([".%s %sp [tusfiles]" % (tipo, calidad), video_url])

        video_urls.sort(key=lambda it: int(it[0].split("p ", 1)[0].rsplit(" ")[1]))
    else:
        matches = scrapertools.find_multiple_matches(data, '<source src="([^"]+)" type="([^"]+)"')
        for video_url, tipo in matches:
            tipo = tipo.replace("video/", "")
            video_urls.append([".%s [tusfiles]" % tipo, video_url])

        id = scrapertools.find_single_match(data, 'name="id" value="([^"]+)"')
        rand = scrapertools.find_single_match(data, 'name="rand" value="([^"]+)"')
        if id and rand:
            post = "op=download2&id=%s&rand=%s&referer=&method_free=&method_premium=" % (id, rand)
            location = httptools.downloadpage(page_url, post, follow_redirects=False, only_headers=True).headers.get(
                "location")
            if location:
                ext = location[-4:]
                video_urls.append(["%s [tusfiles]" % ext, location])

    return video_urls
