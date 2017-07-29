# -*- coding: utf-8 -*-

import string

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

__modo_grafico__ = config.get_setting('modo_grafico', "allpeliculas")
__perfil__ = int(config.get_setting('perfil', "allpeliculas"))

# Fijar perfil de color
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]
color1, color2, color3 = perfil[__perfil__]

IDIOMAS = {"Castellano": "CAST", "Latino": "LAT", "Subtitulado": "VOSE", "Ingles": "VO"}
SERVERS = {"26": "powvideo", "45": "okru", "75": "openload", "12": "netutv", "65": "thevideos",
           "67": "spruto", "71": "stormo", "73": "idowatch", "48": "okru", "55": "openload",
           "20": "nowvideo", "84": "fastplay", "96": "raptu", "94": "tusfiles"}


def mainlist(item):
    logger.info()
    itemlist = []
    item.text_color = color1

    itemlist.append(item.clone(title="Películas", action="lista", fanart="http://i.imgur.com/c3HS8kj.png",
                               url="http://allpeliculas.co/Movies/fullView/1/0/&ajax=1"))
    itemlist.append(item.clone(title="Series", action="lista", fanart="http://i.imgur.com/9loVksV.png", extra="tv",
                               url="http://allpeliculas.co/Movies/fullView/1/86/?ajax=1&withoutFilter=1", ))
    itemlist.append(item.clone(title="Géneros", action="subindice", fanart="http://i.imgur.com/ymazCWq.jpg"))
    itemlist.append(item.clone(title="Índices", action="indices", fanart="http://i.imgur.com/c3HS8kj.png"))
    itemlist.append(item.clone(title="", action=""))
    itemlist.append(item.clone(title="Buscar...", action="search"))
    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", text_color="gold", folder=False))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    if texto != "":
        texto = texto.replace(" ", "+")
    item.url = "http://allpeliculas.co/Search/advancedSearch?searchType=movie&movieName=" + texto + "&ajax=1"
    try:
        return busqueda(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = "http://allpeliculas.co/Movies/fullView/1/0/&ajax=1"
            item.action = "lista"
            itemlist = lista(item)

            if itemlist[-1].action == "lista":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def busqueda(item):
    logger.info()
    itemlist = []
    item.infoLabels = {}
    item.text_color = color2

    data = httptools.downloadpage(item.url).data
    data = data.replace("\n", "").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)

    patron = '<img class="poster" src="([^"]+)".*?<div class="vote-div-count".*?>(.*?)/.*?' \
             '<a class="movie-list-link" href="([^"]+)" title="([^"]+)".*?' \
             'Year:</b> (.*?) </p>.*?Género:</b> (.*?)</p>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for thumbnail, vote, url, title, year, genre in matches:
        url = "http://allpeliculas.co" + url.replace("#", "") + "&ajax=1"
        thumbnail = thumbnail.replace("/105/", "/400/").replace("/141/", "/600/").replace(" ", "%20")
        titulo = title + " (" + year + ")"
        item.infoLabels['year'] = year
        item.infoLabels['genre'] = genre
        item.infoLabels['rating'] = vote
        if "Series" not in genre:
            itemlist.append(item.clone(action="findvideos", title=titulo, fulltitle=title, url=url, thumbnail=thumbnail,
                                       context=["buscar_trailer"], contentTitle=title, contentType="movie"))
        else:
            itemlist.append(item.clone(action="temporadas", title=titulo, fulltitle=title, url=url, thumbnail=thumbnail,
                                       context=["buscar_trailer"], contentTitle=title, contentType="tvshow"))

    # Paginacion
    next_page = scrapertools.find_single_match(data, 'class="pagination-active".*?href="([^"]+)"')
    if next_page != "":
        url = next_page.replace("#", "") + "&ajax=1"
        itemlist.append(item.clone(action="lista", title=">> Siguiente", url=url, text_color=color3))

    return itemlist


def indices(item):
    logger.info()
    itemlist = []
    item.text_color = color1

    itemlist.append(item.clone(title="Alfabético", action="subindice"))
    itemlist.append(item.clone(title="Por idioma", action="subindice"))
    itemlist.append(item.clone(title="Por valoración", action="lista",
                               url="http://allpeliculas.co/Movies/fullView/1/0/rating:imdb|date:1900-3000|"
                                   "alphabet:all|?ajax=1&withoutFilter=1"))
    itemlist.append(item.clone(title="Por año", action="subindice"))
    itemlist.append(item.clone(title="Por calidad", action="subindice"))

    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    item.infoLabels = {}
    item.text_color = color2

    data = httptools.downloadpage(item.url).data
    data = data.replace("\n", "").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)

    bloque = scrapertools.find_single_match(data, '<div class="movies-block-main"(.*?)<div class="movies-'
                                                  'long-pagination"')
    patron = '<div class="thumb"><img src="([^"]+)".*?<a href="([^"]+)".*?' \
             '(?:class="n-movie-trailer">([^<]+)<\/span>|<div class="imdb-votes">)' \
             '.*?<div class="imdb"><span>(.*?)</span>.*?<span>Year.*?">(.*?)</a>.*?<span>' \
             '(?:Género|Genre).*?<span>(.*?)</span>.*?<span>Language.*?<span>(.*?)</span>.*?' \
             '<div class="info-full-text".*?>(.*?)<.*?<div class="views">(.*?)<.*?' \
             '<div class="movie-block-title".*?>(.*?)<'

    if bloque == "":
        bloque = data[:]
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for thumbnail, url, trailer, vote, year, genre, idioma, sinopsis, calidad, title in matches:
        url = url.replace("#", "") + "&ajax=1"
        thumbnail = thumbnail.replace("/157/", "/400/").replace("/236/", "/600/").replace(" ", "%20")
        idioma = idioma.replace(" ", "").split(",")
        idioma.sort()
        titleidioma = "[" + "/".join(idioma) + "]"

        titulo = title + " " + titleidioma + " [" + calidad + "]"
        item.infoLabels['plot'] = sinopsis
        item.infoLabels['year'] = year
        item.infoLabels['genre'] = genre
        item.infoLabels['rating'] = vote
        item.infoLabels['trailer'] = trailer.replace("youtu.be/", "http://www.youtube.com/watch?v=")
        if item.extra != "tv" or "Series" not in genre:
            itemlist.append(item.clone(action="findvideos", title=titulo, fulltitle=title, url=url, thumbnail=thumbnail,
                                       context=["buscar_trailer"], contentTitle=title, contentType="movie"))
        else:
            itemlist.append(item.clone(action="temporadas", title=titulo, fulltitle=title, url=url, thumbnail=thumbnail,
                                       context=["buscar_trailer"], contentTitle=title, show=title,
                                       contentType="tvshow"))

    try:
        from core import tmdb
        # Obtenemos los datos basicos de todas las peliculas mediante multihilos
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass
    # Paginacion
    next_page = scrapertools.find_single_match(data, 'class="pagination-active".*?href="([^"]+)"')
    if next_page != "":
        url = next_page.replace("#", "") + "&ajax=1"
        itemlist.append(item.clone(action="lista", title=">> Siguiente", url=url, text_color=color3))

    return itemlist


def subindice(item):
    logger.info()
    itemlist = []

    url_base = "http://allpeliculas.co/Movies/fullView/1/0/date:1900-3000|alphabet:all|?ajax=1&withoutFilter=1"
    indice_genero, indice_alfa, indice_idioma, indice_year, indice_calidad = dict_indices()
    if "Géneros" in item.title:
        for key, value in indice_genero.items():
            url = url_base.replace("/0/", "/" + key + "/")
            itemlist.append(item.clone(action="lista", title=value, url=url))
            itemlist.sort(key=lambda item: item.title)

    elif "Alfabético" in item.title:
        for i in range(len(indice_alfa)):
            url = url_base.replace(":all", ":" + indice_alfa[i])
            itemlist.append(item.clone(action="lista", title=indice_alfa[i], url=url))

    elif "Por idioma" in item.title:
        for key, value in indice_idioma.items():
            url = url_base.replace("3000|", "3000|language:" + key)
            itemlist.append(item.clone(action="lista", title=value, url=url))
            itemlist.sort(key=lambda item: item.title)

    elif "Por año" in item.title:
        for i in range(len(indice_year)):
            year = indice_year[i]
            url = url_base.replace("1900-3000", year + "-" + year)
            itemlist.append(item.clone(action="lista", title=year, url=url))

    elif "Por calidad" in item.title:
        for key, value in indice_calidad.items():
            url = "http://allpeliculas.co/Search/advancedSearch?searchType=movie&movieName=&movieDirector=&movieGenre" \
                  "=&movieActor=&movieYear=&language=&movieTypeId=" + key + "&ajax=1"
            itemlist.append(item.clone(action="busqueda", title=value, url=url))
            itemlist.sort(key=lambda item: item.title)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    item.text_color = color3

    # Rellena diccionarios idioma y calidad
    idiomas_videos, calidad_videos = dict_videos()

    data = httptools.downloadpage(item.url).data
    data = data.replace("\n", "").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)

    if item.extra != "library":
        try:
            from core import tmdb
            tmdb.set_infoLabels(item, __modo_grafico__)
        except:
            pass

    # Enlaces Online
    patron = '<span class="movie-online-list" id_movies_types="([^"]+)" id_movies_servers="([^"]+)".*?id_lang=' \
             '"([^"]+)".*?online-link="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for calidad, servidor_num, language, url in matches:

        if servidor_num == '94' and not 'stormo.tv' in url:
            url = "http://tusfiles.org/?%s" % url

        if 'vimeo' in url:
            url += "|" + item.url

        if "filescdn" in url and url.endswith("htm"):
            url += "l"

        idioma = IDIOMAS.get(idiomas_videos.get(language))
        titulo = "%s  [" + idioma + "] [" + calidad_videos.get(calidad) + "]"
        itemlist.append(item.clone(action="play", title=titulo, url=url, extra=idioma))

    # Enlace Descarga
    patron = '<span class="movie-downloadlink-list" id_movies_types="([^"]+)" id_movies_servers="([^"]+)".*?id_lang=' \
             '"([^"]+)".*?online-link="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for calidad, servidor_num, language, url in matches:
        idioma = IDIOMAS.get(idiomas_videos.get(language))
        titulo = "[%s]  [" + idioma + "] [" + calidad_videos.get(calidad) + "]"
        itemlist.append(item.clone(action="play", title=titulo, url=url, extra=idioma))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    itemlist.sort(key=lambda item: (item.extra, item.server))
    if itemlist:
        if not "trailer" in item.infoLabels:
            trailer_url = scrapertools.find_single_match(data, 'class="n-movie-trailer">([^<]+)</span>')
            item.infoLabels['trailer'] = trailer_url.replace("youtu.be/", "http://www.youtube.com/watch?v=")

        itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                                   text_color="magenta", context=""))
        if item.extra != "library":
            if config.get_videolibrary_support():
                itemlist.append(Item(channel=item.channel, title="Añadir película a la videoteca",
                                     action="add_pelicula_to_library", url=item.url, text_color="green",
                                     infoLabels={'title': item.fulltitle}, fulltitle=item.fulltitle,
                                     extra="library"))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    try:
        from core import tmdb
        tmdb.set_infoLabels_item(item, __modo_grafico__)
    except:
        pass

    matches = scrapertools.find_multiple_matches(data, '<a class="movie-season" data-id="([^"]+)"')
    matches = list(set(matches))
    for season in matches:
        item.infoLabels['season'] = season
        itemlist.append(item.clone(action="episodios", title="Temporada " + season, context=["buscar_trailer"],
                                   contentType="season"))

    itemlist.sort(key=lambda item: item.title)
    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass

    if not "trailer" in item.infoLabels:
        trailer_url = scrapertools.find_single_match(data, 'class="n-movie-trailer">([^<]+)</span>')
        item.infoLabels['trailer'] = trailer_url.replace("youtu.be/", "http://www.youtube.com/watch?v=")

    itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                               text_color="magenta", context=""))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    # Rellena diccionarios idioma y calidad
    idiomas_videos, calidad_videos = dict_videos()

    data = httptools.downloadpage(item.url).data
    data = data.replace("\n", "").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)

    patron = '<li><a class="movie-episode"[^>]+season="' + str(item.infoLabels['season']) + '"[^>]+>([^<]+)</a></li>'
    matches = scrapertools.find_multiple_matches(data, patron)
    capitulos = []
    for title in matches:
        if not title in capitulos:
            episode = int(title.split(" ")[1])
            capitulos.append(title)
            itemlist.append(
                item.clone(action="findvideostv", title=title, contentEpisodeNumber=episode, contentType="episode"))

    itemlist.sort(key=lambda item: item.contentEpisodeNumber)
    try:
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass
    for item in itemlist:
        if item.infoLabels["episodio_titulo"]:
            item.title = "%dx%02d: %s" % (
            item.contentSeason, item.contentEpisodeNumber, item.infoLabels["episodio_titulo"])
        else:
            item.title = "%dx%02d: %s" % (item.contentSeason, item.contentEpisodeNumber, item.title)

    return itemlist


def findvideostv(item):
    logger.info()
    itemlist = []

    # Rellena diccionarios idioma y calidad
    idiomas_videos, calidad_videos = dict_videos()

    data = httptools.downloadpage(item.url).data
    data = data.replace("\n", "").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)

    patron = '<span class="movie-online-list" id_movies_types="([^"]+)" id_movies_servers="([^"]+)".*?episode="%s' \
             '" season="%s" id_lang="([^"]+)".*?online-link="([^"]+)"' \
             % (str(item.infoLabels['episode']), str(item.infoLabels['season']))
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, servidor_num, language, url in matches:

        if servidor_num == '94' and not 'stormo.tv' in url:
            url = "http://tusfiles.org/?%s" % url

        if 'vimeo' in url:
            url += "|" + item.url

        if "filescdn" in url and url.endswith("htm"):
            url += "l"

        idioma = IDIOMAS.get(idiomas_videos.get(language))
        titulo = "%s [" + idioma + "] (" + calidad_videos.get(quality) + ")"

        itemlist.append(item.clone(action="play", title=titulo, url=url, contentType="episode", server=server))

    # Enlace Descarga
    patron = '<span class="movie-downloadlink-list" id_movies_types="([^"]+)" id_movies_servers="([^"]+)".*?episode="%s' \
             '" season="%s" id_lang="([^"]+)".*?online-link="([^"]+)"' \
             % (str(item.infoLabels['episode']), str(item.infoLabels['season']))
    # patron = '<span class="movie-downloadlink-list" id_movies_types="([^"]+)" id_movies_servers="([^"]+)".*?episode="'+str(item.infoLabels['episode']) +'" season="'+str(item.infoLabels['season']) + '" id_lang="([^"]+)".*?online-link="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, servidor_num, episode, language, url in matches:
        idioma = IDIOMAS.get(idiomas_videos.get(language))
        titulo = "%s [" + idioma + "] (" + calidad_videos.get(quality) + ")"
        itemlist.append(item.clone(action="play", title=titulo, url=url, contentType="episode", server=server))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    itemlist.sort(key=lambda item: (int(item.infoLabels['episode']), item.title))
    try:
        from core import tmdb
        tmdb.set_infoLabels(itemlist, __modo_grafico__)
    except:
        pass

    return itemlist


def dict_videos():
    idiomas_videos = {}
    calidad_videos = {}
    data = httptools.downloadpage("http://allpeliculas.co/Search/advancedSearch&ajax=1").data
    data = data.replace("\n", "").replace("\t", "")
    bloque_idioma = scrapertools.find_single_match(data,
                                                   '<select name="language".*?<option value="" selected(.*?)</select>')
    matches = scrapertools.find_multiple_matches(bloque_idioma, '<option value="([^"]+)" >(.*?)</option>')
    for key1, key2 in matches:
        idiomas_videos[key1] = unicode(key2, "utf8").capitalize().encode("utf8")
    bloque_calidad = scrapertools.find_single_match(data, '<select name="movieTypeId".*?<option value="" selected(.*?)'
                                                          '</select>')
    matches = scrapertools.find_multiple_matches(bloque_calidad, '<option value="([^"]+)" >(.*?)</option>')
    for key1, key2 in matches:
        calidad_videos[key1] = key2

    return idiomas_videos, calidad_videos


def dict_indices():
    indice_genero = {}
    indice_alfa = list(string.ascii_uppercase)
    indice_alfa.append("0-9")
    indice_idioma = {}
    indice_year = []
    indice_calidad = {}
    data = httptools.downloadpage("http://allpeliculas.co/Search/advancedSearch&ajax=1").data
    data = data.replace("\n", "").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)
    bloque_genero = scrapertools.find_single_match(data, '<select name="movieGenre".*?<option value="" selected(.*?)'
                                                         '</select>')
    matches = scrapertools.find_multiple_matches(bloque_genero, '<option value="([^"]+)" >(.*?)</option>')
    for key1, key2 in matches:
        if key2 != "Series":
            if key2 == "Mystery":
                key2 = "Misterio"
            indice_genero[key1] = key2
    bloque_year = scrapertools.find_single_match(data, '<select name="movieYear".*?<option value="" selected(.*?)'
                                                       '</select>')
    matches = scrapertools.find_multiple_matches(bloque_year, '<option value="([^"]+)"')
    for key1 in matches:
        indice_year.append(key1)
    bloque_idioma = scrapertools.find_single_match(data, '<select name="language".*?<option value="" selected(.*?)'
                                                         '</select>')
    matches = scrapertools.find_multiple_matches(bloque_idioma, '<option value="([^"]+)" >(.*?)</option>')
    for key1, key2 in matches:
        if key2 == "INGLES":
            key2 = "Versión original"
        indice_idioma[key1] = unicode(key2, "utf8").capitalize().encode("utf8")

    bloque_calidad = scrapertools.find_single_match(data, '<select name="movieTypeId".*?<option value="" selected(.*?)'
                                                          '</select>')
    matches = scrapertools.find_multiple_matches(bloque_calidad, '<option value="([^"]+)" >(.*?)</option>')
    for key1, key2 in matches:
        indice_calidad[key1] = key2

    return indice_genero, indice_alfa, indice_idioma, indice_year, indice_calidad
