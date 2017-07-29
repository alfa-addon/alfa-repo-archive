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
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Novedades", fanart=item.fanart,
                         url="http://es.pornhub.com/video?o=cm"))
    itemlist.append(Item(channel=item.channel, action="categorias", title="Categorias", fanart=item.fanart,
                         url="http://es.pornhub.com/categories?o=al"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar", fanart=item.fanart,
                         url="http://es.pornhub.com/video/search?search=%s&o=mr"))
    return itemlist


def search(item, texto):
    logger.info()

    item.url = item.url % texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, '<div id="categoriesStraightImages">(.*?)</ul>')

    # Extrae las categorias
    patron = '<li class="cat_pic" data-category=".*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'alt="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        if "?" in scrapedurl:
            url = urlparse.urljoin(item.url, scrapedurl + "&o=cm")
        else:
            url = urlparse.urljoin(item.url, scrapedurl + "?o=cm")

        itemlist.append(Item(channel=item.channel, action="peliculas", title=scrapedtitle, url=url, fanart=item.fanart,
                             thumbnail=scrapedthumbnail))

    itemlist.sort(key=lambda x: x.title)
    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    videodata = scrapertools.find_single_match(data, 'videos search-video-thumbs">(.*?)<div class="reset"></div>')

    # Extrae las peliculas
    patron = '<div class="phimage">.*?'
    patron += '<a href="([^"]+)" title="([^"]+).*?'
    patron += '<var class="duration">([^<]+)</var>(.*?)</div>.*?'
    patron += 'data-mediumthumb="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(videodata)

    for url, scrapedtitle, duration, scrapedhd, thumbnail in matches:
        title = scrapedtitle.replace("&amp;amp;", "&amp;") + " (" + duration + ")"

        scrapedhd = scrapertools.find_single_match(scrapedhd, '<span class="hd-thumbnail">(.*?)</span>')
        if scrapedhd == 'HD':
            title += ' [HD]'

        url = urlparse.urljoin(item.url, url)
        itemlist.append(
            Item(channel=item.channel, action="play", title=title, url=url, fanart=item.fanart, thumbnail=thumbnail))

    if itemlist:
        # Paginador
        patron = '<li class="page_next"><a href="([^"]+)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if matches:
            url = urlparse.urljoin(item.url, matches[0].replace('&amp;', '&'))
            itemlist.append(
                Item(channel=item.channel, action="peliculas", title=">> Página siguiente", fanart=item.fanart,
                     url=url))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    quality = scrapertools.find_multiple_matches(data, '"id":"quality([^"]+)"')
    for q in quality:
        match = scrapertools.find_single_match(data, 'var quality_%s=(.*?);' % q)
        match = re.sub(r'(/\*.*?\*/)', '', match).replace("+", "")
        url = ""
        for s in match.split():
            val = scrapertools.find_single_match(data, 'var %s=(.*?);' % s.strip())
            if "+" in val:
                values = scrapertools.find_multiple_matches(val, '"([^"]+)"')
                val = "".join(values)

            url += val.replace('"', "")
        itemlist.append([".mp4 %s [directo]" % q, url])

    return itemlist
