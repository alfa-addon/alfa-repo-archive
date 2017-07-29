# -*- coding: utf-8 -*-

import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Ultimas Agregadas", action="listado2",
                         url="http://www.vepelis.com/pelicula/ultimas-peliculas",
                         extra="http://www.vepelis.com/pelicula/ultimas-peliculas"))
    itemlist.append(Item(channel=item.channel, title="Estrenos en DVD", action="listado2",
                         url="http://www.vepelis.com/pelicula/ultimas-peliculas/estrenos-dvd",
                         extra="http://www.vepelis.com/pelicula/ultimas-peliculas/estrenos-dvd"))
    itemlist.append(Item(channel=item.channel, title="Peliculas en Cartelera", action="listado2",
                         url="http://www.vepelis.com/pelicula/ultimas-peliculas/cartelera",
                         extra="http://www.vepelis.com/pelicula/ultimas-peliculas/cartelera"))
    itemlist.append(Item(channel=item.channel, title="Ultimas Actualizadas", action="listado2",
                         url="http://www.vepelis.com/pelicula/ultimas-peliculas/ultimas/actualizadas",
                         extra="http://www.vepelis.com/pelicula/ultimas-peliculas/ultimas/actualizadas"))
    itemlist.append(Item(channel=item.channel, title="Por Genero", action="generos", url="http://www.vepelis.com/"))
    itemlist.append(
        Item(channel=item.channel, title="Por Orden Alfabetico", action="alfabetico", url="http://www.vepelis.com/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url="http://www.vepelis.com/"))
    return itemlist


def listarpeliculas(item):
    logger.info()

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    extra = item.extra

    # Extrae las entradas de la pagina seleccionada
    '''<td class="DarkText" align="center" valign="top" width="100px" height="160px" style="background-color:#1e1e1e;" onmouseover="this.style.backgroundColor='#000000'" onmouseout="this.style.backgroundColor='#1e1e1e'"><p style="margin-bottom: 3px;border-bottom:#ABABAB 1px solid"> 
                    	<a href="http://www.peliculasaudiolatino.com/movies/Larry_Crowne.html"><img src="http://www.peliculasaudiolatino.com/poster/85x115/peliculas/movieimg/movie1317696842.jpg" alt="Larry Crowne" border="0" height="115" width="85"></a>'''
    patron = '<td class=.*?<a '
    patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []
    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[2]
        scrapedtitle = unicode(scrapedtitle, "iso-8859-1", errors="replace").encode("utf-8")
        scrapedthumbnail = match[1]
        scrapedplot = ""
        logger.info(scrapedtitle)

        # Añade al listado
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=scrapedtitle, fulltitle=scrapedtitle, url=scrapedurl,
                 thumbnail=scrapedthumbnail, plot=scrapedplot, extra=extra, folder=True))

    # Extrae la marca de siguiente página
    patron = 'Anterior.*?  :: <a href="/../../.*?/page/([^"]+)">Siguiente '
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = extra + match
            scrapedtitle = "!Pagina Siguiente"
            scrapedthumbnail = ""
            scrapedplot = ""

            itemlist.append(
                Item(channel=item.channel, action="listarpeliculas", title=scrapedtitle, fulltitle=scrapedtitle,
                     url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, extra=extra, folder=True))

    return itemlist


def findvideos(item):
    logger.info()
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    title = item.title
    scrapedthumbnail = item.thumbnail
    itemlist = []
    patron = '<li><a href="#ms.*?">([^"]+)</a></li>.*?<iframe src="(.*?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    # itemlist.append( Item(channel=item.channel, action="play", title=title , fulltitle=item.fulltitle, url=item.url , thumbnail=scrapedthumbnail , folder=False) )

    for match in matches:
        url = match[1]
        title = "SERVIDOR: " + match[0]
        title = unicode(title, "iso-8859-1", errors="replace").encode("utf-8")
        itemlist.append(Item(channel=item.channel, action="play", title=title, fulltitle=item.fulltitle, url=url,
                             thumbnail=scrapedthumbnail, folder=False))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    from core import servertools
    itemlist = servertools.find_video_items(data=item.url)
    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.action = "play"
        videoitem.folder = False

    return itemlist
    # data2 = scrapertools.cache_page(item.url)
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/show/mv.php?url=","http://www.megavideo.com/?v=")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/show/videobb.php?url=","http://www.videobb.com/watch_video.php?v=")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/show/vidbux.php?url=","http://www.vidbux.com/")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/show/vidxden.php?url=","http://www.vidxden.com/")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/show/videozer.php?url=","http://www.videozer.com/video/")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/v/pl/play.php?url=","http://www.putlocker.com/embed/")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/v/mv/play.php?url=","http://www.modovideo.com/frame.php?v=")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/v/ss/play.php?url=","http://www.sockshare.com/embed/")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/v/vb/play.php?url=","http://vidbull.com/")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/show/sockshare.php?url=","http://www.sockshare.com/embed/")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/show/moevide.php?url=","http://moevideo.net/?page=video&uid=")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/show/novamov.php?url=","http://www.novamov.com/video/")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/show/movshare.php?url=","http://www.movshare.net/video/")
    # data2 = data2.replace("http://www.peliculasaudiolatino.com/show/divxstage.php?url=","http://www.divxstage.net/video/")
    # listavideos = servertools.findvideos(data2)


# for video in listavideos:
#    invalid = video[1]
#    invalid = invalid[0:8]
#    if invalid!= "FN3WE43K" and invalid!="9CC3F8&e":
#        scrapedtitle = item.title+video[0]
#        videourl = item.url
#        server = video[2]
#        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+videourl+"]")
# logger.info("url=" + item.url)

# Añade al listado de XBMC
# itemlist.append( Item(channel=item.channel, action="play", title=scrapedtitle , fulltitle=item.fulltitle, url=videourl , server=server , folder=False) )
#    itemlist.append( Item(channel=item.channel, action="play" , title=item.title , url=item.url, thumbnail="", plot="", server=item.url))


#   return itemlist

def generos(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    patron = '>.*?<li><a title="(.*?)" href="(.*?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        scrapedurl = urlparse.urljoin("", match[1])
        scrapedurl = scrapedurl.replace(".html", "/page/0.html")
        extra = scrapedurl.replace("/page/0.html", "/page/")
        scrapedtitle = match[0]
        # scrapedtitle = scrapedtitle.replace("","")
        scrapedthumbnail = ""
        scrapedplot = ""
        logger.info(scrapedtitle)

        if scrapedtitle == "Eroticas +18":
            if config.get_setting("adult_mode") != 0:
                itemlist.append(Item(channel=item.channel, action="listado2", title="Eroticas +18",
                                     url="http://www.myhotamateurvideos.com", thumbnail=scrapedthumbnail,
                                     plot=scrapedplot, extra="", folder=True))
        else:
            if scrapedtitle <> "" and len(scrapedtitle) < 20 and scrapedtitle <> "Iniciar Sesion":
                itemlist.append(Item(channel=item.channel, action="listado2", title=scrapedtitle, url=scrapedurl,
                                     thumbnail=scrapedthumbnail, plot=scrapedplot, extra=extra, folder=True))

    itemlist = sorted(itemlist, key=lambda Item: Item.title)
    return itemlist


def alfabetico(item):
    logger.info()

    extra = item.url
    itemlist = []
    itemlist.append(
        Item(channel=item.channel, action="listado2", title="0-9", url="http://www.vepelis.com/letra/09.html",
             extra="http://www.vepelis.com/letra/09.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="A", url="http://www.vepelis.com/letra/a.html",
                         extra="http://www.vepelis.com/letra/a.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="B", url="http://www.vepelis.com/letra/b.html",
                         extra="http://www.vepelis.com/letra/b.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="C", url="http://www.vepelis.com/letra/c.html",
                         extra="http://www.vepelis.com/letra/c.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="E", url="http://www.vepelis.com/letra/d.html",
                         extra="http://www.vepelis.com/letra/d.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="D", url="http://www.vepelis.com/letra/e.html",
                         extra="http://www.vepelis.com/letra/e.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="F", url="http://www.vepelis.com/letra/f.html",
                         extra="http://www.vepelis.com/letra/f.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="G", url="http://www.vepelis.com/letra/g.html",
                         extra="http://www.vepelis.com/letra/g.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="H", url="http://www.vepelis.com/letra/h.html",
                         extra="http://www.vepelis.com/letra/h.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="I", url="http://www.vepelis.com/letra/i.html",
                         extra="http://www.vepelis.com/letra/i.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="J", url="http://www.vepelis.com/letra/j.html",
                         extra="http://www.vepelis.com/letra/j.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="K", url="http://www.vepelis.com/letra/k.html",
                         extra="http://www.vepelis.com/letra/k.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="L", url="http://www.vepelis.com/letra/l.html",
                         extra="http://www.vepelis.com/letra/l.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="M", url="http://www.vepelis.com/letra/m.html",
                         extra="http://www.vepelis.com/letra/m.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="N", url="http://www.vepelis.com/letra/n.html",
                         extra="http://www.vepelis.com/letra/n.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="O", url="http://www.vepelis.com/letra/o.html",
                         extra="http://www.vepelis.com/letra/o.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="P", url="http://www.vepelis.com/letra/p.html",
                         extra="http://www.vepelis.com/letra/p.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="Q", url="http://www.vepelis.com/letra/q.html",
                         extra="http://www.vepelis.com/letra/q.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="R", url="http://www.vepelis.com/letra/r.html",
                         extra="http://www.vepelis.com/letra/r.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="S", url="http://www.vepelis.com/letra/s.html",
                         extra="http://www.vepelis.com/letra/s.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="T", url="http://www.vepelis.com/letra/t.html",
                         extra="http://www.vepelis.com/letra/t.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="U", url="http://www.vepelis.com/letra/u.html",
                         extra="http://www.vepelis.com/letra/u.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="V", url="http://www.vepelis.com/letra/v.html",
                         extra="http://www.vepelis.com/letra/v.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="W", url="http://www.vepelis.com/letra/w.html",
                         extra="http://www.vepelis.com/letra/w.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="X", url="http://www.vepelis.com/letra/x.html",
                         extra="http://www.vepelis.com/letra/x.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="Y", url="http://www.vepelis.com/letra/y.html",
                         extra="http://www.vepelis.com/letra/y.html"))
    itemlist.append(Item(channel=item.channel, action="listado2", title="Z", url="http://www.vepelis.com/letra/z.html",
                         extra="http://www.vepelis.com/letra/z.html"))

    return itemlist


def listado2(item):
    logger.info()
    extra = item.extra
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    patron = '<h2 class="titpeli.*?<a href="([^"]+)" title="([^"]+)".*?peli_img_img">.*?<img src="([^"]+)".*?<strong>Idioma</strong>:.*?/>([^"]+)</div>.*?<strong>Calidad</strong>: ([^"]+)</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        scrapedurl = match[0]  # urlparse.urljoin("",match[0])
        scrapedtitle = match[1] + ' - ' + match[4]
        scrapedtitle = unicode(scrapedtitle, "iso-8859-1", errors="replace").encode("utf-8")
        scrapedthumbnail = match[2]
        # scrapedplot = match[0]
        # itemlist.append( Item(channel=item.channel, action="findvideos", title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=scrapedtitle, fulltitle=scrapedtitle, url=scrapedurl,
                 thumbnail=scrapedthumbnail, folder=True))

        # if extra<>"":
        # Extrae la marca de siguiente página
    # patron = 'page=(.*?)"><span><b>'
    patron = '<span><b>(.*?)</b></span>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    # if DEBUG: scrapertools.printMatches(matches)
    for match in matches:
        # if len(matches)>0:
        nu = int(match[0]) + 1
        scrapedurl = extra + "?page=" + str(nu)
        scrapedtitle = "!Pagina Siguiente ->"
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=item.channel, action="listado2", title=scrapedtitle, fulltitle=scrapedtitle, url=scrapedurl,
                 thumbnail=scrapedthumbnail, extra=extra, folder=True))

    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []

    texto = texto.replace(" ", "+")
    try:
        # Series
        item.url = "http://www.vepelis.com/buscar/?q=%s"
        item.url = item.url % texto
        item.extra = ""
        itemlist.extend(listado2(item))
        itemlist = sorted(itemlist, key=lambda Item: Item.title)

        return itemlist

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
