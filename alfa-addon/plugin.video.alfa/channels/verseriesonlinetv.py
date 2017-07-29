# -*- coding: utf-8 -*-

import os
import re
import urllib2

import xbmc
import xbmcgui
from core import config
from core import logger
from core import scrapertools, httptools
from core import servertools
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

api_key = "2e2160006592024ba87ccdf78c28f49f"
api_fankey = "dffe90fba4d02c199ae7a9e71330c987"


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
    # br.addheaders =[('Cookie','SRCHD=D=4210979&AF=NOFORM; domain=.bing.com; expires=Wednesday, 09-Nov-06 23:12:40 GMT; MUIDB=36F71C46589F6EAD0BE714175C9F68FC; domain=www.bing.com;	expires=15 de enero de 2018 08:43:26 GMT+1')]

    # Open some site, let's pick a random one, the first that pops in mind
    r = br.open("http://anonymouse.org/cgi-bin/anon-www.cgi/" + url)
    response = r.read()
    if not ".ftrH,.ftrHd,.ftrD>" in response:
        print "proooxy"
        r = br.open("http://ssl-proxy.my-addr.org/myaddrproxy.php/" + url)
        response = r.read()
    return response


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(Item(channel=item.channel, title="[COLOR chartreuse][B]Series[/B][/COLOR]", action="scraper",
                         url="http://www.verseriesonline.tv/series",
                         thumbnail="http://s6.postimg.org/6hpa9tzgx/verseriesthumb.png",
                         fanart="http://s6.postimg.org/71zpys3bl/verseriesfan2.jpg"))

    itemlist.append(Item(channel=item.channel, title="[COLOR chartreuse][B]Buscar[/B][/COLOR]", action="search", url="",
                         thumbnail="http://s6.postimg.org/5gp1kpihd/verseriesbuscthumb.png",
                         fanart="http://s6.postimg.org/7vgx54yq9/verseriesbuscfan.jpg", extra="search"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://www.verseriesonline.tv/series?s=" + texto

    try:
        return scraper(item)
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def scraper(item):
    logger.info()
    itemlist = []
    ###Borra customkeys


    # Descarga la página
    data = dhe(httptools.downloadpage(item.url).data)

    patron = '<li class="item">.*?<a class="poster" href="([^"]+)".*?<img src="([^"]+)" alt="([^<]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title_fan = scrapedtitle.strip()

        # Busqueda del año y puntuacion
        urlyear = scrapedurl
        data2 = httptools.downloadpage(scrapedurl).data
        year = scrapertools.get_match(data2, '<h1>.*?<span>\((.*?)\)</span></h1>')
        points = scrapertools.get_match(data2, '<div class="number">.*?<b>(.*?)</b>')
        if points == "":
            points = "No puntuada"

        scrapedtitle = scrapedtitle + " (" + "[COLOR orange][B]" + points + "[/B][/COLOR]" + ")"
        show = title_fan + "|" + year

        scrapedtitle = scrapedtitle.replace(scrapedtitle, "[COLOR springgreen]" + scrapedtitle + "[/COLOR]")
        itemlist.append(
            Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action="fanart", thumbnail=scrapedthumbnail,
                 fanart="http://s6.postimg.org/8pyvdfh75/verseriesfan.jpg", show=show, plot=title_fan, folder=True))

    ## Paginación
    # <span class='current'>1</span><a href='http://www.bricocine.com/c/hd-microhd/page/2/'

    # Si falla no muestra ">> Página siguiente"
    try:

        next_page = scrapertools.get_match(data,
                                           "<span class='current'>\d+</span><a class=\"page larger\" href=\"([^\"]+)\"")

        title = "[COLOR floralwhite]Pagina siguiente>>[/COLOR]"
        itemlist.append(Item(channel=item.channel, title=title, url=next_page, action="scraper",
                             fanart="http://s6.postimg.org/8pyvdfh75/verseriesfan.jpg",
                             thumbnail="http://virtualmarketingpro.com/app/webroot/img/vmp/arrows/Green%20Arrow%20(26).png",
                             folder=True))
    except:
        pass

    return itemlist


def fanart(item):
    # Vamos a sacar todos los fanarts y arts posibles
    logger.info()
    itemlist = []
    url = item.url
    data = dhe(httptools.downloadpage(item.url).data)
    data = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|\[.*?\]|&nbsp;", "", data)
    try:
        sinopsis = scrapertools.get_match(data, '<div class="sinopsis">.*?</b>(.*?)</div>')
        if " . Aquí podrán encontrar la información de toda la serie incluyendo sus temporadas y episodios." in sinopsis:
            sinopsis = ""
        else:
            sinopsis = re.sub(
                '.. Aquí podrán encontrar la información de toda la serie incluyendo sus temporadas y episodios.', '.',
                sinopsis)
    except:
        sinopsis = ""

    title_fan = item.show.split("|")[0]
    title = title_fan.decode('utf8').encode('latin1')
    title = title.replace(' ', '%20')
    item.title = re.sub(r"\(.*?\)", "", item.title)
    year = item.show.split("|")[1]

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
    if sinopsis == "":
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
    data_tmdb = httptools.downloadpage(url_tmdb).data
    data_tmdb = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data_tmdb)
    patron = '"page":1.*?,"id":(.*?),.*?"backdrop_path":(.*?),'
    matches = re.compile(patron, re.DOTALL).findall(data_tmdb)

    ###Busqueda en bing el id de imdb de la serie
    if len(matches) == 0:
        url_tmdb = "http://api.themoviedb.org/3/search/tv?api_key=" + api_key + "&query=" + title + "&language=es"
        data_tmdb = httptools.downloadpage(url_tmdb).data
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
            data_tmdb = httptools.downloadpage(urlremotetbdb).data
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
        data_tvdb = httptools.downloadpage(urlid_tvdb).data
        id = scrapertools.find_single_match(data_tvdb, 'tvdb_id":(.*?),"tvrage_id"')
        if id == "null":
            id = ""
        category = id
        ###Busqueda nºepisodios y temporadas,status
        url_status = "http://api.themoviedb.org/3/tv/" + id_tmdb + "?api_key=" + api_key + "&append_to_response=credits&language=es"
        data_status = httptools.downloadpage(url_status).data
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
            fanart = "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg"
        else:
            fanart = "https://image.tmdb.org/t/p/original" + fan

        if fanart == "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg":
            fanart_info = fanart
            fanart_2 = fanart
            fanart_3 = fanart
            fanart_4 = fanart
        else:
            url = "http://api.themoviedb.org/3/tv/" + id_tmdb + "/images?api_key=" + api_key

            data = httptools.downloadpage(url).data
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

            file_path = scrapertools.find_multiple_matches(data, '"file_path":"(.*?)"')
            if len(file_path) >= 5:
                fanart_info = "https://image.tmdb.org/t/p/original" + file_path[1]
                fanart_2 = "https://image.tmdb.org/t/p/original" + file_path[2]
                fanart_3 = "https://image.tmdb.org/t/p/original" + file_path[3]
                fanart_4 = "https://image.tmdb.org/t/p/original" + file_path[4]
                if fanart == "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg":
                    fanart = "https://image.tmdb.org/t/p/original" + fanart_info
            elif len(file_path) == 4:
                fanart_info = "https://image.tmdb.org/t/p/original" + file_path[1]
                fanart_2 = "https://image.tmdb.org/t/p/original" + file_path[2]
                fanart_3 = "https://image.tmdb.org/t/p/original" + file_path[3]
                fanart_4 = "https://image.tmdb.org/t/p/original" + file_path[1]
                if fanart == "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg":
                    fanart = "https://image.tmdb.org/t/p/original" + fanart_info
            elif len(file_path) == 3:
                fanart_info = "https://image.tmdb.org/t/p/original" + file_path[1]
                fanart_2 = "https://image.tmdb.org/t/p/original" + file_path[2]
                fanart_3 = "https://image.tmdb.org/t/p/original" + file_path[1]
                fanart_4 = "https://image.tmdb.org/t/p/original" + file_path[0]
                if fanart == "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg":
                    fanart = "https://image.tmdb.org/t/p/original" + fanart_info
            elif len(file_path) == 2:
                fanart_info = "https://image.tmdb.org/t/p/original" + file_path[1]
                fanart_2 = "https://image.tmdb.org/t/p/original" + file_path[0]
                fanart_3 = "https://image.tmdb.org/t/p/original" + file_path[1]
                fanart_4 = "https://image.tmdb.org/t/p/original" + file_path[1]
                if fanart == "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg":
                    fanart = "https://image.tmdb.org/t/p/original" + fanart_info
            else:
                fanart_info = fanart
                fanart_2 = fanart
                fanart_3 = fanart
                fanart_4 = fanart

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
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                    else:
                        thumbnail = hdtvlogo
                        extra = thumbnail + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                    itemlist.append(Item(channel=item.channel, title=item.title, action="temporadas", url=item.url,
                                         server="torrent", thumbnail=thumbnail, fanart=fanart, category=category,
                                         extra=extra, show=show, folder=True))


                else:
                    if '"hdclearart"' in data:
                        thumbnail = hdtvlogo
                        extra = hdtvclear + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                    else:
                        thumbnail = hdtvlogo
                        extra = thumbnail + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                    itemlist.append(Item(channel=item.channel, title=item.title, action="temporadas", url=item.url,
                                         server="torrent", thumbnail=thumbnail, fanart=fanart, extra=extra, show=show,
                                         category=category, folder=True))
            else:
                extra = "" + "|" + year
                show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                itemlist.append(
                    Item(channel=item.channel, title=item.title, action="temporadas", url=item.url, server="torrent",
                         thumbnail=posterdb, fanart=fanart, extra=extra, show=show, category=category, folder=True))

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
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                    itemlist.append(Item(channel=item.channel, title=item.title, action="temporadas", url=item.url,
                                         server="torrent", thumbnail=thumbnail, fanart=fanart, extra=extra, show=show,
                                         category=category, folder=True))
                else:
                    extra = clear + "|" + year
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                    itemlist.append(Item(channel=item.channel, title=item.title, action="temporadas", url=item.url,
                                         server="torrent", thumbnail=thumbnail, fanart=fanart, extra=extra, show=show,
                                         category=category, folder=True))

            if "showbackground" in data:

                if '"clearart"' in data:
                    clear = scrapertools.get_match(data, '"clearart":.*?"url": "([^"]+)"')
                    extra = clear + "|" + year
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                else:
                    extra = logo + "|" + year
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                    itemlist.append(Item(channel=item.channel, title=item.title, action="temporadas", url=item.url,
                                         server="torrent", thumbnail=thumbnail, fanart=fanart, extra=extra, show=show,
                                         category=category, folder=True))

            if not '"clearart"' in data and not '"showbackground"' in data:
                if '"hdclearart"' in data:
                    extra = hdtvclear + "|" + year
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                else:
                    extra = thumbnail + "|" + year
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb + "|" + fanart_4
                itemlist.append(
                    Item(channel=item.channel, title=item.title, action="temporadas", url=item.url, server="torrent",
                         thumbnail=thumbnail, fanart=fanart, extra=extra, show=show, category=category, folder=True))
    title = "Info"
    title_info = title.replace(title, "[COLOR seagreen]" + title + "[/COLOR]")

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

    id = id_scraper

    extra = extra + "|" + id + "|" + title.encode('utf8')

    itemlist.append(Item(channel=item.channel, action="info", title=title_info, url=item.url, thumbnail=thumbnail,
                         fanart=fanart_info, extra=extra, category=category, plot=plot, show=show,
                         viewmode="movie_with_plot", folder=False))

    return itemlist


def temporadas(item):
    logger.info()

    itemlist = []

    data = dhe(httptools.downloadpage(item.url).data)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    if "Temporada 0" in data:
        bloque_temporadas = 'Temporada 0.*?(<h3 class="three fourths col-xs-12 pad0">.*?<div class="col-md-4 padl0">)'
        matchestemporadas = re.compile(bloque_temporadas, re.DOTALL).findall(data)

        for bloque_temporadas in matchestemporadas:
            patron = '<h3 class="three fourths col-xs-12 pad0">.*?href="([^"]+)" title="([^<]+)"'
            matches = re.compile(patron, re.DOTALL).findall(bloque_temporadas)

    else:
        patron = '<h3 class="three fourths col-xs-12 pad0">.*?href="([^"]+)" title="([^<]+)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        itemlist.append(Item(channel=item.channel, title="[COLOR gold][B]No hay resultados...[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                             fanart="http://pic.raise5.com/user_pictures/user-1423992581-237429.jpg", folder=False))
    for scrapedurl, scrapedtitle in matches:
        ###Busqueda poster temporada tmdb
        scrapedtitle = scrapedtitle.replace(scrapedtitle, "[COLOR springgreen]" + scrapedtitle + "[/COLOR]")
        temporada = scrapertools.get_match(scrapedtitle, 'Temporada (\d+)')
        scrapedtitle = scrapedtitle.replace("Temporada", "[COLOR darkorange]Temporada[/COLOR]")

        ###Busca poster de temporada Tmdb
        urltmdb_temp = "http://api.themoviedb.org/3/tv/" + item.show.split("|")[
            5] + "/season/" + temporada + "/images?api_key=" + api_key
        data = httptools.downloadpage(urltmdb_temp).data
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        patron = '{"id".*?"file_path":"(.*?)","height"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if len(matches) == 0:
            thumbnail = item.thumbnail
        for temp in matches:
            thumbnail = "https://image.tmdb.org/t/p/original" + temp
        extra = item.extra + "|" + temporada

        itemlist.append(
            Item(channel=item.channel, title=scrapedtitle, action="capitulos", url=scrapedurl, thumbnail=thumbnail,
                 fanart=item.show.split("|")[0], show=item.show, extra=extra, category=item.category, folder=True))

    return itemlist


def capitulos(item):
    logger.info()

    itemlist = []

    data = dhe(httptools.downloadpage(item.url).data)
    patron = '<div class="item_episodio col-xs-3 ">.*?href="([^"]+)" title="([^<]+)".*?<img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        itemlist.append(
            Item(channel=item.channel, title="[COLOR coral][B]" + "no hay capítulos...".upper() + "[/B][/COLOR]",
                 thumbnail="http://s6.postimg.org/wa269heq9/verseriesnohaythumb.png",
                 fanart="http://s6.postimg.org/4nzeosvdd/verseriesnothingfan.jpg", folder=False))
    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = re.sub(r"(.*?Temporada \d+)", "", scrapedtitle).strip()
        capitulo = re.sub(r"Capitulo", "", scrapedtitle).strip()
        scrapedtitle = scrapedtitle.replace(scrapedtitle, "[COLOR limegreen]" + scrapedtitle + "[/COLOR]")
        extra = item.extra + "|" + capitulo

        itemlist.append(Item(channel=item.channel, title=scrapedtitle, action="findvideos", url=scrapedurl,
                             thumbnail=item.show.split("|")[4], fanart=item.show.split("|")[1], show=item.show,
                             extra=extra, category=item.category, folder=True))
        title = "Info"
        title = title.replace(title, "[COLOR darkseagreen]" + title + "[/COLOR]")
        itemlist.append(
            Item(channel=item.channel, action="info_capitulos", title=title, url=item.url, thumbnail=scrapedthumbnail,
                 fanart=item.show.split("|")[1], extra=extra, show=item.show, category=item.category, folder=False))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<td><a href="([^"]+)".*?<img src="([^"]+)" title="([^<]+)" .*?<td>([^<]+)</td>.*?<td>([^<]+)</td>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    print matches
    for scrapedurl, scrapedthumbnail, scrapedserver, scrapedidioma, scrapedcalidad in matches:

        server = scrapertools.get_match(scrapedserver, '(.*?)[.]')
        icon_server = os.path.join(config.get_runtime_path(), "resources", "images", "servers",
                                   "server_" + server + ".png")
        icon_server = re.sub(r"tv|com|net|", "", icon_server)
        icon_server = icon_server.replace('streamin', 'streaminto')
        icon_server = icon_server.replace('ul', 'uploadedto')

        if not os.path.exists(icon_server):
            icon_server = scrapedthumbnail

        scrapedserver = scrapedserver.replace(scrapedserver,
                                              "[COLOR darkorange][B]" + "[" + scrapedserver + "]" + "[/B][/COLOR]")
        scrapedidioma = scrapedidioma.replace(scrapedidioma,
                                              "[COLOR lawngreen][B]" + "--" + scrapedidioma + "--" + "[/B][/COLOR]")
        scrapedcalidad = scrapedcalidad.replace(scrapedcalidad,
                                                "[COLOR floralwhite][B]" + scrapedcalidad + "[/B][/COLOR]")

        title = scrapedserver + scrapedidioma + scrapedcalidad
        itemlist.append(Item(channel=item.channel, title=title, action="play", url=scrapedurl, thumbnail=icon_server,
                             fanart=item.show.split("|")[6], extra=item.thumbnail, folder=True))

    return itemlist


def play(item):
    logger.info()
    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')

    itemlist = servertools.find_video_items(data=item.url)

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
            data_plot = httptools.downloadpage(url_plot).data
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
        rating = ""
        rating_filam = ""

    if "serie" in item.url:
        check2 = "serie"

        icon = "http://s6.postimg.org/hzcjag975/tvdb.png"
        foto = item.show.split("|")[1]
        if not "image.tmdb" in foto:
            foto = ""
        if item.extra.split("|")[5] != "":
            critica = item.extra.split("|")[5]
        else:
            critica = "Esta serie no tiene críticas..."

        photo = item.extra.split("|")[0].replace(" ", "%20")
        if not ".png" in photo:
            photo = ""
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
        data_tpi = httptools.downloadpage(url_tpi).data
        tpi = scrapertools.find_multiple_matches(data_tpi,
                                                 'id":(.*?),.*?"original_name":"(.*?)",.*?"poster_path":(.*?),"popularity"')

    else:
        url_tpi = "http://api.themoviedb.org/3/movie/" + item.extra.split("|")[
            1] + "/recommendations?api_key=" + api_key + "&language=es"
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

    check2 = check2.replace("pelicula", "movie").replace("serie", "tvshow")
    infoLabels = {'title': title, 'plot': plot, 'thumbnail': photo, 'fanart': foto, 'tagline': tagline,
                  'rating': rating}
    item_info = item.clone(info=infoLabels, icon=icon, extra=id, rating=rating, rating_filma=rating_filma,
                           critica=critica, contentType=check2, thumb_busqueda="http://imgur.com/zKjAjzB.png")
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
                    foto = "http://imgur.com/zKjAjzB.png"

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
                foto = "http://imgur.com/zKjAjzB.png"
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

        self.background = xbmcgui.ControlImage(70, 20, 1150, 630, 'http://imgur.com/mpMQp6c.jpg')
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
