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
        Item(channel=item.channel, title="Últimas agregadas", action="agregadas", url="http://peliscity.com",
             viewmode="movie_with_plot"))
    itemlist.append(Item(channel=item.channel, title="Peliculas HD", action="agregadas",
                         url="http://peliscity.com/calidad/hd-real-720", viewmode="movie_with_plot"))
    itemlist.append(
        Item(channel=item.channel, title="Listado por género", action="porGenero", url="http://peliscity.com"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url="http://peliscity.com/?s="))
    itemlist.append(Item(channel=item.channel, title="Idioma", action="porIdioma", url="http://peliscity.com/"))

    return itemlist


def porIdioma(item):
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Castellano", action="agregadas",
                         url="http://www.peliscity.com/idioma/espanol-castellano/", viewmode="movie_with_plot"))
    itemlist.append(
        Item(channel=item.channel, title="VOS", action="agregadas", url="http://www.peliscity.com/idioma/subtitulada/",
             viewmode="movie_with_plot"))
    itemlist.append(Item(channel=item.channel, title="Latino", action="agregadas",
                         url="http://www.peliscity.com/idioma/espanol-latino/", viewmode="movie_with_plot"))

    return itemlist


def porGenero(item):
    logger.info()

    itemlist = []
    data = scrapertools.cache_page(item.url)

    logger.info("data=" + data)
    patron = 'cat-item.*?href="([^"]+).*?>(.*?)<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for urlgen, genero in matches:
        itemlist.append(Item(channel=item.channel, action="agregadas", title=genero, url=urlgen, folder=True,
                             viewmode="movie_with_plot"))

    return itemlist


def search(item, texto):
    logger.info()
    texto_post = texto.replace(" ", "+")
    item.url = "http://www.peliscity.com/?s=" + texto_post

    try:
        return listaBuscar(item)
    # Se captura la excepci?n, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def agregadas(item):
    logger.info()
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info("data=" + data)

    patron = 'class=\'reflectMe\' src="([^"]+).*?class="infor".*?href="([^"]+).*?<h2>(.*?)<.*?class="sinopsis">(.*?)<'  # url

    matches = re.compile(patron, re.DOTALL).findall(data)

    for thumbnail, url, title, sinopsis in matches:
        url = urlparse.urljoin(item.url, url)
        thumbnail = urlparse.urljoin(url, thumbnail)
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title + " ", fulltitle=title, url=url,
                             thumbnail=thumbnail, show=title, plot=sinopsis))

    # Paginación
    try:
        patron = 'tima">.*?href="([^"]+)" ><i'

        next_page = re.compile(patron, re.DOTALL).findall(data)

        itemlist.append(Item(channel=item.channel, action="agregadas", title="Página siguiente >>", url=next_page[0],
                             viewmode="movie_with_plot"))
    except:
        pass

    return itemlist


def listaBuscar(item):
    logger.info()
    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n", " ", data)
    logger.info("data=" + data)

    patron = 'class="row"> <a.*?="([^"]+).*?src="([^"]+).*?title="([^"]+).*?class="text-list">(.*?)</p>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumbnail, title, sinopsis in matches:
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title + " ", fulltitle=title, url=url,
                             thumbnail=thumbnail, show=title, plot=sinopsis))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []
    plot = item.plot

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    patron = 'class="optxt"><span>(.*?)<.*?width.*?class="q">(.*?)</span.*?cursor: hand" rel="(.*?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedidioma, scrapedcalidad, scrapedurl in matches:
        idioma = ""
        scrapedserver = re.findall("http[s*]?://(.*?)/", scrapedurl)
        title = item.title + " [" + scrapedcalidad + "][" + scrapedidioma + "][" + scrapedserver[0] + "]"
        if not ("omina.farlante1" in scrapedurl or "404" in scrapedurl):
            itemlist.append(
                Item(channel=item.channel, action="play", title=title, fulltitle=title, url=scrapedurl, thumbnail="",
                     plot=plot, show=item.show))
    return itemlist


def play(item):
    logger.info()

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = item.channel

    return itemlist
