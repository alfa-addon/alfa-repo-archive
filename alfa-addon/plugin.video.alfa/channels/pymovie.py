# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

host = "http://www.pymovie.com.mx"

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'],
           ['Referer', host]]

tgenero = {"comedia": "https://s7.postimg.org/ne9g9zgwb/comedia.png",
           "drama": "https://s16.postimg.org/94sia332d/drama.png",
           "accion": "https://s3.postimg.org/y6o9puflv/accion.png",
           "aventura": "https://s10.postimg.org/6su40czih/aventura.png",
           "romance": "https://s15.postimg.org/fb5j8cl63/romance.png",
           "animacion": "https://s13.postimg.org/5on877l87/animacion.png",
           "ciencia ficcion": "https://s9.postimg.org/diu70s7j3/cienciaficcion.png",
           "terror": "https://s7.postimg.org/yi0gij3gb/terror.png",
           "musical": "https://s29.postimg.org/bbxmdh9c7/musical.png",
           "deporte": "https://s13.postimg.org/xuxf5h06v/deporte.png",
           "artes Marciales": "https://s24.postimg.org/w1aw45j5h/artesmarciales.png",
           "intriga": "https://s27.postimg.org/v9og43u2b/intriga.png",
           "infantil": "https://s23.postimg.org/g5rmazozv/infantil.png",
           "mexicanas": "https://s3.postimg.org/p36ntnxfn/mexicana.png",
           "espionaje": "https://s2.postimg.org/5hv64b989/espionaje.png",
           "biografia": "https://s15.postimg.org/5lrpbx323/biografia.png"}

tcalidad = {'hd-1080': '[COLOR limegreen]HD-1080[/COLOR]', 'hd-720': '[COLOR limegreen]HD-720[/COLOR]',
            'blueray': '[COLOR limegreen]BLUERAY[/COLOR]', 'dvd': '[COLOR limegreen]DVD[/COLOR]',
            'cam': '[COLOR red]CAM[/COLOR]'}

tcalidad2 = {'hd-1080': 'https://s21.postimg.org/4h1s0t1wn/hd1080.png',
             'hd-720': 'https://s12.postimg.org/lthu7v4q5/hd720.png', 'blueray': '',
             'dvd': 'https://s1.postimg.org/m89hus1tb/dvd.png', 'cam': 'https://s11.postimg.org/ad4o5wpz7/cam.png'}


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Peliculas", action="menupeliculas",
                               thumbnail='https://s8.postimg.org/6wqwy2c2t/peliculas.png',
                               fanart='https://s8.postimg.org/6wqwy2c2t/peliculas.png', extra='peliculas/'))

    itemlist.append(itemlist[-1].clone(title="Series", action="menuseries",
                                       thumbnail='https://s27.postimg.org/iahczwgrn/series.png',
                                       fanart='https://s27.postimg.org/iahczwgrn/series.png', extra='peliculas/'))

    itemlist.append(itemlist[-1].clone(title="Documentales", action="menudocumental",
                                       thumbnail='https://s16.postimg.org/7xjj4bmol/documental.png',
                                       fanart='https://s16.postimg.org/7xjj4bmol/documental.png', extra='documental'))

    return itemlist


def menupeliculas(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Ultimas", action="lista", url=host + '/Ordenar/Estreno/?page=1',
                         thumbnail='https://s22.postimg.org/cb7nmhwv5/ultimas.png',
                         fanart='https://s22.postimg.org/cb7nmhwv5/ultimas.png', extra='Estreno'))

    itemlist.append(Item(channel=item.channel, title="Todas", action="lista", url=host + '?page=1',
                         thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                         fanart='https://s18.postimg.org/fwvaeo6qh/todas.png', extra='todas'))

    itemlist.append(Item(channel=item.channel, title="Generos", action="seccion", url=host,
                         thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                         fanart='https://s3.postimg.org/5s9jg2wtf/generos.png', extra='generos'))

    itemlist.append(
        Item(channel=item.channel, title="Alfabetico", action="lista", url=host + '/Ordenar/Alfabetico/?page=1',
             thumbnail='https://s17.postimg.org/fwi1y99en/a-z.png', fanart='https://s17.postimg.org/fwi1y99en/a-z.png',
             extra='Alfabetico'))

    itemlist.append(Item(channel=item.channel, title="Calidad", action="seccion", url=host,
                         thumbnail='https://s13.postimg.org/6nzv8nlkn/calidad.png',
                         fanart='https://s13.postimg.org/6nzv8nlkn/calidad.png', extra='calidad'))

    itemlist.append(
        Item(channel=item.channel, title="Mas Vistas", action="lista", url=host + '/Ordenar/MasVistas/?page=1',
             thumbnail='https://s9.postimg.org/wmhzu9d7z/vistas.png',
             fanart='https://s9.postimg.org/wmhzu9d7z/vistas.png', extra='Estreno'))

    itemlist.append(
        Item(channel=item.channel, title="Mas Votadas", action="lista", url=host + '/Ordenar/MasVotos/?page=1',
             thumbnail='https://s7.postimg.org/9kg1nthzf/votadas.png',
             fanart='https://s7.postimg.org/9kg1nthzf/votadas.png', extra='Estreno'))

    itemlist.append(
        Item(channel=item.channel, title="Calificacion", action="lista", url=host + '/Ordenar/Calificacion/?page=1',
             thumbnail='https://s18.postimg.org/mjqrl49h5/calificacion.png',
             fanart='https://s18.postimg.org/mjqrl49h5/calificacion.png', extra='Estreno'))

    return itemlist


def menuseries(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Ultimas", action="lista", url=host + "/Series-estreno/?page=1",
                         thumbnail='https://s22.postimg.org/cb7nmhwv5/ultimas.png',
                         fanart='https://s22.postimg.org/cb7nmhwv5/ultimas.png', extra='series'))

    itemlist.append(Item(channel=item.channel, title="Generos", action="seccion", url=host,
                         thumbnail='https://s3.postimg.org/5s9jg2wtf/generos.png',
                         fanart='https://s3.postimg.org/5s9jg2wtf/generos.png', extra='series-generos'))

    itemlist.append(
        Item(channel=item.channel, title="Alfabetico", action="lista", url=host + '/Ordernar-Serie/Alfabetico/?page=1',
             thumbnail='https://s17.postimg.org/fwi1y99en/a-z.png', fanart='https://s17.postimg.org/fwi1y99en/a-z.png',
             extra='series-alpha'))

    itemlist.append(
        Item(channel=item.channel, title="Mas Vistas", action="lista", url=host + '/Ordernar-Serie/MasVistas/?page=1',
             thumbnail='https://s9.postimg.org/wmhzu9d7z/vistas.png',
             fanart='https://s9.postimg.org/wmhzu9d7z/vistas.png', extra='series-masvistas'))

    itemlist.append(
        Item(channel=item.channel, title="Mas Votadas", action="lista", url=host + '/Ordernar-Serie/Masvotos/?page=1',
             thumbnail='https://s7.postimg.org/9kg1nthzf/votadas.png',
             fanart='https://s7.postimg.org/9kg1nthzf/votadas.png', extra='series-masvotadas'))

    itemlist.append(Item(channel=item.channel, title="Recomendadas", action="lista",
                         url=host + '/Ordernar-Serie/Recomendadas/?page=1',
                         thumbnail='https://s12.postimg.org/s881laywd/recomendadas.png',
                         fanart='https://s12.postimg.org/s881laywd/recomendadas.png', extra='series-recomendadas'))

    return itemlist


def menudocumental(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Todas", action="lista", url=host + "/Documentales/?page=1",
                         thumbnail='https://s18.postimg.org/fwvaeo6qh/todas.png',
                         fanart='https://s18.postimg.org/fwvaeo6qh/todas.png', extra='documental'))

    itemlist.append(Item(channel=item.channel, title="Alfabetico", action="lista",
                         url=host + "/OrdenarDocumental/Alfabetico/?page=1",
                         thumbnail='https://s17.postimg.org/fwi1y99en/a-z.png',
                         fanart='https://s17.postimg.org/fwi1y99en/a-z.png', extra='documental'))

    itemlist.append(Item(channel=item.channel, title="Mas Vistas", action="lista",
                         url=host + "/OrdenarDocumental/MasVistas/?page=1",
                         thumbnail='https://s9.postimg.org/wmhzu9d7z/vistas.png',
                         fanart='https://s9.postimg.org/wmhzu9d7z/vistas.png', extra='documental'))

    return itemlist


def lista(item):
    logger.info()

    if item.extra == 'series':
        accion = 'episodiosxtemp'
    elif 'series-' in item.extra:
        accion = 'temporadas'
    else:
        accion = 'findvideos'

    itemlist = []
    data = httptools.downloadpage(item.url).data

    if 'series' in item.extra or item.extra == 'documental':
        patron = '<h2 itemprop="name" >([^<]+)<\/h2><a href="([^.]+)" title=".*?" ><img.*?src="([^"]+)".*?class=".*?boren2"\/([^<]+)'
    else:
        patron = '<h2 itemprop="name" >([^<]+)<\/h2><a href="([^.]+)" title=".*?" ><img.*?src="([^"]+)".*?class=".*?boren2".*?>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl, scrapedthumbnail, scrapedcalidad in matches:
        url = scrapertools.decodeHtmlentities(host + scrapedurl)
        url = url.strip(' ')

        scrapedcalidad = scrapedcalidad.strip(' ')
        scrapedcalidad = scrapedcalidad.strip('p')
        scrapedcalidad = scrapedcalidad.lower()
        if 'series' in item.extra or item.extra == 'documental':
            title = scrapertools.decodeHtmlentities(scrapedtitle)
        else:
            calidad = tcalidad[scrapedcalidad]
            title = scrapertools.decodeHtmlentities(scrapedtitle) + ' (' + calidad + ') '

        thumbnail = scrapedthumbnail
        fanart = ''
        plot = ''

        itemlist.append(Item(channel=item.channel, action=accion, title=title, url=url, thumbnail=thumbnail, plot=plot,
                             fanart=fanart, contentSerieName=scrapedtitle, contentTitle=scrapedtitle, extra=item.extra))

        # Paginacion
    if itemlist != []:
        actual_page_url = item.url
        next_page = scrapertools.find_single_match(data, '<a href="\?page=([^"]+)" class="next">next &')
        while item.url[-1] != '=':
            item.url = item.url[:-1]
        next_page_url = item.url + next_page
        if next_page != '':
            itemlist.append(Item(channel=item.channel, action="lista", title='Siguiente >>>', url=next_page_url,
                                 thumbnail='https://s16.postimg.org/9okdu7hhx/siguiente.png', extra=item.extra))
    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []
    templist = []
    data = httptools.downloadpage(item.url).data

    patron = 'class="listatemporadas" ><a href="([^"]+)" title=".*?"  ><img src="([^"]+)"  width="80" height="100" title=".*?alt=".*?<h3>([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        url = host + scrapedurl
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ''
        fanart = ''
        contentSeasonNumber = scrapedtitle.replace('Temporada ', '')

        itemlist.append(Item(channel=item.channel, action="episodiosxtemp", title=title, fulltitle=item.title, url=url,
                             thumbnail=thumbnail, plot=plot, fanart=fanart, contentSerieName=item.contentSerieName,
                             contentSeasonNumber=contentSeasonNumber))

    if item.extra == 'temporadas':
        for tempitem in itemlist:
            templist += episodiosxtemp(tempitem)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = temporadas(item)
    for tempitem in templist:
        itemlist += episodiosxtemp(tempitem)

    return itemlist


def episodiosxtemp(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<a href="\/VerCapitulo\/([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    ep = 1
    for scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace(item.contentSeasonNumber + 'x' + '0' + str(ep), '')
        url = host + '/VerCapitulo/' + scrapedtitle.replace(' ', '-')
        title = item.contentSeasonNumber + 'x' + str(ep) + ' ' + scrapedtitle.strip('/')

        thumbnail = item.thumbnail
        plot = ''
        fanart = ''
        plot = ''
        contentEpisodeNumber = ep

        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, fulltitle=item.title, url=url,
                             thumbnail=thumbnail, plot=plot, fanart=fanart, extra='series',
                             contentSerieName=item.contentSerieName, contentSeasonNumber=item.contentSeasonNumber,
                             contentEpisodeNumber=contentEpisodeNumber))
        ep = ep + 1

    return itemlist


def seccion(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<option class="opselect" value="([^"]+)".*?>([^<]+)<\/option>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if item.extra == 'generos':
        oplista = tgenero
        opdir = '/Categoria/'
    elif item.extra == 'calidad':
        oplista = tcalidad
        opdir = '/Calidad/'
    elif item.extra == 'series-generos':
        oplista = tgenero
        opdir = '/Categoria-Series/'

    for scrapeddir, scrapedtitle in matches:

        url = item.url + opdir + scrapeddir + '/?page=1'
        title = scrapedtitle.upper()

        if 'generos' in item.extra and scrapedtitle.lower() in oplista:
            thumbnail = oplista[scrapedtitle.lower()]
            fanart = oplista[scrapedtitle.lower()]

        elif 'calidad' in item.extra and scrapedtitle.lower() in oplista:
            thumbnail = tcalidad2[scrapedtitle.lower()]
            fanart = tcalidad[scrapedtitle.lower()]

        else:
            thumbnail = ''
            fanart = ''

        if scrapedtitle.lower() in oplista:
            itemlist.append(Item(channel=item.channel, action="lista", title=title, fulltitle=item.title, url=url,
                                 thumbnail=thumbnail, fanart=fanart, extra=item.extra))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    audio = {'Latino': '[COLOR limegreen]LATINO[/COLOR]', 'Español': '[COLOR yellow]ESPAÑOL[/COLOR]',
             'Ingles': '[COLOR red]ORIGINAL SUBTITULADO[/COLOR]', 'Latino-Ingles': 'DUAL'}
    data = httptools.downloadpage(item.url).data

    if item.extra != 'series':
        patron = 'data-video="([^"]+)" class="reproductorVideo"><ul><li>([^<]+)<\/li><li>([^<]+)<\/li>'
        tipotitle = item.contentTitle
    elif item.extra == 'series':
        tipotitle = str(item.contentSeasonNumber) + 'x' + str(item.contentEpisodeNumber) + ' ' + item.contentSerieName
        patron = '<li class="enlaces-l"><a href="([^"]+)" target="_blank"><ul><li>([^<]+)<.*?>([^<]+)<.*?>Reproducir<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.extra != 'documental':
        n = 0

        for scrapedurl, scrapedcalidad, scrapedaudio in matches:
            if 'series' in item.extra:
                datab = httptools.downloadpage(host + scrapedurl).data
                url = scrapertools.find_single_match(datab, 'class="reproductor"><iframe src="([^"]+)"')
                print url + 'esta es la direccion'
            else:
                url = scrapedurl

            title = tipotitle
            idioma = audio[scrapedaudio]
            itemlist.extend(servertools.find_video_items(data=url))
            if n < len(itemlist):
                itemlist[n].title = tipotitle + ' (' + idioma + ' ) ' + '(' + itemlist[n].server + ' )'
            n = n + 1
    else:
        url = scrapertools.find_single_match(data, 'class="reproductor"><iframe src="([^"]+)"')
        itemlist.extend(servertools.find_video_items(data=url))

    for videoitem in itemlist:
        if item.extra == 'documental':
            videoitem.title = item.title + ' (' + videoitem.server + ')'
        videoitem.channel = item.channel
        videoitem.action = "play"
        videoitem.folder = False

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'series':
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                 action="add_pelicula_to_library", extra="findvideos", contentTitle=item.contentTitle))

    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    item.extra = 'Estrenos'
    try:
        if categoria == 'peliculas':
            item.url = host + '/Ordenar/Estreno/?page=1'

        elif categoria == 'infantiles':
            item.url = host + '/Categoria/Animacion/?page=1'

        elif categoria == 'documentales':
            item.url = host + '/Documentales/?page=1'
            item.extra = 'documental'

        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
