# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import jsontools
from core import logger
from core import scrapertools
from core import tmdb
from core.item import Item

tgenero = {"Drama": "https://s16.postimg.org/94sia332d/drama.png",
           u"Accción": "https://s3.postimg.org/y6o9puflv/accion.png",
           u"Animación": "https://s13.postimg.org/5on877l87/animacion.png",
           u"Ciencia Ficción": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png",
           "Terror": "https://s7.postimg.org/yi0gij3gb/terror.png",
           }

audio = {'LAT': '[COLOR limegreen]LATINO[/COLOR]', 'SUB': '[COLOR red]Subtitulado[/COLOR]'}

host = 'http://pelisfox.tv'


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Ultimas",
                               action="lista",
                               thumbnail='https://s22.postimg.org/cb7nmhwv5/ultimas.png',
                               fanart='https://s22.postimg.org/cb7nmhwv5/ultimas.png',
                               url=host + '/estrenos/'
                               ))

    itemlist.append(item.clone(title="Generos",
                               action="seccion",
                               url=host,
                               thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                               fanart='https://s3.postimg.org/5s9jg2wtf/generos.png',
                               seccion='generos'
                               ))

    itemlist.append(item.clone(title="Por Año",
                               action="seccion",
                               url=host + '/peliculas/2017/',
                               thumbnail='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                               fanart='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                               seccion='anios'
                               ))

    itemlist.append(item.clone(title="Por Actor",
                               action="seccion",
                               url=host + '/actores/',
                               thumbnail='https://s17.postimg.org/w25je5zun/poractor.png',
                               fanart='https://s17.postimg.org/w25je5zun/poractor.png',
                               seccion='actor'
                               ))

    itemlist.append(item.clone(title="Buscar",
                               action="search",
                               url=host + '/api/elastic/suggest?query=',
                               thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                               fanart='https://s30.postimg.org/pei7txpa9/buscar.png'
                               ))

    return itemlist


def lista(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    if item.seccion != 'actor':
        patron = '<li class=item-serie.*?><a href=(.*?) title=(.*?)><img src=(.*?) alt=><span '
        patron += 'class=s-title><strong>.*?<\/strong><p>(.*?)<\/p><\/span><\/a><\/li>'
    else:
        patron = '<li><a href=(\/pelicula\/.*?)><figure><img src=(.*?) alt=><\/figure><p class=title>(.*?)<\/p><p '
        patron += 'class=year>(.*?)<\/p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedyear in matches:
        url = host + scrapedurl
        if item.seccion != 'actor':
            thumbnail = scrapedthumbnail
            contentTitle = scrapedtitle
        else:
            thumbnail = scrapedtitle
            contentTitle = scrapedthumbnail
        plot = ''
        year = scrapedyear
        title = contentTitle + ' (' + year + ')'
        itemlist.append(
            Item(channel=item.channel,
                 action='findvideos',
                 title=title,
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 contentTitle=contentTitle,
                 infoLabels={'year': year}
                 ))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # Paginacion

    if itemlist != []:
        actual_page = scrapertools.find_single_match(data, '<a class=active item href=.*?>(.*?)<\/a>')
        if actual_page:
            next_page_num = int(actual_page) + 1
            next_page = scrapertools.find_single_match(data,
                                                       '<li><a class= item href=(.*?)\?page=.*?&limit=.*?>Siguiente')
            next_page_url = host + next_page + '?page=%s' % next_page_num
            if next_page != '':
                itemlist.append(Item(channel=item.channel,
                                     action="lista",
                                     title='Siguiente >>>',
                                     url=next_page_url,
                                     thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'
                                     ))
    return itemlist


def seccion(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    if item.seccion == 'generos':
        patron = '<a href=(\/peliculas\/[\D].*?\/) title=Películas de .*?>(.*?)<\/a>'
    elif item.seccion == 'anios':
        patron = '<li class=.*?><a href=(.*?)>(\d{4})<\/a> <\/li>'
    elif item.seccion == 'actor':
        patron = '<li><a href=(.*?)><div.*?<div class=photopurple title=(.*?)><\/div><img src=(.*?)><\/figure>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.seccion != 'actor':
        for scrapedurl, scrapedtitle in matches:
            title = scrapedtitle.decode('utf-8')
            thumbnail = ''
            if item.seccion == 'generos':
                thumbnail = tgenero[title]
            fanart = ''
            url = host + scrapedurl

            itemlist.append(
                Item(channel=item.channel,
                     action="lista",
                     title=title,
                     fulltitle=item.title,
                     url=url,
                     thumbnail=thumbnail,
                     fanart=fanart
                     ))
    else:
        for scrapedurl, scrapedname, scrapedthumbnail in matches:
            thumbnail = scrapedthumbnail
            fanart = ''
            title = scrapedname
            url = host + scrapedurl

            itemlist.append(Item(channel=item.channel,
                                 action="lista",
                                 title=title,
                                 fulltitle=item.title,
                                 url=url,
                                 thumbnail=thumbnail,
                                 fanart=fanart,
                                 seccion=item.seccion
                                 ))
        # Paginacion

        if itemlist != []:
            next_page = scrapertools.find_single_match(data, '<li><a class= item href=(.*?)&limit=.*?>Siguiente <')
            next_page_url = host + next_page
            if next_page != '':
                itemlist.append(item.clone(action="seccion",
                                           title='Siguiente >>>',
                                           url=next_page_url,
                                           thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'
                                           ))

    return itemlist


def busqueda(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    dict_data = jsontools.load(data)
    resultados = dict_data['result'][0]['options']

    for resultado in resultados:
        if 'title' in resultado['_source']:
            title = resultado['_source']['title']
            thumbnail = 'http://s3.amazonaws.com/pelisfox' + '/' + resultado['_source']['cover']
            plot = resultado['_source']['sinopsis']
            url = host + resultado['_source']['url'] + '/'

            itemlist.append(item.clone(title=title,
                                       thumbnail=thumbnail,
                                       plot=plot,
                                       url=url,
                                       action='findvideos',
                                       contentTitle=title
                                       ))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    if texto != '':
        return busqueda(item)
    else:
        return []


def findvideos(item):
    logger.info()
    itemlist = []
    templist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    patron = '<li data-quality=(.*?) data-lang=(.*?)><a href=(.*?) title=.*?'
    matches = matches = re.compile(patron, re.DOTALL).findall(data)
    for quality, lang, scrapedurl in matches:
        url = host + scrapedurl
        title = item.title + ' (' + lang + ') (' + quality + ')'
        templist.append(item.clone(title=title,
                                   language=lang,
                                   url=url
                                   ))

    for videoitem in templist:

        data = httptools.downloadpage(videoitem.url).data
        data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
        id = scrapertools.find_single_match(data, 'var _SOURCE =.*?source:(.*?),')
        if videoitem.language == 'SUB':
            sub = scrapertools.find_single_match(data, 'var _SOURCE =.*?srt:(.*?),')
            sub = sub.replace('\\', '')
        else:
            sub = ''
        new_url = 'http://iplay.one/api/embed?id=%s&token=8908d9f846&%s' % (id, sub)

        data = httptools.downloadpage(new_url).data

        patron = 'file":"(.*?)","label":"(.*?)","type":".*?"}'
        matches = matches = re.compile(patron, re.DOTALL).findall(data)

        for scrapedurl, quality in matches:
            title = videoitem.contentTitle + ' (' + quality + ') (' + audio[videoitem.language] + ')'
            url = scrapedurl.replace('\\', '')
            itemlist.append(item.clone(title=title,
                                       action='play',
                                       url=url,
                                       subtitle=sub,
                                       server='directo',
                                       quality=quality,
                                       language='lang'
                                       ))

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
            item.url = host + '/estrenos/'
            item.extra = 'peliculas'
        elif categoria == 'infantiles':
            item.url = host + 'http://pelisfox.tv/peliculas/animacion/'
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
