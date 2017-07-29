# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.cache_page(url=page_url)
    if "<b>File Not Found</b>" in data:
        return False, "El archivo no existe<br/>en filebox o ha sido borrado."
    else:
        return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    '''
    <input type="hidden" name="op" value="download2">
    <input type="hidden" name="id" value="235812b1j9w1">
    <input type="hidden" name="rand" value="na73zeeooqyfkndsv4uxzzpbajwi6mhbmixtogi">
    <input type="hidden" name="referer" value="http://www.seriesyonkis.com/s/ngo/2/5/1/8/773">
    '''
    logger.info("URL")
    data = scrapertools.cache_page(page_url)
    import time
    time.sleep(5)

    codigo = scrapertools.get_match(data, '<input type="hidden" name="id" value="([^"]+)">[^<]+')
    rand = scrapertools.get_match(data, '<input type="hidden" name="rand" value="([^"]+)">')

    # op=download2&id=xuquejiv6xdf&rand=r6dq7hn7so2ygpnxv2zg2i3cu3sbdsunf57gtni&referer=&method_free=&method_premium=&down_direct=1
    post = "op=download2&id=" + codigo + "&rand=" + rand + "&referer=&method_free=&method_premium=&down_direct=1"

    data = scrapertools.cache_page(page_url, post=post, headers=[
        ['User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'],
        ['Referer', page_url]])
    logger.info("data=" + data)
    media_url = scrapertools.get_match(data, "this.play\('([^']+)'")
    video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [filebox]", media_url])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
