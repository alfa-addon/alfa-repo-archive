# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()
    itemlist = []

    if item.url == "":
        item.url = "http://www.ecartelera.com/videos/"

    # ------------------------------------------------------
    # Descarga la página
    # ------------------------------------------------------
    data = scrapertools.cachePage(item.url)
    # logger.info(data)

    # ------------------------------------------------------
    # Extrae las películas
    # ------------------------------------------------------
    patron = '<div class="viditem"[^<]+'
    patron += '<div class="fimg"><a href="([^"]+)"><img alt="([^"]+)" src="([^"]+)"/><p class="length">([^<]+)</p></a></div[^<]+'
    patron += '<div class="fcnt"[^<]+'
    patron += '<h4><a[^<]+</a></h4[^<]+'
    patron += '<p class="desc">([^<]+)</p>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, duration, scrapedplot in matches:
        title = scrapedtitle + " (" + duration + ")"
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = scrapedplot.strip()

        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail,
                 plot=plot, server="directo", folder=False))

    # ------------------------------------------------------
    # Extrae la página siguiente
    # ------------------------------------------------------
    patron = '<a href="([^"]+)">Siguiente</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = "Pagina siguiente"
        scrapedurl = match
        scrapedthumbnail = ""
        scrapeddescription = ""

        # Añade al listado de XBMC
        itemlist.append(Item(channel=item.channel, action="mainlist", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot, server="directo", folder=True,
                             viewmode="movie_with_plot"))

    return itemlist


# Reproducir un vídeo
def play(item):
    logger.info()
    itemlist = []
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    logger.info(data)

    # Extrae las películas
    patron = '<source src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        url = urlparse.urljoin(item.url, matches[0])
        logger.info("url=" + url)
        itemlist.append(Item(channel=item.channel, action="play", title=item.title, url=url, thumbnail=item.thumbnail,
                             plot=item.plot, server="directo", folder=False))

    return itemlist
