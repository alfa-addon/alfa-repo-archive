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
           "Western": "https://s23.postimg.org/lzyfbjzhn/western.png",
           "Fantasía": "https://s13.postimg.org/65ylohgvb/fantasia.png",
           "Guerra": "https://s4.postimg.org/n1h2jp2jh/guerra.png",
           "Misterio": "https://s1.postimg.org/w7fdgf2vj/misterio.png",
           "Crimen": "https://s4.postimg.org/6z27zhirx/crimen.png",
           "Historia": "https://s15.postimg.org/fmc050h1n/historia.png",
           "película de la televisión": "https://s9.postimg.org/t8xb14fb3/delatv.png",
           "Action & Adventure": "https://s4.postimg.org/neu65orz1/action_adventure.png",
           "Sci-Fi & Fantasy": "https://s23.postimg.org/ys5if2oez/scifi_fantasy.png",
           "Suspenso": "https://s13.postimg.org/wmw6vl1cn/suspenso.png",
           "Familia": "https://s7.postimg.org/6s7vdhqrf/familiar.png",
           "Foreign": "https://s29.postimg.org/jdc2m158n/extranjera.png",
           "Cartelera MDT": "https://s1.postimg.org/6yle12szj/cartelera.png",
           "Romanticas": "https://s21.postimg.org/xfsj7ua0n/romantica.png"
           }

tcalidad = {"FULL HD": "https://s18.postimg.org/qszt3n6tl/fullhd.png",
            "HD": "https://s27.postimg.org/m2dhhkrur/image.png",
            "SD": "https://s29.postimg.org/l66t2pfqf/image.png"
            }
host = 'http://miradetodo.io/'


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Peliculas",
                               action="menu_peliculas",
                               thumbnail='https://s8.postimg.org/6wqwy2c2t/peliculas.png',
                               fanart='https://s8.postimg.org/6wqwy2c2t/peliculas.png'
                               ))

    itemlist.append(item.clone(title="Series",
                               action="menu_series",
                               thumbnail='https://s27.postimg.org/iahczwgrn/series.png',
                               fanart='https://s27.postimg.org/iahczwgrn/series.png',
                               ))

    itemlist.append(item.clone(title="Buscar", action="search",
                               thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                               fanart='https://s30.postimg.org/pei7txpa9/buscar.png',
                               url=host + '?s='
                               ))

    return itemlist


def menu_peliculas(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Todas",
                               action="lista",
                               thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               fanart='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               url=host + 'page/1/?s'
                               ))

    itemlist.append(item.clone(title="Generos",
                               action="seccion",
                               url=host + 'page/1/?s',
                               thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                               fanart='https://s3.postimg.org/5s9jg2wtf/generos.png',
                               seccion='generos-pelicula'
                               ))

    itemlist.append(item.clone(title="Por Año",
                               action="seccion",
                               url=host + 'page/1/?s',
                               thumbnail='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                               fanart='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                               seccion='fecha-estreno'
                               ))

    itemlist.append(item.clone(title="Calidad",
                               action="seccion",
                               url=host + 'page/1/?s',
                               thumbnail='https://s13.postimg.org/6nzv8nlkn/calidad.png',
                               fanart='https://s13.postimg.org/6nzv8nlkn/calidad.png',
                               seccion='calidad'
                               ))

    return itemlist


def menu_series(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Todas",
                               action="lista",
                               thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               fanart='https://s18.postimg.org/fwvaeo6qh/todas.png',
                               url=host + 'series/page/1/',
                               ))

    itemlist.append(item.clone(title="Generos",
                               action="seccion",
                               url=host + 'series/page/1/',
                               thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                               fanart='https://s3.postimg.org/5s9jg2wtf/generos.png',
                               seccion='generos-serie'
                               ))

    itemlist.append(item.clone(title="Por Año",
                               action="seccion",
                               url=host + 'series/page/1/',
                               thumbnail='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                               fanart='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                               seccion='series-lanzamiento'
                               ))

    return itemlist


def lista(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)
    patron = 'class=item>.*?<a href=(.*?)><div class=image>.*?<img src=(.*?) alt=(.*?) \(\d{4}.*?ttx>(.*?)'
    patron += '<div class=degradado>.*?fixyear><h2>.*?<\/h2>.*?<span class=year>(.*?)<\/span><\/div>(.*?)<\/div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot, scrapedyear, scrapedquality in matches:
        url = scrapedurl
        action = 'findvideos'
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        contentSerieName = ''
        contentTitle = scrapedtitle
        title = contentTitle
        if scrapedquality != '':
            quality = scrapertools.find_single_match(scrapedquality, 'calidad2>(.*?)<')
            title = contentTitle + ' (%s)' % quality
        year = scrapedyear

        if 'series' in item.url or 'series' in url:
            action = 'temporadas'
            contentSerieName = contentTitle
            contentTitle = ''
            quality = ''

        itemlist.append(Item(channel=item.channel,
                             action=action,
                             title=title,
                             url=url,
                             thumbnail=thumbnail,
                             plot=plot,
                             contentTitle=contentTitle,
                             contentSerieName=contentSerieName,
                             quality=quality,
                             infoLabels={'year': year}
                             ))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # Paginacion

    if itemlist != []:
        actual_page_url = item.url
        next_page = scrapertools.find_single_match(data,
                                                   'alignleft><a href=(.*?) ><\/a><\/div><div class=nav-next alignright>')
        if next_page != '':
            itemlist.append(Item(channel=item.channel,
                                 action="lista",
                                 title='Siguiente >>>',
                                 url=next_page,
                                 thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'
                                 ))
    return itemlist


def seccion(item):
    logger.info()
    itemlist = []
    data = get_source(item.url)
    if item.seccion == 'generos-pelicula':
        patron = '<li class=cat-item cat-item-.*?><a href=(.*?) >(.*?<\/a> <span>.*?)<\/span><\/li>'
    elif item.seccion == 'generos-serie':
        patron = '<li class=cat-item cat-item-.*?><a href=(.*?\/series-genero\/.*?) >(.*?<\/a> <span>.*?)<\/span><\/li>'
    elif item.seccion in ['fecha-estreno', 'series-lanzamiento']:
        patron = '<li><a href=http:\/\/miradetodo\.io\/fecha-estreno(.*?)>(.*?)<\/a>'
    elif item.seccion == 'calidad':
        patron = '<li><a href=http:\/\/miradetodo\.io\/calidad(.*?)>(.*?)<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        thumbnail = ''
        if 'generos' in item.seccion:
            cantidad = re.sub(r'.*?<\/a> <span>', '', scrapedtitle)
            title = re.sub(r'<\/a> <span>|\d|\.', '', scrapedtitle)
            url = scrapedurl
            title = scrapertools.decodeHtmlentities(title)
            if title in tgenero:
                thumbnail = tgenero[title]
            title = title + ' (%s)' % cantidad
        elif item.seccion in ['series-lanzamiento', 'fecha-estreno', 'calidad']:
            title = scrapedtitle
            url = 'http://miradetodo.io/%s%s' % (item.seccion, scrapedurl)
            if item.seccion == 'calidad' and title in tcalidad:
                thumbnail = tcalidad[title]

        itemlist.append(item.clone(action='lista',
                                   title=title,
                                   url=url,
                                   thumbnail=thumbnail
                                   ))
    return itemlist


def temporadas(item):
    logger.info()

    itemlist = []

    data = get_source(item.url)
    patron = '<span class=title>.*?- Temporada (.*?)<\/span>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for temporada in matches:
        title = 'Temporada %s' % temporada
        contentSeasonNumber = temporada
        item.infoLabels['season'] = contentSeasonNumber
        itemlist.append(item.clone(action='episodiosxtemp',
                                   title=title,
                                   contentSeasonNumber=contentSeasonNumber
                                   ))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_serie_to_library",
                             extra="episodios",
                             contentSerieName=item.contentSerieName,
                             contentSeasonNumber=contentSeasonNumber
                             ))

    return itemlist


def episodios(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)

    patron = '<li><div class=numerando>(\d+).*?x.*?(\d+)<\/div>.*?<a href=(.*?)> (.*?)<\/a>.*?<\/i>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtemp, scrapedep, scrapedurl, scrapedtitle in matches:
        temporada = scrapedtemp
        title = temporada + 'x%s %s' % (scrapedep, scrapedtitle)
        url = scrapedurl
        contentEpisodeNumber = scrapedep
        item.infoLabels['episode'] = contentEpisodeNumber
        itemlist.append(item.clone(action='findvideos',
                                   title=title,
                                   url=url,
                                   contentEpisodeNumber=contentEpisodeNumber,
                                   ))
    return itemlist


def episodiosxtemp(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)
    temporada = item.contentSeasonNumber
    patron = '<li><div class=numerando>%s.*?x.*?(\d+)<\/div>.*?<a href=(.*?)> (.*?)<\/a>.*?<\/i>' % temporada
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedep, scrapedurl, scrapedtitle in matches:
        title = temporada + 'x%s %s' % (scrapedep, scrapedtitle)
        url = scrapedurl
        contentEpisodeNumber = scrapedep
        item.infoLabels['episode'] = contentEpisodeNumber
        itemlist.append(item.clone(action='findvideos',
                                   title=title,
                                   url=url,
                                   contentEpisodeNumber=contentEpisodeNumber,
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    return itemlist


def findvideos(item):
    logger.info()
    url_list = []
    itemlist = []
    duplicados = []
    data = get_source(item.url)
    src = data
    patron = 'id=(?:div|player)(\d+)>.*?<iframe src=.*? data-lazy-src=(.*?) marginheight'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for option, videoitem in matches:
        lang = scrapertools.find_single_match(src,
                                              '<a href=#(?:div|player)%s.*?>.*?(Doblado|Subtitulado)<\/a>' % option)
        data = get_source(videoitem)
        if 'play' in videoitem:
            url = scrapertools.find_single_match(data, '<span>Ver Online<.*?<li><a href=(.*?)><span class=icon>')
        else:
            url = scrapertools.find_single_match(data, '<iframe src=(.*?) scrolling=')

        url_list.append([url, lang])

    for video_url in url_list:
        language = video_url[1]
        if 'jw.miradetodo' in video_url[0]:
            data = get_source('http:' + video_url[0])
            patron = 'label:.*?(.*?),.*?file:.*?(.*?)&app.*?\}'
            matches = re.compile(patron, re.DOTALL).findall(data)

            for quality, scrapedurl in matches:
                quality = quality
                title = item.contentTitle + ' (%s) %s' % (quality, language)
                server = 'directo'
                url = scrapedurl
                url = url.replace('\/', '/')
                subtitle = scrapertools.find_single_match(data, "tracks: \[\{file: '.*?linksub=(.*?)',label")
                if url not in duplicados:
                    itemlist.append(item.clone(title=title,
                                               action='play',
                                               url=url,
                                               quality=quality,
                                               server=server,
                                               subtitle=subtitle,
                                               language=language
                                               ))
                    duplicados.append(url)
        elif video_url != '':
            itemlist.extend(servertools.find_video_items(data=video_url[0]))

        for videoitem in itemlist:
            if videoitem.server != 'directo':

                quality = item.quality
                title = item.contentTitle + ' (%s) %s' % (videoitem.server, language)
                if item.quality != '':
                    title = item.contentTitle + ' (%s) %s' % (quality, language)
                videoitem.title = title
                videoitem.channel = item.channel
                videoitem.thumbnail = config.get_thumb("server_%s.png" % videoitem.server)
                videoitem.quality = item.quality

    if item.infoLabels['mediatype'] == 'movie':
        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
            itemlist.append(Item(channel=item.channel,
                                 title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                                 url=item.url,
                                 action="add_pelicula_to_library",
                                 extra="findvideos",
                                 contentTitle=item.contentTitle
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


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host + 'page/1/?s'

        elif categoria == 'infantiles':
            item.url = host + 'category/animacion/'

        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def get_source(url):
    logger.info()
    data = httptools.downloadpage(url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    return data
