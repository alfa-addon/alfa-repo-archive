# -*- coding: utf-8 -*-

import re
import urlparse

from channels import autoplay
from channels import filtertools
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import tmdb
from core.item import Item

IDIOMAS = {'Latino': 'Latino', 'Español': 'Español', 'Sub español': 'VOS'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = [
    'openload',
]

host = 'http://www.locopelis.com/'

audio = {'Latino': '[COLOR limegreen]LATINO[/COLOR]', 'Español': '[COLOR yellow]ESPAÑOL[/COLOR]',
         'Sub Español': '[COLOR red]SUB ESPAÑOL[/COLOR]'}


def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(Item(channel=item.channel,
                         title="Peliculas",
                         action="todas",
                         url=host,
                         thumbnail='https://s8.postimg.org/6wqwy2c2t/peliculas.png',
                         fanart='https://s8.postimg.org/6wqwy2c2t/peliculas.png'
                         ))

    itemlist.append(Item(channel=item.channel,
                         title="Generos",
                         action="generos",
                         url=host,
                         thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                         fanart='https://s3.postimg.org/5s9jg2wtf/generos.png'
                         ))

    itemlist.append(Item(channel=item.channel,
                         title="Alfabetico",
                         action="letras",
                         url=host,
                         thumbnail='https://s17.postimg.org/fwi1y99en/a-z.png',
                         fanart='https://s17.postimg.org/fwi1y99en/a-z.png',
                         extra='letras'
                         ))

    itemlist.append(Item(channel=item.channel,
                         title="Ultimas Agregadas",
                         action="ultimas",
                         url=host,
                         thumbnail='https://s22.postimg.org/cb7nmhwv5/ultimas.png',
                         fanart='https://s22.postimg.org/cb7nmhwv5/ultimas.png'
                         ))

    itemlist.append(Item(channel=item.channel,
                         title="Mas Vistas",
                         action="todas",
                         url=host + 'pelicula/peliculas-mas-vistas',
                         thumbnail='https://s9.postimg.org/wmhzu9d7z/vistas.png',
                         fanart='https://s9.postimg.org/wmhzu9d7z/vistas.png'
                         ))

    itemlist.append(Item(channel=item.channel,
                         title="Mas Votadas",
                         action="todas",
                         url=host + 'pelicula/peliculas-mas-votadas',
                         thumbnail='https://s7.postimg.org/9kg1nthzf/votadas.png',
                         fanart='https://s7.postimg.org/9kg1nthzf/votadas.png'
                         ))

    itemlist.append(Item(channel=item.channel,
                         title="Estrenos DVD",
                         action="todas",
                         url=host + 'pelicula/ultimas-peliculas/estrenos-dvd',
                         thumbnail='https://s1.postimg.org/m89hus1tb/dvd.png',
                         fanart='https://s1.postimg.org/m89hus1tb/dvd.png'
                         ))

    itemlist.append(Item(channel=item.channel,
                         title="Actualizadas",
                         action="todas",
                         url=host + 'pelicula/ultimas-peliculas/ultimas/actualizadas',
                         thumbnail='https://s16.postimg.org/57evw0wo5/actualizadas.png',
                         fanart='https://s16.postimg.org/57evw0wo5/actualizadas.png'
                         ))

    itemlist.append(Item(channel=item.channel,
                         title="Buscar",
                         action="search",
                         url=host + '/buscar/?q=',
                         thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                         fanart='https://s30.postimg.org/pei7txpa9/buscar.png'
                         ))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def todas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)

    patron = '<h2 class="titpeli bold ico_b">.*?<\/h2>.*?'
    patron += '<a href="([^"]+)" title="([^"]+)">.*?'
    patron += '<img src="([^"]+)" alt=.*?><\/a>.*?'
    patron += '<p>([^<]+)<\/p>.*?'
    patron += '<div class="stars f_left pdtop10px"><strong>Genero<\/strong>:.*?, (.*?)<\/div>.*?'
    patron += '<div class=.*?>Idioma<\/strong>:.*?img src=.*?>([^<]+)<\/div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedplot, scrapedyear, scrapedidioma in matches:

        year = scrapedyear
        idioma_id = scrapertools.decodeHtmlentities(scrapedidioma.strip())
        idioma = scrapertools.decodeHtmlentities(idioma_id)
        # if idioma == 'Espa&ntilde;ol':
        #    idioma ='Español'
        logger.debug('idioma original: %s' % idioma_id)
        logger.debug('idioma: %s' % idioma)
        if idioma in audio:
            idioma = audio[idioma]

        url = scrapedurl
        if idioma != '':
            title = scrapedtitle + ' (' + idioma + ')' + ' (' + year + ')'
        else:
            title = scrapedtitle + ' (' + year + ')'
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        contentTitle = scrapedtitle
        fanart = 'https://s31.postimg.org/5worjw2nv/locopelis.png'

        itemlist.append(Item(channel=item.channel,
                             action="findvideos",
                             title=title,
                             url=url,
                             thumbnail=thumbnail,
                             plot=plot,
                             fanart=fanart,
                             extra=idioma,
                             contentTitle=contentTitle,
                             infoLabels={'year': year},
                             language=idioma_id,
                             context=autoplay.context
                             ))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # Paginacion
    siguiente = ''
    title = ''
    data = scrapertools.find_single_match(data, '<ul class="nav.*?\/ul>')
    actual = scrapertools.find_single_match(data, '<a href="(\?page=\d|.*?&page=\d*)"><span><b>(.*?)<\/b>')
    if actual:
        base_url = item.url + actual[0]
        while not base_url.endswith('='): base_url = base_url[:-1]
        siguiente = int(actual[1]) + 1
        if base_url.endswith('='):
            siguiente_url = base_url + str(siguiente)
        titlen = 'Pagina Siguiente >>> '
        fanart = 'https://s31.postimg.org/5worjw2nv/locopelis.png'
        itemlist.append(Item(channel=item.channel,
                             action="todas",
                             title=titlen,
                             url=siguiente_url,
                             fanart=fanart
                             ))

    return itemlist


def generos(item):
    tgenero = {"comedia": "https://s7.postimg.org/ne9g9zgwb/comedia.png",
               "suspenso": "https://s13.postimg.org/wmw6vl1cn/suspenso.png",
               "drama": "https://s16.postimg.org/94sia332d/drama.png",
               "accion": "https://s3.postimg.org/y6o9puflv/accion.png",
               "aventura": "https://s10.postimg.org/6su40czih/aventura.png",
               "romance": "https://s15.postimg.org/fb5j8cl63/romance.png",
               "animacion e infantil": "https://s13.postimg.org/5on877l87/animacion.png",
               "ciencia ficcion": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png",
               "terror": "https://s7.postimg.org/yi0gij3gb/terror.png",
               "anime": 'https://s2.postimg.org/s38borokp/anime.png',
               "documentales": "https://s16.postimg.org/7xjj4bmol/documental.png",
               "intriga": "https://s27.postimg.org/v9og43u2b/intriga.png",
               "musical": "https://s29.postimg.org/bbxmdh9c7/musical.png",
               "western": "https://s23.postimg.org/lzyfbjzhn/western.png",
               "fantasia": "https://s13.postimg.org/65ylohgvb/fantasia.png",
               "asiaticas": "https://s4.postimg.org/oo8txm8od/asiatica.png",
               "bélico (guerra)": "https://s23.postimg.org/71itp9hcr/belica.png",
               "deporte": "https://s13.postimg.org/xuxf5h06v/deporte.png",
               "adolescente": "https://s27.postimg.org/713imu3j7/adolescente.png",
               "artes marciales": "https://s24.postimg.org/w1aw45j5h/artesmarciales.png",
               "cine negro": "https://s27.postimg.org/absaoxx83/cinenegro.png",
               "eroticas +18": "https://s15.postimg.org/exz7kysjf/erotica.png",
               "hindu": "https://s28.postimg.org/ljn3fxf8d/hindu.png",
               "religiosas": "https://s7.postimg.org/llo852fwr/religiosa.png",
               "vampiros": "https://s22.postimg.org/3x69mu1fl/vampiros.png",
               "zombies": "https://s28.postimg.org/dnn5haqml/zombies.png"}

    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<li><a title.*?href="http:\/\/www.locopelis.com\/categoria\/([^"]+)">([^<]+)<\/a><\/li>.*?'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url = urlparse.urljoin(item.url, 'http://www.locopelis.com/categoria/' + scrapedurl)
        title = scrapedtitle.decode('cp1252')
        title = title.encode('utf-8')
        if title.lower() in tgenero:
            thumbnail = tgenero[title.lower()]
            fanart = tgenero[title.lower()]
        else:
            thumbnail = ''
            fanart = ''
        plot = ''
        itemlist.append(Item(channel=item.channel,
                             action="todas",
                             title=title.lower(),
                             fulltitle=item.fulltitle,
                             url=url,
                             thumbnail=thumbnail,
                             plot=plot,
                             fanart=fanart
                             ))

    return itemlist


def ultimas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    data = data.decode('cp1252')
    realplot = ''
    patron = '<a href="([^"]+)" title="([^"]+)"><img src="([^"]+)" alt=.*? style="width:105px; height:160px; ' \
             'border:1px solid #999"\/><\/a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = ''
        title = scrapedtitle
        fanart = 'https://s22.postimg.org/cb7nmhwv5/ultimas.png'
        itemlist.append(Item(channel=item.channel,
                             action="findvideos",
                             title=title,
                             url=url,
                             thumbnail=thumbnail,
                             plot=plot,
                             fanart=fanart
                             ))

    return itemlist


def letras(item):
    thumbletras = {'0-9': 'https://s32.postimg.org/drojt686d/image.png',
                   '0 - 9': 'https://s32.postimg.org/drojt686d/image.png',
                   '#': 'https://s32.postimg.org/drojt686d/image.png',
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

    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    data = data.decode('cp1252')
    data = scrapertools.find_single_match(data, '<\/form><\/table><\/div>.*?<\/ul>')

    patron = '<li><a href="(.*?)" title="Letra.*?">(.*?)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url = scrapedurl
        title = scrapedtitle
        plot = ''
        if scrapedtitle.lower() in thumbletras:
            thumbnail = thumbletras[scrapedtitle.lower()]
        else:
            thumbnail = ''
        itemlist.append(Item(channel=item.channel,
                             action='todas',
                             title=title,
                             url=url,
                             thumbnail=thumbnail,
                             plot=plot
                             ))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    if texto != '':
        return todas(item)
    else:
        return []


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data

    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    if item.language == 'Espa&ntilde;ol':
        item.language == 'Español'
    for videoitem in itemlist:
        videoitem.language = IDIOMAS[item.language]
        videoitem.title = item.contentTitle + ' (' + videoitem.server + ') (' + videoitem.language + ')'
        videoitem.channel = item.channel
        videoitem.folder = False
        videoitem.extra = item.thumbnail
        videoitem.fulltitle = item.title
        videoitem.quality = 'default'

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_pelicula_to_library",
                             extra="findvideos",
                             contentTitle=item.contentTitle
                             ))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    from core import servertools
    itemlist.extend(servertools.find_video_items(data=item.url))
    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.title = item.title
        videoitem.folder = False
        videoitem.thumbnail = item.extra
        videoitem.fulltitle = item.fulltitle
        videoitem.infoLabels = item.infoLabels
    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    # categoria='peliculas'
    try:
        if categoria == 'peliculas':
            item.url = host
            item.extra = 'peliculas'
        elif categoria == 'infantiles':
            item.url = host + 'categoria/animacion-e-infantil/'
            item.extra = 'peliculas'
        itemlist = todas(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
