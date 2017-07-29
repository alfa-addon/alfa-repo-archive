# -*- coding: utf-8 -*-

import re

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="videos", title="Útimos vídeos", url="http://es.xhamster.com/",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="categorias", title="Categorías"))
    itemlist.append(Item(channel=item.channel, action="votados", title="Más votados"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar",
                         url="http://xhamster.com/search.php?q=%s&qcat=video"))
    return itemlist


# REALMENTE PASA LA DIRECCION DE BUSQUEDA

def search(item, texto):
    logger.info()
    tecleado = texto.replace(" ", "+")
    item.url = item.url % tecleado
    item.extra = "buscar"
    try:
        return videos(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# SECCION ENCARGADA DE BUSCAR

def videos(item):
    logger.info()
    data = scrapertools.cache_page(item.url)
    itemlist = []

    data = scrapertools.get_match(data, '<div class="boxC videoList clearfix">(.*?)<div id="footer">')

    # Patron #1
    patron = '<div class="video"><a href="([^"]+)" class="hRotator">' + "<img src='([^']+)' class='thumb'" + ' alt="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="play", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                 folder=True))

    # Patron #2
    patron = '<a href="([^"]+)"  data-click="[^"]+" class="hRotator"><img src=\'([^\']+)\' class=\'thumb\' alt="([^"]+)"/>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="play", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                 folder=True))

    # Paginador
    patron = "<a href='([^']+)' class='last colR'><div class='icon iconPagerNextHover'></div>Próximo</a>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) > 0:
        itemlist.append(
            Item(channel=item.channel, action="videos", title="Página Siguiente", url=matches[0], thumbnail="",
                 folder=True, viewmode="movie"))

    return itemlist


# SECCION ENCARGADA DE VOLCAR EL LISTADO DE CATEGORIAS CON EL LINK CORRESPONDIENTE A CADA PAGINA

def categorias(item):
    logger.info()
    itemlist = []

    itemlist.append(
        Item(channel=item.channel, action="lista", title="Heterosexual", url="http://es.xhamster.com/channels.php"))
    itemlist.append(
        Item(channel=item.channel, action="lista", title="Transexuales", url="http://es.xhamster.com/channels.php"))
    itemlist.append(Item(channel=item.channel, action="lista", title="Gays", url="http://es.xhamster.com/channels.php"))
    return itemlist


def votados(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, action="videos", title="Día",
                         url="http://es.xhamster.com/rankings/daily-top-videos.html", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="videos", title="Semana",
                         url="http://es.xhamster.com/rankings/weekly-top-videos.html", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="videos", title="Mes",
                         url="http://es.xhamster.com/rankings/monthly-top-videos.html", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="videos", title="De siempre",
                         url="http://es.xhamster.com/rankings/alltime-top-videos.html", viewmode="movie"))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = scrapertools.downloadpageGzip(item.url)
    # data = data.replace("\n","")
    # data = data.replace("\t","")

    if item.title == "Gays":
        data = scrapertools.get_match(data,
                                      '<div class="title">' + item.title + '</div>.*?<div class="list">(.*?)<div id="footer">')
    else:
        data = scrapertools.get_match(data,
                                      '<div class="title">' + item.title + '</div>.*?<div class="list">(.*?)<div class="catName">')
    patron = '(<div.*?</div>)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        data = data.replace(match, "")
    patron = 'href="([^"]+)">(.*?)</a>'
    data = ' '.join(data.split())
    logger.info(data)
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        itemlist.append(Item(channel=item.channel, action="videos", title=scrapedtitle, url=scrapedurl, folder=True,
                             viewmode="movie"))

    sorted_itemlist = sorted(itemlist, key=lambda Item: Item.title)
    return sorted_itemlist


# OBTIENE LOS ENLACES SEGUN LOS PATRONES DEL VIDEO Y LOS UNE CON EL SERVIDOR
def play(item):
    logger.info()
    itemlist = []

    data = scrapertools.cachePage(item.url)
    logger.debug(data)

    patron = '"([0-9]+p)":"([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for res, url in matches:
        url = url.replace("\\", "")
        logger.debug("url=" + url)
        itemlist.append(["%s %s [directo]" % (res, scrapertools.get_filename_from_url(url)[-4:]), url])

    return itemlist
