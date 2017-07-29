# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="lista", title="Útimos videos", url="http://www.vidz7.com/"))
    itemlist.append(
        Item(channel=item.channel, action="categorias", title="Categorias", url="http://www.vidz7.com/category/"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar",
                         url="http://www.vidz7.com/?s="))

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
    patron = '<li><a href="([^"]+)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, actriz in matches:
        itemlist.append(Item(channel=item.channel, action="lista", title=actriz, url=url))

    return itemlist


def lista(item):
    logger.info()

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    # Extrae las entradas de la pagina seleccionada
    patron = "<a href='.*?.' class='thumb' style='background-image:url\(\"([^\"]+)\"\).*?.<h6><a class='hp' href='([^']+)'>(.*?)</a></h6>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        url = urlparse.urljoin(item.url, scrapedurl)
        title = scrapedtitle.strip()

        # Añade al listado
        itemlist.append(Item(channel=item.channel, action="play", title=title, thumbnail=thumbnail, fanart=thumbnail,
                             fulltitle=title, url=url,
                             viewmode="movie", folder=True))

    paginacion = scrapertools.find_single_match(data,
                                                '<a class="active".*?.>\d+</a><a class="inactive" href ="([^"]+)">')

    if paginacion:
        itemlist.append(Item(channel=item.channel, action="lista", title=">> Página Siguiente", url=paginacion))

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
