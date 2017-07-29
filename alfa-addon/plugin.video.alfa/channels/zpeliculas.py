# -*- coding: utf-8 -*-

import re
import urllib

from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    # itemlist.append( Item(channel=item.channel, action="destacadas" , title="Destacadas", url="http://www.zpeliculas.com", fanart="http://www.zpeliculas.com/templates/mytopV2/images/background.png"))
    itemlist.append(
        Item(channel=item.channel, action="peliculas", title="Últimas peliculas", url="http://www.zpeliculas.com/",
             fanart="http://www.zpeliculas.com/templates/mytopV2/images/background.png", viewmode="movie"))
    # itemlist.append( Item(channel=item.channel, action="sugeridas"  , title="Películas sugeridas", url="http://www.zpeliculas.com", fanart="http://www.zpeliculas.com/templates/mytopV2/images/background.png", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="generos", title="Por género", url="http://www.zpeliculas.com",
                         fanart="http://www.zpeliculas.com/templates/mytopV2/images/background.png"))
    itemlist.append(Item(channel=item.channel, action="alfabetico", title="Listado alfabético",
                         fanart="http://www.zpeliculas.com/templates/mytopV2/images/background.png"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscador", url="http://www.zpeliculas.com",
                         fanart="http://www.zpeliculas.com/templates/mytopV2/images/background.png", viewmode="movie"))

    return itemlist


def alfabetico(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="peliculas", title="A", url="http://www.zpeliculas.com/cat/a",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="B", url="http://www.zpeliculas.com/cat/b",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="C", url="http://www.zpeliculas.com/cat/c",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="D", url="http://www.zpeliculas.com/cat/d",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="E", url="http://www.zpeliculas.com/cat/e",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="F", url="http://www.zpeliculas.com/cat/f",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="G", url="http://www.zpeliculas.com/cat/g",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="H", url="http://www.zpeliculas.com/cat/h",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="I", url="http://www.zpeliculas.com/cat/i",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="J", url="http://www.zpeliculas.com/cat/j",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="K", url="http://www.zpeliculas.com/cat/k",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="L", url="http://www.zpeliculas.com/cat/l",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="M", url="http://www.zpeliculas.com/cat/m",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="N", url="http://www.zpeliculas.com/cat/n",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="O", url="http://www.zpeliculas.com/cat/o",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="P", url="http://www.zpeliculas.com/cat/p",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Q", url="http://www.zpeliculas.com/cat/q",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="R", url="http://www.zpeliculas.com/cat/r",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="S", url="http://www.zpeliculas.com/cat/s",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="T", url="http://www.zpeliculas.com/cat/t",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="U", url="http://www.zpeliculas.com/cat/u",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="V", url="http://www.zpeliculas.com/cat/v",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="W", url="http://www.zpeliculas.com/cat/w",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="X", url="http://www.zpeliculas.com/cat/x",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Y", url="http://www.zpeliculas.com/cat/y",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Z", url="http://www.zpeliculas.com/cat/z",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="0", url="http://www.zpeliculas.com/cat/0",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="1", url="http://www.zpeliculas.com/cat/1",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="2", url="http://www.zpeliculas.com/cat/2",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="3", url="http://www.zpeliculas.com/cat/3",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="4", url="http://www.zpeliculas.com/cat/4",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="5", url="http://www.zpeliculas.com/cat/5",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="6", url="http://www.zpeliculas.com/cat/6",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="7", url="http://www.zpeliculas.com/cat/7",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="8", url="http://www.zpeliculas.com/cat/8",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="9", url="http://www.zpeliculas.com/cat/9",
                         viewmode="movie"))

    return itemlist


def generos(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Acción",
                         url="http://www.zpeliculas.com/peliculas/p-accion/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Animación",
                         url="http://www.zpeliculas.com/peliculas/p-animacion/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Aventura",
                         url="http://www.zpeliculas.com/peliculas/p-aventura/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Biografía",
                         url="http://www.zpeliculas.com/peliculas/p-biografia/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Bélico",
                         url="http://www.zpeliculas.com/peliculas/p-belico/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Ciencia Ficción",
                         url="http://www.zpeliculas.com/peliculas/p-cienciaficcion/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Comedia",
                         url="http://www.zpeliculas.com/peliculas/p-comedia/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Crimen",
                         url="http://www.zpeliculas.com/peliculas/p-crimen/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Drama",
                         url="http://www.zpeliculas.com/peliculas/p-drama/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Fantasía",
                         url="http://www.zpeliculas.com/peliculas/p-fantasia/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Histórico",
                         url="http://www.zpeliculas.com/peliculas/p-historico/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Intriga",
                         url="http://www.zpeliculas.com/peliculas/p-intriga/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Musical",
                         url="http://www.zpeliculas.com/peliculas/p-musical/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Romántica",
                         url="http://www.zpeliculas.com/peliculas/p-romantica/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Terror",
                         url="http://www.zpeliculas.com/peliculas/p-terror/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Thriller",
                         url="http://www.zpeliculas.com/peliculas/p-thriller/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Western",
                         url="http://www.zpeliculas.com/peliculas/p-western/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Otros",
                         url="http://www.zpeliculas.com/peliculas/p-otros/", viewmode="movie"))
    return itemlist


def search(item, texto):
    try:
        post = urllib.urlencode({"story": texto, "do": "search", "subaction": "search", "x": "0", "y": "0"})
        data = scrapertools.cache_page("http://www.zpeliculas.com", post=post)

        patron = '<div class="leftpane">(.*?)<div class="clear"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        itemlist = []

        for match in matches:
            scrapedtitle = scrapertools.find_single_match(match, '<div class="shortname">([^<]+)</div>')
            scrapedurl = scrapertools.find_single_match(match, '<a href="([^"]+)"')
            scrapedthumbnail = scrapertools.find_single_match(match, '<img src="([^"]+)"')
            scrapedyear = scrapertools.find_single_match(match, '<div class="year"[^>]+>([^<]+)</div>')
            scrapedidioma = scrapertools.find_single_match(match, 'title="Idioma">([^<]+)</div>')
            scrapedcalidad = scrapertools.find_single_match(match,
                                                            '<div class="shortname"[^<]+</div[^<]+<div[^>]+>([^<]+)</div>')

            title = scrapedtitle + ' (' + scrapedyear + ') [' + scrapedidioma + '] [' + scrapedcalidad + ']'
            url = scrapedurl
            thumbnail = scrapedthumbnail
            plot = ""
            logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
            itemlist.append(
                Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                     show=title, fanart=thumbnail, hasContentDetails=True, contentTitle=title,
                     contentThumbnail=thumbnail,
                     contentType="movie", context=["buscar_trailer"]))

        return itemlist
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = "http://www.zpeliculas.com"

        elif categoria == 'infantiles':
            item.url = "http://www.zpeliculas.com/peliculas/p-animacion/"

        else:
            return []

        itemlist = peliculas(item)
        if itemlist[-1].extra == "next_page":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def peliculas(item):
    logger.info()

    # Descarga la página
    body = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(body,
                                  '<div class="shortmovies">(.*?)<div class="navigation ignore-select" align="center">')

    '''
    <div class="leftpane">
    <div class="movieposter" title="Descargar Sólo los amantes sobreviven">
    <a href="http://www.zpeliculas.com/peliculas/p-drama/1634-slo-los-amantes-sobreviven.html"><img src="http://i.imgur.com/NBPgXrp.jpg" width="110" height="150" alt="Sólo los amantes sobreviven" title="Descargar Sólo los amantes sobreviven" /></a>
    <div class="shortname">Sólo los amantes sobreviven</div>
    <div class="BDRip">BDRip</div>
    </div>
    </div>

    <div class="rightpane">
    <div style="display:block;overflow:hidden;">
    <h2 class="title" title="Sólo los amantes sobreviven"><a href="http://www.zpeliculas.com/peliculas/p-drama/1634-slo-los-amantes-sobreviven.html">Sólo los amantes sobreviven</a></h2>

    <div style="height:105px; overflow:hidden;">
    <div class="small">
    <div class="cats" title="Genero"><a href="http://www.zpeliculas.com/peliculas/p-drama/">Drama</a>, <a href="http://www.zpeliculas.com/peliculas/p-fantasia/">Fantasia</a>, <a href="http://www.zpeliculas.com/peliculas/p-romantica/">Romantica</a></div>
    <div class="year" title="A&ntilde;o">2013</div>
    <div class="ESP" title="Idioma">ESP</div>
    <div class="FA" title="Sólo los amantes sobreviven FA Official Website"><a href="http://www.filmaffinity.com/es/film851633.html" target="_blank" title="Sólo los amantes sobreviven en filmaffinity">Sólo los amantes sobreviven en FA</a></div>
    </div>
    </div>
    <div class="clear" style="height:2px;"></div>
    <div style="float:right">
    '''
    patron = '<div class="leftpane">(.*?)<div style="float\:right">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    itemlist = []

    for match in matches:
        scrapedurl = scrapertools.find_single_match(match, '<a href="([^"]+)"')
        scrapedthumbnail = scrapertools.find_single_match(match, '<img src="([^"]+)"')
        scrapedtitle = scrapertools.find_single_match(match, '<div class="shortname">([^<]+)')
        scrapedcalidad = scrapertools.find_single_match(match,
                                                        '<div class="shortname">[^<]+</div[^<]+<div class="[^"]+">([^<]+)')
        scrapedyear = scrapertools.find_single_match(match, '<div class="year[^>]+>([^<]+)')
        scrapedidioma = scrapertools.find_single_match(match,
                                                       '<div class="year[^>]+>[^<]+</div[^<]+<div class[^>]+>([^<]+)')

        contentTitle = scrapertools.htmlclean(scrapedtitle)
        # logger.info("title="+scrapedtitle)
        title = contentTitle + ' (' + scrapedyear + ') [' + scrapedidioma + '] [' + scrapedcalidad + ']'
        # title = scrapertools.htmlclean(title)
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 hasContentDetails=True, contentTitle=contentTitle, contentThumbnail=thumbnail, fanart=thumbnail,
                 contentType="movie", context=["buscar_trailer"]))

    next_page = scrapertools.find_single_match(body, '<a href="([^"]+)">Siguiente')
    if next_page != "":
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=">> Página siguiente", url=next_page, thumbnail="",
                 plot="", show="", viewmode="movie", fanart=thumbnail, extra="next_page"))

    return itemlist


def destacadas(item):
    logger.info()

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data, '<div id="sliderwrapper">(.*?)<div class="genreblock">')
    '''
    <div class="imageview view-first">
    <a href="/templates/mytopV2/blockpro/noimage-full.png" onclick="return hs.expand(this)"><img src="http://i.imgur.com/H4d96Wn.jpg" alt="Ocho apellidos vascos"></a>
    <div class="mask">
    <h2><a href="/peliculas/p-comedia/1403-ocho-apellidos-vascos.html" title="Ocho apellidos vascos">Ocho apellidos vascos</a></h2>
    </div>
    '''
    patron = '<div class="imageview view-first">.*?<a href=.*?>.*?src="(.*?)" alt="(.*?)"></a>.*?<h2><a href="(.*?)".*?</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist = []

    for scrapedthumbnail, scrapedtitle, scrapedurl in matches:
        logger.info("title=" + scrapedtitle)
        title = scrapedtitle
        title = scrapertools.htmlclean(title)
        url = "http://www.zpeliculas.com" + scrapedurl
        thumbnail = scrapedthumbnail
        plot = ""
        plot = unicode(plot, "iso-8859-1", errors="replace").encode("utf-8")
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 show=title, fanart=thumbnail, hasContentDetails=True, contentTitle=title, contentThumbnail=thumbnail,
                 contentType="movie", context=["buscar_trailer"]))

    return itemlist


def sugeridas(item):
    logger.info()

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data, '<ul class="links">(.*?)</ul>')
    '''
    <li><a href="/peliculas/p-accion/425-instinto-asesino.html" title="Descargar Instinto asesino (The Crew)"><span class="movie-name">Instinto asesino (The Crew)</span><img src="http://i.imgur.com/1xXLz.jpg" width="102" height="138" alt="Instinto asesino (The Crew)" title="Descargar Instinto asesino (The Crew)" /></a></li>
    '''
    patron = '<li>.*?<a href="(.*?)".*?"movie-name">(.*?)</span><img src="(.*?)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist = []

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        logger.info("title=" + scrapedtitle)
        title = scrapedtitle
        title = scrapertools.htmlclean(title)
        url = "http://www.zpeliculas.com" + scrapedurl
        thumbnail = scrapedthumbnail
        plot = ""
        plot = unicode(plot, "iso-8859-1", errors="replace").encode("utf-8")
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 show=title, fanart=thumbnail, hasContentDetails=True, contentTitle=title, contentThumbnail=thumbnail,
                 contentType="movie", context=["buscar_trailer"]))

    return itemlist


def findvideos(item):
    logger.info("item=" + item.tostring())

    # Descarga la página para obtener el argumento
    data = scrapertools.cachePage(item.url)
    item.plot = scrapertools.find_single_match(data, '<div class="contenttext">([^<]+)<').strip()
    item.contentPlot = item.plot
    logger.info("plot=" + item.plot)

    return servertools.find_video_items(item=item, data=data)
