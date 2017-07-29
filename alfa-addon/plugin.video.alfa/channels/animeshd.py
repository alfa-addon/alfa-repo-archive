# -*- coding: utf-8 -*-

import re
import urllib

from core import httptools
from core import logger
from core import scrapertools
from core.item import Item

tgenero = {"Comedia": "https://s7.postimg.org/ne9g9zgwb/comedia.png",
           "Drama": "https://s16.postimg.org/94sia332d/drama.png",
           "Acción": "https://s3.postimg.org/y6o9puflv/accion.png",
           "Aventura": "https://s10.postimg.org/6su40czih/aventura.png",
           "Romance": "https://s15.postimg.org/fb5j8cl63/romance.png",
           "Ciencia ficción": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png",
           "Terror": "https://s7.postimg.org/yi0gij3gb/terror.png",
           "Fantasía": "https://s13.postimg.org/65ylohgvb/fantasia.png",
           "Misterio": "https://s1.postimg.org/w7fdgf2vj/misterio.png",
           "Crimen": "https://s4.postimg.org/6z27zhirx/crimen.png",
           "Hentai": "https://s29.postimg.org/aamrngu2f/hentai.png",
           "Magia": "https://s9.postimg.org/nhkfzqffj/magia.png",
           "Psicológico": "https://s13.postimg.org/m9ghzr86f/psicologico.png",
           "Sobrenatural": "https://s9.postimg.org/6hxbvd4ov/sobrenatural.png",
           "Torneo": "https://s2.postimg.org/ajoxkk9ih/torneo.png",
           "Thriller": "https://s22.postimg.org/5y9g0jsu9/thriller.png",
           "Otros": "https://s30.postimg.org/uj5tslenl/otros.png"}

host = "http://www.animeshd.tv"

headers = [['User-Agent', 'Mozilla/50.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'],
           ['Referer', host]]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(title="Ultimas",
                               action="lista",
                               thumbnail='https://s22.postimg.org/cb7nmhwv5/ultimas.png',
                               fanart='https://s22.postimg.org/cb7nmhwv5/ultimas.png',
                               url=host + '/ultimos'
                               ))

    itemlist.append(item.clone(title="Todas",
                               action="lista",
                               thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               fanart='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               url=host + '/buscar?t=todos&q='
                               ))

    itemlist.append(item.clone(title="Generos",
                               action="generos",
                               url=host,
                               thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                               fanart='https://s3.postimg.org/5s9jg2wtf/generos.png'
                               ))

    itemlist.append(item.clone(title="Buscar",
                               action="search",
                               url=host + '/buscar?t=todos&q=',
                               thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                               fanart='https://s30.postimg.org/pei7txpa9/buscar.png'
                               ))

    return itemlist


def get_source(url):
    logger.info()
    data = httptools.downloadpage(url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}|"|\(|\)', "", data)
    return data


def lista(item):
    logger.info()

    itemlist = []

    post = ''
    if item.extra in ['episodios']:
        post = {'tipo': 'episodios', '_token': 'rAqVX74O9HVHFFigST3M9lMa5VL7seIO7fT8PBkl'}
        post = urllib.urlencode(post)
    data = get_source(item.url)
    patron = 'class=anime><div class=cover style=background-image: url(.*?)>.*?<a href=(.*?)><h2>(.*?)<\/h2><\/a><\/div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        url = scrapedurl
        thumbnail = host + scrapedthumbnail
        title = scrapedtitle
        itemlist.append(item.clone(action='episodios',
                                   title=title,
                                   url=url,
                                   thumbnail=thumbnail,
                                   contentSerieName=title
                                   ))

        # Paginacion
    next_page = scrapertools.find_single_match(data,
                                               '<li class=active><span>.*?<\/span><\/li><li><a href=(.*?)>.*?<\/a><\/li>')
    next_page_url = scrapertools.decodeHtmlentities(next_page)
    if next_page_url != "":
        itemlist.append(Item(channel=item.channel,
                             action="lista",
                             title=">> Página siguiente",
                             url=next_page_url,
                             thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'
                             ))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    try:
        if texto != '':
            return lista(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def generos(item):
    logger.info()
    itemlist = []

    data = get_source(item.url)
    patron = '<li class=><a href=http:\/\/www\.animeshd\.tv\/genero\/(.*?)>(.*?)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        if title == 'Recuentos de la vida':
            title = 'Otros'
        genero = scrapertools.decodeHtmlentities(scrapedurl)
        thumbnail = ''
        if title in tgenero:
            thumbnail = tgenero[title]

        url = 'http://www.animeshd.tv/genero/%s' % genero
        itemlist.append(item.clone(action='lista', title=title, url=url, thumbnail=thumbnail))
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = get_source(item.url)
    patron = '<li id=epi-.*? class=list-group-item ><a href=(.*?) class=badge.*?width=25 title=(.*?)> <\/span>(.*?)<\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedlang, scrapedtitle in matches:
        language = scrapedlang
        title = scrapedtitle + ' (%s)' % language
        url = scrapedurl
        itemlist.append(item.clone(title=title, url=url, action='findvideos', language=language))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = get_source(item.url)
    patron = '<iframe.*?src=(.*?) frameborder=0'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for video_url in matches:
        data = get_source(video_url)
        data = data.replace("'", '')
        patron = 'file:(.*?),label:(.*?),type'
        matches = re.compile(patron, re.DOTALL).findall(data)

        for scrapedurl, scrapedquality in matches:
            url = scrapedurl
            quality = scrapedquality
            title = item.contentSerieName + ' (%s)' % quality
            itemlist.append(item.clone(action='play', title=title, url=url, quality=quality))

    return itemlist
