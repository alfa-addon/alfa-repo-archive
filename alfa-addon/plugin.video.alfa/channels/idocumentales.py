# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from core import tmdb
from core.item import Item

host = 'http://www.idocumentales.net'


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Todas", action="lista", thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               fanart='https://s18.postimg.org/fwvaeo6qh/todas.png', url=host))

    itemlist.append(Item(channel=item.channel, title="Generos", action="generos", url=host,
                         thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                         fanart='https://s3.postimg.org/5s9jg2wtf/generos.png'))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host + '/?s=',
                         thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                         fanart='https://s30.postimg.org/pei7txpa9/buscar.png'))

    return itemlist


def lista(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    patron = '<div class=item><a href=(.*?) title=(.*?)\(.*?\)><div class=img><img src=(.*?) alt=.*?'
    patron += '<span class=player><\/span><span class=year>(.*?)<\/span><span class=calidad>(.*?)<\/span><\/div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedyear, calidad in matches:
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = ''
        contentTitle = scrapedtitle
        title = contentTitle + ' (' + calidad + ')'
        year = scrapedyear
        fanart = ''

        itemlist.append(
            Item(channel=item.channel, action='findvideos', title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fanart=fanart, contentTitle=contentTitle, infoLabels={'year': year}))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # Paginacion

    if itemlist != []:
        actual_page_url = item.url
        next_page = scrapertools.find_single_match(data, '<link rel=next href=(.*?) \/>')
        if next_page != '':
            itemlist.append(Item(channel=item.channel, action="lista", title='Siguiente >>>', url=next_page,
                                 thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    duplicado = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    patron = '<li id=menu-item-.*? class=menu-item menu-item-type-taxonomy menu-item-object-category menu-item-.*?><a href=(.*?)>(.*?)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        thumbnail = ''
        fanart = ''
        title = scrapedtitle
        url = scrapedurl

        if url not in duplicado:
            itemlist.append(Item(channel=item.channel, action="lista", title=title, fulltitle=item.title, url=url,
                                 thumbnail=thumbnail, fanart=fanart))
            duplicado.append(url)
    return itemlist


def busqueda(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    patron = '<li class=s-item><div class=s-img><img class=imx style=margin-top:0px; src=(.*?) alt=(.*?)><span><\/span><\/div><div class=s-box>.*?'
    patron += '<h3><a href=(.*?)>.*?<\/a><\/h3><span class=year>(.*?)<\/span><p>(.*?)<\/p>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedthumbnail, scrapedtitle, scrapedurl, scrapedyear, scrapedplot in matches:
        url = scrapedurl
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        year = scrapedyear
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url, thumbnail=thumbnail,
                 plot=plot, contentSerieName=title, infoLabels={'year': year}))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    # Paginacion

    if itemlist != []:
        actual_page_url = item.url
        next_page = scrapertools.find_single_match(data, '<link rel=next href=(.*?) \/>')
        if next_page != '':
            itemlist.append(Item(channel=item.channel, action="busqueda", title='Siguiente >>>', url=next_page,
                                 thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    if texto != '':
        return busqueda(item)


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'documentales':
            item.url = host

        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
