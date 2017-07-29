# -*- coding: utf-8 -*-

import os
import re
import ssl
from threading import Thread

import xbmc
import xbmcgui
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from core.scrapertools import decodeHtmlentities as dhe

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

ACTION_SHOW_FULLSCREEN = 36
ACTION_GESTURE_SWIPE_LEFT = 511
ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_DOWN = 4
ACTION_MOVE_UP = 3
OPTION_PANEL = 6
OPTIONS_OK = 5

__modo_grafico__ = config.get_setting('modo_grafico', "borrachodetorrent")


# Para la busqueda en bing evitando baneos

def browser(url):
    import mechanize

    # Utilizamos Browser mechanize para saltar problemas con la busqueda en bing
    br = mechanize.Browser()
    # Browser options
    br.set_handle_equiv(False)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(False)
    br.set_handle_robots(False)
    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    # Want debugging messages?
    # br.set_debug_http(True)
    # br.set_debug_redirects(True)
    # br.set_debug_responses(True)

    # User-Agent (this is cheating, ok?)
    # br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/7.1.7 Safari/537.85.16')]
    # br.addheaders =[('Cookie','SRCHD=AF=QBRE; domain=.bing.com; expires=25 de febrero de 2018 13:00:28 GMT+1; MUIDB=3B942052D204686335322894D3086911; domain=www.bing.com;expires=24 de febrero de 2018 13:00:28 GMT+1')]
    # Open some site, let's pick a random one, the first that pops in mind
    r = br.open(url)
    response = r.read()
    print response
    if "img,divreturn" in response:
        r = br.open("http://ssl-proxy.my-addr.org/myaddrproxy.php/" + url)
        print "prooooxy"
        response = r.read()

    return response


api_key = "2e2160006592024ba87ccdf78c28f49f"
api_fankey = "dffe90fba4d02c199ae7a9e71330c987"


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="[COLOR floralwhite][B]Películas[/B][/COLOR]", action="scraper",
                               url="https://www.borrachodetorrent.com/peliculas-torrent/",
                               thumbnail="http://imgur.com/tBvoGIk.png", fanart="http://imgur.com/AqUvMW3.jpg",
                               contentType="movie"))
    itemlist.append(item.clone(title="[COLOR floralwhite][B]      Estrenos[/B][/COLOR]", action="scraper",
                               url="https://www.borrachodetorrent.com/peliculas-estrenos-torrent/",
                               thumbnail="http://imgur.com/tBvoGIk.png", fanart="http://imgur.com/AqUvMW3.jpg",
                               contentType="movie"))
    itemlist.append(item.clone(title="[COLOR floralwhite][B]      Esenciales[/B][/COLOR]", action="scraper",
                               url="https://www.borrachodetorrent.com/peliculas-torrent-deberias-haber-visto/",
                               thumbnail="http://imgur.com/tBvoGIk.png", fanart="http://imgur.com/AqUvMW3.jpg",
                               contentType="movie"))

    itemlist.append(itemlist[-1].clone(title="[COLOR floralwhite][B]Series[/B][/COLOR]", action="scraper",
                                       url="https://www.borrachodetorrent.com/series-torrent/",
                                       thumbnail="http://imgur.com/lMHcNwc.png", contentType="tvshow"))

    itemlist.append(itemlist[-1].clone(title="[COLOR cadetblue][B]Buscar[/B][/COLOR]", action="search",
                                       thumbnail="http://imgur.com/NrIVpps.png",
                                       fanart="http://imgur.com/AqUvMW3.jpg", ))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "https://www.borrachodetorrent.com/?s=" + texto
    item.extra = "search"
    try:
        return buscador(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def buscador(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = scrapertools.find_multiple_matches(data,
                                                '<a id="busca_a" class="busca_a" href="([^"]+)">.*?<img src="([^"]+)".*?<span class="tt">([^"]+)</span>(.*?)<span class="calidad2">([^"]+)</span>')

    for url, thumb, title, check_year, calidad in patron:

        if "SERIE" in calidad or "&#" in title:
            if "&#" in title:
                item.extra = ""

            checkmt = "tvshow"

        else:
            checkmt = "movie"
        year = scrapertools.find_single_match(check_year, '<span class="year_SKA">([^"]+)</span>')
        if year == "":
            year = "  "
        titulo = "[COLOR teal]" + title + "[/COLOR]" + " " + "[COLOR floralwhite]" + calidad + "[/COLOR]"
        title = re.sub(r"!|¡", "", title)
        title = re.sub(r"&#8217;|PRE-Estreno|\d+&#.*", "'", title)

        if checkmt == "movie":
            new_item = item.clone(action="findvideos", title=titulo, url=url, thumbnail=thumb, fulltitle=title,
                                  contentTitle=title, contentType="movie", extra=year, library=True)
        else:
            if item.extra == "search":
                new_item = item.clone(action="findtemporadas", title=titulo, url=url, thumbnail=thumb, fulltitle=title,
                                      contentTitle=title, show=title, contentType="tvshow", library=True)
            else:
                new_item = item.clone(action="findvideos", title=titulo, url=url, thumbnail=thumb, fulltitle=title,
                                      contentTitle=title, show=title, contentType="tvshow", library=True)
        new_item.infoLabels['year'] = year
        itemlist.append(new_item)

    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
        for item in itemlist:
            if not "Siguiente >>" in item.title:
                if "0." in str(item.infoLabels['rating']):
                    item.infoLabels['rating'] = "[COLOR indianred]Sin puntuacíon[/COLOR]"
                else:
                    item.infoLabels['rating'] = "[COLOR springgreen]" + str(item.infoLabels['rating']) + "[/COLOR]"
                item.title = item.title + "  " + str(item.infoLabels['rating'])
    except:
        pass

    return itemlist


def scraper(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    if item.contentType == "movie":
        patron = scrapertools.find_multiple_matches(data,
                                                    '<a id="busca_a" class="busca_a" href="([^"]+)">.*?<img src="([^"]+)".*?<span class="tt">([^"]+)</span>(.*?)<span class="calidad2">([^"]+)</span>')

        for url, thumb, title, check_year, calidad in patron:

            year = scrapertools.find_single_match(check_year, '<span class="year_SKA">([^"]+)</span>')
            if year == "":
                year = "  "

            titulo = "[COLOR teal]" + title + "[/COLOR]" + "  " + "[COLOR floralwhite]" + calidad + "[/COLOR]"
            title = re.sub(r"!|¡", "", title)
            title = re.sub(r"&#8217;|PRE-Estreno", "'", title)

            new_item = item.clone(action="findvideos", title=titulo, url=url, thumbnail=thumb, fulltitle=title,
                                  contentTitle=title, contentType="movie", extra=year, library=True)
            new_item.infoLabels['year'] = year
            itemlist.append(new_item)

    else:

        data = re.sub(r'&#215;', 'x', data)
        patron = scrapertools.find_multiple_matches(data,
                                                    'id="busca_a" class="busca_a" href="([^"]+)">.*?<img src="([^"]+)".*?<span class="tt">([^"]+)</span>.*?<span class="calidad2">([^"]+)</span>')

        for url, thumb, title, calidad in patron:
            titulo = "[COLOR teal]" + title + "[/COLOR]" + " " + "[COLOR floralwhite]" + calidad + "[/COLOR]"
            title = re.sub(r'\d+x\d+', '', title)
            title = re.sub(r"&#8217;", "'", title)
            filtro_thumb = thumb.replace("https://image.tmdb.org/t/p/w300", "")
            filtro_list = {"poster_path": filtro_thumb}
            filtro_list = filtro_list.items()

            new_item = item.clone(action="findvideos", title=titulo, url=url, thumbnail=thumb,
                                  fulltitle=title, infoLabels={'filtro': filtro_list},
                                  contentTitle=title, show=title, contentType="tvshow", library=True)
            itemlist.append(new_item)

    ## Paginación
    next = scrapertools.find_single_match(data, "<div class='paginado'>.*?<a class='current'>.*?href='([^']+)'")
    if len(next) > 0:
        url = next

        itemlist.append(item.clone(title="[COLOR dodgerblue][B]Siguiente >>[/B][/COLOR]", url=url))
    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
        for item in itemlist:
            if not "Siguiente >>" in item.title:
                if "0." in str(item.infoLabels['rating']):
                    item.infoLabels['rating'] = "[COLOR indianred]Sin puntuacíon[/COLOR]"
                else:
                    item.infoLabels['rating'] = "[COLOR springgreen]" + str(item.infoLabels['rating']) + "[/COLOR]"
                item.title = item.title + "  " + str(item.infoLabels['rating'])
    except:
        pass

    for item_tmdb in itemlist:
        logger.info(str(item_tmdb.infoLabels['tmdb_id']))

    return itemlist


def findtemporadas(item):
    logger.info()
    itemlist = []
    if item.extra == "search":
        th = Thread(target=get_art(item))
        th.setDaemon(True)
        th.start()
    data = httptools.downloadpage(item.url).data
    if len(item.extra.split("|")):
        if len(item.extra.split("|")) >= 4:
            fanart = item.extra.split("|")[2]
            extra = item.extra.split("|")[3]
            try:
                fanart_extra = item.extra.split("|")[4]
            except:
                fanart_extra = item.extra.split("|")[3]
            try:
                fanart_info = item.extra.split("|")[5]
            except:
                fanart_extra = item.extra.split("|")[3]
        elif len(item.extra.split("|")) == 3:
            fanart = item.extra.split("|")[2]
            extra = item.extra.split("|")[0]
            fanart_extra = item.extra.split("|")[0]
            fanart_info = item.extra.split("|")[1]
        elif len(item.extra.split("|")) == 2:
            fanart = item.extra.split("|")[1]
            extra = item.extra.split("|")[0]
            fanart_extra = item.extra.split("|")[0]
            fanart_info = item.extra.split("|")[1]
    else:
        extra = item.extra
        fanart_extra = item.extra
        fanart_info = item.extra
    try:
        logger.info(fanart_extra)
        logger.info(fanart_info)
    except:
        fanart_extra = item.fanart
        fanart_info = item.fanart
    bloque_episodios = scrapertools.find_multiple_matches(data, 'Temporada (\d+) -(.*?)</ul>')
    for temporada, bloque_epis in bloque_episodios:
        if 'no data' in bloque_epis or '<a href="">' in bloque_epis: continue
        item.infoLabels = item.InfoLabels
        item.infoLabels['season'] = temporada
        itemlist.append(item.clone(action="epis",
                                   title="[COLOR royalblue][B]Temporada [/B][/COLOR]" + "[COLOR antiquewhite][B]" + temporada + "[/B][/COLOR]",
                                   url=bloque_epis, fanart=fanart, contentType=item.contentType,
                                   contentTitle=item.contentTitle, show=item.show, extra=item.extra,
                                   fanart_extra=fanart_extra, fanart_info=fanart_info, datalibrary=data, folder=True))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    for item in itemlist:
        item.fanart = fanart
        item.extra = extra
    if config.get_videolibrary_support() and itemlist:

        if len(bloque_episodios) == 1:
            extra = "epis"
        else:
            extra = "epis###serie_add"
        infoLabels = {'tmdb_id': item.infoLabels['tmdb_id'], 'tvdb_id': item.infoLabels['tvdb_id'],
                      'imdb_id': item.infoLabels['imdb_id']}
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", text_color="0xFF00ffff",
                             action="add_serie_to_library", extra=extra, url=item.url,
                             contentSerieName=item.fulltitle, infoLabels=infoLabels,
                             thumbnail='http://imgur.com/BbafXw7.png', datalibrary=data))

    return itemlist


def epis(item):
    logger.info()
    itemlist = []
    if item.extra == "serie_add":
        item.url = item.datalibrary
    patron = scrapertools.find_multiple_matches(item.url,
                                                '<div class="numerando">([^"]+)</div>.*?href="([^"]+)">([^"]+)</a>')

    for epi, url, title in patron:
        epi = epi.replace(" ", "")
        episodio = epi
        episodio = scrapertools.find_single_match(episodio, '\d+x(\d+)')
        item.infoLabels['episode'] = episodio
        itemlist.append(
            item.clone(title="[COLOR blue][B]" + epi + "[/B][/COLOR]", url=url, action="findvideos", show=item.show,
                       fanart=item.extra, extra=item.extra, fanart_extra=item.fanart_extra,
                       fanart_info=item.fanart_info, folder=True))
    if item.extra != "serie_add":
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
        for item in itemlist:
            item.fanart = item.extra
            if item.infoLabels['title']: title = "[COLOR lightblue]" + item.infoLabels['title'] + "[/COLOR]"
            item.title = item.title + "[CR]\"" + title + "\""
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if not item.infoLabels['episode']:
        th = Thread(target=get_art(item))
        th.setDaemon(True)
        th.start()
    url = scrapertools.find_single_match(data, '<div class="botones_descarga">.*?href="([^"]+)"').strip()
    if item.contentType != "movie":
        check_online = '<div class="linkstv">'
        if not item.infoLabels['episode']:
            capitulo = scrapertools.find_single_match(item.title, '(\d+x\d+)')
            url_serie = re.sub(r'-\d+x\d+.*', '', item.url)
            url_serie = re.sub(r'\/episodio', '/series', url_serie)
            if len(item.extra.split("|")) >= 2:
                extra = item.extra
            else:
                extra = item.fanart
        else:
            capitulo = scrapertools.find_single_match(item.title, '\d+x\d+')
        try:
            fanart = item.fanart_extra
        except:
            fanart = item.extra.split("|")[0]
        if not url and item.library:
            itemlist.append(Item(channel=item.channel, title="[COLOR slateblue][B]No disponible[/B][/COLOR]", url=url,
                                 fanart=fanart, thumbnail=item.thumbnail, extra=item.extra, folder=False))
        else:

            title = "[COLOR darkturquoise][B]Torrent [/B][/COLOR]" + "[COLOR aliceblue][B]" + capitulo + "[/B][/COLOR]"

            title = re.sub(r'\".*', '', title)
            itemlist.append(
                Item(channel=item.channel, title=title, url=url, action="play", server="torrent", fanart=fanart,
                     thumbnail=item.thumbnail, extra=item.extra, folder=False))


    else:

        check_online = '<div class="realse">'
        item.infoLabels['year'] = None
        itemlist.append(
            Item(channel=item.channel, title="[COLOR deepskyblue][B]Torrent[/B][/COLOR]", url=url, action="play",
                 server="torrent", fanart=item.fanart, thumbnail=item.thumbnail, extra=item.extra,
                 InfoLabels=item.infoLabels, folder=False))
        if item.library and config.get_videolibrary_support() and len(itemlist) > 0:
            infoLabels = {'tmdb_id': item.infoLabels['tmdb_id'],
                          'title': item.infoLabels['title']}
            itemlist.append(Item(channel=item.channel, title="Añadir esta película a la videoteca",
                                 action="add_pelicula_to_library", url=item.url, infoLabels=infoLabels,
                                 text_color="0xFF00ffff",
                                 thumbnail='http://imgur.com/BbafXw7.png'))

    dd = scrapertools.find_multiple_matches(data, '<h1 class="h1_pelis_online">(.*?)' + check_online + '')
    if dd:
        if item.library:
            extra = dd
            itemlist.append(
                Item(channel=item.channel, title="[COLOR floralwhite][B]      Online[/B][/COLOR]", url=item.url,
                     action="dd_y_o", thumbnail="http://imgur.com/hYgra9W.png", fanart=item.extra.split("|")[0],
                     contentType=item.contentType, extra=str(extra) + "|" + item.extra, folder=True))
        else:

            patron = scrapertools.find_multiple_matches(str(dd),
                                                        '<li class="elemento">.*?href="([^"]+)".*?<span class="c">([^"]+)</span>.*?<span class="d">([^"]+)</span>')

            for url, idioma, calidad, in patron:
                idioma = re.sub(r'\\xc3\\xb1', 'ñ', idioma)
                idioma = re.sub(r'\\xc3\\xa9', 'é', idioma)
                videolist = servertools.find_video_items(data=url)
                for video in videolist:
                    icon_server = os.path.join(config.get_runtime_path(), "resources", "images", "servers",
                                               "server_" + video.server + ".png")
                    if not os.path.exists(icon_server):
                        icon_server = ""
                    itemlist.append(Item(channel=item.channel, url=video.url, server=video.server,
                                         title="[COLOR floralwhite][B]" + video.server + "[/B][/COLOR]" + " " + "[COLOR powderblue]" + idioma + "[/COLOR]" + "[COLOR deepskyblue]--" + calidad + "[/COLOR]",
                                         thumbnail=icon_server, fanart=fanart, action="play", folder=False))
    if not item.infoLabels['episode'] and item.contentType != "movie":
        itemlist.append(
            Item(channel=item.channel, title="[COLOR paleturquoise][B]Todos los episodios[/B][/COLOR]", url=url_serie,
                 action="findtemporadas", server="torrent", fanart=item.extra.split("|")[1], thumbnail=item.thumbnail,
                 thumb_art=item.thumb_art, thumb_info=item.thumb_info, extra=item.extra + "|" + item.thumbnail,
                 contentType=item.contentType, contentTitle=item.contentTitle, InfoLabels=item.infoLabels,
                 library=item.library, fulltitle=item.fulltitle, folder=True))
    if item.infoLabels['episode'] and item.library:

        thumbnail = scrapertools.find_single_match(item.extra, 'http://assets.fanart.tv/.*jpg')
        if thumbnail == "":
            thumbnail = item.thumbnail
        if not "assets.fanart" in item.fanart_info:
            fanart = item.fanart_info
        else:
            fanart = item.fanart
        itemlist.append(
            Item(channel=item.channel, title="[COLOR steelblue][B] info[/B][/COLOR]", url=url, action="info_capitulos",
                 fanart=item.extra.split("|")[0], thumbnail=item.thumb_art, thumb_info=item.thumb_info,
                 extra=item.extra, show=item.show, InfoLabels=item.infoLabels, folder=False))
    return itemlist


def dd_y_o(item):
    logger.info()
    itemlist = []
    if item.contentType == "movie":
        enlaces = item.extra.split("|")[0]
        fanart = item.extra.split("|")[2]

    else:
        enlaces = item.extra.split("|")[0]
        fanart = ""
    patron = scrapertools.find_multiple_matches(enlaces,
                                                '<li class="elemento">.*?href="([^"]+)".*?<span class="c">([^"]+)</span>.*?<span class="d">([^"]+)</span>')
    for url, idioma, calidad, in patron:
        idioma = re.sub(r'\\xc3\\xb1', 'ñ', idioma)
        idioma = re.sub(r'\\xc3\\xa9', 'é', idioma)
        videolist = servertools.find_video_items(data=url)
        for video in videolist:
            icon_server = os.path.join(config.get_runtime_path(), "resources", "images", "servers",
                                       "server_" + video.server + ".png")
            if not os.path.exists(icon_server):
                icon_server = ""
            itemlist.append(Item(channel=item.channel, url=video.url, server=video.server,
                                 title="[COLOR floralwhite][B]" + video.server + "[/B][/COLOR]" + " " + "[COLOR powderblue]" + idioma + "[/COLOR]" + "[COLOR deepskyblue]--" + calidad + "[/COLOR]",
                                 thumbnail=icon_server, fanart=fanart, action="play", folder=False))
    return itemlist


def info_capitulos(item, images={}):
    logger.info()
    try:
        url = "http://thetvdb.com/api/1D62F2F90030C444/series/" + str(item.InfoLabels['tvdb_id']) + "/default/" + str(
            item.InfoLabels['season']) + "/" + str(item.InfoLabels['episode']) + "/es.xml"
        if "/0" in url:
            url = url.replace("/0", "/")
        from core import jsontools
        data = httptools.downloadpage(url).data
        if "<filename>episodes" in data:
            image = scrapertools.find_single_match(data, '<Data>.*?<filename>(.*?)</filename>')
            image = "http://thetvdb.com/banners/" + image
        else:
            try:
                image = item.InfoLabels['episodio_imagen']
            except:
                image = "http://imgur.com/ZiEAVOD.png"

        foto = item.thumb_info
        if not ".png" in foto:
            foto = "http://imgur.com/AdGHzKS.png"
        try:
            title = item.InfoLabels['episodio_titulo']
        except:
            title = ""
        title = "[COLOR red][B]" + title + "[/B][/COLOR]"

        try:
            plot = item.InfoLabels['episodio_sinopsis']
        except:
            plot = scrapertools.find_single_match(data, '<Overview>(.*?)</Overview>')
            if plot == "":
                plot = "Sin información todavia"
        try:
            rating = item.InfoLabels['episodio_vote_average']
        except:
            rating = 0
        try:

            if rating >= 5 and rating < 8:
                rating = "[COLOR yellow]Puntuación[/COLOR] " + "[COLOR springgreen][B]" + str(rating) + "[/B][/COLOR]"
            elif rating >= 8 and rating < 10:
                rating = "[COLOR yellow]Puntuación[/COLOR] " + "[COLOR yellow][B]" + str(rating) + "[/B][/COLOR]"
            elif rating == 10:
                rating = "[COLOR yellow]Puntuación[/COLOR] " + "[COLOR orangered][B]" + str(rating) + "[/B][/COLOR]"
            else:
                rating = "[COLOR yellow]Puntuación[/COLOR] " + "[COLOR crimson][B]" + str(rating) + "[/B][/COLOR]"
        except:
            rating = "[COLOR yellow]Puntuación[/COLOR] " + "[COLOR crimson][B]" + str(rating) + "[/B][/COLOR]"
        if "10." in rating:
            rating = re.sub(r'10\.\d+', '10', rating)


    except:

        title = "[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
        plot = "Este capitulo no tiene informacion..."
        plot = "[COLOR yellow][B]" + plot + "[/B][/COLOR]"
        image = "http://s6.postimg.org/ub7pb76c1/noinfo.png"
        foto = "http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        rating = ""

    ventana = TextBox2(title=title, plot=plot, thumbnail=image, fanart=foto, rating=rating)
    ventana.doModal()


class TextBox2(xbmcgui.WindowDialog):
    """ Create a skinned textbox window """

    def __init__(self, *args, **kwargs):
        self.getTitle = kwargs.get('title')
        self.getPlot = kwargs.get('plot')
        self.getThumbnail = kwargs.get('thumbnail')
        self.getFanart = kwargs.get('fanart')
        self.getRating = kwargs.get('rating')

        self.background = xbmcgui.ControlImage(70, 20, 1150, 630, 'http://imgur.com/PKOYIzX.jpg')
        self.title = xbmcgui.ControlTextBox(120, 60, 430, 50)
        self.rating = xbmcgui.ControlTextBox(145, 112, 1030, 45)
        self.plot = xbmcgui.ControlTextBox(120, 150, 1056, 100)
        self.thumbnail = xbmcgui.ControlImage(120, 300, 1056, 300, self.getThumbnail)
        self.fanart = xbmcgui.ControlImage(780, 43, 390, 100, self.getFanart)

        self.addControl(self.background)
        self.background.setAnimations(
            [('conditional', 'effect=slide start=1000% end=0% time=1500 condition=true tween=bounce',),
             ('WindowClose', 'effect=slide delay=800 start=0% end=1000%  time=800 condition=true',)])
        self.addControl(self.thumbnail)
        self.thumbnail.setAnimations([('conditional',
                                       'effect=zoom  start=0% end=100% delay=2700 time=1500 condition=true tween=elastic easing=inout',),
                                      ('WindowClose', 'effect=slide end=0,700%   time=300 condition=true',)])
        self.addControl(self.plot)
        self.plot.setAnimations(
            [('conditional', 'effect=zoom delay=2000 center=auto start=0 end=100  time=800  condition=true  ',), (
            'conditional',
            'effect=rotate  delay=2000 center=auto aceleration=6000 start=0% end=360%  time=800  condition=true',),
             ('WindowClose', 'effect=zoom center=auto start=100% end=-0%  time=600 condition=true',)])
        self.addControl(self.fanart)
        self.fanart.setAnimations(
            [('WindowOpen', 'effect=slide start=0,-700 delay=1000 time=2500 tween=bounce condition=true',), (
            'conditional',
            'effect=rotate center=auto  start=0% end=360% delay=3000 time=2500 tween=bounce condition=true',),
             ('WindowClose', 'effect=slide end=0,-700%  time=1000 condition=true',)])
        self.addControl(self.title)
        self.title.setText(self.getTitle)
        self.title.setAnimations(
            [('conditional', 'effect=slide start=-1500% end=0%  delay=1000 time=2000 condition=true tween=elastic',),
             ('WindowClose', 'effect=slide start=0% end=-1500%  time=800 condition=true',)])
        self.addControl(self.rating)
        self.rating.setText(self.getRating)
        self.rating.setAnimations(
            [('conditional', 'effect=fade start=0% end=100% delay=3000 time=1500 condition=true',),
             ('WindowClose', 'effect=slide end=0,-700%  time=600 condition=true',)])
        xbmc.sleep(200)

        try:
            self.plot.autoScroll(7000, 6000, 30000)
        except:

            xbmc.executebuiltin(
                'Notification([COLOR red][B]Actualiza Kodi a su última versión[/B][/COLOR], [COLOR skyblue]para mejor info[/COLOR],8000,"https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/kodi-icon.png")')
        self.plot.setText(self.getPlot)

    def get(self):
        self.show()

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action.getId() == ACTION_GESTURE_SWIPE_LEFT or action == 110 or action == 92:
            self.close()


def test():
    return True


def tokenize(text, match=re.compile("([idel])|(\d+):|(-?\d+)").match):
    i = 0
    while i < len(text):
        m = match(text, i)
        s = m.group(m.lastindex)
        i = m.end()
        if m.lastindex == 2:
            yield "s"
            yield text[i:i + int(s)]
            i = i + int(s)
        else:
            yield s


def decode_item(next, token):
    if token == "i":
        # integer: "i" value "e"
        data = int(next())
        if next() != "e":
            raise ValueError
    elif token == "s":
        # string: "s" value (virtual tokens)
        data = next()
    elif token == "l" or token == "d":
        # container: "l" (or "d") values "e"
        data = []
        tok = next()
        while tok != "e":
            data.append(decode_item(next, tok))
            tok = next()
        if token == "d":
            data = dict(zip(data[0::2], data[1::2]))
    else:
        raise ValueError
    return data


def decode(text):
    try:
        src = tokenize(text)
        data = decode_item(src.next, src.next())
        for token in src:  # look for more tokens
            raise SyntaxError("trailing junk")
    except (AttributeError, ValueError, StopIteration):
        try:
            data = data
        except:
            data = src

    return data


def convert_size(size):
    import math
    if (size == 0):
        return '0B'
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return '%s %s' % (s, size_name[i])


def fanartv(item, id_tvdb, id, images={}):
    headers = [['Content-Type', 'application/json']]
    from core import jsontools
    if item.contentType == "movie":
        url = "http://webservice.fanart.tv/v3/movies/%s?api_key=cab16e262d72fea6a6843d679aa10300" \
              % id
    else:
        url = "http://webservice.fanart.tv/v3/tv/%s?api_key=cab16e262d72fea6a6843d679aa10300" % id_tvdb
    try:
        data = jsontools.load(scrapertools.downloadpage(url, headers=headers))
        if data and not "error message" in data:
            for key, value in data.items():
                if key not in ["name", "tmdb_id", "imdb_id", "thetvdb_id"]:
                    images[key] = value
        else:
            images = []

    except:
        images = []
    return images


def filmaffinity(item, infoLabels):
    title = infoLabels["title"].replace(" ", "+")
    try:
        year = infoLabels["year"]
    except:
        year = ""
    sinopsis = infoLabels["sinopsis"]

    if year == "":
        if item.contentType != "movie":
            tipo = "serie"
            url_bing = "http://www.bing.com/search?q=%s+Serie+de+tv+site:filmaffinity.com" % title
        else:
            tipo = "película"
            url_bing = "http://www.bing.com/search?q=%s+site:filmaffinity.com" % title
        try:
            data = browser(url_bing)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            if "myaddrproxy.php" in data:
                subdata_bing = scrapertools.get_match(data,
                                                      'li class="b_algo"><div class="b_title"><h2>(<a href="/myaddrproxy.php/http/www.filmaffinity.com/es/film.*?)"')
                subdata_bing = re.sub(r'\/myaddrproxy.php\/http\/', '', subdata_bing)
            else:
                subdata_bing = scrapertools.get_match(data,
                                                      'li class="b_algo"><h2>(<a href="http://www.filmaffinity.com/.*?/film.*?)"')

            url_filma = scrapertools.get_match(subdata_bing, '<a href="([^"]+)')
            if not "http" in url_filma:
                try:
                    data = httptools.downloadpage("http://" + url_filma, cookies=False, timeout=1).data
                except:
                    data = httptools.downloadpage("http://" + url_filma, cookies=False, timeout=1).data
            else:
                try:
                    data = httptools.downloadpage(url_filma, cookies=False, timeout=1).data
                except:
                    data = httptools.downloadpage(url_filma, cookies=False, timeout=1).data
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        except:
            pass
    else:
        tipo = "Pelicula"
        url = "http://www.filmaffinity.com/es/advsearch.php?stext={0}&stype%5B%5D=title&country=&genre=&fromyear={1}&toyear={1}".format(
            title, year)
        data = httptools.downloadpage(url, cookies=False).data
        url_filmaf = scrapertools.find_single_match(data, '<div class="mc-poster">\s*<a title="[^"]*" href="([^"]+)"')
        if url_filmaf:
            url_filmaf = "http://www.filmaffinity.com%s" % url_filmaf
            data = httptools.downloadpage(url_filmaf, cookies=False).data
        else:
            if item.contentType != "movie":
                tipo = "serie"
                url_bing = "http://www.bing.com/search?q=%s+Serie+de+tv+site:filmaffinity.com" % title
            else:
                tipo = "película"
                url_bing = "http://www.bing.com/search?q=%s+site:filmaffinity.com" % title
            try:
                data = browser(url_bing)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                if "myaddrproxy.php" in data:
                    subdata_bing = scrapertools.get_match(data,
                                                          'li class="b_algo"><div class="b_title"><h2>(<a href="/myaddrproxy.php/http/www.filmaffinity.com/es/film.*?)"')
                    subdata_bing = re.sub(r'\/myaddrproxy.php\/http\/', '', subdata_bing)
                else:
                    subdata_bing = scrapertools.get_match(data,
                                                          'li class="b_algo"><h2>(<a href="http://www.filmaffinity.com/.*?/film.*?)"')

                url_filma = scrapertools.get_match(subdata_bing, '<a href="([^"]+)')
                if not "http" in url_filma:
                    data = httptools.downloadpage("http://" + url_filma, cookies=False).data
                else:
                    data = httptools.downloadpage(url_filma, cookies=False).data
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            except:
                pass
    sinopsis_f = scrapertools.find_single_match(data, '<dd itemprop="description">(.*?)</dd>')
    sinopsis_f = sinopsis_f.replace("<br><br />", "\n")
    sinopsis_f = re.sub(r"\(FILMAFFINITY\)<br />", "", sinopsis_f)
    try:
        year_f = scrapertools.get_match(data, '<dt>Año</dt>.*?>(\d+)</dd>')
    except:
        year_f = ""
    try:
        rating_filma = scrapertools.get_match(data, 'itemprop="ratingValue" content="(.*?)">')
    except:
        rating_filma = "Sin puntuacion"
    critica = ""
    patron = '<div itemprop="reviewBody">(.*?)</div>.*?itemprop="author">(.*?)\s*<i alt="([^"]+)"'
    matches_reviews = scrapertools.find_multiple_matches(data, patron)

    if matches_reviews:
        for review, autor, valoracion in matches_reviews:
            review = dhe(scrapertools.htmlclean(review))
            review += "\n" + autor + "[CR]"
            review = re.sub(r'Puntuac.*?\)', '', review)
            if "positiva" in valoracion:
                critica += "[COLOR green][B]%s[/B][/COLOR]\n" % review
            elif "neutral" in valoracion:
                critica += "[COLOR yellow][B]%s[/B][/COLOR]\n" % review
            else:
                critica += "[COLOR red][B]%s[/B][/COLOR]\n" % review
    else:
        critica = "[COLOR floralwhite][B]Esta %s no tiene críticas todavía...[/B][/COLOR]" % tipo

    return critica, rating_filma, year_f, sinopsis_f


def get_art(item):
    logger.info()
    id = item.infoLabels['tmdb_id']
    check_fanart = item.infoLabels['fanart']
    if item.contentType != "movie":
        tipo_ps = "tv"
    else:
        tipo_ps = "movie"
    if not id:
        year = item.extra
        otmdb = tmdb.Tmdb(texto_buscado=item.fulltitle, year=year, tipo=tipo_ps)
        id = otmdb.result.get("id")

        if id == None:
            otmdb = tmdb.Tmdb(texto_buscado=item.fulltitle, tipo=tipo_ps)
            id = otmdb.result.get("id")
            if id == None:
                if item.contentType == "movie":
                    urlbing_imdb = "http://www.bing.com/search?q=%s+%s+tv+series+site:imdb.com" % (
                    item.fulltitle.replace(' ', '+'), year)
                    data = browser(urlbing_imdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|http://ssl-proxy.my-addr.org/myaddrproxy.php/", "", data)
                    subdata_imdb = scrapertools.find_single_match(data,
                                                                  '<li class="b_algo">(.*?)h="ID.*?<strong>.*?TV Series')
                else:
                    urlbing_imdb = "http://www.bing.com/search?q=%s+%s+site:imdb.com" % (
                    item.fulltitle.replace(' ', '+'), year)
                    data = browser(urlbing_imdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|http://ssl-proxy.my-addr.org/myaddrproxy.php/", "", data)
                    subdata_imdb = scrapertools.find_single_match(data, '<li class="b_algo">(.*?)h="ID.*?<strong>')
                try:
                    imdb_id = scrapertools.get_match(subdata_imdb, '<a href=.*?http.*?imdb.com/title/(.*?)/.*?"')
                except:
                    try:
                        imdb_id = scrapertools.get_match(subdata_imdb,
                                                         '<a href=.*?http.*?imdb.com/.*?/title/(.*?)/.*?"')
                    except:
                        imdb_id = ""
                otmdb = tmdb.Tmdb(external_id=imdb_id, external_source="imdb_id", tipo=tipo_ps, idioma_busqueda="es")
                id = otmdb.result.get("id")

                if id == None:
                    if "(" in item.fulltitle:
                        title = scrapertools.find_single_match(item.fulltitle, '\(.*?\)')
                        if item.contentType != "movie":
                            urlbing_imdb = "http://www.bing.com/search?q=%s+%s+tv+series+site:imdb.com" % (
                            title.replace(' ', '+'), year)
                            data = browser(urlbing_imdb)
                            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|http://ssl-proxy.my-addr.org/myaddrproxy.php/", "",
                                          data)
                            subdata_imdb = scrapertools.find_single_match(data,
                                                                          '<li class="b_algo">(.*?)h="ID.*?<strong>.*?TV Series')
                        else:
                            urlbing_imdb = "http://www.bing.com/search?q=%s+%s+site:imdb.com" % (
                            title.replace(' ', '+'), year)
                            data = browser(urlbing_imdb)
                            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|http://ssl-proxy.my-addr.org/myaddrproxy.php/", "",
                                          data)
                            subdata_imdb = scrapertools.find_single_match(data,
                                                                          '<li class="b_algo">(.*?)h="ID.*?<strong>')
                        try:
                            imdb_id = scrapertools.get_match(subdata_imdb,
                                                             '<a href=.*?http.*?imdb.com/title/(.*?)/.*?"')
                        except:
                            try:
                                imdb_id = scrapertools.get_match(subdata_imdb,
                                                                 '<a href=.*?http.*?imdb.com/.*?/title/(.*?)/.*?"')
                            except:
                                imdb_id = ""
                        otmdb = tmdb.Tmdb(external_id=imdb_id, external_source="imdb_id", tipo=tipo_ps,
                                          idioma_busqueda="es")
                        id = otmdb.result.get("id")

                        if not id:
                            fanart = item.fanart

    imagenes = []
    itmdb = tmdb.Tmdb(id_Tmdb=id, tipo=tipo_ps)
    images = itmdb.result.get("images")
    if images:
        for key, value in images.iteritems():
            for detail in value:
                imagenes.append('http://image.tmdb.org/t/p/original' + detail["file_path"])

        if item.contentType == "movie":
            if len(imagenes) >= 4:
                if imagenes[0] != check_fanart:
                    item.fanart = imagenes[0]
                else:
                    item.fanart = imagenes[1]
                if imagenes[1] != check_fanart and imagenes[1] != item.fanart and imagenes[2] != check_fanart:
                    item.extra = imagenes[1] + "|" + imagenes[2]

                else:
                    if imagenes[1] != check_fanart and imagenes[1] != item.fanart:
                        item.extra = imagenes[1] + "|" + imagenes[3]
                    elif imagenes[2] != check_fanart:
                        item.extra = imagenes[2] + "|" + imagenes[3]
                    else:
                        item.extra = imagenes[3] + "|" + imagenes[3]
            elif len(imagenes) == 3:

                if imagenes[0] != check_fanart:
                    item.fanart = imagenes[0]
                else:
                    item.fanart = imagenes[1]

                if imagenes[1] != check_fanart and imagenes[1] != item.fanart and imagenes[2] != check_fanart:
                    item.extra = imagenes[1] + "|" + imagenes[2]


                else:
                    if imagenes[1] != check_fanart and imagenes[1] != item.fanart:
                        item.extra = imagenes[0] + "|" + imagenes[1]
                    elif imagenes[2] != check_fanart:
                        item.extra = imagenes[1] + "|" + imagenes[2]
                    else:
                        item.extra = imagenes[1] + "|" + imagenes[1]
            elif len(imagenes) == 2:
                if imagenes[0] != check_fanart:
                    item.fanart = imagenes[0]
                else:
                    item.fanart = imagenes[1]
                if imagenes[1] != check_fanart and imagenes[1] != item.fanart:
                    item.extra = imagenes[0] + "|" + imagenes[1]
                else:
                    item.extra = imagenes[1] + "|" + imagenes[0]
            elif len(imagenes) == 1:
                item.extra = imagenes[0] + "|" + imagenes[0]
            else:
                item.extra = item.fanart + "|" + item.fanart
            id_tvdb = ""
        else:
            # item.infoLabels['year']=None
            # item.infoLabels['filtro']=None

            if itmdb.result.get("external_ids").get("tvdb_id"):
                id_tvdb = itmdb.result.get("external_ids").get("tvdb_id")
            else:
                id_tvdb = ""
            if len(imagenes) >= 6:

                if imagenes[0] != check_fanart:
                    item.fanart = imagenes[0]
                else:
                    item.fanart = imagenes[1]
                if imagenes[1] != check_fanart and imagenes[1] != item.fanart and imagenes[2] != check_fanart:
                    item.extra = imagenes[1] + "|" + imagenes[2] + "|" + imagenes[3] + "|" + imagenes[4] + "|" + \
                                 imagenes[5]

                else:
                    if imagenes[1] != check_fanart and imagenes[1] != item.fanart:
                        item.extra = imagenes[1] + "|" + imagenes[3] + "|" + imagenes[4] + "|" + imagenes[5] + "|" + \
                                     imagenes[2]
                    elif imagenes[2] != check_fanart:
                        item.extra = imagenes[2] + "|" + imagenes[3] + "|" + imagenes[4] + "|" + imagenes[5] + "|" + \
                                     imagenes[1]
                    else:
                        item.extra = imagenes[3] + "|" + imagenes[4] + "|" + imagenes[5] + "|" + imagenes[2] + "|" + \
                                     imagenes[1]
            elif len(imagenes) == 5:
                if imagenes[0] != check_fanart:
                    item.fanart = imagenes[0]
                else:
                    item.fanart = imagenes[1]
                if imagenes[1] != check_fanart and imagenes[1] != item.fanart and imagenes[2] != check_fanart:
                    item.extra = imagenes[1] + "|" + imagenes[2] + "|" + imagenes[3] + "|" + imagenes[4]


                else:

                    if imagenes[1] != check_fanart and imagenes[1] != item.fanart:
                        item.extra = imagenes[1] + "|" + imagenes[3] + "|" + imagenes[4] + "|" + imagenes[2]
                    elif imagenes[2] != check_fanart:
                        item.extra = imagenes[2] + "|" + imagenes[3] + "|" + imagenes[4] + "|" + imagenes[1]
                    else:
                        item.extra = imagenes[3] + "|" + imagenes[4] + "|" + imagenes[2] + "|" + imagenes[1]
            elif len(imagenes) == 4:
                if imagenes[0] != check_fanart:
                    item.fanart = imagenes[0]
                else:
                    item.fanart = imagenes[1]
                if imagenes[1] != check_fanart and imagenes[1] != item.fanart and imagenes[2] != check_fanart:
                    item.extra = imagenes[1] + "|" + imagenes[2] + "|" + imagenes[3] + "|" + imagenes[4]

                else:
                    if imagenes[1] != check_fanart and imagenes[1] != item.fanart:
                        item.extra = imagenes[1] + "|" + imagenes[3] + "|" + imagenes[2]
                    elif imagenes[2] != check_fanart:
                        item.extra = imagenes[2] + "|" + imagenes[3] + "|" + imagenes[1]
                    else:
                        item.extra = imagenes[3] + "|" + imagenes[2] + "|" + imagenes[1]

            elif len(imagenes) == 3:
                if imagenes[0] != check_fanart:
                    item.fanart = imagenes[0]
                else:
                    item.fanart = imagenes[1]

                if imagenes[1] != check_fanart and imagenes[1] != item.fanart and imagenes[2] != check_fanart:
                    item.extra = imagenes[1] + "|" + imagenes[2]

                else:

                    if imagenes[1] != check_fanart and imagenes[1] != item.fanart:
                        item.extra = imagenes[0] + "|" + imagenes[1]
                    elif imagenes[2] != check_fanart:
                        item.extra = imagenes[1] + "|" + imagenes[2]
                    else:
                        item.extra = imagenes[1] + "|" + imagenes[1]
            elif len(imagenes) == 2:
                if imagenes[0] != check_fanart:
                    item.fanart = imagenes[0]
                else:
                    item.fanart = imagenes[1]
                if imagenes[1] != check_fanart and imagenes[1] != item.fanart:
                    item.extra = imagenes[0] + "|" + imagenes[1]
                else:
                    item.extra = imagenes[1] + "|" + imagenes[0]
            elif len(imagenes) == 1:
                item.extra = imagenes[0] + "|" + imagenes[0]
            else:
                item.extra = item.fanart + "|" + item.fanart
            item.extra = item.extra
    images_fanarttv = fanartv(item, id_tvdb, id)
    if images_fanarttv:
        if item.contentType == "movie":
            if images_fanarttv.get("moviedisc"):
                item.thumbnail = images_fanarttv.get("moviedisc")[0].get("url")
            elif images_fanarttv.get("hdmovielogo"):
                item.thumbnail = images_fanarttv.get("hdmovielogo")[0].get("url")
            elif images_fanarttv.get("moviethumb"):
                item.thumbnail = images_fanarttv.get("moviethumb")[0].get("url")
            elif images_fanarttv.get("moviebanner"):
                item.thumbnail_ = images_fanarttv.get("moviebanner")[0].get("url")
            else:
                item.thumbnail = item.thumbnail
        else:
            if images_fanarttv.get("hdtvlogo"):
                item.thumbnail = images_fanarttv.get("hdtvlogo")[0].get("url")
            elif images_fanarttv.get("clearlogo"):
                item.thumbnail = images_fanarttv.get("hdmovielogo")[0].get("url")
            item.thumb_info = item.thumbnail
            if images_fanarttv.get("tvbanner"):
                item.thumb_art = images_fanarttv.get("tvbanner")[0].get("url")
            elif images_fanarttv.get("tvthumb"):
                item.thumb_art = images_fanarttv.get("tvthumb")[0].get("url")
            else:
                item.thumb_art = item.thumbnail

    else:
        item.extra = item.extra + "|" + item.thumbnail
