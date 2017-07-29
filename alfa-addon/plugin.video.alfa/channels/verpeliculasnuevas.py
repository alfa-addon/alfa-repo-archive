# -*- coding: utf-8 -*-

import re

from channels import autoplay
from channels import filtertools
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

host = 'http://verpeliculasnuevas.com'

IDIOMAS = {'latino': 'Latino', 'castellano': 'Español', 'sub': 'VOS'}
list_language = IDIOMAS.values()

taudio = {'latino': '[COLOR limegreen]LATINO[/COLOR]',
          'castellano': '[COLOR yellow]ESPAÑOL[/COLOR]',
          'sub': '[COLOR red]ORIGINAL SUBTITULADO[/COLOR]',
          'castellanolatinosub': '[COLOR orange]MULTI[/COLOR]',
          'castellanolatino': '[COLOR orange]MULTI[/COLOR]'
          }

thumbaudio = {'latino': 'http://flags.fmcdn.net/data/flags/normal/mx.png',
              'castellano': 'http://flags.fmcdn.net/data/flags/normal/es.png',
              'sub': 'https://s32.postimg.org/nzstk8z11/sub.png'
              }

list_quality = ['HQ',
                'HD',
                'HD-1080',
                'DVD',
                'CAM'
                ]
list_servers = [
    'openload',
    'powvideo',
    'streamplay',
    'streaminto',
    'netu',
    'vidabc',
    'thevideos',
    'yourupload',
    'thevideome',
    'directo',
    'netutv'
]

tcalidad = {'hq': '[COLOR limegreen]HQ[/COLOR]',
            'hd': '[COLOR limegreen]HD[/COLOR]',
            'hd-1080': '[COLOR limegreen]HD-1080[/COLOR]',
            'dvd': '[COLOR limegreen]DVD[/COLOR]',
            'cam': '[COLOR red]CAM[/COLOR]'
            }

thumbcalidad = {'hd-1080': 'https://s21.postimg.org/4h1s0t1wn/hd1080.png',
                'dvd': 'https://s1.postimg.org/m89hus1tb/dvd.png',
                'cam': 'https://s11.postimg.org/ad4o5wpz7/cam.png',
                'hq': 'https://s23.postimg.org/j76ldf8qz/image.png',
                'hd': 'https://s27.postimg.org/m2dhhkrur/image.png'
                }

thumbletras = {'0-9': 'https://s32.postimg.org/drojt686d/image.png', '1': 'https://s32.postimg.org/drojt686d/image.png',
               'a': 'https://s32.postimg.org/llp5ekfz9/image.png', 'b': 'https://s32.postimg.org/y1qgm1yp1/image.png',
               'c': 'https://s32.postimg.org/vlon87gmd/image.png', 'd': 'https://s32.postimg.org/3zlvnix9h/image.png',
               'e': 'https://s32.postimg.org/bgv32qmsl/image.png', 'f': 'https://s32.postimg.org/y6u7vq605/image.png',
               'g': 'https://s32.postimg.org/9237ib6jp/image.png', 'h': 'https://s32.postimg.org/812yt6pk5/image.png',
               'i': 'https://s32.postimg.org/6nbbxvqat/image.png', 'j': 'https://s32.postimg.org/axpztgvdx/image.png',
               'k': 'https://s32.postimg.org/976yrzdut/image.png', 'l': 'https://s32.postimg.org/fmal2e9yd/image.png',
               'm': 'https://s32.postimg.org/m19lz2go5/image.png', 'n': 'https://s32.postimg.org/b2ycgvs2t/image.png',
               "ñ": "https://s30.postimg.org/ayy8g02xd/image.png", 'o': 'https://s32.postimg.org/c6igsucpx/image.png',
               'p': 'https://s32.postimg.org/jnro82291/image.png', 'q': 'https://s32.postimg.org/ve5lpfv1h/image.png',
               'r': 'https://s32.postimg.org/nmovqvqw5/image.png', 's': 'https://s32.postimg.org/zd2t89jol/image.png',
               't': 'https://s32.postimg.org/wk9lo8jc5/image.png', 'u': 'https://s32.postimg.org/w8s5bh2w5/image.png',
               'v': 'https://s32.postimg.org/e7dlrey91/image.png', 'w': 'https://s32.postimg.org/fnp49k15x/image.png',
               'x': 'https://s32.postimg.org/dkep1w1d1/image.png', 'y': 'https://s32.postimg.org/um7j3zg85/image.png',
               'z': 'https://s32.postimg.org/jb4vfm9d1/image.png'}

tgenero = {"comedia": "https://s7.postimg.org/ne9g9zgwb/comedia.png",
           "suspenso": "https://s13.postimg.org/wmw6vl1cn/suspenso.png",
           "drama": "https://s16.postimg.org/94sia332d/drama.png",
           "accion": "https://s3.postimg.org/y6o9puflv/accion.png",
           "aventura": "https://s10.postimg.org/6su40czih/aventura.png",
           "romance": "https://s15.postimg.org/fb5j8cl63/romance.png",
           "thriller": "https://s22.postimg.org/5y9g0jsu9/thriller.png",
           "ciencia-ficcion": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png",
           "terror": "https://s7.postimg.org/yi0gij3gb/terror.png",
           "documental": "https://s16.postimg.org/7xjj4bmol/documental.png",
           "musical": "https://s29.postimg.org/bbxmdh9c7/musical.png",
           "fantastico": "https://s10.postimg.org/pbkbs6j55/fantastico.png",
           "deporte": "https://s13.postimg.org/xuxf5h06v/deporte.png",
           "infantil": "https://s23.postimg.org/g5rmazozv/infantil.png",
           "animacion": "https://s13.postimg.org/5on877l87/animacion.png"
           }

patrones = ['', '<span class="clms">Sinopsis:<\/span>([^<]+)<div class="info_movie">']


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(
        item.clone(title="Todas",
                   action="lista",
                   thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                   fanart='https://s18.postimg.org/fwvaeo6qh/todas.png',
                   extra='peliculas/',
                   url=host
                   ))

    itemlist.append(
        itemlist[-1].clone(title="Generos",
                           action="menuseccion",
                           thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                           fanart='https://s3.postimg.org/5s9jg2wtf/generos.png',
                           url=host,
                           extra='/genero'
                           ))

    itemlist.append(
        itemlist[-1].clone(title="Alfabetico",
                           action="menuseccion",
                           thumbnail='https://s17.postimg.org/fwi1y99en/a-z.png',
                           fanart='https://s17.postimg.org/fwi1y99en/a-z.png',
                           url=host, extra='/tag'
                           ))

    itemlist.append(
        itemlist[-1].clone(title="Audio",
                           action="menuseccion",
                           thumbnail='https://s27.postimg.org/avs17iuw3/audio.png',
                           fanart='https://s27.postimg.org/avs17iuw3/audio.png',
                           url=host,
                           extra='/audio'
                           ))

    itemlist.append(
        itemlist[-1].clone(title="Calidad",
                           action="menuseccion",
                           thumbnail='https://s13.postimg.org/6nzv8nlkn/calidad.png',
                           fanart='https://s13.postimg.org/6nzv8nlkn/calidad.png',
                           extra='/calidad'
                           ))

    itemlist.append(
        itemlist[-1].clone(title="Año",
                           action="menuseccion",
                           thumbnail='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                           fanart='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                           url=host,
                           extra='/fecha-estreno'
                           ))

    itemlist.append(
        itemlist[-1].clone(title="Buscar",
                           action="search",
                           url=host + '?s=',
                           thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                           fanart='https://s30.postimg.org/pei7txpa9/buscar.png'
                           ))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def menuseccion(item):
    logger.info()
    itemlist = []
    seccion = item.extra
    data = httptools.downloadpage(item.url).data

    if seccion == '/audio':
        patron = "<a href='\/audio([^']+)' title='lista de películas en.*?'>(?:Español|Latino|Subtitulado)<\/a>"
    elif seccion == '/calidad':
        patron = "<a href='\/calidad([^']+)' title='lista de películas en.*?'>(?:HD-1080|HD-Real|DvD|HQ|CAM)<\/a>"
    elif seccion == '/fecha-estreno':
        patron = "<a href='\/fecha-estreno([^']+)' title='lista de películas del.*?'>.*?<\/a>"
    elif seccion == '/genero':
        patron = '<a href="\/genero([^"]+)">.*?<\/a><\/li>'
    else:
        patron = "<a href='\/tag([^']+)' title='lista de películas.*?'>.*?<\/a>"

    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:

        url = host + seccion + scrapedurl
        titulo = scrapedurl.replace('/', '')

        if seccion == '/audio':
            title = taudio[titulo.lower()]
            thumbnail = thumbaudio[titulo]
        elif seccion == '/calidad':
            title = tcalidad[titulo.lower()]
            thumbnail = thumbcalidad[titulo]
        elif seccion == '/tag':
            title = titulo.upper()
            if titulo in thumbletras:
                thumbnail = thumbletras[titulo]
            else:
                thumbnail = ''
        else:
            title = titulo.upper()
            if titulo in tgenero:
                thumbnail = tgenero[titulo]
            else:
                thumbnail = ''

        itemlist.append(
            Item(channel=item.channel,
                 action='lista',
                 title=title,
                 url=url,
                 thumbnail=thumbnail
                 ))

    return itemlist


def lista(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>', "", data)

    patron = "peli><a href=([^ ]+) title=(.*?)><img src=([^ ]+) alt=.*?><div class=([^>]+)>.*?<p>.*?<\/p>.*?flags ([" \
             "^']+)'"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedcalidad, scrapedidioma in matches:
        year = scrapertools.find_single_match(scrapedtitle, '.*?\((\d{4})\)')
        scrapedtitle = scrapertools.find_single_match(scrapedtitle, '(.*?)\(\.*?')
        url = scrapedurl
        thumbnail = scrapedthumbnail
        scrapedcalidad = scrapedcalidad.replace("'", "")
        scrapedcalidad = scrapedcalidad.lower()

        if scrapedcalidad in tcalidad:
            scrapedcalidad = tcalidad[scrapedcalidad]
        else:
            scrapedcalidad = '[COLOR orange]MULTI[/COLOR]'

        if scrapedidioma in taudio:
            scrapedidioma = taudio[scrapedidioma]
        else:
            scrapedidioma = '[COLOR orange]MULTI[/COLOR]'

        title = scrapedtitle + ' | ' + scrapedcalidad + ' | ' + scrapedidioma + ' | '
        fanart = ''
        plot = ''

        itemlist.append(
            Item(channel=item.channel,
                 action='findvideos',
                 title=title,
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 fanart=fanart,
                 contentTitle=scrapedtitle,
                 extra=item.extra,
                 infoLabels={'year': year},
                 show=scrapedtitle,
                 list_language=list_language,
                 context=autoplay.context
                 ))

    # #Paginacion
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    itemlist = fail_tmdb(itemlist)
    if itemlist != []:
        actual_page_url = item.url
        next_page = scrapertools.find_single_match(data,
                                                   "class=previouspostslink' href='([^']+)'>Siguiente &rsaquo;<\/a>")
        if next_page != '':
            itemlist.append(
                Item(channel=item.channel,
                     action="lista",
                     title='Siguiente >>>',
                     url=next_page,
                     thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png',
                     extra=item.extra
                     ))

    return itemlist


def fail_tmdb(itemlist):
    logger.info()
    realplot = ''
    for item in itemlist:
        if item.infoLabels['plot'] == '':
            data = httptools.downloadpage(item.url).data
            if item.thumbnail == '':
                item.thumbnail = scrapertools.find_single_match(data, patrones[0])
            realplot = scrapertools.find_single_match(data, patrones[1])
            item.plot = scrapertools.remove_htmltags(realplot)
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    if texto != '':
        return lista(item)
    else:
        return []


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"'|\n|\r|\t|&nbsp;|<br>", "", data)

    patron = 'class="servidor" alt=""> ([^<]+)<\/span><span style="width: 40px;">([^<]+)<\/span><a class="verLink" ' \
             'rel="nofollow" href="([^"]+)" target="_blank"> <img title="Ver online gratis"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedidioma, scrapedcalidad, scrapedurl in matches:

        scrapedidioma = scrapertools.decodeHtmlentities(scrapedidioma)

        scrapedcalidad = scrapertools.decodeHtmlentities(scrapedcalidad)
        if scrapedidioma.lower() == 'español':
            scrapedidioma = 'castellano'
        scrapedidioma = scrapedidioma.lower()
        idioma = taudio[scrapedidioma.lower()]
        calidad = tcalidad[scrapedcalidad.lower()]
        url = scrapedurl
        itemlist.append(
            item.clone(action='play',
                       idioma=idioma,
                       calidad=calidad,
                       url=url,
                       language=IDIOMAS[scrapedidioma.lower()],
                       quality=scrapedcalidad
                       ))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda
        i: item.contentTitle + ' | ' + i.calidad + ' | ' + i.idioma + ' (' + i.server + ')', True)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(
            Item(channel=item.channel,
                 title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
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
            item.url = host
        elif categoria == 'infantiles':
            item.url = host + '/genero/infantil/'
        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
