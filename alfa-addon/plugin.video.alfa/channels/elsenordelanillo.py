# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Novedades",
                         url="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/", viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="generos", title="Por género",
                         url="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/"))
    itemlist.append(Item(channel=item.channel, action="letras", title="Por letra",
                         url="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/"))
    itemlist.append(Item(channel=item.channel, action="anyos", title="Por año",
                         url="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/"))

    return itemlist


def anyos(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    # logger.info("data="+data)
    data = scrapertools.find_single_match(data, 'scalas por a(.*?)</ul>')
    logger.info("data=" + data)

    # Extrae las entradas (carpetas)
    patron = '<li><a target="[^"]+" title="[^"]+" href="([^"]+)"><strong>([^<]+)</strong>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title, viewmode="movie"))

    return itemlist


def letras(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    # logger.info("data="+data)
    data = scrapertools.find_single_match(data, '<div class="bkpelsalf_ul(.*?)</ul>')
    logger.info("data=" + data)

    # Extrae las entradas (carpetas)
    # <li><a target="_top" href="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/letra/a.html" title="Películas que comienzan con A">A</a>
    patron = '<li><a target="[^"]+" href="([^"]+)" title="[^"]+">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title, viewmode="movie"))

    return itemlist


def generos(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    # logger.info("data="+data)

    # Extrae las entradas (carpetas)
    # <a class='generos' target="_top" href='/pelisdelanillo/categoria/accion/' title='Las Mejores Películas de Acción De Todos Los Años'> Acción </a>
    patron = "<a class='generos' target=\"_top\" href='([^']+)' title='[^']+'>([^<]+)</a>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        title = unicode(scrapedtitle, "iso-8859-1", errors="replace").encode("utf-8").strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title, viewmode="movie"))

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    # logger.info("data="+data)

    # Extrae las entradas
    '''
    <!--<pelicula>--> 
    <li class="peli_bx br1px brdr10px ico_a"> 
    <h2 class="titpeli bold ico_b"><a target="_top" href="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/pelicula/1077/el-jardinero-fiel.html" title="El Jardinero Fiel">El Jardinero Fiel</a></h2> 
    <div class="peli_img p_relative"> 
    <div class="peli_img_img"> 
    <a target="_top" href="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/pelicula/1077/el-jardinero-fiel.html" title="El Jardinero Fiel"> 
    <img src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/files/uploads/1077.jpg" alt="El Jardinero Fiel" /></a>
    </div>
    <div>
    <center><table border="5" bordercolor="#000000"><tr><td>
    <img width="26" heigth="17" src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/Temas/default/img/idioma/lat.png">
    </td><td>
    <img width="26" heigth="17" src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/Temas/default/img/idioma/sub.png">
    </td><td>
    <img width="26" heigth="17" src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/Temas/default/img/idioma/no-cam.png">
    </td><td>
    <img width="26" heigth="17" src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/Temas/default/img/idioma/dvd.png">
    </td><td>
    <img width="26" heigth="17" src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/Temas/default/img/idioma/no-hd.png">
    </td></tr></table></center>
    </div>
    <div class="peli_txt bgdeg8 brdr10px bxshd2 ico_b p_absolute pd15px white">
    <div class="plt_tit bold fs14px mgbot10px"><h2 class="bold d_inline fs14px"><font color="black"><b>El Jardinero Fiel</b></font></h2></div>  
    <div class="plt_ft clf mgtop10px">        
    <div class="stars f_left pdtop10px"><strong>Genero</strong>: Suspenso, Drama, 2005</div>  
    <br><br>
    <div class="stars f_left pdtop10px"><table><tr><td><strong>Idioma</strong>:</td><td><img width="26" heigth="17" src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/Temas/default/img/idioma/lat.png"></td><td><img width="26" heigth="17" src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/Temas/default/img/idioma/sub.png"></td></tr></table></div>  
    <br /><br />
    <div class="stars f_left pdtop10px"><table><tr><td><strong>Calidad</strong>:</td><td><img width="26" heigth="17" src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/Temas/default/img/idioma/no-cam.png"></td><td><img width="26" heigth="17" src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/Temas/default/img/idioma/dvd.png"></td><td><img width="26" heigth="17" src="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/Temas/default/img/idioma/no-hd.png"></td></tr></table></div>  
    <br /><br>
    <div class="stars f_left pdtop10px"><strong>Visualizada</strong>: 629 Veces</div>  
    <a target="_top" class="vrfich bold ico f_right" href="http://www.xn--elseordelanillo-1qb.com/pelisdelanillo/pelicula/1077/el-jardinero-fiel.html" title=""></a>

    </div> 
    </div> 
    </div> 
    </li> 
    <!--</pelicula>--> 
    '''
    patronbloque = "<!--<pelicula>--[^<]+<li(.*?)</li>"
    bloques = re.compile(patronbloque, re.DOTALL).findall(data)

    for bloque in bloques:
        scrapedurl = scrapertools.find_single_match(bloque, '<a.*?href="([^"]+)"')
        scrapedtitle = scrapertools.find_single_match(bloque, '<a.*?title="([^"]+)"')
        scrapedthumbnail = scrapertools.find_single_match(bloque, '<img src="([^"]+)"')

        title = unicode(scrapedtitle, "iso-8859-1", errors="replace").encode("utf-8")
        title = title.strip()
        title = scrapertools.htmlclean(title)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title))

    # </b></span></a></li[^<]+<li><a href="?page=2">
    next_page = scrapertools.find_single_match(data, '</b></span></a></li[^<]+<li><a target="_top" href="([^"]+)">')
    if next_page != "":
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=">> Página siguiente", url=item.url + next_page,
                 folder=True, viewmode="movie"))

    return itemlist


def findvideos(item):
    logger.info()

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    # logger.info("data="+data)
    bloque = scrapertools.find_single_match(data, "function cargamos.*?window.open.'([^']+)'")
    data = scrapertools.cache_page(bloque)

    from core import servertools
    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.folder = False

    return itemlist


def play(item):
    logger.info("url=" + item.url)

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = item.channel

    return itemlist
