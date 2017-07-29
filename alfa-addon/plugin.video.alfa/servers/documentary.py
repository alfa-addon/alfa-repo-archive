# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)

    try:
        # var videoVars = {"videoNonceVar":"94767795ce","post_id":"2835"};
        videoNonceVar = scrapertools.get_match(data,
                                               'var\s*videoVars\s*\=\s*\{"videoNonceVar"\:"([^"]+)","post_id"\:"\d+"')
        post_id = scrapertools.get_match(data, 'var\s*videoVars\s*\=\s*\{"videoNonceVar"\:"[^"]+","post_id"\:"(\d+)"')

        # http://documentary.es/wp-admin/admin-ajax.php?postId=2835&videoNonce=94767795ce&action=getVideo&_=1385893877929
        import random
        url = "http://documentary.es/wp-admin/admin-ajax.php?postId=" + post_id + "&videoNonce=" + videoNonceVar + "&action=getVideo&_=" + str(
            random.randint(10000000000, 9999999999999))
        data = scrapertools.cache_page(url)

        # {"videoUrl":"http:\/\/www.dailymotion.com\/embed\/video\/xioggh?autoplay=1&defaultSubtitle=es"}
        data = data.replace("\\", "")
    except:
        pass

    from core import servertools
    real_urls = servertools.find_video_items(data=data)
    if len(real_urls) > 0:
        item = real_urls[len(real_urls) - 1]
        servermodule = __import__('servers.%s' % item.server, None, None, ["servers.%s" % item.server])
        # exec "import " + item.server
        # exec "servermodule = " + item.server
        video_urls = servermodule.get_video_url(item.url)

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
