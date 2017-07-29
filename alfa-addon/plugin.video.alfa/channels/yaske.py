# -*- coding: utf-8 -*-

import re

from core import channeltools
from core import config
from core import httptools
from core import logger
from core import scrapertoolsV2
from core import servertools
from core import tmdb
from core.item import Item

HOST = 'http://www.yaske.ro'
parameters = channeltools.get_channel_parameters('yaske')
fanart_host = parameters['fanart']
thumbnail_host = parameters['thumbnail']
color1, color2, color3 = ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E']


def mainlist(item):
    logger.info()
    itemlist = []
    item.url = HOST
    item.text_color = color2
    item.fanart = fanart_host
    thumbnail = "https://raw.githubusercontent.com/master-1970/resources/master/images/genres/4/verdes/%s.png"

    itemlist.append(item.clone(title="Novedades", action="peliculas", text_bold=True, viewcontent='movies',
                               url=HOST + "/ultimas-y-actualizadas",
                               thumbnail=thumbnail % 'novedades', viewmode="movie_with_plot"))
    itemlist.append(item.clone(title="Estrenos", action="peliculas", text_bold=True,
                               url=HOST + "/genre/premieres", thumbnail=thumbnail % 'estrenos'))
    itemlist.append(item.clone(title="", folder=False))

    itemlist.append(Item(channel=item.channel, title="Filtrar por:", fanart=fanart_host, folder=False,
                         text_color=color3, text_bold=True, thumbnail=thumbnail_host))
    itemlist.append(item.clone(title="    Género", action="menu_buscar_contenido", text_color=color1, text_italic=True,
                               extra="genre", thumbnail=thumbnail % 'generos', viewmode="thumbnails"))
    itemlist.append(item.clone(title="    Idioma", action="menu_buscar_contenido", text_color=color1, text_italic=True,
                               extra="audio", thumbnail=thumbnail % 'idiomas'))
    itemlist.append(item.clone(title="    Calidad", action="menu_buscar_contenido", text_color=color1, text_italic=True,
                               extra="quality", thumbnail=thumbnail % 'calidad'))
    itemlist.append(item.clone(title="    Año", action="menu_buscar_contenido", text_color=color1, text_italic=True,
                               extra="year", thumbnail=thumbnail % 'year'))

    itemlist.append(item.clone(title="", folder=False))
    itemlist.append(item.clone(title="Buscar por título", action="search", thumbnail=thumbnail % 'buscar'))

    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []

    try:
        # http://www.yaske.ro/search/?q=los+pitufos
        item.url = HOST + "/search/?q=" + texto.replace(' ', '+')
        item.extra = ""
        itemlist.extend(peliculas(item))
        if itemlist[-1].title == ">> Página siguiente":
            item_pag = itemlist[-1]
            itemlist = sorted(itemlist[:-1], key=lambda Item: Item.contentTitle)
            itemlist.append(item_pag)
        else:
            itemlist = sorted(itemlist, key=lambda Item: Item.contentTitle)

        return itemlist

    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = HOST + "/ultimas-y-actualizadas"
        elif categoria == 'infantiles':
            item.url = HOST + "/search/?q=&genre%5B%5D=animation"
        else:
            return []

        itemlist = peliculas(item)
        if itemlist[-1].title == ">> Página siguiente":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    url_next_page = ""

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<article class.*?'
    patron += '<a href="([^"]+)">.*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<aside class="item-control down">(.*?)</aside>.*?'
    patron += '<small class="pull-right text-muted">([^<]+)</small>.*?'
    patron += '<h2 class.*?>([^<]+)</h2>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    # Paginacion
    if item.next_page != 'b':
        if len(matches) > 30:
            url_next_page = item.url
        matches = matches[:30]
        next_page = 'b'
    else:
        matches = matches[30:]
        next_page = 'a'
        patron_next_page = 'Anteriores</a> <a href="([^"]+)" class="btn btn-default ".*?Siguiente'
        matches_next_page = re.compile(patron_next_page, re.DOTALL).findall(data)
        if len(matches_next_page) > 0:
            url_next_page = matches_next_page[0]

    for scrapedurl, scrapedthumbnail, idiomas, year, scrapedtitle in matches:
        patronidiomas = "<img src='([^']+)'"
        matchesidiomas = re.compile(patronidiomas, re.DOTALL).findall(idiomas)

        idiomas_disponibles = []
        for idioma in matchesidiomas:
            if idioma.endswith("la_la.png"):
                idiomas_disponibles.append("LAT")
            elif idioma.endswith("en_en.png"):
                idiomas_disponibles.append("VO")
            elif idioma.endswith("en_es.png"):
                idiomas_disponibles.append("VOSE")
            elif idioma.endswith("es_es.png"):
                idiomas_disponibles.append("ESP")

        if idiomas_disponibles:
            idiomas_disponibles = "[" + "/".join(idiomas_disponibles) + "]"

        contentTitle = scrapertoolsV2.decodeHtmlentities(scrapedtitle.strip())
        title = "%s %s" % (contentTitle, idiomas_disponibles)

        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=scrapedurl,
                             thumbnail=scrapedthumbnail, contentTitle=contentTitle,
                             infoLabels={"year": year}, text_color=color1))

    # Obtenemos los datos basicos de todas las peliculas mediante multihilos
    tmdb.set_infoLabels(itemlist)

    # Si es necesario añadir paginacion
    if url_next_page:
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=">> Página siguiente", thumbnail=thumbnail_host,
                 url=url_next_page, next_page=next_page, folder=True, text_color=color3, text_bold=True))

    return itemlist


def menu_buscar_contenido(item):
    logger.info(item)

    data = httptools.downloadpage(item.url).data
    patron = '<select name="' + item.extra + '(.*?)</select>'
    data = scrapertoolsV2.get_match(data, patron)

    # Extrae las entradas
    patron = "<option value='([^']+)'>([^<]+)</option>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    itemlist = []
    for scrapedvalue, scrapedtitle in matches:
        thumbnail = ""

        if item.extra == 'genre':
            if scrapedtitle.strip() in ['Documental', 'Short', 'News']:
                continue

            url = HOST + "/search/?q=&genre%5B%5D=" + scrapedvalue
            filename = scrapedtitle.lower().replace(' ', '%20')
            if filename == "ciencia%20ficción":
                filename = "ciencia%20ficcion"
            thumbnail = "https://raw.githubusercontent.com/master-1970/resources/master/images/genres/4/verdes/%s.png" \
                        % filename

        elif item.extra == 'year':
            url = HOST + "/search/?q=&year=" + scrapedvalue
            thumbnail = item.thumbnail
        else:
            # http://www.yaske.ro/search/?q=&quality%5B%5D=c9
            # http://www.yaske.ro/search/?q=&audio%5B%5D=es
            url = HOST + "/search/?q=&" + item.extra + "%5B%5D=" + scrapedvalue
            thumbnail = item.thumbnail

        itemlist.append(Item(channel=item.channel, action="peliculas", title=scrapedtitle, url=url, text_color=color1,
                             thumbnail=thumbnail, contentType='movie', folder=True, viewmode="movie_with_plot"))

    if item.extra in ['genre', 'audio', 'year']:
        return sorted(itemlist, key=lambda i: i.title.lower(), reverse=item.extra == 'year')
    else:
        return itemlist


def findvideos(item):
    logger.info()
    itemlist = list()
    sublist = list()

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    if not item.plot:
        item.plot = scrapertoolsV2.find_single_match(data, '>Sinopsis</dt> <dd>([^<]+)</dd>')
        item.plot = scrapertoolsV2.decodeHtmlentities(item.plot)

    patron = '<option value="([^"]+)"[^>]+'
    patron += '>([^<]+).*?</i>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, idioma, calidad in matches:
        sublist.append(item.clone(action="play", url=url, folder=False, text_color=color1, quality=calidad.strip(),
                                  language=idioma.strip()))

    sublist = servertools.get_servers_itemlist(sublist, lambda i: "Ver en %s %s" % (i.server, i.quality), True)

    # Añadir servidores encontrados, agrupandolos por idioma
    for k in ["Español", "Latino", "Subtitulado", "Ingles"]:
        lista_idioma = filter(lambda i: i.language == k, sublist)
        if lista_idioma:
            itemlist.append(Item(channel=item.channel, title=k, fanart=item.fanart, folder=False,
                                 text_color=color2, text_bold=True, thumbnail=thumbnail_host))
            itemlist.extend(lista_idioma)

    # Insertar items "Buscar trailer" y "Añadir a la videoteca"
    if itemlist and item.extra != "library":
        title = "%s [Buscar trailer]" % (item.contentTitle)
        itemlist.insert(0, item.clone(channel="trailertools", action="buscartrailer",
                                      text_color=color3, title=title, viewmode="list"))

        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir película a la videoteca",
                                 action="add_pelicula_to_library", url=item.url, text_color="green",
                                 contentTitle=item.contentTitle, extra="library", thumbnail=thumbnail_host))

    return itemlist
