# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()

    if item.url == "":
        item.url = "http://www.peliculaseroticas.net/"

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Extrae las entradas de la pagina seleccionada
    patron = '<div class="post"[^<]+'
    patron += '<a href="([^"]+)">([^<]+)</a[^<]+'
    patron += '<hr[^<]+'
    patron += '<a[^<]+<img src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        plot = ""

        # Añade al listado
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url, thumbnail=thumbnail,
                 plot=plot, viewmode="movie", folder=True))

    # Extrae la marca de siguiente página
    if item.url == "http://www.peliculaseroticas.net/":
        next_page_url = "http://www.peliculaseroticas.net/cine-erotico/2.html"
    else:
        current_page = scrapertools.find_single_match(item.url, "(\d+)")
        next_page = int(current_page) + 1
        next_page_url = "http://www.peliculaseroticas.net/cine-erotico/" + str(next_page) + ".html"

    itemlist.append(
        Item(channel=item.channel, action="peliculas", title=">> Página siguiente", url=next_page_url, folder=True))

    return itemlist
