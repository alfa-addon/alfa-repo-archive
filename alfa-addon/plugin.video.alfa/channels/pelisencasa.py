# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import tmdb
from core.item import Item
from lib import jsunpack

host = 'http://pelisencasa.net'

tgenero = {"Comedia": "https://s7.postimg.org/ne9g9zgwb/comedia.png",
           "Suspense": "https://s13.postimg.org/wmw6vl1cn/suspenso.png",
           "Drama": "https://s16.postimg.org/94sia332d/drama.png",
           "Acción": "https://s3.postimg.org/y6o9puflv/accion.png",
           "Aventura": "https://s10.postimg.org/6su40czih/aventura.png",
           "Romance": "https://s15.postimg.org/fb5j8cl63/romance.png",
           "Animación": "https://s13.postimg.org/5on877l87/animacion.png",
           "Ciencia ficción": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png",
           "Terror": "https://s7.postimg.org/yi0gij3gb/terror.png",
           "Documental": "https://s16.postimg.org/7xjj4bmol/documental.png",
           "Música": "https://s29.postimg.org/bbxmdh9c7/musical.png",
           "Western": "https://s23.postimg.org/lzyfbjzhn/western.png",
           "Fantasía": "https://s13.postimg.org/65ylohgvb/fantasia.png",
           "Guerra": "https://s23.postimg.org/71itp9hcr/belica.png",
           "Misterio": "https://s1.postimg.org/w7fdgf2vj/misterio.png",
           "Crimen": "https://s4.postimg.org/6z27zhirx/crimen.png",
           "Historia": "https://s15.postimg.org/fmc050h1n/historia.png",
           "Familia": "https://s7.postimg.org/6s7vdhqrf/familiar.png"}

tletras = {'#': 'https://s32.postimg.org/drojt686d/image.png',
           'a': 'https://s32.postimg.org/llp5ekfz9/image.png',
           'b': 'https://s32.postimg.org/y1qgm1yp1/image.png',
           'c': 'https://s32.postimg.org/vlon87gmd/image.png',
           'd': 'https://s32.postimg.org/3zlvnix9h/image.png',
           'e': 'https://s32.postimg.org/bgv32qmsl/image.png',
           'f': 'https://s32.postimg.org/y6u7vq605/image.png',
           'g': 'https://s32.postimg.org/9237ib6jp/image.png',
           'h': 'https://s32.postimg.org/812yt6pk5/image.png',
           'i': 'https://s32.postimg.org/6nbbxvqat/image.png',
           'j': 'https://s32.postimg.org/axpztgvdx/image.png',
           'k': 'https://s32.postimg.org/976yrzdut/image.png',
           'l': 'https://s32.postimg.org/fmal2e9yd/image.png',
           'm': 'https://s32.postimg.org/m19lz2go5/image.png',
           'n': 'https://s32.postimg.org/b2ycgvs2t/image.png',
           'o': 'https://s32.postimg.org/c6igsucpx/image.png',
           'p': 'https://s32.postimg.org/jnro82291/image.png',
           'q': 'https://s32.postimg.org/ve5lpfv1h/image.png',
           'r': 'https://s32.postimg.org/nmovqvqw5/image.png',
           's': 'https://s32.postimg.org/zd2t89jol/image.png',
           't': 'https://s32.postimg.org/wk9lo8jc5/image.png',
           'u': 'https://s32.postimg.org/w8s5bh2w5/image.png',
           'v': 'https://s32.postimg.org/e7dlrey91/image.png',
           'w': 'https://s32.postimg.org/fnp49k15x/image.png',
           'x': 'https://s32.postimg.org/dkep1w1d1/image.png',
           'y': 'https://s32.postimg.org/um7j3zg85/image.png',
           'z': 'https://s32.postimg.org/jb4vfm9d1/image.png'}


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Todas", action="lista", thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               fanart='https://s18.postimg.org/fwvaeo6qh/todas.png', url=host))

    itemlist.append(
        item.clone(title="Generos", action="seccion", thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                   fanart='https://s3.postimg.org/5s9jg2wtf/generos.png', url=host, extra='generos'))

    itemlist.append(
        item.clone(title="Alfabetico", action="seccion", thumbnail='https://s17.postimg.org/fwi1y99en/a-z.png',
                   fanart='https://s17.postimg.org/fwi1y99en/a-z.png', url=host, extra='letras'))

    itemlist.append(item.clone(title="Buscar", action="search", url=host + '/?s=',
                               thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                               fanart='https://s30.postimg.org/pei7txpa9/buscar.png'))

    return itemlist


def lista(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    if item.extra != 'letras':
        patron = '<li class="TPostMv">.*?<a href="(.*?)"><div class="Image">.*?src="(.*?)\?resize=.*?".*?class="Title">(.*?)<\/h2>.*?'
        patron += '<span class="Year">(.*?)<\/span>.*?<span class="Qlty">(.*?)<\/span><\/p><div class="Description"><p>(.*?)<\/p>'
    else:
        patron = '<td class="MvTbImg"> <a href="(.*?)".*?src="(.*?)\?resize=.*?".*?<strong>(.*?)<\/strong> <\/a><\/td><td>(.*?)<\/td><td>.*?'
        patron += 'class="Qlty">(.*?)<\/span><\/p><\/td><td>(.*?)<\/td><td>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedyear, calidad, scrapedplot in matches:
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = scrapedplot
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
        next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="(.*?)">')
        if next_page != '':
            itemlist.append(Item(channel=item.channel, action="lista", title='Siguiente >>>', url=next_page,
                                 thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'))
    return itemlist


def seccion(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if item.extra == 'generos':
        patron = 'menu-item-object-category menu-item-.*?"><a href="(.*?)">(.*?)<\/a><\/li>'
    else:
        patron = '<li><a href="(.*?\/letter\/.*?)">(.*?)<\/a><\/li>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        thumbnail = ''
        if item.extra == 'generos' and scrapedtitle in tgenero:
            thumbnail = tgenero[scrapedtitle]
        elif scrapedtitle.lower() in tletras:
            thumbnail = tletras[scrapedtitle.lower()]
        fanart = ''
        title = scrapedtitle
        url = scrapedurl

        itemlist.append(
            Item(channel=item.channel, action="lista", title=title, fulltitle=item.title, url=url, thumbnail=thumbnail,
                 fanart=fanart, extra=item.extra))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = 'class="Num">.*?<\/span>.*?href="(.*?)" class="Button STPb">.*?<\/a>.*?<span>(.*?)<\/span><\/td><td><span>(.*?)<\/span><\/td><td><span>.*?<\/span>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    infoLabels = item.infoLabels
    for scrapedurl, servidor, idioma in matches:
        new_item = (item.clone(url=scrapedurl, servidor=servidor, idioma=idioma, infoLabels=infoLabels))
        itemlist += get_video_urls(new_item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                 action="add_pelicula_to_library", extra="findvideos", contentTitle=item.contentTitle))

    itemlist.insert(len(itemlist) - 1, item.clone(channel='trailertools', action='buscartrailer',
                                                  title='[COLOR orange]Trailer en Youtube[/COLOR]'))

    return itemlist


def get_video_urls(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, '<script type="text\/javascript">(.*?)<\/script>')
    data = jsunpack.unpack(data)
    patron = '"file":"(.*?)","label":"(.*?)","type":"video.*?"}'
    subtitle = scrapertools.find_single_match(data, 'tracks:\[{"file":"(.*?)","label":".*?","kind":"captions"}')
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, calidad in matches:
        if item.servidor == 'PELISENCASA':
            item.servidor = 'Directo'
        title = item.contentTitle + ' (' + item.idioma + ')' + ' (' + calidad + ')' + ' (' + item.servidor + ')'
        itemlist.append(item.clone(title=title, url=url, calidad=calidad, action='play', subtitle=subtitle))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    if texto != '':
        return lista(item)
    else:
        return []


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host
        elif categoria == 'infantiles':
            item.url = host + '/category/animacion/'
        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
