# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

__modo_grafico__ = config.get_setting("modo_grafico", "inkapelis")
__perfil__ = config.get_setting("perfil", "inkapelis")

# Fijar perfil de color
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00', '0xFFFE2E2E'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E', '0xFFFE2E2E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE', '0xFFFE2E2E']]
color1, color2, color3, color4 = perfil[__perfil__]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(title="Novedades", action="entradas", url="http://www.inkapelis.com/",
                               extra="Novedades", text_color=color1))
    itemlist.append(item.clone(title="Estrenos", action="entradas", url="http://www.inkapelis.com/genero/estrenos/",
                               text_color=color1))
    itemlist.append(item.clone(title="Géneros", action="generos", url="http://www.inkapelis.com/", text_color=color1))
    itemlist.append(item.clone(title="Buscar...", action="search", text_color=color1))
    itemlist.append(item.clone(action="", title=""))
    itemlist.append(
        item.clone(action="filtro", title="Filtrar películas", url="http://www.inkapelis.com/?s=", text_color=color1))
    # Filtros personalizados para peliculas
    for i in range(1, 4):
        filtros = config.get_setting("pers_peliculas" + str(i), item.channel)
        if filtros:
            title = "Filtro Personalizado " + str(i)
            new_item = item.clone()
            new_item.values = filtros
            itemlist.append(
                new_item.clone(action="filtro", title=title, url="http://www.inkapelis.com/?s=", text_color=color2))
    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", text_color="gold", folder=False))
    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = "http://www.inkapelis.com/"
            item.action = "entradas"
            item.extra = "Novedades"
            itemlist = entradas(item)

            if itemlist[-1].action == "entradas":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []
    item.extra = "Buscar"
    item.url = "http://www.inkapelis.com/?s=%s" % texto

    try:
        return entradas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def generos(item):
    logger.info()
    itemlist = []

    item.text_color = color1
    data = httptools.downloadpage(item.url).data
    matches = scrapertools.find_multiple_matches(data, '<li class="cat-item cat-item-.*?><a href="([^"]+)".*?>(.*?)<b>')

    for scrapedurl, scrapedtitle in matches:
        if scrapedtitle == "Eroticas +18 " and config.get_setting("adult_mode") != "0":
            itemlist.append(item.clone(action="eroticas", title=scrapedtitle, url=scrapedurl))
        elif (scrapedtitle != "Estrenos ") and (scrapedtitle != "Próximos Estrenos "):
            itemlist.append(item.clone(action="entradas", title=scrapedtitle, url=scrapedurl))

    return itemlist


def filtro(item):
    logger.info()

    list_controls = []
    valores = {}
    strings = {}
    # Se utilizan los valores por defecto/guardados o los del filtro personalizado
    if not item.values:
        valores_guardados = config.get_setting("filtro_defecto_peliculas", item.channel)
    else:
        valores_guardados = item.values
        item.values = ""

    if valores_guardados:
        dict_values = valores_guardados
    else:
        dict_values = None
    if dict_values:
        dict_values["filtro_per"] = 0

    list_controls.append({'id': 'texto', 'label': 'Cadena de búsqueda', 'enabled': True,
                          'type': 'text', 'default': '', 'visible': True})
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    matches = scrapertools.find_multiple_matches(data, 'option value="">([^<]+)</option>(.*?)</select>')
    i = 1
    for filtro_title, values in matches:
        id = filtro_title.replace("A\xc3\xb1o", "year").lower()
        filtro_title = filtro_title.replace("A\xc3\xb1o", "Año")
        list_controls.append({'id': id, 'label': filtro_title, 'enabled': True,
                              'type': 'list', 'default': 0, 'visible': True})
        valores[id] = []
        valores[id].append('')
        strings[filtro_title] = []
        list_controls[i]['lvalues'] = []
        list_controls[i]['lvalues'].append('Cualquiera')
        strings[filtro_title].append('Cualquiera')
        patron = '<option value="([^"]+)">([^<]+)</option>'
        matches_v = scrapertools.find_multiple_matches(values, patron)
        for value, key in matches_v:
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
        config.set_setting("filtro_defecto_peliculas", values_copy, item.channel)

    # Elimina el filtro personalizado elegido
    if "remove" in values and values["remove"] != 0:
        config.set_setting("pers_peliculas" + str(values["remove"]), "", item.channel)

    values_copy = values.copy()
    # Guarda el filtro en un acceso directo personalizado
    if "filtro_per" in values and values["filtro_per"] != 0:
        index = "peliculas" + str(values["filtro_per"])
        values_copy.pop("filtro_per")
        values_copy.pop("save")
        values_copy.pop("remove")
        config.set_setting("pers_" + index, values_copy, item.channel)

    genero = item.valores["genero"][values["genero"]]
    year = item.valores["year"][values["year"]]
    calidad = item.valores["calidad"][values["calidad"]]
    idioma = item.valores["idioma"][values["idioma"]]
    texto = values["texto"].replace(" ", "+")

    strings = []
    for key, value in dict(item.strings).items():
        key2 = key.replace("Año", "year").lower()
        strings.append(key + ": " + value[values[key2]])
    strings.append("Texto: " + texto)

    item.valores = "Filtro: " + ", ".join(sorted(strings))
    item.strings = ""
    item.url = "http://www.inkapelis.com/?anio=%s&genero=%s&calidad=%s&idioma=%s&s=%s" % \
               (year, genero, calidad, idioma, texto)
    item.extra = "Buscar"

    return entradas(item)


def entradas(item):
    logger.info()

    itemlist = []
    item.text_color = color2
    # Descarga la página
    data = httptools.downloadpage(item.url).data
    if "valores" in item and item.valores:
        itemlist.append(item.clone(action="", title=item.valores, text_color=color4))

    # IF en caso de busqueda
    if item.extra == "Buscar":
        # Extrae las entradas
        entradas = scrapertools.find_multiple_matches(data, '<div class="col-mt-5 postsh">(.*?)</div></div></div>')
        patron = '<div class="poster-media-card([^"]+)">.*?<a href="([^"]+)" title="([^"]+)">' \
                 '.*?<img.*?src="([^"]+)"'
        for match in entradas:
            matches = scrapertools.find_multiple_matches(match, patron)
            for calidad, scrapedurl, scrapedtitle, scrapedthumbnail in matches:
                thumbnail = scrapedthumbnail.replace("w185", "original")
                title = scrapedtitle
                calidad = calidad.strip()
                if calidad:
                    title += "  [" + calidad + "]"

                itemlist.append(item.clone(action="findvideos", title=title, url=scrapedurl, thumbnail=thumbnail,
                                           contentTitle=scrapedtitle, fulltitle=scrapedtitle,
                                           context=["buscar_trailer"],
                                           contentType="movie"))

    else:
        # Extrae las entradas
        if item.extra == "Novedades":
            data2 = data.split("<h3>Últimas Películas Agregadas</h3>", 1)[1]
            entradas = scrapertools.find_multiple_matches(data2, '<div class="col-mt-5 postsh">(.*?)</div></div></div>')
        else:
            entradas = scrapertools.find_multiple_matches(data, '<div class="col-mt-5 postsh">(.*?)</div></div></div>')

        patron = '<div class="poster-media-card([^"]+)">.*?<a href="([^"]+)" title="([^"]+)">' \
                 '.*?<div class="idiomes"><div class="(.*?)">.*?' \
                 '<img.*?src="([^"]+)".*?<span class="under-title">(.*?)</span>'
        for match in entradas:
            matches = scrapertools.find_multiple_matches(match, patron)
            for calidad, url, scrapedtitle, idioma, scrapedthumbnail, category in matches:
                # Salto entradas adultos
                if category == "Eroticas +18":
                    continue
                idioma = idioma.strip()
                calidad = calidad.strip()
                scrapedtitle = scrapedtitle.replace("Ver Pelicula ", "")
                title = scrapedtitle
                if idioma:
                    title += "  [" + idioma + "]"
                if calidad:
                    title += "  [" + calidad + "]"
                if 'class="proximamente"' in match:
                    title += " [Próximamente]"
                thumbnail = scrapedthumbnail.replace("w185", "original")

                itemlist.append(item.clone(action="findvideos", title=title, url=url, contentTitle=scrapedtitle,
                                           fulltitle=scrapedtitle, thumbnail=thumbnail, context=["buscar_trailer"],
                                           contentType="movie"))

    # Extrae la marca de la siguiente página
    next_page = scrapertools.find_single_match(data, '<span class="current">.*?<\/span><a href="([^"]+)"')
    if next_page:
        if item.extra == "Buscar":
            next_page = next_page.replace('&#038;', '&')
        itemlist.append(item.clone(action="entradas", title="Siguiente", url=next_page, text_color=color3))

    return itemlist


def eroticas(item):
    logger.info()

    itemlist = []
    # Descarga la página
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas
    entradas = scrapertools.find_multiple_matches(data, '<div class="col-mt-5 postsh">(.*?)</div></div></div>')
    patron = '<div class="poster-media-card([^"]+)">.*?<a href="([^"]+)" title="([^"]+)">' \
             '.*?<div class="idiomes"><div class="(.*?)">.*?' \
             '<img.*?src="([^"]+)"'
    for match in entradas:
        matches = scrapertools.find_multiple_matches(match, patron)
        for calidad, url, scrapedtitle, idioma, scrapedthumbnail in matches:
            title = scrapedtitle + "  [" + idioma + "] [" + calidad + "]"
            thumbnail = scrapedthumbnail.replace("w185", "original")

            itemlist.append(item.clone(action="findvideos", title=title, url=url, thumbnail=thumbnail,
                                       extra="eroticas"))

    # Extrae la marca de la siguiente página
    next_page = scrapertools.find_single_match(data, '<span class="current">.*?<\/span><a href="([^"]+)"')
    if next_page:
        itemlist.append(item.clone(action="entradas", title="Siguiente", url=next_page))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    item.text_color = color2

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    sinopsis = scrapertools.find_single_match(data, '<h2>Sinopsis</h2>.*?>(.*?)</p>')
    item.infoLabels["plot"] = scrapertools.htmlclean(sinopsis)
    # Busca en tmdb si no se ha hecho antes
    if item.extra != "eroticas":
        if item.extra != "library":
            year = scrapertools.find_single_match(data, 'Año de lanzamiento.*?"ab">(\d+)')
            if year:
                try:
                    item.infoLabels['year'] = year
                    # Obtenemos los datos basicos de todas las peliculas mediante multihilos
                    tmdb.set_infoLabels(item, __modo_grafico__)
                except:
                    pass
        trailer_url = scrapertools.find_single_match(data, 'id="trailerpro">.*?src="([^"]+)"')
        item.infoLabels["trailer"] = "www.youtube.com/watch?v=TqqF3-qgJw4"

    patron = '<td><a href="([^"]+)".*?title="([^"]+)".*?<td>([^"]+)<\/td><td>([^"]+)<\/td>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, server, idioma, calidad in matches:
        if server == "Embed":
            server = "Nowvideo"
        if server == "Ul":
            server = "Uploaded"
        title = "%s  [%s][%s]" % (server, idioma, calidad)
        itemlist.append(item.clone(action="play", title=title, url=url))

    patron = 'id="(embed[0-9]*)".*?<div class="calishow">(.*?)<.*?src="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for id_embed, calidad, url in matches:
        title = scrapertools.find_single_match(url, "(?:http://|https://|//)(.*?)(?:embed.|videoembed|)/")
        if re.search(r"(?i)inkapelis|goo.gl", title):
            title = "Directo"
        idioma = scrapertools.find_single_match(data, 'href="#%s".*?>([^<]+)<' % id_embed)
        title = "%s  [%s][%s]" % (title.capitalize(), idioma, calidad)
        itemlist.append(item.clone(action="play", title=title, url=url))

    if itemlist:
        if not config.get_setting('menu_trailer', item.channel):
            itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                                       text_color="magenta", context=""))
        if item.extra != "library":
            if config.get_videolibrary_support():
                itemlist.append(Item(channel=item.channel, title="Añadir película a la videoteca",
                                     action="add_pelicula_to_library", url=item.url, fulltitle=item.fulltitle,
                                     infoLabels={'title': item.fulltitle}, text_color="green", extra="library"))

    return itemlist


def play(item):
    logger.info()
    itemlist = []
    if "drive.php?v=" in item.url or "//goo.gl/" in item.url:
        data = httptools.downloadpage(item.url).data.replace("\\", "")
        matches = scrapertools.find_multiple_matches(data, '"label":(.*?),.*?type":".*?/([^"]+)".*?file":"([^"]+)"')
        for calidad, ext, url in matches:
            title = ".%s %s [directo]" % (ext, calidad)
            itemlist.insert(0, [title, url])
    else:
        itemlist = servertools.find_video_items(data=item.url)

    return itemlist
