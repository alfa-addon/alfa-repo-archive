# -*- coding: utf-8 -*-

import re
import unicodedata

from core import config
from core import httptools
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item

host = "http://pelisipad.com/black_json/%s"
ext = "/list.js"

__perfil__ = config.get_setting('perfil', "pelisipad")

# Fijar perfil de color
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00', '0xFFFE2E2E', '0xFF088A08', '0xFFFFD700'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E', '0xFFFE2E2E', '0xFF088A08', '0xFFFFD700'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE', '0xFFFE2E2E', '0xFF088A08', '0xFFFFD700']]
if __perfil__ < 3:
    color1, color2, color3, color4, color5, color6 = perfil[__perfil__]
else:
    color1 = color2 = color3 = color4 = color5 = color6 = ""


def mainlist(item):
    logger.info()
    item.viewmode = "movie"
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Películas", action="submenu", text_color=color1,
                         thumbnail=host % "list/peliculas/thumbnail_167x250.jpg",
                         fanart=host % "list/peliculas/background_1080.jpg", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, title="Series", action="submenu", text_color=color1,
                         thumbnail=host % "list/series/thumbnail_167x250.jpg",
                         fanart=host % "list/series/background_1080.jpg", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, title="Películas Infantiles", action="entradasconlistas",
                         url=host % "list/peliculas-infantiles" + ext, text_color=color1,
                         thumbnail=host % "list/peliculas-infantiles/thumbnail_167x250.jpg",
                         fanart=host % "list/peliculas-infantiles/background_1080.jpg", viewmode="movie_with_plot"))
    itemlist.append(Item(channel=item.channel, title="", action=""))
    itemlist.append(Item(channel=item.channel, title="Configuración", action="configuracion", text_color=color6))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def submenu(item):
    logger.info()
    itemlist = []

    if "Series" in item.title:
        itemlist.append(Item(channel=item.channel, title="Nuevos Capítulos", action="nuevos_cap",
                             url=host % "list/nuevos-capitulos" + ext, text_color=color2,
                             thumbnail=host % "list/nuevos-capitulos/thumbnail_167x250.jpg",
                             fanart=host % "list/nuevos-capitulos/background_1080.jpg", viewmode="movie"))
        itemlist.append(Item(channel=item.channel, title="Nuevas Temporadas", action="nuevos_cap",
                             url=host % "list/nuevos-capitulos" + ext, text_color=color2,
                             thumbnail=host % "list/nuevos-capitulos/thumbnail_167x250.jpg",
                             fanart=host % "list/nuevos-capitulos/background_1080.jpg", viewmode="movie"))
        itemlist.append(Item(channel=item.channel, title="Series más vistas", action="series", text_color=color2,
                             url=host % "list/series" + ext, viewmode="movie_with_plot",
                             thumbnail=item.thumbnail, fanart=item.fanart, contentTitle="Series"))
        itemlist.append(Item(channel=item.channel, title="Lista de Series A-Z", action="series", text_color=color2,
                             url=host % "list/series" + ext, thumbnail=item.thumbnail,
                             fanart=item.fanart, contentTitle="Series", viewmode="movie_with_plot"))
    else:
        itemlist.append(Item(channel=item.channel, title="Novedades", action="entradas",
                             url=host % "list/ultimas-peliculas" + ext, text_color=color2,
                             thumbnail=host % "list/ultimas-peliculas/thumbnail_167x250.jpg",
                             fanart=host % "list/ultimas-peliculas/background_1080.jpg", viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, title="Destacados", action="entradas",
                             url=host % "list/000-novedades" + ext, text_color=color2,
                             thumbnail=host % "list/screener/thumbnail_167x250.jpg",
                             fanart=host % "list/screener/background_1080.jpg", viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, title="Más vistas", action="entradas",
                             url=host % "list/peliculas-mas-vistas" + ext, text_color=color2,
                             thumbnail=host % "list/peliculas-mas-vistas/thumbnail_167x250.jpg",
                             fanart=host % "list/peliculas-mas-vistas/background_1080.jpg", viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, title="Categorías", action="cat", url=host % "list/peliculas" + ext,
                             text_color=color2, thumbnail=item.thumbnail, fanart=item.fanart))

    return itemlist


def cat(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = jsontools.load(data)

    exception = ["peliculas-mas-vistas", "ultimas-peliculas"]
    for child in data["b"]:
        if child["id"] in exception:
            continue
        child['name'] = child['name'].replace("ciencia-ficcion", "Ciencia Ficción").replace("-", " ")
        url = host % "list/%s" % child["id"] + ext
        # Fanart
        fanart = host % "list/%s/background_1080.jpg" % child["id"]
        # Thumbnail
        thumbnail = host % "list/%s/thumbnail_167x250.jpg" % child["id"]
        title = unicode(child['name'], "utf-8").capitalize().encode("utf-8")
        itemlist.append(
            Item(channel=item.channel, action="entradasconlistas", title=title, url=url,
                 thumbnail=thumbnail, fanart=fanart, text_color=color2))
    itemlist.sort(key=lambda it: it.title)

    return itemlist


def entradas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = jsontools.load(data)

    if "Destacados" in item.title:
        itemlist.append(item.clone(title="Aviso: Si una película no tiene (imagen/carátula) NO va a funcionar",
                                   action="", text_color=color4))

    for child in data["a"]:
        infolabels = {}

        infolabels['originaltitle'] = child['originalTitle']
        infolabels['plot'] = child['description']
        infolabels['year'] = child['year']
        if child.get('tags'): infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rateHuman'].replace(',', '.')
        infolabels['votes'] = child['rateCount']
        if child.get('runtime'):
            try:
                infolabels['duration'] = int(child['runtime'].replace(" min.", "")) * 60
            except:
                pass
        if child.get('cast'): infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']
        url = host % "movie/%s/movie.js" % child["id"]
        # Fanart
        fanart = host % "movie/%s/background_480.jpg" % child["id"]
        if child.get("episode"):
            thumbnail = host % "movie/%s/thumbnail_200x112.jpg" % child["id"]
        else:
            thumbnail = host % "movie/%s/poster_167x250.jpg" % child["id"]

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

        video_urls = []
        for k, v in child.get("video", {}).items():
            for vid in v:
                video_urls.append(["http://%s.pelisipad.com/s/transcoder/%s" % (vid["server"], vid["url"]) + "?%s",
                                   vid["height"]])

        itemlist.append(Item(channel=item.channel, action="findvideos", server="", title=title, url=url,
                             thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, infoLabels=infolabels,
                             contentTitle=fulltitle, video_urls=video_urls, text_color=color3))

    return itemlist


def entradasconlistas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = jsontools.load(data)

    # Si hay alguna lista
    contentSerie = False
    contentList = False
    if data.get('b'):
        for child in data['b']:
            infolabels = {}

            infolabels['originaltitle'] = child['originalTitle']
            infolabels['plot'] = child['description']
            infolabels['year'] = data['year']
            if child.get('tags'): infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
            infolabels['rating'] = child['rateHuman'].replace(',', '.')
            infolabels['votes'] = child['rateCount']
            if child.get('runtime'):
                try:
                    infolabels['duration'] = int(child['runtime'].replace(" min.", "")) * 60
                except:
                    pass
            if child.get('cast'): infolabels['cast'] = child['cast'].split(",")
            infolabels['director'] = child['director']
            season = child.get('season', '')
            if season.isdigit() and not contentList:
                contentSerie = True
                action = "episodios"
            else:
                contentSerie = False
                contentList = True
                action = "entradasconlistas"

            url = host % "list/%s" % child["id"] + ext
            title = re.sub(r"(\w)-(\w)", '\g<1> \g<2>', child['name'])
            fulltitle = re.sub(r"(\w)-(\w)", '\g<1> \g<2>', child['name'])
            if not title:
                title = re.sub(r"(\w)-(\w)", '\g<1> \g<2>', child['id'])
                fulltitle = re.sub(r"(\w)-(\w)", '\g<1> \g<2>', child['id'])
            title = unicode(title, "utf-8").capitalize().encode("utf-8")
            fulltitle = unicode(fulltitle, "utf-8").capitalize().encode("utf-8")
            show = ""
            if contentSerie:
                title += " (Serie TV)"
                show = fulltitle
            thumbnail = host % "list/%s/thumbnail_167x250.jpg" % child["id"]
            fanart = host % "list/%s/background_1080.jpg" % child["id"]

            itemlist.append(Item(channel=item.channel, action=action, title=title,
                                 url=url, thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, show=show,
                                 infoLabels=infolabels, contentTitle=fulltitle, viewmode="movie_with_plot",
                                 text_color=color3))
    else:
        contentList = True

    if contentSerie and itemlist:
        itemlist.sort(key=lambda it: it.infoLabels['season'], reverse=True)

    if itemlist:
        itemlist.insert(0, Item(channel=item.channel, title="**LISTAS**", action="", text_color=color4, text_bold=True,
                                thumbnail=item.thumbnail, fanart=item.fanart))

    if data.get("a") and itemlist:
        itemlist.append(Item(channel=item.channel, title="**VÍDEOS**", action="", text_color=color6, text_bold=True,
                             thumbnail=item.thumbnail, fanart=item.fanart))

    for child in data.get("a", []):
        infolabels = {}

        infolabels['originaltitle'] = child['originalTitle']
        infolabels['plot'] = child['description']
        infolabels['year'] = data['year']
        if child.get('tags'): infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rateHuman'].replace(',', '.')
        infolabels['votes'] = child['rateCount']
        if child.get('runtime'):
            try:
                infolabels['duration'] = int(child['runtime'].replace(" min.", "")) * 60
            except:
                pass
        if child.get('cast'): infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']
        url = host % "movie/%s/movie.js" % child["id"]
        # Fanart
        fanart = host % "movie/%s/background_1080.jpg" % child["id"]
        if child.get("episode"):
            thumbnail = host % "movie/%s/thumbnail.jpg" % child["id"]
        else:
            thumbnail = host % "movie/%s/poster_167x250.jpg" % child["id"]

        if child['height'] < 720:
            quality = "[B]  [SD][/B]"
        elif child['height'] < 1080:
            quality = "[B]  [720p][/B]"
        elif child['height'] >= 1080:
            quality = "[B]  [1080p][/B]"
        fulltitle = unicodedata.normalize('NFD', unicode(child['name'], 'utf-8')).encode('ASCII', 'ignore') \
            .decode("utf-8")
        if not child['name']:
            title = child['id'].rsplit(".", 1)[0]
        else:
            title = child['name']
        if child['year']:
            title += " (" + child['year'] + ")"
        title += quality

        video_urls = []
        for k, v in child.get("video", {}).items():
            for vid in v:
                video_urls.append(["http://%s.pelisipad.com/s/transcoder/%s" % (vid["server"], vid["url"]) + "?%s",
                                   vid["height"]])

        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, video_urls=video_urls,
                             thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, infoLabels=infolabels,
                             contentTitle=fulltitle, viewmode="movie_with_plot", text_color=color3))

    # Se añade item para añadir la lista de vídeos a la videoteca
    if data.get('a') and itemlist and contentList and config.get_videolibrary_support():
        itemlist.append(Item(channel=item.channel, text_color=color5, title="Añadir esta lista a la videoteca",
                             url=item.url, action="listas"))
    elif contentSerie and config.get_videolibrary_support():
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", text_color=color5,
                             url=item.url, action="add_serie_to_library", show=item.show,
                             fulltitle=item.fulltitle, extra="episodios"))

    return itemlist


def series(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = jsontools.load(data)
    for child in data.get("b", []):
        infolabels = {}

        infolabels['originaltitle'] = child['originalTitle']
        infolabels['plot'] = child['description']
        infolabels['year'] = child['year']
        if child.get('tags'): infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rateHuman'].replace(',', '.')
        infolabels['votes'] = child['rateCount']
        if child.get('cast'): infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']
        if child.get('runtime'):
            try:
                infolabels['duration'] = int(child['runtime'].replace(" min.", "")) * 60
            except:
                pass
        infolabels['mediatype'] = "tvshow"
        if child['season']: infolabels['season'] = child['season']

        url = host % "list/%s" % child["id"] + ext
        # Fanart
        fanart = host % "list/%s/background_1080.jpg" % child["id"]
        # Thumbnail
        thumbnail = host % "list/%s/thumbnail_167x250.jpg" % child["id"]
        fulltitle = child['name']
        title = fulltitle + " [%s]" % child['year']
        if child.get("numberOfSeasons") and "- Temporada" not in title:
            title += "  (Temps:%s)" % child['numberOfSeasons']

        itemlist.append(Item(channel=item.channel, action="episodios", title=title, url=url, text_color=color3,
                             thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, infoLabels=infolabels,
                             contentTitle=fulltitle, viewmode="movie_with_plot", show=fulltitle))

    if "A-Z" in item.title:
        itemlist.sort(key=lambda it: it.title)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = jsontools.load(data)

    capitulos = []
    if data.get("b"):
        for child in data["b"]:
            for child2 in child["a"]:
                capitulos.append([child["season"], child2, child["id"]])
    else:
        for child in data.get("a", []):
            capitulos.append(['', child, ''])

    for season, child, id_season in capitulos:
        infoLabels = item.infoLabels.copy()

        if child.get('runtime'):
            try:
                infoLabels['duration'] = int(child['runtime'].replace(" min.", "")) * 60
            except:
                pass
        if not season or not season.isdigit():
            season = scrapertools.find_single_match(child['name'], '(\d+)x\d+')
        try:
            infoLabels['season'] = int(season)
        except:
            infoLabels['season'] = 0

        if not child['episode']:
            episode = scrapertools.find_single_match(child['name'], '\d+x(\d+)')
            if not episode:
                episode = "0"
            infoLabels['episode'] = int(episode)
        else:
            infoLabels['episode'] = int(child['episode'])
        infoLabels['mediatype'] = "episode"

        url = host % "movie/%s/movie.js" % child["id"]
        thumbnail = host % "movie/%s/thumbnail_200x112.jpg" % child["id"]
        if id_season:
            fanart = host % "list/%s/background_1080.jpg" % id_season
        else:
            fanart = item.fanart

        video_urls = []
        for k, v in child.get("video", {}).items():
            for vid in v:
                video_urls.append(["http://%s.pelisipad.com/s/transcoder/%s" % (vid["server"], vid["url"]) + "?%s",
                                   vid["height"]])

        try:
            title = fulltitle = child['name'].rsplit(" ", 1)[0] + " - " + child['name'].rsplit(" ", 1)[1]
        except:
            title = fulltitle = child['id'].replace("-", " ")
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                             fanart=fanart, fulltitle=fulltitle, contentTitle=fulltitle, viewmode="movie",
                             show=item.show, infoLabels=infoLabels, video_urls=video_urls, extra="episodios",
                             text_color=color3))

    itemlist.sort(key=lambda it: (it.infoLabels["season"], it.infoLabels["episode"]), reverse=True)
    if itemlist and config.get_videolibrary_support():
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", text_color=color5,
                             url=item.url, action="add_serie_to_library", infoLabels=item.infoLabels,
                             show=item.show, extra="episodios"))

    return itemlist


def nuevos_cap(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = jsontools.load(data)
    capitulos = []
    if "Nuevas" in item.title:
        for child in data["b"]:
            capitulos.append([child["season"], child])
    else:
        for child in data["a"]:
            capitulos.append(['', child])

    for season, child in capitulos:
        infoLabels = item.infoLabels
        if child.get('runtime'):
            try:
                infoLabels['duration'] = int(child['runtime'].replace(" min.", "")) * 60
            except:
                pass
        if not season:
            season = scrapertools.find_single_match(child['name'], '(\d+)x\d+')
        try:
            infoLabels['season'] = int(season)
        except:
            infoLabels['season'] = 0

        if "Nuevos" in item.title:
            if not child['episode']:
                episode = scrapertools.find_single_match(child['name'], '\d+x(\d+)')
                if not episode:
                    episode = "0"
                infoLabels['episode'] = int(episode)
            else:
                infoLabels['episode'] = int(child['episode'])
            infoLabels['mediatype'] = "episode"

        if "Nuevos" in item.title:
            url = host % "movie/%s/movie.js" % child["id"]
            action = "findvideos"
            thumbnail = host % "movie/%s/thumbnail_200x112.jpg" % child["id"]
            fanart = item.fanart
        else:
            url = host % "list/%s" % child["season"] + ext
            action = "episodios"
            thumbnail = host % "list/%s/thumbnail_167x250.jpg" % child["id"]
            fanart = host % "list/%s/background_1080.jpg" % child["id"]

        video_urls = []
        for k, v in child.get("video", {}).items():
            for vid in v:
                video_urls.append(["http://%s.pelisipad.com/s/transcoder/%s" % (vid["server"], vid["url"]) + "?%s",
                                   vid["height"]])

        if "Nuevos" in item.title:
            title = fulltitle = child['name'].rsplit(" ", 1)[0] + " - " + child['name'].rsplit(" ", 1)[1]
        else:
            title = fulltitle = child['name']

        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                             fanart=fanart, fulltitle=fulltitle, contentTitle=fulltitle, viewmode="movie",
                             show=item.fulltitle, infoLabels=infoLabels, video_urls=video_urls, extra="nuevos",
                             text_color=color3))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if not item.video_urls:
        data = httptools.downloadpage(item.url)
        if not data.sucess:
            itemlist.append(item.clone(title="Película no disponible", action=""))
            return itemlist
        data = jsontools.load(data.data)

        item.video_urls = []
        for k, v in data.get("video", {}).items():
            for vid in v:
                item.video_urls.append(["http://%s.pelisipad.com/s/transcoder/%s" % (vid["server"], vid["url"]) + "?%s",
                                        vid["height"]])

    if item.video_urls:
        import random
        import base64
        item.video_urls.sort(key=lambda it: (it[1], random.random()), reverse=True)
        i = 0
        calidad_actual = ""
        for vid, calidad in item.video_urls:
            title = "Ver vídeo en %sp" % calidad
            if calidad != calidad_actual:
                i = 0
                calidad_actual = calidad

            if i % 2 == 0:
                title += " [COLOR purple]Mirror %s[/COLOR] - %s" % (str(i + 1), item.fulltitle)
            else:
                title += " [COLOR green]Mirror %s[/COLOR] - %s" % (str(i + 1), item.fulltitle)
            url = vid % "%s" % base64.b64decode("dHQ9MTQ4MDE5MDQ1MSZtbT1NRzZkclhFand6QmVzbmxSMHNZYXhBJmJiPUUwb1dVVVgx"
                                                "WTBCQTdhWENpeU9paUE=")
            itemlist.append(item.clone(title=title, action="play", url=url, server="directo", video_urls=""))
            i += 1

        if itemlist and item.extra == "" and config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir enlaces a la videoteca", text_color=color5,
                                 contentTitle=item.fulltitle, url=item.url, action="add_pelicula_to_library",
                                 infoLabels={'title': item.fulltitle}, extra="findvideos", fulltitle=item.fulltitle))

    return itemlist


def listas(item):
    logger.info()
    # Para añadir listas a la videoteca en carpeta CINE
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = jsontools.load(data)
    for child in data.get("a", []):
        infolabels = {}

        # Fanart
        fanart = host % "movie/%s/background_1080.jpg" % child["id"]
        thumbnail = host % "movie/%s/poster_167x250.jpg" % child["id"]

        url = host % "movie/%s/movie.js" % child["id"]
        if child['name'] == "":
            title = scrapertools.slugify(child['id'].rsplit(".", 1)[0])
        else:
            title = scrapertools.slugify(child['name'])
        title = title.replace('-', ' ').replace('_', ' ')
        title = unicode(title, "utf-8").capitalize().encode("utf-8")
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
        itemlist.append(Item(channel=item.channel, title='Lista añadida correctamente a la videoteca', action=""))
    else:
        itemlist.append(Item(channel=item.channel, title='ERROR. Han ocurrido uno o varios errores en el proceso',
                             action=""))

    return itemlist
