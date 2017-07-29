# -*- coding: utf-8 -*-

import re
import urlparse

from core import httptools
from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Catálogo", action="series", url="http://www.vertelenovelas.cc/",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    return itemlist


def search(item, texto):
    logger.info()

    texto = texto.replace(" ", "+")
    item.url = "http://www.vertelenovelas.cc/ajax/autocompletex.php?q=" + texto

    try:
        return series(item)

    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def series(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    patron = '<article.*?</article>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, '<span>([^<]+)</span>')
        if title == "":
            title = scrapertools.find_single_match(match, '<a href="[^"]+" class="title link">([^<]+)</a>')
        url = urlparse.urljoin(item.url, scrapertools.find_single_match(match, '<a href="([^"]+)"'))
        thumbnail = scrapertools.find_single_match(match, '<div data-src="([^"]+)"')
        if thumbnail == "":
            thumbnail = scrapertools.find_single_match(match, '<img src="([^"]+)"')
        logger.debug("title=[" + title + "], url=[" + url + "]")
        itemlist.append(Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail))

    next_page_url = scrapertools.find_single_match(data, '<a href="([^"]+)" class="next">')
    if next_page_url != "":
        itemlist.append(Item(channel=item.channel, action="series", title=">> Pagina siguiente",
                             url=urlparse.urljoin(item.url, next_page_url), viewmode="movie", thumbnail="", plot="",
                             folder=True))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, '<h2>Cap(.*?)</ul>')
    patron = '<li><a href="([^"]+)"><span>([^<]+)</span></a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        plot = ""
        thumbnail = ""
        url = urlparse.urljoin(item.url, scrapedurl)

        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 folder=True, fulltitle=title))

    return itemlist


def findvideos(item):
    logger.info()
    data = httptools.downloadpage(item.url).data

    pattern = 'data-id="([^"]+)"'
    list_servers = re.compile(pattern, re.DOTALL).findall(data)

    logger.debug("llist_servers %s" % list_servers)
    list_urls = []

    for _id in list_servers:
        post = "id=%s" % _id
        data = httptools.downloadpage("http://www.vertelenovelas.cc/goto/", post=post).data
        list_urls.append(scrapertools.find_single_match(data, 'document\.location = "([^"]+)";'))

    from core import servertools
    itemlist = servertools.find_video_items(data=", ".join(list_urls))
    for videoitem in itemlist:
        # videoitem.title = item.title
        videoitem.channel = item.channel

    return itemlist
