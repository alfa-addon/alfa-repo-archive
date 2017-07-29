# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="submenu", title="Películas", url="http://www.newpct1.com/",
                         extra="peliculas"))
    itemlist.append(
        Item(channel=item.channel, action="submenu", title="Series", url="http://www.newpct1.com/", extra="series"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar"))

    return itemlist


def search(item, texto):
    logger.info("search:" + texto)
    texto = texto.replace(" ", "+")
    item.url = "http://www.newpct1.com/index.php?page=buscar&q=%27" + texto + "%27&ordenar=Fecha&inon=Descendente"
    item.extra = "buscar-list"
    try:
        itemlist = completo(item)

        # Esta pagina coloca a veces contenido duplicado, intentamos descartarlo
        dict_aux = {}
        for i in itemlist:
            if not i.url in dict_aux:
                dict_aux[i.url] = i
            else:
                itemlist.remove(i)

        return itemlist


    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def submenu(item):
    logger.info()
    itemlist = []

    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url).data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")

    patron = '<li><a href="http://www.newpct1.com/' + item.extra + '/">.*?<ul>(.*?)</ul>'
    data = scrapertools.get_match(data, patron)

    patron = '<a href="([^"]+)".*?>([^>]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = scrapedurl

        itemlist.append(Item(channel=item.channel, action="listado", title=title, url=url, extra="pelilist"))
        itemlist.append(
            Item(channel=item.channel, action="alfabeto", title=title + " [A-Z]", url=url, extra="pelilist"))

    return itemlist


def alfabeto(item):
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

        itemlist.append(Item(channel=item.channel, action="completo", title=title, url=url, extra=item.extra))

    return itemlist


def listado(item):
    logger.info()
    # logger.info("[newpct1.py] listado url=" + item.url)
    itemlist = []

    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url).data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")

    patron = '<ul class="' + item.extra + '">(.*?)</ul>'
    logger.debug("patron=" + patron)
    fichas = scrapertools.get_match(data, patron)

    # <li><a href="http://www.newpct1.com/pelicula/x-men-dias-del-futuro-pasado/ts-screener/" title="Descargar XMen Dias Del Futuro gratis"><img src="http://www.newpct1.com/pictures/f/58066_x-men-dias-del-futuro--blurayrip-ac3-5.1.jpg" width="130" height="180" alt="Descargar XMen Dias Del Futuro gratis"><h2>XMen Dias Del Futuro </h2><span>BluRayRip AC3 5.1</span></a></li>
    patron = '<li><a href="([^"]+).*?'  # url
    patron += 'title="([^"]+).*?'  # titulo
    patron += '<img src="([^"]+)"[^>]+>.*?'  # thumbnail
    patron += '<span>([^<]*)</span>'  # calidad

    matches = re.compile(patron, re.DOTALL).findall(fichas)

    for scrapedurl, scrapedtitle, scrapedthumbnail, calidad in matches:
        url = scrapedurl
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        action = "findvideos"
        extra = ""

        if "1.com/series" in url:
            action = "completo"
            extra = "serie"
            context = "tvshow"

            title = scrapertools.find_single_match(title, '([^-]+)')
            title = title.replace("Ver online", "", 1).replace("Descarga Serie HD", "", 1).replace("Ver en linea", "",
                                                                                                   1).strip()
            # logger.info("[newpct1.py] titulo="+title)
            '''
            if len(title)>3:    
                url_i = 'http://www.newpct1.com/index.php?page=buscar&url=&letter=&q=%22' + title.replace(" ","%20") + '%22'     
            else:
                url_i = 'http://www.newpct1.com/index.php?page=buscar&url=&letter=&q=' + title 
            
            if "1.com/series-hd" in url:
                extra="serie-hd"
                url = url_i + '&categoryID=&categoryIDR=1469&calidad=' + calidad.replace(" ","+") #DTV+720p+AC3+5.1
            elif "1.com/series-vo" in url: 
                extra="serie-vo"
                url = url_i + '&categoryID=&categoryIDR=775&calidad=' + calidad.replace(" ","+") #HDTV+720p+AC3+5.1       
            elif "1.com/series/" in url: 
                extra="serie-tv"
                url = url_i + '&categoryID=&categoryIDR=767&calidad=' + calidad.replace(" ","+") 
                
            url += '&idioma=&ordenar=Nombre&inon=Descendente'  
            '''
            show = title
        else:
            title = title.replace("Descargar", "", 1).strip()
            if title.endswith("gratis"): title = title[:-7]
            show = ""
            context = "movie"

        context_title = scrapertools.find_single_match(url, "http://www.newpct1.com/(.*?)/(.*?)/")
        if context_title:
            try:
                context_title = context_title[1].replace("-", " ")
                if re.search('\d{4}', context_title[-4:]):
                    context_title = context_title[:-4]
                elif re.search('\(\d{4}\)', context_title[-6:]):
                    context_title = context_title[:-6]
            except:
                context_title = title

        if item.extra != "buscar-list":
            title = title + ' ' + calidad

        itemlist.append(
            Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail, extra=extra, show=show,
                 contentTitle=context_title, contentType=context, context=["buscar_trailer"]))

    if "pagination" in data:
        patron = '<ul class="pagination">(.*?)</ul>'
        paginacion = scrapertools.get_match(data, patron)

        if "Next" in paginacion:
            url_next_page = scrapertools.get_match(paginacion, '<a href="([^>]+)>Next</a>')[:-1].replace(" ", "%20")
            itemlist.append(Item(channel=item.channel, action="listado", title=">> Página siguiente", url=url_next_page,
                                 extra=item.extra))
            # logger.info("[newpct1.py] listado items:" + str(len(itemlist)))
    return itemlist


def completo(item):
    logger.info()
    itemlist = []
    categoryID = ""

    # Guarda el valor por si son etiquetas para que lo vea 'listadofichas'
    item_extra = item.extra
    item_show = item.show
    item_title = item.title

    # Lee las entradas
    if item_extra.startswith("serie"):
        ultimo_action = "get_episodios"

        if item.extra != "serie_add":
            '''
            # Afinar mas la busqueda 
            if item_extra=="serie-hd":
                categoryID=buscar_en_subcategoria(item.show,'1469')
            elif item_extra=="serie-vo":
                categoryID=buscar_en_subcategoria(item.show,'775')
            elif item_extra=="serie-tv":
                categoryID=buscar_en_subcategoria(item.show,'767')
            if categoryID !="":
                item.url=item.url.replace("categoryID=","categoryID="+categoryID)
                
            #Fanart
            oTvdb= TvDb()
            serieID=oTvdb.get_serieId_by_title(item.show)
            fanart = oTvdb.get_graphics_by_serieId(serieID)
            if len(fanart)>0:
                item.fanart = fanart[0]'''
            try:
                from core.tmdb import Tmdb
                oTmdb = Tmdb(texto_buscado=item.show, tipo="tv", idioma_busqueda="es")
                item.fanart = oTmdb.get_backdrop()
                item.plot = oTmdb.get_sinopsis()
                print item.plot
            except:
                pass
        else:
            item_title = item.show

        items_programas = get_episodios(item)
    else:
        ultimo_action = "listado"
        items_programas = listado(item)

    if len(items_programas) == 0:
        return itemlist  # devolver lista vacia

    salir = False
    while not salir:

        # Saca la URL de la siguiente página    
        ultimo_item = items_programas[len(items_programas) - 1]

        # Páginas intermedias
        if ultimo_item.action == ultimo_action:
            # Quita el elemento de "Página siguiente" 
            ultimo_item = items_programas.pop()

            # Añade las entradas de la página a la lista completa
            itemlist.extend(items_programas)

            # Carga la siguiente página
            ultimo_item.extra = item_extra
            ultimo_item.show = item_show
            ultimo_item.title = item_title
            logger.debug("url=" + ultimo_item.url)
            if item_extra.startswith("serie"):
                items_programas = get_episodios(ultimo_item)
            else:
                items_programas = listado(ultimo_item)

        # Última página
        else:
            # Añade a la lista completa y sale
            itemlist.extend(items_programas)
            salir = True

    if (config.get_videolibrary_support() and len(itemlist) > 0 and item.extra.startswith("serie")):
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", url=item.url,
                             action="add_serie_to_library", extra="completo###serie_add", show=item.show))
    logger.debug("items=" + str(len(itemlist)))
    return itemlist


def get_episodios(item):
    logger.info("url=" + item.url)
    itemlist = []
    data = re.sub(r'\n|\r|\t|\s{2}|<!--.*?-->|<i class="icon[^>]+"></i>', "", httptools.downloadpage(item.url).data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")

    logger.debug("data=" + data)

    patron = '<ul class="buscar-list">(.*?)</ul>'
    # logger.info("[newpct1.py] patron=" + patron)

    fichas = scrapertools.get_match(data, patron)
    # logger.info("[newpct1.py] matches=" + str(len(fichas)))

    # <li><a href="http://www.newpct1.com/serie/forever/capitulo-101/" title="Serie Forever 1x01"><img src="http://www.newpct1.com/pictures/c/minis/1880_forever.jpg" alt="Serie Forever 1x01"></a> <div class="info"> <a href="http://www.newpct1.com/serie/forever/capitulo-101/" title="Serie Forever 1x01"><h2 style="padding:0;">Serie <strong style="color:red;background:none;">Forever - Temporada 1 </strong> - Temporada<span style="color:red;background:none;">[ 1 ]</span>Capitulo<span style="color:red;background:none;">[ 01 ]</span><span style="color:red;background:none;padding:0px;">Espa�ol Castellano</span> Calidad <span style="color:red;background:none;">[ HDTV ]</span></h2></a> <span>27-10-2014</span> <span>450 MB</span> <span class="color"><ahref="http://www.newpct1.com/serie/forever/capitulo-101/" title="Serie Forever 1x01"> Descargar</a> </div></li>
    # logger.info("[newpct1.py] get_episodios: " + fichas)
    patron = '<li[^>]*><a href="([^"]+).*?'  # url
    patron += '<img src="([^"]+)".*?'  # thumbnail
    patron += '<h2 style="padding(.*?)/h2>'  # titulo, idioma y calidad

    matches = re.compile(patron, re.DOTALL).findall(fichas)
    # logger.info("[newpct1.py] get_episodios matches: " + str(len(matches)))
    for scrapedurl, scrapedthumbnail, scrapedinfo in matches:
        try:
            url = scrapedurl
            if '</span>' in scrapedinfo:
                # logger.info("[newpct1.py] get_episodios: scrapedinfo="+scrapedinfo)
                try:
                    # <h2 style="padding:0;">Serie <strong style="color:red;background:none;">The Big Bang Theory - Temporada 6 </strong> - Temporada<span style="color:red;background:none;">[ 6 ]</span>Capitulo<span style="color:red;background:none;">[ 03 ]</span><span style="color:red;background:none;padding:0px;">Español Castellano</span> Calidad <span style="color:red;background:none;">[ HDTV ]</span></h2>
                    patron = '<span style=".*?">\[\s*(.*?)\]</span>.*?'  # temporada
                    patron += '<span style=".*?">\[\s*(.*?)\].*?'  # capitulo
                    patron += ';([^/]+)'  # idioma
                    info_extra = re.compile(patron, re.DOTALL).findall(scrapedinfo)
                    (temporada, capitulo, idioma) = info_extra[0]

                except:
                    # <h2 style="padding:0;">Serie <strong style="color:red;background:none;">The Affair  Temporada 3 Capitulo 5</strong> - <span style="color:red;background:none;padding:0px;">Español Castellano</span> Calidad <span style="color:red;background:none;">[ HDTV ]</span></h2>
                    patron = '<strong style=".*?">([^<]+).*?'  # temporada y capitulo
                    patron += '<span style=".*?">([^<]+)'

                    info_extra = re.compile(patron, re.DOTALL).findall(scrapedinfo)
                    (temporada_capitulo, idioma) = info_extra[0]
                    if re.search(r'(?i)Capitulos', temporada_capitulo):
                        temporada = scrapertools.find_single_match(temporada_capitulo, 'Temp.*?\s*([\d]+)')
                        cap1, cap2 = scrapertools.find_single_match(temporada_capitulo, 'Cap.*?\s*(\d+).*?(\d+)')
                        capitulo = ""
                    else:
                        temporada, capitulo = scrapertools.get_season_and_episode(temporada_capitulo).split('x')

                # logger.info("[newpct1.py] get_episodios: temporada=" + temporada)
                # logger.info("[newpct1.py] get_episodios: capitulo=" + capitulo)
                logger.debug("idioma=" + idioma)
                if '">' in idioma:
                    idioma = " [" + scrapertools.find_single_match(idioma, '">([^<]+)').strip() + "]"
                elif '&nbsp' in idioma:
                    idioma = " [" + scrapertools.find_single_match(idioma, '&nbsp;([^<]+)').strip() + "]"
                '''else:
                    idioma=""'''
                if capitulo:
                    title = item.title + " (" + temporada.strip() + "x" + capitulo.strip() + ") " + idioma
                else:
                    title = item.title + " (Del %sx%s al %sx%s) %s" % (temporada, cap1, temporada, cap2, idioma)
            else:
                # <h2 style="padding:0;">The Big Bang Theory - Temporada 6 [HDTV][Cap.602][Español Castellano]</h2>
                # <h2 style="padding:0;">The Beast - Temporada 1 [HDTV] [Capítulo 13] [Español]</h2
                # <h2 style="padding:0;">The Beast - Temp.1 [DVD-DVB][Cap.103][Spanish]</h2>
                try:
                    temp, cap = scrapertools.get_season_and_episode(scrapedinfo).split('x')
                except:
                    # Formatear temporadaXepisodio
                    patron = re.compile('Cap.*?\s*([\d]+)', re.IGNORECASE)
                    info_extra = patron.search(scrapedinfo)

                    if len(str(info_extra.group(1))) >= 3:
                        cap = info_extra.group(1)[-2:]
                        temp = info_extra.group(1)[:-2]
                    else:
                        cap = info_extra.group(1)
                        patron = 'Temp.*?\s*([\d]+)'
                        temp = re.compile(patron, re.IGNORECASE).search(scrapedinfo).group(1)

                title = item.title + " (" + temp + 'x' + cap + ")"

            # logger.info("[newpct1.py] get_episodios: fanart= " +item.fanart)
            itemlist.append(
                Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=item.thumbnail,
                     show=item.show, fanart=item.fanart))
        except:
            logger.error("ERROR al añadir un episodio")
    if "pagination" in data:
        patron = '<ul class="pagination">(.*?)</ul>'
        paginacion = scrapertools.get_match(data, patron)
        # logger.info("[newpct1.py] get_episodios: paginacion= " + paginacion)
        if "Next" in paginacion:
            url_next_page = scrapertools.get_match(paginacion, '<a href="([^>]+)>Next</a>')[:-1]
            url_next_page = url_next_page.replace(" ", "%20")
            # logger.info("[newpct1.py] get_episodios: url_next_page= " + url_next_page)
            itemlist.append(
                Item(channel=item.channel, action="get_episodios", title=">> Página siguiente", url=url_next_page))

    return itemlist


def buscar_en_subcategoria(titulo, categoria):
    data = httptools.downloadpage("http://www.newpct1.com/pct1/library/include/ajax/get_subcategory.php",
                                  post="categoryIDR=" + categoria).data
    data = data.replace("</option>", " </option>")
    patron = '<option value="(\d+)">(' + titulo.replace(" ", "\s").replace("(", "/(").replace(")",
                                                                                              "/)") + '\s[^<]*)</option>'
    logger.debug("data=" + data)
    logger.debug("patron=" + patron)
    matches = re.compile(patron, re.DOTALL | re.IGNORECASE).findall(data)

    if len(matches) == 0: matches = [('', '')]
    logger.debug("resultado=" + matches[0][0])
    return matches[0][0]


def findvideos(item):
    logger.info()
    itemlist = []

    ## Cualquiera de las tres opciones son válidas
    # item.url = item.url.replace("1.com/","1.com/ver-online/")
    # item.url = item.url.replace("1.com/","1.com/descarga-directa/")
    item.url = item.url.replace("1.com/", "1.com/descarga-torrent/")

    # Descarga la página
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url).data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")

    title = scrapertools.find_single_match(data, "<h1><strong>([^<]+)</strong>[^<]+</h1>")
    title += scrapertools.find_single_match(data, "<h1><strong>[^<]+</strong>([^<]+)</h1>")
    caratula = scrapertools.find_single_match(data, '<div class="entry-left">.*?src="([^"]+)"')

    # <a href="http://tumejorjuego.com/download/index.php?link=descargar-torrent/058310_yo-frankenstein-blurayrip-ac3-51.html" title="Descargar torrent de Yo Frankenstein " class="btn-torrent" target="_blank">Descarga tu Archivo torrent!</a>

    patron = '<a href="([^"]+)" title="[^"]+" class="btn-torrent" target="_blank">'

    # escraped torrent
    url = scrapertools.find_single_match(data, patron)
    if url != "":
        itemlist.append(
            Item(channel=item.channel, action="play", server="torrent", title=title + " [torrent]", fulltitle=title,
                 url=url, thumbnail=caratula, plot=item.plot, folder=False))

    # escraped ver vídeos, descargar vídeos un link, múltiples liks
    data = data.replace("'", '"')
    data = data.replace(
        'javascript:;" onClick="popup("http://www.newpct1.com/pct1/library/include/ajax/get_modallinks.php?links=', "")
    data = data.replace("http://tumejorserie.com/descargar/url_encript.php?link=", "")
    data = data.replace("$!", "#!")

    patron_descargar = '<div id="tab2"[^>]+>.*?</ul>'
    patron_ver = '<div id="tab3"[^>]+>.*?</ul>'

    match_ver = scrapertools.find_single_match(data, patron_ver)
    match_descargar = scrapertools.find_single_match(data, patron_descargar)

    patron = '<div class="box1"><img src="([^"]+)".*?'  # logo
    patron += '<div class="box2">([^<]+)</div>'  # servidor
    patron += '<div class="box3">([^<]+)</div>'  # idioma
    patron += '<div class="box4">([^<]+)</div>'  # calidad
    patron += '<div class="box5"><a href="([^"]+)".*?'  # enlace
    patron += '<div class="box6">([^<]+)</div>'  # titulo

    enlaces_ver = re.compile(patron, re.DOTALL).findall(match_ver)
    enlaces_descargar = re.compile(patron, re.DOTALL).findall(match_descargar)

    for logo, servidor, idioma, calidad, enlace, titulo in enlaces_ver:
        servidor = servidor.replace("streamin", "streaminto")
        titulo = titulo + " [" + servidor + "]"
        if servertools.is_server_enabled(servidor):
            try:
                servers_module = __import__("servers." + servidor)
                server_module = getattr(servers_module, servidor)
                devuelve = server_module.find_videos(enlace)
                if devuelve:
                    enlace = devuelve[0][1]
                    itemlist.append(
                        Item(fanart=item.fanart, channel=item.channel, action="play", server=servidor, title=titulo,
                             fulltitle=item.title, url=enlace, thumbnail=logo, plot=item.plot, folder=False))
            except:
                pass

    for logo, servidor, idioma, calidad, enlace, titulo in enlaces_descargar:
        servidor = servidor.replace("uploaded", "uploadedto")
        partes = enlace.split(" ")
        p = 1
        for enlace in partes:
            parte_titulo = titulo + " (%s/%s)" % (p, len(partes)) + " [" + servidor + "]"
            p += 1
            if servertools.is_server_enabled(servidor):
                try:
                    servers_module = __import__("servers." + servidor)
                    server_module = getattr(servers_module, servidor)
                    devuelve = server_module.find_videos(enlace)
                    if devuelve:
                        enlace = devuelve[0][1]
                        itemlist.append(Item(fanart=item.fanart, channel=item.channel, action="play", server=servidor,
                                             title=parte_titulo, fulltitle=item.title, url=enlace, thumbnail=logo,
                                             plot=item.plot, folder=False))
                except:
                    pass
    return itemlist


def episodios(item):
    # Necesario para las actualizaciones automaticas
    return completo(Item(channel=item.channel, url=item.url, show=item.show, extra="serie_add"))
