# -*- coding: utf-8 -*-

import re
import urllib
import urlparse

from core import channeltools
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import platformtools

__channel__ = "pelispedia"

CHANNEL_HOST = "http://www.pelispedia.tv/"

# Configuracion del canal
try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
    __perfil__ = config.get_setting('perfil', __channel__)
except:
    __modo_grafico__ = True
    __perfil__ = 0

# Fijar perfil de color
perfil = [['0xFF6E2802', '0xFFFAA171', '0xFFE9D7940'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E64FE', '0xFF0404B4']]

if __perfil__ - 1 >= 0:
    color1, color2, color3 = perfil[__perfil__ - 1]
else:
    color1 = color2 = color3 = ""

parameters = channeltools.get_channel_parameters(__channel__)
fanart_host = parameters['fanart']
thumbnail_host = parameters['thumbnail']


def mainlist(item):
    logger.info()

    itemlist = list()
    itemlist.append(Item(channel=__channel__, title="Películas", text_color=color1, fanart=fanart_host, folder=False,
                         thumbnail=thumbnail_host, text_bold=True))
    itemlist.append(
        Item(channel=__channel__, action="listado", title="    Novedades", text_color=color2, viewcontent="movies",
             url=urlparse.urljoin(CHANNEL_HOST, "movies/all/"), fanart=fanart_host, extra="movies",
             viewmode="movie_with_plot",
             thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Directors%20Chair.png"))
    itemlist.append(
        Item(channel=__channel__, action="listado_alfabetico", title="     Por orden alfabético", text_color=color2,
             url=urlparse.urljoin(CHANNEL_HOST, "movies/all/"), extra="movies", fanart=fanart_host,
             viewmode="thumbnails",
             thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/A-Z.png"))
    itemlist.append(Item(channel=__channel__, action="listado_genero", title="     Por género", text_color=color2,
                         url=urlparse.urljoin(CHANNEL_HOST, "movies/all/"), extra="movies", fanart=fanart_host,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Genre.png"))
    itemlist.append(Item(channel=__channel__, action="listado_anio", title="     Por año", text_color=color2,
                         url=urlparse.urljoin(CHANNEL_HOST, "movies/all/"), extra="movies", fanart=fanart_host,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Year.png"))
    # itemlist.append(Item(channel=__channel__, action="search", title="     Buscar...", text_color=color2,
    #                      url=urlparse.urljoin(CHANNEL_HOST, "buscar/?s="), extra="movies", fanart=fanart_host))

    itemlist.append(Item(channel=__channel__, title="Series", text_color=color1, fanart=fanart_host, folder=False,
                         thumbnail=thumbnail_host, text_bold=True))
    itemlist.append(
        Item(channel=__channel__, action="listado", title="    Novedades", text_color=color2, viewcontent="tvshows",
             url=urlparse.urljoin(CHANNEL_HOST, "series/all/"), extra="serie", fanart=fanart_host,
             viewmode="movie_with_plot",
             thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/TV%20Series.png"))
    itemlist.append(Item(channel=__channel__, action="listado_alfabetico", title="     Por orden alfabético",
                         text_color=color2, extra="serie", fanart=fanart_host, viewmode="thumbnails",
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/A-Z.png"))
    itemlist.append(Item(channel=__channel__, action="listado_genero", title="     Por género", extra="serie",
                         text_color=color2, fanart=fanart_host, url=urlparse.urljoin(CHANNEL_HOST, "series/all/"),
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Genre.png"))
    itemlist.append(
        Item(channel=__channel__, action="listado_anio", title="     Por año", extra="serie", text_color=color2,
             fanart=fanart_host, url=urlparse.urljoin(CHANNEL_HOST, "series/all/"),
             thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Year.png"))
    # itemlist.append(Item(channel=__channel__, action="search", title="     Buscar...", text_color=color2,
    #                      url=urlparse.urljoin(CHANNEL_HOST, "series/buscar/?s="), extra="serie", fanart=fanart_host))

    itemlist.append(Item(channel=__channel__, title="", fanart=fanart_host, folder=False, thumbnail=thumbnail_host))

    itemlist.append(Item(channel=__channel__, action="settings", title="Configuración", text_color=color1,
                         fanart=fanart_host, text_bold=True,
                         thumbnail=config.get_thumb("thumb_setting_0.png")))

    return itemlist


def settings(item):
    return platformtools.show_channel_settings()


def listado_alfabetico(item):
    logger.info()

    itemlist = []

    for letra in '0ABCDEFGHIJKLMNOPQRSTUVWXYZ':

        cadena = "series/letra/"
        if item.extra == "movies":
            cadena = 'movies/all/?letra='
            viewcontent = "movies"
            if letra == '0':
                cadena += "Num"
            else:
                cadena += letra
        else:
            viewcontent = "tvshows"
            if letra == '0':
                cadena += "num/"
            else:
                cadena += letra + "/"

        itemlist.append(
            Item(channel=__channel__, action="listado", title=letra, url=urlparse.urljoin(CHANNEL_HOST, cadena),
                 extra=item.extra, text_color=color2, viewcontent=viewcontent,
                 thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/A-Z.png"))

    return itemlist


def listado_genero(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    if item.extra == "movies":
        cadena = 'movies/all/?gender='
        viewcontent = "movies"
        patron = '<select name="gender" id="genres" class="auxBtn1">.*?</select>'
        data = scrapertools.find_single_match(data, patron)
        patron = '<option value="([^"]+)".+?>(.*?)</option>'

    else:
        cadena = "series/genero/"
        viewcontent = "tvshows"
        patron = '<select id="genres">.*?</select>'
        data = scrapertools.find_single_match(data, patron)
        patron = '<option name="([^"]+)".+?>(.*?)</option>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for key, value in matches[1:]:
        cadena2 = cadena + key
        if item.extra != "movies":
            cadena2 += "/"

        itemlist.append(
            Item(channel=__channel__, action="listado", title=value, url=urlparse.urljoin(CHANNEL_HOST, cadena2),
                 extra=item.extra, text_color=color2, fanart=fanart_host, viewcontent=viewcontent,
                 thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Genre.png"))

    return itemlist


def listado_anio(item):
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    if item.extra == "movies":
        cadena = 'movies/all/?year='
        viewcontent = "movies"
        patron = '<select name="year" id="years" class="auxBtn1">.*?</select>'
        data = scrapertools.find_single_match(data, patron)
        patron = '<option value="([^"]+)"'
        titulo = 'Películas del año '
    else:
        cadena = "series/anio/"
        viewcontent = "tvshows"
        patron = '<select id="year">.*?</select>'
        data = scrapertools.find_single_match(data, patron)
        patron = '<option name="([^"]+)"'
        titulo = 'Series del año '

    matches = re.compile(patron, re.DOTALL).findall(data)

    for value in matches[1:]:
        cadena2 = cadena + value

        if item.extra != "movies":
            cadena2 += "/"

        itemlist.append(Item(channel=__channel__, action="listado", title=titulo + value, extra=item.extra,
                             url=urlparse.urljoin(CHANNEL_HOST, cadena2), text_color=color2, fanart=fanart_host,
                             thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Year.png",
                             viewcontent=viewcontent))

    return itemlist


def search(item, texto):
    # Funcion de busqueda desactivada
    logger.info("texto=%s" % texto)

    item.url = item.url + "%" + texto.replace(' ', '+') + "%"

    try:
        return listado(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = urlparse.urljoin(CHANNEL_HOST, "movies/all/")
            item.extra = "movies"

        else:
            return []

        itemlist = listado(item)
        if itemlist[-1].action == "listado":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

    return itemlist


def listado(item):
    logger.info()
    itemlist = []

    action = "findvideos"
    content_type = "movie"

    if item.extra == 'serie':
        action = "temporadas"
        content_type = "tvshow"

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    # logger.info("data -- {}".format(data))

    patron = '<li[^>]+><a href="([^"]+)" alt="([^<|\(]+).*?<img src="([^"]+).*?>.*?<span>\(([^)]+).*?' \
             '<p class="font12">(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedyear, scrapedplot in matches[:28]:
        title = "%s (%s)" % (scrapertools.unescape(scrapedtitle.strip()), scrapedyear)
        plot = scrapertools.entityunescape(scrapedplot)

        new_item = Item(channel=__channel__, title=title, url=urlparse.urljoin(CHANNEL_HOST, scrapedurl), action=action,
                        thumbnail=scrapedthumbnail, plot=plot, context="", extra=item.extra, text_color=color3,
                        contentType=content_type, fulltitle=title)

        if item.extra == 'serie':
            new_item.show = scrapertools.unescape(scrapedtitle.strip())
            # fix en algunos casos la url está mal
            new_item.url = new_item.url.replace(CHANNEL_HOST + "pelicula", CHANNEL_HOST + "serie")
        else:
            new_item.fulltitle = scrapertools.unescape(scrapedtitle.strip())
            new_item.infoLabels = {'year': scrapedyear}
            # logger.debug(new_item.tostring())

        itemlist.append(new_item)

    # Obtenemos los datos basicos de todas las peliculas mediante multihilos
    tmdb.set_infoLabels(itemlist, __modo_grafico__)

    # numero de registros que se muestran por página, se fija a 28 por cada paginación
    if len(matches) >= 28:

        file_php = "666more"
        tipo_serie = ""

        if item.extra == "movies":
            anio = scrapertools.find_single_match(item.url, "(?:year=)(\w+)")
            letra = scrapertools.find_single_match(item.url, "(?:letra=)(\w+)")
            genero = scrapertools.find_single_match(item.url, "(?:gender=|genre=)(\w+)")
            params = "letra=%s&year=%s&genre=%s" % (letra, anio, genero)

        else:
            tipo2 = scrapertools.find_single_match(item.url, "(?:series/|tipo2=)(\w+)")
            tipo_serie = "&tipo=serie"

            if tipo2 != "all":
                file_php = "letra"
                tipo_serie += "&tipo2=" + tipo2

            genero = ""
            if tipo2 == "anio":
                genero = scrapertools.find_single_match(item.url, "(?:anio/|genre=)(\w+)")
            if tipo2 == "genero":
                genero = scrapertools.find_single_match(item.url, "(?:genero/|genre=)(\w+)")
            if tipo2 == "letra":
                genero = scrapertools.find_single_match(item.url, "(?:letra/|genre=)(\w+)")

            params = "genre=%s" % genero

        url = "http://www.pelispedia.tv/api/%s.php?rangeStart=28&rangeEnd=28%s&%s" % (file_php, tipo_serie, params)

        if "rangeStart" in item.url:
            ant_inicio = scrapertools.find_single_match(item.url, "rangeStart=(\d+)&")
            inicio = str(int(ant_inicio) + 28)
            url = item.url.replace("rangeStart=" + ant_inicio, "rangeStart=" + inicio)

        itemlist.append(Item(channel=__channel__, action="listado", title=">> Página siguiente", extra=item.extra,
                             url=url, thumbnail=thumbnail_host, fanart=fanart_host, text_color=color2))

    return itemlist


def episodios(item):
    logger.info()

    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    patron = '<li class="clearfix gutterVertical20"><a href="([^"]+)".*?><small>(.*?)</small>.*?' \
             '<span class.+?>(.*?)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedname in matches:
        # logger.info("scrap {}".format(scrapedtitle))
        patron = 'Season\s+(\d),\s+Episode\s+(\d+)'
        match = re.compile(patron, re.DOTALL).findall(scrapedtitle)
        season, episode = match[0]

        if 'season' in item.infoLabels and int(item.infoLabels['season']) != int(season):
            continue

        title = "%sx%s: %s" % (season, episode.zfill(2), scrapertools.unescape(scrapedname))
        new_item = item.clone(title=title, url=scrapedurl, action="findvideos", text_color=color3, fulltitle=title,
                              contentType="episode")
        if 'infoLabels' not in new_item:
            new_item.infoLabels = {}

        new_item.infoLabels['season'] = season
        new_item.infoLabels['episode'] = episode.zfill(2)

        itemlist.append(new_item)

    # TODO no hacer esto si estamos añadiendo a la videoteca
    if not item.extra:
        # Obtenemos los datos de todos los capitulos de la temporada mediante multihilos
        tmdb.set_infoLabels(itemlist, __modo_grafico__)
        for i in itemlist:
            if i.infoLabels['title']:
                # Si el capitulo tiene nombre propio añadirselo al titulo del item
                i.title = "%sx%s %s" % (i.infoLabels['season'], i.infoLabels['episode'], i.infoLabels['title'])
            if i.infoLabels.has_key('poster_path'):
                # Si el capitulo tiene imagen propia remplazar al poster
                i.thumbnail = i.infoLabels['poster_path']

    itemlist.sort(key=lambda it: int(it.infoLabels['episode']),
                  reverse=config.get_setting('orden_episodios', __channel__))

    # Opción "Añadir esta serie a la videoteca"
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=__channel__, title="Añadir esta serie a la videoteca", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=item.show, category="Series",
                             text_color=color1, thumbnail=thumbnail_host, fanart=fanart_host))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    if not item.fanart:
        patron = '<div class="hero-image"><img src="([^"]+)"'
        item.fanart = scrapertools.find_single_match(data, patron)

    patron = '<h3 class="pt15 pb15 dBlock clear seasonTitle">([^<]+).*?'
    patron += '<div class="bpM18 bpS25 mt15 mb20 noPadding"><figure><img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 1:
        for scrapedseason, scrapedthumbnail in matches:
            temporada = scrapertools.find_single_match(scrapedseason, '(\d+)')
            new_item = item.clone(text_color=color2, action="episodios", season=temporada, thumbnail=scrapedthumbnail)
            new_item.infoLabels['season'] = temporada
            new_item.extra = ""
            itemlist.append(new_item)

        # Obtenemos los datos de todas las temporadas de la serie mediante multihilos
        tmdb.set_infoLabels(itemlist, __modo_grafico__)
        for i in itemlist:
            i.title = "%s. %s" % (i.infoLabels['season'], i.infoLabels['tvshowtitle'])
            if i.infoLabels['title']:
                # Si la temporada tiene nombre propio añadirselo al titulo del item
                i.title += " - %s" % (i.infoLabels['title'])
            if i.infoLabels.has_key('poster_path'):
                # Si la temporada tiene poster propio remplazar al de la serie
                i.thumbnail = i.infoLabels['poster_path']

        itemlist.sort(key=lambda it: it.title)

        # Opción "Añadir esta serie a la videoteca"
        if config.get_videolibrary_support() and len(itemlist) > 0:
            itemlist.append(Item(channel=__channel__, title="Añadir esta serie a la videoteca", url=item.url,
                                 action="add_serie_to_library", extra="episodios", show=item.show, category="Series",
                                 text_color=color1, thumbnail=thumbnail_host, fanart=fanart_host))

        return itemlist
    else:
        return episodios(item)


def findvideos(item):
    logger.info()
    logger.info("item.url %s" % item.url)
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    patron = '<iframe src=".+?id=(\d+)'
    key = scrapertools.find_single_match(data, patron)
    url = CHANNEL_HOST + 'api/iframes.php?id=%s&update1.1' % key

    headers = dict()
    headers["Referer"] = item.url
    data = httptools.downloadpage(url, headers=headers).data

    # Descarta la opción descarga que es de publicidad
    patron = '<a href="(?!http://go.ad2up.com)([^"]+)".+?><img src="/api/img/([^.]+)'
    matches = scrapertools.find_multiple_matches(data, patron)

    for scrapedurl, scrapedtitle in matches:
        # En algunos vídeos hay opción flash "vip" con varias calidades
        if "api/vip.php" in scrapedurl:
            data_vip = httptools.downloadpage(scrapedurl).data
            patron = '<a href="([^"]+)".+?><img src="/api/img/([^.]+).*?<span class="text">([^<]+)<'
            matches_vip = re.compile(patron, re.DOTALL).findall(data_vip)
            for url, titlevip, calidad in matches_vip:
                title = "Ver vídeo en [" + titlevip + "] " + calidad
                itemlist.append(item.clone(title=title, url=url, action="play"))
        # fix se ignora esta url ya que no devuelve videos
        elif "http://www.pelispedia.tv/Pe_Player_Html6/index.php?" in scrapedurl:
            continue
        else:
            title = "Ver vídeo en [" + scrapedtitle + "]"
            new_item = item.clone(title=title, url=scrapedurl, action="play", extra=item.url, referer=url)
            itemlist.append(new_item)

    # Opción "Añadir esta pelicula a la videoteca"
    if item.extra == "movies" and config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=__channel__, title="Añadir esta película a la videoteca", url=item.url,
                             infoLabels=item.infoLabels, action="add_pelicula_to_library", extra="findvideos",
                             fulltitle=item.title, text_color=color2))

    return itemlist


def play(item):
    logger.info("url=%s" % item.url)

    itemlist = []

    subtitle = ""

    # html5 - http://www.pelispedia.vip
    if item.url.startswith("http://www.pelispedia.vip"):

        headers = dict()
        headers["Referer"] = item.referer
        data = httptools.downloadpage(item.url, headers=headers).data
        data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)

        from lib import jsunpack
        match = scrapertools.find_single_match(data, '\.</div><script type="text/rocketscript">(.*?)</script>')
        data = jsunpack.unpack(match)
        data = data.replace("\\'", "'")

        subtitle = scrapertools.find_single_match(data, "tracks:\[{file:'([^']+)',label:'Spanish'")
        media_urls = scrapertools.find_multiple_matches(data, "{file:'(.+?)',label:'(.+?)',type:'video/mp4'")

        # la calidad más baja tiene que ir primero
        media_urls = sorted(media_urls, key=lambda k: k[1])

        if len(media_urls) > 0:
            for url, desc in media_urls:
                itemlist.append([desc, url, 0, subtitle])

    # otro html5 - https://pelispedia.co/ver/f.php
    elif item.url.startswith("https://pelispedia.co/ver/f.php"):

        headers = dict()
        headers["Referer"] = item.referer
        data = httptools.downloadpage(item.url, headers=headers).data

        sub = scrapertools.find_single_match(data, "subtitulo='([^']+)'")
        data_sub = httptools.downloadpage(sub).data
        subtitle = save_sub(data_sub)

        from lib import jsunpack
        match = scrapertools.find_single_match(data, '<script type="text/rocketscript">(.*?)</script>')
        data = jsunpack.unpack(match)
        data = data.replace("\\'", "'")

        media_urls = scrapertools.find_multiple_matches(data, "{file:'(.+?)',label:'(.+?)'")

        # la calidad más baja tiene que ir primero
        media_urls = sorted(media_urls, key=lambda k: k[1])

        if len(media_urls) > 0:
            for url, desc in media_urls:
                itemlist.append([desc, url, 0, subtitle])

    # NUEVO
    # otro html5 - http://player.pelispedia.tv/ver?v=
    elif item.url.startswith("http://player.pelispedia.tv/ver?v="):
        _id = scrapertools.find_single_match(item.url, 'ver\?v=(.+?)$')

        headers = dict()
        headers["Referer"] = item.referer
        data = httptools.downloadpage(item.url, headers=headers).data

        sub = scrapertools.find_single_match(data, 'var parametros = "\?pic=20&id=([^&]+)&sub=ES";')
        sub = "http://player.pelispedia.tv/cdn" + sub
        data_sub = httptools.downloadpage(sub).data
        subtitle = save_sub(data_sub)

        csrf_token = scrapertools.find_single_match(data, '<meta name="csrf-token" content="([^"]+)">')

        ct = ""
        iv = ""
        s = ""
        pre_token = '{"ct": %s,"iv": %s,"s":%s}' % (ct, iv, s)

        import base64
        token = base64.b64encode(pre_token)

        url = "http://player.pelispedia.tv/template/protected.php"
        post = "fv=%s&url=%s&sou=%s&token=%s" % ("0", _id, "pic", token)
                                                  # eyJjdCI6IkVNYUd3Z2IwS2szSURzSGFGdkxGWlE9PSIsIml2IjoiZDI0NzhlYzU0OTZlYTJkNWFlOTFkZjAzZTVhZTNlNmEiLCJzIjoiOWM3MTM3MjNhMTkyMjFiOSJ9
        data = httptools.downloadpage(url, post=post).data

        logger.debug("datito %s " % data)

        media_urls = scrapertools.find_multiple_matches(data, '"url":"([^"]+)".*?"width":([^,]+),')

        # la calidad más baja tiene que ir primero
        media_urls = sorted(media_urls, key=lambda k: int(k[1]))

        if len(media_urls) > 0:
            for url, desc in media_urls:
                itemlist.append([desc, url, 0, subtitle])

    # netu
    elif item.url.startswith("http://www.pelispedia.tv/netu.html?"):
        url = item.url.replace("http://www.pelispedia.tv/netu.html?url=", "")

        from servers import netutv
        media_urls = netutv.get_video_url(urllib.unquote(url))
        itemlist.append(media_urls[0])

    # flash
    elif item.url.startswith("http://www.pelispedia.tv"):
        key = scrapertools.find_single_match(item.url, 'index.php\?id=([^&]+).+?sub=([^&]+)&.+?imagen=([^&]+)')

        # if len(key) > 2:
        #     thumbnail = key[2]
        if key[1] != "":
            url_sub = "http://www.pelispedia.tv/sub/%s.srt" % key[1]
            data_sub = httptools.downloadpage(url_sub).data
            subtitle = save_sub(data_sub)

        url = "http://www.pelispedia.tv/gkphp_flv/plugins/gkpluginsphp.php"
        post = "link=" + urllib.quote(key[0])

        data = httptools.downloadpage(url, post=post).data

        media_urls = scrapertools.find_multiple_matches(data, 'link":"([^"]+)","type":"([^"]+)"')

        # la calidad más baja tiene que ir primero
        media_urls = sorted(media_urls, key=lambda k: k[1])

        if len(media_urls) > 0:
            for url, desc in media_urls:
                url = url.replace("\\", "")
                itemlist.append([desc, url, 0, subtitle])

    # openload
    elif item.url.startswith("https://load.pelispedia.co/embed/openload.co"):

        url = item.url.replace("/embed/", "/stream/")
        data = httptools.downloadpage(url).data
        url = scrapertools.find_single_match(data, '<meta name="og:url" content="([^"]+)"')

        from servers import openload
        media_urls = openload.get_video_url(url)
        itemlist.append(media_urls[0])

    # raptu
    elif item.url.startswith("https://load.pelispedia.co/embed/raptu.com"):
        url = item.url.replace("/embed/", "/stream/")
        data = httptools.downloadpage(url).data
        url = scrapertools.find_single_match(data, '<meta property="og:url" content="([^"]+)"')
        from servers import raptu
        media_urls = raptu.get_video_url(url)
        if len(media_urls) > 0:
            for desc, url, numero, subtitle in media_urls:
                itemlist.append([desc, url, numero, subtitle])

    else:
        itemlist = servertools.find_video_items(data=item.url)
        for videoitem in itemlist:
            videoitem.title = item.title
            videoitem.channel = __channel__

    return itemlist


def save_sub(data):
    import os
    try:
        ficherosubtitulo = os.path.join(config.get_data_path(), 'subtitulo_pelispedia.srt')
        if os.path.exists(ficherosubtitulo):
            try:
                os.remove(ficherosubtitulo)
            except IOError:
                logger.error("Error al eliminar el archivo " + ficherosubtitulo)
                raise

        fichero = open(ficherosubtitulo, "wb")
        fichero.write(data)
        fichero.close()
        subtitle = ficherosubtitulo
    except:
        subtitle = ""
        logger.error("Error al descargar el subtítulo")

    return subtitle
