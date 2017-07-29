# -*- coding: utf-8 -*-

import os
import re
import urllib
import urlparse

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

host = "http://peliculasgratis.biz"

CALIDADES = {"micro1080p": "[COLOR plum]Micro1080p[/COLOR]", "dvds": "[COLOR lime]Dvds[/COLOR]",
             "hdrip": "[COLOR dodgerblue]Hdrip[/COLOR]", "dvdrip": "[COLOR crimson]Dvdrip[/COLOR]",
             "hdts": "[COLOR aqua]Hdts[/COLOR]", "bluray-line": "[COLOR lightslategray]Bluray-line[/COLOR]",
             "hdtv-rip": "[COLOR black]Hdtv-rip[/COLOR]", "micro720p": "[COLOR yellow]Micro720p[/COLOR]",
             "ts-hq": "[COLOR mediumspringgreen]Ts-Hq[/COLOR]", "camrip": "[COLOR royalblue]Camp-Rip[/COLOR]",
             "webs": "[COLOR lightsalmon]Webs[/COLOR]", "hd": "[COLOR mediumseagreen]HD[/COLOR]"}
IDIOMAS = {"castellano": "[COLOR yellow]Castelllano[/COLOR]", "latino": "[COLOR orange]Latino[/COLOR]",
           "vose": "[COLOR lightsalmon]Subtitulada[/COLOR]", "vo": "[COLOR crimson]Ingles[/COLOR]",
           "en": "[COLOR crimson]Ingles[/COLOR]"}
IDIOMASP = {"es": "[COLOR yellow]CAST[/COLOR]", "la": "[COLOR orange]LAT[/COLOR]",
            "vs": "[COLOR lightsalmon]SUB[/COLOR]", "vo": "[COLOR crimson]Ingles[/COLOR]",
            "en": "[COLOR crimson]INGL[/COLOR]"}


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
    itemlist.append(item.clone(title="[COLOR lightskyblue][B]Películas[/B][/COLOR]", action="scraper", url=host,
                               thumbnail="http://imgur.com/fN2p6qH.png", fanart="http://imgur.com/b8OuBR2.jpg",
                               contentType="movie"))
    itemlist.append(itemlist[-1].clone(title="[COLOR lightskyblue][B]   Más vistas[/B][/COLOR]", action="scraper",
                                       url="http://peliculasgratis.biz/catalogue?order=most_viewed",
                                       thumbnail="http://imgur.com/fN2p6qH.png", fanart="http://imgur.com/b8OuBR2.jpg",
                                       contentType="movie"))
    itemlist.append(itemlist[-1].clone(title="   [COLOR lightskyblue][B]Recomendadas[/B][/COLOR]", action="scraper",
                                       url="http://peliculasgratis.biz/catalogue?order=most_rated",
                                       thumbnail="http://imgur.com/fN2p6qH.png.png",
                                       fanart="http://imgur.com/b8OuBR2.jpg", contentType="movie"))
    itemlist.append(itemlist[-1].clone(title="[COLOR lightskyblue][B]   Actualizadas[/B][/COLOR]", action="scraper",
                                       url="http://peliculasgratis.biz/catalogue?",
                                       thumbnail="http://imgur.com/fN2p6qH.png", fanart="http://imgur.com/b8OuBR2.jpg",
                                       contentType="movie"))
    itemlist.append(itemlist[-1].clone(title="[COLOR lightskyblue][B]Series[/B][/COLOR]", action="scraper",
                                       url="http://peliculasgratis.biz/lista-de-series",
                                       thumbnail="http://imgur.com/Jia27Uc.png", fanart="http://imgur.com/b8OuBR2.jpg",
                                       contentType="tvshow"))
    itemlist.append(itemlist[-1].clone(title="[COLOR lightskyblue][B]Buscar[/B][/COLOR]", action="", url="",
                                       thumbnail="http://imgur.com/mwTwfN7.png", fanart="http://imgur.com/b8OuBR2.jpg"))
    itemlist.append(
        itemlist[-1].clone(title="[COLOR lightskyblue][B]   Buscar Película[/B][/COLOR]", action="search", url="",
                           thumbnail="http://imgur.com/mwTwfN7.png", fanart="http://imgur.com/b8OuBR2.jpg",
                           contentType="movie"))
    itemlist.append(
        itemlist[-1].clone(title="[COLOR lightskyblue][B]   Buscar Serie[/B][/COLOR]", action="search", url="",
                           thumbnail="http://imgur.com/mwTwfN7.png", fanart="http://imgur.com/b8OuBR2.jpg",
                           contentType="tvshow"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://peliculasgratis.biz/search/%s" % texto

    try:
        return scraper(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def scraper(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    bloque_enlaces = scrapertools.find_single_match(data, '<h1 class="titulo-h1">(.*?)<\/i>Anuncios')
    if item.contentType != "movie":
        matches = scrapertools.find_multiple_matches(bloque_enlaces,
                                                     '<a class="i" href="([^"]+)".*?src="([^"]+)".*?<div class="l">(.*?)<\/a><h3>.*?(completa)">([^"]+)<\/a><\/h3> <span>(.*?)<\/span>')
    else:
        matches = scrapertools.find_multiple_matches(bloque_enlaces,
                                                     '<a class="i" href="([^"]+)".*?src="([^"]+)".*?">([^<]+)<.*?<div class="l">(.*?)<\/a><h3>.*?title[^<]+>([^<]+)<\/a><\/h3> <span>(.*?)<')
    for url, thumb, quality, check_idioma, title, check_year in matches:
        title_fan = title
        title_item = "[COLOR cornflowerblue][B]" + title + "[/B][/COLOR]"
        if item.contentType != "movie":
            title = "[COLOR cornflowerblue][B]" + title + "[/B][/COLOR]"
        else:
            if quality == "ts":
                quality = re.sub(r'ts', 'ts-hq', quality)
            if CALIDADES.get(quality):
                quality = CALIDADES.get(quality)
            else:
                quality = quality
            idiomas = scrapertools.find_multiple_matches(check_idioma, '<div class="id (.*?)">')
            if len(idiomas) == 1:
                idioma1 = idiomas[0].strip()
                if IDIOMASP.get(idioma1):
                    idiomas = "-" + IDIOMASP.get(idioma1)
            elif len(idiomas) == 2:
                idioma1, idioma2 = idiomas[0], idiomas[1]
                if IDIOMASP.get(idioma1, idioma2):
                    idioma1 = IDIOMASP.get(idioma1)
                    idioma2 = IDIOMASP.get(idioma2)
                    idiomas = "-" + idioma1 + "|" + idioma2
            elif len(idiomas) == 3:
                idioma1, idioma2, idioma3 = idiomas[0], idiomas[1], idiomas[2]
                idioma1 = IDIOMASP.get(idioma1)
                idioma2 = IDIOMASP.get(idioma2)
                idioma3 = IDIOMASP.get(idioma3)
                idiomas = "-" + idioma1 + "|" + idioma2 + "|" + idioma3
            elif len(idiomas) >= 4:
                idioma1, idioma2, idioma3, idioma4 = idiomas[0], idiomas[1], idiomas[2], idiomas[3]
                idioma1 = IDIOMASP.get(idioma1)
                idioma2 = IDIOMASP.get(idioma2)
                idioma3 = IDIOMASP.get(idioma3)
                idioma4 = IDIOMASP.get(idioma4)
                idiomas = "-" + idioma1 + "|" + idioma2 + "|" + idioma3 + "|" + idioma4

            title = "[COLOR cornflowerblue][B]" + title + "[/B][/COLOR]" + " " + quality + " " + idiomas

        itemlist.append(
            Item(channel=item.channel, title=title, url=urlparse.urljoin(host, url), action="fanart", thumbnail=thumb,
                 fanart="http://imgur.com/nqmJozd.jpg", extra=title_fan + "|" + title_item + "|" + check_year.strip(),
                 contentType=item.contentType, folder=True))
    ## Paginación
    if check_year:
        next = scrapertools.find_single_match(data, 'href="([^"]+)" title="Siguiente página">')
        if len(next) > 0:
            url = next
            if not "http" in url:
                url = urlparse.urljoin(host, url)
            itemlist.append(
                Item(channel=item.channel, action="scraper", title="[COLOR floralwhite][B]Siguiente[/B][/COLOR]",
                     url=url, thumbnail="http://imgur.com/jhRFAmk.png", fanart="http://imgur.com/nqmJozd.jpg",
                     extra=item.extra, contentType=item.contentType, folder=True))

    return itemlist


def fanart(item):
    logger.info()
    itemlist = []
    url = item.url
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    year = item.extra.split("|")[2]
    if not year.isdigit():
        try:
            year = scrapertools.find_single_match(data, '<span class="izq">[^<]+<\/span><span>(\d+)<')
        except:
            year = ""
    if item.contentType != "movie":
        tipo_ps = "tv"
    else:
        tipo_ps = "movie"
    title = item.extra.split("|")[0]
    fulltitle = title
    if "El infiltrado" in title:
        title = "The Night Manager"
    title_o = scrapertools.find_single_match(data, '<meta name="description"[^<]+original(.*?)&')
    item.title = item.extra.split("|")[1]
    title_imdb = re.sub(r'\[.*?\]', '', item.extra.split("|")[1])
    title = re.sub(
        r"\(.*?\)|-Remastered|Black And Chrome Edition|V.extendida|Version Extendida|V.Extendida|HEVC|X\d+|x\d+|LINE|HD|1080p|Screeener|V.O|Hdrip|.*?--|3D|SBS|HOU",
        "", title)

    sinopsis = scrapertools.find_single_match(data, '<div class="sinopsis".*?<\/h2>(.*?)<\/div>')
    if sinopsis == "":
        try:
            sinopsis = scrapertools.find_single_match(data, 'sinopsis\'>(.*?)<\/div>')
        except:
            sinopsis = ""
    if "Miniserie" in sinopsis:
        tipo_ps = "tv"
        year = scrapertools.find_single_match(sinopsis, 'de TV \((\d+)\)')
    if year == "":
        if item.contentType != "movie":
            try:
                year = scrapertools.find_single_match(data, '<strong>Estreno:<\/strong>(\d+)<\/span>')
            except:
                year = ""
        else:
            year = scrapertools.find_single_match(data, '<br \/>A.*?(\d+)<br \/>')
            if year == "":
                try:
                    year = scrapertools.find_single_match(data, 'Estreno.*?\d+/\d+/(\d+)')
                except:
                    try:
                        year = scrapertools.find_single_match(data,
                                                              '<div class=\'descripcion_top\'>.*?A&ntilde;o<br />.*?(\d\d\d\d)')
                    except:
                        try:
                            year = scrapertools.find_single_match(data,
                                                                  '<meta name="description"[^<]+A&ntilde;o[^<]+\d\d\d\d')
                        except:
                            year = ""
    infoLabels = {'title': title, 'sinopsis': sinopsis, 'year': year}
    critica, rating_filma, year_f, sinopsis_f = filmaffinity(item, infoLabels)
    if sinopsis == "":
        sinopsis = sinopsis_f
    if year == "":
        year = year_f
    otmdb = tmdb.Tmdb(texto_buscado=title, year=year, tipo=tipo_ps)
    id = otmdb.result.get("id")
    posterdb = otmdb.result.get("poster_path")
    if posterdb == None:
        otmdb = tmdb.Tmdb(texto_buscado=title, tipo=tipo_ps)
        id = otmdb.result.get("id")
        posterdb = otmdb.result.get("poster_path")
        if posterdb == None:
            if item.contentType != "movie":
                urlbing_imdb = "http://www.bing.com/search?q=%s+%s+tv+series+site:imdb.com" % (
                title_imdb.replace(' ', '+'), year)
                data = browser(urlbing_imdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|http://ssl-proxy.my-addr.org/myaddrproxy.php/", "", data)
                subdata_imdb = scrapertools.find_single_match(data,
                                                              '<li class="b_algo">(.*?)h="ID.*?<strong>.*?TV Series')
            else:
                urlbing_imdb = "http://www.bing.com/search?q=%s+%s+site:imdb.com" % (title_imdb.replace(' ', '+'), year)
                data = browser(urlbing_imdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|http://ssl-proxy.my-addr.org/myaddrproxy.php/", "", data)
                subdata_imdb = scrapertools.find_single_match(data, '<li class="b_algo">(.*?)h="ID.*?<strong>')
            try:
                imdb_id = scrapertools.get_match(subdata_imdb, '<a href=.*?http.*?imdb.com/title/(.*?)/.*?"')
            except:
                try:
                    imdb_id = scrapertools.get_match(subdata_imdb, '<a href=.*?http.*?imdb.com/.*?/title/(.*?)/.*?"')
                except:
                    imdb_id = ""
            otmdb = tmdb.Tmdb(external_id=imdb_id, external_source="imdb_id", tipo=tipo_ps, idioma_busqueda="es")
            id = otmdb.result.get("id")
            posterdb = otmdb.result.get("poster_path")
            if not posterdb:
                if "(" in title_imdb:
                    title = scrapertools.find_single_match(title_imdb, '\(.*?\)')
                    if item.contentType != "movie":
                        urlbing_imdb = "http://www.bing.com/search?q=%s+%s+tv+series+site:imdb.com" % (
                        title_imdb.replace(' ', '+'), year)
                        data = browser(urlbing_imdb)
                        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|http://ssl-proxy.my-addr.org/myaddrproxy.php/", "", data)
                        subdata_imdb = scrapertools.find_single_match(data,
                                                                      '<li class="b_algo">(.*?)h="ID.*?<strong>.*?TV Series')
                    else:
                        urlbing_imdb = "http://www.bing.com/search?q=%s+%s+site:imdb.com" % (
                        title_imdb.replace(' ', '+'), year)
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
                    otmdb = tmdb.Tmdb(external_id=imdb_id, external_source="imdb_id", tipo=tipo_ps,
                                      idioma_busqueda="es")
                    id = otmdb.result.get("id")
                    posterdb = otmdb.result.get("poster_path")
                    if not posterdb:
                        id = tiw = rating = tagline = id_tvdb = ""
                        fanart_4 = fanart_2 = fanart_3 = item.fanart
                        rating = "Sin Puntuación"
                        posterdb = tvf = item.thumbnail
                        fanart_info = item.fanart
                        thumbnail_art = item.thumbnail
                        extra = str(fanart_2) + "|" + str(fanart_3) + "|" + str(fanart_4) + "|" + str(id) + "|" + str(
                            tvf) + "|" + str(id_tvdb) + "|" + str(tiw) + "|" + str(rating)
                        if tipo_ps != "movie":
                            action = "findvideos_series"
                        else:
                            action = "findvideos"
                        itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action=action,
                                             thumbnail=item.thumbnail, fanart=item.fanart, extra=extra, folder=True))
                else:
                    if tipo_ps != "movie":
                        action = "findvideos_series"
                    else:
                        action = "findvideos"
                    id = tiw = rating = tagline = id_tvdb = ""
                    fanart_4 = fanart_2 = fanart_3 = item.fanart
                    rating = "Sin Puntuación"
                    posterdb = tvf = item.thumbnail
                    fanart_info = item.fanart
                    thumbnail_art = item.thumbnail
                    extra = str(fanart_2) + "|" + str(fanart_3) + "|" + str(fanart_4) + "|" + str(id) + "|" + str(
                        tvf) + "|" + str(id_tvdb) + "|" + str(tiw) + "|" + str(rating)
                    itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action=action,
                                         thumbnail=item.thumbnail, fanart=item.fanart, extra=extra,
                                         contentType=item.contentType, folder=True))
    if posterdb != item.thumbnail:
        if not "null" in posterdb:
            posterdb = "https://image.tmdb.org/t/p/original" + posterdb
        else:
            posterdb = item.thumbnail

        if otmdb.result.get("backdrop_path"):
            fanart = "https://image.tmdb.org/t/p/original" + otmdb.result.get("backdrop_path")
        else:
            fanart = item.fanart
        if sinopsis == "":
            if otmdb.result.get("'overview'"):
                sinopsis = otmdb.result.get("'overview'")
            else:
                sinopsis = ""
        if otmdb.result.get("vote_average"):
            rating = otmdb.result.get("vote_average")
        else:
            rating = "Sin puntuacíon"
        imagenes = []
        itmdb = tmdb.Tmdb(id_Tmdb=id, tipo=tipo_ps)
        images = itmdb.result.get("images")
        for key, value in images.iteritems():
            for detail in value:
                imagenes.append('https://image.tmdb.org/t/p/original' + detail["file_path"])
        if item.contentType != "movie":
            if itmdb.result.get("number_of_seasons"):
                season_number = itmdb.result.get("number_of_seasons")
            else:
                season_episode = ""
            if itmdb.result.get("number_of_episodes"):
                season_episode = itmdb.result.get("number_of_episodes")
            else:
                season_episode = ""
            if itmdb.result.get("status"):
                status = itmdb.result.get("status")
            else:
                status = ""
            if status == "Ended":
                status = "Finalizada"
            else:
                status = "En emisión"
            tagline = str(status) + " (Temporadas:" + str(season_number) + ",Episodios:" + str(season_episode) + ")"
            if itmdb.result.get("external_ids").get("tvdb_id"):
                id_tvdb = itmdb.result.get("external_ids").get("tvdb_id")
            else:
                id_tvdb = ""
        else:
            id_tvdb = ""
            if itmdb.result.get("tagline"):
                tagline = itmdb.result.get("tagline")
            else:
                tagline = ""
        if len(imagenes) >= 5:
            fanart_info = imagenes[1]
            fanart_2 = imagenes[2]
            fanart_3 = imagenes[3]
            fanart_4 = imagenes[4]
            if fanart == item.fanart:
                fanart = fanart_info
        elif len(imagenes) == 4:
            fanart_info = imagenes[1]
            fanart_2 = imagenes[2]
            fanart_3 = imagenes[3]
            fanart_4 = imagenes[1]
            if fanart == item.fanart:
                fanart = fanart_info
        elif len(imagenes) == 3:
            fanart_info = imagenes[1]
            fanart_2 = imagenes[2]
            fanart_3 = imagenes[1]
            fanart_4 = imagenes[0]
            if fanart == item.fanart:
                fanart = fanart_info
        elif len(imagenes) == 2:
            fanart_info = imagenes[1]
            fanart_2 = imagenes[0]
            fanart_3 = imagenes[1]
            fanart_4 = imagenes[1]
            if fanart == item.fanart:
                fanart = fanart_info
        else:
            fanart_info = fanart
            fanart_2 = fanart
            fanart_3 = fanart
            fanart_4 = fanart
        images_fanarttv = fanartv(item, id_tvdb, id)
        if item.contentType != "movie":
            url = item.url + "/episodios"
            action = "findvideos_series"
            if images_fanarttv:
                try:
                    thumbnail_art = images_fanarttv.get("hdtvlogo")[0].get("url")
                except:
                    try:
                        thumbnail_art = images_fanarttv.get("clearlogo")[0].get("url")
                    except:
                        thumbnail_art = posterdb
                if images_fanarttv.get("tvbanner"):
                    tvf = images_fanarttv.get("tvbanner")[0].get("url")
                elif images_fanarttv.get("tvthumb"):
                    tvf = images_fanarttv.get("tvthumb")[0].get("url")
                elif images_fanarttv.get("tvposter"):
                    tvf = images_fanarttv.get("tvposter")[0].get("url")
                else:
                    tvf = posterdb
                if images_fanarttv.get("tvthumb"):
                    thumb_info = images_fanarttv.get("tvthumb")[0].get("url")
                else:
                    thumb_info = thumbnail_art

                if images_fanarttv.get("hdclearart"):
                    tiw = images_fanarttv.get("hdclearart")[0].get("url")
                elif images_fanarttv.get("characterart"):
                    tiw = images_fanarttv.get("characterart")[0].get("url")
                elif images_fanarttv.get("hdtvlogo"):
                    tiw = images_fanarttv.get("hdtvlogo")[0].get("url")
                else:
                    tiw = ""
            else:
                tiw = ""
                tvf = thumbnail_info = thumbnail_art = posterdb
        else:
            url = item.url
            action = "findvideos"
            if images_fanarttv:
                if images_fanarttv.get("hdmovielogo"):
                    thumbnail_art = images_fanarttv.get("hdmovielogo")[0].get("url")
                elif images_fanarttv.get("moviethumb"):
                    thumbnail_art = images_fanarttv.get("moviethumb")[0].get("url")
                elif images_fanarttv.get("moviebanner"):
                    thumbnail_art = images_fanarttv.get("moviebanner")[0].get("url")
                else:
                    thumbnail_art = posterdb
                if images_fanarttv.get("moviedisc"):
                    tvf = images_fanarttv.get("moviedisc")[0].get("url")
                elif images_fanarttv.get("hdmovielogo"):
                    tvf = images_fanarttv.get("hdmovielogo")[0].get("url")
                else:
                    tvf = posterdb
                if images_fanarttv.get("hdmovieclearart"):
                    tiw = images_fanarttv.get("hdmovieclearart")[0].get("url")
                elif images_fanarttv.get("hdmovielogo"):
                    tiw = images_fanarttv.get("hdmovielogo")[0].get("url")
                else:
                    tiw = ""
            else:
                tiw = ""
                tvf = thumbnail_art = posterdb
        extra = str(fanart_2) + "|" + str(fanart_3) + "|" + str(fanart_4) + "|" + str(id) + "|" + str(tvf) + "|" + str(
            id_tvdb) + "|" + str(tiw) + "|" + str(rating) + "|" + tipo_ps
        itemlist.append(
            Item(channel=item.channel, title=item.title, url=url, action=action, thumbnail=thumbnail_art, fanart=fanart,
                 extra=extra, contentType=item.contentType, fulltitle=fulltitle, folder=True))
    title_info = "[COLOR powderblue][B]Info[/B][/COLOR]"
    extra = str(rating) + "|" + str(rating_filma) + "|" + str(id) + "|" + str(item.title) + "|" + str(
        id_tvdb) + "|" + str(tagline) + "|" + str(sinopsis) + "|" + str(critica) + "|" + str(thumbnail_art) + "|" + str(
        fanart_4)
    itemlist.append(Item(channel=item.channel, action="info", title=title_info, url=item.url, thumbnail=posterdb,
                         fanart=fanart_info, extra=extra, contentType=item.contentType, folder=False))
    return itemlist


def findvideos_series(item):
    logger.info()
    itemlist = []
    fanart = ""
    check_temp = []
    data = httptools.downloadpage(item.url).data
    if item.contentType != "movie":
        itmdb = tmdb.Tmdb(id_Tmdb=item.extra.split("|")[3], tipo=item.extra.split("|")[8])
        season = itmdb.result.get("seasons")
        check = "no"
        try:
            temp, bloque_enlaces = scrapertools.find_single_match(data, 'Temporada (\d+)(.*?)Temporada')
        except:
            if "no se agregaron" in data:
                temp = bloque_enlaces = ""
            else:
                temp, bloque_enlaces = scrapertools.find_single_match(data, 'Temporada (\d+)(.*?)<div class="enlaces">')
        if temp != "":
            thumbnail = ""
            if season:
                for detail in season:
                    if str(detail["season_number"]) == temp:
                        if detail["poster_path"]:
                            thumbnail = "https://image.tmdb.org/t/p/original" + detail["poster_path"]
            images_fanarttv = fanartv(item, item.extra.split("|")[5], item.extra.split("|")[3])
            if images_fanarttv:
                season_f = images_fanarttv.get("showbackground")
                if season_f:
                    for detail in season_f:
                        if str(detail["season"]) == temp:
                            if detail["url"]:
                                fanart = detail["url"]
                if fanart == "":
                    fanart = item.extra.split("|")[0]
                if thumbnail == "":
                    thumbnail = item.thumbnail
            itemlist.append(Item(channel=item.channel,
                                 title="[COLOR darkturquoise]Temporada[/COLOR] " + "[COLOR beige]" + temp + "[/COLOR]",
                                 url="", action="", thumbnail=thumbnail, fanart=fanart, extra="",
                                 contentType=item.contentType, folder=False))
        capitulos = scrapertools.find_multiple_matches(bloque_enlaces, 'href="([^"]+)".*?Episodio (\d+) - ([^<]+)')
        for url, epi, title in capitulos:
            if epi == "1":
                if epi in str(check_temp):
                    temp = int(temp) + 1
                    thumbnail = ""
                    if season:
                        for detail in season:
                            if detail["season_number"] == temp:
                                if detail["poster_path"]:
                                    thumbnail = "https://image.tmdb.org/t/p/original" + detail["poster_path"]
                    images_fanarttv = fanartv(item, item.extra.split("|")[5], item.extra.split("|")[3])
                    if images_fanarttv:
                        season_f = images_fanarttv.get("showbackground")
                        if season_f:
                            for detail in season_f:
                                if detail["season"] == temp:
                                    if detail["url"]:
                                        fanart = detail["url"]
                    if fanart == "":
                        fanart = item.extra.split("|")[0]
                    if thumbnail == "":
                        thumbnail = item.thumbnail
                    itemlist.append(Item(channel=item.channel,
                                         title="[COLOR darkturquoise]Temporada[/COLOR] " + "[COLOR beige]" + str(
                                             temp) + "[/COLOR]", url="", action="", thumbnail=thumbnail, fanart=fanart,
                                         extra="", contentType=item.contentType, folder=False))
            check_temp.append([epi])
            itemlist.append(Item(channel=item.channel,
                                 title="     [COLOR cyan]Episodio[/COLOR] " + "[COLOR darkcyan]" + epi + "[/COLOR]" + " - " + "[COLOR cadetblue]" + title + "[/COLOR]",
                                 url=url, action="findvideos", thumbnail=item.extra.split("|")[4],
                                 fanart=item.extra.split("|")[0], extra="", contentType=item.contentType, folder=True))
            title_info = "        Info"
            title_info = "[COLOR steelblue]" + title_info + "[/COLOR]"
            itemlist.append(Item(channel=item.channel, action="info_capitulos", title=title_info, url=item.url,
                                 thumbnail=item.extra.split("|")[6], fanart=item.extra.split("|")[1],
                                 extra=item.extra + "|" + str(temp) + "|" + epi, folder=False))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data

    if item.extra != "dd" and item.extra != "descarga":

        if item.contentType != "movie":
            bloque_links = scrapertools.find_single_match(data, '<div class="links">(.*?)<\/i>Selecciona un')
            if bloque_links == "":
                bloque_links = scrapertools.find_single_match(data, '<div class="links">(.*?)<div class="enlaces">')
        else:
            bloque_links = scrapertools.find_single_match(data, '<div class="links">(.*?)<\/i>Descargar')
            if bloque_links == "":
                bloque_links = scrapertools.find_single_match(data, '<div class="links">(.*?)<div class="enlaces">')
        links = scrapertools.find_multiple_matches(bloque_links,
                                                   '<a class="goto" rel="nofollow".*?data-id="([^<]+)".*?src="([^"]+)">([^<]+)<.*?src="([^"]+)">([^<]+).*?<span>([^<]+)')
        for id, thumb, server, idiomapng, idioma, calidad in links:
            idioma = idioma.strip()
            calidad = calidad.lower()
            calidad = re.sub(r' ', '-', calidad)
            if calidad == "ts":
                calidad = re.sub(r'ts', 'ts-hq', calidad)
            url = "http://peliculasgratis.biz/goto/"
            url_post = urllib.urlencode({'id': id})
            server_name = scrapertools.get_match(server, '(.*?)\.').strip()
            icon_server = os.path.join(config.get_runtime_path(), "resources", "images", "servers",
                                       "server_" + server_name + ".png")
            icon_server = icon_server.replace('streamin', 'streaminto')
            if not os.path.exists(icon_server):
                icon_server = thumb
            if CALIDADES.get(calidad):
                calidad = CALIDADES.get(calidad)
            else:
                calidad = "[COLOR brown]" + calidad + "[/COLOR]"
            if IDIOMAS.get(idioma):
                idioma = IDIOMAS.get(idioma)
            else:
                idioma = "[COLOR brown]" + idioma + "[/COLOR]"

            extra = "online"
            itemlist.append(Item(channel=item.channel,
                                 title="[COLOR lightcyan][B]" + server + "[/B][/COLOR] " + calidad + " " + idioma,
                                 url=url, action="play", thumbnail=icon_server, fanart="", contentType=item.contentType,
                                 folder=True, id=url_post))
    else:
        bloque_dd = scrapertools.find_single_match(data, '<\/i>Descargar(.*?)<div class="enlaces">')
        links_dd = scrapertools.find_multiple_matches(bloque_dd,
                                                      '<a class="low".*?data-id="(.*?)".*?src="([^"]+)">([^<]+)<.*?src[^<]+>([^<]+).*?<span>([^<]+)')
        for id, thumb, server, idioma, calidad in links_dd:
            idioma = idioma.strip()
            calidad = calidad.lower()
            calidad = re.sub(r' ', '-', calidad)
            if calidad == "ts":
                calidad = re.sub(r'ts', 'ts-hq', calidad)
            if CALIDADES.get(calidad):
                calidad = CALIDADES.get(calidad)
            else:
                calidad = "[COLOR brown]" + calidad + "[/COLOR]"
            if IDIOMAS.get(idioma):
                idioma = IDIOMAS.get(idioma)
            else:
                idioma = "[COLOR brown]" + idioma + "[/COLOR]"
            url = "http://peliculasgratis.biz/goto/"
            data_post = urllib.urlencode({'id': id})
            server_name = scrapertools.get_match(server, '(.*?)\.').strip()
            icon_server = os.path.join(config.get_runtime_path(), "resources", "images", "servers",
                                       "server_" + server_name + ".png")
            icon_server = icon_server.replace('streamin', 'streaminto')
            icon_server = icon_server.replace('ul', 'uploadedto')
            if not os.path.exists(icon_server):
                icon_server = thumb
            extra = "descarga"
            itemlist.append(
                item.clone(title="[COLOR floralwhite][B]" + server + "[/B][/COLOR] " + calidad + " " + idioma, url=url,
                           action="play", thumbnail=icon_server, fanart="", contentType=item.contentType, id=data_post))

    if item.contentType == "movie" and item.extra != "descarga" and item.extra != "online":

        if config.get_videolibrary_support() and len(itemlist) > 0:
            itemlist.append(Item(channel=item.channel, title="Añadir película a la videoteca",
                                 action="add_pelicula_to_library", url=item.url, text_color="green",
                                 infoLabels={'title': item.fulltitle}, thumbnail="http://imgur.com/xjrGmVM.png",
                                 fulltitle=item.fulltitle,
                                 extra=extra))
    if item.extra != "dd" and item.extra != "descarga" and item.extra != "online":
        bloque_dd = scrapertools.find_single_match(data, '<\/i>Descargar(.*?)<div class="enlaces">')
        if bloque_dd:
            itemlist.append(item.clone(title="[COLOR aqua][B]Ver enlaces Descarga[/B][/COLOR] ", action="findvideos",
                                       thumbnail=thumb, fanart="", contentType=item.contentType, bloque_dd=bloque_dd,
                                       extra="dd"))

    return itemlist


def play(item):
    itemlist = []
    data = httptools.downloadpage(item.url, post=item.id, ).data
    enlaces = scrapertools.find_single_match(data, '<a rel="nofollow" href="([^"]+)"')
    itemlist = servertools.find_video_items(data=enlaces)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.thumbnail = item.extra
        videoitem.extra = item.extra
        videoitem.channel = item.channel

    return itemlist


def info(item):
    logger.info()
    itemlist = []
    url = item.url
    rating_tmdba_tvdb = item.extra.split("|")[0]
    if item.extra.split("|")[6] == "":
        rating_tmdba_tvdb = "Sin puntuación"
    rating_filma = item.extra.split("|")[1]
    filma = "http://s6.postimg.org/6yhe5fgy9/filma.png"
    title = item.extra.split("|")[3]
    title = title.replace("%20", " ")
    try:
        if "." in rating_tmdba_tvdb:
            check_rat_tmdba = scrapertools.get_match(rating_tmdba_tvdb, '(\d+).')
        else:
            check_rat_tmdba = rating_tmdba_tvdb
        if int(check_rat_tmdba) >= 5 and int(check_rat_tmdba) < 8:
            rating = "[COLOR springgreen][B]" + rating_tmdba_tvdb + "[/B][/COLOR]"
        elif int(check_rat_tmdba) >= 8 or rating_tmdba_tvdb == 10:
            rating = "[COLOR yellow][B]" + rating_tmdba_tvdb + "[/B][/COLOR]"
        else:
            rating = "[COLOR crimson][B]" + rating_tmdba_tvdb + "[/B][/COLOR]"
            print "lolaymaue"
    except:
        rating = "[COLOR crimson][B]" + rating_tmdba_tvdb + "[/B][/COLOR]"
    if "10." in rating:
        rating = re.sub(r'10\.\d+', '10', rating)
    try:
        check_rat_filma = scrapertools.get_match(rating_filma, '(\d)')
        print "paco"
        print check_rat_filma
        if int(check_rat_filma) >= 5 and int(check_rat_filma) < 8:
            print "dios"
            print check_rat_filma
            rating_filma = "[COLOR springgreen][B]" + rating_filma + "[/B][/COLOR]"
        elif int(check_rat_filma) >= 8:

            print check_rat_filma
            rating_filma = "[COLOR yellow][B]" + rating_filma + "[/B][/COLOR]"
        else:
            rating_filma = "[COLOR crimson][B]" + rating_filma + "[/B][/COLOR]"
            print "rojo??"
            print check_rat_filma
    except:
        rating_filma = "[COLOR crimson][B]" + rating_filma + "[/B][/COLOR]"
    plot = item.extra.split("|")[6]
    plot = "[COLOR moccasin][B]" + plot + "[/B][/COLOR]"
    plot = re.sub(r"\\|<br />", "", plot)
    if item.extra.split("|")[5] != "":
        tagline = item.extra.split("|")[5]
        if tagline == "\"\"":
            tagline = " "
        tagline = "[COLOR aquamarine][B]" + tagline + "[/B][/COLOR]"
    else:
        tagline = ""
    if item.contentType != "movie":
        icon = "http://s6.postimg.org/hzcjag975/tvdb.png"
    else:
        icon = "http://imgur.com/SenkyxF.png"

    foto = item.extra.split("|")[9]
    if not "tmdb" in foto:
        foto = ""
    if item.extra.split("|")[7] != "":
        critica = item.extra.split("|")[7]
    else:
        critica = "Esta serie no tiene críticas..."

    photo = item.extra.split("|")[8].replace(" ", "%20")
    if ".jpg" in photo:
        photo = ""
    # Tambien te puede interesar
    peliculas = []
    if item.contentType != "movie":
        url_tpi = "http://api.themoviedb.org/3/tv/" + item.extra.split("|")[
            2] + "/recommendations?api_key=" + api_key + "&language=es"
        data_tpi = httptools.downloadpage(url_tpi).data
        tpi = scrapertools.find_multiple_matches(data_tpi,
                                                 'id":(.*?),.*?"original_name":"(.*?)",.*?"poster_path":(.*?),"popularity"')
    else:
        url_tpi = "http://api.themoviedb.org/3/movie/" + item.extra.split("|")[
            2] + "/recommendations?api_key=" + api_key + "&language=es"
        data_tpi = httptools.downloadpage(url_tpi).data
        tpi = scrapertools.find_multiple_matches(data_tpi,
                                                 'id":(.*?),.*?"original_title":"(.*?)",.*?"poster_path":(.*?),"popularity"')

    for idp, peli, thumb in tpi:

        thumb = re.sub(r'"|}', '', thumb)
        if "null" in thumb:
            thumb = "http://s6.postimg.org/tw1vhymj5/noposter.png"
        else:
            thumb = "https://image.tmdb.org/t/p/original" + thumb
        peliculas.append([idp, peli, thumb])

    extra = "" + "|" + item.extra.split("|")[2] + "|" + item.extra.split("|")[2] + "|" + item.extra.split("|")[
        6] + "|" + ""
    infoLabels = {'title': title, 'plot': plot, 'thumbnail': photo, 'fanart': foto, 'tagline': tagline,
                  'rating': rating}
    item_info = item.clone(info=infoLabels, icon=icon, extra=extra, rating=rating, rating_filma=rating_filma,
                           critica=critica, contentType=item.contentType, thumb_busqueda="http://imgur.com/Q0BTHyO.png")
    from channels import infoplus
    infoplus.start(item_info, peliculas)


def info_capitulos(item, images={}):
    logger.info()
    url = "https://api.themoviedb.org/3/tv/" + item.extra.split("|")[3] + "/season/" + item.extra.split("|")[
        9] + "/episode/" + item.extra.split("|")[10] + "?api_key=" + api_key + "&language=es"
    if "/0" in url:
        url = url.replace("/0", "/")
    from core import jsontools
    data = jsontools.load(scrapertools.downloadpage(url))
    foto = item.extra.split("|")[6]
    if not ".png" in foto:
        foto = "http://imgur.com/Q0BTHyO.png"
    if data:
        if data.get("name"):
            title = data.get("name")
        else:
            title = ""
        title = "[COLOR aqua][B]" + title + "[/B][/COLOR]"
        if data.get("still_path"):
            image = "https://image.tmdb.org/t/p/original" + data.get("still_path")
        else:
            image = "http://imgur.com/ZiEAVOD.png"
        if data.get("overview"):
            plot = data.get("overview")
        else:
            plot = "Sin informacion del capítulo aún..."
        plot = "[COLOR honeydew][B]" + plot + "[/B][/COLOR]"
        if data.get("vote_average"):
            rating = data.get("vote_average")
        else:
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


    else:

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

        self.background = xbmcgui.ControlImage(70, 20, 1150, 630, 'http://imgur.com/oWUdNFg.jpg')
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
