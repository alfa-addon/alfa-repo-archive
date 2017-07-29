# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    if "File was deleted" in data:
        return False, "El archivo no existe<br/>en streaminto o ha sido borrado."
    elif "Video is processing now" in data:
        return False, "El archivo está siendo procesado<br/>Prueba dentro de un rato."
    else:
        return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = re.sub(r'\n|\t|\s+', '', httptools.downloadpage(page_url).data)

    video_urls = []
    try:
        media_url = scrapertools.get_match(data, """.setup\({file:"([^"]+)",image""")
    except:
        js_data = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e.*?)</script>")
        js_data = unPack(js_data)
        media_url = scrapertools.get_match(js_data, """.setup\({file:"([^"]+)",image""")

    if media_url.endswith("v.mp4"):
        media_url_mp42flv = re.sub(r'/v.mp4$', '/v.flv', media_url)
        video_urls.append(
            [scrapertools.get_filename_from_url(media_url_mp42flv)[-4:] + " [streaminto]", media_url_mp42flv])
    if media_url.endswith("v.flv"):
        media_url_flv2mp4 = re.sub(r'/v.flv$', '/v.mp4', media_url)
        video_urls.append(
            [scrapertools.get_filename_from_url(media_url_flv2mp4)[-4:] + " [streaminto]", media_url_flv2mp4])
    video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [streaminto]", media_url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls


def unPack(packed):
    pattern = "}\('(.*)', *(\d+), *(\d+), *'(.*)'\.split\('([^']+)'\)"
    d = [d for d in re.search(pattern, packed, re.DOTALL).groups()]

    p = d[0];
    a = int(d[1]);
    c = int(d[2]);
    k = d[3].split(d[4])

    if a <= 62:
        toString = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    else:
        toString = """ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"""

    def e(c):
        return toString[c] if c < a else toString[c // a] + toString[c % a]

    while c > 0:
        c -= 1
        if k[c]:
            x = e(c)
        else:
            x = k[c]
        y = k[c]
        p = re.sub(r"(\b%s\b)" % x, y, p)

    return p
