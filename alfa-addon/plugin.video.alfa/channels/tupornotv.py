# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Pendientes de Votación", action="novedades",
                         url="http://tuporno.tv/pendientes"))
    itemlist.append(
        Item(channel=item.channel, title="Populares", action="masVistos", url="http://tuporno.tv/", folder=True))
    itemlist.append(
        Item(channel=item.channel, title="Categorias", action="categorias", url="http://tuporno.tv/categorias/",
             folder=True))
    itemlist.append(Item(channel=item.channel, title="Videos Recientes", action="novedades",
                         url="http://tuporno.tv/videosRecientes/", folder=True))
    itemlist.append(Item(channel=item.channel, title="Top Videos (mas votados)", action="masVotados",
                         url="http://tuporno.tv/topVideos/", folder=True))
    itemlist.append(Item(channel=item.channel, title="Nube de Tags", action="categorias", url="http://tuporno.tv/tags/",
                         folder=True))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    return itemlist


def novedades(item):
    logger.info()
    url = item.url
    # ------------------------------------------------------
    # Descarga la página
    # ------------------------------------------------------
    data = scrapertools.cachePage(url)
    # logger.info(data)

    # ------------------------------------------------------
    # Extrae las entradas
    # ------------------------------------------------------
    # seccion novedades
    '''
    <table border="0" cellpadding="0" cellspacing="0" ><tr><td align="center" width="100%" valign="top" height="160px">
    <a href="/videos/cogiendo-en-el-bosque"><img src="imagenes/videos//c/o/cogiendo-en-el-bosque_imagen2.jpg" alt="Cogiendo en el bosque" border="0" align="top" /></a>
    <h2><a href="/videos/cogiendo-en-el-bosque">Cogiendo en el bosque</a></h2>
    '''
    patronvideos = '<div class="relative">(.*?)</div><div class="video'

    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    # if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for match in matches:
        # Titulo
        try:
            scrapedtitle = re.compile('title="(.+?)"').findall(match)[0]

        except:
            scrapedtitle = ''
        try:
            scrapedurl = re.compile('href="(.+?)"').findall(match)[0]
            scrapedurl = urlparse.urljoin(url, scrapedurl)
        except:
            continue
        try:
            scrapedthumbnail = re.compile('src="(.+?)"').findall(match)[0]
            scrapedthumbnail = urlparse.urljoin(url, scrapedthumbnail)
        except:
            scrapedthumbnail = ''
        scrapedplot = ""
        try:
            duracion = re.compile('<div class="duracion">(.+?)<').findall(match)[0]
        except:
            try:
                duracion = re.compile('\((.+?)\)<br').findall(match[3])[0]
            except:
                duracion = ""

        # logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"], duracion=["+duracion+"]")
        # Añade al listado de XBMC
        # trozos = scrapedurl.split("/")
        # id = trozos[len(trozos)-1]
        # videos = "http://149.12.64.129/videoscodiH264/"+id[0:1]+"/"+id[1:2]+"/"+id+".flv"
        itemlist.append(
            Item(channel=item.channel, action="play", title=scrapedtitle + " [" + duracion + "]", url=scrapedurl,
                 thumbnail=scrapedthumbnail, plot=scrapedplot, server="Directo", folder=False))

    # ------------------------------------------------------
    # Extrae el paginador
    # ------------------------------------------------------
    # <a href="/topVideos/todas/mes/2/" class="enlace_si">Siguiente </a>
    patronsiguiente = '<a href="(.+?)" class="enlace_si">Siguiente </a>'
    siguiente = re.compile(patronsiguiente, re.DOTALL).findall(data)
    if len(siguiente) > 0:
        scrapedurl = urlparse.urljoin(url, siguiente[0])
        itemlist.append(Item(channel=item.channel, action="novedades", title="!Next page", url=scrapedurl, folder=True))

    return itemlist


def masVistos(item):
    logger.info()

    itemlist = []
    itemlist.append(
        Item(channel=item.channel, title="Hoy", action="novedades", url="http://tuporno.tv/hoy", folder=True))
    itemlist.append(Item(channel=item.channel, title="Recientes", action="novedades", url="http://tuporno.tv/recientes",
                         folder=True))
    itemlist.append(
        Item(channel=item.channel, title="Semana", action="novedades", url="http://tuporno.tv/semana", folder=True))
    itemlist.append(
        Item(channel=item.channel, title="Mes", action="novedades", url="http://tuporno.tv/mes", folder=True))
    itemlist.append(
        Item(channel=item.channel, title="Año", action="novedades", url="http://tuporno.tv/ano", folder=True))
    return itemlist


def categorias(item):
    logger.info()

    url = item.url
    # ------------------------------------------------------
    # Descarga la página
    # ------------------------------------------------------
    data = scrapertools.cachePage(url)
    # logger.info(data)
    # ------------------------------------------------------
    # Extrae las entradas
    # ------------------------------------------------------
    # seccion categorias
    # Patron de las entradas
    if url == "http://tuporno.tv/categorias/":
        patronvideos = '<li><a href="([^"]+)"'  # URL
        patronvideos += '>([^<]+)</a></li>'  # TITULO
    else:
        patronvideos = '<a href="(.tags[^"]+)"'  # URL
        patronvideos += ' class="[^"]+">([^<]+)</a>'  # TITULO

    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    # if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for match in matches:
        if match[1] in ["SexShop", "Videochat", "Videoclub"]:
            continue
        # Titulo
        scrapedtitle = match[1]
        scrapedurl = urlparse.urljoin(url, match[0])
        scrapedthumbnail = ""
        scrapedplot = ""
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

        # Añade al listado de XBMC
        itemlist.append(Item(channel=item.channel, action="novedades", title=scrapedtitle.capitalize(), url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist


def masVotados(item):
    logger.info()

    itemlist = []
    itemlist.append(
        Item(channel=item.channel, title="Hoy", action="novedades", url="http://tuporno.tv/topVideos/todas/hoy",
             folder=True))
    itemlist.append(Item(channel=item.channel, title="Recientes", action="novedades",
                         url="http://tuporno.tv/topVideos/todas/recientes", folder=True))
    itemlist.append(
        Item(channel=item.channel, title="Semana", action="novedades", url="http://tuporno.tv/topVideos/todas/semana",
             folder=True))
    itemlist.append(
        Item(channel=item.channel, title="Mes", action="novedades", url="http://tuporno.tv/topVideos/todas/mes",
             folder=True))
    itemlist.append(
        Item(channel=item.channel, title="Año", action="novedades", url="http://tuporno.tv/topVideos/todas/ano",
             folder=True))
    return itemlist


def search(item, texto):
    logger.info()
    if texto != "":
        texto = texto.replace(" ", "+")
    else:
        texto = item.extra.replace(" ", "+")
    item.url = "http://tuporno.tv/buscador/?str=" + texto
    try:
        return getsearch(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def getsearch(item):
    logger.info()
    data = scrapertools.cachePage(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    patronvideos = '<div class="relative"><a href="(.videos[^"]+)"[^>]+><img.+?src="([^"]+)" alt="(.+?)" .*?<div class="duracion">(.+?)</div></div></div>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        itemlist = []
        for match in matches:
            # Titulo
            scrapedtitle = match[2].replace("<b>", "")
            scrapedtitle = scrapedtitle.replace("</b>", "")
            scrapedurl = urlparse.urljoin("http://tuporno.tv/", match[0])
            scrapedthumbnail = urlparse.urljoin("http://tuporno.tv/", match[1])
            scrapedplot = ""
            duracion = match[3]

            itemlist.append(
                Item(channel=item.channel, action="play", title=scrapedtitle + " [" + duracion + "]", url=scrapedurl,
                     thumbnail=scrapedthumbnail, plot=scrapedplot, server="Directo", folder=False))

        '''<a href="/buscador/?str=busqueda&desde=HV_PAGINA_SIGUIENTE" class="enlace_si">Siguiente </a>'''
        patronsiguiente = '<a href="([^"]+)" class="enlace_si">Siguiente </a>'
        siguiente = re.compile(patronsiguiente, re.DOTALL).findall(data)
        if len(siguiente) > 0:
            patronultima = '<!--HV_SIGUIENTE_ENLACE'
            ultpagina = re.compile(patronultima, re.DOTALL).findall(data)
            scrapertools.printMatches(siguiente)

            if len(ultpagina) == 0:
                scrapedurl = urlparse.urljoin(item.url, siguiente[0])
                itemlist.append(
                    Item(channel=item.channel, action="getsearch", title="!Next page", url=scrapedurl, folder=True))
    return itemlist


def play(item):
    logger.info()
    itemlist = []

    # Lee la pagina del video
    data = scrapertools.cachePage(item.url)
    codVideo = scrapertools.get_match(data, 'body id="([^"]+)"')
    logger.info("codVideo=" + codVideo)

    # Lee la pagina con el codigo
    # http://tuporno.tv/flvurl.php?codVideo=188098&v=MAC%2011,5,502,146
    url = "http://tuporno.tv/flvurl.php?codVideo=" + codVideo + "&v=MAC%2011,5,502,146"
    data = scrapertools.cachePage(url)
    logger.info("data=" + data)
    kpt = scrapertools.get_match(data, "kpt\=(.+?)\&")
    logger.info("kpt=" + kpt)

    # Decodifica
    import base64
    url = base64.decodestring(kpt)
    logger.info("url=" + url)

    itemlist.append(
        Item(channel=item.channel, action="play", title=item.title, url=url, thumbnail=item.thumbnail, plot=item.plot,
             server="Directo", folder=False))

    return itemlist
