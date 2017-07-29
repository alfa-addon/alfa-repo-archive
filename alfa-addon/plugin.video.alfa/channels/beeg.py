# -*- coding: utf-8 -*-

import re
import urllib

from core import jsontools as json
from core import logger
from core import scrapertools
from core.item import Item

url_api = ""
beeg_salt = ""


def get_api_url():
    global url_api
    global beeg_salt
    data = scrapertools.downloadpage("http://beeg.com")
    version = re.compile('<script src="//static.beeg.com/cpl/([\d]+).js"').findall(data)[0]
    js_url = "http:" + re.compile('<script src="(//static.beeg.com/cpl/[\d]+.js)"').findall(data)[0]
    url_api = "https://api2.beeg.com/api/v6/" + version
    data = scrapertools.downloadpage(js_url)
    beeg_salt = re.compile('beeg_salt="([^"]+)"').findall(data)[0]


def decode(key):
    a = beeg_salt
    e = unicode(urllib.unquote(key), "utf8")
    t = len(a)
    o = ""
    for n in range(len(e)):
        r = ord(e[n:n + 1])
        i = n % t
        s = ord(a[i:i + 1]) % 21
        o += chr(r - s)

    n = []
    for x in range(len(o), 0, -3):
        if x >= 3:
            n.append(o[(x - 3):x])
        else:
            n.append(o[0:x])

    return "".join(n)


get_api_url()


def mainlist(item):
    logger.info()
    get_api_url()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="videos", title="Útimos videos", url=url_api + "/index/main/0/pc",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="listcategorias", title="Listado categorias",
                         url=url_api + "/index/main/0/pc"))
    itemlist.append(
        Item(channel=item.channel, action="search", title="Buscar", url=url_api + "/index/search/0/pc?query=%s"))
    return itemlist


def videos(item):
    logger.info()
    itemlist = []
    data = scrapertools.cache_page(item.url)
    JSONData = json.load(data)

    for Video in JSONData["videos"]:
        thumbnail = "http://img.beeg.com/236x177/" + Video["id"] + ".jpg"
        url = url_api + "/video/" + Video["id"]
        title = Video["title"]
        itemlist.append(
            Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail, plot="", show="",
                 folder=True))

    # Paginador
    Actual = int(scrapertools.get_match(item.url, url_api + '/index/[^/]+/([0-9]+)/pc'))
    if JSONData["pages"] - 1 > Actual:
        scrapedurl = item.url.replace("/" + str(Actual) + "/", "/" + str(Actual + 1) + "/")
        itemlist.append(
            Item(channel=item.channel, action="videos", title="Página Siguiente", url=scrapedurl, thumbnail="",
                 folder=True, viewmode="movie"))

    return itemlist


def listcategorias(item):
    logger.info()
    itemlist = []
    data = scrapertools.cache_page(item.url)
    JSONData = json.load(data)

    for Tag in JSONData["tags"]["popular"]:
        url = url_api + "/index/tag/0/pc?tag=" + Tag
        title = Tag
        title = title[:1].upper() + title[1:]
        itemlist.append(
            Item(channel=item.channel, action="videos", title=title, url=url, folder=True, viewmode="movie"))

    return itemlist


def search(item, texto):
    logger.info()

    texto = texto.replace(" ", "+")
    item.url = item.url % (texto)
    try:
        return videos(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def play(item):
    logger.info()
    itemlist = []
    data = scrapertools.downloadpage(item.url)

    JSONData = json.load(data)
    for key in JSONData:
        videourl = re.compile("([0-9]+p)", re.DOTALL).findall(key)
        if videourl:
            videourl = videourl[0]
            if not JSONData[videourl] == None:
                url = JSONData[videourl]
                url = url.replace("{DATA_MARKERS}", "data=pc.ES")
                viedokey = re.compile("key=(.*?)%2Cend=", re.DOTALL).findall(url)[0]

                url = url.replace(viedokey, decode(viedokey))
                if not url.startswith("https:"): url = "https:" + url
                title = videourl
                itemlist.append(["%s %s [directo]" % (title, url[-4:]), url])

    itemlist.sort(key=lambda item: item[0])
    return itemlist
