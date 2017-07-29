# -*- coding: utf-8 -*-

from base64 import b64decode

from core import logger
from core import scrapertools


def get_long_url(short_url):
    logger.info("short_url = '%s'" % short_url)

    data = scrapertools.downloadpage(short_url)
    ysmm = scrapertools.find_single_match(data, "var ysmm = '([^']+)';")
    b64 = ""
    for i in reversed(range(len(ysmm))):
        if i % 2:
            b64 = b64 + ysmm[i]
        else:
            b64 = ysmm[i] + b64

    decoded_uri = b64decode(b64)[2:]

    if "adf.ly/redirecting" in decoded_uri:
        data = scrapertools.downloadpage(decoded_uri)
        decoded_uri = scrapertools.find_single_match(data, "window.location = '([^']+)'")

    return decoded_uri
