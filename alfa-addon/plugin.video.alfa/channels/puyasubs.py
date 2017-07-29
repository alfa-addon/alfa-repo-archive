# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item

__modo_grafico__ = config.get_setting('modo_grafico', 'puyasubs')
__perfil__ = config.get_setting('perfil', "puyasubs")

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00', '0xFFFE2E2E', '0xFFFFD700'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E', '0xFFFE2E2E', '0xFFFFD700'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE', '0xFFFE2E2E', '0xFFFFD700']]
if __perfil__ < 3:
    color1, color2, color3, color4, color5 = perfil[__perfil__]
else:
    color1 = color2 = color3 = color4 = color5 = ""


def mainlist(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, action="listado", title="Novedades Anime", thumbnail=item.thumbnail,
                         url="http://puya.si/?cat=4", text_color=color1))
    itemlist.append(Item(channel=item.channel, action="listado", title="Novedades Doramas", thumbnail=item.thumbnail,
                         url="http://puya.si/?cat=142", text_color=color1))
    itemlist.append(Item(channel=item.channel, action="", title="Descargas", text_color=color2))
    itemlist.append(Item(channel=item.channel, action="descargas", title="   Descargas Animes y Doramas en proceso",
                         thumbnail=item.thumbnail, url="http://puya.si/?page_id=25501", text_color=color1))
    itemlist.append(Item(channel=item.channel, action="descargas", title="   Descargas Animes Finalizados",
                         thumbnail=item.thumbnail, url="http://puya.si/?page_id=15388", text_color=color1))
    itemlist.append(Item(channel=item.channel, action="letra", title="   Descargas Animes Finalizados por Letra",
                         thumbnail=item.thumbnail, url="http://puya.si/?page_id=15388", text_color=color1))
    itemlist.append(Item(channel=item.channel, action="descargas", title="   Descargas Doramas Finalizados",
                         thumbnail=item.thumbnail, url="http://puya.si/?page_id=25507", text_color=color1))
    itemlist.append(Item(channel=item.channel, action="descargas", title="   Descargas Películas y Ovas",
                         thumbnail=item.thumbnail, url="http://puya.si/?page_id=25503", text_color=color1))
    itemlist.append(Item(channel=item.channel, action="torrents", title="Lista de Torrents", thumbnail=item.thumbnail,
                         url="https://www.frozen-layer.com/buscar/descargas", text_color=color1))

    itemlist.append(Item(channel=item.channel, action="search", title="Buscar anime/dorama/película",
                         thumbnail=item.thumbnail, url="http://puya.si/?s=", text_color=color3))

    itemlist.append(item.clone(title="Configurar canal", action="configuracion", text_color=color5, folder=False))
    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    texto = texto.replace(" ", "+")
    item.url += texto
    item.extra = "busqueda"
    try:
        return listado(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def listado(item):
    logger.info()

    itemlist = list()

    data = httptools.downloadpage(item.url).data
    bloques = scrapertools.find_multiple_matches(data, '<h2 class="entry-title">(.*?)</article>')
    patron = 'href="([^"]+)".*?>(.*?)</a>.*?(?:<span class="bl_categ">(.*?)|</span>)</footer>'
    for bloque in bloques:
        matches = scrapertools.find_multiple_matches(bloque, patron)
        for url, title, cat in matches:
            thumb = scrapertools.find_single_match(bloque, 'src="([^"]+)"')
            tipo = "tvshow"
            if item.extra == "busqueda" and cat:
                if "Anime" not in cat and "Dorama" not in cat and "Película" not in cat:
                    continue
                if "Película" in cat or "Movie" in title:
                    tipo = "movie"
            contenttitle = title.replace("[TeamDragon] ", "").replace("[PuyaSubs!] ", "").replace("[Puya+] ", "")
            contenttitle = scrapertools.find_single_match(contenttitle,
                                                          "(.*?)(?:\s+\[|\s+–|\s+&#8211;| Episodio| [0-9]{2,3})")
            filtro_tmdb = {"original_language": "ja"}.items()
            itemlist.append(Item(channel=item.channel, action="findvideos", url=url, title=title, thumbnail=thumb,
                                 contentTitle=contenttitle, show=contenttitle, contentType=tipo,
                                 infoLabels={'filtro': filtro_tmdb}, text_color=color1))

    if ("cat=4" in item.url or item.extra == "busqueda") and not item.extra == "novedades":
        from core import tmdb
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    next_page = scrapertools.find_single_match(data, "<span class='current'>.*?<a href='([^']+)'")
    if next_page:
        next_page = next_page.replace("&#038;", "&")
        itemlist.append(Item(channel=item.channel, action="listado", url=next_page, title=">> Página Siguiente",
                             thumbnail=item.thumbnail, extra=item.extra, text_color=color2))

    return itemlist


def descargas(item):
    logger.info()

    itemlist = list()
    if not item.pagina:
        item.pagina = 0

    data = httptools.downloadpage(item.url).data
    patron = '<li><a href="(http://puya.si/\?page_id=\d+|http://safelinking.net/[0-9A-z]+)">(.*?)</a>'
    if item.letra:
        bloque = scrapertools.find_single_match(data,
                                                '<li>(?:<strong>|)' + item.letra + '(?:</strong>|)</li>(.*?)</ol>')
        matches = scrapertools.find_multiple_matches(bloque, patron)
    else:
        matches = scrapertools.find_multiple_matches(data, patron)
    for url, title in matches[item.pagina:item.pagina + 20]:
        contenttitle = title.replace("[TeamDragon] ", "").replace("[PuyaSubs!] ", "") \
            .replace("[Puya+] ", "")
        contenttitle = re.sub(r'(\[[^\]]*\])', '', contenttitle).strip()
        filtro_tmdb = {"original_language": "ja"}.items()

        tipo = "tvshow"
        if "page_id=25503" in item.url:
            tipo = "movie"

        action = "findvideos"
        if "safelinking" in url:
            action = "extract_safe"
        itemlist.append(Item(channel=item.channel, action=action, url=url, title=title, contentTitle=contenttitle,
                             show=contenttitle, contentType=tipo, infoLabels={'filtro': filtro_tmdb},
                             text_color=color1))

    from core import tmdb
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    if len(matches) > item.pagina + 20:
        pagina = item.pagina + 20
        itemlist.append(Item(channel=item.channel, action="descargas", url=item.url, title=">> Página Siguiente",
                             thumbnail=item.thumbnail, pagina=pagina, letra=item.letra, text_color=color2))

    return itemlist


def letra(item):
    logger.info()

    itemlist = list()
    data = httptools.downloadpage(item.url).data
    patron = '<li>(?:<strong>|)([A-z#]{1})(?:</strong>|)</li>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for match in matches:
        itemlist.append(Item(channel=item.channel, title=match, action="descargas", letra=match, url=item.url,
                             thumbnail=item.thumbnail, text_color=color1))

    return itemlist


def torrents(item):
    logger.info()

    itemlist = list()
    if not item.pagina:
        item.pagina = 0

    post = "utf8=%E2%9C%93&busqueda=puyasubs&search=Buscar&tab=anime&con_seeds=con_seeds"
    data = httptools.downloadpage(item.url, post).data

    patron = "<td>.*?href='([^']+)' title='descargar torrent'>.*?title='informacion de (.*?)'.*?<td class='fecha'>.*?<td>(.*?)</td>" \
             ".*?<span class=\"stats\d+\">(\d+)</span>.*?<span class=\"stats\d+\">(\d+)</span>"
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, title, size, seeds, leechers in matches[item.pagina:item.pagina + 25]:
        contentTitle = title
        if "(" in contentTitle:
            contentTitle = contentTitle.split("(")[0]

        size = size.strip()
        filtro_tmdb = {"original_language": "ja"}.items()
        title += "  [COLOR %s][Semillas:%s[/COLOR]|[COLOR %s]Leech:%s[/COLOR]|%s]" % (
        color4, seeds, color5, leechers, size)
        url = "https://www.frozen-layer.com" + url

        itemlist.append(Item(channel=item.channel, action="play", url=url, title=title, contentTitle=contentTitle,
                             server="torrent", show=contentTitle, contentType="tvshow", text_color=color1,
                             infoLabels={'filtro': filtro_tmdb}))

    from core import tmdb
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    if len(matches) > item.pagina + 25:
        pagina = item.pagina + 25
        itemlist.append(Item(channel=item.channel, action="torrents", url=item.url, title=">> Página Siguiente",
                             thumbnail=item.thumbnail, pagina=pagina, text_color=color2))
    else:
        next_page = scrapertools.find_single_match(data, 'href="([^"]+)" rel="next"')
        if next_page:
            next_page = "https://www.frozen-layer.com" + next_page
            itemlist.append(Item(channel=item.channel, action="torrents", url=next_page, title=">> Página Siguiente",
                                 thumbnail=item.thumbnail, pagina=0, text_color=color2))

    return itemlist


def findvideos(item):
    logger.info()
    if item.infoLabels["tmdb_id"] and not item.infoLabels["plot"]:
        from core import tmdb
        tmdb.set_infoLabels_item(item, True, idioma_busqueda="en")

    itemlist = list()

    data = httptools.downloadpage(item.url).data
    idiomas = scrapertools.find_single_match(data, 'Subtitulo:\s*(.*?)<br />')
    calidades = ['720p', '1080p']
    torrentes = scrapertools.find_multiple_matches(data, '<a href="(https://www.frozen-layer.com/descargas[^"]+)"')
    if torrentes:
        for i, enlace in enumerate(torrentes):
            title = "Ver por Torrent   %s" % idiomas
            if ">720p" in data and ">1080p" in data:
                try:
                    title = "[%s] %s" % (calidades[i], title)
                except:
                    pass
            itemlist.append(item.clone(title=title, action="play", url=enlace, server="torrent"))

    onefichier = scrapertools.find_multiple_matches(data, '<a href="(https://1fichier.com/[^"]+)"')
    if onefichier:
        for i, enlace in enumerate(onefichier):
            title = "Ver por 1fichier   %s" % idiomas
            if ">720p" in data and ">1080p" in data:
                try:
                    title = "[%s] %s" % (calidades[i], title)
                except:
                    pass
            itemlist.append(item.clone(title=title, action="play", url=enlace, server="onefichier"))

    safelink = scrapertools.find_multiple_matches(data, '<a href="(http(?:s|)://safelinking.net/[^"]+)"')
    if safelink:
        for i, safe in enumerate(safelink):
            headers = [['Content-Type', 'application/json;charset=utf-8']]
            hash = safe.rsplit("/", 1)[1]
            post = jsontools.dump({"hash": hash})
            data_sf = httptools.downloadpage("http://safelinking.net/v1/protected", post, headers).data
            data_sf = jsontools.load(data_sf)

            for link in data_sf.get("links"):
                enlace = link["url"]
                domain = link["domain"]
                title = "Ver por %s" % domain
                action = "play"
                if "mega" in domain:
                    server = "mega"
                    if "/#F!" in enlace:
                        action = "carpeta"

                elif "1fichier" in domain:
                    server = "onefichier"
                    if "/dir/" in enlace:
                        action = "carpeta"

                title += "   %s" % idiomas
                if ">720p" in data and ">1080p" in data:
                    try:
                        title = "[%s]  %s" % (calidades[i], title)
                    except:
                        pass
                itemlist.append(item.clone(title=title, action=action, url=enlace, server=server))

    return itemlist


def carpeta(item):
    logger.info()
    itemlist = list()

    if item.server == "onefichier":
        data = httptools.downloadpage(item.url).data

        patron = '<tr>.*?<a href="([^"]+)".*?>(.*?)</a>.*?<td class="normal">(.*?)</td>'
        matches = scrapertools.find_multiple_matches(data, patron)
        for scrapedurl, scrapedtitle, size in matches:
            scrapedtitle += "  (%s)   [1fichier]" % size
            itemlist.append(Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action="play",
                                 server="onefichier", text_color=color1, thumbnail=item.thumbnail,
                                 infoLabels=item.infoLabels))
    else:
        from megaserver import Client
        from platformcode import platformtools

        c = Client(url=item.url)

        files = c.get_files()
        c.stop()
        for enlace in files:
            file_id = enlace["id"]
            itemlist.append(
                Item(channel=item.channel, title=enlace["name"], url=item.url + "|" + file_id, action="play",
                     server="mega", text_color=color1, thumbnail=item.thumbnail,
                     infoLabels=item.infoLabels))

    itemlist.sort(key=lambda item: item.title)
    return itemlist


def extract_safe(item):
    logger.info()
    if item.infoLabels["tmdb_id"] and not item.infoLabels["plot"]:
        from core import tmdb
        tmdb.set_infoLabels_item(item, True, idioma_busqueda="en")
    itemlist = list()

    hash = item.url.rsplit("/", 1)[1]
    headers = [['Content-Type', 'application/json;charset=utf-8']]
    post = jsontools.dump({"hash": hash})
    data = httptools.downloadpage("http://safelinking.net/v1/protected", post, headers).data
    data = jsontools.load(data)

    for link in data.get("links"):
        enlace = link["url"]
        domain = link["domain"]
        title = "Ver por %s" % domain
        action = "play"
        if "mega" in domain:
            server = "mega"
            if "/#F!" in enlace:
                action = "carpeta"

        elif "1fichier" in domain:
            server = "onefichier"
            if "/dir/" in enlace:
                action = "carpeta"

        itemlist.append(item.clone(title=title, action=action, url=enlace, server=server))

    return itemlist


def play(item):
    logger.info()
    itemlist = list()

    if item.server == "torrent" and "frozen" in item.url and not item.url.endswith(".torrent"):
        data = httptools.downloadpage(item.url).data
        enlace = scrapertools.find_single_match(data, "<div id='descargar_torrent'>.*?href='([^']+)'")
        if enlace:
            itemlist.append(item.clone(url=enlace))
    else:
        itemlist.append(item)

    return itemlist


def newest(categoria):
    logger.info()
    item = Item()
    try:
        item.url = "http://puya.si/?cat=4"
        item.extra = "novedades"
        itemlist = listado(item)

        if itemlist[-1].action == "listado":
            itemlist.pop()
        for it in itemlist:
            it.contentTitle = it.title

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
