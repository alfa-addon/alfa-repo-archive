# -*- coding: utf-8 -*-

import re
import urlparse

from core import config
from core import httptools
from core import jsontools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

__modo_grafico__ = config.get_setting('modo_grafico', 'cinefox')
__perfil__ = int(config.get_setting('perfil', "cinefox"))
__menu_info__ = config.get_setting('menu_info', 'cinefox')

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00', '0xFFFE2E2E', '0xFF088A08'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E', '0xFFFE2E2E', '0xFF088A08'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE', '0xFFFE2E2E', '0xFF088A08']]
if __perfil__ < 3:
    color1, color2, color3, color4, color5 = perfil[__perfil__]
else:
    color1 = color2 = color3 = color4 = color5 = ""

host = "http://www.cinefox.tv"


def mainlist(item):
    logger.info()
    item.text_color = color1
    itemlist = []

    itemlist.append(item.clone(action="seccion_peliculas", title="Películas", fanart="http://i.imgur.com/PjJaW8o.png",
                               url="http://www.cinefox.tv/catalogue?type=peliculas"))
    # Seccion series
    itemlist.append(item.clone(action="seccion_series", title="Series",
                               url="http://www.cinefox.tv/ultimos-capitulos", fanart="http://i.imgur.com/9loVksV.png"))

    itemlist.append(item.clone(action="peliculas", title="Documentales", fanart="http://i.imgur.com/Q7fsFI6.png",
                               url="http://www.cinefox.tv/catalogue?type=peliculas&genre=documental"))

    if config.get_setting("adult_mode") != 0:
        itemlist.append(item.clone(action="peliculas", title="Sección Adultos +18",
                                   url="http://www.cinefox.tv/catalogue?type=adultos",
                                   fanart="http://i.imgur.com/kIvE1Zh.png"))

    itemlist.append(item.clone(title="Buscar...", action="local_search"))
    itemlist.append(item.clone(title="Configurar canal...", text_color="gold", action="configuracion", folder=False))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://www.cinefox.tv/search?q=%s" % texto
    try:
        return busqueda(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def local_search(item):
    logger.info()
    text = ""
    if config.get_setting("save_last_search", item.channel):
        text = config.get_setting("last_search", item.channel)
    from platformcode import platformtools
    texto = platformtools.dialog_input(default=text, heading="Buscar en Cinefox")
    if texto is None:
        return

    if config.get_setting("save_last_search", item.channel):
        config.set_setting("last_search", texto, item.channel)

    return search(item, texto)


def busqueda(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    patron = '<div class="poster-media-card">(.*?)(?:<li class="search-results-item media-item">|<footer>)'
    bloque = scrapertools.find_multiple_matches(data, patron)
    for match in bloque:
        patron = 'href="([^"]+)" title="([^"]+)".*?src="([^"]+)".*?' \
                 '<p class="search-results-main-info">.*?del año (\d+).*?' \
                 'p class.*?>(.*?)<'
        matches = scrapertools.find_multiple_matches(match, patron)
        for scrapedurl, scrapedtitle, scrapedthumbnail, year, plot in matches:
            scrapedtitle = scrapedtitle.capitalize()
            item.infoLabels["year"] = year
            plot = scrapertools.htmlclean(plot)
            if "/serie/" in scrapedurl:
                action = "episodios"
                show = scrapedtitle
                scrapedurl += "/episodios"
                title = " [Serie]"
                contentType = "tvshow"
            elif "/pelicula/" in scrapedurl:
                action = "menu_info"
                show = ""
                title = " [Película]"
                contentType = "movie"
            else:
                continue
            title = scrapedtitle + title + " (" + year + ")"
            itemlist.append(item.clone(action=action, title=title, url=scrapedurl, thumbnail=scrapedthumbnail,
                                       contentTitle=scrapedtitle, fulltitle=scrapedtitle,
                                       plot=plot, show=show, text_color=color2, contentType=contentType))

    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass

    next_page = scrapertools.find_single_match(data, 'href="([^"]+)"[^>]+>Más resultados')
    if next_page != "":
        next_page = urlparse.urljoin(host, next_page)
        itemlist.append(Item(channel=item.channel, action="busqueda", title=">> Siguiente", url=next_page,
                             thumbnail=item.thumbnail, text_color=color3))

    return itemlist


def filtro(item):
    logger.info()

    list_controls = []
    valores = {}
    strings = {}
    # Se utilizan los valores por defecto/guardados o los del filtro personalizado
    if not item.values:
        valores_guardados = config.get_setting("filtro_defecto_" + item.extra, item.channel)
    else:
        valores_guardados = item.values
        item.values = ""
    if valores_guardados:
        dict_values = valores_guardados
    else:
        dict_values = None
    if dict_values:
        dict_values["filtro_per"] = 0

    excluidos = ['País', 'Películas', 'Series', 'Destacar']
    data = httptools.downloadpage(item.url).data
    matches = scrapertools.find_multiple_matches(data, '<div class="dropdown-sub[^>]+>(\S+)(.*?)</ul>')
    i = 0
    for filtro_title, values in matches:
        if filtro_title in excluidos: continue

        filtro_title = filtro_title.replace("Tendencia", "Ordenar por")
        id = filtro_title.replace("Género", "genero").replace("Año", "year").replace(" ", "_").lower()
        list_controls.append({'id': id, 'label': filtro_title, 'enabled': True,
                              'type': 'list', 'default': 0, 'visible': True})
        valores[id] = []
        valores[id].append('')
        strings[filtro_title] = []
        list_controls[i]['lvalues'] = []
        if filtro_title == "Ordenar por":
            list_controls[i]['lvalues'].append('Más recientes')
            strings[filtro_title].append('Más recientes')
        else:
            list_controls[i]['lvalues'].append('Cualquiera')
            strings[filtro_title].append('Cualquiera')
        patron = '<li>.*?(?:genre|release|quality|language|order)=([^"]+)">([^<]+)<'
        matches_v = scrapertools.find_multiple_matches(values, patron)
        for value, key in matches_v:
            if value == "action-adventure": continue
            list_controls[i]['lvalues'].append(key)
            valores[id].append(value)
            strings[filtro_title].append(key)

        i += 1

    item.valores = valores
    item.strings = strings
    if "Filtro Personalizado" in item.title:
        return filtrado(item, valores_guardados)

    list_controls.append({'id': 'espacio', 'label': '', 'enabled': False,
                          'type': 'label', 'default': '', 'visible': True})
    list_controls.append({'id': 'save', 'label': 'Establecer como filtro por defecto', 'enabled': True,
                          'type': 'bool', 'default': False, 'visible': True})
    list_controls.append({'id': 'filtro_per', 'label': 'Guardar filtro en acceso directo...', 'enabled': True,
                          'type': 'list', 'default': 0, 'visible': True, 'lvalues': ['No guardar', 'Filtro 1',
                                                                                     'Filtro 2', 'Filtro 3']})
    list_controls.append({'id': 'remove', 'label': 'Eliminar filtro personalizado...', 'enabled': True,
                          'type': 'list', 'default': 0, 'visible': True, 'lvalues': ['No eliminar', 'Filtro 1',
                                                                                     'Filtro 2', 'Filtro 3']})

    from platformcode import platformtools
    return platformtools.show_channel_settings(list_controls=list_controls, dict_values=dict_values,
                                               caption="Filtra los resultados", item=item, callback='filtrado')


def filtrado(item, values):
    values_copy = values.copy()
    # Guarda el filtro para que sea el que se cargue por defecto
    if "save" in values and values["save"]:
        values_copy.pop("remove")
        values_copy.pop("filtro_per")
        values_copy.pop("save")
        config.set_setting("filtro_defecto_" + item.extra, values_copy, item.channel)

    # Elimina el filtro personalizado elegido
    if "remove" in values and values["remove"] != 0:
        config.set_setting("pers_" + item.extra + str(values["remove"]), "", item.channel)

    values_copy = values.copy()
    # Guarda el filtro en un acceso directo personalizado
    if "filtro_per" in values and values["filtro_per"] != 0:
        index = item.extra + str(values["filtro_per"])
        values_copy.pop("filtro_per")
        values_copy.pop("save")
        values_copy.pop("remove")
        config.set_setting("pers_" + index, values_copy, item.channel)

    genero = item.valores["genero"][values["genero"]]
    year = item.valores["year"][values["year"]]
    calidad = item.valores["calidad"][values["calidad"]]
    idioma = item.valores["idioma"][values["idioma"]]
    order = item.valores["ordenar_por"][values["ordenar_por"]]

    strings = []
    for key, value in dict(item.strings).items():
        key2 = key.replace("Género", "genero").replace("Año", "year").replace(" ", "_").lower()
        strings.append(key + ": " + value[values[key2]])

    item.valores = "Filtro: " + ", ".join(sorted(strings))
    item.strings = ""
    item.url = "http://www.cinefox.tv/catalogue?type=%s&genre=%s&release=%s&quality=%s&language=%s&order=%s" % \
               (item.extra, genero, year, calidad, idioma, order)

    return globals()[item.extra](item)


def seccion_peliculas(item):
    logger.info()
    itemlist = []
    # Seccion peliculas
    itemlist.append(item.clone(action="peliculas", title="Novedades", fanart="http://i.imgur.com/PjJaW8o.png",
                               url="http://www.cinefox.tv/catalogue?type=peliculas"))
    itemlist.append(item.clone(action="peliculas", title="Estrenos",
                               url="http://www.cinefox.tv/estrenos-de-cine", fanart="http://i.imgur.com/PjJaW8o.png"))
    itemlist.append(item.clone(action="filtro", title="Filtrar películas", extra="peliculas",
                               url="http://www.cinefox.tv/catalogue?type=peliculas",
                               fanart="http://i.imgur.com/PjJaW8o.png"))
    # Filtros personalizados para peliculas
    for i in range(1, 4):
        filtros = config.get_setting("pers_peliculas" + str(i), item.channel)
        if filtros:
            title = "Filtro Personalizado " + str(i)
            new_item = item.clone()
            new_item.values = filtros
            itemlist.append(new_item.clone(action="filtro", title=title, fanart="http://i.imgur.com/PjJaW8o.png",
                                           url="http://www.cinefox.tv/catalogue?type=peliculas", extra="peliculas"))
    itemlist.append(item.clone(action="mapa", title="Mapa de películas", extra="peliculas",
                               url="http://www.cinefox.tv/mapa-de-peliculas",
                               fanart="http://i.imgur.com/PjJaW8o.png"))

    return itemlist


def seccion_series(item):
    logger.info()
    itemlist = []
    # Seccion series
    itemlist.append(item.clone(action="ultimos", title="Últimos capítulos",
                               url="http://www.cinefox.tv/ultimos-capitulos", fanart="http://i.imgur.com/9loVksV.png"))
    itemlist.append(item.clone(action="series", title="Series recientes",
                               url="http://www.cinefox.tv/catalogue?type=series",
                               fanart="http://i.imgur.com/9loVksV.png"))
    itemlist.append(item.clone(action="filtro", title="Filtrar series", extra="series",
                               url="http://www.cinefox.tv/catalogue?type=series",
                               fanart="http://i.imgur.com/9loVksV.png"))
    # Filtros personalizados para series
    for i in range(1, 4):
        filtros = config.get_setting("pers_series" + str(i), item.channel)
        if filtros:
            title = "               Filtro Personalizado " + str(i)
            new_item = item.clone()
            new_item.values = filtros
            itemlist.append(new_item.clone(action="filtro", title=title, fanart="http://i.imgur.com/9loVksV.png",
                                           url="http://www.cinefox.tv/catalogue?type=series", extra="series"))
    itemlist.append(item.clone(action="mapa", title="Mapa de series", extra="series",
                               url="http://www.cinefox.tv/mapa-de-series",
                               fanart="http://i.imgur.com/9loVksV.png"))

    return itemlist


def mapa(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    patron = '<li class="sitemap-initial"> <a class="initial-link" href="([^"]+)">(.*?)</a>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        scrapedtitle = scrapedtitle.capitalize()
        itemlist.append(item.clone(title=scrapedtitle, url=scrapedurl, action=item.extra, extra="mapa"))

    return itemlist


def peliculas(item):
    logger.info()

    itemlist = []
    if "valores" in item and item.valores:
        itemlist.append(item.clone(action="", title=item.valores, text_color=color4))

    if __menu_info__:
        action = "menu_info"
    else:
        action = "findvideos"

    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_multiple_matches(data,
                                                '<div class="media-card "(.*?)<div class="hidden-info">')
    for match in bloque:
        if item.extra == "mapa":
            patron = '.*?src="([^"]+)".*?href="([^"]+)">([^<]+)</a>'
            matches = scrapertools.find_multiple_matches(match, patron)
            for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
                url = urlparse.urljoin(host, scrapedurl)
                itemlist.append(Item(channel=item.channel, action=action, title=scrapedtitle, url=url, extra="media",
                                     thumbnail=scrapedthumbnail, contentTitle=scrapedtitle, fulltitle=scrapedtitle,
                                     text_color=color2, contentType="movie"))
        else:
            patron = '<div class="audio-info">(.*?)</div>(.*?)' \
                     'src="([^"]+)".*?href="([^"]+)">([^<]+)</a>'
            matches = scrapertools.find_multiple_matches(match, patron)

            for idiomas, calidad, scrapedthumbnail, scrapedurl, scrapedtitle in matches:
                calidad = scrapertools.find_single_match(calidad, '<div class="quality-info".*?>([^<]+)</div>')
                if calidad:
                    calidad = calidad.capitalize().replace("Hd", "HD")
                audios = []
                if "medium-es" in idiomas: audios.append('CAST')
                if "medium-vs" in idiomas: audios.append('VOSE')
                if "medium-la" in idiomas: audios.append('LAT')
                if "medium-en" in idiomas or 'medium-"' in idiomas:
                    audios.append('V.O')
                title = "%s  [%s]" % (scrapedtitle, "/".join(audios))
                if calidad:
                    title += " (%s)" % calidad
                url = urlparse.urljoin(host, scrapedurl)

                itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, extra="media",
                                     thumbnail=scrapedthumbnail, contentTitle=scrapedtitle, fulltitle=scrapedtitle,
                                     text_color=color2, contentType="movie"))

    next_page = scrapertools.find_single_match(data, 'href="([^"]+)"[^>]+>Siguiente')
    if next_page != "" and item.title != "":
        itemlist.append(Item(channel=item.channel, action="peliculas", title=">> Siguiente", url=next_page,
                             thumbnail=item.thumbnail, extra=item.extra, text_color=color3))

        if not config.get_setting("last_page", item.channel) and config.is_xbmc():
            itemlist.append(Item(channel=item.channel, action="select_page", title="Ir a página...", url=next_page,
                                 thumbnail=item.thumbnail, text_color=color5))

    return itemlist


def ultimos(item):
    logger.info()
    item.text_color = color2

    if __menu_info__:
        action = "menu_info_episode"
    else:
        action = "episodios"

    itemlist = []
    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_multiple_matches(data, '<div class="media-card "(.*?)<div class="info-availability '
                                                      'one-line">')
    for match in bloque:
        patron = '<div class="audio-info">(.*?)<img class.*?src="([^"]+)".*?href="([^"]+)">([^<]+)</a>'
        matches = scrapertools.find_multiple_matches(match, patron)
        for idiomas, scrapedthumbnail, scrapedurl, scrapedtitle in matches:
            show = re.sub(r'(\s*[\d]+x[\d]+\s*)', '', scrapedtitle)
            audios = []
            if "medium-es" in idiomas: audios.append('CAST')
            if "medium-vs" in idiomas: audios.append('VOSE')
            if "medium-la" in idiomas: audios.append('LAT')
            if "medium-en" in idiomas or 'medium-"' in idiomas:
                audios.append('V.O')
            title = "%s - %s" % (show, re.sub(show, '', scrapedtitle))
            if audios:
                title += " [%s]" % "/".join(audios)
            url = urlparse.urljoin(host, scrapedurl)
            itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=scrapedthumbnail,
                                       contentTitle=show, fulltitle=show, show=show,
                                       text_color=color2, extra="ultimos", contentType="tvshow"))

    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass

    next_page = scrapertools.find_single_match(data, 'href="([^"]+)"[^>]+>Siguiente')
    if next_page != "":
        itemlist.append(item.clone(action="ultimos", title=">> Siguiente", url=next_page, text_color=color3))

    return itemlist


def series(item):
    logger.info()
    itemlist = []

    if "valores" in item:
        itemlist.append(item.clone(action="", title=item.valores, text_color=color4))

    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_multiple_matches(data, '<div class="media-card "(.*?)<div class="hidden-info">')
    for match in bloque:
        patron = '<img class.*?src="([^"]+)".*?href="([^"]+)">([^<]+)</a>'
        matches = scrapertools.find_multiple_matches(match, patron)
        for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
            url = urlparse.urljoin(host, scrapedurl + "/episodios")
            itemlist.append(Item(channel=item.channel, action="episodios", title=scrapedtitle, url=url,
                                 thumbnail=scrapedthumbnail, contentTitle=scrapedtitle, fulltitle=scrapedtitle,
                                 show=scrapedtitle, text_color=color2, contentType="tvshow"))

    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass

    next_page = scrapertools.find_single_match(data, 'href="([^"]+)"[^>]+>Siguiente')
    if next_page != "":
        title = ">> Siguiente - Página " + scrapertools.find_single_match(next_page, 'page=(\d+)')
        itemlist.append(Item(channel=item.channel, action="series", title=title, url=next_page,
                             thumbnail=item.thumbnail, extra=item.extra, text_color=color3))

    return itemlist


def menu_info(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    year = scrapertools.find_single_match(data, '<div class="media-summary">.*?release.*?>(\d+)<')
    if year != "" and not "tmdb_id" in item.infoLabels:
        try:
            from core import tmdb
            item.infoLabels["year"] = year
            tmdb.set_infoLabels_item(item, __modo_grafico__)
        except:
            pass

    if item.infoLabels["plot"] == "":
        sinopsis = scrapertools.find_single_match(data, '<p id="media-plot".*?>.*?\.\.\.(.*?)Si te parece')
        item.infoLabels["plot"] = scrapertools.htmlclean(sinopsis)

    id = scrapertools.find_single_match(item.url, '/(\d+)/')
    data_trailer = httptools.downloadpage("http://www.cinefox.tv/media/trailer?idm=%s&mediaType=1" % id).data
    trailer_url = jsontools.load(data_trailer)["video"]["url"]
    if trailer_url != "":
        item.infoLabels["trailer"] = trailer_url

    title = "Ver enlaces %s - [" + item.contentTitle + "]"
    itemlist.append(item.clone(action="findvideos", title=title % "Online", extra="media", type="streaming"))
    itemlist.append(item.clone(action="findvideos", title=title % "de Descarga", extra="media", type="download"))
    itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                               text_color="magenta", context=""))
    if config.get_videolibrary_support():
        itemlist.append(Item(channel=item.channel, action="add_pelicula_to_library", text_color=color5,
                             title="Añadir película a la videoteca", url=item.url, thumbnail=item.thumbnail,
                             fanart=item.fanart, fulltitle=item.fulltitle,
                             extra="media|"))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if item.extra == "ultimos":
        data = httptools.downloadpage(item.url).data
        item.url = scrapertools.find_single_match(data, '<a href="([^"]+)" class="h1-like media-title"')
        item.url += "/episodios"

    data = httptools.downloadpage(item.url).data
    data_season = data[:]

    if "episodios" in item.extra or not __menu_info__ or item.path:
        action = "findvideos"
    else:
        action = "menu_info_episode"

    seasons = scrapertools.find_multiple_matches(data, '<a href="([^"]+)"[^>]+><span class="season-toggle')
    for i, url in enumerate(seasons):
        if i != 0:
            data_season = httptools.downloadpage(url, add_referer=True).data
        patron = '<div class="ep-list-number">.*?href="([^"]+)">([^<]+)</a>.*?<span class="name">([^<]+)</span>'
        matches = scrapertools.find_multiple_matches(data_season, patron)
        for scrapedurl, episode, scrapedtitle in matches:
            new_item = item.clone(action=action, url=scrapedurl, text_color=color2, contentType="episode")
            new_item.contentSeason = episode.split("x")[0]
            new_item.contentEpisodeNumber = episode.split("x")[1]

            new_item.title = episode + " - " + scrapedtitle
            new_item.extra = "episode"
            if "episodios" in item.extra or item.path:
                new_item.extra = "episode|"
            itemlist.append(new_item)

    if "episodios" not in item.extra and not item.path:
        try:
            from core import tmdb
            tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
        except:
            pass

    itemlist.reverse()
    if "episodios" not in item.extra and not item.path:
        id = scrapertools.find_single_match(item.url, '/(\d+)/')
        data_trailer = httptools.downloadpage("http://www.cinefox.tv/media/trailer?idm=%s&mediaType=1" % id).data
        item.infoLabels["trailer"] = jsontools.load(data_trailer)["video"]["url"]
        itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                                   text_color="magenta"))
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, action="add_serie_to_library", text_color=color5,
                                 title="Añadir serie a la videoteca", show=item.show, thumbnail=item.thumbnail,
                                 url=item.url, fulltitle=item.fulltitle, fanart=item.fanart,
                                 extra="episodios###episodios",
                                 contentTitle=item.fulltitle))

    return itemlist


def menu_info_episode(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    if item.show == "":
        item.show = scrapertools.find_single_match(data, 'class="h1-like media-title".*?>([^<]+)</a>')

    episode = scrapertools.find_single_match(data, '<span class="indicator">([^<]+)</span>')
    item.infoLabels["season"] = episode.split("x")[0]
    item.infoLabels["episode"] = episode.split("x")[1]

    try:
        from core import tmdb
        tmdb.set_infoLabels_item(item, __modo_grafico__)
    except:
        pass

    if item.infoLabels["plot"] == "":
        sinopsis = scrapertools.find_single_match(data, 'id="episode-plot">(.*?)</p>')
        if not "No hay sinopsis" in sinopsis:
            item.infoLabels["plot"] = scrapertools.htmlclean(sinopsis)

    title = "Ver enlaces %s - [" + item.show + " " + episode + "]"
    itemlist.append(item.clone(action="findvideos", title=title % "Online", extra="episode", type="streaming"))
    itemlist.append(item.clone(action="findvideos", title=title % "de Descarga", extra="episode", type="download"))

    siguiente = scrapertools.find_single_match(data, '<a class="episode-nav-arrow next" href="([^"]+)" title="([^"]+)"')
    if siguiente:
        titulo = ">> Siguiente Episodio - [" + siguiente[1] + "]"
        itemlist.append(item.clone(action="menu_info_episode", title=titulo, url=siguiente[0], extra="",
                                   text_color=color1))

    patron = '<a class="episode-nav-arrow previous" href="([^"]+)" title="([^"]+)"'
    anterior = scrapertools.find_single_match(data, patron)
    if anterior:
        titulo = "<< Episodio Anterior - [" + anterior[1] + "]"
        itemlist.append(item.clone(action="menu_info_episode", title=titulo, url=anterior[0], extra="",
                                   text_color=color3))

    url_serie = scrapertools.find_single_match(data, '<a href="([^"]+)" class="h1-like media-title"')
    url_serie += "/episodios"
    itemlist.append(item.clone(title="Ir a la lista de capítulos", action="episodios", url=url_serie, extra="",
                               text_color=color4))

    itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                               text_color="magenta", context=""))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if not "|" in item.extra and not __menu_info__:
        data = httptools.downloadpage(item.url, add_referer=True).data
        year = scrapertools.find_single_match(data, '<div class="media-summary">.*?release.*?>(\d+)<')
        if year != "" and not "tmdb_id" in item.infoLabels:
            try:
                from core import tmdb
                item.infoLabels["year"] = year
                tmdb.set_infoLabels_item(item, __modo_grafico__)
            except:
                pass

        if item.infoLabels["plot"] == "":
            sinopsis = scrapertools.find_single_match(data, '<p id="media-plot".*?>.*?\.\.\.(.*?)Si te parece')
            item.infoLabels["plot"] = scrapertools.htmlclean(sinopsis)

    id = scrapertools.find_single_match(item.url, '/(\d+)/')
    if "|" in item.extra or not __menu_info__:
        extra = item.extra
        if "|" in item.extra:
            extra = item.extra[:-1]
        url = "http://www.cinefox.tv/sources/list?id=%s&type=%s&order=%s" % (id, extra, "streaming")
        itemlist.extend(get_enlaces(item, url, "Online"))
        url = "http://www.cinefox.tv/sources/list?id=%s&type=%s&order=%s" % (id, extra, "download")
        itemlist.extend(get_enlaces(item, url, "de Descarga"))

        if extra == "media":
            data_trailer = httptools.downloadpage("http://www.cinefox.tv/media/trailer?idm=%s&mediaType=1" % id).data
            trailer_url = jsontools.load(data_trailer)["video"]["url"]
            if trailer_url != "":
                item.infoLabels["trailer"] = trailer_url

            title = "Ver enlaces %s - [" + item.contentTitle + "]"
            itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                                       text_color="magenta", context=""))

            if config.get_videolibrary_support() and not "|" in item.extra:
                itemlist.append(Item(channel=item.channel, action="add_pelicula_to_library", text_color=color5,
                                     title="Añadir película a la videoteca", url=item.url, thumbnail=item.thumbnail,
                                     fanart=item.fanart, fulltitle=item.fulltitle,
                                     extra="media|"))
    else:
        url = "http://www.cinefox.tv/sources/list?id=%s&type=%s&order=%s" % (id, item.extra, item.type)
        type = item.type.replace("streaming", "Online").replace("download", "de Descarga")
        itemlist.extend(get_enlaces(item, url, type))

    return itemlist


def get_enlaces(item, url, type):
    itemlist = []
    itemlist.append(item.clone(action="", title="Enlaces %s" % type, text_color=color1))

    data = httptools.downloadpage(url, add_referer=True).data
    patron = '<div class="available-source".*?data-url="([^"]+)".*?class="language.*?title="([^"]+)"' \
             '.*?class="source-name.*?>\s*([^<]+)<.*?<span class="quality-text">([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    if matches:
        for scrapedurl, idioma, server, calidad in matches:
            if server == "streamin": server = "streaminto"
            if server == "waaw" or server == "miracine": server = "netutv"
            if server == "ul": server = "uploadedto"
            if server == "player": server = "vimpleru"
            if servertools.is_server_enabled(server):
                scrapedtitle = "    Ver en " + server.capitalize() + " [" + idioma + "/" + calidad + "]"
                itemlist.append(item.clone(action="play", url=scrapedurl, title=scrapedtitle, text_color=color2,
                                           extra="", server=server))

    if len(itemlist) == 1:
        itemlist.append(item.clone(title="   No hay enlaces disponibles", action="", text_color=color2))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.extra != "":
        post = "id=%s" % item.extra
        data = httptools.downloadpage("http://www.cinefox.tv/goto/", post=post, add_referer=True).data

        item.url = scrapertools.find_single_match(data, 'document.location\s*=\s*"([^"]+)"')

    url = item.url.replace("http://miracine.tv/n/?etu=", "http://hqq.tv/player/embed_player.php?vid=")
    url = url.replace("streamcloud.eu/embed-", "streamcloud.eu/")
    if item.server:
        enlaces = servertools.findvideosbyserver(url, item.server)[0]
    else:
        enlaces = servertools.findvideos(url)[0]
    itemlist.append(item.clone(url=enlaces[1], server=enlaces[2]))

    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = "http://www.cinefox.tv/catalogue?type=peliculas"
            item.action = "peliculas"
            itemlist = peliculas(item)

            if itemlist[-1].action == "peliculas":
                itemlist.pop()

        if categoria == "series":
            item.url = "http://www.cinefox.tv/ultimos-capitulos"
            item.action = "ultimos"
            itemlist = ultimos(item)

            if itemlist[-1].action == "ultimos":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def select_page(item):
    import xbmcgui
    dialog = xbmcgui.Dialog()
    number = dialog.numeric(0, "Introduce el número de página")
    if number != "":
        item.url = re.sub(r'page=(\d+)', "page=" + number, item.url)

    return peliculas(item)
