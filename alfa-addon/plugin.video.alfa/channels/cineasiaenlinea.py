# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

host = "http://www.cineasiaenlinea.com/"
# Configuracion del canal
__perfil__ = int(config.get_setting('perfil', 'cineasiaenlinea'))

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

    itemlist.append(item.clone(action="peliculas", title="Novedades", url=host + "archivos/peliculas",
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres"
                                         "/0/Directors%20Chair.png", text_color=color1))
    itemlist.append(item.clone(action="peliculas", title="Estrenos", url=host + "archivos/estrenos",
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres"
                                         "/0/Directors%20Chair.png", text_color=color1))
    itemlist.append(item.clone(action="indices", title="Por géneros", url=host,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres"
                                         "/0/Genre.png", text_color=color1))
    itemlist.append(item.clone(action="indices", title="Por país", url=host, text_color=color1))
    itemlist.append(item.clone(action="indices", title="Por año", url=host, text_color=color1))

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

    item.url = "%s?s=%s" % (host, texto.replace(" ", "+"))

    try:
        return peliculas(item)
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
            item.url = host + "archivos/peliculas"
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

    patron = '<h3><a href="([^"]+)">([^<]+)<.*?src="([^"]+)".*?<a rel="tag">([^<]+)<' \
             '.*?<a rel="tag">([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle, scrapedthumbnail, year, calidad in matches:
        title = re.sub(r' \((\d+)\)', '', scrapedtitle)
        scrapedtitle += "  [%s]" % calidad
        infolab = {'year': year}
        itemlist.append(item.clone(action="findvideos", title=scrapedtitle, url=scrapedurl,
                                   thumbnail=scrapedthumbnail, infoLabels=infolab,
                                   contentTitle=title, contentType="movie"))

    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" href="([^"]+)"')
    if next_page:
        itemlist.append(item.clone(title=">> Página Siguiente", url=next_page))

    return itemlist


def indices(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    logger.info(data)
    if "géneros" in item.title:
        bloque = scrapertools.find_single_match(data, '(?i)<h4>Peliculas por genero</h4>(.*?)</ul>')
        matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?>([^<]+)<')
    elif "año" in item.title:
        bloque = scrapertools.find_single_match(data, '(?i)<h4>Peliculas por Año</h4>(.*?)</select>')
        matches = scrapertools.find_multiple_matches(bloque, '<option value="([^"]+)">([^<]+)<')
    else:
        bloque = scrapertools.find_single_match(data, '(?i)<h4>Peliculas por Pais</h4>(.*?)</ul>')
        matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?>([^<]+)<')

    for scrapedurl, scrapedtitle in matches:
        if "año" in item.title:
            scrapedurl = "%sfecha-estreno/%s" % (host, scrapedurl)
        itemlist.append(Item(channel=item.channel, action="peliculas", title=scrapedtitle, url=scrapedurl,
                             thumbnail=item.thumbnail, text_color=color3))

    return itemlist


def findvideos(item):
    logger.info()
    data = httptools.downloadpage(item.url).data
    item.infoLabels["plot"] = scrapertools.find_single_match(data, '(?i)<h2>SINOPSIS.*?<p>(.*?)</p>')
    item.infoLabels["trailer"] = scrapertools.find_single_match(data, 'src="(http://www.youtube.com/embed/[^"]+)"')

    itemlist = servertools.find_video_items(item=item, data=data)
    for it in itemlist:
        it.thumbnail = item.thumbnail
        it.text_color = color2

    itemlist.append(item.clone(action="add_pelicula_to_library", title="Añadir película a la videoteca"))
    if item.infoLabels["trailer"]:
        folder = True
        if config.is_xbmc():
            folder = False
        itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Ver Trailer", folder=folder,
                                   contextual=not folder))

    return itemlist
