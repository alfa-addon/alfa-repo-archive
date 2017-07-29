# -*- coding: utf-8 -*-

import re
import urlparse

from channels import renumbertools
from channelselector import get_thumb
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import tmdb
from core.item import Item

host = "https://seriesmeme.com/"


def mainlist(item):
    logger.info()

    thumb_series = get_thumb("thumb_channels_tvshow.png")

    thumb_series_az = get_thumb("thumb_channels_tvshow_az.png")

    itemlist = list()

    itemlist.append(Item(channel=item.channel, action="lista_gen", title="Novedades", url=host,
                         thumbnail=thumb_series))
    itemlist.append(Item(channel=item.channel, action="lista", title="Series", url=urlparse.urljoin(host, "/lista"),
                         thumbnail=thumb_series))
    itemlist.append(Item(channel=item.channel, action="categorias", title="Categorias", url=host,
                         thumbnail=thumb_series))
    itemlist.append(Item(channel=item.channel, action="alfabetico", title="Listado Alfabetico", url=host,
                         thumbnail=thumb_series_az))
    itemlist.append(Item(channel=item.channel, action="top", title="Top Series", url=host,
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


def categorias(item):
    logger.info()
    dict_gender = {"acción": "accion", "animes": "animacion", "aventuras": "aventura", "dibujos": "animacion",
                   "ciencia ficción": "ciencia%20ficcion", "intriga": "misterio", "suspenso": "suspense",
                   "thriller": "suspense", "fantástico": "fantasia"}
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron_cat = '<li id="menu-item-15068" class=".+?"><.+?>.+?<\/a>(.+?)<\/ul><\/li>'
    categorias = scrapertools.find_single_match(data, patron_cat)
    patron = '<li id="menu-item-.+?" class=".+?"><a href="([^"]+)">([^"]+)<\/a><\/li>'
    matches = scrapertools.find_multiple_matches(categorias, patron)
    for link, name in matches:
        if 'Género' in name:
            title = name.replace('Género ', '')
        url = link
        thumbnail = "https://raw.githubusercontent.com/master-1970/resources/master/images/genres/4/azul/%s.png"
        thumbnail = thumbnail % dict_gender.get(title.lower(), title.lower())
        itemlist.append(item.clone(title=title, url=url, plot=title, action="lista_gen", thumbnail=thumbnail))
    return itemlist


def alfabetico(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron_alf1 = '<li id="menu-item-15069" class=".+?"><.+?>.+?<\/a>(.+?)<\/ul><\/li>'
    patron_alf2 = '<li id="menu-item-15099" class=".+?"><.+?>.+?<\/a>(.+?)<\/ul><\/li>'
    alfabeto1 = scrapertools.find_single_match(data, patron_alf1)
    alfabeto2 = scrapertools.find_single_match(data, patron_alf2)
    alfabeto = alfabeto1 + alfabeto2
    patron = '<li id="menu-item-.+?" class=".+?"><a href="([^"]+)">([^"]+)<\/a><\/li>'
    matches = scrapertools.find_multiple_matches(alfabeto, patron)
    for link, name in matches:
        title = name
        url = link
        itemlist.append(item.clone(title=title, url=url, plot=title, action="lista_gen"))
    return itemlist


def top(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron_top = '<li id="menu-item-15087" class=".+?"><.+?>.+?<\/a>(.+?)<\/ul><\/li>'
    top = scrapertools.find_single_match(data, patron_top)
    patron = '<a href="([^"]+)">([^"]+)<\/a>'
    matches = scrapertools.find_multiple_matches(top, patron)
    for link, name in matches:
        title = name
        url = link
        itemlist.append(item.clone(title=title, url=url, plot=title, action="lista_gen", show=title))
    tmdb.set_infoLabels(itemlist)
    return itemlist


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
    patron = '<li><strong><a href="([^"]+)">([^"]+)<\/a>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for link, name in matches:
        title = name
        url = link
        itemlist.append(item.clone(title=title, url=url, plot=title, action="episodios"))
    return itemlist


def episodios(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron_caps = '<li><strong><a href="([^"]+)">(.+?)&#8211;(.+?)<\/a>'
    matches = scrapertools.find_multiple_matches(data, patron_caps)
    show = scrapertools.find_single_match(data, '<h3><strong>.+?de (.+?)<\/strong>')
    scrapedplot = scrapertools.find_single_match(data, '<strong>Sinopsis<\/strong><strong>([^"]+)<\/strong><\/pre>')
    logger.info("epibla   " + data)
    for link, cap, name in matches:
        if 'x' in cap:
            title = cap + " - " + name
        else:
            season = 1
            episode = int(cap)
            season, episode = renumbertools.numbered_for_tratk(
                item.channel, item.show, season, episode)
            date = name
            title = "{0}x{1:02d} {2} ({3})".format(
                season, episode, "Episodio " + str(episode), date)
        # title = cap+" - "+name
        url = link
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=item.thumbnail,
                             plot=scrapedplot, show=show))

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", url=item.url,

                             action="add_serie_to_library", extra="episodios", show=show))

    return itemlist
