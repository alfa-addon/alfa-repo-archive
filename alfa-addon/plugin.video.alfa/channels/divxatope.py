# -*- coding: utf-8 -*-

import re
import urllib
import urlparse

from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="menu", title="Películas", url="http://www.divxatope1.com/",
                         extra="Peliculas", folder=True))
    itemlist.append(
        Item(channel=item.channel, action="menu", title="Series", url="http://www.divxatope1.com", extra="Series",
             folder=True))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar..."))
    return itemlist


def menu(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # logger.info("data="+data)

    data = scrapertools.find_single_match(data, item.extra + "</a[^<]+<ul(.*?)</ul>")
    # logger.info("data="+data)

    patron = "<li><a.*?href='([^']+)'[^>]+>([^<]+)</a></li>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, thumbnail=thumbnail, plot=plot,
                             folder=True))
        if title != "Todas las Peliculas":
            itemlist.append(
                Item(channel=item.channel, action="alfabetico", title=title + " [A-Z]", url=url, thumbnail=thumbnail,
                     plot=plot, folder=True))

    if item.extra == "Peliculas":
        title = "4k UltraHD"
        url = "http://divxatope1.com/peliculas-hd/4kultrahd/"
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, thumbnail=thumbnail, plot=plot,
                             folder=True))
        itemlist.append(
            Item(channel=item.channel, action="alfabetico", title=title + " [A-Z]", url=url, thumbnail=thumbnail,
                 plot=plot,
                 folder=True))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://www.divxatope1.com/buscar/descargas"
    item.extra = urllib.urlencode({'q': texto})

    try:
        itemlist = lista(item)

        # Esta pagina coloca a veces contenido duplicado, intentamos descartarlo
        dict_aux = {}
        for i in itemlist:
            if not i.url in dict_aux:
                dict_aux[i.url] = i
            else:
                itemlist.remove(i)

        return itemlist
    # Se captura la excepci?n, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = "http://www.divxatope1.com/peliculas"

        elif categoria == 'series':
            item.url = "http://www.divxatope1.com/series"

        else:
            return []

        itemlist = lista(item)
        if itemlist[-1].title == ">> Página siguiente":
            itemlist.pop()

        # Esta pagina coloca a veces contenido duplicado, intentamos descartarlo
        dict_aux = {}
        for i in itemlist:
            if not i.url in dict_aux:
                dict_aux[i.url] = i
            else:
                itemlist.remove(i)

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    # return dict_aux.values()
    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url).data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")

    patron = '<ul class="alfabeto">(.*?)</ul>'
    data = scrapertools.get_match(data, patron)

    patron = '<a href="([^"]+)"[^>]+>([^>]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.upper()
        url = scrapedurl

        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url))

    return itemlist


def lista(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, post=item.extra).data
    # logger.info("data="+data)

    bloque = scrapertools.find_single_match(data, '(?:<ul class="pelilist">|<ul class="buscar-list">)(.*?)</ul>')
    patron = '<li[^<]+'
    patron += '<a href="([^"]+)".*?'
    patron += 'src="([^"]+)".*?'
    patron += '<h2[^>]*>(.*?)</h2.*?'
    patron += '(?:<strong[^>]*>|<span[^>]*>)(.*?)(?:</strong>|</span>)'

    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle, calidad in matches:
        scrapedtitle = scrapertools.htmlclean(scrapedtitle)
        title = scrapedtitle.strip()
        if scrapertools.htmlclean(calidad):
            title += " (" + scrapertools.htmlclean(calidad) + ")"
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        contentTitle = scrapertools.htmlclean(scrapedtitle).strip()
        patron = '([^<]+)<br>'
        matches = re.compile(patron, re.DOTALL).findall(calidad + '<br>')
        idioma = ''

        if "divxatope1.com/serie" in url:
            contentTitle = re.sub('\s+-|\.{3}$', '', contentTitle)
            capitulo = ''
            temporada = 0
            episodio = 0

            if len(matches) == 3:
                calidad = matches[0].strip()
                idioma = matches[1].strip()
                capitulo = matches[2].replace('Cap', 'x').replace('Temp', '').replace(' ', '')
                temporada, episodio = capitulo.strip().split('x')

            itemlist.append(Item(channel=item.channel, action="episodios", title=title, fulltitle=title, url=url,
                                 thumbnail=thumbnail, plot=plot, folder=True, contentTitle=contentTitle,
                                 language=idioma, contentSeason=int(temporada),
                                 contentEpisodeNumber=int(episodio), contentQuality=calidad))

        else:
            if len(matches) == 2:
                calidad = matches[0].strip()
                idioma = matches[1].strip()

            itemlist.append(Item(channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url,
                                 thumbnail=thumbnail, plot=plot, folder=True, contentTitle=contentTitle,
                                 language=idioma, contentThumbnail=thumbnail, contentQuality=calidad))

    next_page_url = scrapertools.find_single_match(data, '<li><a href="([^"]+)">Next</a></li>')
    if next_page_url != "":
        itemlist.append(Item(channel=item.channel, action="lista", title=">> Página siguiente",
                             url=urlparse.urljoin(item.url, next_page_url), folder=True))
    else:
        next_page_url = scrapertools.find_single_match(data,
                                                       '<li><input type="button" class="btn-submit" value="Siguiente" onClick="paginar..(\d+)')
        if next_page_url != "":
            itemlist.append(Item(channel=item.channel, action="lista", title=">> Página siguiente", url=item.url,
                                 extra=item.extra + "&pg=" + next_page_url, folder=True))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, post=item.extra).data
    # logger.info("data="+data)

    patron = '<div class="chap-desc"[^<]+'
    patron += '<a class="chap-title".*?href="([^"]+)" title="([^"]+)"[^<]+'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url, thumbnail=thumbnail,
                 plot=plot, folder=True))

    next_page_url = scrapertools.find_single_match(data, "<a class='active' href=[^<]+</a><a\s*href='([^']+)'")
    if next_page_url != "":
        itemlist.append(Item(channel=item.channel, action="episodios", title=">> Página siguiente",
                             url=urlparse.urljoin(item.url, next_page_url), folder=True))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    item.plot = scrapertools.find_single_match(data, '<div class="post-entry" style="height:300px;">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()
    item.contentPlot = item.plot

    link = scrapertools.find_single_match(data, 'href="http://(?:tumejorserie|tumejorjuego).*?link=([^"]+)"')
    if link != "":
        link = "http://www.divxatope1.com/" + link
        logger.info("torrent=" + link)
        itemlist.append(
            Item(channel=item.channel, action="play", server="torrent", title="Vídeo en torrent", fulltitle=item.title,
                 url=link, thumbnail=servertools.guess_server_thumbnail("torrent"), plot=item.plot, folder=False,
                 parentContent=item))

    patron = "<div class=\"box1\"[^<]+<img[^<]+</div[^<]+"
    patron += '<div class="box2">([^<]+)</div[^<]+'
    patron += '<div class="box3">([^<]+)</div[^<]+'
    patron += '<div class="box4">([^<]+)</div[^<]+'
    patron += '<div class="box5">(.*?)</div[^<]+'
    patron += '<div class="box6">([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist_ver = []
    itemlist_descargar = []

    for servername, idioma, calidad, scrapedurl, comentarios in matches:
        title = "Mirror en " + servername + " (" + calidad + ")" + " (" + idioma + ")"
        servername = servername.replace("uploaded", "uploadedto").replace("1fichier", "onefichier")
        if comentarios.strip() != "":
            title = title + " (" + comentarios.strip() + ")"
        url = urlparse.urljoin(item.url, scrapedurl)
        mostrar_server = servertools.is_server_enabled(servername)
        if mostrar_server:
            thumbnail = servertools.guess_server_thumbnail(title)
            plot = ""
            logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
            action = "play"
            if "partes" in title:
                action = "extract_url"
            new_item = Item(channel=item.channel, action=action, title=title, fulltitle=title, url=url,
                            thumbnail=thumbnail, plot=plot, parentContent=item)
            if comentarios.startswith("Ver en"):
                itemlist_ver.append(new_item)
            else:
                itemlist_descargar.append(new_item)

    for new_item in itemlist_ver:
        itemlist.append(new_item)

    for new_item in itemlist_descargar:
        itemlist.append(new_item)

    return itemlist


def extract_url(item):
    logger.info()

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        videoitem.title = "Enlace encontrado en " + videoitem.server + " (" + scrapertools.get_filename_from_url(
            videoitem.url) + ")"
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = item.channel

    return itemlist


def play(item):
    logger.info()

    if item.server != "torrent":
        itemlist = servertools.find_video_items(data=item.url)

        for videoitem in itemlist:
            videoitem.title = "Enlace encontrado en " + videoitem.server + " (" + scrapertools.get_filename_from_url(
                videoitem.url) + ")"
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = item.channel
    else:
        itemlist = [item]

    return itemlist
