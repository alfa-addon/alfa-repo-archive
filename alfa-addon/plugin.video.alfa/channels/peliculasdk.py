# -*- coding: utf-8 -*-

import re

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.scrapertools import decodeHtmlentities as dhe

try:
    import xbmc
    import xbmcgui
except:
    pass
import unicodedata

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

host = "http://www.peliculasdk.com/"


def bbcode_kodi2html(text):
    if config.get_platform().startswith("plex") or config.get_platform().startswith("mediaserver"):
        import re
        text = re.sub(r'\[COLOR\s([^\]]+)\]',
                      r'<span style="color: \1">',
                      text)
        text = text.replace('[/COLOR]', '</span>')
        text = text.replace('[CR]', '<br>')
        text = text.replace('[B]', '<b>')
        text = text.replace('[/B]', '</b>')
        text = text.replace('"color: yellow"', '"color: gold"')
        text = text.replace('"color: white"', '"color: auto"')

    return text


def mainlist(item):
    logger.info()
    itemlist = []
    title = "Estrenos"
    title = title.replace(title, bbcode_kodi2html("[COLOR orange]" + title + "[/COLOR]"))
    itemlist.append(
        Item(channel=item.channel, title=title, action="peliculas", url="http://www.peliculasdk.com/ver/estrenos",
             fanart="http://s24.postimg.org/z6ulldcph/pdkesfan.jpg",
             thumbnail="http://s16.postimg.org/st4x601d1/pdkesth.jpg"))
    title = "PelisHd"
    title = title.replace(title, bbcode_kodi2html("[COLOR orange]" + title + "[/COLOR]"))
    itemlist.append(
        Item(channel=item.channel, title=title, action="peliculas", url="http://www.peliculasdk.com/calidad/HD-720/",
             fanart="http://s18.postimg.org/wzqonq3w9/pdkhdfan.jpg",
             thumbnail="http://s8.postimg.org/nn5669ln9/pdkhdthu.jpg"))
    title = "Pelis HD-Rip"
    title = title.replace(title, bbcode_kodi2html("[COLOR orange]" + title + "[/COLOR]"))
    itemlist.append(
        Item(channel=item.channel, title=title, action="peliculas", url="http://www.peliculasdk.com/calidad/HD-320",
             fanart="http://s7.postimg.org/3pmnrnu7f/pdkripfan.jpg",
             thumbnail="http://s12.postimg.org/r7re8fie5/pdkhdripthub.jpg"))
    title = "Pelis Audio español"
    title = title.replace(title, bbcode_kodi2html("[COLOR orange]" + title + "[/COLOR]"))
    itemlist.append(
        Item(channel=item.channel, title=title, action="peliculas", url="http://www.peliculasdk.com/idioma/Espanol/",
             fanart="http://s11.postimg.org/65t7bxlzn/pdkespfan.jpg",
             thumbnail="http://s13.postimg.org/sh1034ign/pdkhsphtub.jpg"))
    title = "Buscar..."
    title = title.replace(title, bbcode_kodi2html("[COLOR orange]" + title + "[/COLOR]"))
    itemlist.append(
        Item(channel=item.channel, title=title, action="search", url="http://www.peliculasdk.com/calidad/HD-720/",
             fanart="http://s14.postimg.org/ceqajaw2p/pdkbusfan.jpg",
             thumbnail="http://s13.postimg.org/o85gsftyv/pdkbusthub.jpg"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")

    item.url = "http://www.peliculasdk.com/index.php?s=%s&x=0&y=0" % (texto)

    try:
        return buscador(item)
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def buscador(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<div class="karatula".*?'
    patron += 'src="([^"]+)".*?'
    patron += '<div class="tisearch"><a href="([^"]+)">'
    patron += '([^<]+)<.*?'
    patron += 'Audio:(.*?)</a>.*?'
    patron += 'Género:(.*?)</a>.*?'
    patron += 'Calidad:(.*?),'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedthumbnail, scrapedurl, scrapedtitle, scrapedlenguaje, scrapedgenero, scrapedcalidad in matches:
        try:
            year = scrapertools.get_match(scrapedtitle, '\((\d+)\)')
        except:
            year = ""
        title_fan = re.sub(r"\[.*?\]|\(.*?\)|\d+x\d+.*?Final|-\d+|-|\d+x\d+|Temporada.*?Completa| ;", "",
                           scrapedtitle).strip()
        scrapedcalidad = re.sub(r"<a href.*?>|</a>|</span>", "", scrapedcalidad).strip()
        scrapedlenguaje = re.sub(r"<a href.*?>|</a>|</span>", "", scrapedlenguaje).strip()

        if not "Adultos" in scrapedgenero and not "Adultos" in scrapedlenguaje and not "Adultos" in scrapedcalidad:
            scrapedcalidad = scrapedcalidad.replace(scrapedcalidad,
                                                    bbcode_kodi2html("[COLOR orange]" + scrapedcalidad + "[/COLOR]"))
            scrapedlenguaje = scrapedlenguaje.replace(scrapedlenguaje,
                                                      bbcode_kodi2html("[COLOR orange]" + scrapedlenguaje + "[/COLOR]"))

            scrapedtitle = scrapedtitle + "-(Idioma: " + scrapedlenguaje + ")" + "-(Calidad: " + scrapedcalidad + ")"
            scrapedtitle = scrapedtitle.replace(scrapedtitle,
                                                bbcode_kodi2html("[COLOR white]" + scrapedtitle + "[/COLOR]"))
            extra = year + "|" + title_fan
            itemlist.append(Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action="fanart",
                                 thumbnail=scrapedthumbnail, extra=extra,
                                 fanart="http://s18.postimg.org/h9kb22mnt/pdkfanart.jpg", library=True, folder=True))

    try:
        next_page = scrapertools.get_match(data,
                                           '<span class="current">.*?<a href="(.*?)".*?>Siguiente &raquo;</a></div>')

        title = "siguiente>>"
        title = title.replace(title, bbcode_kodi2html("[COLOR red]" + title + "[/COLOR]"))
        itemlist.append(Item(channel=item.channel, action="buscador", title=title, url=next_page,
                             thumbnail="http://s6.postimg.org/uej03x4r5/bricoflecha.png",
                             fanart="http://s18.postimg.org/h9kb22mnt/pdkfanart.jpg", folder=True))
    except:
        pass

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|&#.*?;", "", data)

    patron = 'style="position:relative;"> '
    patron += '<a href="([^"]+)" '
    patron += 'title="([^<]+)">'
    patron += '<img src="([^"]+)".*?'
    patron += 'Audio:(.*?)</br>.*?'
    patron += 'Calidad:(.*?)</br>.*?'
    patron += 'Género:.*?tag">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedlenguaje, scrapedcalidad, scrapedgenero in matches:

        try:
            year = scrapertools.get_match(scrapedtitle, '\((\d+)\)')
        except:
            year = ""
        title_fan = re.sub(r"\[.*?\]|\(.*?\)|\d+x\d+.*?Final|-\d+|-|\d+x\d+|Temporada.*?Completa| ;", "", scrapedtitle)
        scrapedtitle = re.sub(r"\(\d+\)", "", scrapedtitle).strip()
        scrapedcalidad = re.sub(r"<a href.*?>|</a>", "", scrapedcalidad).strip()
        scrapedlenguaje = re.sub(r"<a href.*?>|</a>", "", scrapedlenguaje).strip()
        scrapedcalidad = scrapedcalidad.replace(scrapedcalidad,
                                                bbcode_kodi2html("[COLOR orange]" + scrapedcalidad + "[/COLOR]"))

        if not "Adultos" in scrapedgenero and not "Adultos" in scrapedlenguaje and not "Adultos" in scrapedcalidad:
            scrapedlenguaje = scrapedlenguaje.replace(scrapedlenguaje,
                                                      bbcode_kodi2html("[COLOR orange]" + scrapedlenguaje + "[/COLOR]"))

            scrapedtitle = scrapedtitle + "-(Idioma: " + scrapedlenguaje + ")" + "-(Calidad: " + scrapedcalidad + ")"
            scrapedtitle = scrapedtitle.replace(scrapedtitle,
                                                bbcode_kodi2html("[COLOR white]" + scrapedtitle + "[/COLOR]"))
            extra = year + "|" + title_fan
            itemlist.append(Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action="fanart",
                                 thumbnail=scrapedthumbnail, extra=extra,
                                 fanart="http://s18.postimg.org/h9kb22mnt/pdkfanart.jpg", library=True, folder=True))
    ## Paginación

    next_page = scrapertools.get_match(data, '<span class="current">.*?<a href="(.*?)".*?>Siguiente &raquo;</a></div>')

    title = "siguiente>>"
    title = title.replace(title, bbcode_kodi2html("[COLOR red]" + title + "[/COLOR]"))
    itemlist.append(Item(channel=item.channel, action="peliculas", title=title, url=next_page,
                         thumbnail="http://s6.postimg.org/uej03x4r5/bricoflecha.png",
                         fanart="http://s18.postimg.org/h9kb22mnt/pdkfanart.jpg", folder=True))

    return itemlist


def fanart(item):
    logger.info()
    itemlist = []
    url = item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    title_fan = item.extra.split("|")[1]
    title = re.sub(r'Serie Completa|Temporada.*?Completa', '', title_fan)
    fulltitle = title
    title = title.replace(' ', '%20')
    title = ''.join(
        (c for c in unicodedata.normalize('NFD', unicode(title.decode('utf-8'))) if unicodedata.category(c) != 'Mn'))
    try:
        sinopsis = scrapertools.find_single_match(data, '<span class="clms">Sinopsis: <\/span>(.*?)<\/div>')
    except:
        sinopsis = ""
    year = item.extra.split("|")[0]

    if not "series" in item.url:

        # filmafinity
        url = "http://www.filmaffinity.com/es/advsearch.php?stext={0}&stype%5B%5D=title&country=&genre=&fromyear={1}&toyear={1}".format(
            title, year)
        data = scrapertools.downloadpage(url)

        url_filmaf = scrapertools.find_single_match(data, '<div class="mc-poster">\s*<a title="[^"]*" href="([^"]+)"')
        if url_filmaf:
            url_filmaf = "http://www.filmaffinity.com%s" % url_filmaf
            data = scrapertools.downloadpage(url_filmaf)
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
                    data = scrapertools.cachePage("http://" + url_filma)
                else:
                    data = scrapertools.cachePage(url_filma)
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

        url = "http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title + "&year=" + year + "&language=es&include_adult=false"
        data = scrapertools.cachePage(url)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        patron = '"page":1.*?,"id":(.*?),.*?"backdrop_path":(.*?),'
        matches = re.compile(patron, re.DOTALL).findall(data)

        if len(matches) == 0:

            title = re.sub(r":.*|\(.*?\)", "", title)
            url = "http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title + "&language=es&include_adult=false"

            data = scrapertools.cachePage(url)
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

                itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                     thumbnail=item.thumbnail, fanart=item.fanart, extra=extra, show=show,
                                     category=category, library=item.library, fulltitle=fulltitle, folder=True))

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

            url = "http://api.themoviedb.org/3/movie/" + id + "/images?api_key=2e2160006592024ba87ccdf78c28f49f"
            data = scrapertools.cachePage(url)
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
            # clearart, fanart_2 y logo
            url = "http://webservice.fanart.tv/v3/movies/" + id + "?api_key=dffe90fba4d02c199ae7a9e71330c987"
            data = scrapertools.cachePage(url)
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
                         thumbnail=posterdb, fanart=item.extra, extra=extra, show=show, category=category,
                         library=item.library, fulltitle=fulltitle, folder=True))
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
                                             show=show, category=category, library=item.library, fulltitle=fulltitle,
                                             folder=True))
                    else:
                        extra = clear
                        show = fanart_2 + "|" + fanart_3 + "|" + sinopsis
                        if '"moviedisc"' in data:
                            category = disc
                        else:
                            category = clear
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,
                                             show=show, category=category, library=item.library, fulltitle=fulltitle,
                                             folder=True))

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
                                             show=show, category=category, library=item.library, fulltitle=fulltitle,
                                             folder=True))

                if not '"hdmovieclearart"' in data and not '"moviebackground"' in data:
                    extra = logo
                    show = fanart_2 + "|" + fanart_3 + "|" + sinopsis
                    if '"moviedisc"' in data:
                        category = disc
                    else:
                        category = item.extra
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                         server="torrent", thumbnail=logo, fanart=item.extra, extra=extra, show=show,
                                         category=category, library=item.library, fulltitle=fulltitle, folder=True))

    title_info = "Info"

    if posterdb == item.thumbnail:
        if '"movieposter"' in data:
            thumbnail = poster
        else:
            thumbnail = item.thumbnail
    else:
        thumbnail = posterdb

    id = id_scraper

    extra = extra + "|" + id + "|" + title.encode('utf8')

    title_info = title_info.replace(title_info, bbcode_kodi2html("[COLOR skyblue]" + title_info + "[/COLOR]"))
    itemlist.append(Item(channel=item.channel, action="info", title=title_info, url=item.url, thumbnail=thumbnail,
                         fanart=fanart_info, extra=extra, category=category, show=show, folder=False))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"<!--.*?-->", "", data)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    bloque_tab = scrapertools.find_single_match(data, '<div id="verpelicula">(.*?)<div class="tab_container">')
    patron = '<li><a href="#([^<]+)"><span class="re">\d<\/span><span class="([^<]+)"><\/span><span class=.*?>([^<]+)<\/span>'
    check = re.compile(patron, re.DOTALL).findall(bloque_tab)

    servers_data_list = []

    patron = '<div id="(tab\d+)" class="tab_content"><script type="text/rocketscript">(\w+)\("([^"]+)"\)</script></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) == 0:
        patron = '<div id="(tab\d+)" class="tab_content"><script>(\w+)\("([^"]+)"\)</script></div>'
        matches = re.compile(patron, re.DOTALL).findall(data)

    for check_tab, server, id in matches:
        scrapedplot = scrapertools.get_match(data, '<span class="clms">(.*?)</div></div>')
        plotformat = re.compile('(.*?:) </span>', re.DOTALL).findall(scrapedplot)
        scrapedplot = scrapedplot.replace(scrapedplot, bbcode_kodi2html("[COLOR white]" + scrapedplot + "[/COLOR]"))

        for plot in plotformat:
            scrapedplot = scrapedplot.replace(plot, bbcode_kodi2html("[COLOR red][B]" + plot + "[/B][/COLOR]"))
        scrapedplot = scrapedplot.replace("</span>", "[CR]")
        scrapedplot = scrapedplot.replace(":", "")
        if check_tab in str(check):
            idioma, calidad = scrapertools.find_single_match(str(check), "" + check_tab + "', '(.*?)', '(.*?)'")

            servers_data_list.append([server, id, idioma, calidad])

    url = "http://www.peliculasdk.com/Js/videod.js"
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    data = data.replace('<iframe width="100%" height="400" scrolling="no" frameborder="0"', '')

    patron = 'function (\w+)\(id\).*?'
    patron += 'data-src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for server, url in matches:

        for enlace, id, idioma, calidad in servers_data_list:

            if server == enlace:

                video_url = re.sub(r"embed\-|\-.*?x.*?\.html|u\'|\'\(", "", str(url))
                video_url = re.sub(r"'\+codigo\+'", "", video_url)
                video_url = video_url.replace('embed//', 'embed/')
                video_url = video_url + id
                if "goo.gl" in video_url:
                    try:
                        from unshortenit import unshorten
                        url = unshorten(video_url)
                        video_url = scrapertools.get_match(str(url), "u'([^']+)'")
                    except:
                        continue

                servertitle = scrapertools.get_match(video_url, 'http.*?://(.*?)/')
                servertitle = servertitle.replace(servertitle,
                                                  bbcode_kodi2html("[COLOR red]" + servertitle + "[/COLOR]"))
                servertitle = servertitle.replace("embed.", "")
                servertitle = servertitle.replace("player.", "")
                servertitle = servertitle.replace("api.video.", "")
                servertitle = re.sub(r"hqq.tv|hqq.watch", "netu.tv", servertitle)
                servertitle = servertitle.replace("anonymouse.org", "netu.tv")
                title = bbcode_kodi2html("[COLOR orange]Ver en --[/COLOR]") + servertitle + " " + idioma + " " + calidad
                itemlist.append(
                    Item(channel=item.channel, title=title, url=video_url, action="play", thumbnail=item.category,
                         plot=scrapedplot, fanart=item.show))
    if item.library and config.get_videolibrary_support() and len(itemlist) > 0:
        infoLabels = {'tmdb_id': item.infoLabels['tmdb_id'],
                      'title': item.fulltitle}
        itemlist.append(Item(channel=item.channel, title="Añadir esta película a la videoteca",
                             action="add_pelicula_to_library", url=item.url, infoLabels=infoLabels,
                             text_color="0xFFff6666",
                             thumbnail='http://imgur.com/0gyYvuC.png'))

    return itemlist


def play(item):
    logger.info()

    itemlist = servertools.find_video_items(data=item.url)
    data = scrapertools.cache_page(item.url)

    listavideos = servertools.findvideos(data)

    for video in listavideos:
        videotitle = scrapertools.unescape(video[0])
        url = item.url
        server = video[2]

        # xbmctools.addnewvideo( item.channel , "play" , category , server ,  , url , thumbnail , plot )
        itemlist.append(
            Item(channel=item.channel, action="play", server=server, title="Trailer - " + videotitle, url=url,
                 thumbnail=item.thumbnail, plot=item.plot, fulltitle=item.title,
                 fanart="http://s23.postimg.org/84vkeq863/movietrailers.jpg", folder=False))

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

    if not "serie" in item.url:
        url_plot = "http://api.themoviedb.org/3/movie/" + item.extra.split("|")[
            1] + "?api_key=2e2160006592024ba87ccdf78c28f49f&append_to_response=credits&language=es"
        data_plot = scrapertools.cache_page(url_plot)
        plot = scrapertools.find_single_match(data_plot, '"overview":"(.*?)",')
        tagline = scrapertools.find_single_match(data_plot, '"tagline":(".*?")')
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

    if "serie" in item.url:
        check2 = "serie"
        icon = "http://s6.postimg.org/hzcjag975/tvdb.png"
        foto = item.show.split("|")[1]
        if item.extra.split("|")[5] != "":
            critica = item.extra.split("|")[5]
        else:
            critica = "Esta serie no tiene críticas..."
        if not ".png" in item.extra.split("|")[0]:
            photo = "http://imgur.com/6uXGkrz.png"
        else:
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
            5] + "/recommendations?api_key=2e2160006592024ba87ccdf78c28f49f&language=es"
        data_tpi = scrapertools.cachePage(url_tpi)
        tpi = scrapertools.find_multiple_matches(data_tpi,
                                                 'id":(.*?),.*?"original_name":"(.*?)",.*?"poster_path":(.*?),')

    else:
        url_tpi = "http://api.themoviedb.org/3/movie/" + item.extra.split("|")[
            1] + "/recommendations?api_key=2e2160006592024ba87ccdf78c28f49f&language=es"
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
                           critica=critica, contentType=check2, thumb_busqueda="http://imgur.com/kdfWEJ6.png")
    from channels import infoplus
    infoplus.start(item_info, peliculas)


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
