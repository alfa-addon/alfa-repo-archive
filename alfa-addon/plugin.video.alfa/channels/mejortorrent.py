# -*- coding: utf-8 -*-

import os
import re
import sys
import urllib
import urlparse

from channelselector import get_thumbnail_path
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import Tmdb

host = "http://www.mejortorrent.com"


def mainlist(item):
    logger.info()

    itemlist = []

    thumb_pelis = get_thumbnail("thumb_channels_movie.png")
    thumb_pelis_hd = get_thumbnail("thumb_channels_movie_hd.png")
    thumb_series = get_thumbnail("thumb_channels_tvshow.png")
    thumb_series_hd = get_thumbnail("thumb_channels_tvshow_hd.png")
    thumb_series_az = get_thumbnail("thumb_channels_tvshow_az.png")
    thumb_docus = get_thumbnail("thumb_channels_documentary.png")
    thumb_buscar = get_thumbnail("thumb_search.png")

    itemlist.append(Item(channel=item.channel, title="Peliculas", action="getlist",
                         url="http://www.mejortorrent.com/torrents-de-peliculas.html", thumbnail=thumb_pelis))
    itemlist.append(Item(channel=item.channel, title="Peliculas HD", action="getlist",
                         url="http://www.mejortorrent.com/torrents-de-peliculas-hd-alta-definicion.html",
                         thumbnail=thumb_pelis_hd))
    itemlist.append(Item(channel=item.channel, title="Series", action="getlist",
                         url="http://www.mejortorrent.com/torrents-de-series.html", thumbnail=thumb_series))
    itemlist.append(Item(channel=item.channel, title="Series HD", action="getlist",
                         url="http://www.mejortorrent.com/torrents-de-series-hd-alta-definicion.html",
                         thumbnail=thumb_series_hd))
    itemlist.append(Item(channel=item.channel, title="Series Listado Alfabetico", action="listalfabetico",
                         url="http://www.mejortorrent.com/torrents-de-series.html", thumbnail=thumb_series_az))
    itemlist.append(Item(channel=item.channel, title="Documentales", action="getlist",
                         url="http://www.mejortorrent.com/torrents-de-documentales.html", thumbnail=thumb_docus))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", thumbnail=thumb_buscar))

    return itemlist


def listalfabetico(item):
    logger.info()

    itemlist = []

    for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                  'U', 'V', 'W', 'X', 'Y', 'Z']:
        itemlist.append(Item(channel=item.channel, action="getlist", title=letra,
                             url="http://www.mejortorrent.com/series-letra-" + letra.lower() + ".html"))

    itemlist.append(Item(channel=item.channel, action="getlist", title="Todas",
                         url="http://www.mejortorrent.com/series-letra..html"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")

    item.url = "http://www.mejortorrent.com/secciones.php?sec=buscador&valor=%s" % (texto)
    try:
        return buscador(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def buscador(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # pelis
    # <a href="/peli-descargar-torrent-9578-Presentimientos.html">
    # <img src="/uploads/imagenes/peliculas/Presentimientos.jpg" border="1"></a
    #
    # series
    #
    # <a href="/serie-descargar-torrents-11589-11590-Ahora-o-nunca-4-Temporada.html">
    # <img src="/uploads/imagenes/series/Ahora o nunca4.jpg" border="1"></a>
    #
    # docs
    #
    # <a href="/doc-descargar-torrent-1406-1407-El-sueno-de-todos.html">
    # <img border="1" src="/uploads/imagenes/documentales/El sueno de todos.jpg"></a>

    # busca series
    patron = "<a href='(/serie-descargar-torrent[^']+)'[^>]+>(.*?)</a>"
    patron += ".*?<span style='color:gray;'>([^']+)</span>"
    patron_enlace = "/serie-descargar-torrents-\d+-\d+-(.*?)\.html"

    matches = scrapertools.find_multiple_matches(data, patron)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedinfo in matches:
        title = scrapertools.remove_htmltags(scrapedtitle).decode('iso-8859-1').encode(
            'utf8') + ' ' + scrapedinfo.decode('iso-8859-1').encode('utf8')
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "]")

        itemlist.append(
            Item(channel=item.channel, action="episodios", title=title, url=url, folder=True, extra="series",
                 viewmode="movie_with_plot"))

    # busca pelis
    patron = "<a href='(/peli-descargar-torrent-[^']+)'[^>]+>(.*?)</a>"
    patron_enlace = "/peli-descargar-torrent-\d+(.*?)\.html"

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.remove_htmltags(scrapedtitle).decode('iso-8859-1').encode('utf-8')
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "]")

        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, folder=False, extra=""))

    # busca docu
    patron = "<a href='(/doc-descargar-torrent[^']+)' .*?"
    patron += "<font Color='darkblue'>(.*?)</font>.*?"
    patron += "<td align='right' width='20%'>(.*?)</td>"
    patron_enlace = "/doc-descargar-torrent-\d+-\d+-(.*?)\.html"

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedinfo in matches:
        title = scrapedtitle.decode('iso-8859-1').encode('utf8') + " " + scrapedinfo.decode('iso-8859-1').encode('utf8')
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "]")

        itemlist.append(Item(channel=item.channel, action="episodios",
                             title=title, url=url, folder=True, extra="docu",
                             viewmode="movie_with_plot"))

    return itemlist


def getlist(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # pelis
    # <a href="/peli-descargar-torrent-9578-Presentimientos.html">
    # <img src="/uploads/imagenes/peliculas/Presentimientos.jpg" border="1"></a
    #
    # series
    #
    # <a href="/serie-descargar-torrents-11589-11590-Ahora-o-nunca-4-Temporada.html">
    # <img src="/uploads/imagenes/series/Ahora o nunca4.jpg" border="1"></a>
    #
    # docs
    #
    # <a href="/doc-descargar-torrent-1406-1407-El-sueno-de-todos.html">
    # <img border="1" src="/uploads/imagenes/documentales/El sueno de todos.jpg"></a>

    if item.url.find("peliculas") > -1:
        patron = '<a href="(/peli-descargar-torrent[^"]+)">[^<]+'
        patron += '<img src="([^"]+)"[^<]+</a>'
        patron_enlace = "/peli-descargar-torrent-\d+(.*?)\.html"
        patron_title = '<a href="/peli-descargar-torrent[^"]+">([^<]+)</a>(\s*<b>([^>]+)</b>)?'
        action = "show_movie_info"
        folder = True
        extra = ""
    elif item.url.find("series-letra") > -1:
        patron = "<a href='(/serie-descargar-torrent[^']+)'>()"
        patron_enlace = "/serie-descargar-torrents-\d+-\d+-(.*?)\.html"
        patron_title = '<a href="/serie-descargar-torrent[^"]+">([^<]+)</a>(\s*<b>([^>]+)</b>)?'
        action = "episodios"
        folder = True
        extra = "series"
    elif item.url.find("series") > -1:
        patron = '<a href="(/serie-descargar-torrent[^"]+)">[^<]+'
        patron += '<img src="([^"]+)"[^<]+</a>'
        patron_enlace = "/serie-descargar-torrents-\d+-\d+-(.*?)\.html"
        patron_title = '<a href="/serie-descargar-torrent[^"]+">([^<]+)</a>(\s*<b>([^>]+)</b>)?'
        action = "episodios"
        folder = True
        extra = "series"
    else:
        patron = '<a href="(/doc-descargar-torrent[^"]+)">[^<]+'
        patron += '<img src="([^"]+)"[^<]+</a>'
        patron_enlace = "/doc-descargar-torrent-\d+-\d+-(.*?)\.html"
        patron_title = '<a href="/doc-descargar-torrent[^"]+">([^<]+)</a>(\s*<b>([^>]+)</b>)?'
        action = "episodios"
        folder = True
        extra = "docus"

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail in matches:
        title = scrapertools.get_match(scrapedurl, patron_enlace)
        title = title.replace("-", " ")
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, urllib.quote(scrapedthumbnail))
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail, plot=plot,
                             folder=folder, extra=extra))

    matches = re.compile(patron_title, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    # Cambia el título sacado de la URL por un título con más información.
    # esta implementación asume que va a encontrar las mismas coincidencias
    # que en el bucle anterior, lo cual técnicamente es erróneo, pero que
    # funciona mientras no cambien el formato de la página
    cnt = 0
    for scrapedtitle, notused, scrapedinfo in matches:
        title = re.sub('\r\n', '', scrapedtitle).decode('iso-8859-1').encode('utf8').strip()
        if title.endswith('.'):
            title = title[:-1]

        info = scrapedinfo.decode('iso-8859-1').encode('utf8')
        if info != "":
            title = '{0} {1}'.format(title, info)

        itemlist[cnt].title = title
        cnt += 1
        if cnt == len(itemlist) - 1:
            break

    if len(itemlist) == 0:
        itemlist.append(Item(channel=item.channel, action="mainlist", title="No se ha podido cargar el listado"))
    else:
        # Extrae el paginador
        patronvideos = "<a href='([^']+)' class='paginar'> Siguiente >>"
        matches = re.compile(patronvideos, re.DOTALL).findall(data)
        scrapertools.printMatches(matches)

        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, matches[0])
            itemlist.append(
                Item(channel=item.channel, action="getlist", title="Pagina siguiente >>", url=scrapedurl, folder=True))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    total_capis = scrapertools.get_match(data, "<input type='hidden' name='total_capis' value='(\d+)'>")
    tabla = scrapertools.get_match(data, "<input type='hidden' name='tabla' value='([^']+)'>")
    titulo = scrapertools.get_match(data, "<input type='hidden' name='titulo' value='([^']+)'>")

    item.thumbnail = scrapertools.find_single_match(data,
                                                    "src='http://www\.mejortorrent\.com(/uploads/imagenes/" + tabla + "/[a-zA-Z0-9_ ]+.jpg)'")
    item.thumbnail = 'http://www.mejortorrent.com' + urllib.quote(item.thumbnail)

    # <form name='episodios' action='secciones.php?sec=descargas&ap=contar_varios' method='post'>
    data = scrapertools.get_match(data,
                                  "<form name='episodios' action='secciones.php\?sec=descargas\&ap=contar_varios' method='post'>(.*?)</form>")
    '''
        <td bgcolor='#C8DAC8' style='border-bottom:1px solid black;'><a href='/serie-episodio-descargar-torrent-18741-Juego-de-tronos-4x01.html'>4x01 - Episodio en V.O. Sub Esp.</a></td>
        <td width='120' bgcolor='#C8DAC8' align='right' style='border-right:1px solid black; border-bottom:1px solid black;'><div style='color:#666666; font-size:9px; margin-right:5px;'>Fecha: 2014-04-07</div></td>
        <td width='60' bgcolor='#F1F1F1' align='center' style='border-bottom:1px solid black;'>
        <input type='checkbox' name='episodios[1]' value='18741'>
        '''

    if item.extra == "series":
        patron = "<td bgcolor[^>]+><a[^>]+>([^>]+)</a></td>[^<]+"
    else:
        patron = "<td bgcolor[^>]+>([^>]+)</td>[^<]+"

    patron += "<td[^<]+<div[^>]+>Fecha: ([^<]+)</div></td>[^<]+"
    patron += "<td[^<]+"
    patron += "<input type='checkbox' name='([^']+)' value='([^']+)'"

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    tmdb_title = re.sub(r'(\s*-\s*)?\d+.*?\s*Temporada|(\s*-\s*)?\s*Miniserie\.?|\(.*\)|\[.*\]', '', item.title).strip()
    logger.debug('tmdb_title=' + tmdb_title)

    if item.extra == "series":
        oTmdb = Tmdb(texto_buscado=tmdb_title.strip(), tipo='tv', idioma_busqueda="es")
    else:
        oTmdb = Tmdb(texto_buscado=tmdb_title.strip(), idioma_busqueda="es")

    for scrapedtitle, fecha, name, value in matches:
        scrapedtitle = scrapedtitle.strip()
        if scrapedtitle.endswith('.'):
            scrapedtitle = scrapedtitle[:-1]

        title = scrapedtitle + " (" + fecha + ")"

        url = "http://www.mejortorrent.com/secciones.php?sec=descargas&ap=contar_varios"
        # "episodios%5B1%5D=11744&total_capis=5&tabla=series&titulo=Sea+Patrol+-+2%AA+Temporada"
        post = urllib.urlencode({name: value, "total_capis": total_capis, "tabla": tabla, "titulo": titulo})
        logger.debug("post=" + post)

        if item.extra == "series":
            epi = scrapedtitle.split("x")

            # Sólo comprobar Tmdb si el formato es temporadaXcapitulo
            if len(epi) > 1:
                temporada = re.sub("\D", "", epi[0])
                capitulo = re.search("\d+", epi[1])
                if capitulo:
                    capitulo = capitulo.group()
                else:
                    capitulo = 1

                epi_data = oTmdb.get_episodio(temporada, capitulo)
                logger.debug("epi_data=" + str(epi_data))

                if epi_data:
                    item.thumbnail = epi_data["temporada_poster"]
                    item.fanart = epi_data["episodio_imagen"]
                    item.plot = epi_data["episodio_sinopsis"]
                    epi_title = epi_data["episodio_titulo"]
                    if epi_title != "":
                        title = scrapedtitle + " " + epi_title + " (" + fecha + ")"
        else:
            try:
                item.fanart = oTmdb.get_backdrop()
            except:
                pass

            item.plot = oTmdb.get_sinopsis()

        logger.debug("title=[" + title + "], url=[" + url + "], item=[" + str(item) + "]")

        itemlist.append(
            Item(channel=item.channel, action="play", title=title, url=url, thumbnail=item.thumbnail, plot=item.plot,
                 fanart=item.fanart, extra=post, folder=False))

    return itemlist


def show_movie_info(item):
    logger.info()

    itemlist = []

    tmdb_title = re.sub(r'\(.*\)|\[.*\]', '', item.title).strip()
    logger.debug('tmdb_title=' + tmdb_title)

    try:
        oTmdb = Tmdb(texto_buscado=tmdb_title, idioma_busqueda="es")
        item.fanart = oTmdb.get_backdrop()
        item.plot = oTmdb.get_sinopsis()
    except:
        pass

    data = httptools.downloadpage(item.url).data
    logger.debug("data=" + data)

    patron = "<a href='(secciones.php\?sec\=descargas[^']+)'"
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + item.title + "], url=[" + url + "], thumbnail=[" + item.thumbnail + "]")

        torrent_data = httptools.downloadpage(url).data
        logger.debug("torrent_data=" + torrent_data)
        # <a href='/uploads/torrents/peliculas/los-juegos-del-hambre-brrip.torrent'>
        link = scrapertools.get_match(torrent_data, "<a href='(/uploads/torrents/peliculas/.*?\.torrent)'>")
        link = urlparse.urljoin(url, link)

        logger.debug("link=" + link)

        itemlist.append(Item(channel=item.channel, action="play", server="torrent", title=item.title, url=link,
                             thumbnail=item.thumbnail, plot=item.plot, fanart=item.fanart, folder=False))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.extra == "":
        itemlist.append(Item(channel=item.channel, action="play", server="torrent", title=item.title, url=item.url,
                             thumbnail=item.thumbnail, plot=item.plot, fanart=item.fanart, folder=False))

    else:
        data = httptools.downloadpage(item.url, post=item.extra).data
        logger.debug("data=" + data)

        # series
        #
        # <a href="http://www.mejortorrent.com/uploads/torrents/series/falling-skies-2-01_02.torrent"
        # <a href="http://www.mejortorrent.com/uploads/torrents/series/falling-skies-2-03.torrent"
        #
        # docus
        #
        # <a href="http://www.mejortorrent.com/uploads/torrents/documentales/En_Suenyos_De_Todos_DVDrip.torrent">El sueo de todos. </a>

        params = dict(urlparse.parse_qsl(item.extra))

        patron = '<a href="(http://www.mejortorrent.com/uploads/torrents/' + params["tabla"] + '/.*?\.torrent)"'

        link = scrapertools.get_match(data, patron)

        logger.info("link=" + link)

        itemlist.append(Item(channel=item.channel, action="play", server="torrent", title=item.title, url=link,
                             thumbnail=item.thumbnail, plot=item.plot, folder=False))

    return itemlist


def get_thumbnail(thumb_name=None):
    img_path = config.get_runtime_path() + '/resources/images/squares'

    if thumb_name:
        file_path = os.path.join(img_path, thumb_name)
        if os.path.isfile(file_path):
            thumb_path = file_path
        else:
            thumb_path = urlparse.urljoin(get_thumbnail_path(), thumb_name)
    else:
        thumb_path = urlparse.urljoin(get_thumbnail_path(), thumb_name)

    return thumb_path
