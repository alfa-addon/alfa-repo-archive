# -*- coding: utf-8 -*-

import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools

host = "http://www.javtasty.com"


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(action="lista", title="Nuevos Vídeos", url=host + "/videos"))
    itemlist.append(item.clone(action="lista", title="Mejor Valorados", url=host + "/videos?o=tr"))
    itemlist.append(item.clone(action="lista", title="Más Vistos", url=host + "/videos?o=mv"))
    itemlist.append(item.clone(action="lista", title="Ordenados por duración", url=host + "/videos?o=lg"))
    itemlist.append(item.clone(action="categorias", title="Categorías", url=host + "/categories"))
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
    item.url = "%s/search?search_query=%s&search_type=videos" % (host, texto)
    item.extra = texto
    try:
        return lista(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def lista(item):
    logger.info()
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data

    action = "play"
    if config.get_setting("menu_info", "javtasty"):
        action = "menu_info"

    # Extrae las entradas
    patron = '<div class="well wellov well-sm".*?href="([^"]+)".*?data-original="([^"]+)" title="([^"]+)"(.*?)<div class="duration">(?:.*?</i>|)\s*([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, quality, duration in matches:
        scrapedurl = urlparse.urljoin(host, scrapedurl)
        scrapedtitle = scrapedtitle.strip()
        if duration:
            scrapedtitle = "%s - %s" % (duration.strip(), scrapedtitle)

        if '>HD<' in quality:
            scrapedtitle += "  [COLOR red][HD][/COLOR]"

        itemlist.append(item.clone(action=action, title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                                   fanart=scrapedthumbnail))

    # Extrae la marca de siguiente página
    next_page = scrapertools.find_single_match(data, 'href="([^"]+)" class="prevnext">')
    if next_page:
        next_page = next_page.replace("&amp;", "&")
        itemlist.append(item.clone(action="lista", title=">> Página Siguiente", url=next_page))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    # Descarga la pagina    
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas
    patron = '<div class="col-sm-4.*?href="([^"]+)".*?data-original="([^"]+)" title="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(host, scrapedurl)
        scrapedthumbnail = urlparse.urljoin(host, scrapedthumbnail)
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                                   fanart=scrapedthumbnail))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    videourl = scrapertools.find_single_match(data, "var video_sd\s*=\s*'([^']+)'")
    if videourl:
        itemlist.append(['.mp4 [directo]', videourl])
    videourl = scrapertools.find_single_match(data, "var video_hd\s*=\s*'([^']+)'")
    if videourl:
        itemlist.append(['.mp4 HD [directo]', videourl])

    if item.extra == "play_menu":
        return itemlist, data

    return itemlist


def menu_info(item):
    logger.info()
    itemlist = []

    video_urls, data = play(item.clone(extra="play_menu"))
    itemlist.append(item.clone(action="play", title="Ver -- %s" % item.title, video_urls=video_urls))

    bloque = scrapertools.find_single_match(data, '<div class="carousel-inner"(.*?)<div class="container">')
    matches = scrapertools.find_multiple_matches(bloque, 'src="([^"]+)"')
    for i, img in enumerate(matches):
        if i == 0:
            continue
        title = "Imagen %s" % (str(i))
        itemlist.append(item.clone(action="", title=title, thumbnail=img, fanart=img))

    return itemlist
