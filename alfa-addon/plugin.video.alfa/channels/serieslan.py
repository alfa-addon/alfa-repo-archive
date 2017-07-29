# -*- coding: utf-8 -*-

import re

from channels import renumbertools
from channelselector import get_thumb
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

host = "https://serieslan.com"


def mainlist(item):
    logger.info()
    thumb_series = get_thumb("thumb_channels_tvshow.png")

    itemlist = list()

    itemlist.append(
        Item(channel=item.channel, action="lista", title="Series", url=host, thumbnail=thumb_series, page=0))
    itemlist = renumbertools.show_option(item.channel, itemlist)
    return itemlist


def lista(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '<a href="([^"]+)" '
    patron += 'class="link">.+?<img src="([^"]+)".*?'
    patron += 'title="([^"]+)">'

    matches = scrapertools.find_multiple_matches(data, patron)

    # Paginacion
    num_items_x_pagina = 30
    min = item.page * num_items_x_pagina
    max = min + num_items_x_pagina - 1

    for link, img, name in matches[min:max]:
        title = name
        url = host + link
        scrapedthumbnail = host + img
        itemlist.append(item.clone(title=title, url=url, action="episodios", thumbnail=scrapedthumbnail, show=title,
                                   context=renumbertools.context(item)))

    itemlist.append(
        Item(channel=item.channel, title="Página Siguiente >>", url=item.url, action="lista", page=item.page + 1))

    tmdb.set_infoLabels(itemlist)
    return itemlist


def episodios(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    # obtener el numero total de episodios
    total_episode = 0

    patron_caps = '<li><span>Capitulo ([^"]+)\:<\/span><[^"]+"(.+?)">([^"]+)<[^"]+<\/li>'
    matches = scrapertools.find_multiple_matches(data, patron_caps)
    # data_info = scrapertools.find_single_match(data, '<div class="info">.+?<\/div><\/div>')
    patron_info = '<img src="([^"]+)">.+?<\/span>([^"]+)<\/p><p><span>I.+?Reseña: <\/span>(.+?)<\/p><\/div>'
    scrapedthumbnail, show, scrapedplot = scrapertools.find_single_match(data, patron_info)
    scrapedthumbnail = host + scrapedthumbnail

    for cap, link, name in matches:

        title = ""
        pat = "as/sd"
        # varios episodios en un enlace
        if len(name.split(pat)) > 1:
            i = 0
            for pos in name.split(pat):
                i = i + 1
                total_episode += 1
                season, episode = renumbertools.numbered_for_tratk(item.channel, item.show, 1, total_episode)
                if len(name.split(pat)) == i:
                    title += "{0}x{1:02d} ".format(season, episode)
                else:
                    title += "{0}x{1:02d}_".format(season, episode)
        else:
            total_episode += 1
            season, episode = renumbertools.numbered_for_tratk(item.channel, item.show, 1, total_episode)

            title += "{0}x{1:02d} ".format(season, episode)

        url = host + "/" + link
        if "disponible" in link:
            title += "No Disponible aún"
        else:
            title += name
            itemlist.append(
                Item(channel=item.channel, action="findvideos", title=title, url=url, show=show, plot=scrapedplot,
                     thumbnail=scrapedthumbnail))

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=show))

    return itemlist


# def getUrlVideo(item):
def findvideos(item):
    ## Kodi 17+
    ## Openload as default server

    import base64

    itemlist = []

    ## Urls
    urlServer = "https://openload.co/embed/%s/"
    urlApiGetKey = "https://serieslan.com/idv.php?i=%s"

    ## JS
    def txc(key, str):
        s = range(256)
        j = 0
        res = ''
        for i in range(256):
            j = (j + s[i] + ord(key[i % len(key)])) % 256
            x = s[i]
            s[i] = s[j]
            s[j] = x
        i = 0
        j = 0
        for y in range(len(str)):
            i = (i + 1) % 256
            j = (j + s[i]) % 256
            x = s[i]
            s[i] = s[j]
            s[j] = x
            res += chr(ord(str[y]) ^ s[(s[i] + s[j]) % 256])
        return res

    data = httptools.downloadpage(item.url).data
    pattern = '<div id="video" idv="([^"]*)" ide="([^"]*)" ids="[^"]*" class="video">'
    idv, ide = scrapertools.find_single_match(data, pattern)
    thumbnail = scrapertools.find_single_match(data,
                                               '<div id="tab-1" class="tab-content current">.+?<img src="([^"]*)">')
    show = scrapertools.find_single_match(data, '<span>Episodio: <\/span>([^"]*)<\/p><p><span>Idioma')
    thumbnail = host + thumbnail
    data = httptools.downloadpage(urlApiGetKey % idv, headers={'Referer': item.url}).data
    video_url = urlServer % (txc(ide, base64.decodestring(data)))
    server = "openload"
    if " SUB" in item.title:
        lang = "VOS"
    elif " Sub" in item:
        lang = "VOS"
    else:
        lang = "Latino"
    title = "Enlace encontrado en " + server + " [" + lang + "]"
    itemlist.append(Item(channel=item.channel, action="play", title=title, show=show, url=video_url, plot=item.plot,
                         thumbnail=thumbnail, server=server, folder=False))

    return itemlist


def play(item):
    logger.info()
    itemlist = []
    # Buscamos video por servidor ...
    devuelve = servertools.findvideosbyserver(item.url, item.server)
    if not devuelve:
        # ...sino lo encontramos buscamos en todos los servidores disponibles
        devuelve = servertools.findvideos(item.url, skip=True)
    if devuelve:
        # logger.debug(devuelve)
        itemlist.append(Item(channel=item.channel, title=item.contentTitle, action="play", server=devuelve[0][2],
                             url=devuelve[0][1], thumbnail=item.thumbnail, folder=False))
    return itemlist
