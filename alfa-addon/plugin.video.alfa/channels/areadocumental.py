# -*- coding: utf-8 -*-

import urllib

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core.item import Item

host = "http://www.area-documental.com"
__perfil__ = int(config.get_setting('perfil', "areadocumental"))

# Fijar perfil de color
perfil = [['', '', ''],
          ['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]
color1, color2, color3 = perfil[__perfil__]


def mainlist(item):
    logger.info()
    itemlist = []
    item.text_color = color1
    itemlist.append(item.clone(title="Novedades", action="entradas",
                               url="http://www.area-documental.com/resultados-reciente.php?buscar=&genero=",
                               fanart="http://i.imgur.com/Q7fsFI6.png"))
    itemlist.append(item.clone(title="Destacados", action="entradas",
                               url="http://www.area-documental.com/resultados-destacados.php?buscar=&genero=",
                               fanart="http://i.imgur.com/Q7fsFI6.png"))
    itemlist.append(item.clone(title="Categorías", action="cat", url="http://www.area-documental.com/index.php",
                               fanart="http://i.imgur.com/Q7fsFI6.png"))
    itemlist.append(item.clone(title="Ordenados por...", action="indice", fanart="http://i.imgur.com/Q7fsFI6.png"))

    itemlist.append(item.clone(title="Buscar...", action="search"))
    itemlist.append(item.clone(title="Configurar canal", action="configuracion", text_color="gold"))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    item.url = "http://www.area-documental.com/resultados.php?buscar=%s&genero=&x=0&y=0" % texto
    item.action = "entradas"
    try:
        itemlist = entradas(item)
        return itemlist
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
        if categoria == "documentales":
            item.url = "http://www.area-documental.com/resultados-reciente.php?buscar=&genero="
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


def indice(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Título", action="entradas",
                               url="http://www.area-documental.com/resultados-titulo.php?buscar=&genero="))
    itemlist.append(item.clone(title="Año", action="entradas",
                               url="http://www.area-documental.com/resultados-anio.php?buscar=&genero="))
    return itemlist


def cat(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_single_match(data, '<ul class="menu">(.*?)</nav>')
    matches = scrapertools.find_multiple_matches(bloque, "<li>.*?<a href='([^']+)'.*?>(.*?)</a>")
    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + "/" + scrapedurl
        if not "span" in scrapedtitle:
            scrapedtitle = "[COLOR gold]    **" + scrapedtitle + "**[/COLOR]"
            itemlist.append(item.clone(action="entradas", title=scrapedtitle, url=scrapedurl))
        else:
            scrapedtitle = scrapertools.htmlclean(scrapedtitle)
            itemlist.append(item.clone(action="entradas", title=scrapedtitle, url=scrapedurl))

    return itemlist


def entradas(item):
    logger.info()
    itemlist = []
    item.text_color = color2

    data = httptools.downloadpage(item.url).data
    data = scrapertools.unescape(data)
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"> ></a>')
    if next_page != "":
        data2 = scrapertools.unescape(httptools.downloadpage(host + next_page).data)
        data += data2
    else:
        data2 = ""
    data = data.replace("\n", "").replace("\t", "")

    patron = '<div id="peliculas">.*?<a href="([^"]+)".*?<img src="([^"]+)".*?' \
             'target="_blank">(.*?)</a>(.*?)<p>(.*?)</p>' \
             '.*?</strong>: (.*?)<strong>.*?</strong>(.*?)</div>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, year, scrapedplot, genero, extra in matches:
        infolab = {'plot': scrapedplot, 'genre': genero}
        scrapedurl = host + "/" + scrapedurl
        scrapedthumbnail = host + urllib.quote(scrapedthumbnail)
        title = scrapedtitle
        if "full_hd" in extra:
            scrapedtitle += " [COLOR gold][3D][/COLOR]"
        elif "720" in extra:
            scrapedtitle += " [COLOR gold][720p][/COLOR]"
        else:
            scrapedtitle += " [COLOR gold][SD][/COLOR]"

        year = year.replace("\xc2\xa0", "").replace(" ", "")
        if not year.isspace() and year != "":
            infolab['year'] = int(year)
            scrapedtitle += "  (" + year + ")"
        itemlist.append(item.clone(action="findvideos", title=scrapedtitle, fulltitle=title,
                                   url=scrapedurl, thumbnail=scrapedthumbnail, infoLabels=infolab))

    next_page = scrapertools.find_single_match(data2, '<a href="([^"]+)"> ></a>')
    if next_page:
        itemlist.append(item.clone(action="entradas", title=">> Página Siguiente", url=host + next_page,
                                   text_color=color3))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data

    subs = scrapertools.find_multiple_matches(data, 'file: "(/webvtt[^"]+)".*?label: "([^"]+)"')
    patron = 'file:\s*"(http://[^/]*/Videos/[^"]+)",\s*label:\s*"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, quality in matches:
        url += "|User-Agent=%s&Referer=%s" \
               % ("Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0", item.url)
        for url_sub, label in subs:
            url_sub = host + urllib.quote(url_sub)
            title = "Ver video en [[COLOR %s]%s[/COLOR]] Sub %s" % (color3, quality, label)
            itemlist.append(item.clone(action="play", server="directo", title=title,
                                       url=url, subtitle=url_sub, extra=item.url, calidad=quality))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    try:
        from core import filetools
        ficherosubtitulo = filetools.join(config.get_data_path(), 'subtitulo_areadocu.srt')
        if filetools.exists(ficherosubtitulo):
            try:
                filetools.remove(ficherosubtitulo)
            except IOError:
                logger.error("Error al eliminar el archivo " + ficherosubtitulo)
                raise

        data = httptools.downloadpage(item.subtitle, headers={'Referer': item.extra}).data
        filetools.write(ficherosubtitulo, data)
        subtitle = ficherosubtitulo
    except:
        subtitle = ""
        logger.error("Error al descargar el subtítulo")

    extension = item.url.rsplit("|", 1)[0][-4:]
    itemlist.append(['%s %s [directo]' % (extension, item.calidad), item.url, 0, subtitle])
    # itemlist.append(item.clone(subtitle=subtitle))

    return itemlist
