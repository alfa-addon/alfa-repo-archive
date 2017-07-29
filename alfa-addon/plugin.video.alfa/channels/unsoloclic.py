# -*- coding: utf-8 -*-

import re
import urlparse

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()
    item.url = "http://unsoloclic.info"
    return novedades(item)


def novedades(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <div class="post-45732 post type-post status-publish format-standard hentry category-2012 category-blu-ray category-mkv-hd720p" id="post-45732">
    <h2 class="title"><a href="http://unsoloclic.info/2012/11/ek-tha-tiger-2012-blu-ray-720p-hd/" rel="bookmark" title="Permanent Link to Pelicula Ek Tha Tiger (2012) BLU-RAY 720p HD">Pelicula Ek Tha Tiger (2012) BLU-RAY 720p HD</a></h2>
    <div class="postdate"><img src="http://unsoloclic.info/wp-content/themes/TinyWeb/images/date.png" /> noviembre 5th, 2012     
    <!-- 
    <img src="http://unsoloclic.info/wp-content/themes/TinyWeb/images/user.png" /> unsoloclic 
    -->
    </div>
    <div class="entry">
    <p><a href="http://unsoloclic.info/2012/11/ek-tha-tiger-2012-blu-ray-720p-hd/" rel="attachment wp-att-45737"><img src="http://unsoloclic.info/wp-content/uploads/2012/11/Ek-Tha-Tiger-2012.jpg" alt="" title="Ek Tha Tiger  (2012)" width="500" height="629" class="aligncenter size-full wp-image-45737" /></a></p>
    <h2 style="text-align: center;"></h2>
    <div class="readmorecontent">
    <a class="readmore" href="http://unsoloclic.info/2012/11/ek-tha-tiger-2012-blu-ray-720p-hd/" rel="bookmark" title="Permanent Link to Pelicula Ek Tha Tiger (2012) BLU-RAY 720p HD">Seguir Leyendo</a>
    </div>
    </div>
    </div><!--/post-45732-->
    '''
    '''
    <div class="post-45923 post type-post status-publish format-standard hentry category-2012 category-blu-ray category-comedia category-drama category-mkv category-mkv-hd720p category-romance tag-chris-messina tag-jenna-fischer tag-lee-kirk tag-the-giant-mechanical-man-pelicula tag-topher-grace" id="post-45923">
    <h2 class="title"><a href="http://unsoloclic.info/2012/12/the-giant-mechanical-man-2012-bluray-720p-hd/" rel="bookmark" title="Permanent Link to The Giant Mechanical Man (2012) BluRay 720p HD">The Giant Mechanical Man (2012) BluRay 720p HD</a></h2>
    <div class="postdate"><img src="http://unsoloclic.info/wp-content/themes/TinyWeb/images/date.png" /> diciembre 24th, 2012 
    <!-- 
    <img src="http://unsoloclic.info/wp-content/themes/TinyWeb/images/user.png" /> deportv 
    -->
    </div>
    <div class="entry">
    <p style="text-align: center;"><a href="http://unsoloclic.info/2012/12/the-giant-mechanical-man-2012-bluray-720p-hd/"><img class="aligncenter size-full wp-image-45924" title="Giant Michanical Man Pelicula Descargar" src="http://unsoloclic.info/wp-content/uploads/2012/12/Giant-Michanical-Man-Pelicula-Descargar.jpg" alt="" width="380" height="500" /></a></p>
    <p style="text-align: center;">
    <div class="readmorecontent">
    <a class="readmore" href="http://unsoloclic.info/2012/12/the-giant-mechanical-man-2012-bluray-720p-hd/" rel="bookmark" title="Permanent Link to The Giant Mechanical Man (2012) BluRay 720p HD">Seguir Leyendo</a>
    </div>
    </div>
    </div><!--/post-45923-->
    '''
    patron = '<div class="post[^"]+" id="post-\d+">[^<]+'
    patron += '<h2 class="title"><a href="([^"]+)" rel="bookmark" title="[^"]+">([^<]+)</a></h2>[^<]+'
    patron += '<div class="postdate">.*?</div>[^<]+'
    patron += '<div class="entry">[^<]+'
    patron += '<p[^<]+<a[^<]+<img.*?src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(Item(channel=item.channel, action="findvideos", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))

    '''
    <a href="http://unsoloclic.info/page/2/" >&laquo; Peliculas anteriores</a>
    '''
    patron = '<a href="([^"]+)" >\&laquo\; Peliculas anteriores</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = ">> Página siguiente"
        scrapedplot = ""
        scrapedurl = urlparse.urljoin(item.url, match)
        scrapedthumbnail = ""
        logger.debug("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(Item(channel=item.channel, action="novedades", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))

    return itemlist


def findvideos(item):
    logger.info()
    data = scrapertools.cache_page(item.url)
    itemlist = []

    # <a href="http://67cfb0db.linkbucks.com"><img title="billionuploads" src="http://unsoloclic.info/wp-content/uploads/2012/11/billonuploads2.png" alt="" width="380" height="50" /></a></p>
    # <a href="http://1bd02d49.linkbucks.com"><img class="colorbox-57103"  title="Freakeshare" alt="" src="http://unsoloclic.info/wp-content/uploads/2013/01/freakshare.png" width="390" height="55" /></a></p>
    patron = '<a href="(http.//[a-z0-9]+.linkbucks.c[^"]+)[^>]+><img.*?title="([^"]+)".*?src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for url, servertag, serverthumb in matches:
        itemlist.append(
            Item(channel=item.channel, action="play", server="linkbucks", title=servertag + " [linkbucks]", url=url,
                 thumbnail=serverthumb, plot=item.plot, folder=False))

    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        if videoitem.server != "linkbucks":
            videoitem.channel = item.channel
            videoitem.action = "play"
            videoitem.folder = False
            videoitem.title = "[" + videoitem.server + "]"

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.server == "linkbucks":
        logger.info("Es linkbucks")

        # Averigua el enlace
        from servers.decrypters import linkbucks
        location = linkbucks.get_long_url(item.url)
        logger.info("location=" + location)

        # Extrae la URL de saltar el anuncio en adf.ly
        if location.startswith("http://adf"):
            # Averigua el enlace
            from servers.decrypters import adfly
            location = adfly.get_long_url(location)
            logger.info("location=" + location)

        from core import servertools
        itemlist = servertools.find_video_items(data=location)
        for videoitem in itemlist:
            videoitem.channel = item.channel
            videoitem.folder = False

    else:
        itemlist.append(item)

    return itemlist
