# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

# Configuracion del canal
__modo_grafico__ = config.get_setting('modo_grafico', "vixto")
__perfil__ = config.get_setting('perfil', "vixto")

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]
color1, color2, color3 = perfil[__perfil__]

host = "http://www.vixto.net/"


def mainlist(item):
    logger.info()
    itemlist = list()

    itemlist.append(item.clone(title="Películas", text_color=color2, action="",
                               text_bold=True))
    itemlist.append(item.clone(action="listado", title="      Estrenos", text_color=color1, url=host,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/"
                                         "0/Directors%20Chair.png"))
    itemlist.append(item.clone(action="listado", title="      Novedades", text_color=color1, url=host,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/"
                                         "0/Directors%20Chair.png"))
    itemlist.append(item.clone(action="listado", title="Series - Novedades", text_color=color2, url=host,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/"
                                         "0/TV%20Series.png", text_bold=True))

    itemlist.append(item.clone(action="search", title="Buscar...", text_color=color3,
                               url="http://www.vixto.net/buscar?q="))

    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", text_color="gold", folder=False))
    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    try:
        return busqueda(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%{0}".format(line))
        return []


def newest(categoria):
    logger.info()
    itemlist = list()
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host
            itemlist = listado(item)

            if itemlist[-1].action == "listado":
                itemlist.pop()
            item.title = "Estrenos"
            itemlist.extend(listado(item))

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def listado(item):
    logger.info()
    itemlist = list()

    item.infoLabels['mediatype'] = "movie"
    if "Estrenos" in item.title:
        bloque_head = "ESTRENOS CARTELERA"
    elif "Series" in item.title:
        bloque_head = "RECIENTE SERIES"
        item.infoLabels['mediatype'] = "tvshow"
    else:
        bloque_head = "RECIENTE PELICULAS"

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|\s{2}", "", data)

    # Extrae las entradas (carpetas)
    bloque = scrapertools.find_single_match(data, bloque_head + '\s*</h2>(.*?)</section>')
    patron = '<div class="".*?href="([^"]+)".*?src="([^"]+)".*?<div class="calZG">(.*?)</div>' \
             '(.*?)</div>.*?href.*?>(.*?)</a>'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    for scrapedurl, scrapedthumbnail, calidad, idiomas, scrapedtitle in matches:
        title = scrapedtitle
        langs = []
        if 'idio idi1' in idiomas:
            langs.append("VOS")
        if 'idio idi2' in idiomas:
            langs.append("LAT")
        if 'idio idi4' in idiomas:
            langs.append("ESP")
        if langs:
            title += "  [%s]" % "/".join(langs)
        if calidad:
            title += " %s" % calidad

        filtro_thumb = scrapedthumbnail.replace("http://image.tmdb.org/t/p/w342", "")
        filtro_list = {"poster_path": filtro_thumb}
        filtro_list = filtro_list.items()

        if item.contentType == "tvshow":
            new_item = item.clone(action="episodios", title=title, url=scrapedurl, thumbnail=scrapedthumbnail,
                                  fulltitle=scrapedtitle, infoLabels={'filtro': filtro_list},
                                  contentTitle=scrapedtitle, context="buscar_trailer", text_color=color1,
                                  show=scrapedtitle, text_bold=False)
        else:
            new_item = item.clone(action="findvideos", title=title, url=scrapedurl, thumbnail=scrapedthumbnail,
                                  fulltitle=scrapedtitle, infoLabels={'filtro': filtro_list}, text_bold=False,
                                  contentTitle=scrapedtitle, context="buscar_trailer", text_color=color1)

        itemlist.append(new_item)

    if item.action == "listado":
        try:
            tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
        except:
            pass

    return itemlist


def busqueda(item):
    logger.info()
    itemlist = list()

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|\s{2}", "", data)

    # Extrae las entradas (carpetas)
    bloque = scrapertools.find_single_match(data, '<h2>Peliculas</h2>(.*?)</div>')
    bloque += scrapertools.find_single_match(data, '<h2>Series</h2>(.*?)</div>')

    patron = '<figure class="col-lg-2.*?href="([^"]+)".*?src="([^"]+)".*?<figcaption title="([^"]+)"'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    peliculas = False
    series = False
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        new_item = Item(channel=item.channel, contentType="movie", url=scrapedurl, title="   " + scrapedtitle,
                        text_color=color1, context="buscar_trailer", fulltitle=scrapedtitle,
                        contentTitle=scrapedtitle, thumbnail=scrapedthumbnail, action="findvideos")

        if "/peliculas/" in scrapedurl and not peliculas:
            itemlist.append(Item(channel=item.channel, action="", title="Películas", text_color=color2))
            peliculas = True
        if "/series/" in scrapedurl and not series:
            itemlist.append(Item(channel=item.channel, action="", title="Series", text_color=color2))
            series = True

        if "/series/" in scrapedurl:
            new_item.contentType = "tvshow"
            new_item.show = scrapedtitle
            new_item.action = "episodios"

        filtro_thumb = scrapedthumbnail.replace("http://image.tmdb.org/t/p/w342", "")
        filtro_list = {"poster_path": filtro_thumb}
        new_item.infoLabels["filtro"] = filtro_list.items()
        itemlist.append(new_item)

    try:
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass

    return itemlist


def episodios(item):
    logger.info()
    itemlist = list()

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|\s{2}", "", data)

    # Extrae las entradas (carpetas)
    bloque = scrapertools.find_single_match(data, '<strong>Temporada:(.*?)</div>')
    matches = scrapertools.find_multiple_matches(bloque, 'href="([^"]+)">(.*?)</a>')

    for scrapedurl, scrapedtitle in matches:
        title = "Temporada %s" % scrapedtitle

        new_item = item.clone(action="", title=title, text_color=color2)
        new_item.infoLabels["season"] = scrapedtitle
        new_item.infoLabels["mediatype"] = "season"
        data_season = httptools.downloadpage(scrapedurl).data
        data_season = re.sub(r"\n|\r|\t|&nbsp;|\s{2}", "", data_season)
        patron = '<li class="media">.*?href="([^"]+)"(.*?)<div class="media-body">.*?href.*?>' \
                 '(.*?)</a>'
        matches = scrapertools.find_multiple_matches(data_season, patron)

        elementos = []
        for url, status, title in matches:
            if not "Enlaces Disponibles" in status:
                continue
            elementos.append(title)
            item_epi = item.clone(action="findvideos", url=url, text_color=color1)
            item_epi.infoLabels["season"] = scrapedtitle
            episode = scrapertools.find_single_match(title, 'Capitulo (\d+)')
            titulo = scrapertools.find_single_match(title, 'Capitulo \d+\s*-\s*(.*?)$')
            item_epi.infoLabels["episode"] = episode
            item_epi.infoLabels["mediatype"] = "episode"
            item_epi.title = "%sx%s  %s" % (scrapedtitle, episode.zfill(2), titulo)

            itemlist.insert(0, item_epi)
        if elementos:
            itemlist.insert(0, new_item)

    if item.infoLabels["tmdb_id"] and itemlist:
        try:
            tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
        except:
            pass

    if itemlist:
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir serie a la videoteca", text_color="green",
                                 filtro=True, action="add_serie_to_library", fulltitle=item.fulltitle,
                                 extra="episodios", url=item.url, infoLabels=item.infoLabels, show=item.show))
    else:
        itemlist.append(item.clone(title="Serie sin episodios disponibles", action="", text_color=color3))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = list()

    try:
        filtro_idioma = config.get_setting("filterlanguages", item.channel)
        filtro_enlaces = config.get_setting("filterlinks", item.channel)
    except:
        filtro_idioma = 3
        filtro_enlaces = 2

    dict_idiomas = {'Castellano': 2, 'Latino': 1, 'Subtitulada': 0}

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|\s{2}", "", data)

    if not item.infoLabels["tmdb_id"]:
        year = scrapertools.find_single_match(data, 'Lanzamiento.*?(\d{4})')

        if year != "":
            item.infoLabels['filtro'] = ""
            item.infoLabels['year'] = int(year)

            # Ampliamos datos en tmdb
            try:
                tmdb.set_infoLabels_item(item, __modo_grafico__)
            except:
                pass

    if not item.infoLabels['plot']:
        plot = scrapertools.find_single_match(data, '<p class="plot">(.*?)</p>')
        item.infoLabels['plot'] = plot

    if filtro_enlaces != 0:
        list_enlaces = bloque_enlaces(data, filtro_idioma, dict_idiomas, "Ver Online", item)
        if list_enlaces:
            itemlist.append(item.clone(action="", title="Enlaces Online", text_color=color1,
                                       text_bold=True))
            itemlist.extend(list_enlaces)
    if filtro_enlaces != 1:
        list_enlaces = bloque_enlaces(data, filtro_idioma, dict_idiomas, "Descarga Directa", item)
        if list_enlaces:
            itemlist.append(item.clone(action="", title="Enlaces Descarga", text_color=color1,
                                       text_bold=True))
            itemlist.extend(list_enlaces)

    # Opción "Añadir esta película a la videoteca de XBMC"
    if itemlist and item.contentType == "movie":
        contextual = config.is_xbmc()
        itemlist.append(item.clone(channel="trailertools", title="Buscar Tráiler", action="buscartrailer", context="",
                                   text_color="magenta", contextual=contextual))
        if item.extra != "findvideos":
            if config.get_videolibrary_support():
                itemlist.append(Item(channel=item.channel, title="Añadir enlaces a la videoteca", text_color="green",
                                     filtro=True, action="add_pelicula_to_library", fulltitle=item.fulltitle,
                                     extra="findvideos", url=item.url, infoLabels=item.infoLabels,
                                     contentType=item.contentType, contentTitle=item.contentTitle, show=item.show))
    elif not itemlist and item.contentType == "movie":
        itemlist.append(item.clone(title="Película sin enlaces disponibles", action="", text_color=color3))

    return itemlist


def bloque_enlaces(data, filtro_idioma, dict_idiomas, tipo, item):
    logger.info()

    lista_enlaces = list()
    bloque = scrapertools.find_single_match(data, tipo + '(.*?)</table>')
    patron = '<td class="sape">\s*<i class="idioma-([^"]+)".*?href="([^"]+)".*?</p>.*?<td>([^<]+)</td>' \
             '.*?<td class="desaparecer">(.*?)</td>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    filtrados = []
    for language, scrapedurl, calidad, orden in matches:
        language = language.strip()
        server = scrapertools.find_single_match(scrapedurl, 'http(?:s|)://(?:www.|)(\w+).')
        if server == "ul":
            server = "uploadedto"
        if server == "streamin":
            server = "streaminto"
        if server == "waaw":
            server = "netutv"

        if servertools.is_server_enabled(server):
            try:
                servers_module = __import__("servers." + server)
                title = "   Mirror en " + server + " (" + language + ") (Calidad " + calidad.strip() + ")"
                if filtro_idioma == 3 or item.filtro:
                    lista_enlaces.append(item.clone(title=title, action="play", server=server, text_color=color2,
                                                    url=scrapedurl, idioma=language, orden=orden))
                else:
                    idioma = dict_idiomas[language]
                    if idioma == filtro_idioma:
                        lista_enlaces.append(item.clone(title=title, text_color=color2, action="play",
                                                        url=scrapedurl, server=server, idioma=language, orden=orden))
                    else:
                        if language not in filtrados:
                            filtrados.append(language)
            except:
                pass

    order = config.get_setting("orderlinks", item.channel)
    if order == 0:
        lista_enlaces.sort(key=lambda item: item.server)
    elif order == 1:
        lista_enlaces.sort(key=lambda item: item.idioma)
    else:
        lista_enlaces.sort(key=lambda item: item.orden, reverse=True)

    if filtro_idioma != 3:
        if len(filtrados) > 0:
            title = "Mostrar enlaces filtrados en %s" % ", ".join(filtrados)
            lista_enlaces.append(item.clone(title=title, action="findvideos", url=item.url, text_color=color3,
                                            filtro=True))

    return lista_enlaces


def play(item):
    logger.info()
    itemlist = list()
    enlace = servertools.findvideosbyserver(item.url, item.server)
    itemlist.append(item.clone(url=enlace[0][1]))

    return itemlist
