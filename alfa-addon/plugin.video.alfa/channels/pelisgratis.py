# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

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
           "Fantasía": "https://s13.postimg.org/65ylohgvb/fantasia.png",
           "Misterio": "https://s1.postimg.org/w7fdgf2vj/misterio.png",
           "Crimen": "https://s4.postimg.org/6z27zhirx/crimen.png",
           "Familia": "https://s7.postimg.org/6s7vdhqrf/familiar.png",
           "Guerra": "https://s4.postimg.org/n1h2jp2jh/guerra.png",
           "Western": "https://s23.postimg.org/lzyfbjzhn/western.png",
           "Historia": "https://s15.postimg.org/fmc050h1n/historia.png"
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

audio = {'Latino': '[COLOR limegreen]LATINO[/COLOR]', 'Español': '[COLOR yellow]ESPAÑOL[/COLOR]',
         'Sub Español': '[COLOR red]SUB ESPAÑOL[/COLOR]'}

host = 'http://pelisgratis.tv/'


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Estrenos",
                               action="lista",
                               thumbnail='https://s21.postimg.org/fy69wzm93/estrenos.png',
                               fanart='https://s21.postimg.org/fy69wzm93/estrenos.png',
                               url=host + 'estrenos'
                               ))

    itemlist.append(item.clone(title="Todas",
                               action="lista",
                               thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               fanart='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               url=host
                               ))

    itemlist.append(item.clone(title="Generos",
                               action="seccion",
                               url=host,
                               thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                               fanart='https://s3.postimg.org/5s9jg2wtf/generos.png',
                               extra='generos'
                               ))

    itemlist.append(item.clone(title="Alfabetico",
                               action="seccion",
                               url=host,
                               thumbnail='https://s17.postimg.org/fwi1y99en/a-z.png',
                               fanart='https://s17.postimg.org/fwi1y99en/a-z.png',
                               extra='a-z'
                               ))

    itemlist.append(item.clone(title="Mas Vistas",
                               action="lista",
                               thumbnail='https://s9.postimg.org/wmhzu9d7z/vistas.png',
                               fanart='https://s9.postimg.org/wmhzu9d7z/vistas.png',
                               url=host + 'peliculas-mas-vistas'
                               ))

    itemlist.append(item.clone(title="Mas Votadas",
                               action="lista",
                               thumbnail='https://s7.postimg.org/9kg1nthzf/votadas.png',
                               fanart='https://s7.postimg.org/9kg1nthzf/votadas.png',
                               url=host + 'peliculas-mas-votadas'
                               ))

    itemlist.append(item.clone(title="Buscar",
                               action="search",
                               url=host + '?s=',
                               thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                               fanart='https://s30.postimg.org/pei7txpa9/buscar.png'
                               ))

    return itemlist


def get_source(url):
    logger.info()
    data = httptools.downloadpage(url, add_referer=True).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    return data


def lista(item):
    logger.info()
    itemlist = []
    data = get_source(item.url)
    patron = 'class=(?:MvTbImg|TPostMv).*?href=(.*?)\/(?:>| class).*?src=(.*?) class=attachment.*?'
    patron += '(?:strong|class=Title)>(.*?)<.*?(?:<td|class=Year)>(.*?)<.*?class=Qlty>(.*?)<.*?'
    patron += '(?:<td|class=Description)>(.*?)<(?:\/td|\/p)>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedyear, scrapedquality, scrapedplot in matches:
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        quality = scrapedquality
        contentTitle = scrapedtitle
        title = contentTitle + ' (%s)' % quality
        year = scrapedyear

        itemlist.append(item.clone(action='findvideos',
                                   title=title,
                                   url=url,
                                   thumbnail=thumbnail,
                                   plot=plot,
                                   contentTitle=contentTitle,
                                   quality=quality,
                                   infoLabels={'year': year}
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # Paginacion

    if itemlist != []:
        actual_page_url = item.url
        next_page = scrapertools.find_single_match(data, '<a class=nextpostslink rel=next href=(.*?)>')
        if next_page != '':
            itemlist.append(item.clone(action="lista",
                                       title='Siguiente >>>',
                                       url=next_page,
                                       thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png'
                                       ))
    return itemlist


def seccion(item):
    logger.info()
    itemlist = []
    data = get_source(item.url)
    if item.extra == 'generos':
        patron = '<li class=cat-item cat-item-.*?><a href=(.*?)>(.*?)<\/li>'
    elif item.extra == 'a-z':
        patron = '<li><a href=(.*?)>(\w|#)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url = scrapedurl
        thumbnail = ''
        if item.extra == 'generos':
            title = re.sub(r'<\/a> \(\d+\)', '', scrapedtitle)
            cantidad = re.findall(r'.*?<\/a> \((\d+)\)', scrapedtitle)
            th_title = title
            title = title + ' (' + cantidad[0] + ')'
            if th_title in tgenero:
                thumbnail = tgenero[th_title]
        else:
            title = scrapedtitle
            if title.lower() in thumbletras:
                thumbnail = thumbletras[title.lower()]

        itemlist.append(item.clone(action='lista', title=title, url=url, thumbnail=thumbnail))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    if texto != '':
        return lista(item)


def findvideos(item):
    logger.info()
    itemlist = []
    duplicados = []

    data = get_source(item.url)
    data = data.replace('amp;', '')
    data_page = data

    patron = 'class=TPlayerTb  id=(.*?)>&lt;iframe width=&quot;560&quot; height=&quot;315&quot; src=&quot;(.*?)&quot;'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for option, video_page in matches:
        language = scrapertools.find_single_match(data_page, 'TPlayerNv=%s><span>.*?<center>(.*?)<\/center>' % option)
        if language == 'Castellano':
            language = 'Español'
        if language in audio:
            id_audio = audio[language]
        else:
            id_audio = language
        if 'redirect' in video_page or 'yourplayer' in video_page:
            data = get_source('http:%s' % video_page)

            patron = 'label:(.*?),.*?file:(.*?)&app.*?}'
            matches = re.compile(patron, re.DOTALL).findall(data)
            for video_url in matches:

                url = video_url[1]
                url = url.replace('\/', '/')
                title = item.contentTitle + ' [%s][%s]' % (video_url[0], id_audio)
                server = 'directo'
                if url not in duplicados:
                    itemlist.append(item.clone(action='play',
                                               title=title,
                                               url=url,
                                               server=server
                                               ))
                    duplicados.append(url)
        else:
            if video_page not in duplicados:
                itemlist.extend(servertools.find_video_items(data=video_page))
                duplicados.append(video_page)

        for video_item in itemlist:
            if video_item.server != 'directo':
                video_item.channel = item.channel
                video_item.quality = item.quality
                video_item.title = item.contentTitle + ' [%s][%s]' % (video_item.server, id_audio)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(item.clone(title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                                   url=item.url,
                                   action="add_pelicula_to_library",
                                   extra="findvideos",
                                   contentTitle=item.contentTitle
                                   ))
    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    # categoria='peliculas'
    try:
        if categoria == 'peliculas':
            item.url = host + 'estrenos'
        elif categoria == 'infantiles':
            item.url = host + 'animacion'
        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
