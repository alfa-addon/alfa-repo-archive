# -*- coding: utf-8 -*-

import re
import unicodedata
import urlparse

import xbmc
import xbmcgui
from core import logger
from core import scrapertools, httptools
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


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="[COLOR forestgreen]Cine[/COLOR]", action="scraper",
                         url="http://cuelgame.net/?category=4",
                         thumbnail="http://img5a.flixcart.com/image/poster/q/t/d/vintage-camera-collage-sr148-medium-400x400-imadkbnrnbpggqyz.jpeg",
                         fanart="http://imgur.com/7frGoPL.jpg"))
    itemlist.append(Item(channel=item.channel, title="[COLOR forestgreen]Series[/COLOR]", action="scraper",
                         url="http://cuelgame.net/?category=8", thumbnail="http://imgur.com/OjP42lL.jpg",
                         fanart="http://imgur.com/Xm49VbL.jpg"))
    itemlist.append(Item(channel=item.channel, title="[COLOR forestgreen]TV[/COLOR]", action="scraper",
                         url="http://cuelgame.net/?category=67", thumbnail="http://imgur.com/C4VDnTo.png",
                         fanart="http://imgur.com/LDoJrAf.jpg"))
    itemlist.append(Item(channel=item.channel, title="[COLOR forestgreen]Documentales[/COLOR]", action="scraper",
                         url="http://cuelgame.net/?category=68", thumbnail="http://imgur.com/nofNYjy.jpg",
                         fanart="http://imgur.com/upB1jL8.jpg"))
    itemlist.append(Item(channel=item.channel, title="[COLOR forestgreen]Música[/COLOR]", action="scraper",
                         url="http://cuelgame.net/?category=13", thumbnail="http://imgur.com/DPrOlme.jpg",
                         fanart="http://imgur.com/FxM6xGY.jpg"))

    itemlist.append(Item(channel=item.channel, title="[COLOR forestgreen]Buscar[/COLOR]", action="search", url="",
                         thumbnail="http://images2.alphacoders.com/846/84682.jpg",
                         fanart="http://imgur.com/1sIHN1r.jpg"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://cuelgame.net/search.php?q=%s" % (texto)

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
    check_search = item.url
    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|CET", "", data)

    # corrige la falta de imagen
    # data = re.sub(r" </div><p>","</div><img src='http://ampaenriquealonso.files.wordpress.com/2011/09/logocineenlacalle.png' texto ><p>",data)

    '''
   <h2> <a href="magnet:?xt=urn:btih:4E7192D0885DDB9219699BBFFD72E709006BF9F2&amp;dn=automata+2014+hdrip+xvid+sam+etrg&amp;tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce" class="l:12087"onmousedown="return clk(this, 12087)" >Automata (2014) [HDRip] [VO] </a><img src="http://cuelgame.net/img/common/is-magnet.png" class="media-icon" width="18" height="15" alt="magnet" title="magnet" /> <a href="magnet:?xt=urn:btih:4E7192D0885DDB9219699BBFFD72E709006BF9F2&dn=automata+2014+hdrip+xvid+sam+etrg&tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce" title="Direct link" rel="nofollow, noindex"><img src="http://cuelgame.net/img/common/link-02.png" class="media-icon" width="18" height="15" alt="Enlace directo" title="Enlace directo" /></a> </h2> <div class="news-submitted"><a href="/user/Dios" class="tooltip u:1179"><img src="http://cuelgame.net/cache/00/04/1179-1328100564-25.jpg" width="25" height="25" alt=""/></a><strong>magnet:?xt=urn:btih:4E7192D0885DDB9219699BBFFD72E709006BF...</strong><br /> por<a href="/user/Dios/history">Dios</a> hace7 horaspublicado hace5 horas 58 minutos</div><img src='http://cuelgame.net/cache/00/2f/thumb-12087.jpg' width='70' height='70' alt='' class='thumbnail'/><p> En un futuro no lejano, en el que el planeta Tierra sufre una creciente desertización, Jacq Vaucan (Antonio Banderas), un agente de seguros de una compañía de robótica, investiga un caso en apariencia rutinario cuando descubre algo que podría tener consecuencias decisivas para el futuro de la humanidad. Banderas produce y protagoniza este thriller futurista, que especula sobre lo que ocurriría si la inteligencia artificial superase a la humana.|<i> Más info. en comentarios.</i></p>

    '''
    # id_torrent = scrapertools.get_match(item.url,"(\d+)-")
    patron = '<h2> <a href="([^"]+)".*?class="l:\d+".*?>(.*?)<\/a>(.*?)<p>([^<]+)<.*?p>.*?title="meta.*?href=".*?amp;(.*?)"'
    '''
    patron += '<a href="([^"]+)".*?'
    patron += 'class="l:\d+".*? >([^<]+)</a>.*?'
    patron += '<img src=\'([^\']+)\'.*?'
    patron += '<p>([^<]+)<.*?p>'
    patron += '.*?class="counter">.*?<a href="\/\?meta=multimedia&amp;(.*?)"'
    '''
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, check_thumb, scrapedplot, check_multimedia in matches:
        scrapedtitle = re.sub(r'\.', ' ', scrapedtitle)
        try:
            scrapedthumbnail = scrapertools.get_match(check_thumb, "</div><img src=\'([^\']+)\'")
        except:
            scrapedthumbnail = "http://ampaenriquealonso.files.wordpress.com/2011/09/logocineenlacalle.png"
        item.url = check_search
        title_year = re.sub(r"(\d+)p", "", scrapedtitle)
        if "search" in item.url:
            if "category=4" or "category=8" in check_multimedia:
                item.url = check_multimedia
        if "category=4" in item.url:
            try:
                year = scrapertools.find_single_match(title_year, '.*?(\d\d\d\d)')
            except:
                year = ""
        else:
            year = ""

        title_fan = re.sub(
            r"End Part \d|\||\[.*?\].*|\(.*?\).*|\d+x\d+.*?Final|-\d+|\d+x\d+|Temporada.*?Completa| ;|V.O|\d.*?GB|\+|subs|s\d+e\d+p.*|s\d+e\d+i.*|s\d+e\d+.*|S\d+E\d+[^<]+|VO|Serie.*|S\d+E\d+p.*|S\d+E\d+720p.*",
            "", scrapedtitle)

        # No deja pasar items de la mula
        if not scrapedurl.startswith("ed2k:"):
            scrapedtitle.strip()
            scrapedplot = re.sub(r"\|<i> Más info. en comentarios.</i>", "", scrapedplot)
            scrapedplot = re.sub(r"<.*?>", "", scrapedplot).strip()

        scrapedtitle = "[COLOR greenyellow]" + scrapedtitle + "[/COLOR]"

        extra = title_fan + "|" + year + "|" + scrapedplot + "|" + scrapedurl + "|" + item.url

        if "category=4" in item.url or "category=8" in item.url:

            itemlist.append(Item(channel=item.channel, title=scrapedtitle, url="", action="fanart", server="torrent",
                                 thumbnail=scrapedthumbnail, extra=extra, folder=True))
        else:

            itemlist.append(
                Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action="play", server="torrent",
                     thumbnail=scrapedthumbnail, folder=False))

    # Extrae el paginador


    patronvideos = '<a href="([^"]+)" rel="next">siguiente &#187;</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        # corrige "&" para la paginación
        next_page = matches[0].replace("amp;", "")

        if "search" in check_search:
            scrapedurl = urlparse.urljoin(check_search, next_page)
        else:
            scrapedurl = urlparse.urljoin(item.url, next_page)
        itemlist.append(Item(channel=item.channel, action="scraper", title="Página siguiente >>", url=scrapedurl,
                             thumbnail="http://imgur.com/ycPgVVO.png", folder=True))

    return itemlist


def fanart(item):
    logger.info()
    itemlist = []

    check_sp = item.extra.split("|")[4]
    title_fan = item.extra.split("|")[0]
    fulltitle = item.title
    fulltitle = re.sub(r"720p|1080.*", "", fulltitle)
    title_fan = re.sub(r"H264.*|Netflix.*|Mitos Griegos|HDTV.*|\d\d\d\d", "", title_fan).strip()
    item.title = title_fan.upper()
    item.title = "[COLOR springgreen][B]" + item.title + "[/B][/COLOR]"
    title = title_fan.replace(' ', '%20')
    title = ''.join((c for c in unicodedata.normalize('NFD', unicode(title.decode('utf-8'))) if
                     unicodedata.category(c) != 'Mn')).encode("ascii", "ignore")
    item.url = item.extra.split("|")[3]

    try:
        sinopsis = item.extra.split("|")[2]
    except:
        sinopsis = ""

    if "category=4" in check_sp:
        id_tmdb = ""
        # filmafinity
        year = item.extra.split("|")[1]

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
                extra = item.thumbnail + "|" + "" + "|" + "" + "|" + "Sin puntuación" + "|" + rating_filma + "|" + critica
                show = item.fanart + "|" + "" + "|" + sinopsis
                posterdb = item.thumbnail
                fanart_info = item.fanart
                fanart_3 = ""
                fanart_2 = item.fanart
                category = item.thumbnail
                id_scraper = ""

                itemlist.append(
                    Item(channel=item.channel, title=item.title, url=item.url, action="play", server="torrent",
                         thumbnail=item.thumbnail, fanart=item.fanart, extra=extra, show=show, category=category,
                         folder=False))

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
                    Item(channel=item.channel, title=item.title, action="play", url=item.url, server="torrent",
                         thumbnail=posterdb, fanart=item.extra, extra=extra, show=show, category=category,
                         folder=False))
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
                        itemlist.append(
                            Item(channel=item.channel, title=item.title, action="play", url=item.url, server="torrent",
                                 thumbnail=logo, fanart=item.extra, extra=extra, show=show, category=category,
                                 folder=False))
                    else:
                        extra = clear
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis
                        if '"moviedisc"' in data:
                            category = disc
                        else:
                            category = clear
                        itemlist.append(
                            Item(channel=item.channel, title=item.title, action="play", url=item.url, server="torrent",
                                 thumbnail=logo, fanart=item.extra, extra=extra, show=show, category=category,
                                 folder=False))

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

                        itemlist.append(
                            Item(channel=item.channel, title=item.title, action="play", url=item.url, server="torrent",
                                 thumbnail=logo, fanart=item.extra, extra=extra, show=show, category=category,
                                 folder=False))

                if not '"hdmovieclearart"' in data and not '"moviebackground"' in data:
                    extra = logo
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis
                    if '"moviedisc"' in data:
                        category = disc
                    else:
                        category = item.extra
                    itemlist.append(
                        Item(channel=item.channel, title=item.title, action="play", url=item.url, server="torrent",
                             thumbnail=logo, fanart=item.extra, extra=extra, show=show, category=category,
                             folder=False))


    else:
        # Busca la temporada y capitulo de la serie.

        try:
            temp, epi = scrapertools.find_single_match(fulltitle, 'S(\d+)E(\d+)')
            temp_epi = ""
        except:
            try:
                temp, epi = scrapertools.find_single_match(fulltitle, 's(\d+)e(\d+)')
                temp_epi = ""
            except:
                try:
                    temp, epi = scrapertools.find_single_match(fulltitle, '(\d+)x(\d+)')
                    temp_epi = ""
                except:
                    temp_epi = "No capitulos"

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
                                                             '"tv_results":.*?"id":(.*?),.*?"poster_path":(.*?),"popularity"')

                if len(matches) == 0:
                    id_tmdb = ""
                    fanart_3 = ""
                    extra = item.thumbnail + "|" + year + "|" + "no data" + "|" + "no data" + "|" + "Sin puntuación" + "|" + "" + "|" + "" + "|" + id_tmdb
                    show = item.fanart + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + item.thumbnail + "|" + id_tmdb
                    fanart_info = item.fanart
                    fanart_2 = item.fanart
                    id_scraper = ""
                    category = ""
                    posterdb = item.thumbnail
                    if temp_epi:
                        itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="play",
                                             thumbnail=item.thumbnail, fanart=item.fanart, server="torrent",
                                             extra=extra, category=category, show=show, folder=False))
                    else:
                        itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                             thumbnail=item.thumbnail, fanart=item.fanart, fulltitle=fulltitle,
                                             extra=extra, category=category, show=show, folder=True))

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
                        if temp_epi:
                            itemlist.append(Item(channel=item.channel, title=item.title, action="play", url=item.url,
                                                 server="torrent", thumbnail=thumbnail, fanart=item.extra,
                                                 category=category, extra=extra, show=show, folder=False))
                        else:
                            itemlist.append(
                                Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                     fulltitle=temp + "|" + epi, thumbnail=thumbnail, fanart=item.extra,
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
                        if temp_epi:
                            itemlist.append(Item(channel=item.channel, title=item.title, action="play", url=item.url,
                                                 server="torrent", thumbnail=thumbnail, fanart=item.extra,
                                                 category=category, extra=extra, show=show, folder=False))
                        else:
                            itemlist.append(
                                Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                     fulltitle=temp + "|" + epi, thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                     show=show, category=category, folder=True))
                else:
                    extra = "" + "|" + year
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                    if temp_epi:
                        itemlist.append(
                            Item(channel=item.channel, title=item.title, action="play", url=item.url, server="torrent",
                                 thumbnail=posterdb, fanart=fanart, extra=extra, show=show, category=category,
                                 folder=False))
                    else:
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             fulltitle=temp + "|" + epi, thumbnail=posterdb, fanart=fanart, extra=extra,
                                             show=show, category=category, folder=True))

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
                        if temp_epi:
                            itemlist.append(Item(channel=item.channel, title=item.title, action="play", url=item.url,
                                                 server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                                 show=show, category=category, folder=False))
                        else:
                            itemlist.append(
                                Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                     fulltitle=temp + "|" + epi, thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                     show=show, category=category, folder=True))

                    else:
                        extra = clear + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                        if temp_epi:
                            itemlist.append(Item(channel=item.channel, title=item.title, action="play", url=item.url,
                                                 server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                                 show=show, category=category, folder=False))
                        else:
                            itemlist.append(
                                Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                     fulltitle=temp + "|" + epi, thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                     show=show, category=category, folder=True))

                if "showbackground" in data:

                    if '"clearart"' in data:
                        clear = scrapertools.get_match(data, '"clearart":.*?"url": "([^"]+)"')
                        extra = clear + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                    else:
                        extra = logo + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                        if temp_epi:
                            itemlist.append(Item(channel=item.channel, title=item.title, action="play", url=item.url,
                                                 server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                                 show=show, category=category, folder=False))
                        else:
                            itemlist.append(
                                Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                     fulltitle=temp + "|" + epi, thumbnail=thumbnail, fanart=item.extra, extra=extra,
                                     show=show, category=category, folder=True))

                if not '"clearart"' in data and not '"showbackground"' in data:
                    if '"hdclearart"' in data:
                        extra = hdtvclear + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                    else:
                        extra = thumbnail + "|" + year
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + tfv + "|" + id_tmdb
                    if temp_epi:
                        itemlist.append(
                            Item(channel=item.channel, title=item.title, action="play", url=item.url, server="torrent",
                                 thumbnail=thumbnail, fanart=item.extra, extra=extra, show=show, category=category,
                                 folder=False))
                    else:
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             fulltitle=temp + "|" + epi, thumbnail=thumbnail, fanart=item.extra,
                                             extra=extra, show=show, category=category, folder=True))
    title_info = "[COLOR olivedrab][B]Info[/B][/COLOR]"
    if not "serie" in item.url:
        thumbnail = posterdb

    if "serie" in item.url:

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

    extra = extra + "|" + id + "|" + title.encode('utf8') + "|" + check_sp

    itemlist.append(
        Item(channel=item.channel, action="info", title=title_info, plot=plot, url=item.url, thumbnail=thumbnail,
             fanart=fanart_info, extra=extra, category=category, show=show, viewmode="movie_with_plot", folder=False))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    temp = item.fulltitle.split("|")[0]
    epi = item.fulltitle.split("|")[1]

    url_temp = "http://api.themoviedb.org/3/tv/" + item.show.split("|")[
        5] + "/season/" + temp + "/images?api_key=" + api_key + ""
    data = httptools.downloadpage(url_temp).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '{"id".*?"file_path":"(.*?)","height"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        thumbnail = item.thumbnail
    for thumtemp in matches:
        thumbnail = "https://image.tmdb.org/t/p/original" + thumtemp
        title = item.show.split("|")[3] + " " + temp + "x" + epi
        title = "[COLOR lightgreen]" + title + "[/COLOR]"
        itemlist.append(Item(channel=item.channel, title=title, action="play", url=item.url, server="torrent",
                             thumbnail=item.show.split("|")[4], extra=item.extra, show=item.show,
                             fanart=item.show.split("|")[0], fulltitle=title, folder=False))
    extra = item.extra + "|" + temp + "|" + epi
    title_info = "    Info"
    title_info = "[COLOR darkseagreen]" + title_info + "[/COLOR]"
    itemlist.append(
        Item(channel=item.channel, action="info_capitulos", title=title_info, url=item.url, thumbnail=thumbnail,
             fanart=item.show.split("|")[1], extra=extra, show=item.show, category=item.category, folder=False))
    return itemlist


def info(item):
    logger.info()
    itemlist = []
    url = item.url
    id = item.extra

    if "serie" in item.extra.split("|")[3]:
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
        if "serie" in item.extra.split("|")[3]:
            title = item.extra.split("|")[8]

        else:
            title = item.extra.split("|")[6]
        title = title.replace("%20", " ")
        title = "[COLOR green][B]" + title + "[/B][/COLOR]"
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
        if not "serie" in item.extra.split("|")[3]:
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

    if "serie" in item.extra.split("|")[3]:
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
    if "serie" in item.extra.split("|")[3]:

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
                           critica=critica, contentType=check2, thumb_busqueda="http://imgur.com/HqI3JnO.png")
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
                foto = "http://imgur.com/X5Xy4ip.png"
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

        self.background = xbmcgui.ControlImage(70, 20, 1150, 630, 'http://imgur.com/btby9SG.jpg')
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
