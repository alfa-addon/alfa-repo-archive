# -*- coding: utf-8 -*-

import re
import urlparse

from core import httptools
from core import logger
from core import scrapertools
from core.item import Item

CHANNEL_HOST = "http://hentai-id.tv/"


def mainlist(item):
    logger.info()

    itemlist = list()
    itemlist.append(Item(channel=item.channel, action="series", title="Novedades",
                         url=urlparse.urljoin(CHANNEL_HOST, "archivos/h2/"), extra="novedades"))
    itemlist.append(Item(channel=item.channel, action="letras", title="Por orden alfabético"))
    itemlist.append(Item(channel=item.channel, action="generos", title="Por géneros", url=CHANNEL_HOST))
    itemlist.append(Item(channel=item.channel, action="series", title="Sin Censura",
                         url=urlparse.urljoin(CHANNEL_HOST, "archivos/sin-censura/")))
    itemlist.append(Item(channel=item.channel, action="series", title="High Definition",
                         url=urlparse.urljoin(CHANNEL_HOST, "archivos/hight-definition/")))
    itemlist.append(Item(channel=item.channel, action="series", title="Mejores Hentais",
                         url=urlparse.urljoin(CHANNEL_HOST, "archivos/ranking-hentai/")))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar",
                         url=urlparse.urljoin(CHANNEL_HOST, "?s=")))

    return itemlist


def letras(item):
    logger.info()

    itemlist = []

    for letra in '0ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        itemlist.append(Item(channel=item.channel, action="series", title=letra,
                             url=urlparse.urljoin(CHANNEL_HOST, "/?s=letra-%s" % letra.replace("0", "num"))))

    return itemlist


def generos(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    data = scrapertools.get_match(data, "<div class='cccon'>(.*?)</div><div id=\"myslides\">")
    patron = "<a.+? href='/([^']+)'>(.*?)</a>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(item.url, scrapedurl)
        # logger.debug("title=[{0}], url=[{1}]".format(title, url))

        itemlist.append(Item(channel=item.channel, action="series", title=title, url=url))

    return itemlist


def search(item, texto):
    logger.info()
    if item.url == "":
        item.url = urlparse.urljoin(CHANNEL_HOST, "animes/?buscar=")
    texto = texto.replace(" ", "+")
    item.url = "%s%s" % (item.url, texto)

    try:
        return series(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def series(item):
    logger.info()

    data = httptools.downloadpage(item.url).data

    patron = '<div class="post" id="post"[^<]+<center><h1 class="post-title entry-title"[^<]+<a href="([^"]+)">' \
             '(.*?)</a>[^<]+</h1></center>[^<]+<div[^<]+</div>[^<]+<div[^<]+<div.+?<img src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    if item.extra == "novedades":
        action = "findvideos"
    else:
        action = "episodios"

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        title = scrapertools.unescape(scrapedtitle)
        fulltitle = title
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        show = title
        # logger.debug("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                             show=show, fulltitle=fulltitle, fanart=thumbnail, folder=True))

    patron = '</span><a class="page larger" href="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = match
            scrapedtitle = ">> Pagina Siguiente"

            itemlist.append(Item(channel=item.channel, action="series", title=scrapedtitle, url=scrapedurl,
                                 folder=True, viewmode="movies_with_plot"))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, '<div class="listanime">(.*?)</div>')
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.unescape(scrapedtitle)
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = item.thumbnail
        plot = item.plot

        # logger.debug("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url,
                             thumbnail=thumbnail, plot=plot, show=item.show, fulltitle="%s %s" % (item.show, title),
                             fanart=thumbnail, viewmode="movies_with_plot", folder=True))

    return itemlist


def findvideos(item):
    logger.info()

    data = httptools.downloadpage(item.url).data
    patron = '<div id="tab\d".+?>[^<]+<[iframe|IFRAME].*?[src|SRC]="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url in matches:
        if 'goo.gl' in url:
            video = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers["location"]
            matches.remove(url)
            matches.append(video)

    from core import servertools
    itemlist = servertools.find_video_items(data=",".join(matches))
    for videoitem in itemlist:
        videoitem.fulltitle = item.fulltitle
        videoitem.channel = item.channel
        videoitem.thumbnail = item.thumbnail

    return itemlist
