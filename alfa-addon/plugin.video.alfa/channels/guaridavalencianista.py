# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Novedades", action="listvideos",
                         url="http://guaridavalencia.blogspot.com.es"))
    # itemlist.append( Item(channel=item.channel, title="Documentales - Series Disponibles"  , action="DocuSeries" , url="http://guaridavalencia.blogspot.com/"))
    itemlist.append(
        Item(channel=item.channel, title="Categorias", action="DocuTag", url="http://guaridavalencia.blogspot.com.es"))
    itemlist.append(Item(channel=item.channel, title="Partidos de liga (Temporada 2014/2015)", action="listvideos",
                         url="http://guaridavalencia.blogspot.com.es/search/label/PARTIDOS%20DEL%20VCF%20%28TEMPORADA%202014-15%29"))

    return itemlist


def DocuSeries(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patronvideos = '<li><b><a href="([^"]+)" target="_blank">([^<]+)</a></b></li>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = ""
        scrapedplot = ""
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(Item(channel=item.channel, action="listvideos", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))

    return itemlist


def DocuTag(item):
    logger.info()
    itemlist = []
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    # ~ patronvideos  =    "<a dir='ltr' href='([^']+)'>([^<]+)</a>[^<]+<span class='label-count' dir='ltr'>(.+?)</span>"
    patronvideos = "<li[^<]+<a dir='ltr' href='([^']+)'>([^<]+)</a[^<]+<span dir='ltr'>[^0-9]+([0-9]+)[^<]+</span[^<]+</li[^<]+"
    # ~ patronvideos  =    "<li[^<]+<a dir='ltr' href='([^']+)'[^<]+([^<]+)</a>"
    # ~ [^<]+<span class='label-count' dir='ltr'>(.+?)</span>"
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedurl = match[0]
        # Se debe quitar saltos de linea en match[1]
        scrapedtitle = match[1][1:-1] + " (" + match[2] + ")"
        # ~ scrapedtitle = match[1]
        scrapedthumbnail = ""
        scrapedplot = ""
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(Item(channel=item.channel, action="listvideos", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))

    return itemlist


def DocuARCHIVO(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    patronvideos = "<a class='post-count-link' href='([^']+)'>([^<]+)</a>[^<]+"
    patronvideos += "<span class='post-count' dir='ltr'>(.+?)</span>"
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[1] + " " + match[2]
        scrapedthumbnail = ""
        scrapedplot = ""
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(Item(channel=item.channel, action="listvideos", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))

    return itemlist


def listvideos(item):
    logger.info()
    itemlist = []

    scrapedthumbnail = ""
    scrapedplot = ""

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    patronvideos = "<h3 class='post-title entry-title'[^<]+"
    patronvideos += "<a href='([^']+)'>([^<]+)</a>.*?"
    patronvideos += "<div class='post-body entry-content'(.*?)<div class='post-footer'>"
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = match[1]
        scrapedtitle = re.sub("<[^>]+>", " ", scrapedtitle)
        scrapedtitle = scrapertools.unescape(scrapedtitle)[1:-1]
        scrapedurl = match[0]
        regexp = re.compile(r'src="(http[^"]+)"')

        matchthumb = regexp.search(match[2])
        if matchthumb is not None:
            scrapedthumbnail = matchthumb.group(1)
        matchplot = re.compile('<div align="center">(<img.*?)</span></div>', re.DOTALL).findall(match[2])

        if len(matchplot) > 0:
            scrapedplot = matchplot[0]
            # print matchplot
        else:
            scrapedplot = ""

        scrapedplot = re.sub("<[^>]+>", " ", scrapedplot)
        scrapedplot = scrapertools.unescape(scrapedplot)
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(Item(channel=item.channel, action="findvideos", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))

    # Extrae la marca de siguiente página
    patronvideos = "<a class='blog-pager-older-link' href='([^']+)'"
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        scrapedtitle = "Página siguiente"
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(Item(channel=item.channel, action="listvideos", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))

    return itemlist

    # ~ return itemlist


def findvideos(item):
    logger.info()
    data = scrapertools.cachePage(item.url)

    # Busca los enlaces a los videos

    listavideos = servertools.findvideos(data)

    if item is None:
        item = Item()

    itemlist = []
    for video in listavideos:
        scrapedtitle = video[0].strip() + " - " + item.title.strip()
        scrapedurl = video[1]
        server = video[2]

        itemlist.append(Item(channel=item.channel, title=scrapedtitle, action="play", server=server, url=scrapedurl,
                             thumbnail=item.thumbnail, show=item.show, plot=item.plot, folder=False))

    return itemlist
