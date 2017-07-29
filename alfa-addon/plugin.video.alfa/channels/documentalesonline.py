# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from core.item import Item

HOST = "http://documentales-online.com/"


def mainlist(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Novedades", action="listado", url=HOST))
    itemlist.append(Item(channel=item.channel, title="Destacados", action="seccion", url=HOST, extra="destacados"))
    itemlist.append(Item(channel=item.channel, title="Series Destacadas", action="seccion", url=HOST, extra="series"))
    # itemlist.append(Item(channel=item.channel, title="Top 100", action="categorias", url=HOST))
    # itemlist.append(Item(channel=item.channel, title="Populares", action="categorias", url=HOST))

    itemlist.append(Item(channel=item.channel, title="Buscar por:"))
    itemlist.append(Item(channel=item.channel, title="    Título", action="search"))
    itemlist.append(Item(channel=item.channel, title="    Categorías", action="categorias", url=HOST))
    # itemlist.append(Item(channel=item.channel, title="    Series y Temas", action="categorias", url=HOST))

    return itemlist


def seccion(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)

    if item.extra == "destacados":
        patron_seccion = '<h4 class="widget-title">Destacados</h4><div class="textwidget"><ul>(.*?)</ul>'
        action = "findvideos"
    else:
        patron_seccion = '<h4 class="widget-title">Series destacadas</h4><div class="textwidget"><ul>(.*?)</ul>'
        action = "listado"

    data = scrapertools.find_single_match(data, patron_seccion)

    matches = re.compile('<a href="([^"]+)">(.*?)</a>', re.DOTALL).findall(data)

    aux_action = action
    for url, title in matches:
        if item.extra != "destacados" and "Cosmos (Carl Sagan)" in title:
            action = "findvideos"
        else:
            action = aux_action
        itemlist.append(item.clone(title=title, url=url, action=action, fulltitle=title))

    return itemlist


def listado(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)

    pagination = scrapertools.find_single_match(data, '<div class="older"><a href="([^"]+)"')
    if not pagination:
        pagination = scrapertools.find_single_match(data, '<span class=\'current\'>\d</span>'
                                                          '<a class="page larger" href="([^"]+)">')

    patron = '<ul class="sp-grid">(.*?)</ul>'
    data = scrapertools.find_single_match(data, patron)

    matches = re.compile('<a href="([^"]+)">(.*?)</a>.*?<img.*?src="([^"]+)"', re.DOTALL).findall(data)

    for url, title, thumb in matches:
        itemlist.append(item.clone(title=title, url=url, action="findvideos", fulltitle=title, thumbnail=thumb))

    if pagination:
        itemlist.append(item.clone(title=">> Página siguiente", url=pagination))

    return itemlist


def categorias(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)

    data = scrapertools.find_single_match(data, 'a href="#">Categorías</a><ul class="sub-menu">(.*?)</ul>')
    matches = re.compile('<a href="([^"]+)">(.*?)</a>', re.DOTALL).findall(data)

    for url, title in matches:
        itemlist.append(item.clone(title=title, url=url, action="listado", fulltitle=title))

    return itemlist


def search(item, texto):
    logger.info()

    texto = texto.replace(" ", "+")

    try:
        item.url = HOST + "?s=%s" % texto
        return listado(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def findvideos(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)

    if item.fulltitle == "Cosmos (Carl Sagan)":

        matches = scrapertools.find_multiple_matches(data,
                                                     '<p><strong>(.*?)</strong><br /><iframe.+?src="(https://www\.youtube\.com/[^?]+)')

        for title, url in matches:
            new_item = item.clone(title=title, url=url)

            from core import servertools
            aux_itemlist = servertools.find_video_items(new_item)
            for videoitem in aux_itemlist:
                videoitem.title = new_item.title
                videoitem.fulltitle = new_item.title
                videoitem.channel = item.channel
                # videoitem.thumbnail = item.thumbnail
                itemlist.extend(aux_itemlist)

    else:
        data = scrapertools.find_multiple_matches(data, '<iframe.+?src="(https://www\.youtube\.com/[^?]+)')

        from core import servertools
        itemlist.extend(servertools.find_video_items(data=",".join(data)))
        for videoitem in itemlist:
            videoitem.fulltitle = item.fulltitle
            videoitem.channel = item.channel
            # videoitem.thumbnail = item.thumbnail

    return itemlist
