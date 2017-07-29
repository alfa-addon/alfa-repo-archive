# -*- coding: utf-8 -*-

import re
import urllib
import urlparse

from channels import autoplay
from channels import filtertools
from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item

IDIOMAS = {'latino': 'Latino'}
list_language = IDIOMAS.values()

CALIDADES = {'1080p': '1080p', '720p': '720p', '480p': '480p', '360p': '360p'}
list_quality = CALIDADES.values()
list_servers = ['directo']

host = 'http://doomtv.net/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0 Chrome/58.0.3029.110',
    'Referer': host}

tgenero = {"Comedia": "https://s7.postimg.org/ne9g9zgwb/comedia.png",
           "Suspenso": "https://s13.postimg.org/wmw6vl1cn/suspenso.png",
           "Drama": "https://s16.postimg.org/94sia332d/drama.png",
           "Acción": "https://s3.postimg.org/y6o9puflv/accion.png",
           "Aventura": "https://s10.postimg.org/6su40czih/aventura.png",
           "Romance": "https://s15.postimg.org/fb5j8cl63/romance.png",
           "Animación": "https://s13.postimg.org/5on877l87/animacion.png",
           "Ciencia Ficción": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png",
           "Terror": "https://s7.postimg.org/yi0gij3gb/terror.png",
           "Documentales": "https://s16.postimg.org/7xjj4bmol/documental.png",
           "Musical": "https://s29.postimg.org/bbxmdh9c7/musical.png",
           "Fantasía": "https://s13.postimg.org/65ylohgvb/fantasia.png",
           "Bélico Guerra": "https://s23.postimg.org/71itp9hcr/belica.png",
           "Misterio": "https://s1.postimg.org/w7fdgf2vj/misterio.png",
           "Crimen": "https://s4.postimg.org/6z27zhirx/crimen.png",
           "Biográfia": "https://s15.postimg.org/5lrpbx323/biografia.png",
           "Familia": "https://s7.postimg.org/6s7vdhqrf/familiar.png",
           "Familiar": "https://s7.postimg.org/6s7vdhqrf/familiar.png",
           "Intriga": "https://s27.postimg.org/v9og43u2b/intriga.png",
           "Thriller": "https://s22.postimg.org/5y9g0jsu9/thriller.png",
           "Guerra": "https://s4.postimg.org/n1h2jp2jh/guerra.png",
           "Estrenos": "https://s21.postimg.org/fy69wzm93/estrenos.png",
           "Peleas": "https://s14.postimg.org/we1oyg05t/peleas.png",
           "Policiales": "https://s21.postimg.org/n9e0ci31z/policial.png",
           "Uncategorized": "https://s30.postimg.org/uj5tslenl/otros.png",
           "LGBT": "https://s30.postimg.org/uj5tslenl/otros.png"}


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(
        item.clone(title="Todas",
                   action="lista",
                   thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                   fanart='https://s18.postimg.org/fwvaeo6qh/todas.png',
                   url=host
                   ))

    itemlist.append(
        item.clone(title="Generos",
                   action="seccion",
                   thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                   fanart='https://s3.postimg.org/5s9jg2wtf/generos.png',
                   url=host,
                   extra='generos'
                   ))

    itemlist.append(
        item.clone(title="Mas vistas",
                   action="seccion",
                   thumbnail='https://s9.postimg.org/wmhzu9d7z/vistas.png',
                   fanart='https://s9.postimg.org/wmhzu9d7z/vistas.png',
                   url=host,
                   extra='masvistas'
                   ))

    itemlist.append(
        item.clone(title="Recomendadas",
                   action="lista",
                   thumbnail='https://s12.postimg.org/s881laywd/recomendadas.png',
                   fanart='https://s12.postimg.org/s881laywd/recomendadas.png',
                   url=host,
                   extra='recomendadas'
                   ))

    itemlist.append(
        item.clone(title="Por año",
                   action="seccion",
                   thumbnail='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                   fanart='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                   url=host, extra='poraño'
                   ))

    itemlist.append(
        item.clone(title="Buscar",
                   action="search",
                   url='http://doomtv.net/?s=',
                   thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                   fanart='https://s30.postimg.org/pei7txpa9/buscar.png'
                   ))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def lista(item):
    logger.info()

    itemlist = []
    max_items = 20
    next_page_url = ''

    data = httptools.downloadpage(item.url).data

    if item.extra == 'recomendadas':
        patron = '<a href="(.*?)">.*?'
        patron += '<div class="imgss">.*?'
        patron += '<img src="(.*?)" alt="(.*?)(?:–.*?|\(.*?|&#8211;|").*?'
        patron += '<div class="imdb">.*?'
        patron += '<\/a>.*?'
        patron += '<span class="ttps">.*?<\/span>.*?'
        patron += '<span class="ytps">(.*?)<\/span><\/div>'
    elif item.extra in ['generos', 'poraño', 'buscar']:
        patron = '<div class=movie>.*?<img src=(.*?) alt=(.*?)(?:\s|\/)><a href=(.*?)>.*?'
        patron += '<h2>.*?<\/h2>.*?(?:<span class=year>(.*?)<\/span>)?.*?<\/div>'
    else:
        patron = '<div class="imagen">.*?'
        patron += '<img src="(.*?)" alt="(.*?)(?:–.*?|\(.*?|&#8211;|").*?'
        patron += '<a href="([^"]+)"><(?:span) class="player"><\/span><\/a>.*?'
        patron += 'h2>\s*.*?(?:year)">(.*?)<\/span>.*?<\/div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.next_page != 'b':
        if len(matches) > max_items:
            next_page_url = item.url
            matches = matches[:max_items]
            next_page = 'b'
    else:
        matches = matches[max_items:]
        next_page = 'a'
        patron_next_page = '<div class="siguiente"><a href="(.*?)"|\/\?'
        matches_next_page = re.compile(patron_next_page, re.DOTALL).findall(data)
        if len(matches_next_page) > 0:
            next_page_url = urlparse.urljoin(item.url, matches_next_page[0])

    for scrapedthumbnail, scrapedtitle, scrapedurl, scrapedyear in matches:
        if item.extra == 'recomendadas':
            url = scrapedthumbnail
            title = scrapedurl
            thumbnail = scrapedtitle
        else:
            url = scrapedurl
            thumbnail = scrapedthumbnail
            title = scrapedtitle
        year = scrapedyear
        fanart = ''
        plot = ''

        if 'serie' not in url:
            itemlist.append(
                Item(channel=item.channel,
                     action='findvideos',
                     title=title,
                     url=url,
                     thumbnail=thumbnail,
                     plot=plot,
                     fanart=fanart,
                     contentTitle=title,
                     infoLabels={'year': year},
                     context=autoplay.context
                     ))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # Paginacion
    if next_page_url != '':
        itemlist.append(
            Item(channel=item.channel,
                 action="lista",
                 title='Siguiente >>>',
                 url=next_page_url,
                 thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png',
                 extra=item.extra,
                 next_page=next_page
                 ))
    return itemlist


def seccion(item):
    logger.info()

    itemlist = []
    duplicado = []
    data = httptools.downloadpage(item.url).data

    if item.extra == 'generos':
        data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    accion = 'lista'
    if item.extra == 'masvistas':
        patron = '<b>\d*<\/b>\s*<a href="(.*?)">(.*?<\/a>\s*<span>.*?<\/span>\s*<i>.*?<\/i><\/li>)'
        accion = 'findvideos'
    elif item.extra == 'poraño':
        patron = '<li><a class="ito" HREF="(.*?)">(.*?)<\/a><\/li>'
    else:
        patron = '<li class=cat-item cat-item-.*?><a href=(.*?)>(.*?)<\/i>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url = scrapedurl
        title = scrapedtitle
        thumbnail = ''
        fanart = ''
        plot = ''
        year = ''
        contentTitle = ''
        if item.extra == 'masvistas':
            year = re.findall(r'\b\d{4}\b', scrapedtitle)
            title = re.sub(r'<\/a>\s*<span>.*?<\/span>\s*<i>.*?<\/i><\/li>', '', scrapedtitle)
            contentTitle = title
            title = title + ' (' + year[0] + ')'

        elif item.extra == 'generos':
            title = re.sub(r'<\/a> <i>\d+', '', scrapedtitle)
            cantidad = re.findall(r'.*?<\/a> <i>(\d+)', scrapedtitle)
            th_title = title
            title = title + ' (' + cantidad[0] + ')'
            thumbnail = tgenero[th_title]
            fanart = thumbnail

        if url not in duplicado:
            itemlist.append(
                Item(channel=item.channel,
                     action=accion,
                     title=title,
                     url=url,
                     thumbnail=thumbnail,
                     plot=plot,
                     fanart=fanart,
                     contentTitle=contentTitle,
                     infoLabels={'year': year}
                     ))
            duplicado.append(url)
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    return itemlist


def unpack(packed):
    p, c, k = re.search("}\('(.*)', *\d+, *(\d+), *'(.*)'\.", packed, re.DOTALL).groups()
    for c in reversed(range(int(c))):
        if k.split('|')[c]: p = re.sub(r'(\b%s\b)' % c, k.split('|')[c], p)
        p = p.replace('\\', '')
        p = p.decode('string_escape')
    return p


def getinfo(page_url):
    info = ()
    logger.info()
    data = httptools.downloadpage(page_url).data
    thumbnail = scrapertools.find_single_match(data, '<div class="cover" style="background-image: url\((.*?)\);')
    plot = scrapertools.find_single_match(data, '<h2>Synopsis<\/h2>\s*<p>(.*?)<\/p>')
    info = (plot, thumbnail)

    return info


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    if texto != '':
        return lista(item)


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    # categoria='peliculas'
    try:
        if categoria == 'peliculas':
            item.url = host
        elif categoria == 'infantiles':
            item.url = host + 'category/animacion/'
        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def get_url(item):
    logger.info()
    itemlist = []
    duplicado = []
    patrones = ["{'label':(.*?),.*?'file':'(.*?)'}", "{file:'(.*?redirector.*?),label:'(.*?)'}"]
    data = httptools.downloadpage(item.url, headers=headers, cookies=False).data
    patron = 'class="player-content"><iframe src="(.*?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for option in matches:
        if 'allplayer' in option:
            url = 'http:/' + option.replace('//', '/')
            data = httptools.downloadpage(url, headers=headers, cookies=False).data
            packed = scrapertools.find_single_match(data, "<div id='allplayer'>.*?(eval\(function\(p,a,c,k.*?\)\)\))")
            if packed:
                unpacked = unpack(packed)
                video_urls = []
                if "vimeocdn" in unpacked:

                    streams = scrapertools.find_multiple_matches(unpacked,
                                                                 "{file:'(.*?)',type:'video/.*?',label:'(.*?)'")
                    for video_url, quality in streams:
                        video_urls.append([video_url, quality])
                else:
                    doc_id = scrapertools.find_single_match(unpacked, 'driveid=(.*?)&')
                    doc_url = "http://docs.google.com/get_video_info?docid=%s" % doc_id
                    response = httptools.downloadpage(doc_url, cookies=False)
                    cookies = ""
                    cookie = response.headers["set-cookie"].split("HttpOnly, ")
                    for c in cookie:
                        cookies += c.split(";", 1)[0] + "; "

                    data = response.data.decode('unicode-escape')
                    data = urllib.unquote_plus(urllib.unquote_plus(data))
                    headers_string = "|Cookie=" + cookies

                    url_streams = scrapertools.find_single_match(data, 'url_encoded_fmt_stream_map=(.*)')
                    streams = scrapertools.find_multiple_matches(url_streams,
                                                                 'itag=(\d+)&url=(.*?)(?:;.*?quality=.*?(?:,|&)|&quality=.*?(?:,|&))')

                    itags = {'18': '360p', '22': '720p', '34': '360p', '35': '480p', '37': '1080p', '59': '480p'}
                    for itag, video_url in streams:
                        video_url += headers_string
                        video_urls.append([video_url, itags[itag]])

                for video_item in video_urls:
                    calidad = video_item[1]
                    title = '%s [%s]' % (item.contentTitle, calidad)
                    url = video_item[0]

                    if url not in duplicado:
                        itemlist.append(
                            Item(channel=item.channel,
                                 action='play',
                                 title=title,
                                 url=url,
                                 thumbnail=item.thumbnail,
                                 plot=item.plot,
                                 fanart=item.fanart,
                                 contentTitle=item.contentTitle,
                                 language=IDIOMAS['latino'],
                                 server='directo',
                                 quality=CALIDADES[calidad],
                                 context=item.context
                                 ))
                        duplicado.append(url)
        else:
            itemlist.extend(servertools.find_video_items(data=option))

    for videoitem in itemlist:

        if 'Enlace' in videoitem.title:
            videoitem.channel = item.channel
            videoitem.title = item.contentTitle + ' (' + videoitem.server + ')'
            videoitem.language = 'latino'
            videoitem.quality = 'default'
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist = get_url(item)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(
            Item(channel=item.channel,
                 title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                 url=item.url,
                 action="add_pelicula_to_library",
                 extra="findvideos",
                 contentTitle=item.contentTitle,
                 ))

    return itemlist
