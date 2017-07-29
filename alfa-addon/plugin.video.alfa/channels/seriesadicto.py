# -*- coding: utf-8 -*-

import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(
        Item(channel=item.channel, action="letras", title="Todas por orden alfabético", url="http://seriesadicto.com/",
             folder=True))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar..."))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://seriesadicto.com/buscar/" + texto

    try:
        return series(item)
    # Se captura la excepci?n, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def letras(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data, '<li class="nav-header">Por inicial</li>(.*?)</ul>')
    logger.info("data=" + data)

    patronvideos = '<li><a rel="nofollow" href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(
            Item(channel=item.channel, action='series', title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist


def series(item):
    logger.info()
    itemlist = []

    '''
    <li class="col-xs-6 col-sm-4 col-md-2">
    <a href="/serie/justicia-ciega-blind-justuce" title="Ver Justicia ciega ( Blind Justuce ) Online" class="thumbnail thumbnail-artist-grid">
    <img style="width: 120px; height: 180px;" src="/img/series/justicia-ciega-blind-justuce-th.jpg" alt="Justicia ciega ( Blind Justuce )"/>
    '''

    data = scrapertools.cachePage(item.url)
    logger.info("data=" + data)

    patron = '<li class="col-xs-6[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img style="[^"]+" src="([^"]+)" alt="([^"]+)"'
    logger.info("patron=" + patron)

    matches = re.compile(patron, re.DOTALL).findall(data)
    logger.info("matches=" + repr(matches))
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle.strip())
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="episodios", title=title, fulltitle=title, url=url, thumbnail=thumbnail,
                 plot=plot, show=title, folder=True))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    '''
    <tr>
    <td class="sape"><i class="glyphicon glyphicon-film"></i> <a href="/capitulo/saving-hope/1/2/82539" class="color4">Saving Hope 1x02</a></td>
    <td><div class="vistodiv" title="82539"><a title="Marcar como Visto"><span class="visto visto-no"></span></a></div></td>
    <td>
    <img src="/img/3.png" border="0" height="14" width="22" />&nbsp;<img src="/img/4.png" border="0" height="14" width="22" />&nbsp;          </td>
    </tr>
    '''

    data = scrapertools.cachePage(item.url)

    patron = '<tr[^<]+'
    patron += '<td class="sape"><i[^<]+</i[^<]+<a href="([^"]+)"[^>]+>([^<]+)</a></td[^<]+'
    patron += '<td><div[^<]+<a[^<]+<span[^<]+</span></a></div></td[^<]+'
    patron += '<td>(.*?)</td'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, bloqueidiomas in matches:
        title = scrapedtitle.strip() + " (" + extrae_idiomas(bloqueidiomas) + ")"
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url, thumbnail=thumbnail,
                 plot=plot, show=item.show, folder=True))

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=item.show))
        itemlist.append(Item(channel=item.channel, title="Descargar todos los episodios de la serie", url=item.url,
                             action="download_all_episodes", extra="episodios", show=item.show))

    return itemlist


def extrae_idiomas(bloqueidiomas):
    logger.info("idiomas=" + bloqueidiomas)
    patronidiomas = '([a-z0-9]+).png"'
    idiomas = re.compile(patronidiomas, re.DOTALL).findall(bloqueidiomas)
    textoidiomas = ""
    for idioma in idiomas:
        if idioma == "1":
            textoidiomas = textoidiomas + "Español" + "/"
        if idioma == "2":
            textoidiomas = textoidiomas + "Latino" + "/"
        if idioma == "3":
            textoidiomas = textoidiomas + "VOS" + "/"
        if idioma == "4":
            textoidiomas = textoidiomas + "VO" + "/"

    textoidiomas = textoidiomas[:-1]
    return textoidiomas


def codigo_a_idioma(codigo):
    idioma = ""
    if codigo == "1":
        idioma = "Español"
    if codigo == "2":
        idioma = "Latino"
    if codigo == "3":
        idioma = "VOS"
    if codigo == "4":
        idioma = "VO"

    return idioma


def findvideos(item):
    logger.info()
    itemlist = []

    '''
    <tr class="lang_3 no-mobile">
    <td><img src="/img/3.png" border="0" height="14" width="22" /></td>
    <td>Nowvideo</td>
    <td class="enlacevideo" title="82539"><a href="http://www.nowvideo.eu/video/4fdc641896fe8" rel="nofollow" target="_blank" class="btn btn-primary btn-xs bg2"><i class="glyphicon glyphicon-play"></i> Reproducir</a></td>
    </td>
    </tr>
    '''
    # Descarga la pagina
    data = scrapertools.cachePage(item.url)

    patron = '<tr class="lang_[^<]+'
    patron += '<td><img src="/img/(\d).png"[^<]+</td[^<]+'
    patron += '<td>([^<]+)</td[^<]+'
    patron += '<td class="enlacevideo"[^<]+<a href="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for idioma, servername, scrapedurl in matches:
        title = "Mirror en " + servername + " (" + codigo_a_idioma(idioma) + ")"
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="play", title=title, fulltitle=title, url=url, thumbnail=thumbnail,
                 plot=plot, folder=False))

    return itemlist


def play(item):
    logger.info()

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        videoitem.title = "Enlace encontrado en " + videoitem.server + " (" + scrapertools.get_filename_from_url(
            videoitem.url) + ")"
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = item.channel

    return itemlist
