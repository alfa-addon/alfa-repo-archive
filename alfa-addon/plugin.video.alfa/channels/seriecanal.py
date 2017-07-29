# -*- coding: utf-8 -*-

import re
import urllib
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools

__modo_grafico__ = config.get_setting('modo_grafico', "seriecanal")
__perfil__ = config.get_setting('perfil', "descargasmix")

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]
color1, color2, color3 = perfil[__perfil__]

URL_BASE = "http://www.seriecanal.com/"


def login():
    logger.info()
    data = scrapertools.downloadpage(URL_BASE)
    if "Cerrar Sesion" in data:
        return True, ""

    usuario = config.get_setting("user", "seriecanal")
    password = config.get_setting("password", "seriecanal")
    if usuario == "" or password == "":
        return False, 'Regístrate en www.seriecanal.com e introduce tus datos en "Configurar Canal"'
    else:
        post = urllib.urlencode({'username': usuario, 'password': password})
        data = scrapertools.downloadpage("http://www.seriecanal.com/index.php?page=member&do=login&tarea=acceder",
                                         post=post)
        if "Bienvenid@, se ha identificado correctamente en nuestro sistema" in data:
            return True, ""
        else:
            return False, "Error en el login. El usuario y/o la contraseña no son correctos"


def mainlist(item):
    logger.info()
    itemlist = []
    item.text_color = color1

    result, message = login()
    if result:
        itemlist.append(item.clone(action="series", title="Últimos episodios", url=URL_BASE))
        itemlist.append(item.clone(action="genero", title="Series por género"))
        itemlist.append(item.clone(action="alfabetico", title="Series por orden alfabético"))
        itemlist.append(item.clone(action="search", title="Buscar..."))
    else:
        itemlist.append(item.clone(action="", title=message, text_color="red"))

    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", text_color="gold", folder=False))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    item.url = "http://www.seriecanal.com/index.php?page=portada&do=category&method=post&category_id=0&order=" \
               "C_Create&view=thumb&pgs=1&p2=1"
    try:
        post = "keyserie=" + texto
        item.extra = post
        return series(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def genero(item):
    logger.info()
    itemlist = []
    data = scrapertools.downloadpage(URL_BASE)
    data = scrapertools.find_single_match(data, '<ul class="tag-cloud">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(data, '<a.*?href="([^"]+)">([^"]+)</a>')
    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.capitalize()
        url = urlparse.urljoin(URL_BASE, scrapedurl)
        itemlist.append(item.clone(action="series", title=scrapedtitle, url=url))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []
    data = scrapertools.downloadpage(URL_BASE)
    data = scrapertools.find_single_match(data, '<ul class="pagination pagination-sm" style="margin:5px 0;">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(data, '<a.*?href="([^"]+)">([^"]+)</a>')
    for scrapedurl, scrapedtitle in matches:
        url = urlparse.urljoin(URL_BASE, scrapedurl)
        itemlist.append(item.clone(action="series", title=scrapedtitle, url=url))
    return itemlist


def series(item):
    logger.info()
    itemlist = []
    item.infoLabels = {}
    item.text_color = color2

    if item.extra != "":
        data = scrapertools.downloadpage(item.url, post=item.extra)
    else:
        data = scrapertools.downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<div class="item-inner" style="margin: 0 20px 0px 0\;"><img src="([^"]+)".*?' \
             'href="([^"]+)" title="Click para Acceder a la Ficha(?:\|([^"]+)|)".*?' \
             '<strong>([^"]+)</strong></a>.*?<strong>([^"]+)</strong></p>.*?' \
             '<p class="text-warning".*?\;">(.*?)</p>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for scrapedthumbnail, scrapedurl, scrapedplot, scrapedtitle, scrapedtemp, scrapedepi in matches:
        title = scrapedtitle + " - " + scrapedtemp + " - " + scrapedepi
        url = urlparse.urljoin(URL_BASE, scrapedurl)
        temporada = scrapertools.find_single_match(scrapedtemp, "(\d+)")
        new_item = item.clone()
        new_item.contentType = "tvshow"
        if temporada != "":
            new_item.infoLabels['season'] = temporada
            new_item.contentType = "season"

        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(new_item.clone(action="findvideos", title=title, fulltitle=scrapedtitle, url=url,
                                       thumbnail=scrapedthumbnail, plot=scrapedplot, contentTitle=scrapedtitle,
                                       context=["buscar_trailer"], show=scrapedtitle))

    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass
    # Extra marca siguiente página
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" (?:onclick="return false;" |)title='
                                                     '"Página Siguiente"')
    if next_page != "/":
        url = urlparse.urljoin(URL_BASE, next_page)
        itemlist.append(item.clone(action="series", title=">> Siguiente", url=url, text_color=color3))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    item.text_color = color3

    data = scrapertools.downloadpage(item.url)
    data = scrapertools.decodeHtmlentities(data)

    # Busca en la seccion descarga/torrent
    data_download = scrapertools.find_single_match(data, '<th>Episodio - Enlaces de Descarga</th>(.*?)</table>')
    patron = '<p class="item_name".*?<a href="([^"]+)".*?>([^"]+)</a>'
    matches = scrapertools.find_multiple_matches(data_download, patron)
    for scrapedurl, scrapedepi in matches:
        new_item = item.clone()
        if "Episodio" not in scrapedepi:
            scrapedtitle = "[Torrent] Episodio " + scrapedepi
        else:
            scrapedtitle = "[Torrent] " + scrapedepi
        scrapedtitle = scrapertools.htmlclean(scrapedtitle)

        new_item.infoLabels['episode'] = scrapertools.find_single_match(scrapedtitle, "Episodio (\d+)")
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(new_item.clone(action="play", title=scrapedtitle, url=scrapedurl, server="torrent",
                                       contentType="episode"))

    # Busca en la seccion online
    data_online = scrapertools.find_single_match(data, "<th>Enlaces de Visionado Online</th>(.*?)</table>")
    patron = '<a href="([^"]+)\\n.*?src="([^"]+)".*?' \
             'title="Enlace de Visionado Online">([^"]+)</a>'
    matches = scrapertools.find_multiple_matches(data_online, patron)

    for scrapedurl, scrapedthumb, scrapedtitle in matches:
        # Deshecha enlaces de trailers
        scrapedtitle = scrapertools.htmlclean(scrapedtitle)
        if (scrapedthumb != "images/series/youtube.png") & (scrapedtitle != "Trailer"):
            new_item = item.clone()
            server = scrapertools.find_single_match(scrapedthumb, "images/series/(.*?).png")
            title = "[" + server.capitalize() + "]" + " " + scrapedtitle

            new_item.infoLabels['episode'] = scrapertools.find_single_match(scrapedtitle, "Episodio (\d+)")
            itemlist.append(new_item.clone(action="play", title=title, url=scrapedurl, contentType="episode"))

    # Comprueba si hay otras temporadas
    if not "No hay disponible ninguna Temporada adicional" in data:
        data_temp = scrapertools.find_single_match(data, '<div class="panel panel-success">(.*?)</table>')
        data_temp = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data_temp)
        patron = '<tr><td><p class="item_name"><a href="([^"]+)".*?' \
                 '<p class="text-success"><strong>([^"]+)</strong>'
        matches = scrapertools.find_multiple_matches(data_temp, patron)
        for scrapedurl, scrapedtitle in matches:
            new_item = item.clone()
            url = urlparse.urljoin(URL_BASE, scrapedurl)
            scrapedtitle = scrapedtitle.capitalize()
            temporada = scrapertools.find_single_match(scrapedtitle, "Temporada (\d+)")
            if temporada != "":
                new_item.infoLabels['season'] = temporada
                new_item.infoLabels['episode'] = ""
            itemlist.append(new_item.clone(action="findvideos", title=scrapedtitle, url=url, text_color="red",
                                           contentType="season"))

    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass

    new_item = item.clone()
    if config.is_xbmc():
        new_item.contextual = True
    itemlist.append(new_item.clone(channel="trailertools", title="Buscar Tráiler", action="buscartrailer", context="",
                                   text_color="magenta"))
    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.extra == "torrent":
        itemlist.append(item.clone())
    else:
        # Extrae url de enlace bit.ly
        if item.url.startswith("http://bit.ly/"):
            item.url = scrapertools.getLocationHeaderFromResponse(item.url)
        video_list = servertools.findvideos(item.url)
        if video_list:
            url = video_list[0][1]
            server = video_list[0][2]
        itemlist.append(item.clone(server=server, url=url))

    return itemlist
