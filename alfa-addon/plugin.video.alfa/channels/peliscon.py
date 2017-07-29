# -*- coding: utf-8 -*-

import re
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

__modo_grafico__ = config.get_setting('modo_grafico', "peliscon")


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
    itemlist.append(
        item.clone(title="[COLOR aqua][B]Películas[/B][/COLOR]", action="scraper", url="http://peliscon.com/peliculas/",
                   thumbnail="http://imgur.com/FrcWTS8.png", fanart="http://imgur.com/MGQyetQ.jpg",
                   contentType="movie"))
    itemlist.append(itemlist[-1].clone(title="[COLOR aqua][B]Series[/B][/COLOR]", action="scraper",
                                       url="http://peliscon.com/series/", thumbnail="http://imgur.com/FrcWTS8.png",
                                       fanart="http://imgur.com/i41eduI.jpg", contentType="tvshow"))
    itemlist.append(item.clone(title="[COLOR aqua][B]       Últimos capitulos[/B][/COLOR]", action="ul_cap",
                               url="http://peliscon.com/episodios/", thumbnail="http://imgur.com/FrcWTS8.png",
                               fanart="http://imgur.com/i41eduI.jpg", contentType="tvshow"))
    itemlist.append(itemlist[-1].clone(title="[COLOR crimson][B]Buscar[/B][/COLOR]", action="search",
                                       thumbnail="http://imgur.com/FrcWTS8.png", fanart="http://imgur.com/h1b7tfN.jpg"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "https://peliscon.com/?s=" + texto
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
                                                '<div class="result-item">.*?href="([^"]+)".*?alt="([^"]+)".*?<span class=".*?">([^"]+)</span>.*?<span class="year">([^"]+)</span>')

    for url, title, genere, year in patron:

        if "Serie" in genere:
            checkmt = "tvshow"
            genere = "[COLOR aqua][B]" + genere + "[/B][/COLOR]"
        else:
            checkmt = "movie"
            genere = "[COLOR cadetblue][B]" + genere + "[/B][/COLOR]"
        titulo = "[COLOR crimson]" + title + "[/COLOR]" + " [ " + genere + " ] "

        if checkmt == "movie":
            new_item = item.clone(action="findvideos", title=titulo, url=url, fulltitle=title, contentTitle=title,
                                  contentType="movie", library=True)
        else:

            new_item = item.clone(action="findtemporadas", title=titulo, url=url, fulltitle=title, contentTitle=title,
                                  show=title, contentType="tvshow", library=True)

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
    ## Paginación
    next = scrapertools.find_single_match(data, '<div class=\'resppages\'><a href="([^"]+)"')
    if len(next) > 0:
        url = next

        itemlist.append(item.clone(title="[COLOR springgreen][B]Siguiente >>[/B][/COLOR]", action="buscador", url=url))
    return itemlist


def scraper(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data

    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    if item.contentType == "movie":

        patron = scrapertools.find_multiple_matches(data,
                                                    '<div class="poster"><a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)".*?/flags/(.*?).png.*?<span>(.*?)</span>')

        for url, thumb, title, idioma, year in patron:
            titulo = title
            title = re.sub(r"!|¡", "", title)
            title = title.replace("Autosia", "Autopsia")
            title = re.sub(r"&#8217;|PRE-Estreno", "'", title)
            new_item = item.clone(action="findvideos", title="[COLOR aqua]" + titulo + "[/COLOR]", url=url,
                                  fulltitle=title, contentTitle=title, contentType="movie", extra=year, library=True)
            new_item.infoLabels['year'] = year
            itemlist.append(new_item)


    else:

        patron = scrapertools.find_multiple_matches(data,
                                                    '<div class="poster"><a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)".*?<span>(.*?)</span>')

        for url, thumb, title, year in patron:
            titulo = title.strip()
            title = re.sub(r"\d+x.*", "", title)
            new_item = item.clone(action="findtemporadas", title="[COLOR aqua]" + titulo + "[/COLOR]", url=url,
                                  thumbnail=thumb, fulltitle=title, contentTitle=title, show=title,
                                  contentType="tvshow", library=True)
            new_item.infoLabels['year'] = year
            itemlist.append(new_item)

    ## Paginación
    next = scrapertools.find_single_match(data, '<div class=\'resppages\'><a href="([^"]+)"')
    if len(next) > 0:
        url = next

        itemlist.append(
            item.clone(title="[COLOR springgreen][B]Siguiente >>[/B][/COLOR]", thumbnail="http://imgur.com/a7lQAld.png",
                       url=url))
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


def ul_cap(item):
    itemlist = []
    logger.info()
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = scrapertools.find_multiple_matches(data,
                                                '<div class="poster">.*?<img src="([^"]+)" alt="([^"]+):.*?href="([^"]+)"><span class="b">(\d+x\d+)<\/span>')

    for thumb, title, url, cap in patron:
        temp = re.sub(r"x\d+", "", cap)
        epi = re.sub(r"\d+x", "", cap)
        titulo = title.strip() + "--" + "[COLOR red][B]" + cap + "[/B][/COLOR]"
        title = re.sub(r"\d+x.*", "", title)
        # filtro_thumb = thumb.replace("https://image.tmdb.org/t/p/w300", "")
        # filtro_list = {"poster_path": filtro_thumb}
        # filtro_list = filtro_list.items()
        # url_tv = scrapertools.find_single_match(url,'episodios/(.*?)/')
        new_item = item.clone(action="findvideos", title="[COLOR aqua]" + titulo + "[/COLOR]", url=url, thumbnail=thumb,
                              fulltitle=title, contentTitle=title, show=title, contentType="tvshow", temp=temp, epi=epi,
                              library=True)

        itemlist.append(new_item)

    ## Paginación
    next = scrapertools.find_single_match(data, '<div class=\'resppages\'><a href="([^"]+)"')
    if len(next) > 0:
        url = next

        itemlist.append(
            item.clone(title="[COLOR springgreen][B]Siguiente >>[/B][/COLOR]", thumbnail="http://imgur.com/a7lQAld.png",
                       url=url))
    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

        for item in itemlist:

            if not "Siguiente >>" in item.title:

                if "0." in str(item.infoLabels['rating']):
                    item.infoLabels['rating'] = "[COLOR indianred]Sin puntuacíon[/COLOR]"
                else:
                    item.infoLabels['rating'] = "[COLOR springgreen] (" + str(item.infoLabels['rating']) + ")[/COLOR]"
                item.title = item.title + "  " + str(item.infoLabels['rating'])

    except:
        pass

    for item_tmdb in itemlist:
        logger.info(str(item_tmdb.infoLabels['tmdb_id']))

    return itemlist


def findtemporadas(item):
    logger.info()
    itemlist = []

    if not item.temp:
        th = Thread(target=get_art(item))
        th.setDaemon(True)
        th.start()
        check_temp = None
    else:

        check_temp = "yes"
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

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

    bloque_episodios = scrapertools.find_multiple_matches(data, 'Temporada (\d+) <i>(.*?)</div></li></ul></div></div>')
    for temporada, bloque_epis in bloque_episodios:
        item.infoLabels = item.InfoLabels
        item.infoLabels['season'] = temporada

        itemlist.append(item.clone(action="epis",
                                   title="[COLOR cornflowerblue][B]Temporada [/B][/COLOR]" + "[COLOR darkturquoise][B]" + temporada + "[/B][/COLOR]",
                                   url=bloque_epis, contentType=item.contentType, contentTitle=item.contentTitle,
                                   show=item.show, extra=item.extra, fanart_extra=fanart_extra, fanart_info=fanart_info,
                                   datalibrary=data, check_temp=check_temp, folder=True))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    for item in itemlist:
        item.fanart = fanart
        item.extra = extra
        if item.temp:
            item.thumbnail = item.infoLabels['temporada_poster']

    if config.get_videolibrary_support() and itemlist:
        if len(bloque_episodios) == 1:
            extra = "epis"
        else:
            extra = "epis###serie_add"

        infoLabels = {'tmdb_id': item.infoLabels['tmdb_id'], 'tvdb_id': item.infoLabels['tvdb_id'],
                      'imdb_id': item.infoLabels['imdb_id']}
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", text_color="0xFFe5ffcc",
                             action="add_serie_to_library", extra=extra, url=item.url,
                             contentSerieName=item.fulltitle, infoLabels=infoLabels,
                             thumbnail='http://imgur.com/3ik73p8.png', datalibrary=data))
    return itemlist


def epis(item):
    logger.info()
    itemlist = []

    if item.extra == "serie_add":
        item.url = item.datalibrary

    patron = scrapertools.find_multiple_matches(item.url, '<div class="imagen"><a href="([^"]+)".*?"numerando">(.*?)<')
    for url, epi in patron:
        episodio = scrapertools.find_single_match(epi, '\d+ - (\d+)')
        item.infoLabels['episode'] = episodio
        epi = re.sub(r" - ", "X", epi)

        itemlist.append(
            item.clone(title="[COLOR deepskyblue]Episodio " + "[COLOR red]" + epi, url=url, action="findvideos",
                       show=item.show, fanart=item.extra, extra=item.extra, fanart_extra=item.fanart_extra,
                       fanart_info=item.fanart_info, check_temp=item.check_temp, folder=True))
    if item.extra != "serie_add":
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
        for item in itemlist:
            item.fanart = item.extra
            if item.infoLabels['title']: title = "[COLOR royalblue]" + item.infoLabels['title'] + "[/COLOR]"
            item.title = item.title + " -- \"" + title + "\""
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    if item.temp:
        url_epis = item.url

    data = httptools.downloadpage(item.url).data

    if not item.infoLabels['episode'] or item.temp:
        th = Thread(target=get_art(item))
        th.setDaemon(True)
        th.start()

    if item.contentType != "movie":

        if not item.infoLabels['episode']:
            capitulo = scrapertools.find_single_match(item.title, '(\d+x\d+)')
            url_capitulo = scrapertools.find_single_match(data,
                                                          '<a href="(http://www.divxtotal.com/wp-content/uploads/.*?' + capitulo + '.*?.torrent)')

            if len(item.extra.split("|")) >= 2:
                extra = item.extra
            else:
                extra = item.fanart
        else:
            capitulo = item.title
            url_capitulo = item.url

        try:
            fanart = item.fanart_extra
        except:
            fanart = item.extra.split("|")[0]

        url_data = scrapertools.find_multiple_matches(data, '<div id="option-(.*?)".*?src="([^"]+)"')
        for option, url in url_data:
            server, idioma = scrapertools.find_single_match(data,
                                                            'href="#option-' + option + '">.*?</b>(.*?)<span class="dt_flag">.*?flags/(.*?).png')

            if not item.temp:
                item.infoLabels['year'] = None
            if item.temp:
                capitulo = re.sub(r".*--.*", "", capitulo)
                title = "[COLOR darkcyan][B]Ver capítulo [/B][/COLOR]" + "[COLOR red][B]" + capitulo + "[/B][/COLOR]"
                new_item = item.clone(title=title, url=url, action="play", fanart=fanart, thumbnail=item.thumbnail,
                                      server_v=server, idioma=idioma, extra=item.extra, fulltitle=item.fulltitle,
                                      folder=False)
                new_item.infoLabels['episode'] = item.epi
                new_item.infoLabels['season'] = item.temp
                itemlist.append(new_item)
            else:
                title = "[COLOR darkcyan][B]Ver capítulo [/B][/COLOR]" + "[COLOR red][B]" + capitulo + "[/B][/COLOR]" + "  " + "[COLOR darkred]" + server + " ( " + idioma + " )" + "[/COLOR]"
                itemlist.append(Item(channel=item.channel, title=title, url=url, action="play", fanart=fanart,
                                     thumbnail=item.thumbnail, extra=item.extra, fulltitle=item.fulltitle,
                                     folder=False))

        if item.temp:
            tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
            for item in itemlist:
                if item.infoLabels['title']: title_inf = "[COLOR royalblue]" + item.infoLabels['title'] + "[/COLOR]"
                item.title = item.title + " -- \"" + title_inf + "\"" + "  " + "[COLOR darkred]" + item.server_v + " ( " + item.idioma + " )" + "[/COLOR]"
        if item.infoLabels['episode'] and item.library or item.temp and item.library:
            thumbnail = scrapertools.find_single_match(item.extra, 'http://assets.fanart.tv/.*jpg')
            if thumbnail == "":
                thumbnail = item.thumbnail
            if not "assets.fanart" in item.fanart_info:
                fanart = item.fanart_info
            else:
                fanart = item.fanart
            if item.temp:
                item.infoLabels['tvdb_id'] = item.tvdb

            itemlist.append(
                Item(channel=item.channel, title="[COLOR steelblue][B]       info[/B][/COLOR]", action="info_capitulos",
                     fanart=fanart, thumbnail=item.thumb_art, thumb_info=item.thumb_info, extra=item.extra,
                     show=item.show, InfoLabels=item.infoLabels, folder=False))
        if item.temp and not item.check_temp:
            url_epis = re.sub(r"-\dx.*", "", url_epis)
            url_epis = url_epis.replace("episodios", "series")
            itemlist.append(
                Item(channel=item.channel, title="[COLOR salmon][B]Todos los episodios[/B][/COLOR]", url=url_epis,
                     action="findtemporadas", server="torrent", fanart=item.extra.split("|")[1],
                     thumbnail=item.infoLabels['thumbnail'], extra=item.extra + "|" + item.thumbnail,
                     contentType=item.contentType, contentTitle=item.contentTitle, InfoLabels=item.infoLabels,
                     thumb_art=item.thumb_art, thumb_info=item.thumbnail, fulltitle=item.fulltitle,
                     library=item.library, temp=item.temp, folder=True))



    else:

        url_data = scrapertools.find_multiple_matches(data, '<div id="option-(.*?)".*?src="([^"]+)"')
        for option, url in url_data:
            server, idioma = scrapertools.find_single_match(data,
                                                            'href="#option-' + option + '">.*?</b>(.*?)<span class="dt_flag">.*?flags/(.*?).png')
            title = server + " ( " + idioma + " )"
            item.infoLabels['year'] = None

            itemlist.append(Item(channel=item.channel, title="[COLOR dodgerblue][B]" + title + " [/B][/COLOR]", url=url,
                                 action="play", fanart=item.fanart, thumbnail=item.thumbnail, extra=item.extra,
                                 InfoLabels=item.infoLabels, folder=True))

        if item.library and config.get_videolibrary_support() and len(itemlist) > 0:
            infoLabels = {'tmdb_id': item.infoLabels['tmdb_id'],
                          'title': item.infoLabels['title']}
            itemlist.append(Item(channel=item.channel, title="Añadir esta película a la videoteca",
                                 action="add_pelicula_to_library", url=item.url, fanart=item.extra.split("|")[0],
                                 infoLabels=infoLabels, text_color="0xFFe5ffcc",
                                 thumbnail='http://imgur.com/3ik73p8.png'))

    return itemlist


def play(item):
    itemlist = []
    videolist = servertools.find_video_items(data=item.url)
    for video in videolist:
        itemlist.append(
            Item(channel=item.channel, title="[COLOR saddlebrown][B]" + video.server + "[/B][/COLOR]", url=video.url,
                 server=video.server, action="play", fanart=item.fanart, thumbnail=item.thumbnail, extra=item.extra,
                 InfoLabels=item.infoLabels, folder=False))
    return itemlist


def info_capitulos(item, images={}):
    logger.info()
    itemlist = []

    try:
        url = "http://thetvdb.com/api/1D62F2F90030C444/series/" + str(item.InfoLabels['tvdb_id']) + "/default/" + str(
            item.InfoLabels['season']) + "/" + str(item.InfoLabels['episode']) + "/es.xml"
        if "/0" in url:
            url = url.replace("/0", "/")
        from core import jsontools
        data = httptools.downloadpage(url).data
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

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
            foto = "http://imgur.com/PRiEW1D.png"
        try:
            title = item.InfoLabels['episodio_titulo']
        except:
            title = ""
        title = "[COLOR red][B]" + title + "[/B][/COLOR]"

        try:
            plot = "[COLOR peachpuff]" + str(item.InfoLabels['episodio_sinopsis']) + "[/COLOR]"
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

        self.background = xbmcgui.ControlImage(70, 20, 1150, 630, 'http://imgur.com/aj4qzTr.jpg')
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

            if itmdb.result.get("external_ids").get("tvdb_id"):
                id_tvdb = itmdb.result.get("external_ids").get("tvdb_id")
                if item.temp:
                    item.tvdb = id_tvdb


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
                    item.thumbnail = images_fanarttv.get("clearlogo")[0].get("url")
                item.thumb_info = item.thumbnail
                if images_fanarttv.get("hdclearart"):
                    item.thumb_art = images_fanarttv.get("hdclearart")[0].get("url")
                elif images_fanarttv.get("tvbanner"):
                    item.thumb_art = images_fanarttv.get("tvbanner")[0].get("url")
                else:
                    item.thumb_art = item.thumbnail

    else:
        item.extra = item.extra + "|" + item.thumbnail


def get_year(url):
    data = httptools.downloadpage(url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    year = scrapertools.find_single_match(data, 'Fecha de lanzamiento.*?, (\d\d\d\d)')
    if year == "":
        year = "1111"
    return year
