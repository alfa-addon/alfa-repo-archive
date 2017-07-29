# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="listalfabetico", title="Listado alfabetico",
                         url="http://www.seriesyonkis.sx",
                         fanart=item.fanart))
    itemlist.append(Item(channel=item.channel, action="mostviewed", title="Series más vistas",
                         url="http://www.seriesyonkis.sx/series-mas-vistas",
                         fanart=item.fanart))
    itemlist.append(
        Item(channel=item.channel, action="search", title="Buscar", url="http://www.seriesyonkis.sx/buscar/serie",
             fanart=item.fanart))

    return itemlist


def search(item, texto, categoria="*"):
    logger.info()
    itemlist = []

    if categoria not in ("*", "S"): return itemlist  ## <--

    if item.url == "":
        item.url = "http://www.seriesyonkis.sx/buscar/serie"
    url = "http://www.seriesyonkis.sx/buscar/serie"  # write ur URL here
    post = 'keyword=' + texto[0:18] + '&search_type=serie'

    data = scrapertools.cache_page(url, post=post)
    try:
        return getsearchresults(item, data, "episodios")
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def getsearchresults(item, data, action):
    itemlist = []

    patron = '_results_wrapper">(.*?)<div id="fixed-footer"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        # <li class="nth-child1n"> <figure> <a href="/pelicula/el-moderno-sherlock-holmes-1924" title="El moderno Sherlock Holmes (1924)"><img width="100" height="144" src="http://s.staticyonkis.com/img/peliculas/100x144/el-moderno-sherlock-holmes-1924.jpg" alt=""></a> <figcaption>8.0</figcaption> </figure> <aside> <h2><a href="/pelicula/el-moderno-sherlock-holmes-1924" title="El moderno Sherlock Holmes (1924)">El moderno Sherlock Holmes (1924)</a></h2> <p class="date">1924 | Estados Unidos | votos: 3</p> <div class="content">Película sobre el mundo del cine, Keaton es un proyeccionista que sueña con ser un detective cuando, milagrosamente, se encuentra dentro de la película que está proyectando. Allí intentará salvar a su amada de las garras del villano. Una de...</div> <p class="generos">  <a href="/genero/comedia">Comedia</a>  <a class="topic" href="/genero/cine-mudo">Cine mudo</a>  <a class="topic" href="/genero/mediometraje">Mediometraje</a>  <i>(1 más) <span class="aditional_links"> <span>  <a class="topic" href="/genero/sherlock-holmes">Sherlock Holmes</a>  </span> </span> </i>  </p> </aside> </li>
        patron = '<li[^>]+>.*?href="([^"]+)".*?title="([^"]+)".*?src="([^"]+).*?<div class="content">([^<]+)</div>.*?</li>'
        results = re.compile(patron, re.DOTALL).findall(match)
        for result in results:
            scrapedtitle = result[1]
            scrapedurl = urlparse.urljoin(item.url, result[0])
            scrapedthumbnail = result[2]
            scrapedplot = result[3]
            logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

            itemlist.append(
                Item(channel=item.channel, action=action, title=scrapedtitle, fulltitle=scrapedtitle, url=scrapedurl,
                     thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle))

    return itemlist


def lastepisodes(item):
    logger.info()

    data = scrapertools.cache_page(item.url)

    # <li class="thumb-episode "> <a href="/capitulo/strike-back/project-dawn-part-3/200215"><img class="img-shadow" src="/img/series/170x243/strike-back.jpg" height="166" width="115"></a> <div class="transparent"> <a href="/capitulo/strike-back/project-dawn-part-3/200215"><span>2x03</span></a> </div> <strong><a href="/serie/strike-back" title="Strike back">Strike back</a></strong> </li>
    matches = re.compile('<li class="thumb-episode ">.*?</li>', re.S).findall(data)
    # scrapertools.printMatches(matches)

    itemlist = []
    for match in matches:

        # <li class="thumb-episode "> <a href="/capitulo/strike-back/project-dawn-part-3/200215"><img class="img-shadow" src="/img/series/170x243/strike-back.jpg" height="166" width="115"></a> <div class="transparent"> <a href="/capitulo/strike-back/project-dawn-part-3/200215"><span>2x03</span></a> </div> <strong><a href="/serie/strike-back" title="Strike back">Strike back</a></strong> </li>
        datos = re.compile('<a href="([^"]+)">.*?src="([^"]+)".*?<span>([^<]+)</span>.*?title="([^"]+)"', re.S).findall(
            match)

        for capitulo in datos:
            scrapedtitle = capitulo[3] + " " + capitulo[2]
            scrapedurl = urlparse.urljoin(item.url, capitulo[0])
            scrapedthumbnail = item.url + capitulo[1]
            scrapedplot = ""

            # Depuracion
            logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
            itemlist.append(Item(channel=item.channel, action="findvideos", title=scrapedtitle, fulltitle=scrapedtitle,
                                 url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle,
                                 fanart=item.fanart))

    return itemlist


def mostviewed(item):
    logger.info()
    data = scrapertools.cachePage(item.url)

    # <div id="tabs-1"> <h1>Más vistas ayer</h1>
    # <ul class="covers-list">
    #     <li class="thumb-episode"><a title="Cómo conocí a vuestra madre (2005)" href="/serie/como-conoci-a-vuestra-madre"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/How_I_Met_Your_Mother-19641.JPEG" alt="Cómo conocí a vuestra madre"/></a><strong><a href="/serie/como-conoci-a-vuestra-madre" title"Cómo conocí a vuestra madre (2005)">Cómo conocí a vuestra madre (2005)</a></strong></li><li class="thumb-episode"><a title="The Big Bang Theory (2007)" href="/serie/the-big-bang-theory"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/2/The_Big_Bang_Theory-20285.PNG" alt="The Big Bang Theory"/></a><strong><a href="/serie/the-big-bang-theory" title"The Big Bang Theory (2007)">The Big Bang Theory (2007)</a></strong></li><li class="thumb-episode"><a title="Friends (1994)" href="/serie/friends"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/2/Friends-20013.PNG" alt="Friends"/></a><strong><a href="/serie/friends" title"Friends (1994)">Friends (1994)</a></strong></li><li class="thumb-episode"><a title="The vampire diaries (Crónicas Vampíricas) (2009)" href="/serie/the-vampire-diaries"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/The_Vampire_Diaries-18597.JPEG" alt="The vampire diaries (Crónicas Vampíricas)"/></a><strong><a href="/serie/the-vampire-diaries" title"The vampire diaries (Crónicas Vampíricas) (2009)">The vampire diaries (Crónicas Vampíricas) (2009)</a></strong></li><li class="clear"></li> <li class="thumb-episode"><a title="Breaking Bad (2008)" href="/serie/breaking-bad"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/Breaking_Bad-18431.PNG" alt="Breaking Bad"/></a><strong><a href="/serie/breaking-bad" title"Breaking Bad (2008)">Breaking Bad (2008)</a></strong></li><li class="thumb-episode"><a title="Anatomía de Grey (2005)" href="/serie/anatomia-de-grey"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/Grey_s_Anatomy-18325.JPEG" alt="Anatomía de Grey"/></a><strong><a href="/serie/anatomia-de-grey" title"Anatomía de Grey (2005)">Anatomía de Grey (2005)</a></strong></li><li class="thumb-episode"><a title="Keeping up with the Kardashians (2007)" href="/serie/keeping-up-with-the-kardashians"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/Keeping_Up_with_the_Kardashians-19944.JPEG" alt="Keeping up with the Kardashians"/></a><strong><a href="/serie/keeping-up-with-the-kardashians" title"Keeping up with the Kardashians (2007)">Keeping up with the Kardashians (2007)</a></strong></li><li class="thumb-episode"><a title="The Walking Dead (2010)" href="/serie/the-walking-dead-yonkis1"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/The_Walking_Dead-19273.PNG" alt="The Walking Dead"/></a><strong><a href="/serie/the-walking-dead-yonkis1" title"The Walking Dead (2010)">The Walking Dead (2010)</a></strong></li><li class="clear"></li> <li class="thumb-episode"><a title="Pequeñas mentirosas (Pretty Little Liars) (2010)" href="/serie/pretty-little-liars"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/Pretty_Little_Liars-18575.PNG" alt="Pequeñas mentirosas (Pretty Little Liars)"/></a><strong><a href="/serie/pretty-little-liars" title"Pequeñas mentirosas (Pretty Little Liars) (2010)">Pequeñas mentirosas (Pretty Little Liars) (2010)</a></strong></li><li class="thumb-episode"><a title="Sobrenatural (Supernatural) (2005)" href="/serie/sobrenatural"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/Supernatural-19429.JPEG" alt="Sobrenatural (Supernatural)"/></a><strong><a href="/serie/sobrenatural" title"Sobrenatural (Supernatural) (2005)">Sobrenatural (Supernatural) (2005)</a></strong></li><li class="thumb-episode"><a title="Juego de tronos (2011)" href="/serie/juego-de-tronos-2011"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/2/Game_of_Thrones-22818.PNG" alt="Juego de tronos"/></a><strong><a href="/serie/juego-de-tronos-2011" title"Juego de tronos (2011)">Juego de tronos (2011)</a></strong></li><li class="thumb-episode"><a title="New girl (2011)" href="/serie/new-girl"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/3/New_Girl-40390.JPEG" alt="New girl"/></a><strong><a href="/serie/new-girl" title"New girl (2011)">New girl (2011)</a></strong></li><li class="clear"></li> <li class="thumb-episode"><a title="Modern Family (2009)" href="/serie/modern-family"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/Modern_Family-19537.JPEG" alt="Modern Family"/></a><strong><a href="/serie/modern-family" title"Modern Family (2009)">Modern Family (2009)</a></strong></li><li class="thumb-episode"><a title="Padre de Familia (1999)" href="/serie/padre-de-familia"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/2/Family_Guy-21309.PNG" alt="Padre de Familia"/></a><strong><a href="/serie/padre-de-familia" title"Padre de Familia (1999)">Padre de Familia (1999)</a></strong></li><li class="thumb-episode"><a title="Suits (2011)" href="/serie/suits"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/2/Suits-35726.JPEG" alt="Suits"/></a><strong><a href="/serie/suits" title"Suits (2011)">Suits (2011)</a></strong></li><li class="thumb-episode"><a title="Gossip Girl (2007)" href="/serie/gossip-girl-yonkis1"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/Gossip_Girl-19209.JPEG" alt="Gossip Girl"/></a><strong><a href="/serie/gossip-girl-yonkis1" title"Gossip Girl (2007)">Gossip Girl (2007)</a></strong></li><li class="clear"></li> <li class="thumb-episode"><a title="Los Simpsons (1989)" href="/serie/los-simpsons"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/The_Simpsons-19237.PNG" alt="Los Simpsons"/></a><strong><a href="/serie/los-simpsons" title"Los Simpsons (1989)">Los Simpsons (1989)</a></strong></li><li class="thumb-episode"><a title="Dos Hombres y Medio (Two and a Half Men) (2003)" href="/serie/dos-hombres-y-medio-two-and-a-half-men"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/Two_and_a_Half_Men-19450.JPEG" alt="Dos Hombres y Medio (Two and a Half Men)"/></a><strong><a href="/serie/dos-hombres-y-medio-two-and-a-half-men" title"Dos Hombres y Medio (Two and a Half Men) (2003)">Dos Hombres y Medio (Two and a Half Men) (2003)</a></strong></li><li class="thumb-episode"><a title="Revenge (2011)" href="/serie/revenge"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/3/Revenge-40394.JPEG" alt="Revenge"/></a><strong><a href="/serie/revenge" title"Revenge (2011)">Revenge (2011)</a></strong></li><li class="thumb-episode"><a title="Glee (2009)" href="/serie/glee"><img width="100" height="144" class="img-shadow" src="http://static2.seriesyonkis.sx/90/1/Glee-19136.JPEG" alt="Glee"/></a><strong><a href="/serie/glee" title"Glee (2009)">Glee (2009)</a></strong></li><li class="clear"></li>  
    # </ul>
    # </div>
    matches = re.compile('<div id="tabs-1">(.*?)</div>', re.S).findall(data)
    if len(matches) <= 0:
        return []
    data = matches[0]

    # <li class="thumb-episode"> <a href="/serie/como-conoci-a-vuestra-madre" title="Cómo conocí a vuestra madre"><img class="img-shadow" src="/img/series/170x243/como-conoci-a-vuestra-madre.jpg" height="166" width="115"></a> <strong><a href="/serie/como-conoci-a-vuestra-madre" title="Cómo conocí a vuestra madre">Cómo conocí a vuestra madre</a></strong> </li>
    matches = re.compile('<a title="([^"]+)" href="([^"]+)".*?src="([^"]+)".*?</a>', re.S).findall(data)
    # scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedtitle = match[0]
        scrapedurl = urlparse.urljoin(item.url, match[1])
        scrapedthumbnail = urlparse.urljoin(item.url, match[2])
        scrapedplot = ""

        # Depuracion
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="episodios", title=scrapedtitle, fulltitle=scrapedtitle, url=scrapedurl,
                 thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle,
                 fanart=item.fanart))

    return itemlist


def series(item):
    logger.info()
    itemlist = []

    data = scrapertools.cachePage(item.url)

    # Paginador
    # <div class="paginator"> &nbsp;<a href="/lista-de-series/C/">&lt;</a>&nbsp;<a href="/lista-de-series/C/">1</a>&nbsp;<strong>2</strong>&nbsp;<a href="/lista-de-series/C/200">3</a>&nbsp;<a href="/lista-de-series/C/200">&gt;</a>&nbsp; </div>
    matches = re.compile('<a href="([^"]+)">></a>', re.S).findall(data)
    # matches = re.compile('<div class="paginator">.*?<a href="([^"]+)".*?</div>', re.S).findall(data)
    if len(matches) > 0:
        paginador = Item(channel=item.channel, action="series", title="!Página siguiente",
                         url=urlparse.urljoin(item.url, matches[0]), thumbnail=item.thumbnail, plot="", extra="",
                         show=item.show, fanart=item.fanart)
    else:
        paginador = None

    if paginador is not None:
        itemlist.append(paginador)

    # <div id="main-section" class="lista-series">.*?</div>
    # matches = re.compile('<div id="main-section" class="lista-series">.*?</div>', re.S).findall(data)
    matches = re.compile('<ul id="list-container".*?</ul>', re.S).findall(data)
    # scrapertools.printMatches(matches)
    for match in matches:
        data = match
        break

    # <li><a href="/serie/al-descubierto" title="Al descubierto">Al descubierto</a></li>
    # matches = re.compile('<li>.*?href="([^"]+)".*?title="([^"]+)".*?</li>', re.S).findall(data)
    matches = re.compile('title="([^"]+)" href="([^"]+)"', re.S).findall(data)
    # scrapertools.printMatches(matches)

    for match in matches:
        itemlist.append(Item(channel=item.channel, action="episodios", title=match[0], fulltitle=match[0],
                             url=urlparse.urljoin(item.url, match[1]), thumbnail="", plot="", extra="", show=match[0],
                             fanart=item.fanart))

    if len(itemlist) > 0 and config.get_platform() in ("wiimc", "rss") and item.channel <> "wiideoteca":
        itemlist.append(
            Item(channel=item.channel, action="add_serie_to_wiideoteca", title=">> Agregar Serie a Wiideoteca <<",
                 fulltitle=item.fulltitle, url=item.url, thumbnail="", plot="", extra=""))

    if paginador is not None:
        itemlist.append(paginador)

    return itemlist


def detalle_programa(item, data=""):
    # http://www.seriesyonkis.sx/serie/gungrave
    # http://www.seriesyonkis.sx/ficha/serie/gungrave
    url = item.url
    if "seriesyonkis.com/serie/" in url:
        url = url.replace("seriesyonkis.com/serie/", "seriesyonkis.com/ficha/serie/")

    # Descarga la página
    if data == "":
        data = scrapertools.cache_page(url)

    # Obtiene el thumbnail
    try:
        item.thumbnail = scrapertools.get_match(data, '<div class="profile-info"[^<]+<a[^<]+<img src="([^"]+)"')
    except:
        pass

    try:
        item.plot = scrapertools.htmlclean(scrapertools.get_match(data, '<div class="details">(.*?)</div>'))
    except:
        pass
    logger.info("plot=" + item.plot)

    try:
        item.title = scrapertools.get_match(data, '<h1 class="underline"[^>]+>([^<]+)</h1>').strip()
    except:
        pass

    return item


def episodios(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    item = detalle_programa(item)

    # <h2 class="header-subtitle">CapÃ­tulos</h2> <ul class="menu">
    # <h2 class="header-subtitle">Cap.*?</h2> <ul class="menu">.*?</ul>
    matches = re.compile('<h2 class="header-subtitle">Cap.*?</h2> <ul class="menu">.*?</ul>', re.S).findall(data)
    if len(matches) > 0:
        data = matches[0]
    # <li.*?
    matches = re.compile('<li.*?</li>', re.S).findall(data)
    # scrapertools.printMatches(matches)

    itemlist = []

    No = 0
    for match in matches:
        itemlist.extend(addChapters(
            Item(channel=item.channel, url=item.url, extra=match, thumbnail=item.thumbnail, show=item.show,
                 plot=item.plot, fulltitle=item.title)))
        '''
        if(len(matches)==1):
            itemlist = addChapters(Item(url=match, thumbnail=thumbnail))
        else:
            # Añade al listado de XBMC
            No = No + 1
            title = "Temporada "+str(No)
            itemlist.append( Item(channel=item.channel, action="season" , title= title, url=match, thumbnail=thumbnail, plot="", show = title, folder=True))
        '''

    if config.get_videolibrary_support():
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=item.show,
                             fanart=item.fanart))
        itemlist.append(Item(channel=item.channel, title="Descargar todos los episodios de la serie", url=item.url,
                             action="download_all_episodes", extra="episodios", show=item.show,
                             fanart=item.fanart))

    return itemlist


def addChapters(item):
    # <tr > <td class="episode-title"> <span class="downloads allkind" title="Disponibles enlaces a descarga directa y visualizaciones"></span>
    # <a href="/capitulo/bones/capitulo-2/2870"> <strong> 1x02 </strong> - El hombre en la unidad especial de victimas </a> </td> <td> 18/08/2007 </td> <td class="episode-lang">  <span class="flags_peq spa" title="Español"></span>  </td> <td class="score"> 8 </td> </tr>
    matches = re.compile('<a class="episodeLink p1" href="([^"]+)"[^<]+<strong>([^<]+)</strong>(.*?)</a>(.*?)</tr>',
                         re.S).findall(item.extra)
    scrapertools.printMatches(matches)

    itemlist = []
    for match in matches:
        url = urlparse.urljoin(item.url, match[0])
        title = match[1].strip() + match[2]

        patron = '<span class="flags[^"]+" title="([^"]+)">'
        flags = re.compile(patron, re.DOTALL).findall(match[3])
        for flag in flags:
            title = title + " (" + flag + ")"

        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, fulltitle=item.fulltitle + " " + title,
                 url=url, thumbnail=item.thumbnail, plot=item.plot, show=item.show, context="4", folder=True,
                 fanart=item.fanart))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    try:
        Nro = 0
        fmt = id = ""

        # Acota la zona de búsqueda
        data = scrapertools.cache_page(item.url)
        data = scrapertools.get_match(data, '<div id="section-content"(.*?)</table>')

        # Procesa línea por línea
        matches = re.compile('<tr>.*?</tr>', re.S).findall(data)

        for match in matches:
            logger.info(match)
            # <tr> <td class="episode-server"> <a href="/s/ngo/2/0/0/4/967" title="Reproducir No estamos solos 2x1" target="_blank"><img src="http://s.staticyonkis.com/img/veronline.png" height="22" width="22"> Reproducir</a> </td> <td class="episode-server-img"><a href="/s/ngo/2/0/0/4/967" title="Reproducir No estamos solos 2x1" target="_blank"><span class="server megavideo"></span></a></td> <td class="episode-lang"><span class="flags esp" title="Español">esp</span></td> <td class="center"><span class="flags no_sub" title="Sin subtítulo o desconocido">no</span></td> <td> <span class="episode-quality-icon" title="Calidad del episodio"> <i class="sprite quality5"></i> </span> </td> <td class="episode-notes"><span class="icon-info"></span> <div class="tip hidden"> <h3>Información vídeo</h3> <div class="arrow-tip-right-dark sprite"></div> <ul> <li>Calidad: 6, Duración: 85.8 min, Peso: 405.79 MB, Resolución: 640x368</li> </ul> </div> </td> <td class="episode-uploader">lksomg</td> <td class="center"><a href="#" class="errorlink" data-id="2004967"><img src="http://s.staticyonkis.com/img/icons/bug.png" alt="" /></a></td> </tr>
            # <tr> <td class="episode-server" data-value="0"> <a href="/s/ngo/5/5/9/8/737" title="Descargar Capítulo 514 1x514 de rapidgator" target="_blank"><img src="http://s.staticyonkis.com/img/descargadirecta.png" height="22" width="22" alt="descarga directa" /> Descargar</a>  <span class="public_sprite like_green vote_link_positive user_not_logged" data-id="5598737" data-type="+" title="Voto positivo">[positivo]</span> <span class="public_sprite dislike_red vote_link_negative user_not_logged" data-id="5598737" data-type="-" title="Voto negativo">[negativo]</span> </td> <td class="episode-server-img"><a href="/s/ngo/5/5/9/8/737" title="Descargar Capítulo 514 1x514" target="_blank"><span class="server rapidgator"></span></a></td> <td class="episode-lang"><span class="flags spa" title="Español">spa</span></td> <td class="episode-subtitle subtitles center"><span class="flags no_sub" title="Sin información">no_sub</span></td> <td class="episode-notes"> <span class="icon-info"></span> <div class="tip hidden"> <h3>Información vídeo</h3> <div class="arrow-tip-right-dark sprite"></div> <ul> <li>hdtv</li>  </ul> </div> </td> <td class="episode-uploader"> <span title="repomen77">repomen77</span> </td> <td class="episode-error bug center"><a href="#" class="errorlink" data-id="5598737"><img src="http://s.staticyonkis.com/img/icons/bug.png" alt="error" /></a></td> </tr>
            # <a href="/s/ngo/5/5/9/8/737"
            # <span class="server rapidgator"></span></a></td> <td class="episode-lang">
            # <span class="flags spa" title="Español">spa</span></td> <td class="episode-subtitle subtitles center">
            # <span class="flags no_sub" title="Sin información">no_sub</span></td> <td class="episode-notes"> <span class="icon-info"></span> <div class="tip hidden"> <h3>Información vídeo</h3>
            # <div class="arrow-tip-right-dark sprite"></div> <ul> <li>hdtv</li>  </ul> </div> </td> <td class="episode-uploader"> <span title="repomen77">repomen77</span> </td> <td class="episode-error bug center"><a href="#" class="errorlink" data-id="5598737"><img src="http://s.staticyonkis.com/img/icons/bug.png" alt="error" /></a></td> </tr>
            patron = '<a href="([^"]+)".*?</td>.*?'
            patron += 'alt="([^"]+)".*?'
            patron += 'class="episode-lang">.*?title="([^"]+)"'
            datos = re.compile(patron, re.S).findall(match)
            for info in datos:
                id = info[0]
                servidor = info[1]
                Nro = Nro + 1
                audio = "Audio:" + info[2]
                url = "http://www.seriesyonkis.sx" + info[0]
                scraptedtitle = "%02d) [%s] - [%s] " % (Nro, audio, servidor)
                # El plot va vacío porque necesita menos memoria, y en realidad es el de la serie y no el del episodio :)
                itemlist.append(
                    Item(channel=item.channel, action="play", title=scraptedtitle, fulltitle=item.fulltitle, url=url,
                         thumbnail=item.thumbnail, plot="", folder=False,
                         fanart=item.fanart))
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = scrapertools.cache_page(item.url)
    videos = servertools.findvideos(data)

    if (len(videos) > 0):
        url = videos[0][1]
        server = videos[0][2]
        itemlist.append(Item(channel=item.channel, action="play", title=item.title, fulltitle=item.fulltitle, url=url,
                             thumbnail=item.thumbnail, plot=item.plot, server=server, extra=item.extra, folder=False))
    else:
        patron = '<ul class="form-login">(.*?)</ul'
        matches = re.compile(patron, re.S).findall(data)
        if (len(matches) > 0):
            if "xbmc" in config.get_platform():
                data = matches[0]
                # buscamos la public key
                patron = 'src="http://www.google.com/recaptcha/api/noscript\?k=([^"]+)"'
                pkeys = re.compile(patron, re.S).findall(data)
                if (len(pkeys) > 0):
                    pkey = pkeys[0]
                    # buscamos el id de challenge
                    data = scrapertools.cache_page("http://www.google.com/recaptcha/api/challenge?k=" + pkey)
                    patron = "challenge.*?'([^']+)'"
                    challenges = re.compile(patron, re.S).findall(data)
                    if (len(challenges) > 0):
                        challenge = challenges[0]
                        image = "http://www.google.com/recaptcha/api/image?c=" + challenge

                        # CAPTCHA
                        exec "import platformcode.captcha as plugin"
                        tbd = plugin.Keyboard("", "", image)
                        tbd.doModal()
                        confirmed = tbd.isConfirmed()
                        if (confirmed):
                            tecleado = tbd.getText()
                            logger.info("tecleado=" + tecleado)
                            sendcaptcha(playurl, challenge, tecleado)
                        del tbd
                        # tbd ya no existe
                        if (confirmed and tecleado != ""):
                            itemlist = play(item)
            else:
                itemlist.append(Item(channel=item.channel, action="error", title="El sitio web te requiere un captcha"))

    logger.info("len(itemlist)=%s" % len(itemlist))
    return itemlist


def sendcaptcha(url, challenge, text):
    values = {'recaptcha_challenge_field': challenge,
              'recaptcha_response_field': text}
    form_data = urllib.urlencode(values)
    url = url.replace("seriesyonkis", "seriescoco")
    url = url.replace("peliculasyonkis", "peliculascoco")
    logger.info("url=" + url + ", form_data=" + form_data)
    request = urllib2.Request(url, form_data)
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)')
    response = urllib2.urlopen(request)
    html = response.read()
    logger.info("response=" + html)
    response.close()
    return html


# Pone todas las series del listado alfabético juntas, para no tener que ir entrando una por una
def completo(item):
    logger.info()
    itemlist = []

    # Carga el menú "Alfabético" de series
    item = Item(channel=item.channel, action="listalfabetico")
    items_letras = listalfabetico(item)

    # Para cada letra
    for item_letra in items_letras:
        # print item_letra.title

        # Lee las series
        items_programas = series(item_letra)

        salir = False
        while not salir:

            # Saca la URL de la siguiente página
            ultimo_item = items_programas[len(items_programas) - 1]

            # Páginas intermedias
            if ultimo_item.action == "series":
                # print ultimo_item.url
                # Quita el elemento de "Página siguiente" 
                ultimo_item = items_programas.pop()

                # Añade las series de la página a la lista completa
                itemlist.extend(items_programas)

                # Carga la sigiuente página
                items_programas = series(ultimo_item)

            # Última página
            else:
                # Añade a la lista completa y sale
                itemlist.extend(items_programas)
                salir = True

    return itemlist


def listalfabetico(item):
    logger.info()

    itemlist = []

    itemlist.append(
        Item(channel=item.channel, action="series", title="0-9", url="http://www.seriesyonkis.sx/lista-de-series/0-9",
             fanart=item.fanart))
    for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                  'U', 'V', 'W', 'X', 'Y', 'Z']:
        itemlist.append(Item(channel=item.channel, action="series", title=letra,
                             url="http://www.seriesyonkis.sx/lista-de-series/" + letra,
                             fanart=item.fanart))

    return itemlist
