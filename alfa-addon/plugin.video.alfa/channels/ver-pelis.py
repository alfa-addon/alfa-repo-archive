# -*- coding: utf-8 -*-

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
    itemlist.append(
        item.clone(title="[COLOR oldlace][B]Películas[/B][/COLOR]", action="scraper", url="http://ver-pelis.me/ver/",
                   thumbnail="http://imgur.com/36xALWc.png", fanart="http://imgur.com/53dhEU4.jpg",
                   contentType="movie"))
    itemlist.append(item.clone(title="[COLOR oldlace][B]Películas en Español[/B][/COLOR]", action="scraper",
                               url="http://ver-pelis.me/ver/espanol/", thumbnail="http://imgur.com/36xALWc.png",
                               fanart="http://imgur.com/53dhEU4.jpg", contentType="movie"))

    itemlist.append(itemlist[-1].clone(title="[COLOR orangered][B]Buscar[/B][/COLOR]", action="search",
                                       thumbnail="http://imgur.com/ebWyuGe.png", fanart="http://imgur.com/53dhEU4.jpg",
                                       contentType="tvshow"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://ver-pelis.me/ver/buscar?s=" + texto
    item.extra = "search"
    if texto != '':
        return scraper(item)


def scraper(item):
    logger.info()
    itemlist = []
    url_next_page = ""
    global i
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = scrapertools.find_multiple_matches(data,
                                                '<a class="thumb cluetip".*?href="([^"]+)".*?src="([^"]+)" alt="([^"]+)".*?"res">([^"]+)</span>')
    if len(patron) > 20:
        if item.next_page != 20:
            url_next_page = item.url
            patron = patron[:20]
            next_page = 20
            item.i = 0
        else:
            patron = patron[item.i:][:20]
            next_page = 20

            url_next_page = item.url

    for url, thumb, title, cuality in patron:
        title = re.sub(r"Imagen", "", title)
        title = ''.join((c for c in unicodedata.normalize('NFD', unicode(title.decode('utf-8'))) if
                         unicodedata.category(c) != 'Mn')).encode("ascii", "ignore")
        titulo = "[COLOR floralwhite]" + title + "[/COLOR]" + " " + "[COLOR crimson][B]" + cuality + "[/B][/COLOR]"
        title = re.sub(r"!|\/.*", "", title).strip()

        if item.extra != "search":
            item.i += 1
        new_item = item.clone(action="findvideos", title=titulo, url=url, thumbnail=thumb, fulltitle=title,
                              contentTitle=title, contentType="movie", library=True)
        new_item.infoLabels['year'] = get_year(url)
        itemlist.append(new_item)

    ## Paginación
    if url_next_page:
        itemlist.append(item.clone(title="[COLOR crimson]Siguiente >>[/COLOR]", url=url_next_page, next_page=next_page,
                                   thumbnail="http://imgur.com/w3OMy2f.png", i=item.i))
    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
        for item in itemlist:
            if not "Siguiente >>" in item.title:
                if "0." in str(item.infoLabels['rating']):
                    item.infoLabels['rating'] = "[COLOR indianred]Sin puntuacíon[/COLOR]"
                else:
                    item.infoLabels['rating'] = "[COLOR orange]" + str(item.infoLabels['rating']) + "[/COLOR]"
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
    data_post = scrapertools.find_single_match(data, "type: 'POST'.*?id: (.*?),slug: '(.*?)'")
    if data_post:
        post = 'id=' + data_post[0] + '&slug=' + data_post[1]
        data_info = httptools.downloadpage('http://ver-pelis.me/ajax/cargar_video.php', post=post).data
        enlaces = scrapertools.find_multiple_matches(data_info,
                                                     "</i> (\w+ \w+).*?<a onclick=\"load_player\('([^']+)','([^']+)', ([^']+),.*?REPRODUCIR\">([^']+)</a>")
        for server, id_enlace, name, number, idioma_calidad in enlaces:

            if "SUBTITULOS" in idioma_calidad and not "P" in idioma_calidad:
                idioma_calidad = idioma_calidad.replace("SUBTITULOS", "VO")
                idioma_calidad = idioma_calidad.replace("VO", "[COLOR orangered] VO[/COLOR]")
            elif "SUBTITULOS" in idioma_calidad and "P" in idioma_calidad:
                idioma_calidad = "[COLOR indianred] " + idioma_calidad + "[/COLOR]"

            elif "LATINO" in idioma_calidad:
                idioma_calidad = idioma_calidad.replace("LATINO", "[COLOR red]LATINO[/COLOR]")
            elif "Español" in idioma_calidad:
                idioma_calidad = idioma_calidad.replace("Español", "[COLOR crimson]ESPAÑOL[/COLOR]")
            if "HD" in idioma_calidad:
                idioma_calidad = idioma_calidad.replace("HD", "[COLOR crimson] HD[/COLOR]")
            elif "720" in idioma_calidad:
                idioma_calidad = idioma_calidad.replace("720", "[COLOR firebrick] 720[/COLOR]")
            elif "TS" in idioma_calidad:
                idioma_calidad = idioma_calidad.replace("TS", "[COLOR brown] TS[/COLOR]")

            elif "CAM" in idioma_calidad:
                idioma_calidad = idioma_calidad.replace("CAM", "[COLOR darkkakhi] CAM[/COLOR]")

            url = "http://ver-pelis.me/ajax/video.php?id=" + id_enlace + "&slug=" + name + "&quality=" + number

            if not "Ultra" in server:
                server = "[COLOR cyan][B]" + server + "[/B][/COLOR]"
                extra = "yes"
            else:
                server = "[COLOR yellow][B]" + server + "[/B][/COLOR]"
                extra = ""
            title = server.strip() + "  " + idioma_calidad
            itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, fanart=item.fanart,
                                 thumbnail=item.thumbnail, fulltitle=item.title, extra=extra, folder=True))
        if item.library and config.get_videolibrary_support() and len(itemlist) > 0:
            infoLabels = {'tmdb_id': item.infoLabels['tmdb_id'],
                          'title': item.infoLabels['title']}
            itemlist.append(Item(channel=item.channel, title="Añadir esta película a la videoteca",
                                 action="add_pelicula_to_library", url=item.url, infoLabels=infoLabels,
                                 text_color="0xFFf7f7f7",
                                 thumbnail='http://imgur.com/gPyN1Tf.png'))
    else:
        itemlist.append(
            Item(channel=item.channel, action="", title="[COLOR red][B]Upps!..Archivo no encontrado...[/B][/COLOR]",
                 thumbnail=item.thumbnail))
    return itemlist


def play(item):
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\\', '', data)
    item.url = scrapertools.find_single_match(data, 'src="([^"]+)"')
    data = httptools.downloadpage(item.url).data

    if item.extra != "yes":
        patron = '"label":(.*?),.*?"type":"(.*?)",.*?"file":"(.*?)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if not matches:
            patron = '"label":(.*?),.*?"file":"(.*?)"'
            matches = re.compile(patron, re.DOTALL).findall(data)

        for dato_a, type, dato_b in matches:
            if 'http' in dato_a:
                url = dato_a
                calidad = dato_b
            else:
                url = dato_b
                calidad = dato_a
            url = url.replace('\\', '')
            type = type.replace('\\', '')
            itemlist.append(
                Item(channel=item.channel, url=url, action="play", title=item.fulltitle + " (" + dato_a + ")",
                     folder=False))
    else:

        url = scrapertools.find_single_match(data, 'window.location="([^"]+)"')

        videolist = servertools.find_video_items(data=url)
        for video in videolist:
            itemlist.append(Item(channel=item.channel, url=video.url, server=video.server,
                                 title="[COLOR floralwhite][B]" + video.server + "[/B][/COLOR]", action="play",
                                 folder=False))

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


def get_year(url):
    data = httptools.downloadpage(url).data
    year = scrapertools.find_single_match(data, '<p><strong>Año:</strong>(.*?)</p>')
    if year == "":
        year = " "
    return year
