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
    itemlist.append(
        Item(channel=item.channel, action="PorFecha", title="Año de Lanzamiento", url="http://www.peliculasrey.com"))
    itemlist.append(Item(channel=item.channel, action="Idiomas", title="Idiomas", url="http://www.peliculasrey.com"))
    itemlist.append(
        Item(channel=item.channel, action="calidades", title="Por calidad", url="http://www.peliculasrey.com"))
    itemlist.append(Item(channel=item.channel, action="generos", title="Por género", url="http://www.peliculasrey.com"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar...", url="http://www.peliculasrey.com"))

    return itemlist


def PorFecha(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data, '<section class="lanzamiento">(.*?)</section>')
    logger.info("data=" + data)

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+).*?title="([^"]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title, viewmode="movie"))

    return itemlist


def Idiomas(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data, '<section class="idioma">(.*?)</section>')
    logger.info("data=" + data)

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+).*?title="([^"]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title, viewmode="movie"))

    return itemlist


def calidades(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data, '<section class="calidades">(.*?)</section>')
    logger.info("data=" + data)

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+).*?title="([^"]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title, viewmode="movie"))

    return itemlist


def generos(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data, '<section class="generos">(.*?)</section>')
    logger.info("data=" + data)

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+).*?title="([^"]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title, viewmode="movie"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://www.peliculasrey.com/?s=" + texto

    try:
        # return buscar(item)
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    logger.info("data=" + data)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    tabla_pelis = scrapertools.find_single_match(data,
                                                 'class="section col-17 col-main grid-125 overflow clearfix">(.*?)</div></section>')
    patron = '<img src="([^"]+)" alt="([^"]+).*?href="([^"]+)'

    matches = re.compile(patron, re.DOTALL).findall(tabla_pelis)
    itemlist = []

    for scrapedthumbnail, scrapedtitle, scrapedurl in matches:
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(Item(channel=item.channel, action="findvideos", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot="", fulltitle=scrapedtitle))

    next_page = scrapertools.find_single_match(data, 'rel="next" href="([^"]+)')
    if next_page != "":
        #    itemlist.append( Item(channel=item.channel, action="peliculas" , title=">> Página siguiente" , url=item.url+next_page, folder=True, viewmode="movie"))
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=">> Página siguiente", url=next_page, folder=True,
                 viewmode="movie"))

    return itemlist


def findvideos(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    # logger.info("data="+data)

    # Extrae las entradas (carpetas)  
    patron = 'hand" rel="([^"]+).*?title="(.*?)".*?<span>([^<]+)</span>.*?</span><span class="q">(.*?)<'

    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, nombre_servidor, idioma, calidad in matches:
        idioma = idioma.strip()
        calidad = calidad.strip()

        title = "Ver en " + nombre_servidor + " (" + idioma + ") (Calidad " + calidad + ")"
        url = scrapedurl
        thumbnail = ""
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot,
                             folder=False))

    return itemlist


def play(item):
    logger.info("url=" + item.url)

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = item.channel

    return itemlist
