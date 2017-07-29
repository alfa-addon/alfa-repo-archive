# -*- coding: UTF-8 -*-

import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

host = "http://www.cinehindi.com/"


def mainlist(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, action="genero", title="Generos", url=host))
    itemlist.append(Item(channel=item.channel, action="lista", title="Novedades", url=host))
    itemlist.append(Item(channel=item.channel, action="proximas", title="Próximas Películas",
                         url=urlparse.urljoin(host, "proximamente")))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=urlparse.urljoin(host, "?s=")))
    return itemlist


def genero(item):
    logger.info()
    itemlist = list()
    data = httptools.downloadpage(host).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron_generos = '<ul id="menu-submenu" class=""><li id="menu-item-.+?"(.+)<\/li><\/ul>'
    data_generos = scrapertools.find_single_match(data, patron_generos)
    patron = 'class="menu-item menu-item-type-taxonomy menu-item-object-category menu-item-.*?"><a href="(.*?)">(.*?)<\/a><\/li>'
    matches = scrapertools.find_multiple_matches(data_generos, patron)
    for scrapedurl, scrapedtitle in matches:
        if scrapedtitle != 'Próximas Películas':
            itemlist.append(item.clone(action='lista', title=scrapedtitle, url=scrapedurl))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    if texto != '':
        return lista(item)


def proximas(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)  # Eliminamos tabuladores, dobles espacios saltos de linea, etc...
    patron = 'class="item">.*?'  # Todos los items de peliculas (en esta web) empiezan con esto
    patron += '<a href="([^"]+).*?'  # scrapedurl
    patron += '<img src="([^"]+).*?'  # scrapedthumbnail
    patron += 'alt="([^"]+).*?'  # scrapedtitle
    patron += '<span class="player">.+?<span class="year">([^"]+)<\/span>'  # scrapedyear
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedyear in matches:
        if "ver" in scrapedurl:
            scrapedtitle = scrapedtitle + " [" + scrapedyear + "]"
        else:
            scrapedtitle = scrapedtitle + " [" + scrapedyear + "]" + '(Proximamente)'
        itemlist.append(item.clone(title=scrapedtitle, url=scrapedurl, action="findvideos", extra=scrapedtitle,
                                   show=scrapedtitle, thumbnail=scrapedthumbnail, contentType="movie",
                                   context=["buscar_trailer"]))
    # Paginacion
    patron_pag = '<a rel=.+?nofollow.+? class=.+?page larger.+? href=.+?(.+?)proximamente.+?>([^"]+)<\/a>'
    pagina = scrapertools.find_multiple_matches(data, patron_pag)
    for next_page_url, i in pagina:
        if int(i) == 2:
            item.url = next_page_url + 'proximamente/page/' + str(i) + '/'
            itemlist.append(Item(channel=item.channel, action="proximas", title=">> Página siguiente", url=item.url,
                                 thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png'))

    return itemlist


def lista(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)  # Eliminamos tabuladores, dobles espacios saltos de linea, etc...
    patron = 'class="item">.*?'  # Todos los items de peliculas (en esta web) empiezan con esto
    patron += '<a href="([^"]+).*?'  # scrapedurl
    patron += '<img src="([^"]+).*?'  # scrapedthumbnail
    patron += 'alt="([^"]+).*?'  # scrapedtitle
    patron += '<span class="ttx">([^<]+).*?'  # scrapedplot
    patron += '<div class="fixyear">(.*?)</span></div></div>'  # scrapedfixyear

    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot, scrapedfixyear in matches:
        patron = '<span class="year">([^<]+)'  # scrapedyear
        scrapedyear = scrapertools.find_single_match(scrapedfixyear, patron)
        if scrapedyear:
            scrapedtitle += ' (%s)' % (scrapedyear)

        patron = '<span class="calidad2">([^<]+).*?'  # scrapedquality
        scrapedquality = scrapertools.find_single_match(scrapedfixyear, patron)
        if scrapedquality:
            scrapedtitle += ' [%s]' % (scrapedquality)

        itemlist.append(
            item.clone(title=scrapedtitle, url=scrapedurl, plot=scrapedplot, action="findvideos", extra=scrapedtitle,
                       show=scrapedtitle, thumbnail=scrapedthumbnail, contentType="movie", context=["buscar_trailer"]))

    # Paginacion
    patron_genero = '<h1>([^"]+)<\/h1>'
    genero = scrapertools.find_single_match(data, patron_genero)
    if genero == "Romance" or genero == "Drama":
        patron = "<a rel='nofollow' class=previouspostslink' href='([^']+)'>Siguiente "
    else:
        patron = "<span class='current'>.+?href='(.+?)'>"

    next_page_url = scrapertools.find_single_match(data, patron)

    if next_page_url != "":
        item.url = next_page_url
        itemlist.append(Item(channel=item.channel, action="lista", title=">> Página siguiente", url=next_page_url,
                             thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png'))
    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    itemlist.extend(servertools.find_video_items(data=data))
    patron_show = '<div class="data"><h1 itemprop="name">([^<]+)<\/h1>'
    show = scrapertools.find_single_match(data, patron_show)
    for videoitem in itemlist:
        videoitem.channel = item.channel
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                 action="add_pelicula_to_library", extra="findvideos", contentTitle=show))

    return itemlist
