# -*- coding: utf-8 -*-

import re
import urllib
import urlparse

from core import logger
from core import scrapertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="submenu", title="Películas"))
    itemlist.append(Item(channel=item.channel, action="submenu", title="Series"))
    itemlist.append(Item(channel=item.channel, action="listado", title="Anime", url="http://www.newpct.com/anime/",
                         viewmode="movie_with_plot"))
    itemlist.append(
        Item(channel=item.channel, action="listado", title="Documentales", url="http://www.newpct.com/documentales/",
             viewmode="movie_with_plot"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")

    item.url = "http://www.newpct.com/buscar-descargas/%s" % (texto)
    try:
        return buscador(item)
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def buscador(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    # <td class="center" style="border-bottom:solid 1px cyan;">14-09-14</td><td style="border-bottom:solid 1px cyan;"><strong><a href="http://www.newpct.com/descargar-pelicula/malefica-3d-sbs/" title="M&aacute;s informaci&oacute;n sobre Malefica 3D SBS [BluRay 1080p][DTS 5.1-AC3 5.1 Castellano DTS 5.1-Ingles+Subs][ES-EN]"> <span class="searchTerm">Malefica</span> 3D SBS [BluRay 1080p][DTS 5.1-AC3 5.1 Castellano DTS 5.1-Ingles+Subs][ES-EN]</a></strong></td><td class="center" style="border-bottom:solid 1px cyan;">10.9 GB</td><td style="border-bottom:solid 1px cyan;"><a href="http://tumejorserie.com/descargar/index.php?link=torrents/059784.torrent" title="Descargar Malefica 3D SBS [BluRay 1080p][DTS 5.1-AC3 5.1 Castellano DTS 5.1-Ingles+Subs][ES-EN]"><img src="http://newpct.com/v2/imagenes//buttons/download.png"

    patron = '<td class="center" style="border-bottom:solid 1px cyan;">([^<]+)</td>.*?'  # createdate
    patron += '<td class="center" style="border-bottom:solid 1px cyan;">([^<]+)</td>.*?'  # info
    patron += '<a href="([^"]+)" '  # url
    patron += 'title="Descargar([^"]+)">'  # title
    patron += '<img src="([^"]+)"'  # thumbnail

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedcreatedate, scrapedinfo, scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapedtitle + "(Tamaño:" + scrapedinfo + "--" + scrapedcreatedate + ")"
        itemlist.append(Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action="play", server="torrent",
                             thumbnail=scrapedthumbnail, fulltitle=scrapedtitle, folder=True))

    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.action = "play"
        videoitem.folder = False

    return itemlist


def submenu(item):
    logger.info()
    itemlist = []

    if item.title == "Películas":
        itemlist.append(Item(channel=item.channel, action="listado", title="Peliculas DVDRIP-BRRIP Castellano",
                             url="http://www.newpct.com/peliculas-castellano/peliculas-rip/",
                             viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, action="listado", title="Peliculas Latino",
                             url="http://www.newpct.com/peliculas-latino/", viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, action="listado", title="Estrenos de Cine Castellano",
                             url="http://www.newpct.com/peliculas-castellano/estrenos-de-cine/",
                             viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, action="listado", title="Peliculas Alta Definicion HD",
                             url="http://www.newpct.com/cine-alta-definicion-hd/", viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, action="listado", title="Peliculas en 3D HD",
                             url="http://www.newpct.com/peliculas-en-3d-hd/", viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, action="listado", title="Peliculas DVDFULL",
                             url="http://www.newpct.com/peliculas-castellano/peliculas-dvd/",
                             viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, action="listado", title="Peliculas V.O.Subtituladas",
                             url="http://www.newpct.com/peliculas-vo/", viewmode="movie_with_plot"))
    else:
        itemlist.append(
            Item(channel=item.channel, action="listado", title="HDTV Castellano", url="http://www.newpct.com/series/",
                 category="serie", viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, action="listado", title="Miniseries Castellano",
                             url="http://www.newpct.com/miniseries-es/", viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, action="listado", title="Series TV - V.O.S.E",
                             url="http://www.newpct.com/series-vo/", category="serie", viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, action="listado", title="Últimos Capítulos HD",
                             url="http://www.newpct.com/series-alta-definicion-hd/", category="serie",
                             viewmode="movie_with_plot"))
        itemlist.append(Item(channel=item.channel, action="series", title="Series HD [A-Z]",
                             url="http://www.newpct.com/index.php?l=torrentListByCategory&subcategory_s=1469&more=listar",
                             category="serie"))
    return itemlist


def listado(item):
    logger.info()
    itemlist = []
    data = scrapertools.cache_page(item.url)

    '''
    <li>
    <a href='http://www.newpct.com/descargar-pelicula/la-pequena-venecia/'>
    <div class='boxgrid captionb'>
    <img src='http://images.newpct.com/banco_de_imagenes/destacados/038707/la-pequeña-venecia--dvdrip--ac3-5-1-español-castellano--2012-.jpg'  alt='Descargar Peliculas Castellano &raquo; Películas RIP La Pequeña Venecia [DVDrip][AC3 5.1 Español Castellano][2012]' />
    <div class='cover boxcaption'>
    <h3>La Pequeña Venecia </h3>
    <p>Peliculas Castellano<br/>
    Calidad: DVDRIP AC3 5.1<br>
    Tama&ntilde;o: 1.1 GB<br>
    Idioma : Español Castellano
    </p>
    </div>
    </div>
    </a>
    <div id='bot-desc'>
    <div id='tinfo'>
    <a class='youtube' href='#' rel='gx9EKDC0UFQ' title='Ver Trailer' alt='Ver Trailer'>
    <img style='width:25px;' src='http://www.newpct.com/images.inc/images/playm2.gif'></a>
    </div>
    <div id='tdescargar' ><a class='atdescargar' href='http://www.newpct.com/descargar-pelicula/la-pequena-venecia/'>DESCARGAR</a></div>
    </div>
    </li>
    '''
    patron = "<li[^<]+"
    patron += "<a href='([^']+)'[^<]+"
    patron += "<div class='boxgrid captionb'[^<]+"
    patron += "<img src='([^']+)'[^<]+"
    patron += "<div class='cover boxcaption'[^<]+"
    patron += '<h3>([^<]+)</h3>(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        title = scrapedtitle.strip()
        title = unicode(title, "iso-8859-1", errors="replace").encode("utf-8")

        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        plot = scrapertools.htmlclean(scrapedplot).strip()
        plot = unicode(plot, "iso-8859-1", errors="replace").encode("utf-8")

        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        if item.category == "serie":
            itemlist.append(
                Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail, plot=plot))
        else:
            itemlist.append(
                Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot))

    # Página siguiente
    '''
    GET /include.inc/ajax.php/orderCategory.php?type=todo&leter=&sql=SELECT+DISTINCT+++%09%09%09%09%09%09torrentID%2C+++%09%09%09%09%09%09torrentCategoryID%2C+++%09%09%09%09%09%09torrentCategoryIDR%2C+++%09%09%09%09%09%09torrentImageID%2C+++%09%09%09%09%09%09torrentName%2C+++%09%09%09%09%09%09guid%2C+++%09%09%09%09%09%09torrentShortName%2C++%09%09%09%09%09%09torrentLanguage%2C++%09%09%09%09%09%09torrentSize%2C++%09%09%09%09%09%09calidad+as+calidad_%2C++%09%09%09%09%09%09torrentDescription%2C++%09%09%09%09%09%09torrentViews%2C++%09%09%09%09%09%09rating%2C++%09%09%09%09%09%09n_votos%2C++%09%09%09%09%09%09vistas_hoy%2C++%09%09%09%09%09%09vistas_ayer%2C++%09%09%09%09%09%09vistas_semana%2C++%09%09%09%09%09%09vistas_mes++%09%09%09%09++FROM+torrentsFiles+as+t+WHERE++(torrentStatus+%3D+1+OR+torrentStatus+%3D+2)++AND+(torrentCategoryID+IN+(1537%2C+758%2C+1105%2C+760%2C+1225))++++ORDER+BY+torrentDateAdded++DESC++LIMIT+0%2C+50&pag=3&tot=&ban=3&cate=1225 HTTP/1.1
    Host: www.newpct.com
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:19.0) Gecko/20100101 Firefox/19.0
    Accept: */*
    Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3
    Accept-Encoding: gzip, deflate
    X-Requested-With: XMLHttpRequest
    Referer: http://www.newpct.com/peliculas-castellano/peliculas-rip/
    Cookie: adbooth_popunder=5%7CSat%2C%2009%20Mar%202013%2018%3A23%3A22%20GMT
    Connection: keep-alive
    '''

    '''
    function orderCategory(type,leter,pag,other)
    {
        
        
        if(leter=='buscar')
        {
            leter = document.getElementById('word').value;
        }
        if(type=='todo')
        {
            document.getElementById('todo').className = "active_todo";
        }	
        if(type=='letter')
        {
            switch(leter)
            {
                case '09':
                document.getElementById('09').className = "active_num";
                break;
                default:
                document.getElementById(leter).className = "active_a";
                break;
            }
        }
        
        var parametros = {
                    "type" : type,
                    "leter" : leter,
                    "sql" : "SELECT DISTINCT   						torrentID,   						torrentCategoryID,   						torrentCategoryIDR,   						torrentImageID,   						torrentName,   						guid,   						torrentShortName,  						torrentLanguage,  						torrentSize,  						calidad as calidad_,  						torrentDescription,  						torrentViews,  						rating,  						n_votos,  						vistas_hoy,  						vistas_ayer,  						vistas_semana,  						vistas_mes  				  FROM torrentsFiles as t WHERE  (torrentStatus = 1 OR torrentStatus = 2)  AND (torrentCategoryID IN (1537, 758, 1105, 760, 1225))    ORDER BY torrentDateAdded  DESC  LIMIT 0, 50",
                    "pag" : pag,   
                    "tot" : '',
                    "ban" : '3',
                    "other": other,
                    "cate" : '1225'
                    
            };
        //alert(type+leter);
        
        $('#content-category').html('<div style="margin:100px auto;width:100px;height:100px;"><img src="http://www.newpct.com/images.inc/images/ajax-loader.gif"/></div>');
            var page = $(this).attr('data');        
            var dataString = 'page='+page;
            
         $.ajax({
              type: "GET",
              url:   'http://www.newpct.com/include.inc/ajax.php/orderCategory.php',
              data:  parametros,
              success: function(data) {
             
                    //Cargamos finalmente el contenido deseado
                    $('#content-category').fadeIn(1000).html(data);
              }
         });
         
    }
    '''
    if item.extra != "":
        bloque = item.extra
    else:
        bloque = scrapertools.get_match(data, "function orderCategory(.*?)\}\)\;")
    logger.info("bloque=" + bloque)
    param_type = scrapertools.get_match(data, "<a href='javascript:;' onclick=\"orderCategory\('([^']+)'[^>]+> >> </a>")
    logger.info("param_type=" + param_type)
    param_leter = scrapertools.get_match(data,
                                         "<a href='javascript:;' onclick=\"orderCategory\('[^']+','([^']*)'[^>]+> >> </a>")
    logger.info("param_leter=" + param_leter)
    param_pag = scrapertools.get_match(data,
                                       "<a href='javascript:;' onclick=\"orderCategory\('[^']+','[^']*','([^']+)'[^>]+> >> </a>")
    logger.info("param_pag=" + param_pag)
    param_total = scrapertools.get_match(bloque, '"total"\s*\:\s*\'([^\']+)')
    logger.info("param_sql=" + param_total)
    param_sql = scrapertools.get_match(bloque, '"sql"\s*\:\s*\'([^\']+)')
    logger.info("param_sql=" + param_sql)
    param_tot = scrapertools.get_match(bloque, "\"tot\"\s*\:\s*'([^']*)'")
    logger.info("param_tot=" + param_tot)
    param_ban = scrapertools.get_match(bloque, "\"ban\"\s*\:\s*'([^']+)'")
    logger.info("param_ban=" + param_ban)
    param_cate = scrapertools.get_match(bloque, "\"cate\"\s*\:\s*'([^']+)'")
    logger.info("param_cate=" + param_cate)
    base_url = scrapertools.get_match(bloque, "url\s*\:\s*'([^']+)'")
    base_url = re.sub("../..", "http://www.newpct.com", base_url, count=1)
    logger.info("base_url=" + base_url)
    # http://www.newpct.com/include.inc/ajax.php/orderCategory.php?type=todo&leter=&sql=SELECT+DISTINCT+++%09%09%09%09%09%09torrentID%2C+++%09%09%09%09%09%09torrentCategoryID%2C+++%09%09%09%09%09%09torrentCategoryIDR%2C+++%09%09%09%09%09%09torrentImageID%2C+++%09%09%09%09%09%09torrentName%2C+++%09%09%09%09%09%09guid%2C+++%09%09%09%09%09%09torrentShortName%2C++%09%09%09%09%09%09torrentLanguage%2C++%09%09%09%09%09%09torrentSize%2C++%09%09%09%09%09%09calidad+as+calidad_%2C++%09%09%09%09%09%09torrentDescription%2C++%09%09%09%09%09%09torrentViews%2C++%09%09%09%09%09%09rating%2C++%09%09%09%09%09%09n_votos%2C++%09%09%09%09%09%09vistas_hoy%2C++%09%09%09%09%09%09vistas_ayer%2C++%09%09%09%09%09%09vistas_semana%2C++%09%09%09%09%09%09vistas_mes++%09%09%09%09++FROM+torrentsFiles+as+t+WHERE++(torrentStatus+%3D+1+OR+torrentStatus+%3D+2)++AND+(torrentCategoryID+IN+(1537%2C+758%2C+1105%2C+760%2C+1225))++++ORDER+BY+torrentDateAdded++DESC++LIMIT+0%2C+50&pag=3&tot=&ban=3&cate=1225
    url_next_page = base_url + "?" + urllib.urlencode(
        {"total": param_total, "type": param_type, "leter": param_leter, "sql": param_sql, "pag": param_pag,
         "tot": param_tot, "ban": param_ban, "cate": param_cate})
    logger.info("url_next_page=" + url_next_page)
    if item.category == "serie":
        itemlist.append(
            Item(channel=item.channel, action="listado", title=">> Página siguiente", url=url_next_page, extra=bloque,
                 category="serie", viewmode="movie_with_plot"))
    else:
        itemlist.append(
            Item(channel=item.channel, action="listado", title=">> Página siguiente", url=url_next_page, extra=bloque,
                 viewmode="movie_with_plot"))

    return itemlist


def series(item):
    logger.info()
    itemlist = []
    # Lista menú Series de la A-Z
    data = scrapertools.cache_page(item.url)
    patron = '<div id="content-abc">(.*?)<\/div>'
    data = re.compile(patron, re.DOTALL | re.M).findall(data)
    patron = 'id="([^"]+)".*?>([^"]+)<\/a>'
    matches = re.compile(patron, re.DOTALL | re.M).findall(data[0])
    for id, scrapedtitle in matches:
        url_base = "http://www.newpct.com/include.inc/ajax.php/orderCategory.php?total=9&type=letter&leter=%s&sql=+%09%09SELECT++t.torrentID%2C++%09%09%09%09t.torrentCategoryID%2C++%09%09%09%09t.torrentCategoryIDR%2C++%09%09%09%09t.torrentImageID%2C++%09%09%09%09t.torrentName%2C++%09%09%09%09t.guid%2C++%09%09%09%09t.torrentShortName%2C+%09%09%09%09t.torrentLanguage%2C+%09%09%09%09t.torrentSize%2C+%09%09%09%09t.calidad+as+calidad_%2C+%09%09%09%09t.torrentDescription%2C+%09%09%09%09t.torrentViews%2C+%09%09%09%09t.rating%2C+%09%09%09%09t.n_votos%2C+%09%09%09%09t.vistas_hoy%2C+%09%09%09%09t.vistas_ayer%2C+%09%09%09%09t.vistas_semana%2C+%09%09%09%09t.vistas_mes%2C+%09%09%09%09t.imagen+FROM+torrentsFiles+as+t++%09%09LEFT+JOIN+torrentsCategories+as+tc+ON+(t.torrentCategoryID+%3D+tc.categoryID)++%09%09INNER+JOIN++%09%09(+%09%09%09SELECT+torrentID+%09%09%09FROM+torrentsFiles++%09%09%09WHERE++torrentCategoryIDR+%3D+1469+%09%09%09ORDER+BY+torrentID+DESC+%09%09)t1+ON+t1.torrentID+%3D+t.torrentID+WHERE+(t.torrentStatus+%3D+1+OR+t.torrentStatus+%3D+2)+AND+t.home_active+%3D+0++AND+tc.categoryIDR+%3D+1469+GROUP+BY+t.torrentCategoryID+ORDER+BY+t.torrentID+DESC+LIMIT+0%2C+50&pag=&tot=&ban=3&cate=1469"
        scrapedurl = url_base.replace("%s", id)
        if id != "todo": itemlist.append(
            Item(channel=item.channel, action="listaseries", title=scrapedtitle, url=scrapedurl, folder=True))

    return itemlist


def listaseries(item):
    logger.info()
    itemlist = []

    data = scrapertools.downloadpageGzip(item.url)
    patron = "<li[^<]+<a href='([^']+)'>.*?<img src='([^']+)'.*?<h3>([^']+)<\/h3>"
    matches = re.compile(patron, re.DOTALL | re.M).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        itemlist.append(Item(channel=item.channel, action="episodios", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, folder=True))
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = scrapertools.cache_page(item.url)
    patron = "<ul style='display:none;'.*?>(.*?)<\/ul>"
    data = re.compile(patron, re.DOTALL | re.M).findall(data)
    patron = "<a href='([^']+)'.*?title='([^']+)'"
    for index in range(len(data)):
        matches = re.compile(patron, re.DOTALL | re.M).findall(data[index])
        for scrapedurl, scrapedtitle in matches:
            itemlist.append(Item(channel=item.channel, action="findvideos", title=scrapedtitle, url=scrapedurl,
                                 thumbnail=item.thumbnail, folder=True))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = scrapertools.cache_page(item.url)

    # <span id='content-torrent'>                    <a href='http://tumejorjuego.com/descargar/index.php?link=descargar/torrent/58591/el-tour-de-los-muppets-bluray-screener-espanol-castellano-line-2014.html' rel='nofollow' id='58591' title='el-tour-de-los-muppets-bluray-screener-espanol-castellano-line-2014' class='external-url' target='_blank'>
    torrent_url = scrapertools.find_single_match(data, "<span id='content-torrent'[^<]+<a href='([^']+)'")
    if torrent_url != "":
        itemlist.append(Item(channel=item.channel, action="play", title="Torrent", url=torrent_url, server="torrent"))

    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.action = "play"
        videoitem.folder = False
        videoitem.title = "[" + videoitem.server + "]"

    return itemlist
