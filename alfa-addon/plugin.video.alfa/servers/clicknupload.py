# -*- coding: utf-8 -*-

import re
import urllib

from core import httptools
from core import logger
from core import scrapertools

token = ""
excption = False


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = get_data(page_url.replace(".org", ".me"))
    if "File Not Found" in data: return False, "[Clicknupload] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = get_data(page_url.replace(".org", ".me"))

    post = ""
    block = scrapertools.find_single_match(data, '(?i)<Form method="POST"(.*?)</Form>')
    matches = scrapertools.find_multiple_matches(block, 'input.*?name="([^"]+)".*?value="([^"]*)"')
    for inputname, inputvalue in matches:
        post += inputname + "=" + inputvalue + "&"
    post = post.replace("download1", "download2")

    data = get_data(page_url, post)

    video_urls = []
    media = scrapertools.find_single_match(data, "onClick=\"window.open\('([^']+)'")
    # Solo es necesario codificar la ultima parte de la url
    url_strip = urllib.quote(media.rsplit('/', 1)[1])
    media_url = media.rsplit('/', 1)[0] + "/" + url_strip
    video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [clicknupload]", media_url])
    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls


def get_data(url_orig, req_post=""):
    try:
        if not excption:
            response = httptools.downloadpage(url_orig, req_post)
            if not response.data or "urlopen error [Errno 1]" in str(response.code):
                global excption
                excption = True
                raise Exception
            return response.data
        else:
            raise Exception
    except:
        import urllib
        post = {"address": url_orig.replace(".me", ".org")}
        if req_post:
            post["options"] = [{"man": "--data", "attribute": req_post}]
        else:
            post["options"] = []
        from core import jsontools
        global token
        if not token:
            data = httptools.downloadpage("http://onlinecurl.com/").data
            token = scrapertools.find_single_match(data, '<meta name="csrf-token" content="([^"]+)"')

        headers = {'X-Requested-With': 'XMLHttpRequest', 'X-CSRF-Token': token, 'Referer': 'http://onlinecurl.com/'}
        post = "curl_request=" + urllib.quote(jsontools.dump(post)) + "&email="
        response = httptools.downloadpage("http://onlinecurl.com/onlinecurl", post=post, headers=headers).data
        data = jsontools.load(response).get("body", "")

        return data
