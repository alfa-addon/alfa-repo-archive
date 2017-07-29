# -*- coding: utf-8 -*-

import re
import urlparse

from core import config
from core import jsontools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

DEFAULT_HEADERS = []
DEFAULT_HEADERS.append(
    ["User-Agent", "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"])


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="menuseries", title="Series", url=""))
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Películas", url="http://vserie.com/peliculas",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar...", url="http://vserie.com/search"))

    return itemlist


def menuseries(item):
    logger.info()

    itemlist = []
    itemlist.append(
        Item(channel=item.channel, action="novedades", title="Últimos episodios", url="http://vserie.com/series",
             viewmode="movie"))
    itemlist.append(
        Item(channel=item.channel, action="series", title="Todas", url="http://vserie.com/series", viewmode="movie"))

    return itemlist


def search(item, texto):
    logger.info()

    try:
        if config.get_setting("zampaseriesaccount") == True:
            login()

        if item.url == "":
            item.url = "http://vserie.com/search"

        texto = texto.replace(" ", "+")

        # Mete el referer en item.extra
        post = "s=" + texto
        data = scrapertools.cache_page(item.url, post=post)
        data = scrapertools.find_single_match(data, '<div id="resultados">(.*?)<div id="cargando">')
        '''
        <div id="resultados">
        <h1>Resultados de la Busqueda para skyfall (1)</h1>
        <div id="lista">              <ul>                <li title="007 Skyfall" id="id-1"><a href="http://vserie.com/pelicula/2-007-skyfall"><img src="http://vserie.com/images/p_p2_s.png" alt=""></a></li>              </ul>            </div>
        <div id="cargando"><i class="icon-spinner icon-spin"></i>Cargando más resultados</div>
        </div>
        '''
        patron = '<li title="([^"]+)"[^<]+<a href="([^"]+)"><img src="([^"]+)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        itemlist = []
        for scrapedtitle, scrapedurl, scrapedthumbnail in matches:
            if "/pelicula/" in scrapedurl:
                title = scrapedtitle
                url = scrapedurl
                thumbnail = scrapedthumbnail
                plot = ""
                itemlist.append(
                    Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                         plot=plot, show=title))
            else:
                title = scrapedtitle
                url = scrapedurl
                thumbnail = scrapedthumbnail
                plot = ""
                itemlist.append(
                    Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail, plot=plot,
                         show=title))

        return itemlist

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def novedades(item):
    logger.info()

    if config.get_setting("zampaseriesaccount") == True:
        login()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data, 'ltimas Series Actualizadas</h2[^<]+<div id="listado">(.*?)</ul>')
    logger.info("data=" + data)

    # Extrae las entradas (carpetas)  
    patron = '<li><a href="([^"]+)"><img src="([^"]+)[^<]+<h3>([^<]+)</h3></a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 show=title))

    return itemlist


def series(item, data=""):
    logger.info()

    if config.get_setting("zampaseriesaccount") == True:
        login()

    # Descarga la pagina
    if data == "":
        if item.extra == "":
            data = scrapertools.cache_page(item.url)
        else:
            data = scrapertools.cache_page(item.url, post=item.extra)
            logger.info("data=" + data)

            json_object = jsontools.load(data)
            # {"resultado":{"40":"<li id=\"id-40\" title=\"The 100\"><a href=\"http:\/\/vserie.com\/serie\/175-the-100\"><img src=\"http:\/\/vserie.com\/images\/s_s175_s.png\" alt=\"The 100\"><\/a><\/li>","41":"<li id=\"id-41\" title=\"Teen Wolf\"><a href=\"http:\/\/vserie.com\/serie\/25-teen-wolf\"><img src=\"http:\/\/vserie.com\/images\/s_s25_s.png\" alt=\"Teen Wolf\"><\/a><\/li>","42":"<li id=\"id-42\" title=\"Surviving Jack\"><a href=\"http:\/\/vserie.com\/serie\/178-surviving-jack\"><img src=\"http:\/\/vserie.com\/images\/s_s178_s.png\" alt=\"Surviving Jack\"><\/a><\/li>","43":"<li id=\"id-43\" title=\"Supernatural\"><a href=\"http:\/\/vserie.com\/serie\/68-supernatural\"><img src=\"http:\/\/vserie.com\/images\/s_s68_s.png\" alt=\"Supernatural\"><\/a><\/li>","44":"<li id=\"id-44\" title=\"Suits\"><a href=\"http:\/\/vserie.com\/serie\/131-suits\"><img src=\"http:\/\/vserie.com\/images\/s_s131_s.png\" alt=\"Suits\"><\/a><\/li>","45":"<li id=\"id-45\" title=\"Star-Crossed\"><a href=\"http:\/\/vserie.com\/serie\/154-star-crossed\"><img src=\"http:\/\/vserie.com\/images\/s_s154_s.png\" alt=\"Star-Crossed\"><\/a><\/li>","46":"<li id=\"id-46\" title=\"Sons of Anarchy\"><a href=\"http:\/\/vserie.com\/serie\/46-sons-of-anarchy\"><img src=\"http:\/\/vserie.com\/images\/s_s46_s.png\" alt=\"Sons of Anarchy\"><\/a><\/li>","47":"<li id=\"id-47\" title=\"Sleepy Hollow\"><a href=\"http:\/\/vserie.com\/serie\/52-sleepy-hollow\"><img src=\"http:\/\/vserie.com\/images\/s_s52_s.png\" alt=\"Sleepy Hollow\"><\/a><\/li>","48":"<li id=\"id-48\" title=\"Skins\"><a href=\"http:\/\/vserie.com\/serie\/36-skins\"><img src=\"http:\/\/vserie.com\/images\/s_s36_s.png\" alt=\"Skins\"><\/a><\/li>","49":"<li id=\"id-49\" title=\"Sirens\"><a href=\"http:\/\/vserie.com\/serie\/172-sirens\"><img src=\"http:\/\/vserie.com\/images\/s_s172_s.png\" alt=\"Sirens\"><\/a><\/li>","50":"<li id=\"id-50\" title=\"Sin identidad\"><a href=\"http:\/\/vserie.com\/serie\/199-sin-identidad\"><img src=\"http:\/\/vserie.com\/images\/s_s199_s.png\" alt=\"Sin identidad\"><\/a><\/li>","51":"<li id=\"id-51\" title=\"Silicon Valley\"><a href=\"http:\/\/vserie.com\/serie\/179-silicon-valley\"><img src=\"http:\/\/vserie.com\/images\/s_s179_s.png\" alt=\"Silicon Valley\"><\/a><\/li>","52":"<li id=\"id-52\" title=\"Siberia\"><a href=\"http:\/\/vserie.com\/serie\/39-siberia\"><img src=\"http:\/\/vserie.com\/images\/s_s39_s.png\" alt=\"Siberia\"><\/a><\/li>","53":"<li id=\"id-53\" title=\"Sherlock\"><a href=\"http:\/\/vserie.com\/serie\/103-sherlock\"><img src=\"http:\/\/vserie.com\/images\/s_s103_s.png\" alt=\"Sherlock\"><\/a><\/li>","54":"<li id=\"id-54\" title=\"Shameless\"><a href=\"http:\/\/vserie.com\/serie\/142-shameless\"><img src=\"http:\/\/vserie.com\/images\/s_s142_s.png\" alt=\"Shameless\"><\/a><\/li>","55":"<li id=\"id-55\" title=\"Salem\"><a href=\"http:\/\/vserie.com\/serie\/186-salem\"><img src=\"http:\/\/vserie.com\/images\/s_s186_s.png\" alt=\"Salem\"><\/a><\/li>","56":"<li id=\"id-56\" title=\"Rosemary&#039;s Baby (La semilla del diablo)\"><a href=\"http:\/\/vserie.com\/serie\/198-rosemary-039-s-baby-la-semilla-del-diablo\"><img src=\"http:\/\/vserie.com\/images\/s_s198_s.png\" alt=\"Rosemary&#039;s Baby (La semilla del diablo)\"><\/a><\/li>","57":"<li id=\"id-57\" title=\"Ripper Street\"><a href=\"http:\/\/vserie.com\/serie\/100-ripper-street\"><img src=\"http:\/\/vserie.com\/images\/s_s100_s.png\" alt=\"Ripper Street\"><\/a><\/li>","58":"<li id=\"id-58\" title=\"Revolution\"><a href=\"http:\/\/vserie.com\/serie\/62-revolution\"><img src=\"http:\/\/vserie.com\/images\/s_s62_s.png\" alt=\"Revolution\"><\/a><\/li>","59":"<li id=\"id-59\" title=\"Revenge\"><a href=\"http:\/\/vserie.com\/serie\/67-revenge\"><img src=\"http:\/\/vserie.com\/images\/s_s67_s.png\" alt=\"Revenge\"><\/a><\/li>","60":"<li id=\"id-60\" title=\"Resurrection\"><a href=\"http:\/\/vserie.com\/serie\/167-resurrection\"><img src=\"http:\/\/vserie.com\/images\/s_s167_s.png\" alt=\"Resurrection\"><\/a><\/li>","61":"<li id=\"id-61\" title=\"Remedy\"><a href=\"http:\/\/vserie.com\/serie\/161-remedy\"><img src=\"http:\/\/vserie.com\/images\/s_s161_s.png\" alt=\"Remedy\"><\/a><\/li>","62":"<li id=\"id-62\" title=\"Reign\"><a href=\"http:\/\/vserie.com\/serie\/92-reign\"><img src=\"http:\/\/vserie.com\/images\/s_s92_s.png\" alt=\"Reign\"><\/a><\/li>","63":"<li id=\"id-63\" title=\"Ray Donovan\"><a href=\"http:\/\/vserie.com\/serie\/44-ray-donovan\"><img src=\"http:\/\/vserie.com\/images\/s_s44_s.png\" alt=\"Ray Donovan\"><\/a><\/li>","64":"<li id=\"id-64\" title=\"Ravenswood\"><a href=\"http:\/\/vserie.com\/serie\/93-ravenswood\"><img src=\"http:\/\/vserie.com\/images\/s_s93_s.png\" alt=\"Ravenswood\"><\/a><\/li>","65":"<li id=\"id-65\" title=\"Psych\"><a href=\"http:\/\/vserie.com\/serie\/203-psych\"><img src=\"http:\/\/vserie.com\/images\/s_s203_s.png\" alt=\"Psych\"><\/a><\/li>","66":"<li id=\"id-66\" title=\"Pretty Little Liars (Peque&ntilde;as mentirosas)\"><a href=\"http:\/\/vserie.com\/serie\/38-pretty-little-liars-peque-ntilde-as-mentirosas\"><img src=\"http:\/\/vserie.com\/images\/s_s38_s.png\" alt=\"Pretty Little Liars (Peque&ntilde;as mentirosas)\"><\/a><\/li>","67":"<li id=\"id-67\" title=\"Power\"><a href=\"http:\/\/vserie.com\/serie\/205-power\"><img src=\"http:\/\/vserie.com\/images\/s_s205_s.png\" alt=\"Power\"><\/a><\/li>","68":"<li id=\"id-68\" title=\"Person of Interest\"><a href=\"http:\/\/vserie.com\/serie\/59-person-of-interest\"><img src=\"http:\/\/vserie.com\/images\/s_s59_s.png\" alt=\"Person of Interest\"><\/a><\/li>","69":"<li id=\"id-69\" title=\"Perdidos (Lost)\"><a href=\"http:\/\/vserie.com\/serie\/112-perdidos-lost\"><img src=\"http:\/\/vserie.com\/images\/s_s112_s.png\" alt=\"Perdidos (Lost)\"><\/a><\/li>","70":"<li id=\"id-70\" title=\"Perception\"><a href=\"http:\/\/vserie.com\/serie\/164-perception\"><img src=\"http:\/\/vserie.com\/images\/s_s164_s.png\" alt=\"Perception\"><\/a><\/li>","71":"<li id=\"id-71\" title=\"Penny Dreadful\"><a href=\"http:\/\/vserie.com\/serie\/195-penny-dreadful\"><img src=\"http:\/\/vserie.com\/images\/s_s195_s.png\" alt=\"Penny Dreadful\"><\/a><\/li>","72":"<li id=\"id-72\" title=\"Peaky Blinders\"><a href=\"http:\/\/vserie.com\/serie\/97-peaky-blinders\"><img src=\"http:\/\/vserie.com\/images\/s_s97_s.png\" alt=\"Peaky Blinders\"><\/a><\/li>","73":"<li id=\"id-73\" title=\"Orphan Black\"><a href=\"http:\/\/vserie.com\/serie\/158-orphan-black\"><img src=\"http:\/\/vserie.com\/images\/s_s158_s.png\" alt=\"Orphan Black\"><\/a><\/li>","74":"<li id=\"id-74\" title=\"Orange Is the New Black\"><a href=\"http:\/\/vserie.com\/serie\/13-orange-is-the-new-black\"><img src=\"http:\/\/vserie.com\/images\/s_s13_s.png\" alt=\"Orange Is the New Black\"><\/a><\/li>"}
            rows = json_object["resultado"]

            data = ""
            for row in rows:
                data = data + rows[row]

            logger.info("data=" + repr(data))

    # Extrae las entradas (carpetas)  
    patron = 'title="([^"]+)"[^<]+<a href="(http.//vserie.com/serie/[^"]+)"><img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedtitle, scrapedurl, scrapedthumbnail in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 show=title))

    if not "/paginador/" in item.url:
        itemlist.append(Item(channel=item.channel, action="series", title=">> Página siguiente",
                             url="http://vserie.com/api/paginador/", extra="tipo=series&last=39", viewmode="movie"))
    else:
        actual = scrapertools.find_single_match(item.extra, "last\=(\d+)")
        siguiente = str(int(actual) + 35)
        itemlist.append(Item(channel=item.channel, action="series", title=">> Página siguiente",
                             url="http://vserie.com/api/paginador/", extra="tipo=series&last=" + siguiente,
                             viewmode="movie"))

    return itemlist


def peliculas(item, data=""):
    logger.info()

    if config.get_setting("zampaseriesaccount") == True:
        login()

    # Descarga la pagina
    if data == "":
        if item.extra == "":
            data = scrapertools.cache_page(item.url)
        else:
            data = scrapertools.cache_page(item.url, post=item.extra)
            # logger.info("data="+data)

            json_object = jsontools.load(data)
            # {"resultado":{"40":"<li id=\"id-40\" title=\"The 100\"><a href=\"http:\/\/vserie.com\/serie\/175-the-100\"><img src=\"http:\/\/vserie.com\/images\/s_s175_s.png\" alt=\"The 100\"><\/a><\/li>","41":"<li id=\"id-41\" title=\"Teen Wolf\"><a href=\"http:\/\/vserie.com\/serie\/25-teen-wolf\"><img src=\"http:\/\/vserie.com\/images\/s_s25_s.png\" alt=\"Teen Wolf\"><\/a><\/li>","42":"<li id=\"id-42\" title=\"Surviving Jack\"><a href=\"http:\/\/vserie.com\/serie\/178-surviving-jack\"><img src=\"http:\/\/vserie.com\/images\/s_s178_s.png\" alt=\"Surviving Jack\"><\/a><\/li>","43":"<li id=\"id-43\" title=\"Supernatural\"><a href=\"http:\/\/vserie.com\/serie\/68-supernatural\"><img src=\"http:\/\/vserie.com\/images\/s_s68_s.png\" alt=\"Supernatural\"><\/a><\/li>","44":"<li id=\"id-44\" title=\"Suits\"><a href=\"http:\/\/vserie.com\/serie\/131-suits\"><img src=\"http:\/\/vserie.com\/images\/s_s131_s.png\" alt=\"Suits\"><\/a><\/li>","45":"<li id=\"id-45\" title=\"Star-Crossed\"><a href=\"http:\/\/vserie.com\/serie\/154-star-crossed\"><img src=\"http:\/\/vserie.com\/images\/s_s154_s.png\" alt=\"Star-Crossed\"><\/a><\/li>","46":"<li id=\"id-46\" title=\"Sons of Anarchy\"><a href=\"http:\/\/vserie.com\/serie\/46-sons-of-anarchy\"><img src=\"http:\/\/vserie.com\/images\/s_s46_s.png\" alt=\"Sons of Anarchy\"><\/a><\/li>","47":"<li id=\"id-47\" title=\"Sleepy Hollow\"><a href=\"http:\/\/vserie.com\/serie\/52-sleepy-hollow\"><img src=\"http:\/\/vserie.com\/images\/s_s52_s.png\" alt=\"Sleepy Hollow\"><\/a><\/li>","48":"<li id=\"id-48\" title=\"Skins\"><a href=\"http:\/\/vserie.com\/serie\/36-skins\"><img src=\"http:\/\/vserie.com\/images\/s_s36_s.png\" alt=\"Skins\"><\/a><\/li>","49":"<li id=\"id-49\" title=\"Sirens\"><a href=\"http:\/\/vserie.com\/serie\/172-sirens\"><img src=\"http:\/\/vserie.com\/images\/s_s172_s.png\" alt=\"Sirens\"><\/a><\/li>","50":"<li id=\"id-50\" title=\"Sin identidad\"><a href=\"http:\/\/vserie.com\/serie\/199-sin-identidad\"><img src=\"http:\/\/vserie.com\/images\/s_s199_s.png\" alt=\"Sin identidad\"><\/a><\/li>","51":"<li id=\"id-51\" title=\"Silicon Valley\"><a href=\"http:\/\/vserie.com\/serie\/179-silicon-valley\"><img src=\"http:\/\/vserie.com\/images\/s_s179_s.png\" alt=\"Silicon Valley\"><\/a><\/li>","52":"<li id=\"id-52\" title=\"Siberia\"><a href=\"http:\/\/vserie.com\/serie\/39-siberia\"><img src=\"http:\/\/vserie.com\/images\/s_s39_s.png\" alt=\"Siberia\"><\/a><\/li>","53":"<li id=\"id-53\" title=\"Sherlock\"><a href=\"http:\/\/vserie.com\/serie\/103-sherlock\"><img src=\"http:\/\/vserie.com\/images\/s_s103_s.png\" alt=\"Sherlock\"><\/a><\/li>","54":"<li id=\"id-54\" title=\"Shameless\"><a href=\"http:\/\/vserie.com\/serie\/142-shameless\"><img src=\"http:\/\/vserie.com\/images\/s_s142_s.png\" alt=\"Shameless\"><\/a><\/li>","55":"<li id=\"id-55\" title=\"Salem\"><a href=\"http:\/\/vserie.com\/serie\/186-salem\"><img src=\"http:\/\/vserie.com\/images\/s_s186_s.png\" alt=\"Salem\"><\/a><\/li>","56":"<li id=\"id-56\" title=\"Rosemary&#039;s Baby (La semilla del diablo)\"><a href=\"http:\/\/vserie.com\/serie\/198-rosemary-039-s-baby-la-semilla-del-diablo\"><img src=\"http:\/\/vserie.com\/images\/s_s198_s.png\" alt=\"Rosemary&#039;s Baby (La semilla del diablo)\"><\/a><\/li>","57":"<li id=\"id-57\" title=\"Ripper Street\"><a href=\"http:\/\/vserie.com\/serie\/100-ripper-street\"><img src=\"http:\/\/vserie.com\/images\/s_s100_s.png\" alt=\"Ripper Street\"><\/a><\/li>","58":"<li id=\"id-58\" title=\"Revolution\"><a href=\"http:\/\/vserie.com\/serie\/62-revolution\"><img src=\"http:\/\/vserie.com\/images\/s_s62_s.png\" alt=\"Revolution\"><\/a><\/li>","59":"<li id=\"id-59\" title=\"Revenge\"><a href=\"http:\/\/vserie.com\/serie\/67-revenge\"><img src=\"http:\/\/vserie.com\/images\/s_s67_s.png\" alt=\"Revenge\"><\/a><\/li>","60":"<li id=\"id-60\" title=\"Resurrection\"><a href=\"http:\/\/vserie.com\/serie\/167-resurrection\"><img src=\"http:\/\/vserie.com\/images\/s_s167_s.png\" alt=\"Resurrection\"><\/a><\/li>","61":"<li id=\"id-61\" title=\"Remedy\"><a href=\"http:\/\/vserie.com\/serie\/161-remedy\"><img src=\"http:\/\/vserie.com\/images\/s_s161_s.png\" alt=\"Remedy\"><\/a><\/li>","62":"<li id=\"id-62\" title=\"Reign\"><a href=\"http:\/\/vserie.com\/serie\/92-reign\"><img src=\"http:\/\/vserie.com\/images\/s_s92_s.png\" alt=\"Reign\"><\/a><\/li>","63":"<li id=\"id-63\" title=\"Ray Donovan\"><a href=\"http:\/\/vserie.com\/serie\/44-ray-donovan\"><img src=\"http:\/\/vserie.com\/images\/s_s44_s.png\" alt=\"Ray Donovan\"><\/a><\/li>","64":"<li id=\"id-64\" title=\"Ravenswood\"><a href=\"http:\/\/vserie.com\/serie\/93-ravenswood\"><img src=\"http:\/\/vserie.com\/images\/s_s93_s.png\" alt=\"Ravenswood\"><\/a><\/li>","65":"<li id=\"id-65\" title=\"Psych\"><a href=\"http:\/\/vserie.com\/serie\/203-psych\"><img src=\"http:\/\/vserie.com\/images\/s_s203_s.png\" alt=\"Psych\"><\/a><\/li>","66":"<li id=\"id-66\" title=\"Pretty Little Liars (Peque&ntilde;as mentirosas)\"><a href=\"http:\/\/vserie.com\/serie\/38-pretty-little-liars-peque-ntilde-as-mentirosas\"><img src=\"http:\/\/vserie.com\/images\/s_s38_s.png\" alt=\"Pretty Little Liars (Peque&ntilde;as mentirosas)\"><\/a><\/li>","67":"<li id=\"id-67\" title=\"Power\"><a href=\"http:\/\/vserie.com\/serie\/205-power\"><img src=\"http:\/\/vserie.com\/images\/s_s205_s.png\" alt=\"Power\"><\/a><\/li>","68":"<li id=\"id-68\" title=\"Person of Interest\"><a href=\"http:\/\/vserie.com\/serie\/59-person-of-interest\"><img src=\"http:\/\/vserie.com\/images\/s_s59_s.png\" alt=\"Person of Interest\"><\/a><\/li>","69":"<li id=\"id-69\" title=\"Perdidos (Lost)\"><a href=\"http:\/\/vserie.com\/serie\/112-perdidos-lost\"><img src=\"http:\/\/vserie.com\/images\/s_s112_s.png\" alt=\"Perdidos (Lost)\"><\/a><\/li>","70":"<li id=\"id-70\" title=\"Perception\"><a href=\"http:\/\/vserie.com\/serie\/164-perception\"><img src=\"http:\/\/vserie.com\/images\/s_s164_s.png\" alt=\"Perception\"><\/a><\/li>","71":"<li id=\"id-71\" title=\"Penny Dreadful\"><a href=\"http:\/\/vserie.com\/serie\/195-penny-dreadful\"><img src=\"http:\/\/vserie.com\/images\/s_s195_s.png\" alt=\"Penny Dreadful\"><\/a><\/li>","72":"<li id=\"id-72\" title=\"Peaky Blinders\"><a href=\"http:\/\/vserie.com\/serie\/97-peaky-blinders\"><img src=\"http:\/\/vserie.com\/images\/s_s97_s.png\" alt=\"Peaky Blinders\"><\/a><\/li>","73":"<li id=\"id-73\" title=\"Orphan Black\"><a href=\"http:\/\/vserie.com\/serie\/158-orphan-black\"><img src=\"http:\/\/vserie.com\/images\/s_s158_s.png\" alt=\"Orphan Black\"><\/a><\/li>","74":"<li id=\"id-74\" title=\"Orange Is the New Black\"><a href=\"http:\/\/vserie.com\/serie\/13-orange-is-the-new-black\"><img src=\"http:\/\/vserie.com\/images\/s_s13_s.png\" alt=\"Orange Is the New Black\"><\/a><\/li>"}
            rows = json_object["resultado"]

            data = ""
            for row in rows:
                # logger.info("rows[row]="+rows[row])
                data = data + rows[row]

            logger.info("data=" + repr(data))

    # Extrae las entradas (carpetas)  
    patron = 'title="([^"]+)"[^<]+<a href="(http.//vserie.com/pelicula/[^"]+)"><img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedtitle, scrapedurl, scrapedthumbnail in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 show=title))

    if not "/paginador/" in item.url:
        itemlist.append(Item(channel=item.channel, action="peliculas", title=">> Página siguiente",
                             url="http://vserie.com/api/paginador/", extra="tipo=peliculas&last=40", viewmode="movie"))
    else:
        actual = scrapertools.find_single_match(item.extra, "last\=(\d+)")
        siguiente = str(int(actual) + 35)
        itemlist.append(Item(channel=item.channel, action="peliculas", title=">> Página siguiente",
                             url="http://vserie.com/api/paginador/", extra="tipo=peliculas&last=" + siguiente,
                             viewmode="movie"))

    return itemlist


def episodios(item):
    logger.info()

    if config.get_setting("zampaseriesaccount") == True:
        login()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data, '<div id="listado">(.*?)</ul>');
    logger.info("data=" + data)

    # Extrae las entradas (carpetas)  
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 show=item.show))

    return itemlist


def findvideos(item):
    logger.info()

    if config.get_setting("zampaseriesaccount") == True:
        login()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    # logger.info("data="+data)

    # Extrae las entradas (carpetas)  
    patron = '<tr[^<]+'
    patron += '<td>([^<]*)</td[^<]+'
    patron += '<td>([^<]*)</td[^<]+'
    patron += '<td>([^<]*)</td[^<]+'
    patron += '<td>([^<]*)</td[^<]+'
    patron += '<td>[^<]*</td[^<]+'
    patron += '<td>[^<]*</td[^<]+'
    patron += '<td class="descarga"><a href="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for nombre_servidor, idioma, subs, calidad, scrapedurl in matches:
        if subs.strip() == "":
            subtitulos = ""
        else:
            subtitulos = scrapertools.htmlclean(" sub " + subs)
        title = "Ver en " + nombre_servidor + " (" + scrapertools.htmlclean(
            idioma) + subtitulos + ") (Calidad " + calidad.strip() + ")"
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, extra=item.url, folder=False))

    return itemlist


def play(item):
    logger.info("url=" + item.url)

    if config.get_setting("zampaseriesaccount") == True:
        login()

    headers = DEFAULT_HEADERS[:]
    headers.append(["Referer", item.extra])

    '''
    21:32:07 T:4560547840  NOTICE: 'GET /serie/104-1x01-sincronizado/temporada-1/capitulo-1/17088" rel="nofollow" target="_blank" class="btn btn-success HTTP/1.1\r\nAccept-Encoding: identity\r\nReferer: http://vserie.com/serie/104-1x01-sincronizado/temporada-1/capitulo-1\r\nHost: vserie.com\r\nCookie: PHPSESSID=fed3f2fbe02705b186646e0a5b4692b8\r\nConnection: close\r\nUser-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12\r\n\r\n'
    '''
    media_url = scrapertools.downloadpage(item.url, header_to_get="location", follow_redirects=False, headers=headers)
    logger.info("media_url=" + media_url)

    itemlist = servertools.find_video_items(data=media_url)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = item.channel

    return itemlist
