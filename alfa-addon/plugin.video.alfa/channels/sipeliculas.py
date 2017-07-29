# -*- coding: utf-8 -*-

import re
import urlparse

from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

host = 'http://www.sipeliculas.com'


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(item.clone(title="Novedades", action="lista", url=host + "/cartelera/"))
    itemlist.append(item.clone(title="Actualizadas", action="lista", url=host + "/peliculas-actualizadas/"))
    itemlist.append(item.clone(title="Recomendadas", action="lista", url=host + "/peliculas-recomendadas/"))
    itemlist.append(item.clone(title="Categorias", action="menuseccion", url=host, extra="/online/"))
    itemlist.append(item.clone(title="Año", action="menuseccion", url=host, extra="/estrenos-gratis/"))
    itemlist.append(item.clone(title="Alfabetico", action="alfabetica", url=host + '/mirar/'))
    itemlist.append(item.clone(title="Buscar", action="search", url=host + "/ver/"))

    return itemlist


def alfabetica(item):
    logger.info()
    itemlist = []
    for letra in "1abcdefghijklmnopqrstuvwxyz":
        itemlist.append(item.clone(title=letra.upper(), url=item.url + letra, action="lista"))

    return itemlist


def menuseccion(item):
    logger.info()
    itemlist = []
    seccion = item.extra
    data = httptools.downloadpage(item.url).data

    if seccion == '/online/':
        data = scrapertools.find_single_match(data,
                                              '<h2 class="[^"]+"><i class="[^"]+"></i>Películas por géneros<u class="[^"]+"></u></h2>(.*?)<ul class="abc">')
        patron = '<li ><a href="([^"]+)" title="[^"]+"><i class="[^"]+"></i>([^<]+)</a></li>'
    elif seccion == '/estrenos-gratis/':
        data = scrapertools.find_single_match(data, '<ul class="lista-anio" id="lista-anio">(.*?)</ul>')
        patron = '<li ><a href="([^"]+)" title="[^"]+">([^<]+)</a></li>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, extra in matches:
        itemlist.append(Item(channel=item.channel, action='lista', title=extra, url=scrapedurl))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    # data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>', "", data)

    listado = scrapertools.find_single_match(data,
                                             '<div id="sipeliculas" class="borde"><div class="izquierda">(.*?)<div class="derecha"><h2')
    logger.info('vergas' + listado)
    patron = '<li class="[^"]+"><a class="[^"]+" href="([^"]+)" title="Ver Película([^"]+)"><i></i><img.*?src="([^"]+)" alt="[^"]+"/>(.*?)</li>'
    matches = re.compile(patron, re.DOTALL).findall(listado)
    for scrapedurl, scrapedtitle, scrapedthumbnail, dataplot in matches:
        dataplot = scrapertools.find_single_match(data, '<div class="ttip"><h5>[^<]+</h5><p><span>([^<]+)</span>')
        itemlist.append(Item(channel=item.channel, action='findvideos', title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=dataplot, contentTitle=scrapedtitle, extra=item.extra))

    # Paginacion
    if itemlist != []:
        patron = '<li[^<]+<a href="([^"]+)" title="[^"]+">Siguiente[^<]+</a></li>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if matches:
            itemlist.append(
                item.clone(title="Pagina Siguiente", action='lista', url=urlparse.urljoin(host, matches[0])))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = item.url + texto
    if texto != '':
        return lista(item)
    else:
        return []


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    # data = re.sub(r"'|\n|\r|\t|&nbsp;|<br>", "", data)

    listado1 = scrapertools.find_single_match(data,
                                              '<div class="links" id="ver-mas-opciones"><h2 class="h2"><i class="[^"]+"></i>[^<]+</h2><ul class="opciones">(.*?)</ul>')
    patron1 = '<li ><a id="([^"]+)" rel="nofollow" href="([^"]+)" title="[^"]+" alt="([^"]+)"><span class="opcion"><i class="[^"]+"></i><u>[^<]+</u>[^<]+</span><span class="ico"><img src="[^"]+" alt="[^"]+"/>[^<]+</span><span>([^"]+)</span><span>([^"]+)</span></a></li>'
    matches = matches = re.compile(patron1, re.DOTALL).findall(listado1)
    for vidId, vidUrl, vidServer, idioma, calidad in matches:
        itemlist.append(Item(channel=item.channel, action='play', url=vidUrl, extra=vidId,
                             title='Ver en ' + vidServer + ' | ' + idioma + ' | ' + calidad, thumbnail=item.thumbnail))

    listado2 = scrapertools.find_single_match(data, '<ul class="opciones-tab">(.*?)</ul>')
    patron2 = '<li ><a id="([^"]+)" rel="nofollow" href="([^"]+)" title="[^"]+" alt="([^"]+)"><img src="[^"]+" alt="[^"]+"/>[^<]+</a></li>'
    matches = matches = re.compile(patron2, re.DOTALL).findall(listado2)
    for vidId, vidUrl, vidServer in matches:
        itemlist.append(Item(channel=item.channel, action='play', url=vidUrl, extra=vidId, title='Ver en ' + vidServer,
                             thumbnail=item.thumbnail))

    for videoitem in itemlist:
        videoitem.fulltitle = item.title
        videoitem.folder = False

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    video = httptools.downloadpage(host + '/ajax.public.php', 'acc=ver_opc&f=' + item.extra).data
    logger.info("video=" + video)
    enlaces = servertools.findvideos(video)
    if enlaces:
        logger.info("server=" + enlaces[0][2])
        thumbnail = servertools.guess_server_thumbnail(video)
        # Añade al listado de XBMC
        itemlist.append(
            Item(channel=item.channel, action="play", title=item.title, fulltitle=item.fulltitle, url=enlaces[0][1],
                 server=enlaces[0][2], thumbnail=thumbnail, folder=False))

    return itemlist
