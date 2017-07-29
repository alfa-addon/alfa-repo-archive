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
    itemlist.append(Item(channel=item.channel, action="ultimo", title="Últimos Documentales",
                         url="http://www.teledocumentales.com/", viewmode="movie_with_plot"))
    itemlist.append(Item(channel=item.channel, action="ListaCat", title="Listado por Genero",
                         url="http://www.teledocumentales.com/"))

    return itemlist


def ultimo(item):
    logger.info()
    itemlist = []

    data = scrapertools.cachePage(item.url)

    # Extrae las entradas    
    patron = '<div class="imagen"(.*?)<div style="clear.both">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    print "manolo"
    print matches

    for match in matches:
        scrapedtitle = scrapertools.get_match(match, '<img src="[^"]+" alt="([^"]+)"')
        scrapedtitle = scrapertools.htmlclean(scrapedtitle)
        scrapedurl = scrapertools.get_match(match, '<a href="([^"]+)"')
        scrapedthumbnail = scrapertools.get_match(match, '<img src="([^"]+)" alt="[^"]+"')
        scrapedplot = scrapertools.get_match(match, '<div class="excerpt">([^<]+)</div>')
        itemlist.append(
            Item(channel=item.channel, action="play", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                 plot=scrapedplot, fanart=scrapedthumbnail))

    # Extrae la marca de siguiente pagina
    try:
        next_page = scrapertools.get_match(data, '<a class="next" href="([^"]+)">')
        itemlist.append(Item(channel=item.channel, action="ultimo", title=">> Página siguiente",
                             url=urlparse.urljoin(item.url, next_page, viewmode="movie_with_plot")))
    except:
        pass

    return itemlist


def ListaCat(item):
    logger.info()

    url = item.url

    data = scrapertools.cachePage(url)

    # Extrae las entradas (carpetas)

    # <div class="slidethumb">
    # <a href="http://www.cine-adicto.com/transformers-dark-of-the-moon.html"><img src="http://www.cine-adicto.com/wp-content/uploads/2011/09/Transformers-Dark-of-the-moon-wallpaper.jpg" width="638" alt="Transformers: Dark of the Moon 2011" /></a>
    # </div>

    patron = '<div id="menu_horizontal">(.*?)<div class="cuerpo">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    logger.info("hay %d matches" % len(matches))

    itemlist = []
    for match in matches:
        data2 = match
        patron = '<li class="cat-item cat-item-.*?<a href="(.*?)".*?>(.*?)</a>.*?</li>'
        matches2 = re.compile(patron, re.DOTALL).findall(data2)
        logger.info("hay %d matches2" % len(matches2))

        for match2 in matches2:
            scrapedtitle = match2[1].replace("&#8211;", "-").replace("&amp;", "&").strip()
            scrapedurl = match2[0]
            scrapedthumbnail = match2[0].replace(" ", "%20")
            scrapedplot = ""

            itemlist.append(Item(channel=item.channel, action="ultimo", title=scrapedtitle, url=scrapedurl,
                                 thumbnail=scrapedthumbnail, plot=scrapedplot, fanart=scrapedthumbnail,
                                 viewmode="movie_with_plot"))

    return itemlist


def play(item):
    logger.info()

    data = scrapertools.cachePage(item.url)

    urlvideo = scrapertools.get_match(data, '<!-- end navigation -->.*?<iframe src="([^"]+)"')
    data = scrapertools.cachePage(urlvideo)
    url = scrapertools.get_match(data, 'iframe src="([^"]+)"')

    itemlist = servertools.find_video_items(data=url)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.channel = item.channel

    return itemlist
