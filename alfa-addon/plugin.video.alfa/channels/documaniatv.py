# -*- coding: utf-8 -*-

import re
import urllib
import urlparse

from core import config
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item

host = "http://www.documaniatv.com/"
account = config.get_setting("documaniatvaccount", "documaniatv")

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'],
           ['Referer', host]]


def login():
    logger.info()

    user = config.get_setting("documaniatvuser", "documaniatv")
    password = config.get_setting("documaniatvpassword", "documaniatv")
    if user == "" or password == "":
        return True, ""

    data = scrapertools.cachePage(host, headers=headers)
    if "http://www.documaniatv.com/user/" + user in data:
        return False, user

    post = "username=%s&pass=%s&Login=Iniciar Sesión" % (user, password)
    data = scrapertools.cachePage("http://www.documaniatv.com/login.php", headers=headers, post=post)

    if "Nombre de usuario o contraseña incorrectas" in data:
        logger.error("login erróneo")
        return True, ""

    return False, user


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(item.clone(action="novedades", title="Novedades", url="http://www.documaniatv.com/newvideos.html"))
    itemlist.append(
        item.clone(action="categorias", title="Categorías y Canales", url="http://www.documaniatv.com/browse.html"))
    itemlist.append(item.clone(action="novedades", title="Top", url="http://www.documaniatv.com/topvideos.html"))
    itemlist.append(item.clone(action="categorias", title="Series Documentales",
                               url="http://www.documaniatv.com/top-series-documentales-html"))
    itemlist.append(item.clone(action="viendo", title="Viendo ahora", url="http://www.documaniatv.com"))
    itemlist.append(item.clone(action="", title=""))
    itemlist.append(item.clone(action="search", title="Buscar"))

    folder = False
    action = ""
    if account:
        error, user = login()
        if error:
            title = "Playlists Personales (Error en usuario y/o contraseña)"
        else:
            title = "Playlists Personales (Logueado)"
            action = "usuario"
            folder = True

    else:
        title = "Playlists Personales (Sin cuenta configurada)"
        user = ""

    url = "http://www.documaniatv.com/user/%s" % user
    itemlist.append(item.clone(title=title, action=action, url=url, folder=folder))
    itemlist.append(item.clone(title="Configurar canal...", text_color="gold", action="configuracion",
                               folder=False))
    return itemlist


def configuracion(item):
    from platformcode import platformtools
    platformtools.show_channel_settings()
    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("Container.Refresh")


def newest(categoria):
    itemlist = []
    item = Item()
    try:
        if categoria == 'documentales':
            item.url = "http://www.documaniatv.com/newvideos.html"
            itemlist = novedades(item)

            if itemlist[-1].action == "novedades":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info()
    data = scrapertools.cachePage(host, headers=headers)
    item.url = scrapertools.find_single_match(data, 'form action="([^"]+)"') + "?keywords=%s&video-id="
    texto = texto.replace(" ", "+")
    item.url = item.url % texto
    try:
        return novedades(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def novedades(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cachePage(item.url, headers=headers)
    # Saca el plot si lo tuviese
    scrapedplot = scrapertools.find_single_match(data, '<div class="pm-section-head">(.*?)</div>')
    if "<div" in scrapedplot:
        scrapedplot = ""
    else:
        scrapedplot = scrapertools.htmlclean(scrapedplot)
    bloque = scrapertools.find_multiple_matches(data, '<li class="col-xs-[\d] col-sm-[\d] col-md-[\d]">(.*?)</li>')

    if "Registrarse" in data or not account:
        for match in bloque:
            patron = '<span class="pm-label-duration">(.*?)</span>.*?<a href="([^"]+)"' \
                     '.*?title="([^"]+)".*?data-echo="([^"]+)"'
            matches = scrapertools.find_multiple_matches(match, patron)
            for duracion, scrapedurl, scrapedtitle, scrapedthumbnail in matches:
                contentTitle = scrapedtitle[:]
                scrapedtitle += "   [" + duracion + "]"
                if not scrapedthumbnail.startswith("data:image"):
                    scrapedthumbnail += "|" + headers[0][0] + "=" + headers[0][1]
                else:
                    scrapedthumbnail = item.thumbnail
                logger.debug(
                    "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
                itemlist.append(item.clone(action="play_", title=scrapedtitle, url=scrapedurl,
                                           thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot,
                                           fulltitle=scrapedtitle, contentTitle=contentTitle, folder=False))
    else:
        for match in bloque:
            patron = '<span class="pm-label-duration">(.*?)</span>.*?onclick="watch_later_add\(([\d]+)\)' \
                     '.*?<a href="([^"]+)".*?title="([^"]+)".*?data-echo="([^"]+)"'
            matches = scrapertools.find_multiple_matches(match, patron)
            for duracion, video_id, scrapedurl, scrapedtitle, scrapedthumbnail in matches:
                contentTitle = scrapedtitle[:]
                scrapedtitle += "   [" + duracion + "]"
                if not scrapedthumbnail.startswith("data:image"):
                    scrapedthumbnail += "|" + headers[0][0] + "=" + headers[0][1]
                else:
                    scrapedthumbnail = item.thumbnail
                logger.debug(
                    "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
                itemlist.append(item.clone(action="findvideos", title=scrapedtitle, url=scrapedurl,
                                           thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot,
                                           id=video_id,
                                           fulltitle=scrapedtitle, contentTitle=contentTitle))

    # Busca enlaces de paginas siguientes...
    try:
        next_page_url = scrapertools.get_match(data, '<a href="([^"]+)">&raquo;</a>')
        next_page_url = urlparse.urljoin(host, next_page_url)
        itemlist.append(item.clone(action="novedades", title=">> Página siguiente", url=next_page_url))
    except:
        logger.error("Siguiente pagina no encontrada")

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = scrapertools.cachePage(item.url, headers=headers)

    patron = '<div class="pm-li-category">.*?<a href="([^"]+)"' \
             '.*?<img src="([^"]+)".*?<h3>(?:<a.*?><span.*?>|)(.*?)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        if not scrapedthumbnail.startswith("data:image"):
            scrapedthumbnail += "|" + headers[0][0] + "=" + headers[0][1]
        else:
            scrapedthumbnail = item.thumbnail
        itemlist.append(item.clone(action="novedades", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                                   fanart=scrapedthumbnail))

    # Busca enlaces de paginas siguientes...
    next_page_url = scrapertools.find_single_match(data, '<a href="([^"]+)"><i class="fa fa-arrow-right">')
    if next_page_url != "":
        itemlist.append(item.clone(action="categorias", title=">> Página siguiente", url=next_page_url))

    return itemlist


def viendo(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cachePage(item.url, headers=headers)
    bloque = scrapertools.find_single_match(data, '<ul class="pm-ul-carousel-videos list-inline"(.*?)</ul>')
    patron = '<span class="pm-label-duration">(.*?)</span>.*?<a href="([^"]+)"' \
             '.*?title="([^"]+)".*?data-echo="([^"]+)"'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for duracion, scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle += "   [" + duracion + "]"
        if not scrapedthumbnail.startswith("data:image"):
            scrapedthumbnail += "|" + headers[0][0] + "=" + headers[0][1]
        else:
            scrapedthumbnail = item.thumbnail
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(item.clone(action="play_", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                                   fanart=scrapedthumbnail, fulltitle=scrapedtitle))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    # Se comprueba si el vídeo está ya en favoritos/ver más tarde
    url = "http://www.documaniatv.com/ajax.php?p=playlists&do=video-watch-load-my-playlists&video-id=%s" % item.id
    data = scrapertools.cachePage(url, headers=headers)
    data = jsontools.load(data)
    data = re.sub(r"\n|\r|\t", '', data['html'])

    itemlist.append(item.clone(action="play_", title=">> Reproducir vídeo", folder=False))
    if "kodi" in config.get_platform():
        folder = False
    else:
        folder = True
    patron = '<li data-playlist-id="([^"]+)".*?onclick="playlist_(\w+)_item' \
             '.*?<span class="pm-playlists-name">(.*?)</span>.*?' \
             '<span class="pm-playlists-video-count">(.*?)</span>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for playlist_id, playlist_action, playlist_title, video_count in matches:
        scrapedtitle = playlist_action.replace('remove', 'Eliminar de ').replace('add', 'Añadir a ')
        scrapedtitle += playlist_title + "   (" + video_count + ")"
        itemlist.append(item.clone(action="acciones_playlist", title=scrapedtitle, list_id=playlist_id,
                                   url="http://www.documaniatv.com/ajax.php", folder=folder))

    if "kodi" in config.get_platform():
        itemlist.append(item.clone(action="acciones_playlist", title="Crear una nueva playlist y añadir el documental",
                                   id=item.id, url="http://www.documaniatv.com/ajax.php", folder=folder))
    itemlist.append(item.clone(action="acciones_playlist", title="Me gusta", url="http://www.documaniatv.com/ajax.php",
                               folder=folder))

    return itemlist


def play_(item):
    logger.info()
    itemlist = []

    try:
        import xbmc
        if not xbmc.getCondVisibility('System.HasAddon(script.cnubis)'):
            from platformcode import platformtools
            platformtools.dialog_ok("Addon no encontrado",
                                    "Para ver vídeos alojados en cnubis necesitas tener su instalado su add-on",
                                    line3="Descárgalo en http://cnubis.com/kodi-pelisalacarta.html")
            return itemlist
    except:
        pass

    # Descarga la pagina
    data = scrapertools.cachePage(item.url, headers=headers)
    # Busca enlace directo
    video_url = scrapertools.find_single_match(data, 'class="embedded-video"[^<]+<iframe.*?src="([^"]+)"')
    if config.get_platform() == "plex" or config.get_platform() == "mediaserver":
        code = scrapertools.find_single_match(video_url, 'u=([A-z0-9]+)')
        url = "http://cnubis.com/plugins/mediaplayer/embeder/_embedkodi.php?u=%s" % code
        data = scrapertools.downloadpage(url, headers=headers)
        video_url = scrapertools.find_single_match(data, 'file\s*:\s*"([^"]+)"')
        itemlist.append(item.clone(action="play", url=video_url, server="directo"))
        return itemlist

    cnubis_script = xbmc.translatePath("special://home/addons/script.cnubis/default.py")
    xbmc.executebuiltin("XBMC.RunScript(%s, url=%s&referer=%s&title=%s)"
                        % (cnubis_script, urllib.quote_plus(video_url), urllib.quote_plus(item.url),
                           item.fulltitle))

    return itemlist


def usuario(item):
    logger.info()
    itemlist = []
    data = scrapertools.cachePage(item.url, headers=headers)
    profile_id = scrapertools.find_single_match(data, 'data-profile-id="([^"]+)"')
    url = "http://www.documaniatv.com/ajax.php?p=profile&do=profile-load-playlists&uid=%s" % profile_id

    data = scrapertools.cachePage(url, headers=headers)
    data = jsontools.load(data)
    data = data['html']

    patron = '<div class="pm-video-thumb">.*?src="([^"]+)".*?' \
             '<span class="pm-pl-items">(.*?)</span>(.*?)</div>' \
             '.*?<h3.*?href="([^"]+)".*?title="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedthumbnail, items, videos, scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("Historia", 'Historial')
        scrapedtitle += " (" + items + videos + ")"
        if "no-thumbnail" in scrapedthumbnail:
            scrapedthumbnail = ""
        else:
            scrapedthumbnail += "|" + headers[0][0] + "=" + headers[0][1]
        itemlist.append(item.clone(action="playlist", title=scrapedtitle, url=scrapedurl,
                                   thumbnail=scrapedthumbnail, fanart=scrapedthumbnail))

    return itemlist


def acciones_playlist(item):
    logger.info()
    itemlist = []
    if item.title == "Crear una nueva playlist y añadir el documental":
        from platformcode import platformtools
        texto = platformtools.dialog_input(heading="Introduce el título de la nueva playlist")
        if texto is not None:
            post = "p=playlists&do=create-playlist&title=%s&visibility=1&video-id=%s&ui=video-watch" % (texto, item.id)
            data = scrapertools.cachePage(item.url, headers=headers, post=post)
        else:
            return

    elif item.title != "Me gusta":
        if "Eliminar" in item.title:
            action = "remove-from-playlist"
        else:
            action = "add-to-playlist"
        post = "p=playlists&do=%s&playlist-id=%s&video-id=%s" % (action, item.list_id, item.id)
        data = scrapertools.cachePage(item.url, headers=headers, post=post)
    else:
        item.url = "http://www.documaniatv.com/ajax.php?vid=%s&p=video&do=like" % item.id
        data = scrapertools.cachePage(item.url, headers=headers)

    try:
        import xbmc
        from platformcode import platformtools
        platformtools.dialog_notification(item.title, "Se ha añadido/eliminado correctamente")
        xbmc.executebuiltin("Container.Refresh")
    except:
        itemlist.append(item.clone(action="", title="Se ha añadido/eliminado correctamente"))
        return itemlist


def playlist(item):
    logger.info()
    itemlist = []
    data = scrapertools.cachePage(item.url, headers=headers)
    patron = '<div class="pm-pl-list-index.*?src="([^"]+)".*?' \
             '<a href="([^"]+)".*?>(.*?)</a>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedthumbnail += "|" + headers[0][0] + "=" + headers[0][1]
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(item.clone(action="play_", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                                   fanart=scrapedthumbnail, fulltitle=scrapedtitle, folder=False))

    return itemlist
