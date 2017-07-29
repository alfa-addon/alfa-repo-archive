# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(
        Item(channel=item.channel, action="ultimos_capitulos", title="Últimos Capitulos", url="http://jkanime.net/"))
    itemlist.append(Item(channel=item.channel, action="ultimos", title="Últimos", url="http://jkanime.net/"))
    itemlist.append(Item(channel=item.channel, action="letras", title="Listado Alfabetico", url="http://jkanime.net/"))
    itemlist.append(Item(channel=item.channel, action="generos", title="Listado por Genero", url="http://jkanime.net/"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar"))

    return itemlist


def ultimos_capitulos(item):
    logger.info()
    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data, '<ul class="ratedul">.+?</ul>')

    data = data.replace('\t', '')
    data = data.replace('\n', '')
    data = data.replace('/thumbnail/', '/image/')

    patron = '<img src="(http://cdn.jkanime.net/assets/images/animes/.+?)" .+?href="(.+?)">(.+?)<.+?span>(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumb, scrapedurl, scrapedtitle, scrapedepisode in matches:
        title = scrapedtitle.strip() + scrapedepisode
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = scrapedthumb
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist


def search(item, texto):
    logger.info()
    if item.url == "":
        item.url = "http://jkanime.net/buscar/%s/"
    texto = texto.replace(" ", "+")
    item.url = item.url % texto
    try:
        return series(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def ultimos(item):
    logger.info()
    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data, '<ul class="latestul">(.*?)</ul>')

    patron = '<a href="([^"]+)">([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(
            Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data, '<div class="genres">(.*?)</div>')

    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(
            Item(channel=item.channel, action="series", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 viewmode="movie_with_plot"))

    return itemlist


def letras(item):
    logger.info()
    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data, '<ul class="animelet">(.*?)</ul>')

    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(
            Item(channel=item.channel, action="series", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 viewmode="movie_with_plot"))

    return itemlist


def series(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas
    '''
    <table class="search">
    <tr>
    <td rowspan="2">
    <a href="http://jkanime.net/basilisk-kouga-ninpou-chou/"><img src="http://jkanime.net/assets/images/animes/thumbnail/basilisk-kouga-ninpou-chou.jpg" width="50" /></a>
    </td>
    <td><a class="titl" href="http://jkanime.net/basilisk-kouga-ninpou-chou/">Basilisk: Kouga Ninpou Chou</a></td>
    <td rowspan="2" style="width:50px; text-align:center;">Serie</td>
    <td rowspan="2" style="width:50px; text-align:center;" >24 Eps</td>
    </tr>
    <tr>
    <td><p>Basilisk, considerada una de las mejores series del genero ninja, nos narra la historia de dos clanes ninja separados por el odio entre dos familias. Los actuales representantes, Kouga Danjo del clan Kouga y Ogen del clan&#8230; <a class="next" href="http://jkanime.net/basilisk-kouga-ninpou-chou/">seguir leyendo</a></p></td>
    </tr>
    </table>
    '''
    patron = '<table class="search[^<]+'
    patron += '<tr[^<]+'
    patron += '<td[^<]+'
    patron += '<a href="([^"]+)"><img src="([^"]+)"[^<]+</a>[^<]+'
    patron += '</td>[^<]+'
    patron += '<td><a[^>]+>([^<]+)</a></td>[^<]+'
    patron += '<td[^>]+>([^<]+)</td>[^<]+'
    patron += '<td[^>]+>([^<]+)</td>[^<]+'
    patron += '</tr>[^<]+'
    patron += '<tr>[^<]+'
    patron += '<td>(.*?)</td>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedthumbnail, scrapedtitle, line1, line2, scrapedplot in matches:
        title = scrapedtitle.strip() + " (" + line1.strip() + ") (" + line2.strip() + ")"
        extra = line2.strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        thumbnail = thumbnail.replace("thumbnail", "image")
        plot = scrapertools.htmlclean(scrapedplot)
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(
            Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail,
                 plot=plot, extra=extra))

    try:
        siguiente = scrapertools.get_match(data, '<a class="listsiguiente" href="([^"]+)" >Resultados Siguientes')
        scrapedurl = urlparse.urljoin(item.url, siguiente)
        scrapedtitle = ">> Pagina Siguiente"
        scrapedthumbnail = ""
        scrapedplot = ""

        itemlist.append(
            Item(channel=item.channel, action="series", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                 plot=scrapedplot, folder=True, viewmode="movie_with_plot"))
    except:
        pass
    return itemlist


def getPagesAndEpisodes(data):
    results = re.findall('href="#pag([0-9]+)">[0-9]+ - ([0-9]+)', data)
    if results:
        return int(results[-1][0]), int(results[-1][1])
    return 1, 0


def episodios(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    scrapedplot = scrapertools.get_match(data, '<meta name="description" content="([^"]+)"/>')
    scrapedthumbnail = scrapertools.find_single_match(data, '<div class="separedescrip">.*?src="([^"]+)"')

    idserie = scrapertools.get_match(data, "ajax/pagination_episodes/(\d+)/")
    logger.info("idserie=" + idserie)
    if " Eps" in item.extra and not "Desc" in item.extra:
        caps_x = item.extra
        caps_x = caps_x.replace(" Eps", "")
        capitulos = int(caps_x)
        paginas = capitulos / 10 + (capitulos % 10 > 0)
    else:
        paginas, capitulos = getPagesAndEpisodes(data)

    logger.info("idserie=" + idserie)
    for numero in range(1, paginas + 1):

        numero_pagina = str(numero)
        headers = []
        headers.append(
            ["User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:16.0) Gecko/20100101 Firefox/16.0"])
        headers.append(["Referer", item.url])
        data2 = scrapertools.cache_page(
            "http://jkanime.net/ajax/pagination_episodes/" + idserie + "/" + numero_pagina + "/")
        logger.info("data2=" + data2)

        '''
        [{"number":"1","title":"Rose of Versailles - 1"},{"number":"2","title":"Rose of Versailles - 2"},{"number":"3","title":"Rose of Versailles - 3"},{"number":"4","title":"Rose of Versailles - 4"},{"number":"5","title":"Rose of Versailles - 5"},{"number":"6","title":"Rose of Versailles - 6"},{"number":"7","title":"Rose of Versailles - 7"},{"number":"8","title":"Rose of Versailles - 8"},{"number":"9","title":"Rose of Versailles - 9"},{"number":"10","title":"Rose of Versailles - 10"}]
        [{"id":"14199","title":"GetBackers - 1","number":"1","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14200","title":"GetBackers - 2","number":"2","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14201","title":"GetBackers - 3","number":"3","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14202","title":"GetBackers - 4","number":"4","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14203","title":"GetBackers - 5","number":"5","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14204","title":"GetBackers - 6","number":"6","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14205","title":"GetBackers - 7","number":"7","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14206","title":"GetBackers - 8","number":"8","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14207","title":"GetBackers - 9","number":"9","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14208","title":"GetBackers - 10","number":"10","animes_id":"122","timestamp":"2012-01-04 16:59:30"}]
        '''
        patron = '"number"\:"(\d+)","title"\:"([^"]+)"'
        matches = re.compile(patron, re.DOTALL).findall(data2)

        # http://jkanime.net/get-backers/1/
        for numero, scrapedtitle in matches:
            title = scrapedtitle.strip()
            url = urlparse.urljoin(item.url, numero)
            thumbnail = scrapedthumbnail
            plot = scrapedplot
            logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

            itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                                 fanart=thumbnail, plot=plot))

    if len(itemlist) == 0:
        try:
            porestrenar = scrapertools.get_match(data,
                                                 '<div[^<]+<span class="labl">Estad[^<]+</span[^<]+<span[^>]+>Por estrenar</span>')
            itemlist.append(Item(channel=item.channel, action="findvideos", title="Serie por estrenar", url="",
                                 thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot,
                                 server="directo", folder=False))
        except:
            pass

    return itemlist
