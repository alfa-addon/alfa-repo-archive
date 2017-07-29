# -*- coding: utf-8 -*-

from core import httptools
from core import logger
from core import scrapertools


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(action="categorias", title="Categorías", url="http://dato.porn/categories_all"))
    itemlist.append(item.clone(title="Buscar...", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    item.url = "http://dato.porn/?k=%s&op=search" % texto.replace(" ", "+")
    return lista(item)


def lista(item):
    logger.info()
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas
    patron = '<div class="vid_block">\s*<a href="([^"]+)".*?url\(\'([^\']+)\'.*?<span>(.*?)</span>.*?<b>(.*?)</b>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, duration, scrapedtitle in matches:
        if "/embed-" not in scrapedurl:
            scrapedurl = scrapedurl.replace("datoporn.com/", "datoporn.com/embed-") + ".html"
        if duration:
            scrapedtitle = "%s - %s" % (duration, scrapedtitle)

        itemlist.append(item.clone(action="play", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                                   server="datoporn", fanart=scrapedthumbnail.replace("_t.jpg", ".jpg")))

        # Extrae la marca de siguiente página
    next_page = scrapertools.find_single_match(data, "<a href='([^']+)'>Next")
    if next_page and itemlist:
        itemlist.append(item.clone(action="lista", title=">> Página Siguiente", url=next_page))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    # Descarga la pagina    
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<div class="vid_block">\s*<a href="([^"]+)".*?url\((.*?)\).*?<span>(.*?)</span>.*?<b>(.*?)</b>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, numero, scrapedtitle in matches:
        if numero:
            scrapedtitle = "%s  (%s)" % (scrapedtitle, numero)

        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail))

    return itemlist
