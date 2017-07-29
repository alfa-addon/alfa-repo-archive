# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(
        Item(channel=item.channel, action="videos", title="Útimos videos", url="http://www.submityourflicks.com/",
             viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar",
                         url="http://www.submityourflicks.com/index.php?mode=search&q=%s&submit=Search"))

    return itemlist


def search(item, texto):
    logger.info()
    tecleado = texto.replace(" ", "+")
    item.url = item.url % tecleado
    try:
        return videos(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def videos(item):
    logger.info()
    itemlist = []

    '''
    <div class="item-block item-normal col" >
    <div class="inner-block">
    <a href="http://www.submityourflicks.com/1846642-my-hot-wife-bending-over-and-getting-her-cunt-reamed.html" title="My hot wife bending over and getting her cunt reamed..">
    <span class="image">
    <script type='text/javascript'>stat['56982c566d05c'] = 0;
    pic['56982c566d05c'] = new Array();
    pics['56982c566d05c'] = new Array(1, 1, 1, 1, 1, 1, 1, 1, 1, 1);</script>
    <img src="
    '''

    data = scrapertools.downloadpageGzip(item.url)
    patron = '<div class="item-block[^<]+'
    patron += '<div class="inner-block[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<span class="image".*?'
    patron += '<img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        title = scrapedtitle
        url = scrapedurl
        thumbnail = scrapedthumbnail.replace(" ", "%20")
        plot = ""

        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot,
                             folder=False))

    next_page_url = scrapertools.find_single_match(data, "<a href='([^']+)' class=\"next\">NEXT</a>")
    if next_page_url != "":
        url = urlparse.urljoin(item.url, next_page_url)
        itemlist.append(Item(channel=item.channel, action="videos", title=">> Página siguiente", url=url, folder=True,
                             viewmode="movie"))

    return itemlist


def play(item):
    logger.info()

    data = scrapertools.cache_page(item.url)

    media_url = scrapertools.find_single_match(data, 'file\:\s*"([^"]+)"')
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title=item.title, fulltitle=item.fulltitle, url=media_url,
                         thumbnail=item.thumbnail, plot=item.plot, show=item.title, server="directo", folder=False))

    return itemlist
