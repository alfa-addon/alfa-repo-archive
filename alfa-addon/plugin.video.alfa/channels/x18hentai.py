# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from core.item import Item

host = 'http://www.18hentaionline.eu/'
headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'],
           ['Referer', host]]


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Todos", action="todas", url=host, thumbnail='', fanart=''))

    itemlist.append(
        Item(channel=item.channel, title="Sin Censura", action="todas", url=host + 'tag/sin-censura/', thumbnail='',
             fanart=''))

    itemlist.append(
        Item(channel=item.channel, title="Estrenos", action="todas", url=host + 'category/estreno/', thumbnail='',
             fanart=''))

    itemlist.append(
        Item(channel=item.channel, title="Categorias", action="categorias", url=host, thumbnail='', fanart=''))

    return itemlist


def todas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<h3><a href="([^"]+)" title="([^"]+)">.*?<\/a><\/h3>.*?'
    patron += '<.*?>.*?'
    patron += '<a.*?img src="([^"]+)" alt'

    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        url = scrapedurl
        title = scrapedtitle.decode('utf-8')
        thumbnail = scrapedthumbnail
        fanart = ''
        itemlist.append(
            Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail, fanart=fanart))

    # Paginacion
    title = ''
    siguiente = scrapertools.find_single_match(data,
                                               '<a rel="nofollow" class="next page-numbers" href="([^"]+)">Siguiente &raquo;<\/a><\/div>')
    title = 'Pagina Siguiente >>> '
    fanart = ''
    itemlist.append(Item(channel=item.channel, action="todas", title=title, url=siguiente, fanart=fanart))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    if texto != '':
        return todas(item)
    else:
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, headers=headers).data
    patron = "<a href='([^']+)' class='tag-link-.*? tag-link-position-.*?' title='.*?' style='font-size: 11px;'>([^<]+)<\/a>"

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url = scrapedurl
        title = scrapedtitle
        itemlist.append(Item(channel=item.channel, action="todas", title=title, fulltitle=item.fulltitle, url=url))

    return itemlist


def episodios(item):
    censura = {'Si': 'con censura', 'No': 'sin censura'}
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<td>([^<]+)<\/td>.<td>([^<]+)<\/td>.<td>([^<]+)<\/td>.<td>([^<]+)<\/td>.<td><a href="([^"]+)".*?>Ver Capitulo<\/a><\/td>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedcap, scrapedaud, scrapedsub, scrapedcen, scrapedurl in matches:
        url = scrapedurl
        title = 'CAPITULO ' + scrapedcap + ' AUDIO: ' + scrapedaud + ' SUB:' + scrapedsub + ' ' + censura[scrapedcen]
        thumbnail = ''
        plot = ''
        fanart = ''
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, fulltitle=item.fulltitle, url=url,
                             thumbnail=item.thumbnail, plot=plot))

    return itemlist
