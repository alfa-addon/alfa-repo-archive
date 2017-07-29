# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import tmdb
from core.item import Item

host = "http://www.clasicofilm.com/"
# Configuracion del canal
__modo_grafico__ = config.get_setting('modo_grafico', 'clasicofilm')
__perfil__ = config.get_setting('perfil', 'clasicofilm')

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]

if __perfil__ - 1 >= 0:
    color1, color2, color3 = perfil[__perfil__ - 1]
else:
    color1 = color2 = color3 = ""


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(title="Películas", text_color=color2, action="", text_bold=True))
    itemlist.append(item.clone(action="peliculas", title="      Novedades",
                               url="http://www.clasicofilm.com/feeds/posts/summary?start-index=1&max-results=20&alt=json-in-script&callback=finddatepost",
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres"
                                         "/0/Directors%20Chair.png",
                               text_color=color1))
    itemlist.append(item.clone(action="generos", title="      Por géneros", url=host,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres"
                                         "/0/Genre.png",
                               text_color=color1))

    itemlist.append(item.clone(title="", action=""))
    itemlist.append(item.clone(action="search", title="Buscar...", text_color=color3))
    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", text_color="gold", folder=False))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()

    data = httptools.downloadpage(host).data
    cx = scrapertools.find_single_match(data, "var cx = '([^']+)'")
    texto = texto.replace(" ", "%20")
    item.url = "https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=20&hl=es&sig=0c3990ce7a056ed50667fe0c3873c9b6&cx=%s&q=%s&sort=&googlehost=www.google.com&start=0" % (
    cx, texto)

    try:
        return busqueda(item)
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
        if categoria == 'peliculas':
            item.url = "http://www.clasicofilm.com/feeds/posts/summary?start-index=1&max-results=20&alt=json-in-script&callback=finddatepost"
            item.action = "peliculas"
            itemlist = peliculas(item)

            if itemlist[-1].action == "peliculas":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    item.text_color = color2

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(data, 'finddatepost\((\{.*?\]\}\})\);')
    from core import jsontools
    data = jsontools.load(data)["feed"]

    for entry in data["entry"]:
        for link in entry["link"]:
            if link["rel"] == "alternate":
                title = link["title"]
                url = link["href"]
                break
        thumbnail = entry["media$thumbnail"]["url"].replace("s72-c/", "")
        try:
            title_split = re.split(r"\s*\((\d)", title, 1)
            year = title_split[1] + scrapertools.find_single_match(title_split[2], '(\d{3})\)')
            fulltitle = title_split[0]
        except:
            fulltitle = title
            year = ""
        if not "DVD" in title and not "HDTV" in title and not "HD-" in title:
            continue
        infolabels = {'year': year}
        new_item = item.clone(action="findvideos", title=title, fulltitle=fulltitle,
                              url=url, thumbnail=thumbnail, infoLabels=infolabels,
                              contentTitle=fulltitle, contentType="movie")
        itemlist.append(new_item)

    try:
        tmdb.set_infoLabels(itemlist, __modo_grafico__)
    except:
        pass

    actualpage = int(scrapertools.find_single_match(item.url, 'start-index=(\d+)'))
    totalresults = int(data["openSearch$totalResults"]["$t"])
    if actualpage + 20 < totalresults:
        url_next = item.url.replace("start-index=" + str(actualpage), "start-index=" + str(actualpage + 20))
        itemlist.append(Item(channel=item.channel, action=item.action, title=">> Página Siguiente", url=url_next))

    return itemlist


def busqueda(item):
    logger.info()
    itemlist = []
    item.text_color = color2

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    from core import jsontools
    data = jsontools.load(data)

    for entry in data["results"]:
        try:
            title = entry["richSnippet"]["metatags"]["ogTitle"]
            url = entry["richSnippet"]["metatags"]["ogUrl"]
            thumbnail = entry["richSnippet"]["metatags"]["ogImage"]
        except:
            continue

        try:
            title_split = re.split(r"\s*\((\d)", title, 1)
            year = title_split[1] + scrapertools.find_single_match(title_split[2], '(\d{3})\)')
            fulltitle = title_split[0]
        except:
            fulltitle = title
            year = ""
        if not "DVD" in title and not "HDTV" in title and not "HD-" in title:
            continue
        infolabels = {'year': year}
        new_item = item.clone(action="findvideos", title=title, fulltitle=fulltitle,
                              url=url, thumbnail=thumbnail, infoLabels=infolabels,
                              contentTitle=fulltitle, contentType="movie")
        itemlist.append(new_item)

    try:
        tmdb.set_infoLabels(itemlist, __modo_grafico__)
    except:
        pass

    actualpage = int(scrapertools.find_single_match(item.url, 'start=(\d+)'))
    totalresults = int(data["cursor"]["resultCount"])
    if actualpage + 20 <= totalresults:
        url_next = item.url.replace("start=" + str(actualpage), "start=" + str(actualpage + 20))
        itemlist.append(Item(channel=item.channel, action="busqueda", title=">> Página Siguiente", url=url_next))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    patron = '<b>([^<]+)</b><br/>\s*<script src="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedtitle, scrapedurl in matches:
        scrapedurl = scrapedurl.replace("max-results=500", "start-index=1&max-results=20") \
            .replace("recentpostslist", "finddatepost")
        itemlist.append(Item(channel=item.channel, action="peliculas", title=scrapedtitle, url=scrapedurl,
                             thumbnail=item.thumbnail, text_color=color3))

    itemlist.sort(key=lambda x: x.title)
    return itemlist


def findvideos(item):
    from core import servertools

    if item.infoLabels["tmdb_id"]:
        tmdb.set_infoLabels_item(item, __modo_grafico__)

    data = httptools.downloadpage(item.url).data
    iframe = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
    if "goo.gl/" in iframe:
        data += httptools.downloadpage(iframe, follow_redirects=False, only_headers=True).headers.get("location", "")
    itemlist = servertools.find_video_items(item, data)

    library_path = config.get_videolibrary_path()
    if config.get_videolibrary_support():
        title = "Añadir película a la videoteca"
        if item.infoLabels["imdb_id"] and not library_path.lower().startswith("smb://"):
            try:
                from core import filetools
                movie_path = filetools.join(config.get_videolibrary_path(), 'CINE')
                files = filetools.walk(movie_path)
                for dirpath, dirname, filename in files:
                    for f in filename:
                        if item.infoLabels["imdb_id"] in f and f.endswith(".nfo"):
                            from core import videolibrarytools
                            head_nfo, it = videolibrarytools.read_nfo(filetools.join(dirpath, dirname, f))
                            canales = it.library_urls.keys()
                            canales.sort()
                            if "clasicofilm" in canales:
                                canales.pop(canales.index("clasicofilm"))
                                canales.insert(0, "[COLOR red]clasicofilm[/COLOR]")
                            title = "Película ya en tu videoteca. [%s] ¿Añadir?" % ",".join(canales)
                            break
            except:
                import traceback
                logger.error(traceback.format_exc())

        itemlist.append(item.clone(action="add_pelicula_to_library", title=title))

    token_auth = config.get_setting("token_trakt", "tvmoviedb")
    if token_auth and item.infoLabels["tmdb_id"]:
        itemlist.append(item.clone(channel="tvmoviedb", title="[Trakt] Gestionar con tu cuenta", action="menu_trakt",
                                   extra="movie"))

    return itemlist
