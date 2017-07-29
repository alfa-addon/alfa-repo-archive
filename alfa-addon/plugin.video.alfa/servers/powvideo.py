# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from lib import jsunpack

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0']]
host = "http://powvideo.net/"


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    if "<title>watch </title>" in data.lower():
        return False, "[powvideo] El archivo no existe o  ha sido borrado"
    if "el archivo ha sido borrado por no respetar" in data.lower():
        return False, "[powvideo] El archivo no existe o ha sido borrado por no respetar los Terminos de uso"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    url = page_url.replace(host, "http://powvideo.xyz/iframe-") + "-954x562.html"

    data = httptools.downloadpage(page_url, cookies=False)
    cookie = data.headers['set-cookie']
    data = data.data

    file_id, aff = scrapertools.find_single_match(data, "'file_id', '(\d+)',[^']+'aff', '(\d+)',")
    _cookie = {"Cookie": cookie.replace("path=/; HttpOnly", "file_id=" + file_id + "; aff=" + aff)}

    id = scrapertools.find_single_match(data, 'name="id" value="([^"]+)"')
    fname = scrapertools.find_single_match(data, 'name="fname" value="([^"]+)"')
    hash = scrapertools.find_single_match(data, 'name="hash" value="([^"]+)"')

    post = "op=download1&usr_login=&referer=&fname=%s&id=%s&hash=%s" % (fname, id, hash)

    import time
    time.sleep(7)
    data = httptools.downloadpage(page_url, post, headers=_cookie).data

    for list in scrapertools.find_multiple_matches(data, '_[^=]+=(\[[^\]]+\]);'):
        if len(list) == 703 or len(list) == 711:
            key = "".join(eval(list)[7:9])
            break
    if key.startswith("embed"):
        key = key[6:] + key[:6]
    matches = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")
    data = jsunpack.unpack(matches).replace("\\", "")

    data = scrapertools.find_single_match(data.replace('"', "'"), "sources\s*=[^\[]*\[([^\]]+)\]")
    matches = scrapertools.find_multiple_matches(data, "[src|file]:'([^']+)'")
    video_urls = []
    for video_url in matches:
        _hash = scrapertools.find_single_match(video_url, '[A-z0-9\_\-]{40,}')
        hash = decrypt(_hash, key)
        video_url = video_url.replace(_hash, hash)

        filename = scrapertools.get_filename_from_url(video_url)[-4:]
        if video_url.startswith("rtmp"):
            rtmp, playpath = video_url.split("vod/", 1)
            video_url = "%svod/ playpath=%s swfUrl=%splayer6/jwplayer.flash.swf pageUrl=%s" % \
                        (rtmp, playpath, host, page_url)
            filename = "RTMP"
        elif video_url.endswith(".m3u8"):
            video_url += "|User-Agent=" + headers[0][1]
        elif video_url.endswith("/v.mp4"):
            video_url_flv = re.sub(r'/v.mp4', '/v.flv', video_url)
            video_urls.append(["flv [powvideo]", video_url_flv])

        video_urls.append([filename + " [powvideo]", video_url])

    video_urls.sort(key=lambda x: x[0], reverse=True)
    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls


def decrypt(h, k):
    import base64

    if len(h) % 4:
        h += "=" * (4 - len(h) % 4)
    sig = []
    h = base64.b64decode(h.replace("-", "+").replace("_", "/"))
    for c in range(len(h)):
        sig += [ord(h[c])]

    sec = []
    for c in range(len(k)):
        sec += [ord(k[c])]

    dig = range(256)
    g = 0
    v = 128
    for b in range(len(sec)):
        a = (v + (sec[b] & 15)) % 256
        c = dig[(g)]
        dig[g] = dig[a]
        dig[a] = c
        g += 1

        a = (v + (sec[b] >> 4 & 15)) % 256
        c = dig[g]
        dig[g] = dig[a]
        dig[a] = c
        g += 1

    k = 0
    q = 1
    p = 0
    n = 0
    for b in range(512):
        k = (k + q) % 256
        n = (p + dig[(n + dig[k]) % 256]) % 256
        p = (k + p + dig[n]) % 256
        c = dig[k]
        dig[k] = dig[n]
        dig[n] = c

    q = 3
    for a in range(v):
        b = 255 - a
        if dig[a] > dig[b]:
            c = dig[a]
            dig[a] = dig[b]
            dig[b] = c

    k = 0
    for b in range(512):
        k = (k + q) % 256
        n = (p + dig[(n + dig[k]) % 256]) % 256
        p = (k + p + dig[n]) % 256
        c = dig[k]
        dig[k] = dig[n]
        dig[n] = c

    q = 5
    for a in range(v):
        b = 255 - a
        if dig[a] > dig[b]:
            c = dig[a]
            dig[a] = dig[b]
            dig[b] = c

    k = 0
    for b in range(512):
        k = (k + q) % 256
        n = (p + dig[(n + dig[k]) % 256]) % 256
        p = (k + p + dig[n]) % 256
        c = dig[k]
        dig[k] = dig[n]
        dig[n] = c

    q = 7
    k = 0
    u = 0
    d = []
    for b in range(len(dig)):
        k = (k + q) % 256
        n = (p + dig[(n + dig[k]) % 256]) % 256
        p = (k + p + dig[n]) % 256
        c = dig[k]
        dig[k] = dig[n]
        dig[n] = c
        u = dig[(n + dig[(k + dig[(u + p) % 256]) % 256]) % 256]
        d += [u]

    c = []
    for f in range(len(d)):
        try:
            c += [(256 + (sig[f] - d[f])) % 256]
        except:
            break

    h = ""
    for s in c:
        h += chr(s)

    return h
