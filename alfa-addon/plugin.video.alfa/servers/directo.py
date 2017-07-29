# -*- coding: utf-8 -*-

import re

from core import logger


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    video_urls = [["%s [directo]" % page_url[-4:], page_url]]

    return video_urls
