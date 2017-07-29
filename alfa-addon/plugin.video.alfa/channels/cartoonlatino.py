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

host = "http://www.cartoon-latino.com/"


def mainlist(item):
    logger.info()

    thumb_series = get_thumb("thumb_channels_tvshow.png")
    thumb_series_az = get_thumb("thumb_channels_tvshow_az.png")

    itemlist = list()

    itemlist.append(Item(channel=item.channel, action="lista", title="Series", url=host,
                         thumbnail=thumb_series))
    itemlist = renumbertools.show_option(item.channel, itemlist)

    return itemlist


"""
def search(item, texto):
    logger.info()
    texto = texto.replace(" ","+")
    item.url = item.url+texto
    if texto!='':
       return lista(item)
"""


def lista_gen(item):
    logger.info()

    itemlist = []

    data1 = httptools.downloadpage(item.url).data
    data1 = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data1)
    patron_sec = '<section class="content">.+?<\/section>'
    data = scrapertools.find_single_match(data1, patron_sec)
    patron = '<article id=.+? class=.+?><div.+?>'
    patron += '<a href="([^"]+)" title="([^"]+)'  # scrapedurl, # scrapedtitle
    patron += ' Capítulos Completos ([^"]+)">'  # scrapedlang
    patron += '<img.+? data-src=.+? data-lazy-src="([^"]+)"'  # scrapedthumbnail
    matches = scrapertools.find_multiple_matches(data, patron)
    i = 0
    for scrapedurl, scrapedtitle, scrapedlang, scrapedthumbnail in matches:
        i = i + 1
        if 'HD' in scrapedlang:
            scrapedlang = scrapedlang.replace('HD', '')
        title = scrapedtitle + " [ " + scrapedlang + "]"
        itemlist.append(
            Item(channel=item.channel, title=title, url=scrapedurl, thumbnail=scrapedthumbnail, action="episodios",
                 show=scrapedtitle, context=renumbertools.context(item)))
    tmdb.set_infoLabels(itemlist)
    # Paginacion
    patron_pag = '<a class="nextpostslink" rel="next" href="([^"]+)">'
    next_page_url = scrapertools.find_single_match(data, patron_pag)

    if next_page_url != "" and i != 1:
        item.url = next_page_url
        itemlist.append(Item(channel=item.channel, action="lista_gen", title=">> Página siguiente", url=next_page_url,
                             thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png'))

    return itemlist


def lista(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    data_lista = scrapertools.find_single_match(data, '<div class="su-list su-list-style-"><ul>(.+?)<\/ul><\/div>')
    patron = "<a href='(.+?)'>(.+?)<\/a>"
    matches = scrapertools.find_multiple_matches(data_lista, patron)
    for link, name in matches:
        title = name + " [Latino]"
        url = link
        itemlist.append(
            item.clone(title=title, url=url, plot=title, action="episodios", show=title,
                       context=renumbertools.context(item)))
    tmdb.set_infoLabels(itemlist)
    return itemlist


def episodios(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    data_lista = scrapertools.find_single_match(data,
                                                '<div class="su-list su-list-style-"><ulclass="lista-capitulos">.+?<\/div><\/p>')
    if '&#215;' in data_lista:
        data_lista = data_lista.replace('&#215;', 'x')

    show = item.title
    if "[Latino]" in show:
        show = show.replace("[Latino]", "")
    if "Ranma" in show:
        patron_caps = '<\/i> <strong>.+?Capitulo ([^"]+)\: <a .+? href="([^"]+)">([^"]+)<\/a>'
    else:
        patron_caps = '<\/i> <strong>Capitulo ([^"]+)x.+?\: <a .+? href="([^"]+)">([^"]+)<\/a>'
    matches = scrapertools.find_multiple_matches(data_lista, patron_caps)
    scrapedplot = scrapertools.find_single_match(data, '<strong>Sinopsis<\/strong><strong>([^"]+)<\/strong><\/pre>')
    number = 0
    ncap = 0
    A = 1
    for temp, link, name in matches:
        if A != temp:
            number = 0
        if "Ranma" in show:
            number = int(temp)
            temp = str(1)
        else:
            number = number + 1
        if number < 10:
            capi = "0" + str(number)
        else:
            capi = str(number)
        if "Ranma" in show:
            season = 1
            episode = number
            season, episode = renumbertools.numbered_for_tratk(
                item.channel, item.show, season, episode)
            date = name
            if episode < 10:
                capi = "0" + str(episode)
            else:
                capi = episode
            title = str(season) + "x" + str(capi) + " - " + name  # "{0}x{1} - ({2})".format(season, episode, date)
        else:
            title = str(temp) + "x" + capi + " - " + name
        url = link
        A = temp
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, show=show))

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="Añadir " + show + " a la videoteca", url=item.url,

                             action="add_serie_to_library", extra="episodios", show=show))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    data_function = scrapertools.find_single_match(data, '<!\[CDATA\[function (.+?)\]\]')
    data_id = scrapertools.find_single_match(data,
                                             "<script>\(adsbygoogle = window\.adsbygoogle \|\| \[\]\)\.push\({}\);<\/script><\/div><br \/>(.+?)<\/ins>")
    itemla = scrapertools.find_multiple_matches(data_function, "src='(.+?)'")
    serverid = scrapertools.find_multiple_matches(data_id, '<script>([^"]+)\("([^"]+)"\)')
    for server, id in serverid:
        for link in itemla:
            if server in link:
                url = link.replace('" + ID' + server + ' + "', str(id))
            if "drive" in server:
                server1 = 'googlevideo'
            else:
                server1 = server
        itemlist.append(item.clone(url=url, action="play", server=server1,
                                   title="Enlace encontrado en %s " % (server1.capitalize())))
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
