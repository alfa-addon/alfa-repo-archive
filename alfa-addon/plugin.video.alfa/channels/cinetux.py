# -*- coding: utf-8 -*-

import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

CHANNEL_HOST = "http://www.cinetux.net/"

# Configuracion del canal
__modo_grafico__ = config.get_setting('modo_grafico', 'cinetux')
__perfil__ = config.get_setting('perfil', 'cinetux')

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]
color1, color2, color3 = perfil[__perfil__]

viewmode_options = {0: 'movie_with_plot', 1: 'movie', 2: 'list'}
viewmode = viewmode_options[config.get_setting('viewmode', 'cinetux')]


def mainlist(item):
    logger.info()
    itemlist = []
    item.viewmode = viewmode

    itemlist.append(item.clone(title="Películas", text_color=color2, action="", text_bold=True))
    itemlist.append(item.clone(action="peliculas", title="      Novedades", url=CHANNEL_HOST,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres"
                                         "/0/Directors%20Chair.png",
                               text_color=color1))
    itemlist.append(item.clone(action="vistas", title="      Más vistas", url="http://www.cinetux.net/mas-vistos/",
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres"
                                         "/0/Favorites.png",
                               text_color=color1))
    itemlist.append(item.clone(action="idioma", title="      Por idioma", text_color=color1))
    itemlist.append(item.clone(action="generos", title="      Por géneros", url=CHANNEL_HOST,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres"
                                         "/0/Genre.png",
                               text_color=color1))

    url = urlparse.urljoin(CHANNEL_HOST, "genero/documental/")
    itemlist.append(item.clone(title="Documentales", text_bold=True, text_color=color2, action=""))
    itemlist.append(item.clone(action="peliculas", title="      Novedades", url=url, text_color=color1,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres"
                                         "/0/Documentaries.png"))
    url = urlparse.urljoin(CHANNEL_HOST, "genero/documental/?orderby=title&order=asc&gdsr_order=asc")
    itemlist.append(item.clone(action="peliculas", title="      Por orden alfabético", text_color=color1, url=url,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres"
                                         "/0/A-Z.png"))
    itemlist.append(item.clone(title="", action=""))
    itemlist.append(item.clone(action="search", title="Buscar...", text_color=color3))
    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", text_color="gold", folder=False))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    item.url = "http://www.cinetux.net/?s="
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
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
            item.url = CHANNEL_HOST
            item.action = "peliculas"
            itemlist = peliculas(item)

            if itemlist[-1].action == "peliculas":
                itemlist.pop()

        elif categoria == 'documentales':
            item.url = urlparse.urljoin(CHANNEL_HOST, "genero/documental/")
            item.action = "peliculas"
            itemlist = peliculas(item)

            if itemlist[-1].action == "peliculas":
                itemlist.pop()

        elif categoria == 'infantiles':
            item.url = urlparse.urljoin(CHANNEL_HOST, "genero/infantil/")
            item.action = "peliculas"
            itemlist = peliculas(item)

            if itemlist[-1].action == "peliculas":
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
    item.text_color = color2

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<div class="item">.*?<div class="audio">\s*([^<]*)<.*?href="([^"]+)".*?src="([^"]+)"' \
             '.*?<h3 class="name"><a.*?>([^<]+)</a>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for calidad, scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        try:
            fulltitle, year = scrapedtitle.rsplit("(", 1)
            year = scrapertools.get_match(year, '(\d{4})')
            if "/" in fulltitle:
                fulltitle = fulltitle.split(" /", 1)[0]
                scrapedtitle = "%s (%s)" % (fulltitle, year)
        except:
            fulltitle = scrapedtitle
            year = ""

        if calidad:
            scrapedtitle += "  [%s]" % calidad
        new_item = item.clone(action="findvideos", title=scrapedtitle, fulltitle=fulltitle,
                              url=scrapedurl, thumbnail=scrapedthumbnail,
                              contentTitle=fulltitle, contentType="movie")
        if year:
            new_item.infoLabels['year'] = int(year)
        itemlist.append(new_item)
    try:
        tmdb.set_infoLabels(itemlist, __modo_grafico__)
    except:
        pass

    # Extrae el paginador
    next_page_link = scrapertools.find_single_match(data, '<a href="([^"]+)"\s*><span [^>]+>&raquo;</span>')
    if next_page_link:
        itemlist.append(item.clone(action="peliculas", title=">> Página siguiente", url=next_page_link,
                                   text_color=color3))

    return itemlist


def vistas(item):
    logger.info()
    itemlist = []
    item.text_color = color2

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<li class="item">.*?href="([^"]+)".*?src="([^"]+)"' \
             '.*?<h3 class="name"><a.*?>([^<]+)</a>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        new_item = item.clone(action="findvideos", title=scrapedtitle, fulltitle=scrapedtitle,
                              url=scrapedurl, thumbnail=scrapedthumbnail,
                              contentTitle=scrapedtitle, contentType="movie")
        itemlist.append(new_item)

    # Extrae el paginador
    next_page_link = scrapertools.find_single_match(data, '<a href="([^"]+)"\s+><span [^>]+>&raquo;</span>')
    if next_page_link:
        itemlist.append(item.clone(action="vistas", title=">> Página siguiente", url=next_page_link, text_color=color3))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_single_match(data, '<div class="sub_title">Géneros</div>(.*?)</ul>')

    # Extrae las entradas
    patron = '<li><a href="([^"]+)">(.*?)</li>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.htmlclean(scrapedtitle).strip()
        scrapedtitle = unicode(scrapedtitle, "utf8").capitalize().encode("utf8")
        if scrapedtitle == "Erotico" and config.get_setting("adult_mode") == '0':
            continue

        itemlist.append(item.clone(action="peliculas", title=scrapedtitle, url=scrapedurl))

    return itemlist


def idioma(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(action="peliculas", title="Español", url="http://www.cinetux.net/idioma/espanol/"))
    itemlist.append(item.clone(action="peliculas", title="Latino", url="http://www.cinetux.net/idioma/latino/"))
    itemlist.append(item.clone(action="peliculas", title="VOSE", url="http://www.cinetux.net/idioma/subtitulado/"))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    try:
        filtro_idioma = config.get_setting("filterlanguages", item.channel)
        filtro_enlaces = config.get_setting("filterlinks", item.channel)
    except:
        filtro_idioma = 3
        filtro_enlaces = 2
    dict_idiomas = {'Español': 2, 'Latino': 1, 'Subtitulado': 0}

    # Busca el argumento
    data = httptools.downloadpage(item.url).data
    year = scrapertools.find_single_match(data, '<h1><span>.*?rel="tag">([^<]+)</a>')

    if year and item.extra != "library":
        item.infoLabels['year'] = int(year)
        # Ampliamos datos en tmdb
        if not item.infoLabels['plot']:
            try:
                tmdb.set_infoLabels(item, __modo_grafico__)
            except:
                pass

    if not item.infoLabels.get('plot'):
        plot = scrapertools.find_single_match(data, '<div class="sinopsis"><p>(.*?)</p>')
        item.infoLabels['plot'] = plot

    if filtro_enlaces != 0:
        list_enlaces = bloque_enlaces(data, filtro_idioma, dict_idiomas, "online", item)
        if list_enlaces:
            itemlist.append(item.clone(action="", title="Enlaces Online", text_color=color1,
                                       text_bold=True))
            itemlist.extend(list_enlaces)
    if filtro_enlaces != 1:
        list_enlaces = bloque_enlaces(data, filtro_idioma, dict_idiomas, "descarga", item)
        if list_enlaces:
            itemlist.append(item.clone(action="", title="Enlaces Descarga", text_color=color1,
                                       text_bold=True))
            itemlist.extend(list_enlaces)

    if itemlist:
        itemlist.append(item.clone(channel="trailertools", title="Buscar Tráiler", action="buscartrailer", context="",
                                   text_color="magenta"))
        # Opción "Añadir esta película a la videoteca de XBMC"
        if item.extra != "library":
            if config.get_videolibrary_support():
                itemlist.append(Item(channel=item.channel, title="Añadir a la videoteca", text_color="green",
                                     filtro=True, action="add_pelicula_to_library", url=item.url,
                                     infoLabels={'title': item.fulltitle}, fulltitle=item.fulltitle,
                                     extra="library"))

    else:
        itemlist.append(item.clone(title="No hay enlaces disponibles", action="", text_color=color3))

    return itemlist


def bloque_enlaces(data, filtro_idioma, dict_idiomas, type, item):
    logger.info()
    lista_enlaces = []

    matches = []
    if type == "online":
        patron = '<a href="#([^"]+)" data-toggle="tab">([^<]+)</a>'
        bloques = scrapertools.find_multiple_matches(data, patron)
        for id, language in bloques:
            patron = 'id="' + id + '">.*?<iframe src="([^"]+)"'
            url = scrapertools.find_single_match(data, patron)
            matches.append([url, "", language])

    bloque2 = scrapertools.find_single_match(data, '<div class="table-link" id="%s">(.*?)</table>' % type)
    patron = 'tr>[^<]+<td>.*?href="([^"]+)".*?src.*?title="([^"]+)"' \
             '.*?src.*?title="([^"]+)".*?src.*?title="(.*?)"'
    matches.extend(scrapertools.find_multiple_matches(bloque2, patron))
    filtrados = []
    for match in matches:
        scrapedurl = match[0]
        language = match[2].strip()
        title = "   Mirror en %s (" + language + ")"
        if len(match) == 4:
            title += " (Calidad " + match[3].strip() + ")"

        if filtro_idioma == 3 or item.filtro:
            lista_enlaces.append(item.clone(title=title, action="play", text_color=color2,
                                            url=scrapedurl, idioma=language, extra=item.url))
        else:
            idioma = dict_idiomas[language]
            if idioma == filtro_idioma:
                lista_enlaces.append(item.clone(title=title, text_color=color2, action="play", url=scrapedurl,
                                                extra=item.url))
            else:
                if language not in filtrados:
                    filtrados.append(language)

    lista_enlaces = servertools.get_servers_itemlist(lista_enlaces, lambda i: i.title % i.server)
    if filtro_idioma != 3:
        if len(filtrados) > 0:
            title = "Mostrar enlaces filtrados en %s" % ", ".join(filtrados)
            lista_enlaces.append(item.clone(title=title, action="findvideos", url=item.url, text_color=color3,
                                            filtro=True))

    return lista_enlaces


def play(item):
    logger.info()
    itemlist = []
    if "api.cinetux" in item.url:
        data = httptools.downloadpage(item.url, headers={'Referer': item.extra}).data.replace("\\", "")
        bloque = scrapertools.find_single_match(data, 'sources:\s*(\[.*?\])')
        if bloque:
            bloque = eval(bloque)
            video_urls = []
            for b in bloque:
                ext = b["type"].replace("video/", "")
                video_urls.append([".%s %sp [directo]" % (ext, b["label"]), b["file"], b["label"]])

            video_urls.sort(key=lambda vdu: vdu[2])
            for v in video_urls:
                itemlist.append([v[0], v[1]])
    else:
        return [item]
    return itemlist
