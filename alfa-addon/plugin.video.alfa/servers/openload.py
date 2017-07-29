# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    header = {}
    if "|" in page_url:
        page_url, referer = page_url.split("|", 1)
        header = {'Referer': referer}
    data = httptools.downloadpage(page_url, headers=header, cookies=False).data
    if 'We’re Sorry!' in data:
        data = httptools.downloadpage(page_url.replace("/embed/", "/f/"), headers=header, cookies=False).data
        if 'We’re Sorry!' in data:
            return False, "[Openload] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []

    header = {}
    if "|" in page_url:
        page_url, referer = page_url.split("|", 1)
        header = {'Referer': referer}
    data = httptools.downloadpage(page_url, headers=header, cookies=False).data
    subtitle = scrapertools.find_single_match(data, '<track kind="captions" src="([^"]+)" srclang="es"')
    # Header para la descarga
    header_down = "|User-Agent=" + headers['User-Agent']

    try:
        from lib.aadecode import decode as aadecode
        if "videocontainer" not in data:
            url = page_url.replace("/embed/", "/f/")
            data = httptools.downloadpage(url, cookies=False).data

        text_encode = scrapertools.find_multiple_matches(data, '(ﾟωﾟ.*?\(\'\_\'\));')
        text_decode = ""
        for t in text_encode:
            text_decode += aadecode(t)

        var_r = scrapertools.find_single_match(text_decode, "window\.[A-z]+\s*=\s*['\"]([^'\"]+)['\"]")
        var_encodes = scrapertools.find_multiple_matches(data, 'id="%s[^"]*">([^<]+)<' % var_r)
        numeros = scrapertools.find_multiple_matches(data,
                                                     '_[A-f0-9]+x[A-f0-9]+\s*(?:=|\^)\s*([0-9]{4,}|0x[A-f0-9]{4,})')
        op1, op2 = scrapertools.find_single_match(data, '\(0x(\d),0x(\d)\);')

        videourl = ""
        for encode in var_encodes:
            text_decode = ""
            try:
                mult = int(op1) * int(op2)
                rango1 = encode[:mult]
                decode1 = []
                for i in range(0, len(rango1), 8):
                    decode1.append(int(rango1[i:i + 8], 16))
                rango1 = encode[mult:]
                j = 0
                i = 0
                while i < len(rango1):
                    index1 = 64
                    value1 = 0
                    value2 = 0
                    value3 = 0
                    while True:
                        if (i + 1) >= len(rango1):
                            index1 = 143
                        value3 = int(rango1[i:i + 2], 16)
                        i += 2
                        data = value3 & 63
                        value2 += data << value1
                        value1 += 6
                        if value3 < index1:
                            break

                    value4 = value2 ^ decode1[j % (mult / 8)]
                    for n in numeros:
                        if not n.isdigit():
                            n = int(n, 16)
                        value4 ^= int(n)
                    value5 = index1 * 2 + 127
                    for h in range(4):
                        valorfinal = (value4 >> 8 * h) & (value5)
                        valorfinal = chr(valorfinal - 1)
                        if valorfinal != "%":
                            text_decode += valorfinal
                    j += 1
            except:
                continue

            videourl = "https://openload.co/stream/%s?mime=true" % text_decode
            resp_headers = httptools.downloadpage(videourl, follow_redirects=False, only_headers=True)
            videourl = resp_headers.headers["location"].replace("https", "http").replace("?mime=true", "")
            extension = resp_headers.headers["content-type"]
            break

        # Falla el método, se utiliza la api aunque en horas punta no funciona
        if not videourl:
            videourl, extension = get_link_api(page_url)
    except:
        import traceback
        logger.info(traceback.format_exc())
        # Falla el método, se utiliza la api aunque en horas punta no funciona
        videourl, extension = get_link_api(page_url)

    extension = extension.replace("video/", ".").replace("application/x-", ".")
    if not extension:
        try:
            extension = scrapertools.find_single_match(data, '<meta name="description" content="([^"]+)"')
            extension = "." + extension.rsplit(".", 1)[1]
        except:
            pass

    if config.get_platform() != "plex":
        video_urls.append([extension + " [Openload] ", videourl + header_down, 0, subtitle])
    else:
        video_urls.append([extension + " [Openload] ", videourl, 0, subtitle])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls


def get_link_api(page_url):
    from core import jsontools
    file_id = scrapertools.find_single_match(page_url, '(?:embed|f)/([0-9a-zA-Z-_]+)')
    login = "97b2326d7db81f0f"
    key = "AQFO3QJQ"
    data = httptools.downloadpage(
        "https://api.openload.co/1/file/dlticket?file=%s&login=%s&key=%s" % (file_id, login, key)).data
    data = jsontools.load(data)

    if data["status"] == 200:
        ticket = data["result"]["ticket"]
        data = httptools.downloadpage("https://api.openload.co/1/file/dl?file=%s&ticket=%s" % (file_id, ticket)).data
        data = jsontools.load(data)
        extension = data["result"]["content_type"]
        videourl = data['result']['url']
        videourl = videourl.replace("https", "http")
        return videourl, extension

    return "", ""
