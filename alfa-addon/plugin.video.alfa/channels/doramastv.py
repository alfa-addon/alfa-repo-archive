# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core.item import Item

host = "http://doramastv.com/"
DEFAULT_HEADERS = []
DEFAULT_HEADERS.append(
    ["User-Agent", "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"])


def mainlist(item):
    logger.info()

    itemlist = list([])
    itemlist.append(
        Item(channel=item.channel, action="pagina_", title="En emision", url=urlparse.urljoin(host, "drama/emision")))
    itemlist.append(Item(channel=item.channel, action="letras", title="Listado alfabetico",
                         url=urlparse.urljoin(host, "lista-numeros")))
    itemlist.append(
        Item(channel=item.channel, action="generos", title="Generos", url=urlparse.urljoin(host, "genero/accion")))
    itemlist.append(Item(channel=item.channel, action="pagina_", title="Ultimos agregados",
                         url=urlparse.urljoin(host, "dramas/ultimos")))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar",
                         url=urlparse.urljoin(host, "buscar/anime/ajax/?title=")))

    return itemlist


def letras(item):
    logger.info()

    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url, headers=headers)

    patron = ' <a href="(\/lista-.+?)">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""

        logger.debug("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(
            Item(channel=item.channel, action="pagina_", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist


def pagina_(item):
    logger.info()
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url, headers=headers)
    data1 = scrapertools.get_match(data, '<div class="animes-bot">(.+?)<!-- fin -->')
    data1 = data1.replace('\n', '')
    data1 = data1.replace('\r', '')
    patron = 'href="(\/drama.+?)".+?<\/div>(.+?)<\/div>.+?src="(.+?)".+?titulo">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data1)
    for scrapedurl, scrapedplot, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        plot = scrapertools.decodeHtmlentities(scrapedplot)
        itemlist.append(
            Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 show=title))

    patron = 'href="([^"]+)" class="next"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=item.channel, action="pagina_", title=scrapedtitle, url=scrapedurl,
                                 thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url, headers=headers)
    data = data.replace('\n', '')
    data = data.replace('\r', '')
    data1 = scrapertools.get_match(data, '<ul id="lcholder">(.+?)</ul>')
    patron = '<a href="(.+?)".+?>(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data1)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        show = item.show
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title, show=show))
    return itemlist


def findvideos(item):
    logger.info()

    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url, headers=headers)
    data = data.replace('\n', '')
    data = data.replace('\r', '')
    patron = '<iframe src="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    data1 = ''
    for match in matches:
        data1 += match + '\n'
    data = data1
    data = data.replace('%26', '&')
    data = data.replace('http://ozhe.larata.in/repro-d/mvk?v=', 'http://vk.com/video_ext.php?oid=')
    data = data.replace('http://ozhe.larata.in/repro-d/send?v=', 'http://sendvid.com/embed/')
    data = data.replace('http://ozhe.larata.in/repro-d/msend?v=', 'http://sendvid.com/embed/')
    data = data.replace('http://ozhe.larata.in/repro-d/vidweed?v=', 'http://www.videoweed.es/file/')
    data = data.replace('http://ozhe.larata.in/repro-d/nowv?v=', 'http://www.nowvideo.sx/video/')
    data = data.replace('http://ozhe.larata.in/repro-d/nov?v=', 'http://www.novamov.com/video/')
    itemlist = []

    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.folder = False
    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url, headers=headers)
    data = data.replace('\n', '')
    data = data.replace('\r', '')

    data = scrapertools.get_match(data, '<!-- Lista de Generos -->(.+?)<\/div>')
    patron = '<a href="(.+?)".+?>(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        logger.debug("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(
            Item(channel=item.channel, action="pagina_", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist


def search(item, texto):
    logger.info()
    item.url = urlparse.urljoin(host, item.url)
    texto = texto.replace(" ", "+")
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url + texto, headers=headers)
    data = data.replace('\n', '')
    data = data.replace('\r', '')
    patron = '<a href="(.+?)".+?src="(.+?)".+?titulo">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        itemlist.append(
            Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail, plot="",
                 show=title))
    return itemlist
