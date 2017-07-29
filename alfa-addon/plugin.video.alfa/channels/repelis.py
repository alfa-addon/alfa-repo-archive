# -*- coding: utf-8 -*-

import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


# Main list manual
def mainlist(item):
    logger.info()
    itemlist = []

    item.url = "http://www.repelis.tv/pag/1"

    mifan = "http://www.psicocine.com/wp-content/uploads/2013/08/Bad_Robot_Logo.jpg"

    itemlist.append(Item(channel=item.channel, action="menupelis", title="Peliculas", url="http://www.repelis.tv/pag/1",
                         thumbnail="http://www.gaceta.es/sites/default/files/styles/668x300/public/metro_goldwyn_mayer_1926-web.png?itok=-lRSR9ZC",
                         fanart=mifan))
    itemlist.append(Item(channel=item.channel, action="menuestre", title="Estrenos",
                         url="http://www.repelis.tv/archivos/estrenos/pag/1",
                         thumbnail="http://t0.gstatic.com/images?q=tbn:ANd9GcS4g68rmeLQFuX7iCrPwd00FI_OlINZXCYXEFrJHTZ0VSHefIIbaw",
                         fanart=mifan))
    itemlist.append(
        Item(channel=item.channel, action="menudesta", title="Destacadas", url="http://www.repelis.tv/pag/1",
             thumbnail="http://img.irtve.es/v/1074982/", fanart=mifan))
    itemlist.append(Item(channel=item.channel, action="todaspelis", title="Proximos estrenos",
                         url="http://www.repelis.tv/archivos/proximos-estrenos/pag/1",
                         thumbnail="https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcTpsRC-GTYzCqhor2gIDfAB61XeymwgXWSVBHoRAKs2c5HAn29f&reload=on",
                         fanart=mifan))
    itemlist.append(
        Item(channel=item.channel, action="todaspelis", title="Todas las Peliculas", url="http://www.repelis.tv/pag/1",
             thumbnail="https://freaksociety.files.wordpress.com/2012/02/logos-cine.jpg", fanart=mifan))

    if config.get_setting("adult_mode") != 0:
        itemlist.append(Item(channel=item.channel, action="todaspelis", title="Eroticas +18",
                             url="http://www.repelis.tv/genero/eroticas/pag/1",
                             thumbnail="http://www.topkamisetas.com/catalogo/images/TB0005.gif",
                             fanart="http://www.topkamisetas.com/catalogo/images/TB0005.gif"))
        # Quito la busqueda por aÃ±o si no esta enabled el adultmode, porque no hay manera de filtrar los enlaces eroticos72
        itemlist.append(
            Item(channel=item.channel, action="poranyo", title="Por Año", url="http://www.repelis.tv/anio/2016",
                 thumbnail="http://t3.gstatic.com/images?q=tbn:ANd9GcSkxiYXdBcI0cvBLsb_nNlz_dWXHRl2Q-ER9dPnP1gNUudhrqlR",
                 fanart=mifan))

    # Por categoria si que filtra la categoria de eroticos
    itemlist.append(Item(channel=item.channel, action="porcateg", title="Por Categoria",
                         url="http://www.repelis.tv/genero/accion/pag/1",
                         thumbnail="http://www.logopro.it/blog/wp-content/uploads/2013/07/categoria-sigaretta-elettronica.png",
                         fanart=mifan))
    itemlist.append(
        Item(channel=item.channel, action="search", title="Buscar...", url="http://www.repelis.tv/search/?s=",
             thumbnail="http://thumbs.dreamstime.com/x/buscar-pistas-13159747.jpg", fanart=mifan))

    return itemlist


# Peliculas recien agregadas ( quitamos las de estreno del slide-bar en el top
def menupelis(item):
    logger.info(item.url)

    itemlist = []

    data = scrapertools.cache_page(item.url).decode('iso-8859-1').encode('utf-8')

    patronenlaces = '<h3>Películas Recién Agregadas</h3>.*?>(.*?)</section>'
    matchesenlaces = re.compile(patronenlaces, re.DOTALL).findall(data)

    logger.info("begin ----------")
    scrapertools.printMatches(matchesenlaces)
    logger.info("end ----------")

    for bloque_enlaces in matchesenlaces:

        patron = '<div class="poster-media-card">.*?'
        patron += '<a href="(.*?)".*?title="(.*?)".*?'
        patron += '<img src="(.*?)"'
        matches = re.compile(patron, re.DOTALL).findall(bloque_enlaces)
        scrapertools.printMatches(matches)

        for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
            logger.info("He encontrado el segundo bloque")
            title = scrapertools.remove_show_from_title(scrapedtitle, "Ver Película")
            title = title.replace("Online", "");
            url = urlparse.urljoin(item.url, scrapedurl)
            thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
            itemlist.append(Item(channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url,
                                 thumbnail=thumbnail, fanart=thumbnail))

    ## PaginaciÃ³n
    # <span class="current">2</span><a href="http://www.repelis.tv/page/3"

    # Si falla no muestra ">> PÃ¡gina siguiente"
    try:
        next_page = scrapertools.get_match(data, '<span class="current">\d+</span><a href="([^"]+)"')
        title = "[COLOR red][B]Pagina siguiente »[/B][/COLOR]"
        itemlist.append(
            Item(channel=item.channel, title=title, url=next_page, action="menupelis", thumbnail=item.thumbnail,
                 fanart=item.fanart, folder=True))
    except:
        pass
    return itemlist


# Todas las peliculas
def todaspelis(item):
    logger.info(item.url)

    itemlist = []

    data = scrapertools.cache_page(item.url).decode('iso-8859-1').encode('utf-8')
    print data
    patronenlaces = '<h1>.*?</h1>.*?>(.*?)</section>'
    matchesenlaces = re.compile(patronenlaces, re.DOTALL).findall(data)

    for bloque_enlaces in matchesenlaces:

        # patron = '<a href="([^"]+)" title="([^"]+)"> <div class="poster".*?<img src="([^"]+)"'

        patron = '<div class="poster-media-card">.*?'
        patron += '<a href="(.*?)".*?title="(.*?)".*?'
        patron += '<img src="(.*?)"'

        matches = re.compile(patron, re.DOTALL).findall(bloque_enlaces)
        scrapertools.printMatches(matches)
        for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
            title = scrapertools.remove_show_from_title(scrapedtitle, "Ver Película")
            title = title.replace("Online", "");
            url = urlparse.urljoin(item.url, scrapedurl)
            thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
            itemlist.append(Item(channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url,
                                 thumbnail=thumbnail, fanart=thumbnail))

    ## PaginaciÃ³n
    # <span class="current">2</span><a href="http://www.repelis.tv/page/3"

    # Si falla no muestra ">> PÃ¡gina siguiente"
    try:
        next_page = scrapertools.get_match(data, '<span class="current">\d+</span><a href="([^"]+)"')
        title = "[COLOR red][B]Pagina siguiente »[/B][/COLOR]"
        itemlist.append(Item(channel=item.channel, title=title, url=next_page, action="todaspelis", folder=True))
    except:
        pass
    return itemlist


# Peliculas Destacadas
def menudesta(item):
    logger.info(item.url)

    itemlist = []

    data = scrapertools.cache_page(item.url).decode('iso-8859-1').encode('utf-8')

    patronenlaces = '<h3>.*?Destacadas.*?>(.*?)<h3>'
    matchesenlaces = re.compile(patronenlaces, re.DOTALL).findall(data)

    for bloque_enlaces in matchesenlaces:

        # patron = '<a href="([^"]+)" title="([^"]+)"> <div class="poster".*?<img src="([^"]+)"'

        patron = '<div class="poster-media-card">.*?'
        patron += '<a href="(.*?)".*?title="(.*?)".*?'
        patron += '<img src="(.*?)"'

        matches = re.compile(patron, re.DOTALL).findall(bloque_enlaces)
        scrapertools.printMatches(matches)
        for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
            title = scrapertools.remove_show_from_title(scrapedtitle, "Ver Película")
            title = title.replace("Online", "");
            url = urlparse.urljoin(item.url, scrapedurl)
            thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
            itemlist.append(Item(channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url,
                                 thumbnail=thumbnail, fanart=thumbnail))

    return itemlist


# Peliculas de Estreno
def menuestre(item):
    logger.info(item.url)

    itemlist = []

    data = scrapertools.cache_page(item.url).decode('iso-8859-1').encode('utf-8')
    patronenlaces = '<h1>Estrenos</h1>(.*?)</section>'
    matchesenlaces = re.compile(patronenlaces, re.DOTALL).findall(data)

    for bloque_enlaces in matchesenlaces:

        # patron = '<a href="([^"]+)" title="([^"]+)"> <div class="poster".*?<img src="([^"]+)"'

        patron = '<div class="poster-media-card">.*?'
        patron += '<a href="(.*?)".*?title="(.*?)".*?'
        patron += '<img src="(.*?)"'

        matches = re.compile(patron, re.DOTALL).findall(bloque_enlaces)
        scrapertools.printMatches(matches)
        for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
            title = scrapertools.remove_show_from_title(scrapedtitle, "Ver Película")
            title = title.replace("Online", "");
            url = urlparse.urljoin(item.url, scrapedurl)
            thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
            itemlist.append(Item(channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url,
                                 thumbnail=thumbnail, fanart=thumbnail))

    ## PaginaciÃ³n
    # <span class="current">2</span><a href="http://www.repelis.tv/page/3"

    # Si falla no muestra ">> PÃ¡gina siguiente"
    try:
        next_page = scrapertools.get_match(data, '<span class="current">\d+</span><a href="([^"]+)"')
        title = "[COLOR red][B]Pagina siguiente »[/B][/COLOR]"
        itemlist.append(Item(channel=item.channel, title=title, url=next_page, action="menuestre", folder=True))
    except:
        pass
    return itemlist


def findvideos(item):
    logger.info(item.url)

    itemlist = []

    data = scrapertools.cache_page(item.url).decode('iso-8859-1').encode('utf-8')

    '''<h2>Sinopsis</2><p>(.*?)</p>
    <div id="informacion" class="tab-pane">
    <h2>Titulo en EspaÃ±ol</h2>
    <p>Abzurdah</p>
    <h2>Titulo Original</h2>
    <p>Abzurdah</p>
    <h2>AÃ±o de Lanzamiento</h2>
    <p>2015</p>
    <h2>Generos</h2>
    <p>Romance</p>
    <h2>Idioma</h2>
    <p>Latino</p>
    <h2>Calidad</h2>
    <p>DVD-Rip</p>
    '''

    # estos son los datos para plot
    patron = '<h2>Sinopsis</h2>.*?<p>(.*?)</p>.*?<div id="informacion".*?</h2>.*?<p>(.*?)</p>'  # titulo
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for sinopsis, title in matches:
        title = "[COLOR white][B]" + title + "[/B][/COLOR]"

    patron = '<div id="informacion".*?>(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedplot in matches:
        splot = title + "\n\n"
        plot = scrapedplot
        plot = re.sub('<h2>', "[COLOR red][B]", plot)
        plot = re.sub('</h2>', "[/B][/COLOR] : ", plot)
        plot = re.sub('<p>', "[COLOR green]", plot)
        plot = re.sub('</p>', "[/COLOR]\n", plot)
        plot = re.sub('<[^>]+>', "", plot)
        splot += plot + "\n[COLOR red][B] Sinopsis[/B][/COLOR]\n " + sinopsis

    # datos de los enlaces
    '''
    <a rel="nofollow" href="(.*?)".*?<td><img.*?</td><td>(.*?)</td><td>(.*?)</td></tr>
 
    ">Vimple</td>
    '''

    patron = '<tbody>(.*?)</tbody>'
    matchesx = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matchesx)

    for bloq in matchesx:
        patron = 'href="(.*?)".*?0 0">(.*?)</.*?<td>(.*?)</.*?<td>(.*?)<'

        matches = re.compile(patron, re.DOTALL).findall(bloq)
        # scrapertools.printMatches(matches)

    for scrapedurl, scrapedserver, scrapedlang, scrapedquality in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.info("Lang:[" + scrapedlang + "] Quality[" + scrapedquality + "] URL[" + url + "]")
        patronenlaces = '.*?://(.*?)/'
        matchesenlaces = re.compile(patronenlaces, re.DOTALL).findall(scrapedurl)
        scrapertools.printMatches(matchesenlaces)
        scrapedtitle = ""
        for scrapedenlace in matchesenlaces:
            scrapedtitle = title + "  [COLOR white][ [/COLOR]" + "[COLOR green]" + scrapedquality + "[/COLOR]" + "[COLOR white] ][/COLOR]" + " [COLOR red] [" + scrapedlang + "][/COLOR]  » " + scrapedserver
        itemlist.append(
            Item(channel=item.channel, action="play", title=scrapedtitle, extra=title, url=url, fanart=item.thumbnail,
                 thumbnail=item.thumbnail, plot=splot, folder=False))

    return itemlist


def play(item):
    logger.info("url=" + item.url)

    # itemlist = servertools.find_video_items(data=item.url)

    url = scrapertools.find_single_match(scrapertools.cache_page(item.url), '<iframe src="([^"]+)"')
    itemlist = servertools.find_video_items(data=url)

    return itemlist


def search(item, texto):
    logger.info(item.url)
    texto = texto.replace(" ", "+")
    item.url = 'http://www.repelis.tv/buscar/?s=%s' % (texto)
    logger.info(item.url)

    data = scrapertools.cache_page(item.url).decode('iso-8859-1').encode('utf-8')

    logger.info("data: " + data)

    '''
    <div class="col-xs-2">
    <div class="row">
    <a href="http://www.repelis.tv/8973/pelicula/contracted-phase-ii.html"  title="Ver PelÃƒÂ­cula Contracted: Phase II Online">
    <img src="http://1.bp.blogspot.com/-YWmw6voBipE/VcB91p-EcnI/AAAAAAAAQZs/EhUzWlInmA8/s175/contracted-phase-2.jpg" border="0">
    '''

    patron = '<div class="col-xs-2">.*?'
    patron += '<div class="row">.*?'
    patron += '<a href="(.*?)" title="(.*?)">.*?'
    patron += '<img src="(.*?)"'

    logger.info(patron)

    matches = re.compile(patron, re.DOTALL).findall(data)

    scrapertools.printMatches(matches)
    print "repelis ..................................."
    itemlist = []

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        title = scrapertools.remove_show_from_title(scrapedtitle, "Ver Película")
        title = title.replace("Online", "")
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        logger.info(url)
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url, thumbnail=thumbnail,
                 fanart=thumbnail))

    return itemlist


# Por aÃ±o, aquÃ­ estÃ¡ difÃ­cil filtrar las "eroticas" asÃ­ que quito la opcion si no esta el adultmode enabled
def poranyo(item):
    logger.info(item.url)

    itemlist = []

    data = scrapertools.cache_page(item.url).decode('iso-8859-1').encode('utf-8')

    patron = '<option value="([^"]+)">(.*?)</option>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.remove_show_from_title(scrapedtitle, "Ver Película")
        title = title.replace("Online", "")
        url = urlparse.urljoin(item.url, scrapedurl)
        itemlist.append(
            Item(channel=item.channel, action="todaspelis", title=title, fulltitle=title, url=url, fanart=item.fanart))

    return itemlist


# Aqui si que se filtran las eroticas
def porcateg(item):
    logger.info(item.url)
    itemlist = []

    data = scrapertools.cache_page(item.url).decode('iso-8859-1').encode('utf-8')
    patron = '<li class="cat-item cat-item-3">.*?<a href="([^"]+)" title="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.remove_show_from_title(scrapedtitle, "Ver Película")
        title = title.replace("Online", "")
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.info(url)
        # si no esta permitidas categoria adultos, la filtramos
        erotica = ""
        if config.get_setting("adult_mode") == 0:
            patron = '.*?/erotic.*?'
            try:
                erotica = scrapertools.get_match(scrapedurl, patron)
            except:
                itemlist.append(
                    Item(channel=item.channel, action="todaspelis", fanart=item.fanart, title=title, fulltitle=title,
                         url=url))
        else:
            itemlist.append(Item(channel=item.channel, action="todaspelis", title=title, fulltitle=title, url=url,
                                 fanart=item.fanart))

    return itemlist
