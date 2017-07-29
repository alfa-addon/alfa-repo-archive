# -*- coding: utf-8 -*-

import re
import sys

from core import httptools
from core import logger
from core import scrapertools
from core.item import Item

thumbnail_host = 'https://github.com/master-1970/resources/raw/master/images/squares/pelis24.PNG'


def mainlist(item):
    logger.info()
    itemlist = []
    item.thumbnail = thumbnail_host
    item.action = "peliculas"
    itemlist.append(item.clone(title="Novedades", url="http://www.pelis24.tv/ultimas-peliculas/"))
    itemlist.append(item.clone(title="Estrenos", url="http://pelis24.tv/estrenos/"))
    itemlist.append(item.clone(title="", folder=False))
    itemlist.append(item.clone(title="Castellano", url="http://pelis24.tv/pelicula-ca/"))
    itemlist.append(item.clone(title="Latino", url="http://pelis24.tv/pelicula-latino/"))
    itemlist.append(item.clone(title="Versión original", url="http://pelis24.tv/peliculasvo/"))
    itemlist.append(item.clone(title="Versión original subtitulada", url="http://pelis24.tv/peliculasvose/"))

    itemlist.append(item.clone(title="", folder=False))
    itemlist.append(item.clone(title="Filtrar por género", action="genero", url="http://pelis24.tv/tags/"))
    itemlist.append(item.clone(title="Buscar", action="search", url="http://www.pelis24.tv/"))
    return itemlist


def newest(categoria):
    logger.info()
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = "http://www.pelis24.tv/ultimas-peliculas/"
        elif categoria == 'infantiles':
            item.url = "http://pelis24.tv/tags/Infantil/"
        else:
            return []

        itemlist = peliculas(item)
        if itemlist[-1].title == ">> Página siguiente":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.extra = texto
        return buscar(item)
    # Se captura la excepci?n, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def buscar(item):
    itemlist = []
    if not item.page:
        item.page = 1

    url = "http://pelis24.tv/index.php?do=search&subaction=search&search_start=%s&story=%s" % (
    item.page, item.extra.replace(" ", "+"))

    data = httptools.downloadpage(url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<a class="sres-wrap clearfix" href="([^"]+).*?'
    patron += '<img src="([^"]+)" alt="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumbnail, title in matches:
        if "/series/" in url:
            # Descartamos las series
            continue

        if not thumbnail.startswith("http"):
            thumbnail = "http://www.pelis24.tv" + thumbnail
        contentTitle = title.split("/")[0]

        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=contentTitle, url=url, thumbnail=thumbnail,
                 contentTitle=contentTitle))

    if itemlist:
        itemlist.append(item.clone(title=">> Página siguiente", action="buscar", thumbnail=thumbnail_host,
                                   page=item.page + 1))

    return itemlist


def genero(item):
    logger.info()
    itemlist = []
    generos = ["Animación", "Aventuras", "Bélico", "Ciencia+ficción", "Crimen", "Comedia",
               "Deporte", "Drama", "Fantástico", "Infantil", "Musical", "Romance", "Terror", "Thriller"]

    for g in generos:
        itemlist.append(Item(channel=item.channel, action="peliculas", title=g.replace('+', ' '),
                             thumbnail=thumbnail_host, url=item.url + g + "/"))

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    data = scrapertools.find_single_match(data, "dle-content(.*?)not-main clearfix")

    patron = '<div class="movie-img img-box">.*?'
    patron += '<img src="([^"]+).*?'
    patron += 'href="([^"]+).*?'
    patron += '<div class="movie-series">([^<]+)</div>'
    patron += '<span><a href=[^>]+>([^<]+)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for thumbnail, url, title, quality in matches:
        if "/series/" in url:
            # Descartamos las series
            continue

        if not thumbnail.startswith("http"):
            thumbnail = "http://www.pelis24.tv" + thumbnail
        contentTitle = title.split("/")[0]
        title = "%s (%s)" % (contentTitle, quality)

        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                 contentQuality=quality, contentTitle=contentTitle))

    # Extrae el paginador
    next_page = scrapertools.find_single_match(data, '<span class="pnext"><a href="([^"]+)')
    if next_page:
        itemlist.append(Item(channel=item.channel, action="peliculas", title=">> Página siguiente",
                             thumbnail=thumbnail_host, url=next_page))

    return itemlist
