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

    itemlist.append(Item(channel=item.channel, title="[COLOR yellow][B]Películas[/B][/COLOR]", action="peliculas",
                         url="http://www.miltorrents.com", thumbnail="http://imgur.com/46ZzwrZ.png",
                         fanart="http://imgur.com/y4nJyZh.jpg"))
    title = "[COLOR firebrick][B]Buscar[/B][/COLOR]" + "  " + "[COLOR yellow][B]Peliculas[/B][/COLOR]"
    itemlist.append(Item(channel=item.channel, title="         " + title, action="search", url="",
                         thumbnail="http://imgur.com/JdSnBeH.png", fanart="http://imgur.com/gwjawWV.jpg",
                         extra="peliculas" + "|" + check_bg))

    itemlist.append(Item(channel=item.channel, title="[COLOR slategray][B]Series[/B][/COLOR]", action="peliculas",
                         url="http://www.miltorrents.com/series", thumbnail="http://imgur.com/sYpu1KF.png",
                         fanart="http://imgur.com/LwS32zX.jpg"))

    title = "[COLOR firebrick][B]Buscar[/B][/COLOR]" + "  " + "[COLOR slategray][B]Series[/B][/COLOR]"
    itemlist.append(Item(channel=item.channel, title="         " + title, action="search", url="",
                         thumbnail="http://imgur.com/brMIPlT.png", fanart="http://imgur.com/ecPmzDj.jpg",
                         extra="series" + "|" + check_bg))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    if item.extra:
        if item.extra.split("|")[0] == "series":
            item.url = "http://www.miltorrents.com/series/?pTit=%s&pOrd=FE" % (texto)
        else:
            item.url = "http://www.miltorrents.com/?pTit=%s&pOrd=FE" % (texto)

        item.extra = "search" + "|" + item.extra.split("|")[1] + "|" + texto

        try:
            return peliculas(item)
        # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
        except:
            import sys
            for line in sys.exc_info():
                logger.error("%s" % line)
            return []
    else:
        if item.contentType != "movie":
            item.url = "http://www.miltorrents.com/series/?pTit=%s&pOrd=FE" % (texto)
            check_sp = "tvshow"
        else:
            item.url = "http://www.miltorrents.com/?pTit=%s&pOrd=FE" % (texto)
            check_sp = "peliculas"
        item.extra = "search" + "|""bglobal" + "|" + texto + "|" + check_sp
        try:
            return peliculas(item)
        # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
        except:
            import sys
            for line in sys.exc_info():
                logger.error("%s" % line)
                return []


def peliculas(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"Independance", "Independence", data)
    if "serie" in item.url:
        patron = '<div class="corner-episode">(.*?)<\/div>.*?<a href="([^"]+)".*?image:url\(\'([^"]+)\'.*?"tooltipbox">(.*?)<br'

        matches = re.compile(patron, re.DOTALL).findall(data)
        if item.extra.split("|")[0] == "search":
            check_bg = item.action
            if item.extra.split("|")[1] != "bglobal" and check_bg != "info":
                if len(matches) == 0:
                    dialog = xbmcgui.Dialog()
                    if dialog.yesno(
                                            '[COLOR crimson][B]Sin resultados en[/B][/COLOR]' + '[COLOR gold][B] Mil[/B][/COLOR]' + '[COLOR floralwhite][B]torrents[/B][/COLOR]',
                                            '[COLOR cadetblue]¿Quieres hacer una busqueda en Alfa?[/COLOR]',
                                            '', "", '[COLOR crimson][B]No,gracias[/B][/COLOR]',
                                            '[COLOR yellow][B]Si[/B][/COLOR]'):
                        item.extra = "serie" + "|" + item.extra.split("|")[2]
                        return busqueda(item)
                    else:

                        xbmc.executebuiltin('Action(Back)')
                        xbmc.sleep(500)

        for episodio, url, thumbnail, title in matches:
            title = title.decode('latin1').encode('utf8')
            title_fan = title.strip()
            trailer = title_fan + " " + "series" + "trailer"
            title = "[COLOR slategray][B]" + title.strip() + "[/B][/COLOR]" + "  " + "[COLOR floralwhite][B]" + episodio + "[/B][/COLOR]"
            trailer = urllib.quote(trailer)
            extra = trailer + "|" + title_fan + "|" + " " + "|" + "pelicula"
            itemlist.append(Item(channel=item.channel, title=title, url=url, action="fanart", thumbnail=thumbnail,
                                 fanart="http://imgur.com/NrZNOTN.jpg", extra=extra, folder=True))
    else:
        patron = '<div class="moviesbox">(.*?)<a href="([^"]+)".*?image:url\(\'([^"]+)\'.*?<span class="tooltipbox">([^<]+)<i>\((\d\d\d\d)\)'

        matches = re.compile(patron, re.DOTALL).findall(data)

        if item.extra.split("|")[0] == "search":
            check_bg = item.action
            if item.extra.split("|")[1] != "bglobal" and check_bg != "info":

                if len(matches) == 0:
                    dialog = xbmcgui.Dialog()
                    if dialog.yesno(
                                            '[COLOR crimson][B]Sin resultados en[/B][/COLOR]' + '[COLOR gold][B] Mil[/B][/COLOR]' + '[COLOR floralwhite][B]torrents[/B][/COLOR]',
                                            '[COLOR cadetblue]¿Quieres hacer una busqueda en Alfa?[/COLOR]',
                                            '', "", '[COLOR crimson][B]No,gracias[/B][/COLOR]',
                                            '[COLOR yellow][B]Si[/B][/COLOR]'):
                        item.extra = "movie" + "|" + item.extra.split("|")[2]

                        return busqueda(item)


                    else:

                        xbmc.executebuiltin('Action(Back)')
                        xbmc.sleep(500)

        for p_rating, url, thumbnail, title, year in matches:

            try:
                rating = scrapertools.get_match(p_rating, '<div class="moviesbox_rating">(.*?)<img')
            except:
                rating = "(Sin puntuacion)"
            title = title.decode('latin1').encode('utf8')
            title_fan = re.sub(r"\[.*?\]|\(.*?\)|\d&#.*?;\d+|-|Temporada.*?Completa| ;|(Sin puntuacion)", "", title)

            try:

                check_rating = scrapertools.get_match(rating, '(\d+).')

                if int(check_rating) >= 5 and int(check_rating) < 8:
                    rating = "[COLOR springgreen][B]" + rating + "[/B][/COLOR]"
                elif int(check_rating) >= 8 and int(check_rating) < 10:
                    rating = "[COLOR yellow][B]" + rating + "[/B][/COLOR]"
                elif int(check_rating) == 10:
                    rating = "[COLOR orangered][B]" + rating + "[/B][/COLOR]"
                else:
                    rating = "[COLOR crimson][B]" + rating + "[/B][/COLOR]"

            except:
                rating = "[COLOR crimson][B]" + rating + "[/B][/COLOR]"
            if "10." in rating:
                rating = re.sub(r'10\.\d+', '10', rating)
            title = "[COLOR gold][B]" + title + "[/B][/COLOR]" + "  " + rating
            trailer = title_fan + " " + "trailer"
            trailer = urllib.quote(trailer)

            extra = trailer + "|" + title_fan + "|" + year + "|" + "pelicula"

            itemlist.append(Item(channel=item.channel, title=title, url=url, action="fanart", thumbnail=thumbnail,
                                 fanart="http://imgur.com/Oi1mlFn.jpg", extra=extra, folder=True))

    ## Paginación
    patronvideos = '<div class="pagination">.*?<a href="#">.*?<\/a><\/span><a href="([^"]+)"'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches) > 0:
        url = matches[0]
        itemlist.append(Item(channel=item.channel, action="peliculas", title="[COLOR khaki]siguiente[/COLOR]", url=url,
                             thumbnail="http://imgur.com/fJzoytz.png", fanart="http://imgur.com/3AqH1Zu.jpg",
                             folder=True))

    return itemlist


def fanart(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    title_fan = item.extra.split("|")[1]
    title = title_fan.replace(' ', '%20')
    title = ''.join((c for c in unicodedata.normalize('NFD', unicode(title.decode('utf-8'))) if
                     unicodedata.category(c) != 'Mn')).encode("ascii", "ignore")

    if not "serie" in item.url:
        item.title = re.sub(r" \[COLOR.*?\]\d+.\d+.*?.*?\[\/COLOR\]|\(Sin puntuacion\)", "", item.title)
    item.plot = item.extra.split("|")[0]
    try:
        sinopsis = scrapertools.get_match(data,
                                          '<b>Sinopsis:<\/b><span class="item" itemprop="description">(.*?)<\/span><\/span>').decode(
            'latin1').encode('utf8')
    except:
        sinopsis = ""

    if not "serie" in item.url:
        id_tmdb = ""
        # filmafinity
        year = item.extra.split("|")[2]

        if year == "0000":
            year = ""

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
                extra = item.thumbnail + "|" + "" + "|" + "" + "|" + "Sin información" + "|" + rating_filma + "|" + critica
                show = item.fanart + "|" + "" + "|" + sinopsis
                posterdb = item.thumbnail
                fanart_info = item.fanart
                fanart_3 = ""
                fanart_2 = item.fanart
                category = item.thumbnail
                id_scraper = ""

                itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                     thumbnail=item.thumbnail, fanart=item.fanart, extra=extra, show=show,
                                     category=category, folder=True))

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
                fanart = item.fanart
            else:
                fanart = "https://image.tmdb.org/t/p/original" + fan
            item.extra = fanart

            url = "http://api.themoviedb.org/3/movie/" + id + "/images?api_key=" + api_key
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
        url_bing = "http://www.bing.com/search?q=%s+Serie+de+tv+site:filmaffinity.com" % (title.replace(' ', '+'))
        data = browser(url_bing)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        try:
            if "myaddrproxy.php" in data:
                subdata_bing = scrapertools.get_match(data,
                                                      'li class="b_algo"><div class="b_title"><h2>(<a href="/myaddrproxy.php/http/www.filmaffinity.com/es/film.*?)"')
                subdata_bing = re.sub(r'\/myaddrproxy.php\/http\/', '', subdata_bing)
            else:
                subdata_bing = scrapertools.get_match(data,
                                                      'li class="b_algo"><h2>(<a href="http://www.filmaffinity.com/es/film.*?)"')
        except:
            pass

        try:
            url_filma = scrapertools.get_match(subdata_bing, '<a href="([^"]+)')
            if not "http" in url_filma:
                data = httptools.downloadpage("http://" + url_filma).data
            else:
                data = httptools.downloadpage(url_filma).data
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            year = scrapertools.get_match(data, '<dt>Año</dt>.*?>(.*?)</dd>')
        except:
            year = ""

        if sinopsis == " ":
            sinopsis = scrapertools.find_single_match(data, '<dd itemprop="description">(.*?)</dd>')
            sinopsis = sinopsis.replace("<br><br />", "\n")
            sinopsis = re.sub(r"\(FILMAFFINITY\)<br />", "", sinopsis)
        try:
            rating_filma = scrapertools.get_match(data, 'itemprop="ratingValue" content="(.*?)">')
        except:
            rating_filma = "Sin puntuacion"
        print "lobeznito"
        print rating_filma

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
        patron = '"page":1.*?,"id":(.*?),.*?"backdrop_path":(.*?),'
        matches = re.compile(patron, re.DOTALL).findall(data_tmdb)

        ###Busqueda en bing el id de imdb de la serie
        if len(matches) == 0:
            url_tmdb = "http://api.themoviedb.org/3/search/tv?api_key=" + api_key + "&query=" + title + "&language=es"
            data_tmdb = scrapertools.cachePage(url_tmdb)
            data_tmdb = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data_tmdb)
            patron = '"page":1.*?,"id":(.*?),.*?"backdrop_path":(.*?),'
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
                    extra = item.thumbnail + "|" + year + "|" + "no data" + "|" + "no data" + "|" + rating_filma + "|" + critica + "|" + "" + "|" + id_tmdb
                    show = item.fanart + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + item.thumbnail + "|" + id_tmdb
                    fanart_info = item.fanart
                    fanart_2 = item.fanart
                    id_scraper = " " + "|" + "serie" + "|" + rating_filma + "|" + critica + "|" + " "
                    category = ""
                    posterdb = item.thumbnail
                    itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                         thumbnail=item.thumbnail, fanart=item.fanart, extra=extra, category=category,
                                         show=show, folder=True))

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
                fanart = item.fanart
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
                fanart_info = "https://image.tmdb.org/t/p/original" + fanart_info
                fanart_3 = "https://image.tmdb.org/t/p/original" + fanart_3
                fanart_2 = "https://image.tmdb.org/t/p/original" + fanart_2
                if fanart == item.fanart:
                    fanart = fanart_info
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
    title_info = u'\u012F\u03B7\u0492\u03BF'
    title_info = title_info.encode('utf-8')
    if not "serie" in item.url:
        thumbnail = posterdb
        title_info = "[COLOR khaki][B]" + title_info + "[/B][/COLOR]"
    if "serie" in item.url:
        title_info = "[COLOR skyblue][B]" + title_info + "[/B][/COLOR]"
        if '"tvposter"' in data:
            thumbnail = scrapertools.get_match(data, '"tvposter":.*?"url": "([^"]+)"')
        else:
            thumbnail = item.thumbnail

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


def capitulos(item):
    logger.info()
    itemlist = []
    data = item.extra
    thumbnail = scrapertools.get_match(data, 'background-image:url\(\'([^"]+)\'')
    thumbnail = re.sub(r"w185", "original", thumbnail)
    patron = '<a href="([^"]+)".*?<br\/><i>(.*?)<\/i>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, capitulo in matches:
        capitulo = re.sub(r"Cap.*?tulo", "", capitulo)
        capitulo = "[COLOR floralwhite][B]" + capitulo + "[/B][/COLOR]"
        if capitulo == item.extra.split("|")[4]:
            continue
        if not ".jpg" in item.extra.split("|")[2]:
            fanart = item.show.split("|")[0]
        else:
            fanart = item.extra.split("|")[2]
        itemlist.append(Item(channel=item.channel, title=capitulo, action="findvideos", url=url, thumbnail=thumbnail,
                             extra="fv2" + "|" + item.extra.split("|")[3], show=item.show, category=item.category,
                             fanart=fanart, folder=True))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if not "serie" in item.url:
        thumbnail = item.category
    else:
        thumbnail = item.show.split("|")[4]
    patronbloque_enlaces = '<div class="detail_content_subtitle">(.*?)<\/div>(.*?)<div class="torrent_sep">'
    matchesenlaces = re.compile(patronbloque_enlaces, re.DOTALL).findall(data)

    if len(matchesenlaces) == 0:
        thumb = ""
        check = ""
        itemlist.append(
            Item(channel=item.channel, title="[COLOR crimson][B]No hay Torrent[/B][/COLOR]", action="mainlist", url="",
                 fanart=item.show.split("|")[0], thumbnail=thumbnail, folder=False))

    for calidad_bloque, bloque_enlaces in matchesenlaces:

        calidad_bloque = dhe(calidad_bloque)
        calidad_bloque = ''.join((c for c in unicodedata.normalize('NFD', unicode(calidad_bloque.decode('utf-8'))) if
                                  unicodedata.category(c) != 'Mn'))
        if "Alta" in calidad_bloque:
            title = u'\u0414\u006C\u03C4\u03B1' + "  " + u'\u0110\u04BC\u0492\u0456\u03B7\u0456\u03C2\u0456\u03BF\u03B7'
            title = title.encode('utf-8')
            title = "                                           [COLOR yellow][B]" + title + "[/B][/COLOR]"
        elif "estandar" in calidad_bloque:
            title = u'\u0110\u04BC\u0492\u0456\u03B7\u0456\u03C2\u0456\u03BF\u03B7' + "  " + u'\u04BC\u0053\u03C4\u03B1\u03B7\u0110\u03B1\u0491'
            title = title.encode('utf-8')
            title = "                                       [COLOR mediumaquamarine][B]" + title + "[/B][/COLOR]"
        else:

            title = u'\u0053\u03C2\u0491\u04BC\u04BC\u03B7\u04BC\u0491'
            title = title.encode('utf-8')
            title = "                                                  [COLOR slategray][B]" + title + "[/B][/COLOR]"
        itemlist.append(
            Item(channel=item.channel, title=title, action="mainlist", url="", fanart=item.show.split("|")[0],
                 thumbnail=thumbnail, folder=False))

        if "serie" in item.url:
            thumb = scrapertools.get_match(data, '<div class="detail_background2".*?url\(([^"]+)\)')
            patron = '<a href=.*?(http.*?)\'\).*?<i>(.*?)<\/i>'
            matches = re.compile(patron, re.DOTALL).findall(bloque_enlaces)
            for url, calidad in matches:

                try:
                    if not url.endswith(".torrent") and not "elitetorrent" in url:
                        if url.endswith("fx"):
                            url = httptools.downloadpage(url, follow_redirects=False)
                            url = url.headers.get("location")

                            if url.endswith(".fx"):
                                url = httptools.downloadpage(url, follow_redirects=False)
                                url = url.headers.get("location")

                            url = " http://estrenosli.org" + url

                        else:
                            if not url.endswith(".mkv"):
                                url = httptools.downloadpage(url, follow_redirects=False)
                                url = url.headers.get("location")

                    torrents_path = config.get_videolibrary_path() + '/torrents'

                    if not os.path.exists(torrents_path):
                        os.mkdir(torrents_path)
                    try:
                        urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'
                        urllib.urlretrieve(url, torrents_path + "/temp.torrent")
                        pepe = open(torrents_path + "/temp.torrent", "rb").read()
                    except:
                        pepe = ""
                    if "used CloudFlare" in pepe:
                        try:
                            urllib.urlretrieve("http://anonymouse.org/cgi-bin/anon-www.cgi/" + url.strip(),
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
                        check_video = scrapertools.find_multiple_matches(str(torrent["info"]["files"]),
                                                                         "'length': (\d+)}")

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
                        size = sizet
                        ext_v = re.sub(r"-.*? bytes|.*?\[.*?\].|'|.*?COM.|.*?\.es.|.*?\[.*?\]|.*?\(.*?\)\.|.*?\.", "",
                                       name)
                        try:
                            os.remove(torrents_path + "/temp.torrent")
                        except:
                            pass
                except:
                    size = "en estos momentos..."
                    ext_v = "no disponible"

                if "Alta" in calidad_bloque:
                    title = "[COLOR navajowhite][B]" + calidad + "[/B][/COLOR]" + " " + "[COLOR peachpuff]( Video [/COLOR]" + "[COLOR peachpuff]" + ext_v + " -- " + size + " )[/COLOR]"
                elif "estandar" in calidad_bloque:
                    title = "[COLOR lavender][B]" + calidad + "[/B][/COLOR]" + " " + "[COLOR azure]( Video [/COLOR]" + "[COLOR azure]" + ext_v + " -- " + size + " )[/COLOR]"
                else:
                    title = "[COLOR gainsboro][B]" + calidad + "[/B][/COLOR]" + " " + "[COLOR silver]( Video [/COLOR]" + "[COLOR silver]" + ext_v + " -- " + size + " )[/COLOR]"
                if "rar" in ext_v:
                    ext_v = ext_v + " -- No reproducible"
                    size = ""

                item.title = re.sub(r"\[.*?\]", "", item.title)
                temp_epi = scrapertools.find_multiple_matches(item.title, '(\d+)x(\d+)')

                for temp, epi in temp_epi:
                    check = temp + "x" + epi
                    if item.extra.split("|")[0] == "fv2":
                        extra = item.extra.split("|")[1] + "|" + " " + "|" + temp + "|" + epi
                    else:
                        extra = item.extra + "|" + temp + "|" + epi

                    itemlist.append(Item(channel=item.channel, title=title, action="play", url=url, server="torrent",
                                         thumbnail=thumbnail, extra=item.extra, show=item.show,
                                         fanart=item.show.split("|")[0], folder=False))
        else:
            patron = '<a href=.*?(http.*?)\'\).*?<i>(.*?)<i>(.*?)<\/i>'
            matches = re.compile(patron, re.DOTALL).findall(bloque_enlaces)
            for url, calidad, peso in matches:

                try:
                    if not url.endswith(".torrent") and not "elitetorrent" in url:
                        if url.endswith("fx"):
                            url = httptools.downloadpage(url, follow_redirects=False)
                            url = url.headers.get("location")

                            if url.endswith(".fx"):
                                url = httptools.downloadpage(url, follow_redirects=False)
                                url = url.headers.get("location")

                            url = " http://estrenosli.org" + url
                        else:
                            if not url.endswith(".mkv"):
                                url = httptools.downloadpage(url, follow_redirects=False)
                                url = url.headers.get("location")

                    torrents_path = config.get_videolibrary_path() + '/torrents'

                    if not os.path.exists(torrents_path):
                        os.mkdir(torrents_path)

                    urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'
                    urllib.urlretrieve(url, torrents_path + "/temp.torrent")
                    pepe = open(torrents_path + "/temp.torrent", "rb").read()

                    if "used CloudFlare" in pepe:
                        try:
                            urllib.urlretrieve("http://anonymouse.org/cgi-bin/anon-www.cgi/" + url.strip(),
                                               torrents_path + "/temp.torrent")
                            pepe = open(torrents_path + "/temp.torrent", "rb").read()
                        except:
                            pepe = ""
                    torrent = decode(pepe)

                    try:
                        name = torrent["info"]["name"]
                    except:
                        name = "no disponible"
                    try:
                        check_video = scrapertools.find_multiple_matches(str(torrent["info"]["files"]),
                                                                         "'length': (\d+)}")

                        size = max([int(i) for i in check_video])

                        for file in torrent["info"]["files"]:
                            manolo = "%r - %d bytes" % ("/".join(file["path"]), file["length"])
                            if str(size) in manolo:
                                video = manolo

                        ext_v = re.sub(r"-.*? bytes|\.*?\[.*?\]\.|'|\.*?COM.|.*?\[.*?\]|\(.*?\)|.*?\.", "", video)
                        try:
                            os.remove(torrents_path + "/temp.torrent")
                        except:
                            pass
                    except:

                        ext_v = re.sub(r"-.*? bytes|.*?\[.*?\].|'|.*?COM.|.*?\.es\.|.*?\[.*?\]|.*?\(.*?\)\.|.*?\.", "",
                                       name)
                        try:
                            os.remove(torrents_path + "/temp.torrent")
                        except:
                            pass
                except:
                    size = "en estos momentos..."
                    ext_v = "no disponible"
                if "rar" in ext_v:
                    ext_v = ext_v + " -- No reproducible"
                calidad = re.sub(r"</i>", "", calidad)

                if "Alta" in calidad_bloque:
                    title = "[COLOR khaki][B]" + calidad + "[/B][/COLOR]" + "[COLOR darkkhaki][B]" + " -  " + peso + "[/B][/COLOR]" + " " + "[COLOR lemonchiffon]( Video [/COLOR]" + "[COLOR lemonchiffon]" + ext_v + " )[/COLOR]"
                elif "estandar" in calidad_bloque:
                    title = "[COLOR darkcyan][B]" + calidad + "[/B][/COLOR]" + "[COLOR cadetblue][B]" + " -  " + peso + "[/B][/COLOR]" + " " + "[COLOR paleturquoise]( Video [/COLOR]" + "[COLOR paleturquoise]" + ext_v + " )[/COLOR]"
                else:
                    title = "[COLOR dimgray][B]" + calidad + "[/B][/COLOR]" + "[COLOR gray][B]" + " -  " + peso + "[/B][/COLOR]" + " " + "[COLOR lightslategray]( Video [/COLOR]" + "[COLOR lightslategray]" + ext_v + " )[/COLOR]"
                itemlist.append(Item(channel=item.channel, title=title, action="play", url=url, server="torrent",
                                     thumbnail=thumbnail, extra=item.extra, show=item.show,
                                     fanart=item.show.split("|")[0], folder=False))
        if "serie" in item.url:
            title_info = u'\u012F\u03B7\u0492\u03BF'
            title_info = title_info.encode('utf-8')
            title_info = "[COLOR darkseagreen]" + title_info + "[/COLOR]"
            itemlist.append(
                Item(channel=item.channel, action="info_capitulos", title="         " + title_info, url=item.url,
                     thumbnail=thumbnail, fanart=item.show.split("|")[0], extra=extra, show=item.show,
                     category=item.category, folder=False))

    if "serie" in item.url and item.extra.split("|")[0] != "fv2":
        title_info = u'\u03C4\u04BC\u04CE\u0420\u03BF\u0491\u03B1\u0110\u03B1\u0053'
        title_info = title_info.encode('utf-8')
        title_info = "[COLOR springgreen][B]" + title_info + "[/B][/COLOR]"
        itemlist.append(Item(channel=item.channel, title="                                             " + title_info,
                             action="mainlist", url="", fanart=item.show.split("|")[0], thumbnail=thumbnail,
                             folder=False))
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        patron = 'class="contactlinkh">(.*?)<\/a><\/div>(.*?)</div></div></div>'
        matches = re.compile(patron, re.DOTALL).findall(data)

        for temporadas, bloque_capitulos in matches:
            thumbnail = scrapertools.get_match(bloque_capitulos, 'background-image:url\(\'([^"]+)\'')

            thumbnail = re.sub(r"w185", "original", thumbnail)

            itemlist.append(Item(channel=item.channel, title="[COLOR chartreuse][B]" + temporadas + "[/B][/COLOR]",
                                 action="capitulos", url=item.url, thumbnail=thumbnail,
                                 extra="fv2" + "|" + bloque_capitulos + "|" + thumb + "|" + item.extra + "|" + check,
                                 show=item.show, fanart=item.show.split("|")[0], category=item.category, folder=True))

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

        critica = item.extra.split("|")[5]
        if "%20" in critica:
            critica = "No hay críticas"
        icon = "http://imgur.com/SenkyxF.png"
        photo = item.extra.split("|")[0].replace(" ", "%20")
        foto = item.show.split("|")[1]

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
                           critica=critica, contentType=check2,
                           thumb_busqueda="http://s6.postimg.org/u381y91u9/logomil.png")
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
                    fanart = item.extra.split("|")[1]
                plot = info
                plot = "[COLOR peachpuff][B]" + plot + "[/B][/COLOR]"
                title = name_epi.upper()
                title = "[COLOR bisque][B]" + title + "[/B][/COLOR]"
                image = fanart
                foto = item.extra.split("|")[0]
                if not ".png" in foto:
                    foto = "http://imgur.com/wSIln04.png"
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
                foto = "http://imgur.com/wSIln04.png"
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

        self.background = xbmcgui.ControlImage(70, 20, 1150, 630, 'http://imgur.com/Vj7pYVt.jpg')
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


def busqueda(item):
    logger.info()
    cat = [item.extra.split("|")[0].replace("tv", "serie"), 'torrent']
    new_item = Item()
    new_item.extra = item.extra.split("|")[1].replace("+", " ")
    new_item.category = item.extra.split("|")[0]

    from channels import search
    return search.do_search(new_item, cat)
