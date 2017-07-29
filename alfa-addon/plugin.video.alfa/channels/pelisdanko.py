# -*- coding: utf-8 -*-

import re

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__modo_grafico__ = config.get_setting('modo_grafico', 'pelisdanko')

host = "http://pelisdanko.com"
art = "http://pelisdanko.com/img/background.jpg"


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(item.clone(action="novedades", title="Novedades", url=host + "/novedades",
                               fanart=art))
    itemlist.append(item.clone(action="novedades", title="Estrenos", url=host + "/estrenos",
                               fanart=art))
    itemlist.append(item.clone(action="novedades", title="Populares", url=host + "/populares",
                               fanart=art))
    itemlist.append(item.clone(action="actualizadas", title="Películas actualizadas", url=host,
                               fanart=art))
    itemlist.append(item.clone(action="indices", title="Índices", fanart=art))
    itemlist.append(item.clone(title="", action=""))
    itemlist.append(item.clone(action="search", title="Buscar...", fanart=art))

    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", fanart=art,
                               text_color="gold", folder=False))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://pelisdanko.com/busqueda?terms=%s" % texto
    try:
        return novedades(item)
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
            item.url = "http://pelisdanko.com/novedades"
            itemlist = novedades(item)

            if itemlist[-1].action == "novedades":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def novedades(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    data = scrapertools.downloadpage(item.url)
    bloque = scrapertools.find_multiple_matches(data, '<div class="col-xs-[\d] col-sm-[\d] col-md-[\d] col-lg-[\d]'
                                                      ' text-center"(.*?)</div>')

    for match in bloque:
        calidades = scrapertools.find_multiple_matches(match, '<span class="badge badge-critic badge-qualities[^>]+>'
                                                              '([^<]+)</span>')
        calidad = "[COLOR darkseagreen]   "
        for quality in calidades:
            calidad += "[" + quality + "]"
        patron = 'title="([^"]+)".*?href="([^"]+)".*?class="img-responsive img-thumbnail" src="([^"]+)"'
        matches = scrapertools.find_multiple_matches(match, patron)
        for scrapedtitle, scrapedurl, scrapedthumbnail in matches:
            contentTitle = scrapedtitle[:]
            scrapedtitle = "[COLOR darkorange][B]" + scrapedtitle + "[/B][/COLOR]" + calidad + "[/COLOR]"
            logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
            itemlist.append(item.clone(action="enlaces", title=bbcode_kodi2html(scrapedtitle),
                                       url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail,
                                       fulltitle=contentTitle, filtro=False, contentTitle=contentTitle,
                                       context=["buscar_trailer"], contentType="movie", trailer=True))

    # Busca enlaces de paginas siguientes...
    next_page_url = scrapertools.find_single_match(data, '<a href="([^"]+)" rel="next">')
    if len(next_page_url) > 0:
        itemlist.append(item.clone(action="novedades", title=">> Página siguiente", url=next_page_url))

    return itemlist


def actualizadas(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    data = scrapertools.downloadpage(item.url)
    bloque_big = scrapertools.find_single_match(data, 'Últimas actualizaciones(.*?)<div class="col-xs-10 col-md-8 '
                                                      'text-left">')
    bloque = scrapertools.find_multiple_matches(bloque_big, '<div class="col-xs-[\d] col-sm-[\d] col-md-[\d]'
                                                            ' col-lg-[\d] text-center"(.*?)<br><br>')

    for match in bloque:
        calidades = scrapertools.find_multiple_matches(match, '<span class="badge badge-critic badge-qualities[^>]+>'
                                                              '([^<]+)</span>')
        calidad = "[COLOR darkseagreen]  "
        for quality in calidades:
            calidad += "[" + quality + "]"
        languages = scrapertools.find_multiple_matches(match, '<img width="28".*?alt="([^"]+)"')
        idiomas = "  ("
        for idioma in languages:
            idioma = idioma.replace('ES_', '').replace('ES', 'CAST')
            if idioma != "CAST" and idioma != "LAT":
                idioma = "VOSE"
            idiomas += idioma + "/"
        patron = 'title="([^"]+)".*?href="([^"]+)".*?class="img-responsive img-thumbnail" src="([^"]+)"'
        matches = scrapertools.find_multiple_matches(match, patron)
        for scrapedtitle, scrapedurl, scrapedthumbnail in matches:
            contentTitle = scrapedtitle[:]
            scrapedtitle = "[COLOR darkorange][B]" + scrapedtitle + "[/B][/COLOR]" + calidad + idiomas[
                                                                                               :-1] + ")[/COLOR]"
            logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
            itemlist.append(item.clone(action="enlaces", title=bbcode_kodi2html(scrapedtitle),
                                       url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail,
                                       fulltitle=contentTitle, filtro=False, contentTitle=contentTitle,
                                       context=["buscar_trailer"], contentType="movie"))

    return itemlist


def indices(item):
    logger.info()
    itemlist = []

    item.text_color = "orchid"
    itemlist.append(item.clone(action="indice_list", title="Género", url=host, fulltitle="genero"))
    itemlist.append(item.clone(action="indice_list", title="Alfabético", url=host, fulltitle="letra"))
    itemlist.append(item.clone(action="indice_list", title="Idioma", url=host, fulltitle="idioma"))
    itemlist.append(item.clone(action="indice_list", title="Calidad", url=host, fulltitle="calidad"))
    itemlist.append(item.clone(action="indice_list", title="Nacionalidad", url=host, fulltitle="nacionalidad"))

    return itemlist


def indice_list(item):
    logger.info()
    itemlist = []
    # Descarga la pagina
    data = scrapertools.downloadpage(item.url)

    patron = '<a href="(http://pelisdanko.com/%s/[^"]+)">([^<]+)</a>' % item.fulltitle
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.capitalize()
        itemlist.append(item.clone(action="novedades", title=scrapedtitle, url=scrapedurl))

    return itemlist


def enlaces(item):
    logger.info()
    item.extra = ""
    item.text_color = ""
    itemlist = []
    # Descarga la pagina
    data = scrapertools.downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}", '', data)
    item.fanart = scrapertools.find_single_match(data, "CUSTOM BACKGROUND.*?url\('([^']+)'")
    item.infoLabels["plot"] = scrapertools.find_single_match(data, 'dt>Sinopsis</dt> <dd class=[^>]+>(.*?)</dd>')
    year = scrapertools.find_single_match(data, '<dt>Estreno</dt> <dd>(\d+)</dd>')

    try:
        from core import tmdb
        item.infoLabels['year'] = int(year)
        # Obtenemos los datos basicos de todas las peliculas mediante multihilos
        tmdb.set_infoLabels_item(item, __modo_grafico__)
    except:
        pass

    filtro_idioma = config.get_setting("filterlanguages", item.channel)
    filtro_enlaces = config.get_setting("filterlinks", item.channel)

    dict_idiomas = {'CAST': 2, 'LAT': 1, 'VOSE': 0}

    if filtro_enlaces != 0:
        itemlist.append(item.clone(action="", title="Enlaces Online", text_color="dodgerblue", text_bold=True))
        itemlist = bloque_enlaces(data, filtro_idioma, dict_idiomas, itemlist, "ss", item)
    if filtro_enlaces != 1:
        itemlist.append(item.clone(action="", title="Enlaces Descarga", text_color="dodgerblue", text_bold=True))
        itemlist = bloque_enlaces(data, filtro_idioma, dict_idiomas, itemlist, "dd", item)

    trailer_id = scrapertools.find_single_match(data, 'data:\s*\{\s*id:\s*"([^"]+)"')
    data_trailer = scrapertools.downloadpage("http://pelisdanko.com/trailer", post="id=%s" % trailer_id)
    url_trailer = scrapertools.find_single_match(data_trailer, 'src="([^"]+)"')
    if url_trailer != "":
        url_trailer = url_trailer.replace("embed/", "watch?v=")
        item.infoLabels['trailer'] = url_trailer
        itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                                   text_color="magenta"))

    return itemlist


def bloque_enlaces(data, filtro_idioma, dict_idiomas, itemlist, type, item):
    logger.info()
    bloque = scrapertools.find_single_match(data, '<div role="tabpanel" class="tab-pane fade" id="tab-' +
                                            type + '">(.*?)</table>')
    patron = '<tr class="rip hover".*?data-slug="([^"]+)".*?src="http://pelisdanko.com/img/flags/(.*?).png"' \
             '.*?<span class="label label-default quality[^>]+>([^<]+)</span>.*?<td class="small">([^<]+)</td>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    filtrados = []
    for slug, flag, quality, date in matches:
        if flag != "ES" and flag != "ES_LAT":
            flag = "VOSE"
        flag = flag.replace('ES_LAT', 'LAT').replace('ES', 'CAST')
        scrapedurl = "%s/%s/%s?#%s" % (item.url, slug, type, type)
        scrapedtitle = "      [COLOR firebrick]Mostrar enlaces:   [/COLOR][COLOR goldenrod][" \
                       + flag + "/" + quality + "][/COLOR][COLOR khaki]  " + date + "[/COLOR]"
        if filtro_idioma == 3 or item.filtro:
            itemlist.append(item.clone(title=bbcode_kodi2html(scrapedtitle), action="findvideos",
                                       url=scrapedurl, id_enlaces=slug, calidad=quality))
        else:
            idioma = dict_idiomas[flag]
            if idioma == filtro_idioma:
                itemlist.append(item.clone(title=bbcode_kodi2html(scrapedtitle),
                                           action="findvideos", url=scrapedurl, id_enlaces=slug))
            else:
                if flag not in filtrados:
                    filtrados.append(flag)

    if filtro_idioma != 3:
        if len(filtrados) > 0:
            title = bbcode_kodi2html("[COLOR orangered]      Mostrar enlaces filtrados en %s[/COLOR]") % ", ".join(
                filtrados)
            itemlist.append(item.clone(title=title, action="enlaces", url=item.url, filtro=True))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.url[-2:] == "ss":
        prefix = "strms"
    else:
        prefix = "lnks"
    # Descarga la pagina
    data = scrapertools.downloadpage(item.url)

    # Parametros para redireccion donde muestra los enlaces
    data_slug = scrapertools.find_single_match(data, '<div id="ad" data-id="[^"]+" data-slug="([^"]+)"')
    data_id = scrapertools.find_single_match(data, '<tr class="rip hover" data-id="([^"]+)"')
    url = "http://pelisdanko.com/%s/%s/%s/%s" % (prefix, data_id, item.id_enlaces, data_slug)
    data = scrapertools.downloadpage(url, post="")

    from core import servertools
    video_item_list = servertools.find_video_items(data=data)
    for video_item in video_item_list:
        title = "[COLOR green]%s[/COLOR]    |    [COLOR darkorange][%s][/COLOR]" % (video_item.server, item.calidad)
        itemlist.append(item.clone(title=bbcode_kodi2html(title), url=video_item.url, action="play",
                                   server=video_item.server, text_color=""))

    # Opción "Añadir esta película a la videoteca de XBMC"
    if config.get_videolibrary_support() and len(itemlist) > 0 and item.category != "Cine":
        itemlist.append(Item(channel=item.channel, title="Añadir película a la videoteca", url=item.url,
                             infoLabels={'title': item.fulltitle}, action="add_pelicula_to_library",
                             fulltitle=item.fulltitle, text_color="green", id_enlaces=item.id_enlaces))

    return itemlist


def bbcode_kodi2html(text):
    if config.get_platform().startswith("plex") or config.get_platform().startswith("mediaserver"):
        import re
        text = re.sub(r'\[COLOR\s([^\]]+)\]',
                      r'<span style="color: \1">',
                      text)
        text = text.replace('[/COLOR]', '</span>') \
            .replace('[CR]', '<br>') \
            .replace('[B]', '<strong>') \
            .replace('[/B]', '</strong>') \
            .replace('"color: white"', '"color: auto"')

    return text
