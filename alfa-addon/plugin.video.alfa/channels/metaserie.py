# -*- coding: utf-8 -*-

import re
import urlparse

from channels import autoplay
from channels import filtertools
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

IDIOMAS = {'la': 'Latino', 'es': 'Español', 'sub': 'VOS'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = [
    'openload',
    'gamovideo',
    'powvideo',
    'streamplay',
    'streaminto',
    'streame',
    'flashx'
]


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(item.clone(title="Series",
                               action="todas",
                               url="http://metaserie.com/series-agregadas",
                               thumbnail='https://s27.postimg.org/iahczwgrn/series.png',
                               fanart='https://s27.postimg.org/iahczwgrn/series.png'
                               ))

    # itemlist.append(item.clone(title="Anime",
    #                            action="todas",
    #                            url="http://metaserie.com/animes-agregados",
    #                            thumbnail='https://s2.postimg.org/s38borokp/anime.png',
    #                            fanart='https://s2.postimg.org/s38borokp/anime.png'
    #                            ))

    itemlist.append(item.clone(title="Buscar",
                               action="search",
                               url="http://www.metaserie.com/?s=",
                               thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                               fanart='https://s30.postimg.org/pei7txpa9/buscar.png'
                               ))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def todas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    logger.debug(data)

    patron = '<div class="poster">[^<]'
    patron += '<a href="([^"]+)" title="([^"]+)en(.*?)">[^<]'
    patron += '<div class="poster_efecto"><span>([^<]+)<.*?div>[^<]'
    patron += '<img.*?src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, lang, scrapedplot, scrapedthumbnail in matches:
        if 'latino' in lang:
            idioma = 'Latino'
        elif 'español' in lang:
            idioma = 'Español'
        url = urlparse.urljoin(item.url, scrapedurl)
        title = scrapertools.decodeHtmlentities(scrapedtitle) + ' (%s)' % idioma
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        fanart = 'https://s32.postimg.org/7g50yo39h/metaserie.png'
        itemlist.append(
            Item(channel=item.channel,
                 action="temporadas",
                 title=title,
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 fanart=fanart,
                 contentSerieName=title,
                 context=autoplay.context
                 ))

    # Paginacion

    next_page_url = scrapertools.find_single_match(data,
                                                   '<li><a class="next page-numbers local-link" href="(['
                                                   '^"]+)">&raquo;.*?li>')
    if next_page_url != "":
        itemlist.append(Item(channel=item.channel,
                             action="todas",
                             title=">> Página siguiente",
                             url=next_page_url,
                             thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'
                             ))
    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []
    templist = []

    data = httptools.downloadpage(item.url).data
    patron = '<li class=".*?="([^"]+)".*?>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url = scrapedurl
        contentSeasonNumber = re.findall(r'.*?temporada-([^-]+)-', url)
        title = scrapedtitle
        title = title.replace("&", "x");
        thumbnail = item.thumbnail
        plot = item.plot
        fanart = scrapertools.find_single_match(data, '<img src="([^"]+)"/>.*?</a>')
        itemlist.append(
            Item(channel=item.channel,
                 action='episodiosxtemp',
                 title=title,
                 fulltitle=item.contentSerieName,
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 fanart=fanart,
                 contentSerieName=item.contentSerieName,
                 contentSeasonNumber=contentSeasonNumber,
                 context=item.context
                 ))

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel,
                 title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                 url=item.url,
                 action="add_serie_to_library",
                 extra='episodios',
                 contentSerieName=item.contentSerieName
                 ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = temporadas(item)
    for tempitem in templist:
        itemlist += episodiosxtemp(tempitem)

    return itemlist


def more_episodes(item, itemlist, url):
    logger.info()
    templist = []
    item.url = url
    templist = episodiosxtemp(item)
    itemlist += templist
    return itemlist


def episodiosxtemp(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    logger.debug(data)
    patron = '<td><h3 class=".*?href="([^"]+)".*?">([^<]+).*?td>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url = scrapedurl
        contentEpisodeNumber = re.findall(r'.*?x([^\/]+)\/', url)
        title = scrapedtitle
        title = title.replace("&#215;", "x")
        title = title.replace("×", "x")
        thumbnail = item.thumbnail
        plot = item.plot
        fanart = item.fanart
        itemlist.append(Item(channel=item.channel,
                             action="findvideos",
                             title=title,
                             fulltitle=item.fulltitle,
                             url=url,
                             thumbnail=item.thumbnail,
                             plot=plot,
                             contentSerieName=item.contentSerieName,
                             contentSeasonNumber=item.contentSeasonNumber,
                             contentEpisodeNumber=contentEpisodeNumber,
                             context=item.context
                             ))
    more_pages = scrapertools.find_single_match(data,
                                                '<li><a class="next page-numbers local-link" href="(.*?)">&raquo;')
    logger.debug('more_pages: %s' % more_pages)
    if more_pages:
        itemlist = more_episodes(item, itemlist, more_pages)
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    itemlist = []
    if texto != '':
        try:
            data = httptools.downloadpage(item.url).data
            patron = '<a href="([^\"]+)" rel="bookmark" class="local-link">([^<]+)<.*?'
            matches = re.compile(patron, re.DOTALL).findall(data)
            scrapertools.printMatches(matches)
            for scrapedurl, scrapedtitle in matches:
                url = scrapedurl
                title = scrapertools.decodeHtmlentities(scrapedtitle)
                thumbnail = ''
                plot = ''
                itemlist.append(Item(channel=item.channel,
                                     action="temporadas",
                                     title=title,
                                     fulltitle=title,
                                     url=url,
                                     thumbnail=thumbnail,
                                     plot=plot,
                                     folder=True,
                                     contentSerieName=title
                                     ))

            return itemlist
        except:
            import sys
            for line in sys.exc_info():
                logger.error("%s" % line)
        return []


def findvideos(item):
    logger.info()
    itemlist = []
    audio = {'la': '[COLOR limegreen]LATINO[/COLOR]', 'es': '[COLOR yellow]ESPAÑOL[/COLOR]',
             'sub': '[COLOR red]ORIGINAL SUBTITULADO[/COLOR]'}
    data = httptools.downloadpage(item.url).data
    patron = '<td><img src="http:\/\/metaserie\.com\/wp-content\/themes\/mstheme\/gt\/assets\/img\/([^\.]+).png" ' \
             'width="20".*?<\/td>.*?<td><img src="http:\/\/www\.google\.com\/s2\/favicons\?domain=([^"]+)" \/>&nbsp;(' \
             '[^<]+)<\/td>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    anterior = scrapertools.find_single_match(data,
                                              '<th scope="col"><a href="([^"]+)" rel="prev" '
                                              'class="local-link">Anterior</a></th>')
    siguiente = scrapertools.find_single_match(data,
                                               '<th scope="col"><a href="([^"]+)" rel="next" '
                                               'class="local-link">Siguiente</a></th>')

    for scrapedid, scrapedurl, scrapedserv in matches:
        url = scrapedurl
        server = servertools.get_server_from_url(url).lower()
        title = item.title + ' audio ' + audio[scrapedid] + ' en ' + server
        extra = item.thumbnail
        thumbnail = servertools.guess_server_thumbnail(server)

        itemlist.append(Item(channel=item.channel,
                             action="play",
                             title=title,
                             fulltitle=item.contentSerieName,
                             url=url,
                             thumbnail=thumbnail,
                             extra=extra,
                             language=IDIOMAS[scrapedid],
                             server=server,
                             ))
    if item.extra1 != 'capitulos':
        if anterior != '':
            itemlist.append(Item(channel=item.channel,
                                 action="findvideos",
                                 title='Capitulo Anterior',
                                 url=anterior,
                                 thumbnail='https://s31.postimg.org/k5kpwyrgb/anterior.png'
                                 ))
        if siguiente != '':
            itemlist.append(Item(channel=item.channel,
                                 action="findvideos",
                                 title='Capitulo Siguiente',
                                 url=siguiente,
                                 thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'
                                 ))

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def play(item):
    logger.info()
    itemlist = []
    from core import servertools
    itemlist.extend(servertools.find_video_items(data=item.url))
    for videoitem in itemlist:
        video = item.channel
        videoitem.title = item.fulltitle
        videoitem.folder = False
        videoitem.thumbnail = item.extra
        videoitem.fulltitle = item.fulltitle
    return itemlist
