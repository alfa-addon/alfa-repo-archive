# -*- coding: utf-8 -*-

import re

from core import channeltools
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

HOST = 'http://www.wopelis.com'
__channel__ = 'wopelis'
parameters = channeltools.get_channel_parameters(__channel__)
fanart_host = parameters['fanart']
thumbnail_host = parameters['thumbnail']
color1, color2, color3 = ['0xFF58D3F7', '0xFF2E64FE', '0xFF0404B4']


def mainlist(item):
    logger.info()
    itemlist = []
    item.url = HOST
    item.text_color = color2
    item.fanart = fanart_host

    item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/Directors%20Chair.png"
    url = HOST + "/galep.php?solo=cenlaces&empen=0"
    itemlist.append(item.clone(title="Películas:", folder=False, text_color=color3, text_bold=True))
    itemlist.append(item.clone(title="    Recientes", action="listado", url=url))
    itemlist.append(item.clone(title="    Mas populares de la semana", action="listado", url=url + "&ord=popu"))
    itemlist.append(item.clone(title="    Por géneros", action="generos", url=HOST + "/index.php"))
    itemlist.append(item.clone(title="    Buscar película", action="search", url=url))

    itemlist.append(item.clone(title="", folder=False, thumbnail=thumbnail_host))

    item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/TV%20Series.png"
    url = HOST + "/gales.php?empen=0"
    itemlist.append(item.clone(title="Series:", folder=False, text_color=color3, text_bold=True))
    itemlist.append(item.clone(title="    Nuevos episodios", action="listado", url=url + "&ord=reci"))
    itemlist.append(item.clone(title="    Mas populares de la semana", action="listado", url=url + "&ord=popu"))
    itemlist.append(item.clone(title="    Por géneros", action="generos", url=HOST + "/series.php"))
    itemlist.append(item.clone(title="    Buscar serie", action="search", url=url + "&ord=popu"))

    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = HOST + "/galep.php?solo=cenlaces&empen=0"

        elif categoria == 'series':
            item.url = HOST + "/gales.php?empen=0&ord=reci"

        else:
            return []

        itemlist = listado(item)
        if itemlist[-1].title == ">> Página siguiente":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info("search:" + texto)
    try:
        if texto:
            item.url = "%s&busqueda=%s" % (item.url, texto.replace(" ", "+"))
            return listado(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def generos(item):
    logger.info()
    itemlist = []
    dict_gender = {"acción": "accion", "animación": "animacion", "ciencia ficción": "ciencia%20ficcion",
                   "fantasía": "fantasia", "música": "musica", "película de la televisión": "pelicula%20de%20tv"}

    data = downloadpage(item.url)
    data = scrapertools.find_single_match(data, '<select name="gener">(.*?)</select>')

    for genero in scrapertools.find_multiple_matches(data, '<option value="([^"]+)'):
        if genero != 'Todos':
            if 'series' in item.url:
                url = HOST + "/gales.php?empen=0&gener=%s" % genero
            else:
                url = HOST + "/galep.php?solo=cenlaces&empen=0&gener=%s" % genero

            thumbnail = "https://raw.githubusercontent.com/master-1970/resources/master/images/genres/4/azul/%s.png"
            thumbnail = thumbnail % dict_gender.get(genero.lower(), genero.lower())

            itemlist.append(Item(channel=item.channel, action="listado", title=genero, url=url, text_color=color1,
                                 contentType='movie', folder=True,
                                 thumbnail=thumbnail))  # ,viewmode="movie_with_plot"))

    return sorted(itemlist, key=lambda i: i.title.lower())


def listado(item):
    logger.info(item)
    itemlist = []

    data = downloadpage(item.url)

    patron = '<a class="extended" href=".([^"]+).*?'
    patron += '<img class="centeredPicFalse"([^>]+).*?'
    patron += '<span class="year">(\d{4})</span>.*?'
    patron += '<span class="title">(.*?)</span>'

    for url, pic, year, title in scrapertools.find_multiple_matches(data, patron):
        thumbnail = scrapertools.find_single_match(pic, 'src="([^"]+)')
        if not thumbnail:
            thumbnail = HOST + "/images/cover-notfound.png"

        new_item = Item(channel=__channel__, thumbnail=thumbnail, text_color=color2, infoLabels={"year": year})

        if "galep.php" in item.url:
            # movie
            new_item.contentTitle = title
            new_item.action = "findvideos"
            new_item.url = HOST + url.replace('peli.php?id=', 'venlaces.php?npl=')


        elif "gales.php" in item.url:
            # tvshow
            title = title.replace(' - 0x0', '')
            new_item.contentSerieName = title
            new_item.action = "temporadas"
            new_item.url = HOST + url
            if "ord=reci" in item.url:
                # episode
                season_episode = scrapertools.get_season_and_episode(title)
                if season_episode:
                    new_item.contentSeason, new_item.contentEpisodeNumber = season_episode.split('x')
                    new_item.action = "get_episodio"
                    new_item.contentSerieName = title.split('-', 1)[1].strip()

            elif "gener=" in item.url and scrapertools.get_season_and_episode(title):
                # Las series filtrada por genero devuelven capitulos y series completas
                title = title.split('-', 1)[1].strip()
                new_item.contentSerieName = title

        else:
            return []

        new_item.title = "%s (%s)" % (title, year)

        itemlist.append(new_item)

    if itemlist:
        # Obtenemos los datos basicos mediante multihilos
        tmdb.set_infoLabels(itemlist)

    # Si es necesario añadir paginacion
    if len(itemlist) == 35:
        empen = scrapertools.find_single_match(item.url, 'empen=(\d+)')
        url_next_page = item.url.replace('empen=%s' % empen, 'empen=%s' % (int(empen) + 35))
        itemlist.append(Item(channel=item.channel, action="listado", title=">> Página siguiente",
                             thumbnail=thumbnail_host, url=url_next_page, folder=True,
                             text_color=color3, text_bold=True))

    return itemlist


def temporadas(item):
    logger.info(item)
    itemlist = []

    data = downloadpage(item.url)
    patron = '<div class="checkSeason" data-num="([^"]+)[^>]+>([^<]+)'

    for num_season, title in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(contentSeason=num_season, title="%s - %s" % (item.contentSerieName, title),
                                   action="episodios"))

    if itemlist:
        # Obtenemos los datos de las temporadas mediante multihilos
        tmdb.set_infoLabels(itemlist)

        if config.get_videolibrary_support():
            itemlist.append(item.clone(title="Añadir esta serie a la videoteca",
                                       action="add_serie_to_library", extra="episodios",
                                       text_color=color1, thumbnail=thumbnail_host, fanart=fanart_host))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = downloadpage(item.url)
    patron = '<div class="checkSeason" data-num="([^"]+)(.*?)</div></div></div>'
    for num_season, data in scrapertools.find_multiple_matches(data, patron):
        if item.contentSeason and item.contentSeason != int(num_season):
            # Si buscamos los episodios de una temporada concreta y no es esta (num_season)...
            continue

        patron = '<div class="info"><a href="..([^"]+).*?class="number">([^<]+)'
        for url, num_episode in scrapertools.find_multiple_matches(data, patron):
            if item.contentEpisodeNumber and item.contentEpisodeNumber != int(num_episode):
                # Si buscamos un episodio concreto y no es este (num_episode)...
                continue

            title = "%sx%s - %s" % (num_season, num_episode.strip().zfill(2), item.contentSerieName)
            itemlist.append(item.clone(title=title, url=HOST + url, action="findvideos",
                                       contentSeason=num_season, contentEpisodeNumber=num_episode))

    if itemlist and hasattr(item, 'contentSeason'):
        # Obtenemos los datos de los episodios de esta temporada mediante multihilos
        tmdb.set_infoLabels(itemlist)

        for i in itemlist:
            if i.infoLabels['title']:
                # Si el capitulo tiene nombre propio añadirselo al titulo del item
                i.title = "%sx%s %s" % (
                i.infoLabels['season'], str(i.infoLabels['episode']).zfill(2), i.infoLabels['title'])

    return itemlist


def get_episodio(item):
    logger.info()
    itemlist = episodios(item)
    if itemlist:
        itemlist = findvideos(itemlist[0])

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    dic_langs = {'esp': 'Español', 'english': 'Ingles', 'japo': 'Japones', 'argentina': 'Latino', 'ntfof': ''}
    dic_servers = {'ntfof': 'Servidor Desconocido', 'stramango': 'streamango', 'flasht': 'flashx'}

    data1 = downloadpage(item.url)
    patron = 'onclick="redir\(([^\)]+).*?'
    patron += '<img style="float:left" src="./[^/]+/([^\.]+).+?'
    patron += '<span[^>]+>([^<]+).*?'
    patron += '<img(.*?)onerror'

    if "Descarga:</h1>" in data1:
        list_showlinks = [('Online:', 'Online:</h1>(.*?)Descarga:</h1>'),
                          ('Download:', 'Descarga:</h1>(.*?)</section>')]
    else:
        list_showlinks = [('Online:', 'Online:</h1>(.*?)</section>')]

    for t in list_showlinks:
        data = scrapertools.find_single_match(data1, t[1])

        if data:
            itemlist.append(Item(title=t[0], text_color=color3, text_bold=True,
                                 folder=False, thumbnail=thumbnail_host))

            for redir, server, quality, langs in scrapertools.find_multiple_matches(data,
                                                                                    patron):  # , server, quality, langs
                redir = redir.split(",")
                url = redir[0][1:-1]
                id = redir[1][1:-1]
                # type = redir[2][1:-1]
                # url = url.split("','")[0] # [2] = 0 movies, [2] = 1 tvshows

                langs = scrapertools.find_multiple_matches(langs, 'src="./images/([^\.]+)')
                idioma = dic_langs.get(langs[0], langs[0])
                subtitulos = dic_langs.get(langs[1], langs[1])
                if subtitulos:
                    idioma = "%s (Sub: %s)" % (idioma, subtitulos)

                if server in dic_servers: server = dic_servers[server]

                itemlist.append(
                    item.clone(url=url, action="play", language=idioma, contentQuality=quality, server=server,
                               title="    %s: %s [%s]" % (server.capitalize(), idioma, quality)))

    if itemlist and config.get_videolibrary_support() and not "library" in item.extra:
        if item.contentType == 'movie':
            itemlist.append(item.clone(title="Añadir película a la videoteca",
                                       action="add_pelicula_to_library", text_color=color1,
                                       contentTitle=item.contentTitle, extra="library", thumbnail=thumbnail_host))
        else:
            # http://www.wopelis.com/serie.php?id=275641
            item.url = "http://www.wopelis.com/serie.php?id=" + id
            item.contentSeason = 0
            item.contentEpisodeNumber = 0
            # logger.error(item)
            itemlist.append(item.clone(title="Añadir esta serie a la videoteca",
                                       action="add_serie_to_library", extra="episodios###library",
                                       text_color=color1, thumbnail=thumbnail_host))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    # Buscamos video por servidor ...
    devuelve = servertools.findvideosbyserver(item.url, item.server)
    if not devuelve:
        # ...sino lo encontramos buscamos en todos los servidores disponibles
        devuelve = servertools.findvideos(item.url, skip=True)

    if devuelve:
        # logger.debug(devuelve)
        itemlist.append(Item(channel=item.channel, title=item.contentTitle, action="play", server=devuelve[0][2],
                             url=devuelve[0][1], thumbnail=item.thumbnail, folder=False))

    return itemlist


def downloadpage(url):
    cookievalue = config.get_setting("cookie", "wopelis")
    if not cookievalue:
        data = httptools.downloadpage(url).data
        cookievalue = get_cookie(data)

    headers = {'Cookie': '%s' % cookievalue}
    data = httptools.downloadpage(url, headers=headers).data
    if "Hola bienvenido" in data:
        cookievalue = get_cookie(data)
        headers = {'Cookie': '%s' % cookievalue}
        data = httptools.downloadpage(url, headers=headers).data

    return re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)


def get_cookie(data):
    import random
    cookievalue = ""
    cookiename = scrapertools.find_single_match(data, 'document.cookie\s*=\s*"([^"]+)"')
    cookiename = cookiename.replace("=", "")
    posible = scrapertools.find_single_match(data, 'var possible\s*=\s*"([^"]+)"')
    bloque = scrapertools.find_single_match(data, 'function cok(.*?);')
    lengths = scrapertools.find_multiple_matches(bloque, '([\S]{1}\d+)')
    for numero in lengths:
        if numero.startswith("("):
            for i in range(0, int(numero[1:])):
                cookievalue += posible[int(random.random() * len(posible))]
        else:
            cookievalue += numero[1:]

    cookievalue = "%s=%s" % (cookiename, cookievalue)
    config.set_setting("cookie", cookievalue, "wopelis")

    return cookievalue
