# -*- coding: utf-8 -*-

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


host = "http://allcalidad.com/"

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel, title = "Novedades", action = "peliculas", url = host))
    itemlist.append(Item(channel = item.channel, title = "Por género", action = "generos_years", url = host, extra = "Genero" ))
    itemlist.append(Item(channel = item.channel, title = "Por año", action = "generos_years", url = host, extra = ">Año<"))
    itemlist.append(Item(channel = item.channel, title = "Favoritas", action = "peliculas", url = host + "/favorites" ))
    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel = item.channel, title = "Buscar", action = "search", url = host + "?s="))
    return itemlist

def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host
        elif categoria == 'infantiles':
            item.url = host + 'category/animacion/'
        itemlist = peliculas(item)
        if "Pagina" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ","+")
    item.url = item.url + texto
    item.extra = "busca"
    if texto!='':
        return peliculas(item)
    else:
        return []


def generos_years(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '(?s)%s(.*?)</ul></div>' %item.extra
    bloque = scrapertools.find_single_match(data, patron)
    patron  = 'href="([^"]+)'
    patron += '">([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for url, titulo in matches:
        itemlist.append(Item(channel = item.channel,
                            action = "peliculas",
                            title = titulo,
                            url = url
                            ))
    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '(?s)short_overlay.*?<a href="([^"]+)'
    patron += '.*?img.*?src="([^"]+)'
    patron += '.*?title="([^"]+)'
    patron += '.*?kinopoisk">([^<]+)'
    patron += '</span(.*?)small_rating'

    patron  = '(?s)short_overlay.*?<a href="([^"]+)'
    patron += '.*?img.*?src="([^"]+)'
    patron += '.*?title="(.*?)"'
    patron += '.*?(Idioma.*?)post-ratings'

    matches = scrapertools.find_multiple_matches(data, patron)
    for url, thumbnail, titulo, varios in matches:
        idioma = scrapertools.find_single_match(varios, '(?s)Idioma.*?kinopoisk">([^<]+)')
        year = scrapertools.find_single_match(varios, 'Año.*?kinopoisk">([^<]+)')
        year = scrapertools.find_single_match(year, '[0-9]{4}')
        mtitulo = titulo + " (" + idioma + ") (" + year + ")"
        new_item = Item(channel = item.channel,
                            action = "findvideos",
                            title = mtitulo,
                            fulltitle = titulo,
                            thumbnail = thumbnail,
                            url = url,
                            contentTitle = titulo,
                            contentType="movie"
							)
        if year:
            new_item.infoLabels['year'] = int(year)
        itemlist.append(new_item)
    url_pagina = scrapertools.find_single_match(data, 'next" href="([^"]+)')
    if url_pagina != "":
        pagina = "Pagina: " + scrapertools.find_single_match(url_pagina, "page/([0-9]+)")
        itemlist.append(Item(channel = item.channel, action = "peliculas", title = pagina, url = url_pagina))
    return itemlist


def findvideos(item):
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '(?s)fmi(.*?)thead'
    bloque = scrapertools.find_single_match(data, patron)
    match = scrapertools.find_multiple_matches(bloque, '(?is)iframe .*?src="([^"]+)')
    for url in match:
        server = servertools.get_server_from_url(url)
        titulo = "Ver en: " + server
        if "youtube" in server:
            if "embed" in url:
                url = "http://www.youtube.com/watch?v=" + scrapertools.find_single_match(url, 'embed/(.*)')
                titulo = "[COLOR = yellow]Ver trailer: " + server + "[/COLOR]"
        elif "directo" in server:
            continue
        itemlist.append(
                 Item(channel = item.channel,
                 action = "play",
                 title = titulo,
                 fulltitle = item.fulltitle,
                 thumbnail = item.thumbnail,
				 server = server,
                 url = url
                 ))
    if itemlist:
        itemlist.append(Item(channel = item.channel))
        itemlist.append(item.clone(channel="trailertools", title="Buscar Tráiler", action="buscartrailer", context="",
                                   text_color="magenta"))
        # Opción "Añadir esta película a la biblioteca de XBMC"
        if item.extra != "library":
            if config.get_library_support():
                itemlist.append(Item(channel=item.channel, title="Añadir a la biblioteca", text_color="green",
                                     filtro=True, action="add_pelicula_to_library", url=item.url, thumbnail = item.thumbnail,
                                     infoLabels={'title': item.fulltitle}, fulltitle=item.fulltitle,
                                     extra="library"))
    return itemlist