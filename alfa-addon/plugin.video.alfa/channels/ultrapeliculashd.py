# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

host = 'http://www.ultrapeliculashd.com'

tgenero = {"ACCIÓN": "https://s3.postimg.org/y6o9puflv/accion.png,",
           "ANIMACIÓN": "https://s13.postimg.org/5on877l87/animacion.png",
           "AVENTURA": "https://s10.postimg.org/6su40czih/aventura.png",
           "CIENCIA FICCIÓN": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png",
           "COMEDIA": "https://s7.postimg.org/ne9g9zgwb/comedia.png",
           "CRIMEN": "https://s4.postimg.org/6z27zhirx/crimen.png",
           "DRAMA": "https://s16.postimg.org/94sia332d/drama.png",
           "ESTRENOS": "https://s21.postimg.org/fy69wzm93/estrenos.png",
           "FAMILIA": "https://s7.postimg.org/6s7vdhqrf/familiar.png",
           "FANTASÍA": "https://s13.postimg.org/65ylohgvb/fantasia.png",
           "GUERRA": "https://s4.postimg.org/n1h2jp2jh/guerra.png",
           "INFANTIL": "https://s23.postimg.org/g5rmazozv/infantil.png",
           "MISTERIO": "https://s1.postimg.org/w7fdgf2vj/misterio.png",
           "ROMANCE": "https://s15.postimg.org/fb5j8cl63/romance.png",
           "SUSPENSO": "https://s13.postimg.org/wmw6vl1cn/suspenso.png",
           "TERROR": "https://s7.postimg.org/yi0gij3gb/terror.png"
           }

thumbletras = {'#': 'https://s32.postimg.org/drojt686d/image.png',
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
               'z': 'https://s32.postimg.org/jb4vfm9d1/image.png'
               }

tcalidad = {'1080P': 'https://s21.postimg.org/4h1s0t1wn/hd1080.png',
            '720P': 'https://s12.postimg.org/lthu7v4q5/hd720.png', "HD": "https://s27.postimg.org/m2dhhkrur/image.png"}


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Todas",
                               action="lista",
                               thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               fanart='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               url=host + '/movies/'
                               ))

    itemlist.append(item.clone(title="Generos",
                               action="generos",
                               url=host,
                               thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                               fanart='https://s3.postimg.org/5s9jg2wtf/generos.png'
                               ))

    itemlist.append(item.clone(title="Alfabetico",
                               action="seccion",
                               url=host,
                               thumbnail='https://s17.postimg.org/fwi1y99en/a-z.png',
                               fanart='https://s17.postimg.org/fwi1y99en/a-z.png',
                               extra='alfabetico'
                               ))

    itemlist.append(item.clone(title="Buscar",
                               action="search",
                               url=host + '/?s=',
                               thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                               fanart='https://s30.postimg.org/pei7txpa9/buscar.png'
                               ))

    return itemlist


def lista(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    if item.extra != 'buscar':
        patron = '<article id=post-.*? class=item movies><div class=poster><a href=(.*?)><img src=(.*?) '
        patron += 'alt=(.*?)>.*?quality>.*?<.*?<\/h3><span>(.*?)<\/span>'
    else:
        patron = '<article><div class=image>.*?<a href=(.*?)\/><img src=(.*?) alt=(.*?) \/>.*?year>(.*?)<\/span>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedyear in matches:
        url = scrapedurl
        thumbnail = scrapedthumbnail
        contentTitle = re.sub(r'\d{4}', '', scrapedtitle)
        contentTitle = contentTitle.replace('|', '')
        contentTitle = contentTitle.strip(' ')
        title = scrapertools.decodeHtmlentities(contentTitle)
        year = scrapedyear
        fanart = ''
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, fulltitle=item.title, url=url,
                             thumbnail=thumbnail, fanart=fanart, contentTitle=contentTitle, infoLabels={'year': year}))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # Paginacion

    if itemlist != []:
        actual_page_url = item.url
        next_page = scrapertools.find_single_match(data, '<div class=pag_b><a href=(.*?) >Siguiente<\/a>')
        if next_page != '':
            itemlist.append(Item(channel=item.channel, action="lista", title='Siguiente >>>', url=next_page,
                                 thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    patron = '<li class=cat-item cat-item-.*?><a href=(.*?) >(.*?)<\/a> <i>(.*?)<\/i><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, cantidad in matches:
        thumbnail = ''
        fanart = ''
        if scrapedtitle in tgenero:
            thumbnail = tgenero[scrapedtitle]
        title = scrapedtitle + ' (' + cantidad + ')'
        url = scrapedurl
        if scrapedtitle not in ['PRÓXIMAMENTE', 'EN CINE']:
            itemlist.append(item.clone(action="lista",
                                       title=title,
                                       fulltitle=item.title,
                                       url=url,
                                       thumbnail=thumbnail,
                                       fanart=fanart
                                       ))
    return itemlist


def seccion(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    if item.extra == 'year':
        patron = '<li><a href=(.*?\/fecha-estreno.*?)>(.*?)<\/a>'
    else:
        patron = '<li><a href=(.*?) >(.*?)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        thumbnail = ''
        if scrapedtitle.lower() in thumbletras:
            thumbnail = thumbletras[scrapedtitle.lower()]
        fanart = ''
        title = scrapedtitle
        url = scrapedurl

        itemlist.append(
            Item(channel=item.channel, action="lista", title=title, fulltitle=item.title, url=url, thumbnail=thumbnail,
                 fanart=fanart))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    patron = '<iframe class=metaframe rptss src=(.*?) frameborder=0 allowfullscreen><\/iframe>'
    matches = matches = re.compile(patron, re.DOTALL).findall(data)
    for videoitem in matches:
        itemlist.extend(servertools.find_video_items(data=videoitem))

    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.action = 'play'
        videoitem.thumbnail = servertools.guess_server_thumbnail(videoitem.server)
        videoitem.infoLabels = item.infoLabels
        videoitem.title = item.contentTitle + ' (' + videoitem.server + ')'
        if 'youtube' in videoitem.url:
            videoitem.title = '[COLOR orange]Trailer en Youtube[/COLOR]'

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                 action="add_pelicula_to_library", extra="findvideos", contentTitle=item.contentTitle))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    try:
        if texto != '':
            item.extra = 'buscar'
            return lista(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    item.extra = 'estrenos/'
    try:
        if categoria == 'peliculas':
            item.url = host + '/category/estrenos/'

        elif categoria == 'infantiles':
            item.url = host + '/category/infantil/'

        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
