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

api_key = "2e2160006592024ba87ccdf78c28f49f"
api_fankey = "dffe90fba4d02c199ae7a9e71330c987"

host = "http://www.txibitsoft.com/"


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(Item(channel=item.channel, title="[COLOR white][B]Peliculas[/B][/COLOR]", action="peliculas",
                         url="http://www.txibitsoft.com/torrents.php?procesar=1&categorias=%27Otras%20Peliculas%27&subcategoria=peliculas&pagina=1",
                         thumbnail="http://imgur.com/v6iC6Er.jpg", fanart="http://imgur.com/tJUbfeC.jpg"))
    itemlist.append(Item(channel=item.channel, title="[COLOR orange][B]Alta Calidad[/B][/COLOR]", action="", url="",
                         thumbnail="http://imgur.com/KXhvWIc.jpg", fanart="http://imgur.com/4kTqOKE.jpg"))

    itemlist.append(Item(channel=item.channel, title="         [COLOR white][B]1080[/B][/COLOR]", action="peliculas",
                         url="http://www.txibitsoft.com/torrents.php?procesar=1&categorias='Cine%20Alta%20Definicion%20HD'&subcategoria=1080p&pagina=1",
                         thumbnail="http://imgur.com/KXhvWIc.jpg", fanart="http://imgur.com/4kTqOKE.jpg"))
    itemlist.append(Item(channel=item.channel, title="         [COLOR white][B]720[/B][/COLOR]", action="peliculas",
                         url="http://www.txibitsoft.com/torrents.php?procesar=1&categorias=%27Peliculas%20x264%20MKV%27&pagina=1",
                         thumbnail="http://imgur.com/KXhvWIc.jpg", fanart="http://imgur.com/4kTqOKE.jpg"))
    itemlist.append(Item(channel=item.channel, title="          [COLOR white][B]4k[/B][/COLOR]", action="peliculas",
                         url="http://www.txibitsoft.com/torrents.php?procesar=1&categorias=%27Cine%20Alta%20Definicion%20HD%27&subcategoria=4KULTRAHD&pagina=1",
                         thumbnail="http://imgur.com/KXhvWIc.jpg", fanart="http://imgur.com/4kTqOKE.jpg"))
    title = "[COLOR white][B]Series[/B][/COLOR]"
    itemlist.append(
        Item(channel=item.channel, title="          [COLOR white][B]BdRemux[/B][/COLOR]", action="peliculas",
             url="http://www.txibitsoft.com/torrents.php?procesar=1&categorias=%27Cine%20Alta%20Definicion%20HD%27&subcategoria=BdRemux%201080p&pagina=1",
             thumbnail="http://imgur.com/KXhvWIc.jpg", fanart="http://imgur.com/4kTqOKE.jpg"))

    itemlist.append(
        Item(channel=item.channel, title="           [COLOR white][B]FullBluRay[/B][/COLOR]", action="peliculas",
             url="http://www.txibitsoft.com/torrents.php?procesar=1&categorias=%27Cine%20Alta%20Definicion%20HD%27&subcategoria=FULLBluRay&pagina=1",
             thumbnail="http://imgur.com/KXhvWIc.jpg", fanart="http://imgur.com/4kTqOKE.jpg"))

    itemlist.append(Item(channel=item.channel, title="[COLOR white][B]Series[/B][/COLOR]", action="peliculas",
                         url="http://www.txibitsoft.com/torrents.php?procesar=1&categorias='Series'&pagina=1",
                         thumbnail="http://imgur.com/qTqX9nU.jpg", fanart="http://imgur.com/rwjtkYj.jpg"))
    title = "[COLOR white][B]Buscar...[/B][/COLOR]"
    itemlist.append(
        Item(channel=item.channel, title=title, action="search", url="", fanart="http://imgur.com/wmkgcCC.jpg",
             thumbnail="http://imgur.com/b9xCys8.png"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")

    item.url = "http://www.txibitsoft.com/torrents.php?procesar=1&texto=%s" % (texto)
    item.extra = "1"
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
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|&amp;", "", data)
    item.url = re.sub(r"&amp;", "", item.url)
    # corrige la falta de imagen
    data = re.sub(r'<img src="<!doctype html><html xmlns="',
                  '</div><img src="http://s30.postimg.org/8n4ej5j0x/noimage.jpg" texto ><p>', data)

    # <div class="torrent-container-2 clearfix"><img class="torrent-image" src="uploads/torrents/images/thumbnails2/4441_step--up--all--in----blurayrip.jpg" alt="Imagen de Presentaci&oacute;n" /><div class="torrent-info"><h4><a href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Step Up All In MicroHD 1080p AC3 5.1-Castellano-AC3 5.1 Ingles Subs</a> </h4><p>19-12-2014</p><p>Subido por: <strong>TorrentEstrenos</strong> en <a href="/ver_torrents_41-id_en_peliculas_microhd.html" title="Peliculas MICROHD">Peliculas MICROHD</a><br />Descargas <strong><a href="#" style="cursor:default">46</a></strong></p><a class="btn-download" href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Descargar</a></div></div>

    patron = '<dl class=".*?dosColumnasDobles"><dt>'
    patron += '<a href="([^"]+)" '
    patron += 'title.*?:([^<]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'Idioma: <span class="categoria">([^<]+).*?'
    patron += 'Tama&ntilde;o: <span class="categoria">([^<]+)'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedlenguage, scrapedsize in matches:
        title_fan = re.sub(r"\[.*?\]|\(.*?\)|\d+x\d+.*?Final|\d\d\d\d|-\d+|-|\d+x\d+|Temporada.*?Completa| ;", "",
                           scrapedtitle)
        scrapedurl = "http://www.txibitsoft.com" + scrapedurl
        scrapedlenguage = scrapedlenguage.replace(scrapedlenguage, "[COLOR blue]" + scrapedlenguage + "[/COLOR]")
        scrapedsize = scrapedsize.replace(scrapedsize, "[COLOR gold]" + scrapedsize + "[/COLOR]")
        scrapedtitle = scrapedtitle.replace(scrapedtitle, "[COLOR white]" + scrapedtitle + "[/COLOR]")
        scrapedtitle = scrapedtitle + "-(Idioma:" + scrapedlenguage + ")" + "-(Tamaño: " + scrapedsize + ")"

        itemlist.append(
            Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action="fanart", thumbnail=scrapedthumbnail,
                 fanart="http://s21.postimg.org/w0lgvyud3/tbfanartgeneral2.jpg", extra=title_fan, folder=True))
    # Paginacion

    try:
        next_page = scrapertools.find_single_match(data, '<ul class="paginacion">.*?href=".*?>(\d)')
        if float(next_page) > float(item.extra):
            if next_page:
                url = item.url + "&pagina=" + next_page
                title = "siguiente>>"
                title = title.replace(title, "[COLOR orange]" + title + "[/COLOR]")
                extra = next_page
                itemlist.append(Item(channel=item.channel, action="buscador", title=title, url=url,
                                     thumbnail="http://s18.postimg.org/4l9172cqx/tbsiguiente.png",
                                     fanart="http://s21.postimg.org/w0lgvyud3/tbfanartgeneral2.jpg", extra=extra,
                                     folder=True))
    except:
        pass
    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []

    # Descar<div id="catalogheader">ga la página
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|&amp;|</span>|</li>|<li>", "", data)
    item.url = re.sub(r"&amp;", "", item.url)
    # corrige la falta de imagen
    data = re.sub(r'<img src="<!doctype html><html xmlns="',
                  '</div><img src="http://s30.postimg.org/8n4ej5j0x/noimage.jpg" texto ><p>', data)

    # <div class="torrent-container-2 clearfix"><img class="torrent-image" src="uploads/torrents/images/thumbnails2/4441_step--up--all--in----blurayrip.jpg" alt="Imagen de Presentaci&oacute;n" /><div class="torrent-info"><h4><a href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Step Up All In MicroHD 1080p AC3 5.1-Castellano-AC3 5.1 Ingles Subs</a> </h4><p>19-12-2014</p><p>Subido por: <strong>TorrentEstrenos</strong> en <a href="/ver_torrents_41-id_en_peliculas_microhd.html" title="Peliculas MICROHD">Peliculas MICROHD</a><br />Descargas <strong><a href="#" style="cursor:default">46</a></strong></p><a class="btn-download" href ="/descargar_torrent_27233-id_step_up_all_in_microhd_1080p_ac3_5.1--castellano--ac3_5.1_ingles_subs.html">Descargar</a></div></div>

    patron = '<dl class=".*?dosColumnasDobles"><dt>'
    patron += '<a href="([^"]+)" '
    patron += 'title.*?:([^<]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'Idioma: <span class="categoria">(.*?)'
    patron += 'Tama&ntilde;o: <span class="categoria">([^<]+)'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches) == 0:
        itemlist.append(Item(channel=item.channel,
                             title="[COLOR gold][B]El video ya no se encuentra en la web, prueba a encontrala por busqueda...[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/vhczf38ep/oops.png",
                             fanart="http://s12.postimg.org/59o1c792l/oopstxibi.jpg", folder=False))

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedlenguage, scrapedsize in matches:
        title_fan = re.sub(r"\[.*?\]|\(.*?\)|\d+x\d+.*?Final|\d\d\d\d|-\d+|-|\d+x\d+|Temporada.*?Completa| ;", "",
                           scrapedtitle)
        scrapedurl = "http://www.txibitsoft.com" + scrapedurl
        scrapedlenguage = scrapedlenguage.replace(scrapedlenguage, "[COLOR blue]" + scrapedlenguage + "[/COLOR]")
        scrapedsize = scrapedsize.replace(scrapedsize, "[COLOR gold]" + scrapedsize + "[/COLOR]")
        scrapedtitle = scrapedtitle.replace(scrapedtitle, "[COLOR white]" + scrapedtitle + "[/COLOR]")
        scrapedtitle = scrapedtitle + "-(Idioma:" + scrapedlenguage + ")" + "-(Tamaño: " + scrapedsize + ")"

        itemlist.append(
            Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action="fanart", thumbnail=scrapedthumbnail,
                 extra=title_fan, fanart="http://s21.postimg.org/w0lgvyud3/tbfanartgeneral2.jpg",
                 fulltitle=scrapedtitle, folder=True))

    # Extrae el paginador
    ## Paginación

    if "pagina=" in item.url:
        current_page_number = int(scrapertools.get_match(item.url, 'pagina=(\d+)'))
        item.url = re.sub(r"pagina=\d+", "pagina={0}", item.url)
    else:
        current_page_number = 1

    next_page_number = current_page_number + 1
    next_page = item.url.format(next_page_number)

    title = "siguiente>>"
    title = title.replace(title, "[COLOR orange]" + title + "[/COLOR]")
    itemlist.append(Item(channel=item.channel, action="peliculas", title=title, url=next_page,
                         thumbnail="http://s18.postimg.org/4l9172cqx/tbsiguiente.png",
                         fanart="http://s21.postimg.org/w0lgvyud3/tbfanartgeneral2.jpg", folder=True))

    return itemlist


def fanart(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    title_fan = item.extra
    title = re.sub(
        r'Serie Completa|Temporada.*?\d+|Fin Temporada|3D|SBS|Montaje del Director|V.Extendida|Quadrilogia|E.Coleccionista',
        '', title_fan)
    title = title.replace(' ', '%20')
    title = ''.join((c for c in unicodedata.normalize('NFD', unicode(title.decode('utf-8'))) if
                     unicodedata.category(c) != 'Mn')).encode("ascii", "ignore")

    try:
        sinopsis_area = scrapertools.get_match(data, '<textarea.*?">(.*?)</textarea></li>')
        if "Sinopsis" in sinopsis_area:
            sinopsis = scrapertools.get_match(data, '<textarea.*Sinopsis(.*?)</textarea></li>')
        elif "SINOPSIS" in sinopsis_area:
            sinopsis = scrapertools.get_match(data, '<textarea.*SINOPSIS(.*?)</textarea></li>')
        elif "Sinópsis" in sinopsis_area:
            sinopsis = scrapertools.get_match(data, '<textarea.*Sinópsis(.*?)</textarea></li>')
        elif "REPARTO" in sinopsis_area:
            sinopsis = scrapertools.get_match(data, '<textarea.*REPARTO(.*?)</textarea></li>')
        else:
            sinopsis = ""

    except:

        sinopsis = ""

    if not "series" in item.url:

        if "Estreno" in sinopsis_area:
            year = scrapertools.find_single_match(data, 'Estreno.*?\d+\/\d+\/(\d+)')
        else:
            year = scrapertools.find_single_match(data, '<textarea.*?A.*?(\d+)')
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
                show = "http://imgur.com/21Oty9A.jpg" + "|" + "" + "|" + sinopsis
                posterdb = item.thumbnail
                fanart_info = "http://imgur.com/21Oty9A.jpg"
                fanart_3 = ""
                fanart_2 = "http://imgur.com/21Oty9A.jpg"
                category = item.thumbnail
                id_scraper = ""

                itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                     thumbnail=item.thumbnail, fanart="http://imgur.com/21Oty9A.jpg", extra=extra,
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
                fanart = "http://imgur.com/21Oty9A.jpg"
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
                if fanart == "http://imgur.com/21Oty9A.jpg":
                    fanart = fanart_info
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

        if sinopsis == "":
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
                                                             '"tv_results":.*?"id":(.*?),.*?"poster_path":(.*?),"popularity"')

                if len(matches) == 0:
                    id_tmdb = ""
                    fanart_3 = ""
                    extra = item.thumbnail + "|" + year + "|" + "no data" + "|" + "no data" + "|" + rating_filma + "|" + critica + "|" + "" + "|" + id_tmdb
                    show = "http://imgur.com/21Oty9A.jpg" + "|" + fanart_3 + "|" + sinopsis + "|" + title_fan + "|" + item.thumbnail + "|" + id_tmdb
                    fanart_info = "http://imgur.com/21Oty9A.jpg"
                    fanart_2 = "http://imgur.com/21Oty9A.jpg"
                    id_scraper = " " + "|" + "serie" + "|" + rating_filma + "|" + critica + "|" + " "
                    category = ""
                    posterdb = item.thumbnail
                    itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                         thumbnail=item.thumbnail, fanart="http://imgur.com/21Oty9A.jpg", extra=extra,
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
            posterdb = scrapertools.find_single_match(data_tmdb, '"poster_path":(.*?)","popularity"')

            if "null" in posterdb:
                posterdb = item.thumbnail
            else:
                posterdb = re.sub(r'\\|"', '', posterdb)
                posterdb = "https://image.tmdb.org/t/p/original" + posterdb
            if "null" in fan:
                fanart = "http://imgur.com/21Oty9A.jpg"
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
                if fanart == "http://imgur.com/21Oty9A.jpg":
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

    title_info = "[COLOR turquoise]Info[/COLOR]"
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


def findvideos(item):
    logger.info()
    itemlist = []

    if not "serie" in item.url:
        thumbnail = item.category
    else:
        thumbnail = item.show.split("|")[4]
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<form name="frm" id="frm" method="get" action="torrent.php">.*?'
    patron += 'alt="([^<]+)".*?'
    patron += '<p class="limpiar centro"><a class="torrent" href="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        itemlist.append(Item(channel=item.channel,
                             title="[COLOR gold][B]El video ya no se encuentra en la web, prueba a encontrala por busqueda...[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/vhczf38ep/oops.png",
                             fanart="http://s12.postimg.org/59o1c792l/oopstxibi.jpg", folder=False))

    for scrapedtitle, scrapedurl in matches:

        if "x" in scrapedtitle:
            patron = '<form name="frm" id="frm" method="get" action="torrent.php">.*?alt=".*?(\d+)x(\d+)'
            matches = re.compile(patron, re.DOTALL).findall(data)
            for temp, epi in matches:
                plot = temp + "|" + epi

        if "Temporada" in scrapedtitle:
            patron = '<form name="frm" id="frm" method="get" action="torrent.php">.*?alt=".*?Temporada (\d+).*?\[Cap.\d(\d+)'
            matches = re.compile(patron, re.DOTALL).findall(data)
            for temp, epi in matches:
                epi = re.sub(r"101|201|301|401|501|601|701|801|901", "01", epi)
                epi = re.sub(r"102|202|302|402|502|602|702|802|902", "02", epi)
                epi = re.sub(r"103|203|303|403|503|603|703|803|903", "03", epi)
                epi = re.sub(r"104|204|304|404|504|604|704|804|904", "04", epi)
                epi = re.sub(r"105|205|305|405|505|605|705|805|905", "05", epi)
                epi = re.sub(r"106|206|306|406|506|606|706|806|906", "06", epi)
                epi = re.sub(r"107|207|307|407|507|607|707|807|907", "07", epi)
                epi = re.sub(r"108|208|308|408|508|608|708|808|908", "08", epi)
                epi = re.sub(r"109|209|309|409|509|609|709|809|909", "09", epi)
                epi = re.sub(r"110|210|310|410|510|610|710|810|910", "10", epi)
                epi = re.sub(r"111|211|311|411|511|611|711|811|911", "11", epi)
                epi = re.sub(r"112|212|312|412|512|612|712|812|912", "12", epi)
                epi = re.sub(r"113|213|313|413|513|613|713|813|913", "13", epi)
                epi = re.sub(r"114|214|314|414|514|614|714|814|914", "14", epi)
                epi = re.sub(r"115|215|315|415|515|615|715|815|915", "15", epi)
                epi = re.sub(r"116|216|316|416|516|616|716|816|916", "16", epi)
                epi = re.sub(r"117|217|317|417|517|617|717|817|917", "17", epi)
                epi = re.sub(r"118|218|318|418|518|618|718|818|918", "18", epi)
                epi = re.sub(r"119|219|319|419|519|619|719|819|919", "19", epi)
                epi = re.sub(r"120|220|320|420|520|620|720|820|920", "20", epi)
                epi = re.sub(r"121|221|321|421|521|621|721|821|921", "21", epi)
                epi = re.sub(r"122|222|322|422|522|622|722|822|922", "22", epi)
                epi = re.sub(r"123|223|323|423|523|623|723|823|923", "23", epi)
                epi = re.sub(r"124|224|324|424|524|624|724|824|924", "24", epi)
                epi = re.sub(r"125|225|325|425|525|625|725|825|925", "25", epi)
                epi = re.sub(r"126|226|326|426|526|626|726|826|926", "26", epi)
                epi = re.sub(r"127|227|327|427|527|627|727|827|927", "27", epi)
                epi = re.sub(r"128|228|328|428|528|628|728|828|928", "28", epi)
                epi = re.sub(r"129|229|329|429|529|629|729|829|929", "29", epi)
                epi = re.sub(r"130|230|330|430|530|630|730|830|930", "30", epi)
                plot = temp + "|" + epi

        if "series" in item.url:

            try:
                # buscamos peso y formato
                url = host + scrapedurl

                torrents_path = config.get_videolibrary_path() + '/torrents'

                if not os.path.exists(torrents_path):
                    os.mkdir(torrents_path)
                # En algunos OS esta dando extraños problemas de certificado.Workaround
                import ssl

                ssl._create_default_https_context = ssl._create_unverified_context
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
                    size = sizet
                    ext_v = re.sub(r"-.*? bytes|.*?\[.*?\].|'|.*?COM.|.*?\.es.|.*?\[.*?\]|.*?\(.*?\)\.|.*?\.", "", name)
                    try:
                        os.remove(torrents_path + "/temp.torrent")
                    except:
                        pass
            except:
                size = "en estos momentos..."
                ext_v = "no disponible"
            if "rar" in ext_v:
                ext_v = ext_v + " -- No reproducible"
                size = ""
            scrapedurl = "http://www.txibitsoft.com" + scrapedurl
            title_tag = "[COLOR orange]Ver--[/COLOR]"
            scrapedtitle = "[COLOR magenta][B] capìtulo" + " " + temp + "x" + epi + "[/B][/COLOR]"
            scrapedtitle = title_tag + scrapedtitle + " " + "[COLOR mediumslateblue]( Video [/COLOR]" + "[COLOR mediumpurple]" + ext_v + " -- " + size + " )[/COLOR]"
            itemlist.append(
                Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action="play", server="torrent",
                     thumbnail=thumbnail, category=item.category, fanart=item.show.split("|")[0], folder=False))
            ###thumb temporada###
            url = "http://api.themoviedb.org/3/tv/" + item.show.split("|")[
                5] + "/season/" + temp + "/images?api_key=" + api_key
            data = httptools.downloadpage(url).data
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            patron = '{"id".*?"file_path":"(.*?)","height"'
            matches = re.compile(patron, re.DOTALL).findall(data)
            if len(matches) == 0:
                thumbnail = item.thumbnail
            for thumtemp in matches:
                print "@@@@@" + thumtemp
                thumbnail = "https://image.tmdb.org/t/p/original" + thumtemp

            extra = item.extra + "|" + temp + "|" + epi
            title = "Info"
            title = title.replace(title, "[COLOR skyblue]" + title + "[/COLOR]")
            itemlist.append(
                Item(channel=item.channel, action="info_capitulos", title=title, url=item.url, thumbnail=thumbnail,
                     fanart=item.show.split("|")[1], show=item.show, extra=extra, folder=False))

        else:
            try:
                # buscamos peso y formato
                url = "http://www.txibitsoft.com" + scrapedurl

                torrents_path = config.get_videolibrary_path() + '/torrents'

                if not os.path.exists(torrents_path):
                    os.mkdir(torrents_path)

                import ssl

                ssl._create_default_https_context = ssl._create_unverified_context
                urllib.urlretrieve("http://ssl-proxy.my-addr.org/myaddrproxy.php/" + url,
                                   torrents_path + "/temp.torrent")
                pepe = open(torrents_path + "/temp.torrent", "rb").read()

                if "used CloudFlare" in pepe:
                    try:
                        urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'
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
                    size = sizet
                    ext_v = re.sub(r"-.*? bytes|.*?\[.*?\].|'|.*?COM.|.*?\.es.|.*?\[.*?\]|.*?\(.*?\)\.|.*?\.", "", name)
                    try:
                        os.remove(torrents_path + "/temp.torrent")
                    except:
                        pass
            except:
                size = "en estos momentos..."
                ext_v = "no disponible"
            if "rar" in ext_v:
                ext_v = ext_v + " -- No reproducible"
                size = ""
            scrapedurl = "http://www.txibitsoft.com" + scrapedurl
            title_tag = "[COLOR orange]Ver--[/COLOR]"
            scrapedtitle = re.sub(r"\[.*?\]|\(.*?\)|\d+x\d+.*?Final|-\d+|-|\d+x\d+|Temporada.*?Completa| ;", "",
                                  scrapedtitle)
            scrapedtitle = "[COLOR magenta][B]" + scrapedtitle + "[/B][/COLOR]"
            scrapedtitle = title_tag + scrapedtitle + " " + "[COLOR mediumslateblue]( Video [/COLOR]" + "[COLOR mediumpurple]" + ext_v + " -- " + size + " )[/COLOR]"
            itemlist.append(
                Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action="play", server="torrent",
                     thumbnail=item.extra, fanart=item.show, folder=False))

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
        if foto == item.thumbnail:
            foto = ""

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
                                                 'id":(.*?),.*?"original_name":"(.*?)",.*?"poster_path":(.*?),"popularity"')

    else:
        url_tpi = "http://api.themoviedb.org/3/movie/" + item.extra.split("|")[
            1] + "/recommendations?api_key=" + api_key + "&language=es"
        data_tpi = scrapertools.cachePage(url_tpi)
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
                           critica=critica, contentType=check2, thumb_busqueda="http://imgur.com/jProvTt.png")
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
                    foto = "http://imgur.com/PXJEqBn.png"
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
                foto = "http://imgur.com/PXJEqBn.png"
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

        self.background = xbmcgui.ControlImage(70, 20, 1150, 630, 'http://imgur.com/H2hMPTP.jpg')
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
