# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Estrenos", action="peliculas",
                         url="http://gnula.nu/peliculas-online/lista-de-peliculas-online-parte-1/", viewmode="movie"))
    itemlist.append(
        Item(channel=item.channel, title="Generos", action="generos", url="http://gnula.nu/generos/lista-de-generos/"))
    itemlist.append(Item(channel=item.channel, title="Recomendadas", action="peliculas",
                         url="http://gnula.nu/peliculas-online/lista-de-peliculas-recomendadas/", viewmode="movie"))
    # itemlist.append( Item(channel=item.channel, title="Portada"       , action="portada"    , url="http://gnula.nu/"))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = scrapertools.cache_page(item.url)

    # <span style="font-weight: bold;">Lista de géneros</span><br/>
    data = scrapertools.find_single_match(data, '<spa[^>]+>Lista de g(.*?)/table')

    # <strong>Historia antigua</strong> [<a href="http://gnula.nu/generos/lista-de-peliculas-del-genero-historia-antigua/"
    patron = '<strong>([^<]+)</strong> .<a href="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for genero, scrapedurl in matches:
        title = scrapertools.htmlclean(genero)
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action='peliculas', title=title, url=url, thumbnail=thumbnail, plot=plot,
                 extra=title, viewmode="movie"))

    itemlist = sorted(itemlist, key=lambda item: item.title)

    return itemlist


def peliculas(item):
    logger.info()

    '''
    <a class="Ntooltip" href="http://gnula.nu/comedia-romantica/ver-with-this-ring-2015-online/">With This Ring<span><br/>
    <img src="http://gnula.nu/wp-content/uploads/2015/06/With_This_Ring2.gif"></span></a> [<span style="color: #33ccff;">18/07/15</span> <span style="color: #33ff33;">(VS)</span><span style="color: red;">(VC)</span><span style="color: #cc66cc;">(VL)</span>] [<span style="color: #ffcc99;">HD-R</span>]&#8212;&#8211;<strong>Comedia, Romántica</strong><br/>
    '''
    '''
    <a class="Ntooltip" href="http://gnula.nu/aventuras/ver-las-aventuras-de-tintin-el-secreto-del-unicornio-2011-online/">The Adventures of Tintin<span><br />
    <img src="http://gnula.nu/wp-content/uploads/2015/07/The_Adventures_of_Tintin_Secret_of_the_Unicorn2.gif"></span></a> (2011) [<span style="color: #33ccff;">10/07/15</span> <span style="color: #33ff33;">(VS)</span><span style="color: red;">(VC)</span><span style="color: #cc66cc;">(VL)</span>] [<span style="color: #ffcc99;">DVD-R</span>]&#8212;&#8211;<strong>Animación, Infantil, Aventuras</strong><br />
    '''
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    patron = '<a class="Ntooltip" href="([^"]+)">([^<]+)<span><br[^<]+'
    patron += '<img src="([^"]+)"></span></a>(.*?)<br'

    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []
    for scrapedurl, scrapedtitle, scrapedthumbnail, resto in matches:
        plot = scrapertools.htmlclean(resto).strip()
        title = scrapedtitle + " " + plot
        fulltitle = title
        contentTitle = scrapedtitle
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(Item(channel=item.channel, action='findvideos', title=title, fulltitle=fulltitle, url=url,
                             thumbnail=thumbnail, plot=plot, extra=title, hasContentDetails=True,
                             contentTitle=contentTitle, contentThumbnail=thumbnail,
                             contentType="movie", context=["buscar_trailer"]))

    return itemlist


def findvideos(item):
    logger.info("item=" + item.tostring())

    # Descarga la página para obtener el argumento
    data = scrapertools.cachePage(item.url)
    item.plot = scrapertools.find_single_match(data, '<div class="entry">(.*?)<div class="iframes">')
    item.plot = scrapertools.htmlclean(item.plot).strip()
    item.contentPlot = item.plot

    newthumbnail = scrapertools.find_single_match(data,
                                                  '<div class="entry"[^<]+<p align="center"><img alt="[^"]+" src="([^"]+)"')
    if newthumbnail != "":
        item.thumbnail = newthumbnail
        item.contentThumbnail = newthumbnail

    logger.info("plot=" + item.plot)

    return servertools.find_video_items(item=item, data=data)
