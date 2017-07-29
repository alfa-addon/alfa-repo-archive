# -*- coding: utf-8 -*-

import os
import re
import unicodedata
import urllib

import xbmc
import xbmcgui
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core.item import Item
from core.scrapertools import decodeHtmlentities as dhe
from platformcode import platformtools

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

krypton = False


# Proxy para acceder a datos(Este canal usa cloudflare con https)
def get_page(url):
    logger.info()
    global krypton
    xbmc_version = xbmc.getInfoLabel("System.BuildVersion")
    check_xbmc_version = scrapertools.get_match(xbmc_version, '(\d+).')

    if check_xbmc_version >= 17:
        krypton = True
        data = httptools.downloadpage(url).data
    else:
        data = httptools.downloadpage("http://ssl-proxy.my-addr.org/myaddrproxy.php/" + url).data

    return data


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
    br.addheaders = [('User-agent',
                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/7.1.7 Safari/537.85.16')]
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
    check_bg = item.action
    if str(check_bg) == "":
        check_bg = "bglobal"
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="[COLOR yellow][B]Peliculas[/B][/COLOR]", action="peliculas",
                         url="http://pasateatorrent.com/",
                         thumbnail="https://s6.postimg.org/j9amymu1d/dxtorrentpelo.png",
                         fanart="http://imgur.com/uexmGEg.png"))
    itemlist.append(Item(channel=item.channel, title="[COLOR skyblue][B]Series[/B][/COLOR]", action="peliculas",
                         url="http://pasateatorrent.com//series/",
                         thumbnail="https://s6.postimg.org/6vxsrq4cx/dxtorrentselo.png",
                         fanart="http://imgur.com/vQTyY6r.png"))

    itemlist.append(Item(channel=item.channel, title="[COLOR green][B]Buscar[/B][/COLOR]", action="", url="",
                         thumbnail="https://s6.postimg.org/hy2vq5yfl/dxtorrentbpelo.png",
                         fanart="http://imgur.com/P9jol7f.png"))

    itemlist.append(
        Item(channel=item.channel, title="         " + "[COLOR yellow]Peliculas[/COLOR]", action="search", url="",
             thumbnail="https://s6.postimg.org/79z4rbogh/dxtorrentpbselo.png", fanart="http://imgur.com/W7iwPvD.png",
             extra="peliculas" + "|" + check_bg))
    itemlist.append(
        Item(channel=item.channel, title="         " + "[COLOR skyblue]Series[/COLOR]", action="search", url="",
             thumbnail="https://s6.postimg.org/hy2vq5yfl/dxtorrentbpelo.png", fanart="http://imgur.com/BD86Wdn.png",
             extra="series" + "|" + check_bg))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    check_bg = item.action
    if item.extra:
        if item.extra.split("|")[0] == "series":
            item.url = "http://pasateatorrent.com/series/?s=%s&post_type=Buscar+serie" % (texto)
            check_sp = "tvshow"
        else:
            item.url = "http://pasateatorrent.com/?s=%s&post_type=Buscar+película" % (texto)
            check_sp = "peliculas"
        item.extra = "search" + "|" + item.extra.split("|")[1] + "|" + texto + "|" + check_sp

        try:
            return peliculas(item)
        # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
        except:
            import sys
            for line in sys.exc_info():
                logger.error("%s" % line)
    else:
        if item.contentType != "movie":
            item.url = "http://pasateatorrent.com/series/?s=%s&post_type=Buscar+serie" % (texto)
            check_sp = "tvshow"
        else:
            item.url = "http://pasateatorrent.com/?s=%s&post_type=Buscar+película" % (texto)
            check_sp = "peliculas"
        item.extra = "search" + "|" + "bglobal" + "|" + texto + "|" + check_sp

        try:
            return peliculas(item)
        # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
        except:
            import sys
            for line in sys.exc_info():
                logger.error("%s" % line)


def peliculas(item):
    logger.info()
    itemlist = []
    global krypton
    check_url = ""
    # Descarga la página
    data = get_page(item.url)
    # data =re.sub("-"," ",data)
    if "serie" in item.url:
        data = re.sub(r"&#.*?;", "x", data)
    if item.extra.split("|")[0] == "search":
        check_bg = item.action
        bloque_enlaces = scrapertools.find_single_match(data,
                                                        '<div class="contenedor_imagenes">(.*?)<center><\/center>')
        bloque_enlaces = bloque_enlaces.strip()
        if item.extra.split("|")[1] != "bglobal" and check_bg != "info":
            if str(bloque_enlaces) == "</div>":
                if item.extra.split("|")[3] == "peliculas":
                    dialog = xbmcgui.Dialog()
                    if dialog.yesno(
                                                    '[COLOR crimson][B]Sin resultados en[/B][/COLOR]' + '[COLOR gold][B] Pasate[/B][/COLOR]' + '[COLOR floralwhite][B]A[/B][/COLOR]' + '[COLOR yellow][B]Torrent[/B][/COLOR]',
                                                    '[COLOR cadetblue]¿Quieres hacer una busqueda en Alfa?[/COLOR]',
                                                    '', "", '[COLOR crimson][B]No,gracias[/B][/COLOR]',
                                                    '[COLOR yellow][B]Si[/B][/COLOR]'):
                        item.extra = "movie" + "|" + item.extra.split("|")[2]
                        return busqueda(item)
                    else:
                        xbmc.executebuiltin('Action(Back)')
                        xbmc.sleep(500)
                else:
                    dialog = xbmcgui.Dialog()
                    if dialog.yesno(
                                                    '[COLOR crimson][B]Sin resultados en[/B][/COLOR]' + '[COLOR slateblue][B] Pasate[/B][/COLOR]' + '[COLOR floralwhite][B]A[/B][/COLOR]' + '[COLOR slateblue][B]Torrent[/B][/COLOR]',
                                                    '[COLOR cadetblue]¿Quieres hacer una busqueda en Alfa?[/COLOR]',
                                                    '', "", '[COLOR crimson][B]No,gracias[/B][/COLOR]',
                                                    '[COLOR yellow][B]Si[/B][/COLOR]'):
                        item.extra = "serie" + "|" + item.extra.split("|")[2]
                        return busqueda(item)
                    else:
                        xbmc.executebuiltin('Action(Back)')
                        xbmc.sleep(500)
    else:
        bloque_enlaces = scrapertools.find_single_match(data,
                                                        '<div class="contenedor_imagenes">(.*?)<center><div class="navigation">')
    if krypton:
        patron = '<a href="https://([^"]+)/".*?src="https://([^"]+)".*?class="bloque_inferior">(.*?)<\/div>'
        matches = re.compile(patron, re.DOTALL).findall(bloque_enlaces)

    else:

        patron = '<a href="\/myaddrproxy.php\/https\/([^"]+)/".*?src="\/myaddrproxy.php\/https\/([^"]+)".*?class="bloque_inferior">(.*?)<\/div>'
        matches = re.compile(patron, re.DOTALL).findall(bloque_enlaces)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        if not item.extra == "search":
            calidad = scrapertools.find_single_match(data, 'class="bloque_superior">(.*?)<\/div>')

        if "search" in item.extra:
            scrapedtitle = re.sub(r'La Saga|Saga|Tetralogía|Tetralogia|Trilogía|Triloga|Pentalogía|Pentalogia', '',
                                  scrapedtitle)
        scrapedtitle = re.sub('<br>', '', scrapedtitle)
        scrapedurl = "http://" + scrapedurl
        if "serie" in item.url:
            scrapedurl = re.sub(r' \d+x\d+| \d+', '', scrapedurl).strip()
            scrapedurl = re.sub(r' ', '-', scrapedurl).strip()
        scrapedthumbnail = "http://" + scrapedthumbnail
        scrapedthumbnail = re.sub(r' ', '-', scrapedthumbnail)
        title_fan = re.sub(
            r"\[.*?\]|\(.*?\)|\d+x\d+.*?Final|-\d+|-|\d+x\d+|Temporada.*?Completa| ;|Serie Completa|Especial.*", "",
            scrapedtitle).strip()
        if not "100" in scrapedtitle:
            title_fan = re.sub(r"\d+", "", title_fan)
        title_serie = re.sub('<br>.*', '', scrapedtitle)
        if "serie" in item.url:
            try:
                check_temp, check_serie = scrapertools.find_single_match(title_serie, '(\d+)x\d+ (\d+)')
                if check_serie:
                    title_serie = title_serie.replace(" " + check_serie, "-" + check_serie)
                if check_temp:
                    scrapedurl = scrapedurl + "-temporada-" + check_temp
            except:
                try:
                    check_temp, check_serie = scrapertools.find_single_match(title_serie, '(\d+)x\d+-(\d+)')
                except:
                    try:
                        check_temp, check_serie = scrapertools.find_single_match(title_serie, '(\d+)-(\d+)')
                    except:
                        check_serie = ""

        title = scrapedtitle.title()
        if "series" in scrapedurl:
            # title_fan= re.sub(r'')
            trailer = title_fan + " " + "series" + "trailer"
            title = "[COLOR skyblue][B]" + title_serie + "[/B][/COLOR]"

        else:
            title = "[COLOR yellow][B]" + scrapedtitle + "[/B][/COLOR]"
            trailer = title_fan + " " + "trailer"

        trailer = urllib.quote(trailer)
        extra = trailer + "|" + title_fan + "|" + "pelicula" + "|" + item.extra
        if "Saga" in title or "Serie Completa" in title or "Tetralogía" in title or "Tetralogia" in title or "Trilogía" in title or "Trilogia" in title or "Pentalogía" in title or "Pentalogia" in title or "Pack Peliculas" in title or "Pack Películas" in title or "Duología" in title or "Duologia" in title:
            if "serie" in item.url:
                if krypton:
                    l_scrapedurl = re.sub(r"http://", "http/", scrapedurl)
                    l_scrapedurl = "http://ssl-proxy.my-addr.org/myaddrproxy.php/" + scrapedurl
                else:
                    l_scrapedurl = scrapedurl
                url = scrapertools.get_header_from_response(l_scrapedurl, header_to_get="location")
                check_url = scrapertools.get_header_from_response(url, header_to_get="location")
                if "series/?s" in check_url:
                    scrapedurl = re.sub(r" ", "-", scrapedurl.strip())
                    action = "peliculas"
                    pepe = "search" + "|" + " "
                    check_bg = ""
                else:
                    check_url = "capitulos"
                    action = "fanart"
                    pepe = extra
            else:
                scrapedurl = re.sub(r" ", "-", scrapedurl.strip())
                action = "peliculas"
                pepe = "search" + "|" + " "
                check_bg = ""
        else:
            action = "fanart"
            pepe = extra
        itemlist.append(
            Item(channel=item.channel, title=title, url=scrapedurl, action=action, thumbnail=scrapedthumbnail,
                 fanart=item.fanart, extra=pepe, folder=True))

        if "series" in item.url and not "Completa" in scrapedtitle and check_serie == "" and not "Temporada" in title_serie:
            xbmc.log("pocoyoespajo")
            xbmc.log(scrapedtitle)
            url_1 = re.compile('([^<]+) (\d+).*?(\d+)', re.DOTALL).findall(scrapedtitle)
            for title_capitulo, temp, epi in url_1:
                xbmc.log("pocoyoespajo")
                xbmc.log(scrapedtitle)
            if "serie-completa" in scrapedurl:
                title = "[COLOR cyan]        Ver capitulos de temporada[/COLOR]"
            else:
                title = "[COLOR cyan]Ver capitulo[/COLOR]" + " " + "[COLOR slateblue]" + temp + "x" + epi + "[/COLOR]"
            # url = "http://descargaportorrent.net/series/"+url_2+"-temporada-"+temp
            extra = temp + "|" + epi + "|" + scrapedtitle
            if "Especial" in scrapedtitle:
                title = "[COLOR cyan]   Ver capitulo especial[/COLOR]"
                extra = "" + "|" + "Especial" + "|" + scrapedtitle
            itemlist.append(Item(channel=item.channel, title="        " + title, url=scrapedurl, action="ver_capitulo",
                                 thumbnail=scrapedthumbnail, fanart=item.fanart, extra=extra, folder=True))
        else:
            if item.extra != "search" or item.extra == "search" and not "Saga" in title and not "Serie Completa" in title and not "Tetralogia" in title and not "Tetralogia" in title and not "Trilogía" in title and not "Trilogia" in title and not "Pentalogía" in title and not "Pentalogia" in title and not "Pack Peliculas" in title and not "Pack Películas" in title or not "Duología" in title or not "Duologia" in title:
                if "series" in scrapedurl and not "Serie Completa" in title:

                    if "Temporada" in scrapedtitle:
                        title = "[COLOR cyan]        Ver capitulos de temporada[/COLOR]"
                    else:
                        title = "[COLOR cyan]        Ver Capitulos[/COLOR]"

                else:

                    if not "Completa" in title and not "Tetralogía" in title and not "Tetralogia" in title and not "Saga" in title and not "Trilogía" in title and not "Trilogia" in title and not "Pentalogía" in title and not "Pentalogia" in title and not "Pack Películas" in title and not "Pack Peliculas" in title and not "Duología" in title and not "Duologia" in title:
                        title = "[COLOR khaki]        Ver pelicula[/COLOR]"
                    else:
                        if "Serie Completa" in title and check_url == "capitulos":
                            title = "[COLOR cyan]        Ver Capitulos[/COLOR]"
                        else:
                            continue
                itemlist.append(Item(channel=item.channel, title=title, url=scrapedurl, action="ver_capitulo",
                                     thumbnail=scrapedthumbnail, fanart=item.fanart, extra=extra, folder=True))
    ## Paginación
    if krypton:
        patronvideos = '<li class="barranav"><a href="([^"]+)" >P'
        matches = re.compile(patronvideos, re.DOTALL).findall(data)

    else:
        patronvideos = '<li class="barranav">.*?<a href="/myaddrproxy.php/https/([^"]+)" >Página siguiente '
        matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches) > 0:
        scrapedurl = matches[0]
        if krypton:
            url = scrapedurl
        else:
            url = "http://" + scrapedurl
        title = "siguiente>>"
        title = "[COLOR slategray]" + title + "[/COLOR]"
        itemlist.append(Item(channel=item.channel, action="peliculas", title=title, url=url,
                             thumbnail="http://s6.postimg.org/drfhhwrtd/muarrow.png", fanart=item.fanart, folder=True))

    return itemlist


def fanart(item):
    logger.info()
    itemlist = []
    url = item.url
    data = get_page(url)
    title_fan = item.extra.split("|")[1]
    title = re.sub(r'Serie Completa|Temporada.*', '', title_fan)
    if "series" in item.url and not "temporada" in item.url:
        item.title = re.sub(r'\d+x\d+.*?Final|-\d+|-|\d+x\d+|\d+', '', item.title)
        item.title = re.sub(r'Especial.*?\[', '[', item.title)
    title = title.replace(' ', '%20')
    title = ''.join((c for c in unicodedata.normalize('NFD', unicode(title.decode('utf-8'))) if
                     unicodedata.category(c) != 'Mn')).encode("ascii", "ignore")

    item.plot = item.extra.split("|")[0]
    try:
        year = scrapertools.get_match(data, '<div class="ano_page_exit">(\d\d\d\d)')
    except:
        year = ""
    try:
        sinopsis = scrapertools.get_match(data, 'Sinopsis.*?<p>(.*?)</p>')
    except:
        sinopsis = ""
    if not "series" in item.url:

        # filmafinity
        url = "http://www.filmaffinity.com/es/advsearch.php?stext={0}&stype%5B%5D=title&country=&genre=&fromyear={1}&toyear={1}".format(
            title, year)
        data = httptools.downloadpage(url).data

        url_filmaf = scrapertools.find_single_match(data, '<div class="mc-poster">\s*<a title="[^"]*" href="([^"]+)"')
        if url_filmaf:
            url_filmaf = "http://www.filmaffinity.com%s" % url_filmaf
            data = httptools.downloadpage(url_filmaf).data
        else:

            try:
                url_bing = "http://www.bing.com/search?q=%s+%s+site:filmaffinity.com" % (title.replace(' ', '+'), year)
                data = browser(url_bing)
                data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

                if "myaddrproxy.php" in data:
                    subdata_bing = scrapertools.get_match(data,
                                                          'li class="b_algo"><div class="b_title"><h2>(<a href="/ myaddrproxy.php/http/www.filmaffinity.com/es/film.*?)"')
                    subdata_bing = re.sub(r'\/myaddrproxy.php\/http\/', '', subdata_bing)
                else:
                    subdata_bing = scrapertools.get_match(data,
                                                          'li class="b_algo"><h2>(<a href="http://www.filmaffinity.com/es/film.*?)"')

                url_filma = scrapertools.get_match(subdata_bing, '<a href="([^"]+)')

                if not "http" in url_filma:
                    data = httptools.downloadpage("http://" + url_filma).data
                else:
                    data = httptools.downloadpage(url_filma).data
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

            except:
                pass
        if sinopsis == " ":
            try:
                sinopsis = scrapertools.find_single_match(data, '<dd itemprop="description">(.*?)</dd>')
                sinopsis = sinopsis.replace("<br><br />", "\n")
                sinopsis = re.sub(r"\(FILMAFFINITY\)<br />", "", sinopsis)
            except:
                pass
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
            critica = "[COLOR floralwhite][B]Esta película no tiene críticas todavía...[/B][/COLOR]"
        print "ozuu"
        print critica

        url = "http://api.themoviedb.org/3/search/movie?api_key=" + api_key + "&query=" + title + "&year=" + year + "&language=es&include_adult=false"
        data = httptools.downloadpage(url).data
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        patron = '"page":1.*?,"id":(.*?),.*?"backdrop_path":(.*?),'
        matches = re.compile(patron, re.DOTALL).findall(data)

        if len(matches) == 0:

            title = re.sub(r":.*|\(.*?\)", "", title)
            url = "http://api.themoviedb.org/3/search/movie?api_key=" + api_key + "&query=" + title + "&language=es&include_adult=false"

            data = httptools.downloadpage(url).data
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            patron = '"page":1.*?,"id":(.*?),.*?"backdrop_path":(.*?),'
            matches = re.compile(patron, re.DOTALL).findall(data)
            if len(matches) == 0:
                extra = item.thumbnail + "|" + "" + "|" + "" + "|" + "Sin puntuacón" + "|" + rating_filma + "|" + critica
                show = "http://imgur.com/c3rzL6x.jpg" + "|" + "" + "|" + sinopsis
                posterdb = item.thumbnail
                fanart_info = "http://imgur.com/c3rzL6x.jpg"
                fanart_3 = ""
                fanart_2 = "http://imgur.com/c3rzL6x.jpg"
                category = item.thumbnail
                id_scraper = ""

                itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                     thumbnail=item.thumbnail, fanart="http://imgur.com/c3rzL6x.jpg", extra=extra,
                                     show=show, category=category, folder=True))

        for id, fan in matches:

            fan = re.sub(r'\\|"', '', fan)

            try:
                rating = scrapertools.find_single_match(data, '"vote_average":(.*?),')
            except:
                rating = "Sin puntuación"

            id_scraper = id + "|" + "peli" + "|" + rating + "|" + rating_filma + "|" + critica
            try:
                posterdb = scrapertools.get_match(data, '"page":1,.*?"poster_path":"\\\(.*?)"')
                posterdb = "https://image.tmdb.org/t/p/original" + posterdb
            except:
                posterdb = item.thumbnail

            if "null" in fan:
                fanart = "http://imgur.com/c3rzL6x.jpg"
            else:
                fanart = "https://image.tmdb.org/t/p/original" + fan
            item.extra = fanart

            url = "http://api.themoviedb.org/3/movie/" + id + "/images?api_key=" + api_key + ""
            data = httptools.downloadpage(url).data
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

            patron = '"backdrops".*?"file_path":".*?",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)"'
            matches = re.compile(patron, re.DOTALL).findall(data)

            if len(matches) == 0:
                patron = '"backdrops".*?"file_path":"(.*?)",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)"'
                matches = re.compile(patron, re.DOTALL).findall(data)
                if len(matches) == 0:
                    fanart_info = item.extra
                    fanart_3 = ""
                    fanart_2 = item.extra
            for fanart_info, fanart_3, fanart_2 in matches:
                fanart_info = "https://image.tmdb.org/t/p/original" + fanart_info
                fanart_3 = "https://image.tmdb.org/t/p/original" + fanart_3
                fanart_2 = "https://image.tmdb.org/t/p/original" + fanart_2

            # clearart, fanart_2 y logo
            url = "http://webservice.fanart.tv/v3/movies/" + id + "?api_key=" + api_fankey
            data = httptools.downloadpage(url).data
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            patron = '"hdmovielogo":.*?"url": "([^"]+)"'
            matches = re.compile(patron, re.DOTALL).findall(data)

            if '"moviedisc"' in data:
                disc = scrapertools.get_match(data, '"moviedisc":.*?"url": "([^"]+)"')
            if '"movieposter"' in data:
                poster = scrapertools.get_match(data, '"movieposter":.*?"url": "([^"]+)"')
            if '"moviethumb"' in data:
                thumb = scrapertools.get_match(data, '"moviethumb":.*?"url": "([^"]+)"')
            if '"moviebanner"' in data:
                banner = scrapertools.get_match(data, '"moviebanner":.*?"url": "([^"]+)"')

            if len(matches) == 0:
                extra = posterdb
                # "http://es.seaicons.com/wp-content/uploads/2015/11/Editing-Overview-Pages-1-icon.png"
                show = fanart_2 + "|" + fanart_3 + "|" + sinopsis
                category = posterdb

                itemlist.append(
                    Item(channel=item.channel, title=item.title, action="findvideos", url=item.url, server="torrent",
                         thumbnail=posterdb, fanart=item.extra, extra=extra, show=show, category=category, folder=True))
            for logo in matches:
                if '"hdmovieclearart"' in data:
                    clear = scrapertools.get_match(data, '"hdmovieclearart":.*?"url": "([^"]+)"')
                    if '"moviebackground"' in data:

                        extra = clear
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis
                        if '"moviedisc"' in data:
                            category = disc
                        else:
                            category = clear
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,
                                             show=show, category=category, folder=True))
                    else:
                        extra = clear
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis
                        if '"moviedisc"' in data:
                            category = disc
                        else:
                            category = clear
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,
                                             show=show, category=category, folder=True))

                if '"moviebackground"' in data:

                    if '"hdmovieclearart"' in data:
                        clear = scrapertools.get_match(data, '"hdmovieclearart":.*?"url": "([^"]+)"')
                        extra = clear
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis
                        if '"moviedisc"' in data:
                            category = disc
                        else:
                            category = clear
                    else:
                        extra = logo
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis
                        if '"moviedisc"' in data:
                            category = disc
                        else:
                            category = logo

                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,
                                             show=show, category=category, folder=True))

                if not '"hdmovieclearart"' in data and not '"moviebackground"' in data:
                    extra = logo
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis
                    if '"moviedisc"' in data:
                        category = disc
                    else:
                        category = item.extra
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                         server="torrent", thumbnail=logo, fanart=item.extra, extra=extra, show=show,
                                         category=category, folder=True))


    else:

        # filmafinity
        url = "http://www.filmaffinity.com/es/advsearch.php?stext={0}&stype%5B%5D=title&country=&ggenre=TV_SE&fromyear={1}&toyear={1}".format(
            title, year)
        data = httptools.downloadpage(url).data

        url_filmaf = scrapertools.find_single_match(data, '<div class="mc-poster">\s*<a title="[^"]*" href="([^"]+)"')
        if url_filmaf:
            url_filmaf = "http://www.filmaffinity.com%s" % url_filmaf
            data = httptools.downloadpage(url_filmaf).data
        else:

            try:
                url_bing = "http://www.bing.com/search?q=%s+%s+site:filmaffinity.com" % (title.replace(' ', '+'), year)
                data = browser(url_bing)
                data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

                if "myaddrproxy.php" in data:
                    subdata_bing = scrapertools.get_match(data,
                                                          'li class="b_algo"><div class="b_title"><h2>(<a href="/ myaddrproxy.php/http/www.filmaffinity.com/es/film.*?)"')
                    subdata_bing = re.sub(r'\/myaddrproxy.php\/http\/', '', subdata_bing)
                else:
                    subdata_bing = scrapertools.get_match(data,
                                                          'li class="b_algo"><h2>(<a href="http://www.filmaffinity.com/es/film.*?)"')

                url_filma = scrapertools.get_match(subdata_bing, '<a href="([^"]+)')
                if not "http" in url_filma:
                    data = httptools.downloadpage("http://" + url_filma).data
                else:
                    data = httptools.downloadpage(url_filma).data
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

            except:
                pass
        if sinopsis == " ":
            try:
                sinopsis = scrapertools.find_single_match(data, '<dd itemprop="description">(.*?)</dd>')
                sinopsis = sinopsis.replace("<br><br />", "\n")
                sinopsis = re.sub(r"\(FILMAFFINITY\)<br />", "", sinopsis)
            except:
                pass
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
            critica = "[COLOR floralwhite][B]Esta serie no tiene críticas[/B][/COLOR]"

        ###Busqueda en tmdb

        url_tmdb = "http://api.themoviedb.org/3/search/tv?api_key=" + api_key + "&query=" + title + "&language=es&include_adult=false&first_air_date_year=" + year
        data_tmdb = scrapertools.cachePage(url_tmdb)
        data_tmdb = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data_tmdb)
        patron = '"page":1.*?,"id":(.*?)".*?"backdrop_path":(.*?),'
        matches = re.compile(patron, re.DOTALL).findall(data_tmdb)
        ###Busqueda en bing el id de imdb de la serie
        if len(matches) == 0:
            url_tmdb = "http://api.themoviedb.org/3/search/tv?api_key=" + api_key + "&query=" + title + "&language=es"
            data_tmdb = scrapertools.cachePage(url_tmdb)
            data_tmdb = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data_tmdb)
            patron = '"page":1.*?,"id":(.*?),"backdrop_path":(.*?),'
            matches = re.compile(patron, re.DOTALL).findall(data_tmdb)
            if len(matches) == 0:
                urlbing_imdb = "http://www.bing.com/search?q=%s+%s+tv+series+site:imdb.com" % (
                title.replace(' ', '+'), year)
                data = browser(urlbing_imdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|http://ssl-proxy.my-addr.org/myaddrproxy.php/", "", data)
                try:
                    subdata_imdb = scrapertools.find_single_match(data,
                                                                  '<li class="b_algo">(.*?)h="ID.*?<strong>.*?TV Series')
                except:
                    pass

                try:
                    imdb_id = scrapertools.get_match(subdata_imdb, '<a href=.*?http.*?imdb.com/title/(.*?)/.*?"')
                except:
                    imdb_id = ""
                ###Busca id de tvdb y tmdb mediante imdb id

                urlremotetbdb = "https://api.themoviedb.org/3/find/" + imdb_id + "?api_key=" + api_key + "&external_source=imdb_id&language=es"
                data_tmdb = scrapertools.cachePage(urlremotetbdb)
                matches = scrapertools.find_multiple_matches(data_tmdb,
                                                             '"tv_results":.*?"id":(.*?),.*?"poster_path":(.*?),')

                if len(matches) == 0:
                    id_tmdb = ""
                    fanart_3 = ""
                    extra = item.thumbnail + "|" + year + "|" + "no data" + "|" + "no data" + "|" + "Sin puntuación" + "|" + "" + "|" + "" + "|" + id_tmdb
                    show = "http://imgur.com/ldWNcHm.jpg" + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + item.thumbnail + "|" + id_tmdb
                    fanart_info = "http://imgur.com/ldWNcHm.jpg"
                    fanart_2 = "http://imgur.com/ldWNcHm.jpg"
                    id_scraper = ""
                    category = ""
                    posterdb = item.thumbnail
                    itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                         thumbnail=item.thumbnail, fanart="http://imgur.com/ldWNcHm.jpg", extra=extra,
                                         category=category, show=show, folder=True))

        for id_tmdb, fan in matches:
            ###Busca id tvdb
            urlid_tvdb = "https://api.themoviedb.org/3/tv/" + id_tmdb + "/external_ids?api_key=" + api_key + "&language=es"
            data_tvdb = scrapertools.cachePage(urlid_tvdb)
            id = scrapertools.find_single_match(data_tvdb, 'tvdb_id":(.*?),"tvrage_id"')
            if id == "null":
                id = ""
            category = id
            ###Busqueda nºepisodios y temporadas,status
            url_status = "http://api.themoviedb.org/3/tv/" + id_tmdb + "?api_key=" + api_key + "&append_to_response=credits&language=es"
            data_status = scrapertools.cachePage(url_status)
            season_episodes = scrapertools.find_single_match(data_status,
                                                             '"(number_of_episodes":\d+,"number_of_seasons":\d+,)"')
            season_episodes = re.sub(r'"', '', season_episodes)
            season_episodes = re.sub(r'number_of_episodes', 'Episodios ', season_episodes)
            season_episodes = re.sub(r'number_of_seasons', 'Temporadas', season_episodes)
            season_episodes = re.sub(r'_', ' ', season_episodes)
            status = scrapertools.find_single_match(data_status, '"status":"(.*?)"')
            if status == "Ended":
                status = "Finalizada"
            else:
                status = "En emisión"
            status = status + " (" + season_episodes + ")"
            status = re.sub(r',', '.', status)
            #######

            fan = re.sub(r'\\|"', '', fan)
            try:
                # rating tvdb
                url_rating_tvdb = "http://thetvdb.com/api/1D62F2F90030C444/series/" + id + "/es.xml"
                print "pepote"
                print url_rating_tvdb
                data = httptools.downloadpage(url_rating_tvdb).data
                rating = scrapertools.find_single_match(data, '<Rating>(.*?)<')
            except:
                ratintg_tvdb = ""
                try:
                    rating = scrapertools.get_match(data, '"vote_average":(.*?),')
                except:

                    rating = "Sin puntuación"

            id_scraper = id_tmdb + "|" + "serie" + "|" + rating_filma + "|" + critica + "|" + rating + "|" + status  # +"|"+emision
            posterdb = scrapertools.find_single_match(data_tmdb, '"poster_path":(.*?)",')

            if "null" in posterdb:
                posterdb = item.thumbnail
            else:
                posterdb = re.sub(r'\\|"', '', posterdb)
                posterdb = "https://image.tmdb.org/t/p/original" + posterdb
            if "null" in fan:
                fanart = "http://imgur.com/ldWNcHm.jpg"
            else:
                fanart = "https://image.tmdb.org/t/p/original" + fan

            item.extra = fanart

            url = "http://api.themoviedb.org/3/tv/" + id_tmdb + "/images?api_key=" + api_key

            data = httptools.downloadpage(url).data
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

            patron = '"backdrops".*?"file_path":".*?",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)"'
            matches = re.compile(patron, re.DOTALL).findall(data)

            if len(matches) == 0:
                patron = '"backdrops".*?"file_path":"(.*?)",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)"'
                matches = re.compile(patron, re.DOTALL).findall(data)
                if len(matches) == 0:
                    fanart_info = item.extra
                    fanart_3 = ""
                    fanart_2 = item.extra
            for fanart_info, fanart_3, fanart_2 in matches:
                if fanart == "http://imgur.com/ldWNcHm.jpg":
                    fanart = "https://image.tmdb.org/t/p/original" + fanart_info
                fanart_info = "https://image.tmdb.org/t/p/original" + fanart_info
                fanart_3 = "https://image.tmdb.org/t/p/original" + fanart_3
                fanart_2 = "https://image.tmdb.org/t/p/original" + fanart_2
            url = "http://webservice.fanart.tv/v3/tv/" + id + "?api_key=" + api_fankey
            data = httptools.downloadpage(url).data
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            patron = '"clearlogo":.*?"url": "([^"]+)"'
            matches = re.compile(patron, re.DOTALL).findall(data)
            if '"tvbanner"' in data:
                tvbanner = scrapertools.get_match(data, '"tvbanner":.*?"url": "([^"]+)"')
                tfv = tvbanner
            elif '"tvposter"' in data:
                tvposter = scrapertools.get_match(data, '"tvposter":.*?"url": "([^"]+)"')
                tfv = tvposter
            else:
                tfv = posterdb
            if '"tvthumb"' in data:
                tvthumb = scrapertools.get_match(data, '"tvthumb":.*?"url": "([^"]+)"')
            if '"hdtvlogo"' in data:
                hdtvlogo = scrapertools.get_match(data, '"hdtvlogo":.*?"url": "([^"]+)"')
            if '"hdclearart"' in data:
                hdtvclear = scrapertools.get_match(data, '"hdclearart":.*?"url": "([^"]+)"')
            if len(matches) == 0:
                if '"hdtvlogo"' in data:
                    if "showbackground" in data:

                        if '"hdclearart"' in data:
                            thumbnail = hdtvlogo
                            extra = hdtvclear + "|" + year
                            show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                        else:
                            thumbnail = hdtvlogo
                            extra = thumbnail + "|" + year
                            show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=thumbnail, fanart=item.extra,
                                             category=category, extra=extra, show=show, folder=True))


                    else:
                        if '"hdclearart"' in data:
                            thumbnail = hdtvlogo
                            extra = hdtvclear + "|" + year
                            show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                        else:
                            thumbnail = hdtvlogo
                            extra = thumbnail + "|" + year
                            show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                             show=show, category=category, folder=True))
                else:
                    extra = "" + "|" + year
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                         server="torrent", thumbnail=posterdb, fanart=fanart, extra=extra, show=show,
                                         category=category, folder=True))

            for logo in matches:
                if '"hdtvlogo"' in data:
                    thumbnail = hdtvlogo
                elif not '"hdtvlogo"' in data:
                    if '"clearlogo"' in data:
                        thumbnail = logo
                else:
                    thumbnail = item.thumbnail
                if '"clearart"' in data:
                    clear = scrapertools.get_match(data, '"clearart":.*?"url": "([^"]+)"')
                    if "showbackground" in data:

                        extra = clear + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                             show=show, category=category, folder=True))
                    else:
                        extra = clear + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                             show=show, category=category, folder=True))

                if "showbackground" in data:

                    if '"clearart"' in data:
                        clear = scrapertools.get_match(data, '"clearart":.*?"url": "([^"]+)"')
                        extra = clear + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                    else:
                        extra = logo + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                             show=show, category=category, folder=True))

                if not '"clearart"' in data and not '"showbackground"' in data:
                    if '"hdclearart"' in data:
                        extra = hdtvclear + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                    else:
                        extra = thumbnail + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                         server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                         show=show, category=category, folder=True))

    if not "series" in item.url:
        thumbnail = posterdb
        title_info = "[COLOR khaki]Info[/COLOR]"
    if "series" in item.url:
        title_info = "[COLOR skyblue]Info[/COLOR]"
        if '"tvposter"' in data:
            thumbnail = scrapertools.get_match(data, '"tvposter":.*?"url": "([^"]+)"')
        else:
            thumbnail = posterdb

        if "tvbanner" in data:
            category = tvbanner
        else:
            category = show
        if '"tvthumb"' in data:
            plot = item.plot + "|" + tvthumb
        else:
            plot = item.plot + "|" + item.thumbnail
        if '"tvbanner"' in data:
            plot = plot + "|" + tvbanner
        elif '"tvthumb"' in data:
            plot = plot + "|" + tvthumb
        else:
            plot = plot + "|" + item.thumbnail
    else:
        if '"moviethumb"' in data:
            plot = item.plot + "|" + thumb
        else:
            plot = item.plot + "|" + posterdb

        if '"moviebanner"' in data:
            plot = plot + "|" + banner
        else:
            if '"hdmovieclearart"' in data:
                plot = plot + "|" + clear

            else:
                plot = plot + "|" + posterdb

    id = id_scraper

    extra = extra + "|" + id + "|" + title.encode('utf8')

    itemlist.append(
        Item(channel=item.channel, action="info", title=title_info, plot=plot, url=item.url, thumbnail=thumbnail,
             fanart=fanart_info, extra=extra, category=category, show=show, viewmode="movie_with_plot", folder=False))

    return itemlist


def ver_capitulo(item):
    logger.info()
    itemlist = []
    data = get_page(item.url)
    data = re.sub(r"&#.*?;", "x", data)
    patronbloque_enlaces = '<tr class="lol">(.*?)ha sido descargada'
    matchesenlaces = re.compile(patronbloque_enlaces, re.DOTALL).findall(data)
    for enlaces in matchesenlaces:
        enlaces = re.sub(r"alt=.*?<a href=.*?rar.*?>Click", "", enlaces)
        enlaces = re.sub(r"\(Contrase.*?\).*?", "NO REPRODUCIBLE-RAR", enlaces)
        if "Serie Completa" in item.extra.split("|")[2] or "pelicula" in item.extra.split("|")[2]:
            patron = 'alt="[^<]+".*?".*?Click'

            matches = re.compile(patron, re.DOTALL).findall(enlaces)

            scrapertools.printMatches(matches)
            if krypton:
                catchurl = re.compile('<a href="([^"]+)"', re.DOTALL).findall(str(matches))
            else:
                catchurl = re.compile('<a href="/myaddrproxy.php/http/([^"]+)"', re.DOTALL).findall(str(matches))

            for datos in matches:

                if "x Temporada" in item.extra.split("|")[2]:

                    for (a, b) in enumerate(matches):

                        calidad = re.compile('alt="[^<]+" title=.*?;">(.*?)</span>', re.DOTALL).findall(b)
                        idioma = re.compile('alt="[^<]+" title=.*?;">[^<]+</span>.*?;">(.*?)</span>',
                                            re.DOTALL).findall(b)

                        for (c, d) in enumerate(calidad):
                            xbmc.log("calidaddd")
                            xbmc.log(str(c))
                            xbmc.log(str(d))

                        for (f, g) in enumerate(idioma):
                            xbmc.log("idiomaaaa")
                            xbmc.log(str(f))

                            xbmc.log("topotamadre")
                            xbmc.log(str(g))
                            matches[a] = b.replace(b, "[COLOR orange][B]" + d + "[/B][/COLOR]") + "--" + b.replace(b,
                                                                                                                   "[COLOR palegreen][B]" + g + "[/B][/COLOR]")
                else:
                    for (a, b) in enumerate(matches):

                        calidad = re.compile('alt=.*?<td>(.*?)<', re.DOTALL).findall(b)
                        idioma = re.compile('alt=.*?<td>.*?<.*?<td>(.*?)<\/td>', re.DOTALL).findall(b)

                        for (c, d) in enumerate(calidad):
                            xbmc.log("calidaddd")
                            xbmc.log(str(c))
                            xbmc.log(str(d))

                        for (f, g) in enumerate(idioma):
                            xbmc.log("idiomaaaa")
                            xbmc.log(str(f))

                            xbmc.log("topotamadre")
                            xbmc.log(str(g))
                            matches[a] = b.replace(b, "[COLOR orange][B]" + g + "[/B][/COLOR]") + "--" + b.replace(b,
                                                                                                                   "[COLOR palegreen][B]" + d + "[/B][/COLOR]")
        else:
            if item.extra.split("|")[1] != "Especial":
                check = item.extra.split("|")[0] + "x" + item.extra.split("|")[1]
            else:
                check = item.extra.split("|")[1]

            patron = 'icono_espaniol\.png" title="[^<]+" alt="[^<]+"><\/td>\\n<td>' + check + '.*?<\/td>\\n<td>[^<]+<\/td>.*?Click'  # 'icono_.*?png" alt="([^<]+)" .*?;">([^<]+)</span>.*?;">(.*?)</span>.*?<a href="/myaddrproxy.php/http/([^"]+)"'
            matches = re.compile(patron, re.DOTALL).findall(enlaces)
            '''patron ='alt="[^<]+" title="[^<]+"/></td><td style="text-align:center"><span style="font-family: \'Open Sans\';">[^<]+</span></td><td style="text-align:center"><span style="font-family: \'Open Sans\';">'+check+'.*?Click' #'icono_.*?png" alt="([^<]+)" .*?;">([^<]+)</span>.*?;">(.*?)</span>.*? <a href="/myaddrproxy.php/http/([^"]+)"'
          matches = re.compile(patron,re.DOTALL).findall(enlaces)'''

            scrapertools.printMatches(matches)
            if krypton:
                catchurl = re.compile('<a href="([^"]+)"', re.DOTALL).findall(str(matches))
            else:
                catchurl = re.compile('<a href="/myaddrproxy.php/http/([^"]+)"', re.DOTALL).findall(str(matches))

            for datos in matches:

                for (a, b) in enumerate(matches):

                    calidad = scrapertools.find_multiple_matches(b, 'alt=".*?<td>.*?<td>(.*?)<')
                    idioma = re.compile('alt="([^<]+)">', re.DOTALL).findall(b)
                    peso = re.compile('alt="[^<]+"><\/td>\\n<td>(.*?)<\/td>\\n<td>.*?<\/td>', re.DOTALL).findall(b)

                    for (c, d) in enumerate(calidad):
                        xbmc.log("calidaddd")
                        xbmc.log(str(c))
                        xbmc.log(str(d))

                    for (f, g) in enumerate(idioma):
                        xbmc.log("idiomaaaa")
                        xbmc.log(str(f))

                        xbmc.log("topotamadre")
                        xbmc.log(str(g))

                    for (h, i) in enumerate(peso):
                        if "RAR" in i:
                            i = "  (No reproducible--RAR)"
                        else:
                            i = ""
                        if not "x" in g:
                            xbmc.log("digiiiit")
                            g = check
                        matches[a] = "[COLOR crimson][B]Capitulo[/B][/COLOR]" + "--" + b.replace(b,
                                                                                                 "[COLOR orange][B]" + g + "[/B][/COLOR]") + "--" + b.replace(
                            b, "[COLOR palegreen][B]" + d + i + "[/B][/COLOR]")

    get_url = [(z, x) for z, x in enumerate(catchurl)]
    get_url = repr(get_url)

    index = xbmcgui.Dialog().select("[COLOR orange][B]Seleciona calidad...[/B][/COLOR]", matches)

    if index != -1:
        index = str(index)
        url = scrapertools.get_match(get_url, '\(' + index + ', \'(.*?)\'')
        if krypton:
            item.url = url
        else:
            item.url = "http://" + url
        item.server = "torrent"
        platformtools.play_video(item)
        xbmc.executebuiltin('Action(Back)')
        xbmc.sleep(100)
    else:
        xbmc.executebuiltin('Action(Back)')
        xbmc.sleep(100)

    return itemlist


def findvideos(item):
    logger.info()
    check_iepi2 = " "
    itemlist = []
    data = get_page(item.url)
    check_calidad = ""
    check_epi = ""
    check_especial = ""
    if not "series" in item.url:
        thumbnail = item.category
    if "series" in item.url:
        try:
            if krypton:
                url = scrapertools.get_match(data, '<a style="float:left;" href="([^"]+)">Temporada Anterior')
            else:
                url = scrapertools.get_match(data,
                                             '<a style="float:left;" href="/myaddrproxy.php/https/([^"]+)">Temporada Anterior')
                url_a = "http://" + url
            temp_a = scrapertools.get_match(url, 'temporada-(\d+)')
            year = item.extra.split("|")[1]

            title_info = item.show.split("|")[3].replace(' ', '%20')

            try:
                backdrop = scrapertools.get_match(data2, 'page":1.*?,"id".*?"backdrop_path":"\\\(.*?)"')
                fanart = "https://image.tmdb.org/t/p/original" + backdrop

            except:
                fanart = item.show.split("|")[0]
            url_temp = "http://api.themoviedb.org/3/tv/" + item.show.split("|")[
                5] + "/season/" + temp_a + "/images?api_key=" + api_key + ""
            data2 = scrapertools.cachePage(url_temp)
            data2 = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data2)
            patron = '{"id".*?"file_path":"(.*?)","height"'
            matches = re.compile(patron, re.DOTALL).findall(data2)
            if len(matches) == 0:
                thumbnail = item.thumbnail
            for thumtemp in matches:
                thumbnail = "https://image.tmdb.org/t/p/original" + thumtemp
                if "Temporada" in item.title:
                    new_temp = "Temporada " + temp_a
                    title = re.sub(r"Temporada.*?(\d+)", new_temp, item.title)
                    title = re.sub(r"skyblue", "tomato", title)
                else:
                    title = "[COLOR darkturquoise][B]TEMPORADA ANTERIOR[/B][/COLOR]"

                itemlist.append(
                    Item(channel=item.channel, title=title, url=url_a, action="findvideos", thumbnail=thumbnail,
                         extra=item.extra, show=item.show, fanart=fanart, folder=True))

        except:
            pass
    patronbloque_enlaces = '<tr class="lol">(.*?)ha sido descargada'
    matchesenlaces = re.compile(patronbloque_enlaces, re.DOTALL).findall(data)

    for enlaces in matchesenlaces:
        if "serie" in item.url:
            try:
                temp_check = scrapertools.find_single_match(enlaces,
                                                            'icono_.*?png".*?alt=".*?".*?<td>(\d+&#\d+;\d+)<\/td>.*?<td>.*?<\/td>')
                if temp_check == "":
                    temp_check = scrapertools.find_single_match(enlaces,
                                                                'icono_.*?png".*?alt=".*?".*?<td>(\d+&#\d+;\d+-\d+)<\/td>.*?<td>.*?<\/td>')
                    if temp_check == "":
                        check = ""
                    else:
                        check = "yes"
                else:
                    check = "yes"
            except:
                check = ""

        else:
            check = "pelicula"

        if "Completa" in item.title and check == "" or not "Completa" in item.title and check == "":
            if krypton:
                patron = 'icono_.*?png" title="(.*?)".*?<td>.*?<.*?<td>(.*?)<.*?<a href="([^"]+)"'
            else:
                patron = 'icono_.*?png" title="(.*?)".*?<td>.*?<.*?<td>(.*?)<.*?<a href="/myaddrproxy.php/http/([^"]+)"'
            matches = re.compile(patron, re.DOTALL).findall(enlaces)
            scrapertools.printMatches(matches)

            for calidad, idioma, url in matches:

                year = item.extra.split("|")[1]
                try:
                    temp = scrapertools.get_match(item.url, 'temporada-(\d+)')
                except:
                    temp = "0"
                url_tmdb2 = "http://api.themoviedb.org/3/tv/" + item.show.split("|")[
                    5] + "/season/" + temp + "/images?api_key=" + api_key + ""
                data = httptools.downloadpage(url_tmdb2).data
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                patron = '{"id".*?"file_path":"(.*?)","height"'
                matches = re.compile(patron, re.DOTALL).findall(data)
                if len(matches) == 0:
                    if "TEMPORADA ANTERIOR" in item.title:
                        fanart = item.fanart
                    thumbnail = item.thumbnail
                    title = "[COLOR steelblue][B]" + idioma + "[/B][/COLOR]" + "-" + "[COLOR lightskyblue][B]" + calidad + "[/B][/COLOR]"
                    title = re.sub(r"tomato", "skyblue", title)
                    itemlist.append(
                        Item(channel=item.channel, title=title, action="play", url="http://" + url, server="torrent",
                             thumbnail=thumbnail, extra=item.extra, show=item.show, fanart=item.show.split("|")[0],
                             folder=False))
                for thumtemp in matches:
                    thumbnail = "https://image.tmdb.org/t/p/original" + thumtemp
                    if "TEMPORADA ANTERIOR" in item.title:
                        fanart = item.fanart

                    title = "[COLOR steelblue][B]" + idioma + "[/B][/COLOR]" + "-" + "[COLOR lightskyblue][B]" + calidad + "[/B][/COLOR]"
                    title = re.sub(r"tomato", "skyblue", title)
                    if not "http://" in url:
                        url = "http://" + url
                    itemlist.append(Item(channel=item.channel, title=title, action="play", url=url, server="torrent",
                                         thumbnail=thumbnail, extra=item.extra, show=item.show,
                                         fanart=item.show.split("|")[0], folder=False))
        else:
            if krypton:
                patron = 'icono_.*?png".*?alt="(.*?)".*?<td>(.*?)<\/td>.*?<td>(.*?)<\/td>.*?href="([^"]+)"'
            else:
                patron = 'icono_.*?png".*?alt="(.*?)".*?<td>(.*?)<\/td>.*?<td>(.*?)<\/td>.*?href="\/myaddrproxy.php\/http\/([^"]+)"'
            matches = re.compile(patron, re.DOTALL).findall(enlaces)
            scrapertools.printMatches(matches)

            for calidad, idioma, peso, url in matches:
                if not "Especial:" in idioma:
                    check_especial = ""
                if "Temporada" in item.title:
                    try:
                        temp_check = scrapertools.find_single_match(enlaces,
                                                                    'icono_.*?png".*?alt=".*?".*?<td>(\d+&#\d+;\d+)<\/td>.*?<td>.*?<\/td>')
                        if temp_check == "":
                            check = ""
                        else:
                            check = "yes"
                    except:
                        check = ""

                idioma = re.sub(r'\(Contra.*?\)', '', idioma)
                if "Completa" in peso and check == "":
                    continue
                if krypton:
                    url = url
                else:
                    url = "http://" + url
                torrents_path = config.get_videolibrary_path() + '/torrents'
                if not os.path.exists(torrents_path):
                    os.mkdir(torrents_path)
                try:
                    urllib.urlretrieve("http://anonymouse.org/cgi-bin/anon-www.cgi/" + url,
                                       torrents_path + "/temp.torrent")
                    pepe = open(torrents_path + "/temp.torrent", "rb").read()
                except:
                    pepe = ""
                torrent = decode(pepe)
                try:
                    name = torrent["info"]["name"]
                    sizet = torrent["info"]['length']
                    sizet = convert_size(sizet)
                except:
                    name = "no disponible"
                try:
                    check_video = scrapertools.find_multiple_matches(str(torrent["info"]["files"]), "'length': (\d+)}")
                    size = max([int(i) for i in check_video])
                    for file in torrent["info"]["files"]:
                        manolo = "%r - %d bytes" % ("/".join(file["path"]), file["length"])
                        if str(size) in manolo:
                            video = manolo
                    size = convert_size(size)
                    ext_v = re.sub(r"-.*? bytes|.*?\[.*?\].|'|.*?COM.|.*?\[.*?\]|\(.*?\)|.*?\.", "", video)
                    try:
                        os.remove(torrents_path + "/temp.torrent")
                    except:
                        pass
                except:
                    try:
                        size = sizet
                        ext_v = re.sub(r"-.*? bytes|.*?\[.*?\].|'|.*?COM.|.*?\.es.|.*?\[.*?\]|.*?\(.*?\)\.|.*?\.", "",
                                       name)
                    except:
                        size = "NO REPRODUCIBLE"
                        ext_v = ""
                    try:
                        os.remove(torrents_path + "/temp.torrent")
                    except:
                        pass
                if "rar" in ext_v:
                    ext_v = ext_v + " -- No reproducible"
                    size = ""

                title = "[COLOR gold][B]" + idioma + "[/B][/COLOR]" + "-" + "[COLOR lemonchiffon][B]" + calidad + "[/B][/COLOR]" + "-" + "[COLOR khaki] ( Video" + "[/COLOR]" + " " + "[COLOR khaki]" + ext_v + "[/COLOR]" + " " + "[COLOR khaki]" + size + " )" + "[/COLOR]"

                if "series" in item.url and not "Completa" in item.title or check != "" and check != "pelicula":
                    year = item.extra.split("|")[1]
                    # idioma= re.sub(r"-.*","",idioma)
                    check = calidad + "|" + peso + "|" + idioma
                    temp_epi = re.compile('(\d)&#.*?;(\d+)', re.DOTALL).findall(check)

                    for temp, epi in temp_epi:
                        url_tmdb2 = "http://api.themoviedb.org/3/tv/" + item.show.split("|")[
                            5] + "/season/" + temp + "/images?api_key=" + api_key + ""
                        data = httptools.downloadpage(url_tmdb2).data
                        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                        patron = '{"id".*?"file_path":"(.*?)","height"'
                        matches = re.compile(patron, re.DOTALL).findall(data)
                        if len(matches) == 0:
                            thumbnail = item.thumbnail
                        for thumtemp in matches:
                            thumbnail = "https://image.tmdb.org/t/p/original" + thumtemp

                    if check_epi == epi and check_calidad != peso and not "Especial:" in idioma or "Especial:" in idioma and check_especial == "yes":
                        check_info = "no"
                        title = "          [COLOR mediumslateblue][B]Versión[/B][/COLOR]" + "  " + "[COLOR royalblue][B]" + peso + "[/B][/COLOR]" + "[COLOR turquoise] ( Video" + "[/COLOR]" + " " + "[COLOR turquoise]" + ext_v + "[/COLOR]" + " " + "[COLOR turquoise]" + size + " )" + "[/COLOR]"
                    else:
                        check_info = "yes"
                        if "Especial:" in idioma:
                            check_especial = "yes"
                        title = "[COLOR steelblue][B]" + idioma + "[/B][/COLOR]" + "-" + "[COLOR lightskyblue][B]" + calidad + "[/B][/COLOR]" + "-" + "[COLOR royalblue][B]" + peso + "[/B][/COLOR]" + "[COLOR turquoise] ( Video" + "[/COLOR]" + " " + "[COLOR turquoise]" + ext_v + "[/COLOR]" + " " + "[COLOR turquoise]" + size + " )" + "[/COLOR]"

                    check_epi = epi
                    check_calidad = peso

                itemlist.append(Item(channel=item.channel, title=title, action="play", url=url, server="torrent",
                                     thumbnail=thumbnail, extra=item.extra, show=item.show,
                                     fanart=item.show.split("|")[0], folder=False))

                if "series" in item.url:
                    if check_info == "yes":
                        extra = item.extra + "|" + temp + "|" + epi
                        if "-" in idioma:
                            temp_epi2 = re.compile('\d&#.*?;\d+-(\d+)', re.DOTALL).findall(check)
                            for epi2 in temp_epi2:
                                len_epis = int(epi2) - int(epi)
                                if len_epis == 1:
                                    check_iepi2 = "ok"
                                    title_info = "    Info Cap." + epi
                                    title_info = "[COLOR skyblue]" + title_info + "[/COLOR]"
                                    itemlist.append(
                                        Item(channel=item.channel, action="info_capitulos", title=title_info,
                                             url=item.url, thumbnail=thumbnail, fanart=item.show.split("|")[0],
                                             extra=extra, show=item.show, category=item.category, folder=False))
                                else:
                                    epis_len = range(int(epi), int(epi2) + 1)
                                    extra = item.extra + "|" + temp + "|" + str(epis_len)
                                    title_info = "    Info Capítulos"
                                    title_info = "[COLOR skyblue]" + title_info + "[/COLOR]"
                                    itemlist.append(
                                        Item(channel=item.channel, action="capitulos", title=title_info, url=item.url,
                                             thumbnail=thumbnail, fanart=item.show.split("|")[0], extra=extra,
                                             show=item.show, category=item.category, folder=True))
                                    check_iepi2 = ""
                        else:
                            title_info = "    Info"
                            title_info = "[COLOR skyblue]" + title_info + "[/COLOR]"
                            itemlist.append(
                                Item(channel=item.channel, action="info_capitulos", title=title_info, url=item.url,
                                     thumbnail=thumbnail, fanart=item.show.split("|")[0], extra=extra, show=item.show,
                                     category=item.category, folder=False))

                        if check_iepi2 == "ok":
                            extra = item.extra + "|" + temp + "|" + epi2
                            title_info = "    Info Cap." + epi2
                            title_info = "[COLOR skyblue]" + title_info + "[/COLOR]"
                            itemlist.append(
                                Item(channel=item.channel, action="info_capitulos", title=title_info, url=item.url,
                                     thumbnail=thumbnail, fanart=item.show.split("|")[0], extra=extra, show=item.show,
                                     category=item.category, folder=False))

    return itemlist


def capitulos(item):
    logger.info()
    itemlist = []
    url = item.url
    capis = item.extra.split("|")[3]
    capis = re.sub(r'\[|\]', '', capis)
    capis = [int(k) for k in capis.split(',')]
    for i in capis:
        extra = item.extra.split("|")[0] + "|" + item.extra.split("|")[1] + "|" + item.extra.split("|")[2] + "|" + str(
            i)
        itemlist.append(
            Item(channel=item.channel, action="info_capitulos", title="[COLOR skyblue]Info Cap." + str(i) + "[/COLOR]",
                 url=item.url, thumbnail=item.thumbnail, fanart=item.show.split("|")[0], extra=extra, show=item.show,
                 category=item.category, folder=False))
    return itemlist


def info(item):
    logger.info()
    itemlist = []
    url = item.url
    id = item.extra

    if "serie" in item.url:
        try:
            rating_tmdba_tvdb = item.extra.split("|")[6]
            if item.extra.split("|")[6] == "":
                rating_tmdba_tvdb = "Sin puntuación"
        except:
            rating_tmdba_tvdb = "Sin puntuación"
    else:
        rating_tmdba_tvdb = item.extra.split("|")[3]
    rating_filma = item.extra.split("|")[4]
    print "eztoquee"
    print rating_filma
    print rating_tmdba_tvdb

    filma = "http://s6.postimg.org/6yhe5fgy9/filma.png"

    try:
        if "serie" in item.url:
            title = item.extra.split("|")[8]

        else:
            title = item.extra.split("|")[6]
        title = title.replace("%20", " ")
        title = "[COLOR yellow][B]" + title + "[/B][/COLOR]"
    except:
        title = item.title

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

    try:
        if not "serie" in item.url:
            url_plot = "http://api.themoviedb.org/3/movie/" + item.extra.split("|")[
                1] + "?api_key=" + api_key + "&append_to_response=credits&language=es"
            data_plot = scrapertools.cache_page(url_plot)
            plot, tagline = scrapertools.find_single_match(data_plot, '"overview":"(.*?)",.*?"tagline":(".*?")')
            if plot == "":
                plot = item.show.split("|")[2]

            plot = "[COLOR moccasin][B]" + plot + "[/B][/COLOR]"
            plot = re.sub(r"\\", "", plot)

        else:
            plot = item.show.split("|")[2]
            plot = "[COLOR moccasin][B]" + plot + "[/B][/COLOR]"
            plot = re.sub(r"\\", "", plot)

            if item.extra.split("|")[7] != "":
                tagline = item.extra.split("|")[7]
                # tagline= re.sub(r',','.',tagline)
            else:
                tagline = ""
    except:
        title = "[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
        plot = "Esta pelicula no tiene informacion..."
        plot = plot.replace(plot, "[COLOR yellow][B]" + plot + "[/B][/COLOR]")
        photo = "http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        foto = "http://s6.postimg.org/ub7pb76c1/noinfo.png"
        info = ""

    if "serie" in item.url:
        check2 = "serie"
        thumb_busqueda = "http://imgur.com/84pleyQ.png"
        icon = "http://s6.postimg.org/hzcjag975/tvdb.png"
        foto = item.show.split("|")[1]
        if item.extra.split("|")[5] != "":
            critica = item.extra.split("|")[5]
        else:
            critica = "Esta serie no tiene críticas..."

        photo = item.extra.split("|")[0].replace(" ", "%20")
        try:
            tagline = "[COLOR aquamarine][B]" + tagline + "[/B][/COLOR]"
        except:
            tagline = ""

    else:
        thumb_busqueda = "http://imgur.com/Slbtn28.png"
        critica = item.extra.split("|")[5]
        if "%20" in critica:
            critica = "No hay críticas"
        icon = "http://imgur.com/SenkyxF.png"

        photo = item.extra.split("|")[0].replace(" ", "%20")
        foto = item.show.split("|")[1]
        if foto == item.thumbnail:
            foto = "http://imgur.com/5jEL62c.jpg"

        try:
            if tagline == "\"\"":
                tagline = " "
        except:
            tagline = " "
        tagline = "[COLOR aquamarine][B]" + tagline + "[/B][/COLOR]"
        check2 = "pelicula"
    # Tambien te puede interesar
    peliculas = []
    if "serie" in item.url:

        url_tpi = "http://api.themoviedb.org/3/tv/" + item.show.split("|")[
            5] + "/recommendations?api_key=" + api_key + "&language=es"
        data_tpi = scrapertools.cachePage(url_tpi)
        tpi = scrapertools.find_multiple_matches(data_tpi,
                                                 'id":(.*?),.*?"original_name":"(.*?)",.*?"poster_path":(.*?),')

    else:
        url_tpi = "http://api.themoviedb.org/3/movie/" + item.extra.split("|")[
            1] + "/recommendations?api_key=" + api_key + "&language=es"
        data_tpi = scrapertools.cachePage(url_tpi)
        tpi = scrapertools.find_multiple_matches(data_tpi,
                                                 'id":(.*?),.*?"original_title":"(.*?)",.*?"poster_path":(.*?),')

    for idp, peli, thumb in tpi:

        thumb = re.sub(r'"|}', '', thumb)
        if "null" in thumb:
            thumb = "http://s6.postimg.org/tw1vhymj5/noposter.png"
        else:
            thumb = "https://image.tmdb.org/t/p/original" + thumb
        peliculas.append([idp, peli, thumb])

    check2 = check2.replace("pelicula", "movie").replace("serie", "tvshow")
    infoLabels = {'title': title, 'plot': plot, 'thumbnail': photo, 'fanart': foto, 'tagline': tagline,
                  'rating': rating}
    item_info = item.clone(info=infoLabels, icon=icon, extra=id, rating=rating, rating_filma=rating_filma,
                           critica=critica, contentType=check2, thumb_busqueda=thumb_busqueda)
    from channels import infoplus
    infoplus.start(item_info, peliculas)


def info_capitulos(item):
    logger.info()
    url = "https://api.themoviedb.org/3/tv/" + item.show.split("|")[5] + "/season/" + item.extra.split("|")[
        2] + "/episode/" + item.extra.split("|")[3] + "?api_key=" + api_key + "&language=es"

    if "/0" in url:
        url = url.replace("/0", "/")

    data = httptools.downloadpage(url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '],"name":"(.*?)","overview":"(.*?)".*?"still_path":(.*?),"vote_average":(\d+\.\d).*?,"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) == 0:

        url = "http://thetvdb.com/api/1D62F2F90030C444/series/" + item.category + "/default/" + item.extra.split("|")[
            2] + "/" + item.extra.split("|")[3] + "/es.xml"
        if "/0" in url:
            url = url.replace("/0", "/")
        data = httptools.downloadpage(url).data
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

        patron = '<Data>.*?<EpisodeName>([^<]+)</EpisodeName>.*?<Overview>(.*?)</Overview>.*?<Rating>(.*?)</Rating>'

        matches = re.compile(patron, re.DOTALL).findall(data)

        if len(matches) == 0:

            title = "[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
            plot = "Este capitulo no tiene informacion..."
            plot = "[COLOR yellow][B]" + plot + "[/B][/COLOR]"
            image = "http://s6.postimg.org/ub7pb76c1/noinfo.png"
            foto = "http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
            rating = ""


        else:

            for name_epi, info, rating in matches:
                if "<filename>episodes" in data:
                    foto = scrapertools.get_match(data, '<Data>.*?<filename>(.*?)</filename>')
                    fanart = "http://thetvdb.com/banners/" + foto
                else:
                    fanart = "http://imgur.com/ZiEAVOD.png"
                plot = info
                plot = "[COLOR peachpuff][B]" + plot + "[/B][/COLOR]"
                title = name_epi.upper()
                title = "[COLOR bisque][B]" + title + "[/B][/COLOR]"
                image = fanart
                foto = item.extra.split("|")[0]
                if not ".png" in foto:
                    if "serie" in item.url:
                        foto = "http://imgur.com/6uXGkrz.png"
                    else:
                        foto = "http://i.imgur.com/5jEL62c.png"
                foto = re.sub(r'\(.*?\)|" "|" "', '', foto)
                foto = re.sub(r' ', '', foto)
                try:

                    check_rating = scrapertools.get_match(rating, '(\d+).')

                    if int(check_rating) >= 5 and int(check_rating) < 8:
                        rating = "Puntuación " + "[COLOR springgreen][B]" + rating + "[/B][/COLOR]"
                    elif int(check_rating) >= 8 and int(check_rating) < 10:
                        rating = "Puntuación " + "[COLOR yellow][B]" + rating + "[/B][/COLOR]"
                    elif int(check_rating) == 10:
                        rating = "Puntuación " + "[COLOR orangered][B]" + rating + "[/B][/COLOR]"
                    else:
                        rating = "Puntuación " + "[COLOR crimson][B]" + rating + "[/B][/COLOR]"

                except:
                    rating = "Puntuación " + "[COLOR crimson][B]" + rating + "[/B][/COLOR]"
                if "10." in rating:
                    rating = re.sub(r'10\.\d+', '10', rating)
    else:
        for name_epi, info, fanart, rating in matches:
            if info == "" or info == "\\":
                info = "Sin informacion del capítulo aún..."
            plot = info
            plot = re.sub(r'/n', '', plot)
            plot = "[COLOR peachpuff][B]" + plot + "[/B][/COLOR]"
            title = name_epi.upper()
            title = "[COLOR bisque][B]" + title + "[/B][/COLOR]"
            image = fanart
            image = re.sub(r'"|}', '', image)
            if "null" in image:
                image = "http://imgur.com/ZiEAVOD.png"
            else:
                image = "https://image.tmdb.org/t/p/original" + image
            foto = item.extra.split("|")[0]
            if not ".png" in foto:
                if "serie" in item.url:
                    foto = "http://imgur.com/6uXGkrz.png"
                else:
                    foto = "http://i.imgur.com/5jEL62c.png"
            foto = re.sub(r'\(.*?\)|" "|" "', '', foto)
            foto = re.sub(r' ', '', foto)
            try:

                check_rating = scrapertools.get_match(rating, '(\d+).')

                if int(check_rating) >= 5 and int(check_rating) < 8:
                    rating = "Puntuación " + "[COLOR springgreen][B]" + rating + "[/B][/COLOR]"
                elif int(check_rating) >= 8 and int(check_rating) < 10:
                    rating = "Puntuación " + "[COLOR yellow][B]" + rating + "[/B][/COLOR]"
                elif int(check_rating) == 10:
                    rating = "Puntuación " + "[COLOR orangered][B]" + rating + "[/B][/COLOR]"
                else:
                    rating = "Puntuación " + "[COLOR crimson][B]" + rating + "[/B][/COLOR]"

            except:
                rating = "Puntuación " + "[COLOR crimson][B]" + rating + "[/B][/COLOR]"
            if "10." in rating:
                rating = re.sub(r'10\.\d+', '10', rating)
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

        self.background = xbmcgui.ControlImage(70, 20, 1150, 630, 'http://imgur.com/gh1GShA.jpg')
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


def translate(to_translate, to_langage="auto", langage="auto"):
    '''Return the translation using google translate
        you must shortcut the langage you define (French = fr, English = en, Spanish = es, etc...)
        if you don't define anything it will detect it or use english by default
        Example:
        print(translate("salut tu vas bien?", "en"))
        hello you alright?'''
    agents = {
        'User-Agent': "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
    before_trans = 'class="t0">'
    link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_langage, langage, to_translate.replace(" ", "+"))
    request = urllib2.Request(link, headers=agents)
    page = urllib2.urlopen(request).read()
    result = page[page.find(before_trans) + len(before_trans):]
    result = result.split("<")[0]
    return result


if __name__ == '__main__':
    to_translate = 'Hola como estas?'
    print("%s >> %s" % (to_translate, translate(to_translate)))
    print("%s >> %s" % (to_translate, translate(to_translate, 'fr')))


# should print Hola como estas >> Hello how are you
# and Hola como estas? >> Bonjour comment allez-vous?



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
            data = data
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


def busqueda(item):
    logger.info()
    cat = [item.extra.split("|")[0].replace("tv", "serie"), 'torrent']
    new_item = Item()
    new_item.extra = item.extra.split("|")[1].replace("+", " ")
    new_item.category = item.extra.split("|")[0]

    from channels import search
    return search.do_search(new_item, cat)
