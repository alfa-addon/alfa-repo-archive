# -*- coding: utf-8 -*-

import re
import urlparse

import xbmc
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


# Main list manual

def listav(item):
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patronbloque = '<li><div class="yt-lockup.*?<img.*?src="([^"]+)".*?'
    patronbloque += '<h3 class="yt-lockup-title "><a href="([^"]+)".*?title="([^"]+)".*?'
    patronbloque += '</a><span class=.*?">(.*?)</span></h3>'
    matchesbloque = re.compile(patronbloque, re.DOTALL).findall(data)
    scrapertools.printMatches(matchesbloque)

    scrapedduration = ''
    for scrapedthumbnail, scrapedurl, scrapedtitle, scrapedduration in matchesbloque:
        scrapedtitle = '[COLOR white]' + scrapedtitle + '[/COLOR] [COLOR red]' + scrapedduration + '[/COLOR]'
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.thumbnail, scrapedthumbnail)
        xbmc.log("$ " + scrapedurl + " " + scrapedtitle + " " + scrapedthumbnail)
        itemlist.append(Item(channel=item.channel, action="play", title=scrapedtitle, fulltitle=scrapedtitle, url=url,
                             thumbnail=thumbnail, fanart=thumbnail))


        # Paginacion

    patronbloque = '<div class="branded-page-box .*? spf-link ">(.*?)</div>'
    matches = re.compile(patronbloque, re.DOTALL).findall(data)
    for bloque in matches:
        patronvideo = '<a href="([^"]+)"'
        matchesx = re.compile(patronvideo, re.DOTALL).findall(bloque)
        for scrapedurl in matchesx:
            url = urlparse.urljoin(item.url, 'https://www.youtube.com' + scrapedurl)
            # solo me quedo con el ultimo enlace
        itemlist.append(
            Item(channel=item.channel, action="listav", title="Siguiente pag >>", fulltitle="Siguiente Pag >>", url=url,
                 thumbnail=item.thumbnail, fanart=item.fanart))

    return itemlist


def busqueda(item):
    itemlist = []
    keyboard = xbmc.Keyboard("", "Busqueda")
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        myurl = keyboard.getText().replace(" ", "+")

        data = scrapertools.cache_page('https://www.youtube.com/results?q=' + myurl)
        data = data.replace("\n", "").replace("\t", "")
        data = scrapertools.decodeHtmlentities(data)

        patronbloque = '<li><div class="yt-lockup.*?<img.*?src="([^"]+)".*?'
        patronbloque += '<h3 class="yt-lockup-title "><a href="([^"]+)".*?title="([^"]+)".*?'
        patronbloque += '</a><span class=.*?">(.*?)</span></h3>'
        matchesbloque = re.compile(patronbloque, re.DOTALL).findall(data)
        scrapertools.printMatches(matchesbloque)

        for scrapedthumbnail, scrapedurl, scrapedtitle, scrapedduracion in matchesbloque:
            scrapedtitle = scrapedtitle + ' ' + scrapedduracion
            url = scrapedurl
            thumbnail = scrapedthumbnail
            xbmc.log("$ " + scrapedurl + " " + scrapedtitle + " " + scrapedthumbnail)
            itemlist.append(
                Item(channel=item.channel, action="play", title=scrapedtitle, fulltitle=scrapedtitle, url=url,
                     thumbnail=thumbnail, fanart=thumbnail))


            # Paginacion

        patronbloque = '<div class="branded-page-box .*? spf-link ">(.*?)</div>'
        matches = re.compile(patronbloque, re.DOTALL).findall(data)
        for bloque in matches:
            patronvideo = '<a href="([^"]+)"'
            matchesx = re.compile(patronvideo, re.DOTALL).findall(bloque)
            for scrapedurl in matchesx:
                url = 'https://www.youtube.com' + scrapedurl
                # solo me quedo con el ultimo enlace

            itemlist.append(
                Item(channel=item.channel, action="listav", title="Siguiente pag >>", fulltitle="Siguiente Pag >>",
                     url=url))
        return itemlist
    else:
        # xbmcgui.Dialog().ok(item.channel, "nada que buscar")
        # xbmc.executebuiltin("Action(up)")
        xbmc.executebuiltin("Action(enter)")

        # itemlist.append( Item(channel=item.channel, action="listav", title="<< Volver", fulltitle="Volver" , url="history.back()") )


def mainlist(item):
    logger.info()
    itemlist = []

    item.url = 'https://www.youtube.com/results?q=crimenes+imperfectos&sp=CAI%253D'
    scrapedtitle = "[COLOR white]Crimenes [COLOR red]Imperfectos[/COLOR]"
    item.thumbnail = urlparse.urljoin(item.thumbnail,
                                      "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcQ2PcyvcYIg6acvdUZrHGFFk_E3mXK9QSh-5TypP8Rk6zQ6S1yb2g")
    item.fanart = urlparse.urljoin(item.fanart,
                                   "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcQ2PcyvcYIg6acvdUZrHGFFk_E3mXK9QSh-5TypP8Rk6zQ6S1yb2g")

    itemlist.append(
        Item(channel=item.channel, action="listav", title=scrapedtitle, fulltitle=scrapedtitle, url=item.url,
             thumbnail=item.thumbnail, fanart=item.fanart))

    item.url = 'https://www.youtube.com/results?search_query=russian+dash+cam&sp=CAI%253D'
    scrapedtitle = "[COLOR blue]Russian[/COLOR] [COLOR White]Dash[/COLOR] [COLOR red]Cam[/COLOR]"
    item.thumbnail = urlparse.urljoin(item.thumbnail, "https://i.ytimg.com/vi/-C6Ftromtig/maxresdefault.jpg")
    item.fanart = urlparse.urljoin(item.fanart,
                                   "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcRQLO-n-kO1ByY8lLhKxz0-cejJD1J7rLge_j0E0Gh9LJ2WtTbSnA")

    itemlist.append(
        Item(channel=item.channel, action="listav", title=scrapedtitle, fulltitle=scrapedtitle, url=item.url,
             thumbnail=item.thumbnail, fanart=item.fanart))

    item.url = 'https://www.youtube.com/results?search_query=cuarto+milenio+programa+completo&sp=CAI%253D'
    scrapedtitle = "[COLOR green]Cuarto[/COLOR] [COLOR White]Milenio[/COLOR]"
    item.thumbnail = urlparse.urljoin(item.thumbnail,
                                      "http://cuatrostatic-a.akamaihd.net/cuarto-milenio/Cuarto-Milenio-analiza-fantasma-Granada_MDSVID20100924_0063_3.jpg")
    item.fanart = urlparse.urljoin(item.fanart,
                                   "http://cuatrostatic-a.akamaihd.net/cuarto-milenio/programas/temporada-07/t07xp32/fantasma-universidad_MDSVID20120420_0001_3.jpg")

    itemlist.append(
        Item(channel=item.channel, action="listav", title=scrapedtitle, fulltitle=scrapedtitle, url=item.url,
             thumbnail=item.thumbnail, fanart=item.fanart))

    item.url = 'https://www.youtube.com/results?q=milenio+3&sp=CAI%253D'
    scrapedtitle = "[COLOR green]Milenio[/COLOR] [COLOR White]3- Podcasts[/COLOR]"
    item.thumbnail = urlparse.urljoin(item.thumbnail,
                                      "http://cuatrostatic-a.akamaihd.net/cuarto-milenio/Cuarto-Milenio-analiza-fantasma-Granada_MDSVID20100924_0063_3.jpg")
    item.fanart = urlparse.urljoin(item.fanart,
                                   "http://cuatrostatic-a.akamaihd.net/cuarto-milenio/programas/temporada-07/t07xp32/fantasma-universidad_MDSVID20120420_0001_3.jpg")

    itemlist.append(
        Item(channel=item.channel, action="listav", title=scrapedtitle, fulltitle=scrapedtitle, url=item.url,
             thumbnail=item.thumbnail, fanart=item.fanart))

    scrapedtitle = "[COLOR red]buscar ...[/COLOR]"
    item.thumbnail = urlparse.urljoin(item.thumbnail,
                                      "http://cuatrostatic-a.akamaihd.net/cuarto-milenio/Cuarto-Milenio-analiza-fantasma-Granada_MDSVID20100924_0063_3.jpg")
    item.fanart = urlparse.urljoin(item.fanart,
                                   "http://cuatrostatic-a.akamaihd.net/cuarto-milenio/programas/temporada-07/t07xp32/fantasma-universidad_MDSVID20120420_0001_3.jpg")

    itemlist.append(Item(channel=item.channel, action="busqueda", title=scrapedtitle, fulltitle=scrapedtitle,
                         thumbnail=item.thumbnail, fanart=item.fanart))

    return itemlist


def play(item):
    logger.info("url=" + item.url)

    itemlist = servertools.find_video_items(data=item.url)

    return itemlist
