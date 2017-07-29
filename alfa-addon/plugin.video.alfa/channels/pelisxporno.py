# -*- coding: utf-8 -*-

from core import httptools
from core import logger
from core import scrapertools


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(item.clone(action="lista", title="Novedades", url="http://www.pelisxporno.com/?order=date"))
    itemlist.append(item.clone(action="categorias", title="Categorías", url="http://www.pelisxporno.com/categorias/"))
    itemlist.append(item.clone(action="search", title="Buscar", url="http://www.pelisxporno.com/?s=%s"))

    return itemlist


def search(item, texto):
    logger.info()
    item.url = item.url % texto
    return lista(item)


def lista(item):
    logger.info()
    itemlist = []

    # Descarga la pagina  
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<div class="Picture">.*?href="([^"]+)".*?<img src="([^"]+)".*?' \
             '<span class="fa-clock.*?>([^<]+)<.*?<h2 class="Title">.*?>([^<]+)</a>' \
             '.*?<p>(.*?)</p>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, duration, scrapedtitle, plot in matches:
        if duration:
            scrapedtitle += "  (%s)" % duration

        itemlist.append(item.clone(action="findvideos", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                                   infoLabels={'plot': plot}))

    # Extrae la marca de siguiente página
    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)"')
    if next_page:
        itemlist.append(item.clone(action="lista", title=">> Página Siguiente", url=next_page))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    # Descarga la pagina  
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<figure class="Picture">.*?<a href="([^"]+)".*?src="([^"]+)".*?<a.*?>(.*?)</a>' \
             '.*?<span class="fa-film Clr3B">(\d+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, cantidad in matches:
        if cantidad:
            scrapedtitle += " (%s vídeos)" % cantidad
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail))

    return itemlist
