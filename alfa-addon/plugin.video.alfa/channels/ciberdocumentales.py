# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from core import tmdb
from core.item import Item

host = 'http://www.ciberdocumentales.com'


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Todas", action="lista", thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               fanart='https://s18.postimg.org/fwvaeo6qh/todas.png', url=host))

    itemlist.append(Item(channel=item.channel, title="Generos", action="generos", url=host,
                         thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                         fanart='https://s3.postimg.org/5s9jg2wtf/generos.png'))

    itemlist.append(Item(channel=item.channel, title="Mas Vistas", action="lista", url=host,
                         thumbnail='https://s9.postimg.org/wmhzu9d7z/vistas.png',
                         fanart='https://s9.postimg.org/wmhzu9d7z/vistas.png', extra='masvistas'))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host,
                         thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                         fanart='https://s30.postimg.org/pei7txpa9/buscar.png'))

    return itemlist


def lista(item):
    logger.info()

    itemlist = []
    if item.extra == 'buscar':
        data = httptools.downloadpage(host + '/index.php?' + 'categoria=0&keysrc=' + item.text).data
    else:
        data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    if item.extra == 'masvistas':
        patron = '<div class=bloquecenmarcado><a title=.*? target=_blank href=(.*?) class=game><img src=(.*?) alt=(.*?) title= class=bloquecenimg \/>.*?<strong>(.*?)<\/strong>'
    else:
        patron = '<div class=fotonoticia><a.*?target=_blank href=(.*?)><img src=(.*?) alt=(.*?) \/>.*?class=textonoticia>.*?\/><br \/>(.*?)<\/div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        url = host + scrapedurl
        thumbnail = host + scrapedthumbnail
        plot = scrapertools.htmlclean(scrapedplot)
        plot = plot.decode('iso8859-1').encode('utf-8')
        contentTitle = scrapedtitle
        title = contentTitle
        title = title.decode('iso8859-1').encode('utf-8')
        fanart = ''
        itemlist.append(
            Item(channel=item.channel, action='findvideos', title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fanart=fanart, contentTitle=contentTitle))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # Paginacion

    if itemlist != []:
        actual_page_url = item.url
        next_page = scrapertools.find_single_match(data, 'class=current>.*?<\/span><a href=(.*?)>.*?<\/a>')
        if next_page != '' and item.extra != 'masvistas':
            itemlist.append(Item(channel=item.channel, action="lista", title='Siguiente >>>', url=host + next_page,
                                 thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    patron = '<a style=text-transform:capitalize; href=(.*?)\/>(.*?)<\/a><\/span><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        thumbnail = ''
        fanart = ''
        title = scrapedtitle
        url = host + scrapedurl

        itemlist.append(
            Item(channel=item.channel, action="lista", title=title, fulltitle=item.title, url=url, thumbnail=thumbnail,
                 fanart=fanart))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.text = texto
    item.extra = 'buscar'
    if texto != '':
        return lista(item)


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
