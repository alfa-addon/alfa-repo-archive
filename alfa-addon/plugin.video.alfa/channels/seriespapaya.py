# -*- coding: utf-8 -*-

import re
import string
import urllib
import urlparse

from channels import filtertools
from channelselector import get_thumb
from core import config
from core import httptools
from core import jsontools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

HOST = "http://www.seriespapaya.com"

IDIOMAS = {'es': 'Español', 'lat': 'Latino', 'in': 'Inglés', 'ca': 'Catalán', 'sub': 'VOS'}
list_idiomas = IDIOMAS.values()
CALIDADES = ['360p', '480p', '720p HD', '1080p HD']


def mainlist(item):
    logger.info()

    thumb_series = get_thumb("thumb_channels_tvshow.png")
    thumb_series_az = get_thumb("thumb_channels_tvshow_az.png")
    thumb_buscar = get_thumb("thumb_search.png")

    itemlist = []
    itemlist.append(
        Item(action="listado_alfabetico", title="Listado Alfabetico", channel=item.channel, thumbnail=thumb_series_az))
    itemlist.append(
        Item(action="novedades", title="Capítulos de estreno", channel=item.channel, thumbnail=thumb_series))
    itemlist.append(Item(action="search", title="Buscar", channel=item.channel, thumbnail=thumb_buscar))

    itemlist = filtertools.show_option(itemlist, item.channel, list_idiomas, CALIDADES)

    return itemlist


def listado_alfabetico(item):
    logger.info()

    itemlist = [item.clone(action="series_por_letra", title="0-9")]
    for letra in string.ascii_uppercase:
        itemlist.append(item.clone(action="series_por_letra", title=letra))

    return itemlist


def series_por_letra(item):
    logger.info("letra: {0}".format(item.title))
    item.letter = item.title.lower()
    item.extra = 0
    return series_por_letra_y_grupo(item)


def series_por_letra_y_grupo(item):
    logger.info("letra: {0} - grupo: {1}".format(item.letter, item.extra))
    itemlist = []
    url = urlparse.urljoin(HOST, "autoload_process.php")

    postRequest = {
        "group_no": item.extra,
        "letra": item.letter.lower()
    }
    data = httptools.downloadpage(url, post=urllib.urlencode(postRequest)).data

    series = re.findall(
        'list_imagen.+?src="(?P<img>[^"]+).+?<div class="list_titulo"><a[^>]+href="(?P<url>[^"]+)[^>]+>(.*?)</a>', data,
        re.MULTILINE | re.DOTALL)

    for img, url, name in series:
        itemlist.append(item.clone(
            action="episodios",
            title=name,
            show=name,
            url=urlparse.urljoin(HOST, url),
            thumbnail=urlparse.urljoin(HOST, img),
            context=filtertools.context(item, list_idiomas, CALIDADES)
        ))

    if len(series) == 8:
        itemlist.append(item.clone(title="Siguiente >>", action="series_por_letra_y_grupo", extra=item.extra + 1))

    if item.extra > 0:
        itemlist.append(item.clone(title="<< Anterior", action="series_por_letra_y_grupo", extra=item.extra - 1))

    return itemlist


def novedades(item):
    logger.info()
    data = httptools.downloadpage(HOST).data
    shows = re.findall('sidebarestdiv[^<]+<a[^<]+title="([^"]*)[^<]+href="([^"]*)[^<]+<img[^<]+src="([^"]+)', data,
                       re.MULTILINE | re.DOTALL)

    itemlist = []

    for title, url, img in shows:
        itemlist.append(item.clone(action="findvideos", title=title, url=urlparse.urljoin(HOST, url), thumbnail=img))

    return itemlist


def newest(categoria):
    logger.info("categoria: {0}".format(categoria))

    if categoria != 'series':
        return []

    try:
        return novedades(Item())

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))

    return []


def episodios(item):
    logger.info("url: {0}".format(item.url))

    data = httptools.downloadpage(item.url).data

    episodes = re.findall('visco.*?href="(?P<url>[^"]+).+?nbsp; (?P<title>.*?)</a>.+?ucapaudio.?>(?P<langs>.*?)</div>',
                          data, re.MULTILINE | re.DOTALL)

    itemlist = []
    for url, title, langs in episodes:
        logger.debug("langs %s" % langs)
        languages = " ".join(
            ["[{0}]".format(IDIOMAS.get(lang, lang)) for lang in re.findall('images/s-([^\.]+)', langs)])
        filter_lang = languages.replace("[", "").replace("]", "").split(" ")
        itemlist.append(item.clone(action="findvideos",
                                   title="{0} {1} {2}".format(item.title, title, languages),
                                   url=urlparse.urljoin(HOST, url),
                                   language=filter_lang
                                   ))

    itemlist = filtertools.get_links(itemlist, item.channel, list_idiomas, CALIDADES)

    # Opción "Añadir esta serie a la videoteca de XBMC"
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            item.clone(title="Añadir esta serie a la videoteca", action="add_serie_to_library", extra="episodios"))

    return itemlist


def search(item, texto):
    logger.info("texto: {0}".format(texto))
    data = httptools.downloadpage(urlparse.urljoin(HOST, "/buscar.php?term={0}".format(texto))).data
    jsonResult = jsontools.load(data)
    tvShows = jsonResult["myData"]

    return [item.clone(action="episodios",
                       title=show["titulo"],
                       show=show["titulo"],
                       url=urlparse.urljoin(HOST, show["urla"]),
                       thumbnail=urlparse.urljoin(HOST, show["img"]),
                       context=filtertools.context(item, list_idiomas, CALIDADES)
                       ) for show in tvShows]


def findvideos(item):
    logger.info("url: {0}".format(item.url))

    data = httptools.downloadpage(item.url).data

    expr = 'mtos' + '.+?' + \
           '<div.+?images/(?P<lang>[^\.]+)' + '.+?' + \
           '<div[^>]+>\s+(?P<date>[^\s<]+)' + '.+?' + \
           '<div.+?img.+?>\s*(?P<server>.+?)</div>' + '.+?' + \
           '<div.+?href="(?P<url>[^"]+).+?images/(?P<type>[^\.]+)' + '.+?' + \
           '<div[^>]+>\s*(?P<quality>.*?)</div>' + '.+?' + \
           '<div.+?<a.+?>(?P<uploader>.*?)</a>'

    links = re.findall(expr, data, re.MULTILINE | re.DOTALL)

    itemlist = [item.clone(
        action="play",
        title="{linkType} en {server} [{lang}] [{quality}] ({uploader}: {date})".format(
            linkType="Ver" if linkType != "descargar" else "Descargar",
            lang=IDIOMAS.get(lang, lang),
            date=date,
            server=server.rstrip(),
            quality=quality,
            uploader=uploader),
        url=urlparse.urljoin(HOST, url),
        language=IDIOMAS.get(lang, lang),
        quality=quality,
    ) for lang, date, server, url, linkType, quality, uploader in links]

    itemlist = filtertools.get_links(itemlist, item.channel, list_idiomas, CALIDADES)

    return itemlist


def play(item):
    logger.info("play: {0}".format(item.url))
    data = httptools.downloadpage(item.url).data
    videoURL = scrapertools.find_single_match(data, "location.href='([^']+)")
    logger.debug("Video URL = {0}".format(videoURL))
    itemlist = servertools.find_video_items(data=videoURL)
    return itemlist
