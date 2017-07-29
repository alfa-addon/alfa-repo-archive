# -*- coding: utf-8 -*-

import re

from core import channeltools
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

HOST = 'http://estrenosli.org/'
parameters = channeltools.get_channel_parameters('estrenosgo')
fanart_host = parameters['fanart']
thumbnail_host = parameters['thumbnail']
color1, color2, color3 = ['0xFF58D3F7', '0xFF2E64FE', '0xFF0404B4']


def mainlist(item):
    logger.info()
    itemlist = []
    item.url = HOST
    item.text_color = color2
    item.fanart = fanart_host

    item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/Directors%20Chair.png"
    itemlist.append(item.clone(title="Películas:", folder=False, text_color=color3, text_bold=True))
    itemlist.append(item.clone(title="    Cartelera", action="listado", url=HOST + "descarga-0-58126-0-0-fx-1-1-.fx"))
    itemlist.append(item.clone(title="    DVD-RIP", action="listado", url=HOST + "descarga-0-581210-0-0-fx-1-1.fx"))
    itemlist.append(item.clone(title="    HD-RIP", action="listado", url=HOST + "descarga-0-58128-0-0-fx-1-1-.fx"))

    itemlist.append(item.clone(title="", folder=False, thumbnail=thumbnail_host))

    item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/TV%20Series.png"
    itemlist.append(item.clone(title="Series:", folder=False, text_color=color3, text_bold=True))
    itemlist.append(item.clone(title="    Nuevos episodios", action="listado",
                               url=HOST + "descarga-0-58122-0-0-fx-1-1.fx"))

    return itemlist


def listado(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<div class="MiniFicha">.*?'
    patron += '<img src="([^"]+).*?'
    patron += '<div class="MiniF_TitleSpecial">[^>]+>([^<]+).*?'
    patron += '<b>Categoria:\s*</b>([^&]+)&raquo;\s*([^<]+).*?'
    patron += '<div class="OpcionesDescargasMini">(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for thumbnail, title, cat_padres, cat_hijos, opciones in matches:
        # logger.debug(thumbnail + "\n" + title + "\n" + cat_padres + "\n" + cat_hijos + "\n" + opciones)
        # Obtenemos el año del titulo y eliminamos lo q sobre
        patron = '\d{4}$'
        year = scrapertools.find_single_match(title, patron)
        if year:
            title = re.sub(patron, "", title)
        patron = '\s?-?\s?(line)?\s?-\s?$'
        regex = re.compile(patron, re.I)
        title = regex.sub("", title)

        # Obtenemos la imagen b por q es mayor
        thumbnail = HOST + thumbnail[:-5] + 'b' + thumbnail[-4:]

        # Buscamos opcion de ver online
        patron = '<a href="http://estrenosly.org/ver-online-([^"]+)'
        url_ver = scrapertools.find_single_match(opciones, patron)
        if url_ver:
            new_item = Item(channel=item.channel, action="findvideos", title=title,
                            thumbnail=thumbnail, url=url_ver,
                            infoLabels={"year": year}, text_color=color1)

            cat_padres = cat_padres.strip()
            if cat_padres in ["peliculas-dvdrip", "HDRIP", "cartelera"]:
                # if item.extra == 'movie':
                new_item.contentTitle = title
                new_item.extra = "movie"
                # Filtramos nombres validos para la calidad
                patron = ("rip|dvd|screener|hd|ts|Telesync")
                if re.search(patron, cat_hijos, flags=re.IGNORECASE):
                    new_item.contentQuality = cat_hijos
                    new_item.title = "%s [%s]" % (title, cat_hijos)
                elif cat_padres == "peliculas-dvdrip":
                    new_item.contentQuality = "DVDRIP"
                    new_item.title = "%s [DVDRIP]" % title
                elif cat_padres == "HDRIP":
                    new_item.contentQuality = "HDRIP"
                    new_item.title = "%s [HDRIP]" % title

            elif cat_padres == "series":
                new_item.contentSerieName = cat_hijos
                patron = re.compile('(\d+)x(\d+)')
                matches = patron.findall(title)
                if len(matches) == 1:
                    new_item.contentSeason = matches[0][0]
                    new_item.contentEpisodeNumber = matches[0][1].zfill(2)
                    new_item.extra = "episodie"
                else:
                    # matches == [('1', '01'), ('1', '02'), ('1', '03')]
                    new_item.extra = "multi-episodie"

            else:  # Otras categorias q de momento no nos interesan
                continue

            ''' Opcionalmente podriamos obtener los enlaces torrent y descargas directas
            patron = '<a href="http://estrenosli.org/descarga-directa-([^"]+)'
            new_item.url_descarga = scrapertools.find_single_match(opciones,patron)
            patron = '<a href="http://estrenosli.org/descargar-torrent-([^"]+).*?'
            new_item.url_torrent = scrapertools.find_single_match(opciones,patron)'''

            itemlist.append(new_item)

    if itemlist:
        # Obtenemos los datos basicos de todas las peliculas mediante multihilos
        tmdb.set_infoLabels(itemlist)

        # Si es necesario añadir paginacion
        patron = '<div class="sPages">.*?'
        patron += '<a href="([^"]+)">Siguiente'
        url_next_page = scrapertools.find_single_match(data, patron)
        if url_next_page:
            itemlist.append(Item(channel=item.channel, action="listado", title=">> Página siguiente",
                                 thumbnail=thumbnail_host, url=HOST + url_next_page, folder=True,
                                 text_color=color3, text_bold=True))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    list_opciones = []
    IDIOMAS = {"banderita1": "Español", "banderita2": "VOSE", "banderita3": "Latino"}

    url = "http://estrenosli.org/ver-online-" + item.url

    data = httptools.downloadpage(url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<div class="content"><a href="([^"]+).*?'
    patron += '<div class="content_mini"><span class="([^"]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, banderita in matches:
        idioma = ""
        if banderita in IDIOMAS:
            idioma = " [%s]" % IDIOMAS[banderita]

        data = httptools.downloadpage(url).data
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

        if item.extra == 'multi-episodie':
            patron = '<div class="linksDescarga"><span class="titulo">Video Online:([^<]+).*?<a href="([^"]+)'
            matches = re.compile(patron, re.DOTALL).findall(data)
            for capitulo, url in matches:
                s = servertools.findvideos(url, skip=True)
                if s:
                    itemlist.append(item.clone(url=s[0][1], action="play", folder=False, server=s[0][2],
                                               title="Ver %s en %s%s" % (
                                               capitulo.strip(), s[0][2].capitalize(), idioma),
                                               thumbnail2=item.thumbnail,
                                               thumbnail=config.get_thumb("server_" + s[0][2] + ".png")))
        else:
            for s in servertools.findvideos(data):
                itemlist.append(item.clone(url=s[1], action="play", folder=False, server=s[2],
                                           title="Ver en %s%s" % (s[2].capitalize(), idioma),
                                           thumbnail2=item.thumbnail,
                                           thumbnail=config.get_thumb("server_" + s[2] + ".png")))

    # Insertar items "Buscar trailer" y "Añadir a la videoteca"
    if itemlist and item.extra == "movie":
        if item.contentQuality:
            title = "%s [%s]" % (item.contentTitle, item.contentQuality)
        else:
            title = item.contentTitle

        itemlist.insert(0, item.clone(channel="trailertools", action="buscartrailer",
                                      text_color=color3, title=title, viewmode="list"))

        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir película a la videoteca",
                                 action="add_pelicula_to_library", url=item.url, text_color="green",
                                 contentTitle=item.contentTitle, extra="library", thumbnail=thumbnail_host))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    # Cambiamos el thumbnail del server por el de la pelicula
    itemlist.append(item.clone(thumbnail=item.thumbnail2))

    return itemlist
