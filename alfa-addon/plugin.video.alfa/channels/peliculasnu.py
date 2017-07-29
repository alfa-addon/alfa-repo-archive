# -*- coding: utf-8 -*-

import urllib

from core import config
from core import httptools
from core import jsontools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

__modo_grafico__ = config.get_setting("modo_grafico", "peliculasnu")
__perfil__ = config.get_setting("perfil", "peliculasnu")

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]
color1, color2, color3 = perfil[__perfil__]
host = "http://peliculas.nu/"


def mainlist(item):
    logger.info()
    itemlist = []
    item.text_color = color1

    itemlist.append(item.clone(title="Novedades", action="entradas", url=host, fanart="http://i.imgur.com/c3HS8kj.png"))
    itemlist.append(item.clone(title="Más Vistas", action="entradas", url=host + "mas-vistas",
                               fanart="http://i.imgur.com/c3HS8kj.png"))
    itemlist.append(item.clone(title="Mejor Valoradas", action="entradas", url=host + "mejor-valoradas",
                               fanart="http://i.imgur.com/c3HS8kj.png"))
    item.text_color = color2
    itemlist.append(item.clone(title="En Español", action="entradas", url=host + "?s=Español",
                               fanart="http://i.imgur.com/c3HS8kj.png"))
    itemlist.append(item.clone(title="En Latino", action="entradas", url=host + "?s=Latino",
                               fanart="http://i.imgur.com/c3HS8kj.png"))
    itemlist.append(
        item.clone(title="En VOSE", action="entradas", url=host + "?s=VOSE", fanart="http://i.imgur.com/c3HS8kj.png"))
    item.text_color = color3
    itemlist.append(item.clone(title="Por género", action="indices", fanart="http://i.imgur.com/c3HS8kj.png"))
    itemlist.append(item.clone(title="Por letra", action="indices", fanart="http://i.imgur.com/c3HS8kj.png"))

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
    texto = texto.replace(" ", "+")
    try:
        item.url = "%s?s=%s" % (host, texto)
        item.action = "entradas"
        return entradas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
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
            item.url = host
            item.from_newest = True
            item.action = "entradas"
            itemlist = entradas(item)

            if itemlist[-1].action == "entradas":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def entradas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    patron = '<li class="TPostMv">.*?href="([^"]+)".*?src="([^"]+)".*?class="Title">([^<]+)<.*?' \
             '.*?"Date AAIco-date_range">(\d+).*?class="Qlty">([^<]+)<.*?<p class="Idioma(.*?)</p>'
    matches = scrapertools.find_multiple_matches(data, patron)
    if item.extra == "next":
        matches_ = matches[15:]
    else:
        matches_ = matches[:15]
    for scrapedurl, scrapedthumbnail, scrapedtitle, year, calidad, data_idioma in matches_:
        idiomas = []
        if "/espm" in data_idioma:
            idiomas.append("CAST")
        if "/latinom" in data_idioma:
            idiomas.append("LAT")
        if "/vosemi" in data_idioma:
            idiomas.append("VOSE")

        titulo = "%s  [%s]" % (scrapedtitle, calidad)
        if idiomas:
            titulo += " [%s]" % "/".join(idiomas)

        scrapedthumbnail = scrapedthumbnail.replace("-160x242", "")
        infolabels = {'year': year}
        itemlist.append(Item(channel=item.channel, action="findvideos", url=scrapedurl, title=titulo,
                             contentTitle=scrapedtitle, infoLabels=infolabels, text_color=color2,
                             thumbnail=scrapedthumbnail, contentType="movie", fulltitle=scrapedtitle))

    if not item.from_newest:
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    if not item.extra and len(matches) > 15:
        itemlist.append(item.clone(title=">> Página Siguiente", extra="next", text_color=color3))
    elif item.extra == "next":
        next_page = scrapertools.find_single_match(data, '<a class="nextpostslink".*?href="([^"]+)"')
        if next_page:
            itemlist.append(item.clone(title=">> Página Siguiente", url=next_page, text_color=color3, extra=""))

    return itemlist


def listado(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    patron = '<td class="MvTbImg">.*?href="([^"]+)".*?src="([^"]+)".*?<strong>([^<]+)<.*?' \
             '.*?<td>(\d+).*?class="Qlty">([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    if item.extra == "next":
        matches_ = matches[15:]
    else:
        matches_ = matches[:15]
    for scrapedurl, scrapedthumbnail, scrapedtitle, year, calidad in matches_:
        titulo = "%s  [%s]" % (scrapedtitle, calidad)
        scrapedthumbnail = scrapedthumbnail.replace("-55x85", "")
        infolabels = {'year': year}
        itemlist.append(Item(channel=item.channel, action="findvideos", url=scrapedurl, title=titulo,
                             contentTitle=scrapedtitle, infoLabels=infolabels, text_color=color2,
                             thumbnail=scrapedthumbnail, contentType="movie", fulltitle=scrapedtitle))

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    if not item.extra and len(matches) > 15:
        itemlist.append(item.clone(title=">> Página Siguiente", extra="next", text_color=color3))
    elif item.extra == "next":
        next_page = scrapertools.find_single_match(data, '<a class="nextpostslink".*?href="([^"]+)"')
        if next_page:
            itemlist.append(item.clone(title=">> Página Siguiente", url=next_page, text_color=color3, extra=""))

    return itemlist


def indices(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data
    if "letra" in item.title:
        action = "listado"
        bloque = scrapertools.find_single_match(data, '<ul class="AZList">(.*?)</ul>')
    else:
        action = "entradas"
        bloque = scrapertools.find_single_match(data, 'Géneros</a>(.*?)</ul>')
    matches = scrapertools.find_multiple_matches(bloque, '<li.*?<a href="([^"]+)">([^<]+)</a>')
    for scrapedurl, scrapedtitle in matches:
        itemlist.append(item.clone(action=action, url=scrapedurl, title=scrapedtitle))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    tmdb.set_infoLabels_item(item, __modo_grafico__)
    data = httptools.downloadpage(item.url).data

    if not item.infoLabels["plot"]:
        item.infoLabels["plot"] = scrapertools.find_single_match(data, '<div class="Description">.*?<p>(.*?)</p>')
    fanart = scrapertools.find_single_match(data, '<img class="TPostBg" src="([^"]+)"')
    if not item.fanart and fanart:
        item.fanart = fanart

    patron = '<li class="Button STPb.*?data-tipo="([^"]+)" data-playersource="([^"]+)".*?><span>.*?<span>(.*?)</span>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for tipo, source, title in matches:
        if tipo == "trailer":
            continue
        post = "source=%s&action=obtenerurl" % urllib.quote(source)
        headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': item.url}
        data_url = httptools.downloadpage(host + 'wp-admin/admin-ajax.php', post, headers=headers).data
        url = jsontools.load(data_url).get("url")

        if 'openload' in url:
            url = url + '|' + item.url

        title = "%s - %s" % ('%s', title)
        itemlist.append(item.clone(action="play", url=url, title=title, text_color=color3))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())

    if item.extra != "findvideos" and config.get_videolibrary_support():
        itemlist.append(item.clone(title="Añadir película a la videoteca", action="add_pelicula_to_library",
                                   extra="findvideos", text_color="green"))

    return itemlist


def play(item):
    logger.info()
    itemlist = []
    if "drive.php?v=" in item.url:
        if not item.url.startswith("http:") and not item.url.startswith("https:"):
            item.url = "http:" + item.url
        data = httptools.downloadpage(item.url, add_referer=True).data.replace("\\", "")

        subtitulo = scrapertools.find_single_match(data, "var subtitulo='([^']+)'")
        patron = '"label":\s*"([^"]+)","type":\s*"video/([^"]+)","(?:src|file)":\s*"([^"]+)"'
        matches = scrapertools.find_multiple_matches(data, patron)
        for calidad, extension, url in matches:
            url = url.replace(",", "%2C")
            title = ".%s %s [directo]" % (extension, calidad)
            itemlist.append([title, url, 0, subtitulo])
        try:
            itemlist.sort(key=lambda it: int(it[0].split(" ")[1].split("p")[0]))
        except:
            pass
    elif "metiscs" in item.url:
        import base64
        from lib import jsunpack

        item.url = item.url.replace("https:", "http:")
        if not item.url.startswith("http:"):
            item.url = "http:" + item.url

        data = httptools.downloadpage(item.url, add_referer=True).data
        str_encode = scrapertools.find_multiple_matches(data, '(?:\+|\()"([^"]+)"')
        data = base64.b64decode("".join(str_encode))
        packed = scrapertools.find_single_match(data, '(eval\(function.*?)(?:</script>|\}\)\))')
        if not packed:
            packed = data
        data_js = jsunpack.unpack(packed)

        subtitle = scrapertools.find_single_match(data_js, 'tracks:\[\{"file":"([^"]+)"')
        patron = '{"file":\s*"([^"]+)","label":\s*"([^"]+)","type":\s*"video/([^"]+)"'
        matches = scrapertools.find_multiple_matches(data_js, patron)
        for url, calidad, extension in matches:
            url = url.replace(",", "%2C")
            title = ".%s %s [directo]" % (extension, calidad)
            itemlist.insert(0, [title, url, 0, subtitle])
    else:
        return [item]

    return itemlist
