# -*- coding: utf-8 -*-

import re
import urllib

from core import config
from core import httptools
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item

host = 'http://pelismag.net'
api = host + '/api'
api_serie = host + "/seapi"
api_temp = host + "/sapi"
__modo_grafico__ = config.get_setting("modo_grafico", "pelismagnet")


def mainlist(item):
    logger.info()

    itemlist = list()
    itemlist.append(Item(channel=item.channel, action="pelis", title="[B]Peliculas[/B]",
                         url=api + "?sort_by=''&page=0"))
    itemlist.append(Item(channel=item.channel, action="pelis", title="     Estrenos",
                         url=api + "?sort_by=date_added&page=0"))
    itemlist.append(Item(channel=item.channel, action="pelis", title="     + Populares", url=api + "?page=0"))
    itemlist.append(Item(channel=item.channel, action="pelis", title="     + Valoradas",
                         url=api + "?sort_by=rating&page=0"))
    itemlist.append(Item(channel=item.channel, action="menu_ord", title="     Ordenado por...",
                         url=api))
    itemlist.append(
        Item(channel=item.channel, action="search", title="     Buscar...", url=api + "?keywords=%s&page=0"))
    itemlist.append(Item(channel=item.channel, action="series", title="[B]Series[/B]",
                         url=api_serie + "?sort_by=''&page=0"))
    itemlist.append(Item(channel=item.channel, action="series", title="     Recientes",
                         url=api_serie + "?sort_by=date_added&page=0"))
    itemlist.append(Item(channel=item.channel, action="series", title="     + Populares", url=api_serie + "?page=0"))
    itemlist.append(Item(channel=item.channel, action="series", title="     + Valoradas",
                         url=api_serie + "?sort_by=rating&page=0"))
    itemlist.append(Item(channel=item.channel, action="menu_ord", title="     Ordenado por...",
                         url=api_serie))
    itemlist.append(Item(channel=item.channel, action="search", title="     Buscar...",
                         url=api_serie + "?keywords=%s&page=0"))
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal"))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def menu_ord(item):
    logger.info()

    itemlist = list()
    itemlist.append(Item(channel=item.channel, action="menu_alf", title="Alfabético",
                         url=item.url))
    itemlist.append(Item(channel=item.channel, action="menu_genero", title="Género",
                         url=item.url))

    return itemlist


def menu_alf(item):
    logger.info()

    itemlist = []

    for letra in ['[0-9]', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                  'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        itemlist.append(Item(channel=item.channel, action="series", title=letra,
                             url=item.url + "?keywords=^" + letra + "&page=0"))

    return itemlist


def menu_genero(item):
    logger.info()

    itemlist = []

    response = httptools.downloadpage("https://kproxy.com/")
    url = "https://kproxy.com/doproxy.jsp"
    post = "page=%s&x=34&y=14" % urllib.quote(host + "/principal")
    response = httptools.downloadpage(url, post, follow_redirects=False).data
    url = scrapertools.find_single_match(response, '<meta http-equiv="refresh".*?url=([^"]+)"')
    data = httptools.downloadpage(url).data

    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    data = scrapertools.find_single_match(data, '<ul class="dropdown-menu.*?>(.*?)</ul>')
    patron = '<li><a href="genero/([^"]+)">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for genero, nombre in matches:
        itemlist.append(Item(channel=item.channel, action="series", title=nombre,
                             url=item.url + "?genre=" + genero + "&page=0"))

    return itemlist


def series(item):
    logger.info()
    itemlist = []

    response = httptools.downloadpage("https://kproxy.com/")
    url = "https://kproxy.com/doproxy.jsp"
    post = "page=%s&x=34&y=14" % urllib.quote(item.url)
    response = httptools.downloadpage(url, post, follow_redirects=False).data
    url = scrapertools.find_single_match(response, '<meta http-equiv="refresh".*?url=([^"]+)"')
    data = httptools.downloadpage(url).data

    lista = jsontools.load(data)
    if item.extra == "next":
        lista_ = lista[25:]
    else:
        lista_ = lista[:25]

    for i in lista_:

        punt = i.get("puntuacio", "")
        valoracion = ""
        if punt and not 0:
            valoracion = "  (Val: {punt})".format(punt=punt)

        title = "{nombre}{val}".format(nombre=i.get("nom", ""), val=valoracion)
        url = "{url}?id={id}".format(url=api_temp, id=i.get("id", ""))

        thumbnail = ""
        fanart = ""
        if i.get("posterurl", ""):
            thumbnail = "http://image.tmdb.org/t/p/w342{file}".format(file=i.get("posterurl", ""))
        if i.get("backurl", ""):
            fanart = "http://image.tmdb.org/t/p/w1280{file}".format(file=i.get("backurl", ""))

        plot = i.get("info", "")
        if plot is None:
            plot = ""

        infoLabels = {'plot': plot, 'year': i.get("year"), 'tmdb_id': i.get("id"), 'mediatype': 'tvshow'}

        itemlist.append(Item(channel=item.channel, action="episodios", title=title, url=url, server="torrent",
                             thumbnail=thumbnail, fanart=fanart, infoLabels=infoLabels, contentTitle=i.get("nom"),
                             show=i.get("nom")))

    from core import tmdb
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    if len(lista_) == 25 and item.extra == "next":
        url = re.sub(r'page=(\d+)', r'page=' + str(int(re.search('\d+', item.url).group()) + 1), item.url)
        itemlist.append(Item(channel=item.channel, action="series", title=">> Página siguiente", url=url))
    elif len(lista_) == 25:
        itemlist.append(
            Item(channel=item.channel, action="series", title=">> Página siguiente", url=item.url, extra="next"))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    response = httptools.downloadpage("https://kproxy.com/")
    url = "https://kproxy.com/doproxy.jsp"
    post = "page=%s&x=34&y=14" % urllib.quote(item.url)
    response = httptools.downloadpage(url, post, follow_redirects=False).data
    url = scrapertools.find_single_match(response, '<meta http-equiv="refresh".*?url=([^"]+)"')
    data = httptools.downloadpage(url).data

    data = jsontools.load(data)
    for i in data.get("temporadas", []):

        titulo = "{temporada} ({total} Episodios)".format(temporada=i.get("nomtemporada", ""),
                                                          total=len(i.get("capituls", "0")))
        itemlist.append(Item(channel=item.channel, action="episodios", title=titulo, url=item.url,
                             server="torrent", fanart=item.fanart, thumbnail=item.thumbnail, plot=data.get("info", ""),
                             folder=False))

        for j in i.get("capituls", []):

            numero = j.get("infocapitul", "")
            if not numero:
                numero = "{temp}x{cap}".format(temp=i.get("numerotemporada", ""), cap=j.get("numerocapitul", ""))

            titulo = j.get("nomcapitul", "")
            if not titulo:
                titulo = "Capítulo {num}".format(num=j.get("numerocapitul", ""))

            calidad = ""
            if j.get("links", {}).get("calitat", ""):
                calidad = " [{calidad}]".format(calidad=j.get("links", {}).get("calitat", ""))

            title = "     {numero} {titulo}{calidad}".format(numero=numero, titulo=titulo, calidad=calidad)

            if j.get("links", {}).get("magnet", ""):
                url = j.get("links", {}).get("magnet", "")
            else:
                return [Item(channel=item.channel, title='No hay enlace magnet disponible para este capitulo')]

            plot = i.get("overviewcapitul", "")
            if plot is None:
                plot = ""

            infoLabels = item.infoLabels
            if plot:
                infoLabels["plot"] = plot
            infoLabels["season"] = i.get("numerotemporada")
            infoLabels["episode"] = j.get("numerocapitul")
            itemlist.append(
                Item(channel=item.channel, action="play", title=title, url=url, server="torrent", infoLabels=infoLabels,
                     thumbnail=item.thumbnail, fanart=item.fanart, show=item.show, contentTitle=item.contentTitle,
                     contentSeason=i.get("numerotemporada"), contentEpisodeNumber=j.get("numerocapitul")))

    return itemlist


def pelis(item):
    logger.info()

    itemlist = []

    response = httptools.downloadpage("https://kproxy.com/")
    url = "https://kproxy.com/doproxy.jsp"
    post = "page=%s&x=34&y=14" % urllib.quote(item.url)
    response = httptools.downloadpage(url, post, follow_redirects=False).data
    url = scrapertools.find_single_match(response, '<meta http-equiv="refresh".*?url=([^"]+)"')
    data = httptools.downloadpage(url).data

    lista = jsontools.load(data)
    if item.extra == "next":
        lista_ = lista[25:]
    else:
        lista_ = lista[:25]

    for i in lista_:
        punt = i.get("puntuacio", "")
        valoracion = ""

        if punt and not 0:
            valoracion = "  (Val: {punt})".format(punt=punt)

        if i.get("magnets", {}).get("M1080", {}).get("magnet", ""):
            url = i.get("magnets", {}).get("M1080", {}).get("magnet", "")
            calidad = "[{calidad}]".format(calidad=i.get("magnets", {}).get("M1080", {}).get("quality", ""))
        else:
            url = i.get("magnets", {}).get("M720", {}).get("magnet", "")
            calidad = "[{calidad}]".format(calidad=i.get("magnets", {}).get("M720", {}).get("quality", ""))

        if not url:
            continue

        title = "{nombre} {calidad}{val}".format(nombre=i.get("nom", ""), val=valoracion, calidad=calidad)

        thumbnail = ""
        fanart = ""
        if i.get("posterurl", ""):
            thumbnail = "http://image.tmdb.org/t/p/w342{file}".format(file=i.get("posterurl", ""))
        if i.get("backurl", ""):
            fanart = "http://image.tmdb.org/t/p/w1280{file}".format(file=i.get("backurl", ""))

        plot = i.get("info", "")
        if plot is None:
            plot = ""
        infoLabels = {'plot': plot, 'year': i.get("year"), 'tmdb_id': i.get("id")}

        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, server="torrent",
                             thumbnail=thumbnail, fanart=fanart, infoLabels=infoLabels, contentTitle=i.get("nom")))

    from core import tmdb
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    if len(lista_) == 25 and item.extra == "next":
        url = re.sub(r'page=(\d+)', r'page=' + str(int(re.search('\d+', item.url).group()) + 1), item.url)
        itemlist.append(Item(channel=item.channel, action="pelis", title=">> Página siguiente", url=url))
    elif len(lista_) == 25:
        itemlist.append(
            Item(channel=item.channel, action="pelis", title=">> Página siguiente", url=item.url, extra="next"))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = item.url % texto.replace(' ', '%20')
        if "/seapi" in item.url:
            return series(item)
        else:
            return pelis(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
