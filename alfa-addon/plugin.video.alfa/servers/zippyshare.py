# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    result = False
    message = ''
    try:
        error_message_file_not_exists = 'File does not exist on this server'
        error_message_file_deleted = 'File has expired and does not exist anymore on this server'

        data = httptools.downloadpage(page_url).data

        if error_message_file_not_exists in data:
            message = 'File does not exist.'
        elif error_message_file_deleted in data:
            message = 'File deleted.'
        else:
            result = True
    except Exception as ex:
        message = ex.message

    return result, message


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    match = re.search('(.+)/v/(\w+)/file.html', page_url)
    domain = match.group(1)

    patron = 'getElementById\(\'dlbutton\'\).href\s*=\s*(.*?);'
    media_url = scrapertools.find_single_match(data, patron)
    numbers = scrapertools.find_single_match(media_url, '\((.*?)\)')
    url = media_url.replace(numbers, "'%s'" % eval(numbers))
    url = eval(url)

    mediaurl = '%s%s' % (domain, url)
    extension = "." + mediaurl.split('.')[-1]
    video_urls.append([extension + " [zippyshare]", mediaurl])

    return video_urls
