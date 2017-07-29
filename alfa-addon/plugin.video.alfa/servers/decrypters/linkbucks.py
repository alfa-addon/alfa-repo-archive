# -*- coding: utf-8 -*-

import urllib

from core import logger
from core import scrapertools


# Obtiene la URL que hay detrás de un enlace a linkbucks
def get_long_url(short_url):
    logger.info("(short_url='%s')" % short_url)

    request_headers = []
    request_headers.append(["User-Agent",
                            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"])
    request_headers.append(["Referer", "http://linkdecrypter.com"])
    post = urllib.urlencode({"pro_links": short_url, "modo_links": "text", "modo_recursivo": "on", "link_cache": "on"})
    url = "http://linkdecrypter.com/"

    # Parche porque python no parece reconocer bien la cabecera phpsessid
    body, response_headers = scrapertools.read_body_and_headers(url, post=post, headers=request_headers)
    location = ""
    n = 1
    while True:
        for name, value in response_headers:
            if name == "set-cookie":
                logger.info("Set-Cookie: " + value)
                cookie_name = scrapertools.get_match(value, '(.*?)\=.*?\;')
                cookie_value = scrapertools.get_match(value, '.*?\=(.*?)\;')
                request_headers.append(["Cookie", cookie_name + "=" + cookie_value])

        body, response_headers = scrapertools.read_body_and_headers(url, headers=request_headers)
        logger.info("body=" + body)

        try:
            location = scrapertools.get_match(body, '<textarea.*?class="caja_des">([^<]+)</textarea>')
            logger.info("location=" + location)
            break
        except:
            n = n + 1
            if n > 3:
                break

    return location
