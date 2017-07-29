# -*- coding: utf-8 -*-

import os
import re
import unicodedata
import urllib

from core import config
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item

host = "http://tv-vip.com"
headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0'],
           ['Accept', 'application/json, text/javascript, */*; q=0.01'],
           ['Accept-Language', 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Connection', 'keep-alive'],
           ['DNT', '1'],
           ['Referer', 'http://tv-vip.com']]

header_string = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0" \
                "&Referer=http://tv-vip.com&Cookie="


def mainlist(item):
    logger.info()
    item.viewmode = "movie"
    itemlist = []

    data = scrapertools.anti_cloudflare("http://tv-vip.com/json/playlist/home/index.json", host=host, headers=headers)

    head = header_string + get_cookie_value()
    itemlist.append(Item(channel=item.channel, title="Películas", action="submenu",
                         thumbnail="http://tv-vip.com/json/playlist/peliculas/thumbnail.jpg" + head,
                         fanart="http://tv-vip.com/json/playlist/peliculas/background.jpg" + head, viewmode="movie"))
    itemlist.append(Item(channel=item.channel, title="Series", action="submenu",
                         thumbnail="http://tv-vip.com/json/playlist/series/poster.jpg" + head,
                         fanart="http://tv-vip.com/json/playlist/series/background.jpg" + head, viewmode="movie"))
    itemlist.append(Item(channel=item.channel, title="Versión Original", action="entradasconlistas",
                         url="http://tv-vip.com/json/playlist/version-original/index.json",
                         thumbnail="http://tv-vip.com/json/playlist/version-original/thumbnail.jpg" + head,
                         fanart="http://tv-vip.com/json/playlist/version-original/background.jpg" + head,
                         viewmode="movie_with_plot"))
    itemlist.append(Item(channel=item.channel, title="Documentales", action="entradasconlistas",
                         url="http://tv-vip.com/json/playlist/documentales/index.json",
                         thumbnail="http://tv-vip.com/json/playlist/documentales/thumbnail.jpg" + head,
                         fanart="http://tv-vip.com/json/playlist/documentales/background.jpg" + head,
                         viewmode="movie_with_plot"))
    itemlist.append(Item(channel=item.channel, title="Películas Infantiles", action="entradasconlistas",
                         url="http://tv-vip.com/json/playlist/peliculas-infantiles/index.json",
                         thumbnail="http://tv-vip.com/json/playlist/peliculas-infantiles/thumbnail.jpg" + head,
                         fanart="http://tv-vip.com/json/playlist/peliculas-infantiles/background.jpg" + head,
                         viewmode="movie_with_plot"))
    itemlist.append(Item(channel=item.channel, title="Series Infantiles", action="entradasconlistas",
                         url="http://tv-vip.com/json/playlist/series-infantiles/index.json",
                         thumbnail="http://tv-vip.com/json/playlist/series-infantiles/thumbnail.jpg" + head,
                         fanart="http://tv-vip.com/json/playlist/series-infantiles/background.jpg" + head,
                         viewmode="movie_with_plot"))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search",
                         thumbnail="http://i.imgur.com/gNHVlI4.png", fanart="http://i.imgur.com/9loVksV.png"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    if item.title == "Buscar...": item.extra = "local"
    item.url = "http://tv-vip.com/video-prod/s/search?q=%s&n=100" % texto

    try:
        return busqueda(item, texto)
        # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def busqueda(item, texto):
    logger.info()
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, host=host, headers=headers)
    data = jsontools.load(data)
    head = header_string + get_cookie_value()
    for child in data["objectList"]:
        infolabels = {}

        infolabels['year'] = child['year']
        if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',', '.')
        infolabels['votes'] = child['rateCount']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']

        if 'playListChilds' not in child:
            infolabels['plot'] = child['description']
            type = "repo"
            fulltitle = unicodedata.normalize('NFD', unicode(child['name'], 'utf-8')) \
                .encode('ASCII', 'ignore').decode("utf-8")
            title = child['name']
            infolabels['duration'] = child['duration']
            if child['height'] < 720:
                quality = "[B]  [SD][/B]"
            elif child['height'] < 1080:
                quality = "[B]  [720p][/B]"
            elif child['height'] >= 1080:
                quality = "[B]  [1080p][/B]"
            if child['name'] == "":
                title = child['id'].rsplit(".", 1)[0]
            else:
                title = child['name']
            if child['year']:
                title += " (" + child['year'] + ")"
            title += quality
        else:
            type = "playlist"
            infolabels['plot'] = "Contiene:\n" + "\n".join(child['playListChilds']) + "\n".join(child['repoChilds'])
            fulltitle = child['id']
            title = "[COLOR red][LISTA][/COLOR] " + child['id'].replace('-', ' ').capitalize() + " ([COLOR gold]" + \
                    str(child['number']) + "[/COLOR])"

        # En caso de búsqueda global se filtran los resultados
        if item.extra != "local":
            if "+" in texto: texto = "|".join(texto.split("+"))
            if not re.search(r'(?i)' + texto, title, flags=re.DOTALL): continue

        url = "http://tv-vip.com/json/%s/%s/index.json" % (type, child["id"])
        # Fanart
        if child['hashBackground']:
            fanart = "http://tv-vip.com/json/%s/%s/background.jpg" % (type, child["id"])
        else:
            fanart = "http://tv-vip.com/json/%s/%s/thumbnail.jpg" % (type, child["id"])
        # Thumbnail
        if child['hasPoster']:
            thumbnail = "http://tv-vip.com/json/%s/%s/poster.jpg" % (type, child["id"])
        else:
            thumbnail = fanart
        thumbnail += head
        fanart += head

        if type == 'playlist':
            itemlist.insert(0, Item(channel=item.channel, action="entradasconlistas", title=bbcode_kodi2html(title),
                                    url=url, thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle,
                                    infoLabels=infolabels, viewmode="movie_with_plot", folder=True))
        else:
            itemlist.append(Item(channel=item.channel, action="findvideos", title=bbcode_kodi2html(title), url=url,
                                 thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, contentTitle=fulltitle,
                                 context="05", infoLabels=infolabels, viewmode="movie_with_plot", folder=True))

    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    data = scrapertools.anti_cloudflare("http://tv-vip.com/json/playlist/home/index.json", host=host, headers=headers)
    head = header_string + get_cookie_value()
    if item.title == "Series":
        itemlist.append(Item(channel=item.channel, title="Nuevos Capítulos", action="episodios",
                             url="http://tv-vip.com/json/playlist/nuevos-capitulos/index.json",
                             thumbnail="http://tv-vip.com/json/playlist/nuevos-capitulos/background.jpg" + head,
                             fanart="http://tv-vip.com/json/playlist/nuevos-capitulos/background.jpg" + head,
                             viewmode="movie"))
        itemlist.append(Item(channel=item.channel, title="Más Vistas", action="series",
                             url="http://tv-vip.com/json/playlist/top-series/index.json",
                             thumbnail="http://tv-vip.com/json/playlist/top-series/thumbnail.jpg" + head,
                             fanart="http://tv-vip.com/json/playlist/top-series/background.jpg" + head,
                             contentTitle="Series", viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, title="Últimas Series", action="series",
                             url="http://tv-vip.com/json/playlist/series/index.json",
                             thumbnail=item.thumbnail, fanart=item.fanart, contentTitle="Series",
                             viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, title="Lista de Series A-Z", action="series",
                             url="http://tv-vip.com/json/playlist/series/index.json", thumbnail=item.thumbnail,
                             fanart=item.fanart, contentTitle="Series", viewmode="movie_with_plot"))
    else:
        itemlist.append(Item(channel=item.channel, title="Novedades", action="entradas",
                             url="http://tv-vip.com/json/playlist/000-novedades/index.json",
                             thumbnail="http://tv-vip.com/json/playlist/ultimas-peliculas/thumbnail.jpg" + head,
                             fanart="http://tv-vip.com/json/playlist/ultimas-peliculas/background.jpg" + head,
                             viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, title="Más vistas", action="entradas",
                             url="http://tv-vip.com/json/playlist/peliculas-mas-vistas/index.json",
                             thumbnail="http://tv-vip.com/json/playlist/peliculas-mas-vistas/thumbnail.jpg" + head,
                             fanart="http://tv-vip.com/json/playlist/peliculas-mas-vistas/background.jpg" + head,
                             viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, title="Categorías", action="cat",
                             url="http://tv-vip.com/json/playlist/peliculas/index.json",
                             thumbnail=item.thumbnail, fanart=item.fanart))
        itemlist.append(Item(channel=item.channel, title="Películas 3D", action="entradasconlistas",
                             url="http://tv-vip.com/json/playlist/3D/index.json",
                             thumbnail="http://tv-vip.com/json/playlist/3D/thumbnail.jpg" + head,
                             fanart="http://tv-vip.com/json/playlist/3D/background.jpg" + head,
                             viewmode="movie_with_plot"))
    return itemlist


def cat(item):
    logger.info()
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, host=host, headers=headers)
    data = jsontools.load(data)
    head = header_string + get_cookie_value()
    exception = ["peliculas-mas-vistas", "ultimas-peliculas"]
    for child in data["sortedPlaylistChilds"]:
        if child["id"] not in exception:
            url = "http://tv-vip.com/json/playlist/%s/index.json" % child["id"]
            # Fanart
            if child['hashBackground']:
                fanart = "http://tv-vip.com/json/playlist/%s/background.jpg" % child["id"]
            else:
                fanart = "http://tv-vip.com/json/playlist/%s/thumbnail.jpg" % child["id"]
            # Thumbnail
            thumbnail = "http://tv-vip.com/json/playlist/%s/thumbnail.jpg" % child["id"]
            thumbnail += head
            fanart += head
            title = child['id'].replace('-', ' ').capitalize().replace("Manga", "Animación/Cine Oriental")
            title += " ([COLOR gold]" + str(child['number']) + "[/COLOR])"
            itemlist.append(
                Item(channel=item.channel, action="entradasconlistas", title=bbcode_kodi2html(title), url=url,
                     thumbnail=thumbnail, fanart=fanart, folder=True))

    return itemlist


def entradas(item):
    logger.info()
    itemlist = []
    if item.title == "Nuevos Capítulos":
        context = "5"
    else:
        context = "05"
    data = scrapertools.anti_cloudflare(item.url, host=host, headers=headers)
    data = jsontools.load(data)
    head = header_string + get_cookie_value()
    for child in data["sortedRepoChilds"]:
        infolabels = {}

        infolabels['plot'] = child['description']
        infolabels['year'] = child['year']
        if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',', '.')
        infolabels['votes'] = child['rateCount']
        infolabels['duration'] = child['duration']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']
        url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
        # Fanart
        if child['hashBackground']:
            fanart = "http://tv-vip.com/json/repo/%s/background.jpg" % child["id"]
        else:
            fanart = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child["id"]
        # Thumbnail
        if child['hasPoster']:
            thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child["id"]
        else:
            thumbnail = fanart
        thumbnail += head
        fanart += head

        if child['height'] < 720:
            quality = "[B]  [SD][/B]"
        elif child['height'] < 1080:
            quality = "[B]  [720p][/B]"
        elif child['height'] >= 1080:
            quality = "[B]  [1080p][/B]"
        fulltitle = unicodedata.normalize('NFD', unicode(child['name'], 'utf-8')).encode('ASCII', 'ignore') \
            .decode("utf-8")
        if child['name'] == "":
            title = child['id'].rsplit(".", 1)[0]
        else:
            title = child['name']
        if child['year']:
            title += " (" + child['year'] + ")"
        title += quality

        itemlist.append(Item(channel=item.channel, action="findvideos", server="", title=title, url=url,
                             thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, infoLabels=infolabels,
                             contentTitle=fulltitle, context=context))

    return itemlist


def entradasconlistas(item):
    logger.info()
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, host=host, headers=headers)
    data = jsontools.load(data)
    head = header_string + get_cookie_value()
    # Si hay alguna lista
    contentSerie = False
    contentList = False
    if data['playListChilds']:
        itemlist.append(Item(channel=item.channel, title="**LISTAS**", action="", text_color="red", text_bold=True,
                             folder=False))
        for child in data['sortedPlaylistChilds']:
            infolabels = {}

            infolabels['plot'] = "Contiene:\n" + "\n".join(child['playListChilds']) + "\n".join(child['repoChilds'])
            if child['seasonNumber'] and not contentList and re.search(r'(?i)temporada', child['id']):
                infolabels['season'] = child['seasonNumber']
                contentSerie = True
            else:
                contentSerie = False
                contentList = True
            title = child['id'].replace('-', ' ').capitalize() + " ([COLOR gold]" + str(child['number']) + "[/COLOR])"
            url = "http://tv-vip.com/json/playlist/%s/index.json" % child["id"]
            thumbnail = "http://tv-vip.com/json/playlist/%s/thumbnail.jpg" % child["id"]
            if child['hashBackground']:
                fanart = "http://tv-vip.com/json/playlist/%s/background.jpg" % child["id"]
            else:
                fanart = "http://tv-vip.com/json/playlist/%s/thumbnail.jpg" % child["id"]

            thumbnail += head
            fanart += head
            itemlist.append(Item(channel=item.channel, action="entradasconlistas", title=bbcode_kodi2html(title),
                                 url=url, thumbnail=thumbnail, fanart=fanart, fulltitle=child['id'],
                                 infoLabels=infolabels, viewmode="movie_with_plot"))
    else:
        contentList = True
    if data["sortedRepoChilds"] and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="**VÍDEOS**", action="", text_color="blue", text_bold=True,
                             folder=False))

    for child in data["sortedRepoChilds"]:
        infolabels = {}

        infolabels['plot'] = child['description']
        infolabels['year'] = data['year']
        if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',', '.')
        infolabels['votes'] = child['rateCount']
        infolabels['duration'] = child['duration']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']
        url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
        # Fanart
        if child['hashBackground']:
            fanart = "http://tv-vip.com/json/repo/%s/background.jpg" % child["id"]
        else:
            fanart = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child["id"]
        # Thumbnail
        if child['hasPoster']:
            thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child["id"]
        else:
            thumbnail = fanart
        thumbnail += head
        fanart += head
        if child['height'] < 720:
            quality = "[B]  [SD][/B]"
        elif child['height'] < 1080:
            quality = "[B]  [720p][/B]"
        elif child['height'] >= 1080:
            quality = "[B]  [1080p][/B]"
        fulltitle = unicodedata.normalize('NFD', unicode(child['name'], 'utf-8')).encode('ASCII', 'ignore') \
            .decode("utf-8")
        if child['name'] == "":
            title = child['id'].rsplit(".", 1)[0]
        else:
            title = child['name']
        if child['year']:
            title += " (" + child['year'] + ")"
        title += quality

        itemlist.append(Item(channel=item.channel, action="findvideos", title=bbcode_kodi2html(title), url=url,
                             thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, infoLabels=infolabels,
                             contentTitle=fulltitle, context="05", viewmode="movie_with_plot", folder=True))

    # Se añade item para añadir la lista de vídeos a la videoteca
    if data['sortedRepoChilds'] and len(itemlist) > 0 and contentList:
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, text_color="green", title="Añadir esta lista a la videoteca",
                                 url=item.url, action="listas"))
    elif contentSerie:
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", url=item.url,
                                 action="series_library", fulltitle=data['name'], show=data['name'],
                                 text_color="green"))

    return itemlist


def series(item):
    logger.info()
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, host=host, headers=headers)
    data = jsontools.load(data)
    head = header_string + get_cookie_value()
    exception = ["top-series", "nuevos-capitulos"]
    for child in data["sortedPlaylistChilds"]:
        if child["id"] not in exception:
            infolabels = {}

            infolabels['plot'] = child['description']
            infolabels['year'] = child['year']
            if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
            infolabels['rating'] = child['rate'].replace(',', '.')
            infolabels['votes'] = child['rateCount']
            if child['cast']: infolabels['cast'] = child['cast'].split(",")
            infolabels['director'] = child['director']
            infolabels['mediatype'] = "episode"
            if child['seasonNumber']: infolabels['season'] = child['seasonNumber']
            url = "http://tv-vip.com/json/playlist/%s/index.json" % child["id"]
            # Fanart
            if child['hashBackground']:
                fanart = "http://tv-vip.com/json/playlist/%s/background.jpg" % child["id"]
            else:
                fanart = "http://tv-vip.com/json/playlist/%s/thumbnail.jpg" % child["id"]
            # Thumbnail
            if child['hasPoster']:
                thumbnail = "http://tv-vip.com/json/playlist/%s/poster.jpg" % child["id"]
            else:
                thumbnail = fanart
            thumbnail += head
            fanart += head

            if item.contentTitle == "Series":
                if child['name'] != "":
                    fulltitle = unicodedata.normalize('NFD', unicode(child['name'].split(" Temporada")[0], 'utf-8')) \
                        .encode('ASCII', 'ignore').decode("utf-8")
                    fulltitle = fulltitle.replace('-', '')
                    title = child['name'] + " (" + child['year'] + ")"
                else:
                    title = fulltitle = child['id'].capitalize()
                if "Temporada" not in title:
                    title += "     [Temporadas: [COLOR gold]" + str(child['numberOfSeasons']) + "[/COLOR]]"
                elif item.title == "Más Vistas":
                    title = title.replace("- Temporada", "--- Temporada")
            else:
                if data['name'] != "":
                    fulltitle = unicodedata.normalize('NFD', unicode(data['name'], 'utf-8')).encode('ASCII', 'ignore') \
                        .decode("utf-8")
                    if child['seasonNumber']:
                        title = data['name'] + " --- Temporada " + child['seasonNumber'] + \
                                "  [COLOR gold](" + str(child['number']) + ")[/COLOR]"
                    else:
                        title = child['name'] + "  [COLOR gold](" + str(child['number']) + ")[/COLOR]"
                else:
                    fulltitle = unicodedata.normalize('NFD', unicode(data['id'], 'utf-8')).encode('ASCII', 'ignore') \
                        .decode("utf-8")
                    if child['seasonNumber']:
                        title = data['id'].capitalize() + " --- Temporada " + child['seasonNumber'] + \
                                "  [COLOR gold](" + str(child['number']) + ")[/COLOR]"
                    else:
                        title = data['id'].capitalize() + "  [COLOR gold](" + str(child['number']) + ")[/COLOR]"
            if not child['playListChilds']:
                action = "episodios"
            else:
                action = "series"
            itemlist.append(Item(channel=item.channel, action=action, title=bbcode_kodi2html(title), url=url, server="",
                                 thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, infoLabels=infolabels,
                                 contentTitle=fulltitle, context="25", viewmode="movie_with_plot", folder=True))
            if len(itemlist) == len(data["sortedPlaylistChilds"]) and item.contentTitle != "Series":

                itemlist.sort(key=lambda item: item.title, reverse=True)
                if config.get_videolibrary_support():
                    itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", url=item.url,
                                         action="add_serie_to_library", show=data['name'],
                                         text_color="green", extra="series_library"))

    if item.title == "Últimas Series": return itemlist
    if item.title == "Lista de Series A-Z": itemlist.sort(key=lambda item: item.fulltitle)

    if data["sortedRepoChilds"] and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="**VÍDEOS RELACIONADOS/MISMA TEMÁTICA**", text_color="blue",
                             text_bold=True, action="", folder=False))
    for child in data["sortedRepoChilds"]:
        infolabels = {}

        if child['description']:
            infolabels['plot'] = data['description']
        else:
            infolabels['plot'] = child['description']
        infolabels['year'] = data['year']
        if not child['tags']:
            infolabels['genre'] = ', '.join([x.strip() for x in data['tags']])
        else:
            infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',', '.')
        infolabels['duration'] = child['duration']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']

        url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
        # Fanart
        if child['hashBackground']:
            fanart = "http://tv-vip.com/json/repo/%s/background.jpg" % child["id"]
        else:
            fanart = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child["id"]
        # Thumbnail
        if child['hasPoster']:
            thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child["id"]
        else:
            thumbnail = fanart
        thumbnail += head
        fanart += head

        if child['height'] < 720:
            quality = "[B]  [SD][/B]"
        elif child['height'] < 1080:
            quality = "[B]  [720p][/B]"
        elif child['height'] >= 1080:
            quality = "[B]  [1080p][/B]"
        fulltitle = unicodedata.normalize('NFD', unicode(child['name'], 'utf-8')).encode('ASCII', 'ignore') \
            .decode("utf-8")

        if child['name'] == "":
            title = child['id'].rsplit(".", 1)[0]
        else:
            title = child['name']
        if child['year']:
            title += " (" + child['year'] + ")"
        title += quality

        itemlist.append(Item(channel=item.channel, action="findvideos", title=bbcode_kodi2html(title), url=url,
                             server="", thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, infoLabels=infolabels,
                             contentTitle=fulltitle, context="25", viewmode="movie_with_plot", folder=True))
    if item.extra == "new":
        itemlist.sort(key=lambda item: item.title, reverse=True)

    return itemlist


def episodios(item):
    logger.info()
    logger.info("categoriaaa es " + item.tostring())
    itemlist = []
    # Redirección para actualización de videoteca
    if item.extra == "series_library":
        itemlist = series_library(item)
        return itemlist

    data = scrapertools.anti_cloudflare(item.url, host=host, headers=headers)
    data = jsontools.load(data)
    head = header_string + get_cookie_value()
    # Se prueba un método u otro porque algunas series no están bien listadas
    if data["sortedRepoChilds"]:
        for child in data["sortedRepoChilds"]:
            if item.infoLabels:
                item.infoLabels['duration'] = str(child['duration'])
                item.infoLabels['season'] = str(data['seasonNumber'])
                item.infoLabels['episode'] = str(child['episode'])
                item.infoLabels['mediatype'] = "episode"
            contentTitle = item.fulltitle + "|" + str(data['seasonNumber']) + "|" + str(child['episode'])
            # En caso de venir del apartado nuevos capítulos se redirige a la función series para mostrar los demás
            if item.title == "Nuevos Capítulos":
                url = "http://tv-vip.com/json/playlist/%s/index.json" % child["season"]
                action = "series"
                extra = "new"
            else:
                url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
                action = "findvideos"
                extra = ""
            if child['hasPoster']:
                thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child["id"]
            else:
                thumbnail = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child["id"]
            thumbnail += head
            try:
                title = fulltitle = child['name'].rsplit(" ", 1)[0] + " - " + child['name'].rsplit(" ", 1)[1]
            except:
                title = fulltitle = child['id']
            itemlist.append(item.clone(action=action, server="", title=title, url=url, thumbnail=thumbnail,
                                       fanart=item.fanart, fulltitle=fulltitle, contentTitle=contentTitle, context="35",
                                       viewmode="movie", extra=extra, show=item.fulltitle, folder=True))
    else:
        for child in data["repoChilds"]:
            url = "http://tv-vip.com/json/repo/%s/index.json" % child
            if data['hasPoster']:
                thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child
            else:
                thumbnail = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child
            thumbnail += head
            title = fulltitle = child.capitalize().replace('_', ' ')
            itemlist.append(item.clone(action="findvideos", server="", title=title, url=url, thumbnail=thumbnail,
                                       fanart=item.fanart, fulltitle=fulltitle, contentTitle=item.fulltitle,
                                       context="25", show=item.fulltitle, folder=True))

    # Opción de añadir a la videoteca en casos de series de una única temporada
    if len(itemlist) > 0 and not "---" in item.title and item.title != "Nuevos Capítulos":
        if config.get_videolibrary_support() and item.show == "":
            if "-" in item.title:
                show = item.title.split('-')[0]
            else:
                show = item.title.split('(')[0]
            itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", text_color="green",
                                 url=item.url, action="add_serie_to_library", show=show, extra="series_library"))
    return itemlist


def series_library(item):
    logger.info()
    # Funcion unicamente para añadir/actualizar series a la libreria
    lista_episodios = []
    show = item.show.strip()

    data_serie = scrapertools.anti_cloudflare(item.url, host=host, headers=headers)
    data_serie = jsontools.load(data_serie)
    # Para series que en la web se listan divididas por temporadas
    if data_serie["sortedPlaylistChilds"]:
        for season_name in data_serie["sortedPlaylistChilds"]:
            url_season = "http://tv-vip.com/json/playlist/%s/index.json" % season_name['id']
            data = scrapertools.anti_cloudflare(url_season, host=host, headers=headers)
            data = jsontools.load(data)

            if data["sortedRepoChilds"]:
                for child in data["sortedRepoChilds"]:
                    url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
                    fulltitle = child['name'].rsplit(" ", 1)[0] + " - " + child['name'].rsplit(" ", 1)[1]
                    try:
                        check_filename = scrapertools.get_season_and_episode(fulltitle)
                    except:
                        fulltitle += " " + str(data['seasonNumber']) + "x00"
                    lista_episodios.append(Item(channel=item.channel, action="findvideos", server="",
                                                title=fulltitle, extra=url, url=item.url, fulltitle=fulltitle,
                                                contentTitle=fulltitle, show=show))
            else:
                for child in data["repoChilds"]:
                    url = "http://tv-vip.com/json/repo/%s/index.json" % child
                    fulltitle = child.capitalize().replace('_', ' ')
                    try:
                        check_filename = scrapertools.get_season_and_episode(fulltitle)
                    except:
                        fulltitle += " " + str(data['seasonNumber']) + "x00"
                    lista_episodios.append(Item(channel=item.channel, action="findvideos", server="",
                                                title=fulltitle, extra=url, url=item.url, contentTitle=fulltitle,
                                                fulltitle=fulltitle, show=show))
    # Para series directas de una sola temporada
    else:
        data = data_serie
        if data["sortedRepoChilds"]:
            for child in data["sortedRepoChilds"]:
                url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
                fulltitle = child['name'].rsplit(" ", 1)[0] + " - " + child['name'].rsplit(" ", 1)[1]
                try:
                    check_filename = scrapertools.get_season_and_episode(fulltitle)
                except:
                    fulltitle += " 1x00"
                lista_episodios.append(Item(channel=item.channel, action="findvideos", server="", title=fulltitle,
                                            contentTitle=fulltitle, url=item.url, extra=url, fulltitle=fulltitle,
                                            show=show))
        else:
            for child in data["repoChilds"]:
                url = "http://tv-vip.com/json/repo/%s/index.json" % child
                fulltitle = child.capitalize().replace('_', ' ')
                try:
                    check_filename = scrapertools.get_season_and_episode(fulltitle)
                except:
                    fulltitle += " 1x00"
                lista_episodios.append(Item(channel=item.channel, action="findvideos", server="", title=fulltitle,
                                            contentTitle=fulltitle, url=item.url, extra=url, fulltitle=fulltitle,
                                            show=show))

    return lista_episodios


def findvideos(item):
    logger.info()
    itemlist = []

    # En caso de llamarse a la función desde una serie de la videoteca
    if item.extra.startswith("http"): item.url = item.extra
    data = scrapertools.anti_cloudflare(item.url, host=host, headers=headers)
    data = jsontools.load(data)
    id = urllib.quote(data['id'])
    for child in data["profiles"].keys():
        videopath = urllib.quote(data["profiles"][child]['videoUri'])
        for i in range(0, len(data["profiles"][child]['servers'])):
            url = data["profiles"][child]['servers'][i]['url'] + videopath
            size = "  " + data["profiles"][child]["sizeHuman"]
            resolution = " [" + (data["profiles"][child]['videoResolution']) + "]"
            title = "Ver vídeo en " + resolution.replace('1920x1080', 'HD-1080p')
            if i == 0:
                title += size + " [COLOR purple]Mirror " + str(i + 1) + "[/COLOR]"
            else:
                title += size + " [COLOR green]Mirror " + str(i + 1) + "[/COLOR]"
            # Para poner enlaces de mayor calidad al comienzo de la lista
            if data["profiles"][child]["profileId"] == "default":
                itemlist.insert(i, item.clone(action="play", server="directo", title=bbcode_kodi2html(title), url=url,
                                              contentTitle=item.fulltitle, viewmode="list", extra=id, folder=False))
            else:
                itemlist.append(item.clone(action="play", server="directo", title=bbcode_kodi2html(title), url=url,
                                           contentTitle=item.fulltitle, viewmode="list", extra=id, folder=False))

    itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                               text_color="magenta"))
    if len(itemlist) > 0 and item.extra == "":
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir enlaces a la videoteca", text_color="green",
                                 contentTitle=item.fulltitle, url=item.url, action="add_pelicula_to_library",
                                 infoLabels={'title': item.fulltitle}, extra="findvideos", fulltitle=item.fulltitle))

    return itemlist


def play(item):
    import time
    import requests
    logger.info()
    itemlist = []

    cookie = get_cookie_value()
    headers_play = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'DNT': '1',
                    'Referer': 'http://tv-vip.com/film/' + item.extra + '/',
                    'Cookie': cookie}

    head = "|User-Agent=" + headers_play['User-Agent'] + "&Referer=" + headers_play['Referer'] + "&Cookie=" + \
           headers_play['Cookie']
    uri = scrapertools.find_single_match(item.url, '(/transcoder[\w\W]+)')
    uri_request = "http://tv-vip.com/video-prod/s/uri?uri=%s&_=%s" % (uri, int(time.time()))

    data = requests.get(uri_request, headers=headers_play)
    data = jsontools.load(data.text)
    url = item.url.replace("/transcoder/", "/s/transcoder/") + "?tt=" + str(data['tt']) + \
          "&mm=" + data['mm'] + "&bb=" + data['bb'] + head
    itemlist.append(item.clone(action="play", server="directo", url=url, folder=False))
    return itemlist


def listas(item):
    logger.info()
    # Para añadir listas a la videoteca en carpeta CINE
    itemlist = []
    data = scrapertools.anti_cloudflare(item.url, host=host, headers=headers)
    data = jsontools.load(data)
    head = header_string + get_cookie_value()
    for child in data["sortedRepoChilds"]:
        infolabels = {}

        # Fanart
        if child['hashBackground']:
            fanart = "http://tv-vip.com/json/repo/%s/background.jpg" % child["id"]
        else:
            fanart = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child["id"]
        # Thumbnail
        if child['hasPoster']:
            thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child["id"]
        else:
            thumbnail = fanart
        thumbnail += head
        fanart += head

        url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
        if child['name'] == "":
            title = scrapertools.slugify(child['id'].rsplit(".", 1)[0])
        else:
            title = scrapertools.slugify(child['name'])
        title = title.replace('-', ' ').replace('_', ' ').capitalize()
        infolabels['title'] = title
        try:
            from core import videolibrarytools
            new_item = item.clone(title=title, url=url, fulltitle=title, fanart=fanart, extra="findvideos",
                                  thumbnail=thumbnail, infoLabels=infolabels, category="Cine")
            videolibrarytools.add_pelicula_to_library(new_item)
            error = False
        except:
            error = True
            import traceback
            logger.error(traceback.format_exc())

    if not error:
        itemlist.append(Item(channel=item.channel, title='Lista añadida correctamente a la videoteca',
                             action="", folder=False))
    else:
        itemlist.append(Item(channel=item.channel, title='ERROR. Han ocurrido uno o varios errores en el proceso',
                             action="", folder=False))

    return itemlist


def get_cookie_value():
    cookies = os.path.join(config.get_data_path(), 'cookies', 'tv-vip.com.dat')
    cookiedatafile = open(cookies, 'r')
    cookiedata = cookiedatafile.read()
    cookiedatafile.close()
    cfduid = scrapertools.find_single_match(cookiedata, "tv-vip.*?__cfduid\s+([A-Za-z0-9\+\=]+)")
    cfduid = "__cfduid=" + cfduid
    return cfduid


def bbcode_kodi2html(text):
    if config.get_platform().startswith("plex") or config.get_platform().startswith("mediaserver"):
        import re
        text = re.sub(r'\[COLOR\s([^\]]+)\]',
                      r'<span style="color: \1">',
                      text)
        text = text.replace('[/COLOR]', '</span>') \
            .replace('[CR]', '<br>') \
            .replace('[B]', '<strong>') \
            .replace('[/B]', '</strong>') \
            .replace('"color: white"', '"color: auto"')

    return text
