# -*- coding: utf-8 -*-

import re
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

IDIOMAS = {'latino': 'Latino', 'castellano': 'Español', 'portugues': 'Portugues'}
list_language = IDIOMAS.values()
logger.debug('lista_language: %s' % list_language)

list_quality = ['1080p', '720p', '480p', '360p', '240p', 'default']
list_servers = [
    'yourupload',
    'thevideos',
    'filescdn',
    'uptobox',
    'okru',
    'nowvideo',
    'userscloud',
    'pcloud',
    'usersfiles',
    'vidbull',
    'openload',
    'directo'
]

host = 'http://www.cinecalidad.to'
thumbmx = 'http://flags.fmcdn.net/data/flags/normal/mx.png'
thumbes = 'http://flags.fmcdn.net/data/flags/normal/es.png'
thumbbr = 'http://flags.fmcdn.net/data/flags/normal/br.png'


def mainlist(item):
    idioma2 = "destacadas"
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(
        item.clone(title="CineCalidad Latino",
                   action="submenu",
                   host="http://cinecalidad.com/",
                   thumbnail=thumbmx,
                   extra="peliculas",
                   language='latino'
                   ))

    itemlist.append(item.clone(title="CineCalidad España",
                               action="submenu",
                               host="http://cinecalidad.com/espana/",
                               thumbnail=thumbes,
                               extra="peliculas",
                               language='castellano'
                               ))

    itemlist.append(
        item.clone(title="CineCalidad Brasil",
                   action="submenu",
                   host="http://cinemaqualidade.com/",
                   thumbnail=thumbbr,
                   extra="filmes",
                   language='portugues'
                   ))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def submenu(item):
    idioma = 'peliculas'
    idioma2 = "destacada"
    host = item.host
    if item.host == "http://cinemaqualidade.com/":
        idioma = "filmes"
        idioma2 = "destacado"
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel,
                         title=idioma.capitalize(),
                         action="peliculas",
                         url=host,
                         thumbnail='https://s8.postimg.org/6wqwy2c2t/peliculas.png',
                         fanart='https://s8.postimg.org/6wqwy2c2t/peliculas.png',
                         language=item.language
                         ))
    itemlist.append(Item(channel=item.channel,
                         title="Destacadas",
                         action="peliculas",
                         url=host + "/genero-" + idioma + "/" + idioma2 + "/",
                         thumbnail='https://s30.postimg.org/humqxklsx/destacadas.png',
                         fanart='https://s30.postimg.org/humqxklsx/destacadas.png',
                         language=item.language
                         ))
    itemlist.append(Item(channel=item.channel,
                         title="Generos",
                         action="generos",
                         url=host + "/genero-" + idioma,
                         thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                         fanart='https://s3.postimg.org/5s9jg2wtf/generos.png',
                         language=item.language
                         ))
    itemlist.append(Item(channel=item.channel,
                         title="Por Año",
                         action="anyos",
                         url=host + "/" + idioma + "-por-ano",
                         thumbnail='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                         fanart='https://s8.postimg.org/7eoedwfg5/pora_o.png',
                         language=item.language
                         ))
    itemlist.append(Item(channel=item.channel,
                         title="Buscar",
                         action="search",
                         thumbnail='https://s30.postimg.org/pei7txpa9/buscar.png',
                         url=host + '/apiseries/seriebyword/',
                         fanart='https://s30.postimg.org/pei7txpa9/buscar.png',
                         host=item.host,
                         language=item.language
                         ))

    return itemlist


def anyos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<a href="([^"]+)">([^<]+)</a> '
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        title = scrapedtitle
        thumbnail = item.thumbnail
        plot = item.plot
        itemlist.append(
            Item(channel=item.channel,
                 action="peliculas",
                 title=title,
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 fanart=item.thumbnail,
                 language=item.language
                 ))

    return itemlist


def generos(item):
    tgenero = {"Comedia": "https://s7.postimg.org/ne9g9zgwb/comedia.png",
               "Suspenso": "https://s13.postimg.org/wmw6vl1cn/suspenso.png",
               "Drama": "https://s16.postimg.org/94sia332d/drama.png",
               "Acción": "https://s3.postimg.org/y6o9puflv/accion.png",
               "Aventura": "https://s10.postimg.org/6su40czih/aventura.png",
               "Romance": "https://s15.postimg.org/fb5j8cl63/romance.png",
               "Fantas\xc3\xada": "https://s13.postimg.org/65ylohgvb/fantasia.png",
               "Infantil": "https://s23.postimg.org/g5rmazozv/infantil.png",
               "Ciencia ficción": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png",
               "Terror": "https://s7.postimg.org/yi0gij3gb/terror.png",
               "Com\xc3\xa9dia": "https://s7.postimg.org/ne9g9zgwb/comedia.png",
               "Suspense": "https://s13.postimg.org/wmw6vl1cn/suspenso.png",
               "A\xc3\xa7\xc3\xa3o": "https://s3.postimg.org/y6o9puflv/accion.png",
               "Fantasia": "https://s13.postimg.org/65ylohgvb/fantasia.png",
               "Fic\xc3\xa7\xc3\xa3o cient\xc3\xadfica": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png"}
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<li id="menu-item-.*?" class="menu-item menu-item-type-taxonomy menu-item-object-category ' \
             'menu-item-.*?"><a href="([^"]+)">([^<]+)<\/a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        title = scrapedtitle
        thumbnail = tgenero[scrapedtitle]
        plot = item.plot
        itemlist.append(
            Item(channel=item.channel,
                 action="peliculas",
                 title=title, url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 fanart=item.thumbnail,
                 language=item.language
                 ))

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data

    patron = '<div class="home_post_cont.*? post_box">.*?<a href="([^"]+)".*?src="([^"]+)".*?title="(.*?) \((' \
             '.*?)\)".*?p&gt;([^&]+)&lt;'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedyear, scrapedplot in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        contentTitle = scrapedtitle
        title = scrapedtitle + ' (' + scrapedyear + ')'
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        year = scrapedyear
        itemlist.append(
            Item(channel=item.channel,
                 action="findvideos",
                 title=title,
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 fanart='https://s31.postimg.org/puxmvsi7v/cinecalidad.png',
                 contentTitle=contentTitle,
                 infoLabels={'year': year},
                 language=item.language,
                 context=autoplay.context
                 ))

    try:
        patron = "<link rel='next' href='([^']+)' />"
        next_page = re.compile(patron, re.DOTALL).findall(data)
        itemlist.append(Item(channel=item.channel,
                             action="peliculas",
                             title="Página siguiente >>",
                             url=next_page[0],
                             fanart='https://s31.postimg.org/puxmvsi7v/cinecalidad.png',
                             language=item.language
                             ))

    except:
        pass
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    return itemlist


def dec(item):
    link = []
    val = item.split(' ')
    link = map(int, val)
    for i in range(len(link)):
        link[i] = link[i] - 7
        real = ''.join(map(chr, link))
    return (real)


def findvideos(item):
    servidor = {"http://uptobox.com/": "uptobox",
                "http://userscloud.com/": "userscloud",
                "https://my.pcloud.com/publink/show?code=": "pcloud",
                "http://thevideos.tv/": "thevideos",
                "http://ul.to/": "uploadedto",
                "http://turbobit.net/": "turbobit",
                "http://www.cinecalidad.com/protect/v.html?i=": "cinecalidad",
                "http://www.mediafire.com/download/": "mediafire",
                "https://www.youtube.com/watch?v=": "youtube",
                "http://thevideos.tv/embed-": "thevideos",
                "//www.youtube.com/embed/": "youtube",
                "http://ok.ru/video/": "okru",
                "http://ok.ru/videoembed/": "okru",
                "http://www.cinemaqualidade.com/protect/v.html?i=": "cinemaqualidade.com",
                "http://usersfiles.com/": "usersfiles",
                "https://depositfiles.com/files/": "depositfiles",
                "http://www.nowvideo.sx/video/": "nowvideo",
                "http://vidbull.com/": "vidbull",
                "http://filescdn.com/": "filescdn",
                "https://www.yourupload.com/watch/": "yourupload",
                "http://www.cinecalidad.to/protect/gdredirect.php?l=": "directo",
                "https://openload.co/embed/": "openload"
                }

    logger.info()
    itemlist = []
    duplicados = []
    data = httptools.downloadpage(item.url).data

    patron = 'dec\("([^"]+)"\)\+dec\("([^"]+)"\)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    recomendados = ["uptobox", "thevideos", "nowvideo", "pcloud", "directo"]
    for scrapedurl, scrapedtitle in matches:

        if dec(scrapedurl) in servidor:
            server = servidor[dec(scrapedurl)]
            title = "Ver " + item.contentTitle + " en " + servidor[dec(scrapedurl)].upper()
            if 'yourupload' in dec(scrapedurl):
                url = dec(scrapedurl).replace('watch', 'embed') + dec(scrapedtitle)
            elif 'gdredirect' in dec(scrapedurl):
                url = ''
                url_list = []
                url_list += get_urls(item, dec(scrapedtitle))

                for video in url_list:
                    new_title = title + ' (' + video['label'] + ')'
                    itemlist.append(
                        Item(channel=item.channel,
                             action="play",
                             title=new_title,
                             fulltitle=item.title,
                             url=video['file'],
                             language=IDIOMAS[item.language],
                             thumbnail=item.thumbnail,
                             plot=item.plot,
                             quality=video['label'],
                             server='directo'
                             ))
                    duplicados.append(title)
            else:

                if 'youtube' in dec(scrapedurl):
                    title = '[COLOR orange]Trailer en Youtube[/COLOR]'
                url = dec(scrapedurl) + dec(scrapedtitle)

            if (servidor[dec(scrapedurl)]) in recomendados:
                title = title + "[COLOR limegreen] [I] (Recomedado) [/I] [/COLOR]"
            thumbnail = servertools.guess_server_thumbnail(servidor[dec(scrapedurl)])
            plot = ""
            if title not in duplicados and url != '':
                new_item = Item(channel=item.channel,
                                action="play",
                                title=title,
                                fulltitle=item.title,
                                url=url,
                                thumbnail=thumbnail,
                                plot=item.plot,
                                extra=item.thumbnail,
                                language=IDIOMAS[item.language],
                                quality='default',
                                server=server.lower()
                                )
                if 'Trailer' in new_item.title:
                    trailer_item = new_item
                else:
                    itemlist.append(new_item)
            duplicados.append(title)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    itemlist.append(trailer_item)
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


def get_urls(item, link):
    from core import jsontools
    logger.info()
    url = 'http://www.cinecalidad.to/ccstream/ccstream.php'
    headers = dict()
    headers["Referer"] = item.url
    post = 'link=%s' % link

    data = httptools.downloadpage(url, post=post, headers=headers).data
    dict_data = jsontools.load(data)
    logger.debug(dict_data['link'])
    logger.debug(data)
    return dict_data['link']


def play(item):
    logger.info()
    itemlist = []
    logger.debug('item: %s' % item)
    if 'juicyapi' not in item.url:
        itemlist = servertools.find_video_items(data=item.url)

        for videoitem in itemlist:
            videoitem.title = item.fulltitle
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.extra
            videoitem.channel = item.channel
    else:
        itemlist.append(item)

    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = 'http://www.cinecalidad.to'
        elif categoria == 'infantiles':
            item.url = 'http://www.cinecalidad.to/genero-peliculas/infantil/'
        itemlist = peliculas(item)
        if itemlist[-1].title == 'Página siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def busqueda(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    from core import jsontools
    data = jsontools.load(data)

    for entry in data["results"]:
        title = entry["richSnippet"]["metatags"]["ogTitle"]
        url = entry["url"]
        plot = entry["content"]
        plot = scrapertools.htmlclean(plot)
        thumbnail = entry["richSnippet"]["metatags"]["ogImage"]
        title = scrapertools.find_single_match(title, '(.*?) \(.*?\)')
        year = re.sub(r'.*?\((\d{4})\)', '', title)
        title = year
        fulltitle = title

        new_item = item.clone(action="findvideos",
                              title=title,
                              fulltitle=fulltitle,
                              url=url,
                              thumbnail=thumbnail,
                              contentTitle=title,
                              contentType="movie",
                              plot=plot,
                              infoLabels={'year': year, 'sinopsis': plot}
                              )
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    actualpage = int(scrapertools.find_single_match(item.url, 'start=(\d+)'))
    totalresults = int(data["cursor"]["resultCount"])
    if actualpage + 20 <= totalresults:
        url_next = item.url.replace("start=" + str(actualpage), "start=" + str(actualpage + 20))
        itemlist.append(
            Item(channel=item.channel,
                 action="busqueda",
                 title=">> Página Siguiente",
                 url=url_next
                 ))

    return itemlist


def search(item, texto):
    logger.info()

    data = httptools.downloadpage(host).data
    cx = scrapertools.find_single_match(data, 'name="cx" value="(.*?)"')
    texto = texto.replace(" ", "%20")
    item.url = "https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz" \
               "=filtered_cse&num=20&hl=es&sig=0c3990ce7a056ed50667fe0c3873c9b6&cx=%s&q=%s&sort=&googlehost=www" \
               ".google.com&start=0" % (cx, texto)

    try:
        return busqueda(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
