# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="lista", title="Útimos videos",
                         url="http://www.ero-tik.com/newvideos.html?&page=1"))
    itemlist.append(
        Item(channel=item.channel, action="categorias", title="Categorias", url="http://www.ero-tik.com/browse.html"))
    itemlist.append(Item(channel=item.channel, action="lista", title="Top ultima semana",
                         url="http://www.ero-tik.com/topvideos.html?do=recent"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar",
                         url="http://www.ero-tik.com/search.php?keywords="))

    return itemlist


def search(item, texto):
    logger.info()

    texto = texto.replace(" ", "+")
    item.url = "{0}{1}".format(item.url, texto)
    try:
        return lista(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)
    patron = '<div class="pm-li-category"><a href="([^"]+)">.*?.<h3>(.*?)</h3></a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, actriz in matches:
        itemlist.append(Item(channel=item.channel, action="listacategoria", title=actriz, url=url))

    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    # Extrae las entradas de la pagina seleccionada
    patron = '<li><div class=".*?<a href="([^"]+)".*?>.*?.img src="([^"]+)".*?alt="([^"]+)".*?>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        title = scrapedtitle.strip()

        # Añade al listado
        itemlist.append(Item(channel=item.channel, action="play", thumbnail=thumbnail, fanart=thumbnail, title=title,
                             fulltitle=title, url=url,
                             viewmode="movie", folder=True))

    paginacion = scrapertools.find_single_match(data,
                                                '<li class="active"><a href="#" onclick="return false;">\d+</a></li><li class=""><a href="([^"]+)">')

    if paginacion:
        itemlist.append(Item(channel=item.channel, action="lista", title=">> Página Siguiente",
                             url="http://ero-tik.com/" + paginacion))

    return itemlist


def listacategoria(item):
    logger.info()
    itemlist = []
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    # Extrae las entradas de la pagina seleccionada
    patron = '<li><div class=".*?<a href="([^"]+)".*?>.*?.img src="([^"]+)".*?alt="([^"]+)".*?>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        title = scrapedtitle.strip()

        # Añade al listado
        itemlist.append(
            Item(channel=item.channel, action="play", thumbnail=thumbnail, title=title, fulltitle=title, url=url,
                 viewmode="movie", folder=True))

    paginacion = scrapertools.find_single_match(data,
                                                '<li class="active"><a href="#" onclick="return false;">\d+</a></li><li class=""><a href="([^"]+)">')

    if paginacion:
        itemlist.append(
            Item(channel=item.channel, action="listacategoria", title=">> Página Siguiente", url=paginacion))

    return itemlist


def play(item):
    logger.info()
    itemlist = []
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.unescape(data)
    logger.info(data)
    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = item.channel
        videoitem.action = "play"
        videoitem.folder = False
        videoitem.title = item.title

    return itemlist
