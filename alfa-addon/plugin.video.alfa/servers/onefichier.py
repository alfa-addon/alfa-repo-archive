# -*- coding: utf-8 -*-

import re
import urllib

from core import config
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    if config.get_setting("premium", server="onefichier") == True:
        user = config.get_setting("user", server="onefichier")
        password = config.get_setting("password", server="onefichier")

        url = "https://1fichier.com/login.pl"
        logger.info("url=" + url)
        post_parameters = {"mail": user, "pass": password, "lt": "on", "purge": "on", "valider": "Send"}
        post = urllib.urlencode(post_parameters)
        logger.info("post=" + post)

        data = scrapertools.cache_page(url, post=post)
        # logger.info("data="+data)

        cookies = config.get_cookie_data()
        logger.info("cookies=" + cookies)

        # 1fichier.com   TRUE    /   FALSE   1443553315  SID imC3q8MQ7cARw5tkXeWvKyrH493rR=1yvrjhxDAA0T0iEmqRfNF9GXwjrwPHssAQ
        sid_cookie_value = scrapertools.find_single_match(cookies, "1fichier.com.*?SID\s+([A-Za-z0-9\+\=]+)")
        logger.info("sid_cookie_value=" + sid_cookie_value)

        # .1fichier.com  TRUE    /   FALSE   1443553315  SID imC3q8MQ7cARw5tkXeWvKyrH493rR=1yvrjhxDAA0T0iEmqRfNF9GXwjrwPHssAQ
        cookie = urllib.urlencode({"SID": sid_cookie_value})

        # Averigua el nombre del fichero real
        headers = []
        headers.append(['User-Agent',
                        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'])
        headers.append(['Cookie', cookie])
        filename = scrapertools.get_header_from_response(page_url, header_to_get="Content-Disposition")
        logger.info("filename=" + filename)

        # Construye la URL final para Kodi
        location = page_url + "|Cookie=" + cookie
        logger.info("location=" + location)

        video_urls = []
        video_urls.append([filename[-4:] + " (Premium) [1fichier]", location])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
