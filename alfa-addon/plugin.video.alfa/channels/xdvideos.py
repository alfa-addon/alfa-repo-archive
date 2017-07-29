# -*- coding: utf-8 -*-

import re

from channelselector import get_thumb
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

host = "http://xdvideos.org/"


def mainlist(item):
    logger.info()
    thumb_series = get_thumb("thumb_channels_tvshow.png")

    itemlist = list()

    itemlist.append(Item(channel=item.channel, action="categorias", title="Categorias", url=host,
                         thumbnail=thumb_series))
    return itemlist


def categorias(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '<ul id="menu-menu-2" class="menu">(.+)>Problemas'
    data = scrapertools.find_single_match(data, patron)
    patron_cat = '<li id="menu-item-[^"]+" class=".+?"><a href="([^"]+)">([^"]+)<\/a><ulclass="sub-menu">'
    matches = scrapertools.find_multiple_matches(data, patron_cat)
    for url, name in matches:
        if name != 'Clasicos':
            title = name
            itemlist.append(item.clone(title=title, url=url, action="lista", show=title))
    return itemlist


def lista(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    category = item.title
    patron = '<li id="menu-item-[^"]+" class="menu-item menu-item-type-post_type menu-item-object-page current-menu-item page_item page-item-[^"]+ current_page_item menu-item-has-children menu-item-[^"]+"><a href="[^"]+">[^"]+<\/a>(.+?)<\/a><\/li><\/ul><\/li>'
    content = scrapertools.find_single_match(data, patron)
    patron_lista = '<a href="([^"]+)">([^"]+)<\/a>'
    match_series = scrapertools.find_multiple_matches(content, patron_lista)
    for url, title in match_series:
        if "(" in title:
            show_dual = title.split("(")
            show = show_dual[1]
            if ")" in show:
                show = show.rstrip(")")
        else:
            show = title
        itemlist.append(item.clone(title=title, url=url, action="episodios", show=show, plot=show))
    tmdb.set_infoLabels(itemlist)
    return itemlist


def episodios(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    scrapedshow, scrapedthumbnail = scrapertools.find_single_match(data,
                                                                   '<h1 class="entry-title">([^"]+)<\/h1>.+?<img .+? src="([^"]+)"')
    data = scrapertools.find_single_match(data, '<div class="entry-content">(.+?)<div id="wpdevar')
    patron_caps = '<a href="([^"]+)">([^"]+)<\/a>'
    matches = scrapertools.find_multiple_matches(data, patron_caps)
    i = 0
    for url, name in matches:
        i = i + 1
        if i < 10:
            title = "1x0" + str(i) + " " + name
        else:
            title = "1x" + str(i) + " " + name
        itemlist.append(
            item.clone(title=title, url=url, action="findvideos", show=scrapedshow, thumbnail=scrapedthumbnail))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    itemlist.extend(servertools.find_video_items(data=data))
    scrapedthumbnail = scrapertools.find_single_match(data, 'src="([^"]+)"')
    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.thumbnail = scrapedthumbnail

    return itemlist
