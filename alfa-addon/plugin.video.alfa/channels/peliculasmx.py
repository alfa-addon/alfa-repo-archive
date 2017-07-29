# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(
        Item(channel=item.channel, title="Últimas añadidas", action="peliculas", url="http://www.peliculasmx.net/"))
    itemlist.append(
        Item(channel=item.channel, title="Últimas por género", action="generos", url="http://www.peliculasmx.net/"))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url="http://www.peliculasmx.net/"))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # <li class="cat-item cat-item-3"><a href="http://peliculasmx.net/category/accion/" >Accion</a> <span>246</span>
    patron = '<li class="cat-item cat-item-.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '>([^<]+).*?'
    patron += '<span>([^<]+)'

    matches = re.compile(patron, re.DOTALL).findall(data)
    logger.debug(matches)
    for match in matches:
        scrapedurl = urlparse.urljoin("", match[0])
        scrapedtitle = match[1].strip() + ' [' + match[2] + ']'

        itemlist.append(Item(channel=item.channel, action="peliculas", title=scrapedtitle, url=scrapedurl, folder=True))

    itemlist = sorted(itemlist, key=lambda Item: Item.title)
    return itemlist


def peliculas(item):
    logger.info()
    extra = item.extra
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    patron = '<div id="mt-.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<span class="tt">([^<]+).*?'
    patron += '<span class="calidad2">([^<]+)'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        scrapedurl = match[0]  # urlparse.urljoin("",match[0])
        scrapedtitle = match[2] + ' [' + match[3] + ']'
        scrapedthumbnail = match[1]
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=scrapedtitle, fulltitle=scrapedtitle, url=scrapedurl,
                 thumbnail=scrapedthumbnail, folder=True))

    # Extrae la marca de siguiente página
    paginador = scrapertools.find_single_match(data, "<div class='paginado'>.*?lateral")

    patron = "<li.*?<a class='current'>.*?href='([^']+)"
    scrapedurl = scrapertools.find_single_match(paginador, patron)

    if scrapedurl:
        scrapedtitle = "!Pagina Siguiente ->"
        itemlist.append(Item(channel=item.channel, action="peliculas", title=scrapedtitle, url=scrapedurl, folder=True))

    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []

    texto = texto.replace(" ", "+")
    try:
        # Series
        item.url = "http://www.peliculasmx.net/?s=%s" % texto
        itemlist.extend(peliculas(item))
        itemlist = sorted(itemlist, key=lambda Item: Item.title)

        return itemlist

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
