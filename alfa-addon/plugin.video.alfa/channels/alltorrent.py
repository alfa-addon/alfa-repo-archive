# -*- coding: utf-8 -*-

import os
import re
import unicodedata
from threading import Thread

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

__modo_grafico__ = config.get_setting('modo_grafico', "ver-pelis")


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
    i = 0
    global i
    itemlist.append(item.clone(title="[COLOR springgreen][B]Todas Las Películas[/B][/COLOR]", action="scraper",
                               url="http://alltorrent.net/", thumbnail="http://imgur.com/XLqPZoF.png",
                               fanart="http://imgur.com/v3ChkZu.jpg", contentType="movie"))
    itemlist.append(item.clone(title="[COLOR springgreen]      Incluyen 1080p[/COLOR]", action="scraper",
                               url="http://alltorrent.net/rezolucia/1080p/", thumbnail="http://imgur.com/XLqPZoF.png",
                               fanart="http://imgur.com/v3ChkZu.jpg", contentType="movie"))
    itemlist.append(item.clone(title="[COLOR springgreen]      Incluyen 720p[/COLOR]", action="scraper",
                               url="http://alltorrent.net/rezolucia/720p/", thumbnail="http://imgur.com/XLqPZoF.png",
                               fanart="http://imgur.com/v3ChkZu.jpg", contentType="movie"))
    itemlist.append(item.clone(title="[COLOR springgreen]      Incluyen Hdrip[/COLOR]", action="scraper",
                               url="http://alltorrent.net/rezolucia/hdrip/", thumbnail="http://imgur.com/XLqPZoF.png",
                               fanart="http://imgur.com/v3ChkZu.jpg", contentType="movie"))
    itemlist.append(item.clone(title="[COLOR springgreen]      Incluyen 3D[/COLOR]", action="scraper",
                               url="http://alltorrent.net/rezolucia/3d/", thumbnail="http://imgur.com/XLqPZoF.png",
                               fanart="http://imgur.com/v3ChkZu.jpg", contentType="movie"))
    itemlist.append(itemlist[-1].clone(title="[COLOR floralwhite][B]Buscar[/B][/COLOR]", action="search",
                                       thumbnail="http://imgur.com/5EBwccS.png", fanart="http://imgur.com/v3ChkZu.jpg",
                                       contentType="movie", extra="titulo"))
    itemlist.append(itemlist[-1].clone(title="[COLOR oldlace]         Por Título[/COLOR]", action="search",
                                       thumbnail="http://imgur.com/5EBwccS.png", fanart="http://imgur.com/v3ChkZu.jpg",
                                       contentType="movie", extra="titulo"))
    itemlist.append(itemlist[-1].clone(title="[COLOR oldlace]         Por Año[/COLOR]", action="search",
                                       thumbnail="http://imgur.com/5EBwccS.png", fanart="http://imgur.com/v3ChkZu.jpg",
                                       contentType="movie", extra="año"))
    itemlist.append(itemlist[-1].clone(title="[COLOR oldlace]         Por Rating Imdb[/COLOR]", action="search",
                                       thumbnail="http://imgur.com/5EBwccS.png", fanart="http://imgur.com/v3ChkZu.jpg",
                                       contentType="movie", extra="rating"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    if item.extra == "titulo":
        item.url = "http://alltorrent.net/?s=" + texto

    elif item.extra == "año":
        item.url = "http://alltorrent.net/weli/" + texto
    else:
        item.url = "http://alltorrent.net/imdb/" + texto
    if texto != '':
        return scraper(item)


def scraper(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = scrapertools.find_multiple_matches(data,
                                                '<div class="browse-movie-wrap col-xs-10 col-sm-4 col-md-5 col-lg-4"><a href="([^"]+)".*?src="([^"]+)".*?alt="([^"]+)".*?rel="tag">([^"]+)</a> ')

    for url, thumb, title, year in patron:
        title = re.sub(r"\(\d+\)", "", title)

        title = ''.join((c for c in unicodedata.normalize('NFD', unicode(title.decode('utf-8'))) if
                         unicodedata.category(c) != 'Mn')).encode("ascii", "ignore")
        titulo = "[COLOR lime]" + title + "[/COLOR]"
        title = re.sub(r"!|\/.*", "", title).strip()

        new_item = item.clone(action="findvideos", title=titulo, url=url, thumbnail=thumb, fulltitle=title,
                              contentTitle=title, contentType="movie", library=True)
        new_item.infoLabels['year'] = year
        itemlist.append(new_item)

    ## Paginación
    next = scrapertools.find_single_match(data, '<li><a href="([^"]+)" rel="nofollow">Next Page')
    if len(next) > 0:
        url = next

        itemlist.append(item.clone(title="[COLOR olivedrab][B]Siguiente >>[/B][/COLOR]", action="scraper", url=url,
                                   thumbnail="http://imgur.com/TExhOJE.png"))

    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
        for item in itemlist:
            if not "Siguiente >>" in item.title:
                if "0." in str(item.infoLabels['rating']):
                    item.infoLabels['rating'] = "[COLOR olive]Sin puntuación[/COLOR]"
                else:
                    item.infoLabels['rating'] = "[COLOR yellow]" + str(item.infoLabels['rating']) + "[/COLOR]"
                item.title = item.title + "  " + str(item.infoLabels['rating'])
    except:
        pass

    for item_tmdb in itemlist:
        logger.info(str(item_tmdb.infoLabels['tmdb_id']))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    th = Thread(target=get_art(item))
    th.setDaemon(True)
    th.start()
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    enlaces = scrapertools.find_multiple_matches(data,
                                                 'id="modal-quality-\w+"><span>(.*?)</span>.*?class="quality-size">(.*?)</p>.*?href="([^"]+)"')
    for calidad, size, url in enlaces:
        title = "[COLOR palegreen][B]Torrent[/B][/COLOR]" + " " + "[COLOR chartreuse]" + calidad + "[/COLOR]" + "[COLOR teal] ( [/COLOR]" + "[COLOR forestgreen]" + size + "[/COLOR]" + "[COLOR teal] )[/COLOR]"
        itemlist.append(
            Item(channel=item.channel, title=title, url=url, action="play", server="torrent", fanart=item.fanart,
                 thumbnail=item.thumbnail, extra=item.extra, InfoLabels=item.infoLabels, folder=False))
    dd = scrapertools.find_single_match(data, 'button-green-download-big".*?href="([^"]+)"><span class="icon-play">')
    if dd:
        if item.library:
            itemlist.append(
                Item(channel=item.channel, title="[COLOR floralwhite][B]Online[/B][/COLOR]", url=dd, action="dd_y_o",
                     thumbnail="http://imgur.com/mRmBIV4.png", fanart=item.extra.split("|")[0],
                     contentType=item.contentType, extra=item.extra, folder=True))
        else:
            videolist = servertools.find_video_items(data=str(dd))
            for video in videolist:
                icon_server = os.path.join(config.get_runtime_path(), "resources", "images", "servers",
                                           "server_" + video.server + ".png")
                if not os.path.exists(icon_server):
                    icon_server = ""
                itemlist.append(Item(channel=item.channel, url=video.url, server=video.server,
                                     title="[COLOR floralwhite][B]" + video.server + "[/B][/COLOR]",
                                     thumbnail=icon_server, fanart=item.extra.split("|")[1], action="play",
                                     folder=False))
    if item.library and config.get_videolibrary_support() and itemlist:
        infoLabels = {'tmdb_id': item.infoLabels['tmdb_id'],
                      'title': item.infoLabels['title']}
        itemlist.append(Item(channel=item.channel, title="Añadir esta película a la videoteca",
                             action="add_pelicula_to_library", url=item.url, infoLabels=infoLabels,
                             text_color="0xFFe5ffcc",
                             thumbnail='http://imgur.com/DNCBjUB.png', extra="library"))

    return itemlist


def dd_y_o(item):
    itemlist = []
    logger.info()
    videolist = servertools.find_video_items(data=item.url)
    for video in videolist:
        icon_server = os.path.join(config.get_runtime_path(), "resources", "images", "servers",
                                   "server_" + video.server + ".png")
        if not os.path.exists(icon_server):
            icon_server = ""
        itemlist.append(Item(channel=item.channel, url=video.url, server=video.server,
                             title="[COLOR floralwhite][B]" + video.server + "[/B][/COLOR]", thumbnail=icon_server,
                             fanart=item.extra.split("|")[1], action="play", folder=False))
    return itemlist


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

    id_tvdb = ""
    imagenes = []
    itmdb = tmdb.Tmdb(id_Tmdb=id, tipo=tipo_ps)
    images = itmdb.result.get("images")
    if images:
        for key, value in images.iteritems():
            for detail in value:
                imagenes.append('http://image.tmdb.org/t/p/original' + detail["file_path"])

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
            item.extra = imagenes + "|" + imagenes
        else:
            item.extra = item.fanart + "|" + item.fanart

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

            if images_fanarttv.get("tvbanner"):
                item.extra = item.extra + "|" + images_fanarttv.get("tvbanner")[0].get("url")
            elif images_fanarttv.get("tvthumb"):
                item.extra = item.extra + "|" + images_fanarttv.get("tvthumb")[0].get("url")
            else:
                item.extra = item.extra + "|" + item.thumbnail
    else:
        item.extra = item.extra + "|" + item.thumbnail
