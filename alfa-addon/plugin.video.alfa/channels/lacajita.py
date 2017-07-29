# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

__modo_grafico__ = config.get_setting("modo_grafico", "lacajita")
__perfil__ = config.get_setting("perfil", "lacajita")

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00', '0xFFFE2E2E', '0xFF088A08'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E', '0xFFFE2E2E', '0xFF088A08'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE', '0xFFFE2E2E', '0xFF088A08']]

if __perfil__ - 1 >= 0:
    color1, color2, color3, color4, color5 = perfil[__perfil__ - 1]
else:
    color1 = color2 = color3 = color4 = color5 = ""
host = "http://lacajita.xyz"


def mainlist(item):
    logger.info()
    itemlist = []
    item.text_color = color1

    itemlist.append(item.clone(title="Novedades DVD", action=""))
    item.text_color = color2
    itemlist.append(item.clone(title="     En Español", action="entradas", url=host + "/estrenos-dvd/es/", page=0))
    itemlist.append(item.clone(title="     En Latino", action="entradas", url=host + "/estrenos-dvd/la/", page=0))
    itemlist.append(item.clone(title="     En VOSE", action="entradas", url=host + "/estrenos-dvd/vos/", page=0))
    item.text_color = color1
    itemlist.append(item.clone(title="Estrenos", action=""))
    item.text_color = color2
    itemlist.append(item.clone(title="     En Español", action="entradas", url=host + "/estrenos/es/", page=0))
    itemlist.append(item.clone(title="     En Latino", action="entradas", url=host + "/estrenos/la/", page=0))
    itemlist.append(item.clone(title="     En VOSE", action="entradas", url=host + "/estrenos/vos/", page=0))
    item.text_color = color1
    itemlist.append(item.clone(title="Más Vistas", action="updated", url=host + "/listado-visto/", page=0))
    itemlist.append(item.clone(title="Actualizadas", action="updated", url=host + "/actualizado/", page=0))
    item.text_color = color5
    itemlist.append(item.clone(title="Por género", action="indices"))
    itemlist.append(item.clone(title="Buscar...", action="search", text_color=color4))
    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", text_color="gold", folder=False))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    try:
        item.url = "%s/search.php?q1=%s" % (host, texto)
        item.action = "busqueda"
        item.page = 0
        return busqueda(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def entradas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_single_match(data, '<ul class="nav navbar-nav">(.*?)</ul>')

    patron = "<li.*?href='([^']+)'.*?src='([^']+)'.*?>([^<]+)</p>(.*?)</button>"
    matches = scrapertools.find_multiple_matches(bloque, patron)
    matches_ = matches[item.page:item.page + 20]
    for scrapedurl, scrapedthumbnail, scrapedtitle, data_idioma in matches_:
        idiomas = []
        if "es.png" in data_idioma:
            idiomas.append("ESP")
        if "la.png" in data_idioma:
            idiomas.append("LAT")
        if "vos.png" in data_idioma:
            idiomas.append("VOSE")

        titulo = scrapedtitle
        if idiomas:
            titulo += "  [%s]" % "/".join(idiomas)

        scrapedurl = host + scrapedurl
        scrapedthumbnail = scrapedthumbnail.replace("/w342/", "/w500/")
        filtro_thumb = scrapedthumbnail.replace("https://image.tmdb.org/t/p/w500", "")
        filtro = {"poster_path": filtro_thumb}.items()
        itemlist.append(Item(channel=item.channel, action="findvideos", url=scrapedurl, title=titulo,
                             contentTitle=scrapedtitle, infoLabels={'filtro': filtro}, text_color=color2,
                             thumbnail=scrapedthumbnail, contentType="movie", fulltitle=scrapedtitle))

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    if len(matches) > item.page + 20:
        page = item.page + 20
        itemlist.append(item.clone(title=">> Página Siguiente", page=page, text_color=color3))

    return itemlist


def updated(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_single_match(data, '<ul class="nav navbar-nav">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, "<li.*?href='([^']+)'.*?src='([^']+)'.*?>([^<]+)</p>")
    matches_ = matches[item.page:item.page + 20]
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches_:
        if scrapedtitle == "Today":
            continue
        scrapedurl = host + scrapedurl
        scrapedthumbnail = scrapedthumbnail.replace("/w342/", "/w500/")
        filtro_thumb = scrapedthumbnail.replace("https://image.tmdb.org/t/p/w500", "")
        filtro = {"poster_path": filtro_thumb}.items()
        itemlist.append(Item(channel=item.channel, action="findvideos", url=scrapedurl, title=scrapedtitle,
                             contentTitle=scrapedtitle, infoLabels={'filtro': filtro}, text_color=color2,
                             thumbnail=scrapedthumbnail, contentType="movie", fulltitle=scrapedtitle))

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    if len(matches) > item.page + 20:
        page = item.page + 20
        itemlist.append(item.clone(title=">> Página Siguiente", page=page, text_color=color3))
    else:
        next = scrapertools.find_single_match(data, '<a href="([^"]+)">>>')
        if next:
            next = item.url + next
            itemlist.append(item.clone(title=">> Página Siguiente", page=0, url=next, text_color=color3))

    return itemlist


def busqueda(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_single_match(data, '<ul class="nav navbar-nav">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, "<li.*?href='([^']+)'.*?src='([^']+)'.*?>\s*([^<]+)</a>")
    matches_ = matches[item.page:item.page + 25]
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches_:
        scrapedurl = host + scrapedurl
        scrapedthumbnail = scrapedthumbnail.replace("/w342/", "/w500/")
        if re.search(r"\(\d{4}\)", scrapedtitle):
            title = scrapedtitle.rsplit("(", 1)[0]
            year = scrapertools.find_single_match(scrapedtitle, '\((\d{4})\)')
            infoLabels = {'year': year}
        else:
            title = scrapedtitle
            filtro_thumb = scrapedthumbnail.replace("https://image.tmdb.org/t/p/w500", "")
            filtro = {"poster_path": filtro_thumb}.items()
            infoLabels = {'filtro': filtro}
        itemlist.append(Item(channel=item.channel, action="findvideos", url=scrapedurl, title=scrapedtitle,
                             contentTitle=title, infoLabels=infoLabels, text_color=color2,
                             thumbnail=scrapedthumbnail, contentType="movie", fulltitle=title))

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    if len(matches) > item.page + 25:
        page = item.page + 25
        itemlist.append(item.clone(title=">> Página Siguiente", page=page, text_color=color3))
    else:
        next = scrapertools.find_single_match(data, '<a href="([^"]+)">>>')
        if next:
            next = item.url + next
            itemlist.append(item.clone(title=">> Página Siguiente", page=0, url=next, text_color=color3))

    return itemlist


def indices(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    matches = scrapertools.find_multiple_matches(data,
                                                 '<li><a href="([^"]+)"><i class="fa fa-bookmark-o"></i>\s*(.*?)</a>')
    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        itemlist.append(item.clone(action="updated", url=scrapedurl, title=scrapedtitle, page=0))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<div class="grid_content2 sno">.*?src="([^"]+)".*?href="([^"]+)".*?src=\'(.*?)(?:.png|.jpg)\'' \
             '.*?<span>.*?<span>(.*?)</span>.*?<span>(.*?)</span>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for idioma, url, servidor, calidad, detalle in matches:
        url = host + url
        servidor = servidor.rsplit("/", 1)[1]
        servidor = servidor.replace("uploaded", "uploadedto").replace("streamin.to", "streaminto")
        if "streamix" in servidor:
            servidor = "streamixcloud"
        try:
            servers_module = __import__("servers." + servidor)
            mostrar_server = servertools.is_server_enabled(servidor)
            if not mostrar_server:
                continue
        except:
            continue

        if "es.png" in idioma:
            idioma = "ESP"
        elif "la.png" in idioma:
            idioma = "LAT"
        elif "vos.png" in idioma:
            idioma = "VOSE"

        title = "%s - %s - %s" % (servidor, idioma, calidad)
        if detalle:
            title += " (%s)" % detalle

        itemlist.append(item.clone(action="play", url=url, title=title, server=servidor, text_color=color3))

    if item.extra != "findvideos" and config.get_videolibrary_support():
        itemlist.append(item.clone(title="Añadir película a la videoteca", action="add_pelicula_to_library",
                                   extra="findvideos", text_color="green"))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, 'window.open\("([^"]+)"')
    enlaces = servertools.findvideosbyserver(url, item.server)
    if enlaces:
        itemlist.append(item.clone(action="play", url=enlaces[0][1]))
    else:
        enlaces = servertools.findvideos(url, True)
        if enlaces:
            itemlist.append(item.clone(action="play", server=enlaces[0][2], url=enlaces[0][1]))

    return itemlist
