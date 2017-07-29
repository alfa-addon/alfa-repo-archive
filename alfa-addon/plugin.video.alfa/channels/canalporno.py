# -*- coding: utf-8 -*-

from core import httptools
from core import logger
from core import scrapertools

host = "http://www.canalporno.com"


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(action="findvideos", title="Útimos videos", url=host))
    itemlist.append(item.clone(action="categorias", title="Listado Categorias",
                               url=host + "/categorias"))
    itemlist.append(item.clone(action="search", title="Buscar", url=host + "/search/?q=%s"))
    return itemlist


def search(item, texto):
    logger.info()

    try:
        item.url = item.url % texto
        itemlist = findvideos(item)
        return sorted(itemlist, key=lambda it: it.title)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<img src="([^"]+)".*?alt="([^"]+)".*?<h2><a href="([^"]+)">.*?' \
             '<div class="duracion"><span class="ico-duracion sprite"></span> ([^"]+) min</div>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for thumbnail, title, url, time in matches:
        scrapedtitle = time + " - " + title
        scrapedurl = host + url
        scrapedthumbnail = "http:" + thumbnail
        itemlist.append(item.clone(action="play", title=scrapedtitle, url=scrapedurl,
                                   thumbnail=scrapedthumbnail))

    patron = '<div class="paginacion">.*?<span class="selected">.*?<a href="([^"]+)">([^"]+)</a>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, title in matches:
        url = host + url
        title = "Página %s" % title
        itemlist.append(item.clone(action="findvideos", title=title, url=url))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_single_match(data, '<ul class="ordenar-por ordenar-por-categoria">'
                                                  '(.*?)<div class="publis-bottom">')

    patron = '<div class="muestra-categorias">.*?<a class="thumb" href="([^"]+)".*?<img class="categorias" src="([^"]+)".*?<div class="nombre">([^"]+)</div>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for url, thumbnail, title in matches:
        url = host + url
        thumbnail = "http:" + thumbnail
        itemlist.append(item.clone(action="findvideos", title=title, url=url, thumbnail=thumbnail))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    url = "http:" + scrapertools.find_single_match(data, '<source src="([^"]+)"')
    itemlist.append(item.clone(url=url, server="directo"))

    return itemlist
