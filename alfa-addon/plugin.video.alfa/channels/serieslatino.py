# -*- coding: utf-8 -*-


import re

from channels import autoplay
from channels import filtertools
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

host = 'http://www.serieslatino.tv/'

IDIOMAS = {'Latino': 'Latino', 'Sub Español': 'VOS'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['yourupload', 'openload', 'sendvid']

vars = {
    'ef5ca18f089cf01316bbc967fa10f72950790c39ef5ca18f089cf01316bbc967fa10f72950790c39': 'http://www.estadepelis.com/',
    'b48699bb49d4550f27879deeb948d4f7d9c5949a8': 'embed', 'JzewJkLlrvcFnLelj2ikbA': 'php?url=',
    'p889c6853a117aca83ef9d6523335dc065213ae86': 'player',
    'e20fb341325556c0fc0145ce10d08a970538987': 'http://yourupload.com/embed/'}

tgenero = {"acción": "https://s3.postimg.org/y6o9puflv/accion.png",
           "animación": "https://s13.postimg.org/5on877l87/animacion.png",
           "aventura": "https://s10.postimg.org/6su40czih/aventura.png",
           "belico": "https://s23.postimg.org/71itp9hcr/belica.png",
           "ciencia ficción": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png",
           "comedia": "https://s7.postimg.org/ne9g9zgwb/comedia.png",
           "comedia romántica": "https://s21.postimg.org/xfsj7ua0n/romantica.png",
           "cortometrajes": "https://s15.postimg.org/kluxxwg23/cortometraje.png",
           "crimen": "https://s4.postimg.org/6z27zhirx/crimen.png",
           "cristianas": "https://s7.postimg.org/llo852fwr/religiosa.png",
           "deportivas": "https://s13.postimg.org/xuxf5h06v/deporte.png",
           "drama": "https://s16.postimg.org/94sia332d/drama.png",
           "familiar": "https://s7.postimg.org/6s7vdhqrf/familiar.png",
           "fantasía": "https://s13.postimg.org/65ylohgvb/fantasia.png",
           "guerra": "https://s4.postimg.org/n1h2jp2jh/guerra.png",
           "historia": "https://s15.postimg.org/fmc050h1n/historia.png",
           "intriga": "https://s27.postimg.org/v9og43u2b/intriga.png",
           "misterios": "https://s1.postimg.org/w7fdgf2vj/misterio.png",
           "musical": "https://s29.postimg.org/bbxmdh9c7/musical.png",
           "romance": "https://s15.postimg.org/fb5j8cl63/romance.png",
           "suspenso": "https://s13.postimg.org/wmw6vl1cn/suspenso.png",
           "terror": "https://s7.postimg.org/yi0gij3gb/terror.png",
           "thriller": "https://s22.postimg.org/5y9g0jsu9/thriller.png"}


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(item.clone(title="Series", action="lista", thumbnail='https://s27.postimg.org/iahczwgrn/series.png',
                               fanart='https://s27.postimg.org/iahczwgrn/series.png', extra='peliculas/',
                               url=host + 'lista-de-series/'))

    itemlist.append(
        itemlist[-1].clone(title="Doramas", action="lista", thumbnail='https://s15.postimg.org/sjcthoa6z/doramas.png',
                           fanart='https://s15.postimg.org/sjcthoa6z/doramas.png', url=host + 'lista-de-doramas/',
                           extra='/genero'))

    itemlist.append(
        itemlist[-1].clone(title="Generos", action="generos", thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                           fanart='https://s3.postimg.org/5s9jg2wtf/generos.png', url=host, extra='/genero'))

    itemlist.append(itemlist[-1].clone(title="Buscar", action="search", url=host + 'resultados/?q=',
                                       thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                                       fanart='https://s30.postimg.org/pei7txpa9/buscar.png'))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def lista(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    # logger.debug(data)
    # return
    patron = '<div id=mt-1830 class=item><a href=(.*?)><div class=image><img src=(.*?) alt=(.*?) width=.*? ' \
             'height=.*?class=player>.*?class=ttx>(.*?)<div class=degradado>.*?class=year>(.*?)<\/span><\/div><\/div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot, scrapedyear in matches:
        url = host + scrapedurl
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        title = scrapedtitle + ' ' + scrapedyear
        fanart = ''
        itemlist.append(
            Item(channel=item.channel, action='temporadas', title=scrapedtitle, url=url, thumbnail=thumbnail, plot=plot,
                 fanart=fanart, contentSerieName=scrapedtitle, contentYear=scrapedyear,
                 infoLabels={'year': scrapedyear}))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # Paginacion

    if itemlist != []:
        actual_page_url = item.url
        next_page = scrapertools.find_single_match(data, '<div class=pag_b><a href=(.*?) >Siguiente<\/a><\/div>')
        if next_page != '':
            itemlist.append(Item(channel=item.channel, action="lista", title='Siguiente >>>', url=item.url + next_page,
                                 thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png'))
    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    # logger.debug(data)
    # return

    patron = '<span class=se-t.*?>(.*?)<\/span>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    infoLabels = item.infoLabels
    for scrapedtitle in matches:
        contentSeasonNumber = scrapedtitle.strip('')
        title = 'Temporada %s' % scrapedtitle
        thumbnail = item.thumbnail
        plot = item.plot
        fanart = item.fanart
        infoLabels['season'] = contentSeasonNumber

        itemlist.append(Item(channel=item.channel, action='episodiosxtemp', url=item.url, title=title,
                             contentSerieName=item.contentSerieName, thumbnail=thumbnail, plot=plot, fanart=fanart,
                             contentSeasonNumber=contentSeasonNumber, infoLabels=item.infoLabels))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodiosxtemp", contentSerieName=item.contentSerieName,
                 contentYear=item.contentYear, extra1='library'))

    return itemlist


def episodiosxtemp(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    patron = 'class=numerando>(.*?)x(.*?)<\/div><div class=episodiotitle><a href=(.*?)>(.*?)<\/a><span class=date>.*?'
    matches = re.compile(patron, re.DOTALL).findall(data)
    infoLabels = item.infoLabels
    for scrapedtemp, scrapedep, scrapedurl, scrapedtitle in matches:
        url = host + scrapedurl
        contentEpisodeNumber = scrapedep.strip(' ')
        temp = scrapedtemp.strip(' ')
        title = item.contentSerieName + ' %sx%s' % (temp, contentEpisodeNumber)
        thumbnail = item.thumbnail
        plot = item.plot
        fanart = item.fanart
        infoLabels['episode'] = contentEpisodeNumber
        logger.debug('Nombre: ' + item.contentSerieName)
        infoLabels = item.infoLabels
        if item.extra1 == 'library':
            itemlist.append(
                Item(channel=item.channel, action="findvideos", title=title, fulltitle=item.fulltitle, url=url,
                     thumbnail=item.thumbnail, plot=plot, contentSerieName=item.contentSerieName,
                     contentSeasonNumber=item.contentSeasonNumber, infoLabels=infoLabels))
        elif temp == item.contentSeasonNumber:
            itemlist.append(
                Item(channel=item.channel, action="findvideos", title=title, fulltitle=item.fulltitle, url=url,
                     thumbnail=item.thumbnail, plot=plot, contentSerieName=item.contentSerieName,
                     contentSeasonNumber=item.contentSeasonNumber, infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    return itemlist


def generos(item):
    logger.info()

    itemlist = []
    norep = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    patron = '<li class=cat-item cat-item-.*?><a href=(.*?)>([^<]+)<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:

        url = host + scrapedurl
        title = scrapedtitle.lower()
        if title in tgenero:
            thumbnail = tgenero[title.lower()]
        else:
            thumbnail = ''

        itemactual = Item(channel=item.channel, action='lista', title=title, url=url, thumbnail=thumbnail,
                          extra=item.extra)

        if title not in norep:
            itemlist.append(itemactual)
            norep.append(itemactual.title)
    return itemlist


def dec(encurl):
    logger.info()
    url = ''
    encurl = encurl.translate(None, "',(,),;")
    encurl = encurl.split('+')

    for cod in encurl:
        if cod in vars:
            url = url + vars[cod]
        else:
            url = url + cod
    return url


def findvideos(item):
    logger.info()

    itemlist = []
    langs = dict()

    data = httptools.downloadpage(item.url).data
    patron = '<a.*?onclick="return (play\d+).*?;".*?> (.*?) <\/a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for key, value in matches:
        langs[key] = value.strip()

    patron = 'function (play\d).*?servidores.*?attr.*?src.*?\+([^;]+);'
    matches = re.compile(patron, re.DOTALL).findall(data)
    title = item.title
    enlace = scrapertools.find_single_match(data,
                                            'var e20fb341325556c0fc0145ce10d08a970538987 =.*?"\/your\.".*?"([^"]+)"')

    for scrapedlang, encurl in matches:

        if 'e20fb34' in encurl:
            url = dec(encurl)
            url = url + enlace

        else:
            url = dec(encurl)
        title = ''
        server = ''
        servers = {'/opl': 'openload', '/your': 'yourupload', '/sen': 'senvid', '/face': 'netutv', '/vk': 'vk'}
        server_id = re.sub(r'.*?embed|\.php.*', '', url)
        if server_id and server_id in servers:
            server = servers[server_id]
        logger.debug('server_id: %s' % server_id)
        logger.debug('langs: %s' % langs)
        if langs[scrapedlang] in list_language:
            language = IDIOMAS[langs[scrapedlang]]
        else:
            language = 'Latino'
        if langs[scrapedlang] == 'Latino':
            idioma = '[COLOR limegreen]LATINO[/COLOR]'
        elif langs[scrapedlang] == 'Sub Español':
            idioma = '[COLOR red]SUB[/COLOR]'

        title = item.contentSerieName + ' (' + server + ') ' + idioma
        plot = item.plot

        thumbnail = servertools.guess_server_thumbnail(title)

        if 'player' not in url and 'php' in url:
            itemlist.append(item.clone(title=title,
                                       url=url,
                                       action="play",
                                       plot=plot,
                                       thumbnail=thumbnail,
                                       server=server,
                                       quality='',
                                       language=language
                                       ))
        logger.debug('url: %s' % url)
    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    if texto != '':
        return lista(item)


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, add_referer=True).data
    if 'your' in item.url:
        item.url = 'http://www.yourupload.com/embed/' + scrapertools.find_single_match(data, 'src=".*?code=(.*?)"')
        itemlist.append(item)
    else:

        itemlist = servertools.find_video_items(data=data)

    return itemlist
