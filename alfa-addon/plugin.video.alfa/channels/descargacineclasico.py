# -*- coding: utf-8 -*-

import re
import urlparse

from channelselector import get_thumbnail_path
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import Tmdb
from servers.decrypters import expurl


def agrupa_datos(data):
    ## Agrupa los datos
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|<!--.*?-->', '', data)
    data = re.sub(r'\s+', ' ', data)
    data = re.sub(r'>\s<', '><', data)
    return data


def mainlist(item):
    logger.info()

    thumb_buscar = get_thumbnail_path() + "thumb_search.png"

    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Últimas agregadas", action="agregadas",
                         url="http://www.descargacineclasico.net/", viewmode="movie_with_plot"))
    itemlist.append(Item(channel=item.channel, title="Listado por género", action="porGenero",
                         url="http://www.descargacineclasico.net/"))
    itemlist.append(
        Item(channel=item.channel, title="Buscar", action="search", url="http://www.descargacineclasico.net/",
             thumbnail=thumb_buscar))

    return itemlist


def porGenero(item):
    logger.info()

    itemlist = []
    data = scrapertools.cache_page(item.url)
    logger.info("data=" + data)

    patron = '<ul class="columnas">(.*?)</ul>'
    data = re.compile(patron, re.DOTALL).findall(data)
    patron = '<li.*?>.*?href="([^"]+).*?>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data[0])

    for url, genero in matches:
        itemlist.append(
            Item(channel=item.channel, action="agregadas", title=genero, url=url, viewmode="movie_with_plot"))

    return itemlist


def search(item, texto):
    logger.info()

    '''
    texto_get = texto.replace(" ","%20")
    texto_post = texto.replace(" ","+")
    item.url = "http://pelisadicto.com/buscar/%s?search=%s" % (texto_get,texto_post)
    '''

    texto = texto.replace(" ", "+")
    item.url = "http://www.descargacineclasico.net/?s=" + texto

    try:
        return agregadas(item)
    # Se captura la excepci?n, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def agregadas(item):
    logger.info()
    itemlist = []
    '''
    # Descarga la pagina
    if "?search=" in item.url:
        url_search = item.url.split("?search=")
        data = scrapertools.cache_page(url_search[0], url_search[1])
    else:
        data = scrapertools.cache_page(item.url)
    logger.info("data="+data)
    '''

    data = scrapertools.cache_page(item.url)
    logger.info("data=" + data)

    # Extrae las entradas
    fichas = re.sub(r"\n|\s{2}", "", scrapertools.get_match(data, '<div class="review-box-container">(.*?)wp-pagenavi'))

    # <a href="http://www.descargacineclasico.net/ciencia-ficcion/quatermass-2-1957/"
    # title="Quatermass II (Quatermass 2) (1957) Descargar y ver Online">
    # <img style="border-radius:6px;"
    # src="//www.descargacineclasico.net/wp-content/uploads/2015/12/Quatermass-II-2-1957.jpg"
    # alt="Quatermass II (Quatermass 2) (1957) Descargar y ver Online Gratis" height="240" width="160">


    patron = '<div class="post-thumbnail"><a href="([^"]+)".*?'  # url
    patron += 'title="([^"]+)".*?'  # title
    patron += 'src="([^"]+).*?'  # thumbnail
    patron += '<p>([^<]+)'  # plot

    matches = re.compile(patron, re.DOTALL).findall(fichas)
    for url, title, thumbnail, plot in matches:
        title = title[0:title.find("Descargar y ver Online")]
        url = urlparse.urljoin(item.url, url)
        thumbnail = urlparse.urljoin(url, thumbnail)

        itemlist.append(Item(channel=item.channel, action="findvideos", title=title + " ", fulltitle=title, url=url,
                             thumbnail=thumbnail, plot=plot, show=title))

    # Paginación
    try:

        # <ul class="pagination"><li class="active"><span>1</span></li><li><span><a href="2">2</a></span></li><li><span><a href="3">3</a></span></li><li><span><a href="4">4</a></span></li><li><span><a href="5">5</a></span></li><li><span><a href="6">6</a></span></li></ul>

        patron_nextpage = r'<a class="nextpostslink" rel="next" href="([^"]+)'
        next_page = re.compile(patron_nextpage, re.DOTALL).findall(data)
        itemlist.append(Item(channel=item.channel, action="agregadas", title="Página siguiente >>", url=next_page[0],
                             viewmode="movie_with_plot"))
    except:
        pass

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []

    data = scrapertools.cache_page(item.url)

    data = scrapertools.unescape(data)

    titulo = item.title
    titulo_tmdb = re.sub("([0-9+])", "", titulo.strip())

    oTmdb = Tmdb(texto_buscado=titulo_tmdb, idioma_busqueda="es")
    item.fanart = oTmdb.get_backdrop()

    # Descarga la pagina
    #    data = scrapertools.cache_page(item.url)
    patron = '#div_\d_\D.+?<img id="([^"]+).*?<span>.*?</span>.*?<span>(.*?)</span>.*?imgdes.*?imgdes/([^\.]+).*?<a href=([^\s]+)'  # Añado calidad
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedidioma, scrapedcalidad, scrapedserver, scrapedurl in matches:
        title = titulo + "_" + scrapedidioma + "_" + scrapedserver + "_" + scrapedcalidad
        itemlist.append(Item(channel=item.channel, action="play", title=title, fulltitle=title, url=scrapedurl,
                             thumbnail=item.thumbnail, plot=item.plot, show=item.show, fanart=item.fanart))

    return itemlist


def play(item):
    logger.info()

    video = expurl.expand_url(item.url)

    itemlist = []

    itemlist = servertools.find_video_items(data=video)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = item.channel

    return itemlist
