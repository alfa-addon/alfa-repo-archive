# -*- coding: utf-8 -*-

import os
import re
import sys
import urlparse

from core import channeltools
from core import config
from core import httptools
from core import jsontools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import platformtools

HOST = 'http://www.plusdede.com'
__channel__ = 'plusdede'
parameters = channeltools.get_channel_parameters(__channel__)
fanart_host = parameters['fanart']
thumbnail_host = parameters['thumbnail']
color1, color2, color3 = ['0xFFB10021', '0xFFB10021', '0xFFB10004']


def login():
    url_origen = "https://www.plusdede.com/login?popup=1"
    data = httptools.downloadpage(url_origen, follow_redirects=True).data
    logger.debug("dataPLUSDEDE=" + data)
    if re.search(r'(?i)%s' % config.get_setting("plusdedeuser", "plusdede"), data):
        return True

    token = scrapertools.find_single_match(data, '<input name="_token" type="hidden" value="([^"]+)"')

    post = "_token=" + str(token) + "&email=" + str(
        config.get_setting("plusdedeuser", "plusdede")) + "&password=" + str(
        config.get_setting("plusdedepassword", "plusdede")) + "&app=2131296469"
    # logger.debug("dataPLUSDEDE_POST="+post)
    url = "https://www.plusdede.com/"
    headers = {"Referer": url, "X-Requested-With": "XMLHttpRequest", "X-CSRF-TOKEN": token}
    data = httptools.downloadpage("https://www.plusdede.com/login", post=post, headers=headers,
                                  replace_headers=False).data
    logger.debug("PLUSDEDE_DATA=" + data)
    if "redirect" in data:
        return True
    else:
        return False


def mainlist(item):
    logger.info()
    itemlist = []

    if config.get_setting("plusdedeuser", "plusdede") == "":
        itemlist.append(
            Item(channel=item.channel, title="Habilita tu cuenta en la configuración...", action="settingCanal",
                 url=""))
    else:
        result = login()
        if not result:
            itemlist.append(Item(channel=item.channel, action="mainlist", title="Login fallido. Volver a intentar..."))
            return itemlist

        item.url = HOST
        item.fanart = fanart_host

        item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/Directors%20Chair.png"
        itemlist.append(item.clone(title="Películas", action="menupeliculas", text_color=color3, text_blod=True))

        item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/TV%20Series.png"
        itemlist.append(item.clone(title="Series", action="menuseries", text_color=color3, text_blod=True))

        itemlist.append(item.clone(title="Listas", action="menulistas", text_color=color3, text_blod=True))

        itemlist.append(item.clone(title="", folder=False, thumbnail=thumbnail_host))
        item.thumbnail = ""
        itemlist.append(item.clone(channel=item.channel, action="settingCanal", title="Configuración...", url=""))
    return itemlist


def settingCanal(item):
    return platformtools.show_channel_settings()


def menuseries(item):
    logger.info()
    itemlist = []
    item.url = HOST
    item.fanart = fanart_host
    item.text_color = None

    item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/Directors%20Chair.png"
    itemlist.append(item.clone(title="Películas", action="menupeliculas", text_color=color3, text_blod=True))

    item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/TV%20Series.png"
    itemlist.append(item.clone(title="Series:", folder=False, text_color=color3, text_blod=True, select=True))
    itemlist.append(item.clone(action="peliculas", title="    Novedades", url="https://www.plusdede.com/series"))
    itemlist.append(item.clone(action="generos", title="    Por géneros", url="https://www.plusdede.com/series"))
    itemlist.append(
        item.clone(action="peliculas", title="    Siguiendo", url="https://www.plusdede.com/series/following"))
    itemlist.append(item.clone(action="peliculas", title="    Capítulos Pendientes",
                               url="https://www.plusdede.com/series/mypending/0?popup=1", viewmode="movie"))
    itemlist.append(
        item.clone(action="peliculas", title="    Favoritas", url="https://www.plusdede.com/series/favorites"))
    itemlist.append(
        item.clone(action="peliculas", title="    Pendientes", url="https://www.plusdede.com/series/pending"))
    itemlist.append(item.clone(action="peliculas", title="    Terminadas", url="https://www.plusdede.com/series/seen"))
    itemlist.append(
        item.clone(action="peliculas", title="    Recomendadas", url="https://www.plusdede.com/series/recommended"))
    itemlist.append(item.clone(action="search", title="    Buscar...", url="https://www.plusdede.com/series"))
    itemlist.append(item.clone(title="", folder=False, thumbnail=thumbnail_host))

    itemlist.append(item.clone(title="Listas", action="menulistas", text_color=color3, text_blod=True))
    itemlist.append(item.clone(title="", folder=False, thumbnail=thumbnail_host))
    item.thumbnail = ""
    itemlist.append(Item(channel=item.channel, action="settingCanal", title="Configuración...", url=""))
    return itemlist


def menupeliculas(item):
    logger.info()

    itemlist = []
    item.url = HOST
    item.fanart = fanart_host
    item.text_color = None

    item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/Directors%20Chair.png"
    itemlist.append(item.clone(title="Películas:", folder=False, text_color=color3, text_blod=True, select=True))
    itemlist.append(item.clone(action="peliculas", title="    Novedades", url="https://www.plusdede.com/pelis"))
    itemlist.append(item.clone(action="generos", title="    Por géneros", url="https://www.plusdede.com/pelis"))
    itemlist.append(item.clone(action="peliculas", title="    Solo HD", url="https://www.plusdede.com/pelis?quality=3"))
    itemlist.append(
        item.clone(action="peliculas", title="    Pendientes", url="https://www.plusdede.com/pelis/pending"))
    itemlist.append(
        item.clone(action="peliculas", title="    Recomendadas", url="https://www.plusdede.com/pelis/recommended"))
    itemlist.append(
        item.clone(action="peliculas", title="    Favoritas", url="https://www.plusdede.com/pelis/favorites"))
    itemlist.append(item.clone(action="peliculas", title="    Vistas", url="https://www.plusdede.com/pelis/seen"))
    itemlist.append(item.clone(action="search", title="    Buscar...", url="https://www.plusdede.com/pelis"))

    itemlist.append(item.clone(title="", folder=False, thumbnail=thumbnail_host))
    item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/TV%20Series.png"

    itemlist.append(item.clone(title="Series", action="menuseries", text_color=color3, text_blod=True))

    itemlist.append(item.clone(title="Listas", action="menulistas", text_color=color3, text_blod=True))
    itemlist.append(item.clone(title="", folder=False, thumbnail=thumbnail_host))
    item.thumbnail = ""
    itemlist.append(item.clone(channel=item.channel, action="settingCanal", title="Configuración...", url=""))
    return itemlist


def menulistas(item):
    logger.info()

    itemlist = []
    item.url = HOST
    item.fanart = fanart_host
    item.text_color = None

    item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/Directors%20Chair.png"
    itemlist.append(item.clone(title="Películas", action="menupeliculas", text_color=color3, text_blod=True))

    item.thumbnail = "https://github.com/master-1970/resources/raw/master/images/genres/0/TV%20Series.png"

    itemlist.append(item.clone(title="Series", action="menuseries", text_color=color3, text_blod=True))

    itemlist.append(item.clone(title="Listas:", folder=False, text_color=color3, text_blod=True))
    itemlist.append(
        item.clone(action="listas", tipo="populares", title="    Populares", url="https://www.plusdede.com/listas"))
    itemlist.append(
        item.clone(action="listas", tipo="siguiendo", title="    Siguiendo", url="https://www.plusdede.com/listas"))
    itemlist.append(
        item.clone(action="listas", tipo="tuslistas", title="    Tus Listas", url="https://www.plusdede.com/listas"))
    itemlist.append(item.clone(title="", folder=False, thumbnail=thumbnail_host))
    item.thumbnail = ""
    itemlist.append(item.clone(channel=item.channel, action="settingCanal", title="Configuración...", url=""))
    return itemlist


def generos(item):
    logger.info()
    tipo = item.url.replace("https://www.plusdede.com/", "")
    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    logger.debug("data=" + data)

    # Extrae las entradas (carpetas)
    data = scrapertools.find_single_match(data,
                                          '<select name="genre_id" class="selectpicker" title="Selecciona...">(.*?)</select>')
    patron = '<option  value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for id_genere, title in matches:
        title = title.strip()
        thumbnail = ""
        plot = ""
        # https://www.plusdede.com/pelis?genre_id=1
        url = "https://www.plusdede.com/" + tipo + "?genre_id=" + id_genere
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="peliculas", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title))

    return itemlist


def search(item, texto):
    logger.info()
    item.tipo = item.url.replace("https://www.plusdede.com/", "")
    item.url = "https://www.plusdede.com/search/"
    texto = texto.replace(" ", "-")

    item.url = item.url + texto
    try:
        return buscar(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def buscar(item):
    logger.info()

    # Descarga la pagina
    headers = {"X-Requested-With": "XMLHttpRequest"}
    data = httptools.downloadpage(item.url, headers=headers).data
    logger.debug("data=" + data)

    # Extrae las entradas (carpetas)
    json_object = jsontools.load(data)
    logger.debug("content=" + json_object["content"])
    data = json_object["content"]

    return parse_mixed_results(item, data)


def parse_mixed_results(item, data):
    itemlist = []
    patron = '<div class="media-dropdown mini dropdown model" data-value="([^"]+)"+'
    patron += '.*?<a href="([^"]+)"[^<]data-toggle="tooltip" data-container="body"+'
    patron += ' data-delay="500" title="([^"]+)"[^<]+'
    patron += '.*?src="([^"]+)"+'
    patron += '.*?<div class="year">([^<]+)</div>+'
    patron += '.*?<div class="value"><i class="fa fa-star"></i> ([^<]+)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.tipo == "lista":
        following = scrapertools.find_single_match(data, '<div class="follow-lista-buttons ([^"]+)">')
        data_id = scrapertools.find_single_match(data, 'data-model="10" data-id="([^"]+)">')
        if following.strip() == "following":
            itemlist.append(
                Item(channel='plusdede', title="Dejar de seguir", idtemp=data_id, token=item.token, valor="unfollow",
                     action="plusdede_check", url=item.url, tipo=item.tipo))
        else:
            itemlist.append(
                Item(channel='plusdede', title="Seguir esta lista", idtemp=data_id, token=item.token, valor="follow",
                     action="plusdede_check", url=item.url, tipo=item.tipo))

    for visto, scrapedurl, scrapedtitle, scrapedthumbnail, scrapedyear, scrapedvalue in matches:
        title = ""
        if visto.strip() == "seen":
            title += "[visto] "
        title += scrapertools.htmlclean(scrapedtitle)
        if scrapedyear != '':
            title += " (" + scrapedyear + ")"
        fulltitle = title
        if scrapedvalue != '':
            title += " (" + scrapedvalue + ")"
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        fanart = thumbnail.replace("mediathumb", "mediabigcover")
        plot = ""
        # https://www.plusdede.com/peli/the-lego-movie
        # https://www.plusdede.com/links/view/slug/the-lego-movie/what/peli?popup=1

        if "/peli/" in scrapedurl or "/docu/" in scrapedurl:

            # sectionStr = "peli" if "/peli/" in scrapedurl else "docu"
            if "/peli/" in scrapedurl:
                sectionStr = "peli"
            else:
                sectionStr = "docu"
            referer = urlparse.urljoin(item.url, scrapedurl)
            url = urlparse.urljoin(item.url, scrapedurl)
            logger.debug("PELII_title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
            if item.tipo != "series":
                itemlist.append(Item(channel=item.channel, action="findvideos", title=title, extra=referer, url=url,
                                     thumbnail=thumbnail, plot=plot, fulltitle=fulltitle, fanart=fanart,
                                     contentTitle=scrapedtitle, contentType="movie", context=["buscar_trailer"]))
        else:
            referer = item.url
            url = urlparse.urljoin(item.url, scrapedurl)
            logger.debug("SERIE_title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
            if item.tipo != "pelis":
                itemlist.append(Item(channel=item.channel, action="episodios", title=title, extra=referer, url=url,
                                     thumbnail=thumbnail, plot=plot, fulltitle=fulltitle, show=title, fanart=fanart,
                                     contentTitle=scrapedtitle, contentType="tvshow", context=["buscar_trailer"]))

    next_page = scrapertools.find_single_match(data,
                                               '<div class="onclick load-more-icon no-json" data-action="replace" data-url="([^"]+)">')
    if next_page != "":
        url = urlparse.urljoin("https://www.plusdede.com", next_page).replace("amp;", "")
        logger.debug("URL_SIGUIENTE:" + url)
        itemlist.append(
            Item(channel=item.channel, action="pag_sig", token=item.token, title=">> Página siguiente",
                 extra=item.extra, url=url))

    try:
        import xbmcplugin
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    except:
        pass
    return itemlist


def siguientes(item):  # No utilizada
    logger.info()

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    logger.debug("data=" + data)

    # Extrae las entradas (carpetas)
    bloque = scrapertools.find_single_match(data, '<h2>Siguiendo</h2>(.*?)<div class="box">')
    patron = '<div class="coverMini     shadow tiptip" title="([^"]+)">[^<]+'
    patron += '<img class="centeredPic centeredPicFalse"  onerror="[^"]+"  src="([^"]+)"[^<]+'
    patron += '<img src="/images/loading-mini.gif" class="loader"/>[^<]+'
    patron += '<div class="extra-info"><span class="year">[^<]+'
    patron += '</span><span class="value"><i class="icon-star"></i>[^<]+'
    patron += '</span></div>[^<]+'
    patron += '</div>[^<]+'
    patron += '</a>[^<]+'
    patron += '<a class="userepiinfo defaultLink" href="([^"]+)">(\d+)x(\d+)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    # for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
    for scrapedtitle, scrapedthumbnail, scrapedurl, scrapedsession, scrapedepisode in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        session = scrapertools.htmlclean(scrapedsession)
        episode = scrapertools.htmlclean(scrapedepisode)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        fanart = thumbnail.replace("mediathumb", "mediabigcover")
        plot = ""
        title = session + "x" + episode + " - " + title
        # https://www.plusdede.com/peli/the-lego-movie
        # https://www.plusdede.com/links/view/slug/the-lego-movie/what/peli?popup=1

        referer = urlparse.urljoin(item.url, scrapedurl)
        url = referer
        # itemlist.append( Item(channel=item.channel, action="episodios" , title=title , url=url, thumbnail=thumbnail, plot=plot, fulltitle=title, show=title))
        itemlist.append(
            Item(channel=item.channel, action="episodio", title=title, url=url, thumbnail=thumbnail, plot=plot,
                 fulltitle=title, show=title, fanart=fanart, extra=session + "|" + episode))

        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

    return itemlist


def episodio(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    # logger.debug("data="+data)

    session = str(int(item.extra.split("|")[0]))
    episode = str(int(item.extra.split("|")[1]))
    patrontemporada = '<div class="checkSeason"[^>]+>Temporada ' + session + '<div class="right" onclick="controller.checkSeason(.*?)\s+</div></div>'
    matchestemporadas = re.compile(patrontemporada, re.DOTALL).findall(data)

    for bloque_episodios in matchestemporadas:
        logger.debug("bloque_episodios=" + bloque_episodios)

        # Extrae los episodios
        patron = '<span class="title defaultPopup" href="([^"]+)"><span class="number">' + episode + ' </span>([^<]+)</span>(\s*</div>\s*<span[^>]*><span[^>]*>[^<]*</span><span[^>]*>[^<]*</span></span><div[^>]*><button[^>]*><span[^>]*>[^<]*</span><span[^>]*>[^<]*</span></button><div class="action([^"]*)" data-action="seen">)?'
        matches = re.compile(patron, re.DOTALL).findall(bloque_episodios)

        for scrapedurl, scrapedtitle, info, visto in matches:
            # visto_string = "[visto] " if visto.strip()=="active" else ""
            if visto.strip() == "active":
                visto_string = "[visto] "
            else:
                visto_string = ""
            numero = episode
            title = visto_string + session + "x" + numero + " " + scrapertools.htmlclean(scrapedtitle)
            thumbnail = ""
            plot = ""
            # https://www.plusdede.com/peli/the-lego-movie
            # https://www.plusdede.com/links/view/slug/the-lego-movie/what/peli?popup=1
            # https://www.plusdede.com/links/viewepisode/id/475011?popup=1
            epid = scrapertools.find_single_match(scrapedurl, "id/(\d+)")
            url = "https://www.plusdede.com/links/viewepisode/id/" + epid
            itemlist.append(
                Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                     fulltitle=title, fanart=item.fanart, show=item.show))
            logger.debug("Abrimos title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

    itemlist2 = []
    for capitulo in itemlist:
        itemlist2 = findvideos(capitulo)
    return itemlist2


def peliculas(item):
    logger.info()

    # Descarga la pagina
    headers = {"X-Requested-With": "XMLHttpRequest"}
    data = httptools.downloadpage(item.url, headers=headers).data
    # logger.debug("data_DEF_PELICULAS="+data)

    # Extrae las entradas (carpetas)
    json_object = jsontools.load(data)
    logger.debug("html=" + json_object["content"])
    data = json_object["content"]

    return parse_mixed_results(item, data)


def episodios(item):
    logger.info()
    itemlist = []

    # Descarga la pagina
    idserie = ''
    data = httptools.downloadpage(item.url).data
    # logger.debug("dataEPISODIOS="+data)
    patrontemporada = '<ul.*?<li class="season-header" >([^<]+)<(.*?)\s+</ul>'
    matchestemporadas = re.compile(patrontemporada, re.DOTALL).findall(data)
    logger.debug(matchestemporadas)
    idserie = scrapertools.find_single_match(data, 'data-model="5" data-id="(\d+)"')
    token = scrapertools.find_single_match(data, '_token" content="([^"]+)"')
    if (config.get_platform().startswith("xbmc") or config.get_platform().startswith("kodi")):
        itemlist.append(Item(channel=item.channel, action="infosinopsis", title="INFO / SINOPSIS", url=item.url,
                             thumbnail=item.thumbnail, fanart=item.fanart, folder=False))
    for nombre_temporada, bloque_episodios in matchestemporadas:
        logger.debug("nombre_temporada=" + nombre_temporada)
        logger.debug("bloque_episodios=" + bloque_episodios)
        logger.debug("id_serie=" + idserie)
        # Extrae los episodios
        patron_episodio = '<li><a href="#"(.*?)</a></li>'
        # patron  =  '<li><a href="#" data-id="([^"]*)".*?data-href="([^"]+)">\s*<div class="name">\s*<span class="num">([^<]+)</span>\s*([^<]+)\s*</div>.*?"show-close-footer episode model([^"]+)"'
        matches = re.compile(patron_episodio, re.DOTALL).findall(bloque_episodios)
        # logger.debug(matches)
        for data_episodio in matches:

            scrapeid = scrapertools.find_single_match(data_episodio, '<li><a href="#" data-id="([^"]*)"')
            scrapedurl = scrapertools.find_single_match(data_episodio, 'data-href="([^"]+)">\s*<div class="name">')
            numero = scrapertools.find_single_match(data_episodio, '<span class="num">([^<]+)</span>')
            scrapedtitle = scrapertools.find_single_match(data_episodio,
                                                          '<span class="num">.*?</span>\s*([^<]+)\s*</div>')
            visto = scrapertools.find_single_match(data_episodio, '"show-close-footer episode model([^"]+)"')

            title = nombre_temporada.replace("Temporada ", "").replace("Extras de la serie", "Extras 0").replace(" ",
                                                                                                                 "") + "x" + numero + " " + scrapertools.htmlclean(
                scrapedtitle)
            logger.debug("CAP_VISTO:" + visto)
            if visto.strip() == "seen":
                title = "[visto] " + title

            thumbnail = item.thumbnail
            fanart = item.fanart
            plot = ""
            # https://www.plusdede.com/peli/the-lego-movie
            # https://www.plusdede.com/links/view/slug/the-lego-movie/what/peli?popup=1
            # https://www.plusdede.com/links/viewepisode/id/475011?popup=1
            # epid = scrapertools.find_single_match(scrapedurl,"id/(\d+)")
            url = "https://www.plusdede.com" + scrapedurl
            itemlist.append(
                Item(channel=item.channel, action="findvideos", nom_serie=item.title, tipo="5", title=title, url=url,
                     thumbnail=thumbnail, plot=plot, fulltitle=title, fanart=fanart, show=item.show))

            logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

    if config.get_videolibrary_support():
        # con año y valoracion la serie no se puede actualizar correctamente, si ademas cambia la valoracion, creara otra carpeta
        # Sin año y sin valoración:
        show = re.sub(r"\s\(\d+\)\s\(\d+\.\d+\)", "", item.show)
        # Sin año:
        # show = re.sub(r"\s\(\d+\)", "", item.show)
        # Sin valoración:
        # show = re.sub(r"\s\(\d+\.\d+\)", "", item.show)
        itemlist.append(
            Item(channel='plusdede', title="Añadir esta serie a la biblioteca de XBMC", url=item.url, token=token,
                 action="add_serie_to_library", extra="episodios###", show=show))
        itemlist.append(
            Item(channel='plusdede', title="Descargar todos los episodios de la serie", url=item.url, token=token,
                 action="download_all_episodes", extra="episodios", show=show))
        itemlist.append(Item(channel='plusdede', title="Marcar como Pendiente", tipo="5", idtemp=idserie, token=token,
                             valor="pending", action="plusdede_check", show=show))
        itemlist.append(Item(channel='plusdede', title="Marcar como Siguiendo", tipo="5", idtemp=idserie, token=token,
                             valor="following", action="plusdede_check", show=show))
        itemlist.append(Item(channel='plusdede', title="Marcar como Finalizada", tipo="5", idtemp=idserie, token=token,
                             valor="seen", action="plusdede_check", show=show))
        itemlist.append(Item(channel='plusdede', title="Marcar como Favorita", tipo="5", idtemp=idserie, token=token,
                             valor="favorite", action="plusdede_check", show=show))
        itemlist.append(
            Item(channel='plusdede', title="Quitar marca", tipo="5", idtemp=idserie, token=token, valor="nothing",
                 action="plusdede_check", show=show))
        itemlist.append(
            Item(channel='plusdede', title="Añadir a lista", tipo="5", tipo_esp="lista", idtemp=idserie, token=token,
                 action="plusdede_check", show=show))
    return itemlist


def parse_listas(item, bloque_lista):
    logger.info()

    if item.tipo == "populares":
        patron = '<div class="lista(.*?)</div>\s*</h4>'
    else:
        patron = '<div class="lista(.*?)</h4>\s*</div>'
    matches = re.compile(patron, re.DOTALL).findall(bloque_lista)
    itemlist = []

    for lista in matches:
        scrapedurl = scrapertools.htmlclean(scrapertools.find_single_match(lista, '<a href="([^"]+)">[^<]+</a>'))
        scrapedtitle = scrapertools.find_single_match(lista, '<a href="[^"]+">([^<]+)</a>')
        scrapedfollowers = scrapertools.find_single_match(lista, 'Follow: <span class="number">([^<]+)')
        scrapedseries = scrapertools.find_single_match(lista, '<div class="lista-stat badge">Series: ([^<]+)')
        scrapedpelis = scrapertools.find_single_match(lista, '<div class="lista-stat badge">Pelis: ([^<]+)')

        title = scrapertools.htmlclean(scrapedtitle) + ' ('
        if scrapedpelis != '':
            title += scrapedpelis + ' pelis, '
        if scrapedseries != '':
            title += scrapedseries + ' series, '
        if scrapedfollowers != '':
            title += scrapedfollowers + ' seguidores'
        title += ')'
        url = urlparse.urljoin("https://www.plusdede.com", scrapedurl)
        thumbnail = ""
        itemlist.append(
            Item(channel=item.channel, action="peliculas", token=item.token, tipo="lista", title=title, url=url))
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "], tipo =[lista]")

    nextpage = scrapertools.find_single_match(bloque_lista,
                                              '<div class="onclick load-more-icon no-json" data-action="replace" data-url="([^"]+)"')
    if nextpage != '':
        url = urlparse.urljoin("https://www.plusdede.com", nextpage)
        itemlist.append(Item(channel=item.channel, action="lista_sig", token=item.token, tipo=item.tipo,
                             title=">> Página siguiente", extra=item.extra, url=url))

    try:
        import xbmcplugin
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    except:
        pass

    return itemlist


def listas(item):
    logger.info()
    if item.tipo == "tuslistas":
        patron = 'Tus listas(.*?)>Listas que sigues<'
    elif item.tipo == "siguiendo":
        patron = '<h3>Listas que sigues</h3>(.*?)<h2>Listas populares</h2>'
    else:
        patron = '<div class="content">\s*<h2>Listas populares(.*?)</div>\s*</div>\s*</div>\s*</div>\s*</div>'

    data = httptools.downloadpage(item.url).data
    logger.debug("dataSINHEADERS=" + data)

    item.token = scrapertools.find_single_match(data, '_token" content="([^"]+)"').strip()
    logger.debug("token_LISTA_" + item.token)

    bloque_lista = scrapertools.find_single_match(data, patron)
    logger.debug("bloque_LISTA" + bloque_lista)

    return parse_listas(item, bloque_lista)


def lista_sig(item):
    logger.info()

    headers = {"X-Requested-With": "XMLHttpRequest"}
    data = httptools.downloadpage(item.url, headers=headers).data
    logger.debug("data=" + data)

    return parse_listas(item, data)


def pag_sig(item):
    logger.info()

    headers = {"X-Requested-With": "XMLHttpRequest"}
    data = httptools.downloadpage(item.url, headers=headers).data
    logger.debug("data=" + data)

    return parse_mixed_results(item, data)


def findvideos(item, verTodos=False):
    logger.info()

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    logger.info(data)
    # logger.debug("data="+data)

    data_model = scrapertools.find_single_match(data, 'data-model="([^"]+)"')
    data_id = scrapertools.find_single_match(data, 'data-id="([^"]+)"')
    trailer = "https://www.youtube.com/watch?v=" + scrapertools.find_single_match(data,
                                                                                  'data-youtube="([^"]+)" class="youtube-link')

    url = "https://www.plusdede.com/aportes/" + data_model + "/" + data_id + "?popup=1"

    data = httptools.downloadpage(url).data
    # logger.debug("dataLINKS"+data)
    token = scrapertools.find_single_match(data, '_token" content="([^"]+)"')

    patron = '<a target="_blank" (.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    idpeli = data_id
    if (config.get_platform().startswith("xbmc") or config.get_platform().startswith("kodi")) and data_model == "4":
        itemlist.append(Item(channel=item.channel, action="infosinopsis", title="INFO / SINOPSIS", url=item.url,
                             thumbnail=item.thumbnail, fanart=item.fanart, folder=False))

        logger.debug("TRAILER_YOUTUBE:" + trailer)
        itemlist.append(Item(channel=item.channel, action="play", title="TRAILER", url=item.url, trailer=trailer,
                             thumbnail=item.thumbnail, fanart=item.fanart, folder=False))

    itemsort = []
    sortlinks = config.get_setting("plusdedesortlinks",
                                   item.channel)  # 0:no, 1:valoracion, 2:idioma, 3:calidad, 4:idioma+calidad, 5:idioma+valoracion, 6:idioma+calidad+valoracion
    showlinks = config.get_setting("plusdedeshowlinks", item.channel)  # 0:todos, 1:ver online, 2:descargar

    # sortlinks = int(sortlinks) if sortlinks != '' and sortlinks !="No" else 0
    # showlinks = int(showlinks) if showlinks != '' and showlinks !="No" else 0

    if sortlinks != '' and sortlinks != "No":
        sortlinks = int(sortlinks)
    else:
        sortlinks = 0

    if showlinks != '' and showlinks != "No":
        showlinks = int(showlinks)
    else:
        showlinks = 0

    for match in matches:
        # logger.debug("match="+match)

        jdown = scrapertools.find_single_match(match, '<span class="fa fa-download"></span>([^<]+)')
        if (showlinks == 1 and jdown != '') or (
                showlinks == 2 and jdown == ''):  # Descartar enlaces veronline/descargar
            continue
        idioma_1 = ""
        idiomas = re.compile('<img src="https://cdn.plusdede.com/images/flags/([^"]+).png', re.DOTALL).findall(match)
        idioma_0 = idiomas[0]
        if len(idiomas) > 1:
            idioma_1 = idiomas[1]
            idioma = idioma_0 + ", SUB " + idioma_1
        else:
            idioma_1 = ''
            idioma = idioma_0

        calidad_video = scrapertools.find_single_match(match,
                                                       '<span class="fa fa-video-camera"></span>(.*?)</div>').replace(
            "  ", "").replace("\n", "")
        logger.debug("calidad_video=" + calidad_video)
        calidad_audio = scrapertools.find_single_match(match,
                                                       '<span class="fa fa-headphones"></span>(.*?)</div>').replace(
            "  ", "").replace("\n", "")
        logger.debug("calidad_audio=" + calidad_audio)

        thumb_servidor = scrapertools.find_single_match(match, '<img src="([^"]+)">')
        logger.debug("thumb_servidor=" + thumb_servidor)
        nombre_servidor = scrapertools.find_single_match(thumb_servidor, "hosts/([^\.]+).png")
        logger.debug("nombre_servidor=" + nombre_servidor)

        if jdown != '':
            title = "Download " + nombre_servidor + " (" + idioma + ") (Calidad " + calidad_video.strip() + ", audio " + calidad_audio.strip() + ")"
        else:
            title = "Ver en " + nombre_servidor + " (" + idioma + ") (Calidad " + calidad_video.strip() + ", audio " + calidad_audio.strip() + ")"

        valoracion = 0

        reports = scrapertools.find_single_match(match,
                                                 '<i class="fa fa-exclamation-triangle"></i><br/>\s*<span class="number" data-num="([^"]*)">')
        valoracion -= int(reports)
        title += " (" + reports + " reps)"

        url = urlparse.urljoin(item.url, scrapertools.find_single_match(match, 'href="([^"]+)"'))
        thumbnail = thumb_servidor
        plot = ""
        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        if sortlinks > 0:
            # orden1 para dejar los "downloads" detras de los "ver" al ordenar
            # orden2 segun configuración
            if sortlinks == 1:
                orden = valoracion
            elif sortlinks == 2:
                orden = valora_idioma(idioma_0, idioma_1)
            elif sortlinks == 3:
                orden = valora_calidad(calidad_video, calidad_audio)
            elif sortlinks == 4:
                orden = (valora_idioma(idioma_0, idioma_1) * 100) + valora_calidad(calidad_video, calidad_audio)
            elif sortlinks == 5:
                orden = (valora_idioma(idioma_0, idioma_1) * 1000) + valoracion
            elif sortlinks == 6:
                orden = (valora_idioma(idioma_0, idioma_1) * 100000) + (
                valora_calidad(calidad_video, calidad_audio) * 1000) + valoracion
            itemsort.append(
                {'action': "play", 'title': title, 'data_id': data_id, 'token': token, 'tipo': data_model, 'url': url,
                 'thumbnail': thumbnail, 'fanart': item.fanart, 'plot': plot, 'extra': item.url,
                 'fulltitle': item.fulltitle, 'orden1': (jdown == ''), 'orden2': orden})
        else:
            itemlist.append(
                Item(channel=item.channel, action="play", data_id=data_id, token=token, tipo=data_model, title=title,
                     url=url, thumbnail=thumbnail, fanart=item.fanart, plot=plot, extra=item.url,
                     fulltitle=item.fulltitle))

    if sortlinks > 0:
        numberlinks = config.get_setting("plusdedenumberlinks", item.channel)  # 0:todos, > 0:n*5 (5,10,15,20,...)
        # numberlinks = int(numberlinks) if numberlinks != '' and numberlinks !="No" else 0
        if numberlinks != '' and numberlinks != "No":
            numberlinks = int(numberlinks)
        else:
            numberlinks = 0

        if numberlinks == 0:
            verTodos = True
        itemsort = sorted(itemsort, key=lambda k: (k['orden1'], k['orden2']), reverse=True)
        for i, subitem in enumerate(itemsort):
            if verTodos == False and i >= numberlinks:
                itemlist.append(
                    Item(channel=item.channel, action='findallvideos', title='Ver todos los enlaces', url=item.url,
                         extra=item.extra))
                break
            itemlist.append(
                Item(channel=item.channel, action=subitem['action'], title=subitem['title'], data_id=subitem['data_id'],
                     token=subitem['token'], tipo=subitem['tipo'], url=subitem['url'], thumbnail=subitem['thumbnail'],
                     fanart=subitem['fanart'], plot=subitem['plot'], extra=subitem['extra'],
                     fulltitle=subitem['fulltitle']))

    if data_model == "4":
        itemlist.append(
            Item(channel=item.channel, action="plusdede_check", tipo="4", token=token, title="Marcar como Pendiente",
                 valor="pending", idtemp=idpeli))
        itemlist.append(
            Item(channel=item.channel, action="plusdede_check", tipo="4", token=token, title="Marcar como Vista",
                 valor="seen", idtemp=idpeli))
        itemlist.append(
            Item(channel=item.channel, action="plusdede_check", tipo="4", token=token, title="Marcar como Favorita",
                 valor="favorite", idtemp=idpeli))
        itemlist.append(Item(channel=item.channel, action="plusdede_check", tipo="4", token=token, title="Quitar Marca",
                             valor="nothing", idtemp=idpeli))
        itemlist.append(
            Item(channel='plusdede', title="Añadir a lista", tipo="4", tipo_esp="lista", idtemp=idpeli, token=token,
                 action="plusdede_check"))
    return itemlist


def findallvideos(item):
    return findvideos(item, True)


def play(item):
    itemlist = []
    if "trailer" in item:
        url = item.trailer
        itemlist = servertools.find_video_items(data=url)

        for videoitem in itemlist:
            videoitem.title = item.title
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = item.channel

        return itemlist
    else:
        logger.info("url=" + item.url)

        # Hace la llamada
        headers = {'Referer': item.extra}

        data = httptools.downloadpage(item.url, headers=headers).data
        # logger.debug("dataLINK="+data)
        url = scrapertools.find_single_match(data,
                                             '<a href="([^"]+)" target="_blank"><button class="btn btn-primary">visitar enlace</button>')
        url = urlparse.urljoin("https://www.plusdede.com", url)
        # logger.debug("DATA_LINK_FINAL:"+url)

        logger.debug("URL_PLAY:" + url)
        headers = {'Referer': item.url}
        media_url = httptools.downloadpage(url, headers=headers, follow_redirects=False).headers.get("location")
        # logger.info("media_url="+media_url)

        itemlist = servertools.find_video_items(data=media_url)

        for videoitem in itemlist:
            videoitem.title = item.title
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = item.channel

        # Marcar como visto
        logger.debug(item)
        checkseen(item)

        return itemlist


def checkseen(item):
    logger.info(item)
    url_temp = ""
    if item.tipo == "8":
        url_temp = "https://www.plusdede.com/set/episode/" + item.data_id + "/seen"
        tipo_str = "series"
        headers = {"Referer": "https://www.plusdede.com/serie/", "X-Requested-With": "XMLHttpRequest",
                   "X-CSRF-TOKEN": item.token}
    else:
        url_temp = "https://www.plusdede.com/set/usermedia/" + item.tipo + "/" + item.data_id + "/seen"
        tipo_str = "pelis"
        headers = {"Referer": "https://www.plusdede.com/" + tipo_str, "X-Requested-With": "XMLHttpRequest",
                   "X-CSRF-TOKEN": item.token}
    logger.debug("Entrando a checkseen " + url_temp + item.token)
    data = httptools.downloadpage(url_temp, post="id=" + item.idtemp, headers=headers, replace_headers=True).data
    return True


def infosinopsis(item):
    logger.info()

    data = httptools.downloadpage(item.url).data
    logger.debug("SINOPSISdata=" + data)

    scrapedtitle = scrapertools.find_single_match(data, '<div class="media-title">([^<]+)</div>')
    scrapedvalue = scrapertools.find_single_match(data, '<span class="value">([^<]+)</span>')
    scrapedyear = scrapertools.find_single_match(data,
                                                 '<strong>Fecha</strong>\s*<div class="mini-content">([^<]+)</div>').strip()
    scrapedduration = scrapertools.htmlclean(scrapertools.find_single_match(data,
                                                                            '<strong>Duración</strong>\s*<div class="mini-content">([^<]+)</div>').strip().replace(
        "   ", "").replace("\n", ""))
    logger.debug(scrapedduration)
    scrapedplot = scrapertools.find_single_match(data, '<div class="plot expandable">([^<]+)<div').strip()
    logger.debug("SINOPSISdataplot=" + scrapedplot)
    generos = scrapertools.find_single_match(data, '<strong>Género</strong>\s*<ul>(.*?)</ul>')
    logger.debug("generos=" + generos)
    scrapedgenres = re.compile('<li>([^<]+)</li>', re.DOTALL).findall(generos)
    scrapedcasting = re.compile(
        '<a href="https://www.plusdede.com/star/[^"]+"><div class="text-main">([^<]+)</div></a>\s*<div class="text-sub">\s*([^<]+)</div>',
        re.DOTALL).findall(data)
    title = scrapertools.htmlclean(scrapedtitle)
    plot = "[B]Año: [/B]" + scrapedyear
    plot += "  [B]Duración: [/B]" + scrapedduration
    plot += "  [B]Puntuación usuarios: [/B]" + scrapedvalue
    plot += "\n[B]Géneros: [/B]" + ", ".join(scrapedgenres)
    plot += "\n\n[B]Sinopsis:[/B]\n" + scrapertools.htmlclean(scrapedplot)
    plot += "\n\n[B]Casting:[/B]\n"
    for actor, papel in scrapedcasting:
        plot += actor + " (" + papel.strip() + ")\n"

    tbd = TextBox("DialogTextViewer.xml", os.getcwd(), "Default")
    tbd.ask(title, plot)
    del tbd
    return


try:
    import xbmcgui


    class TextBox(xbmcgui.WindowXML):
        """ Create a skinned textbox window """

        def __init__(self, *args, **kwargs):
            pass

        def onInit(self):
            try:
                self.getControl(5).setText(self.text)
                self.getControl(1).setLabel(self.title)
            except:
                pass

        def onClick(self, controlId):
            pass

        def onFocus(self, controlId):
            pass

        def onAction(self, action):
            if action == 7:
                self.close()

        def ask(self, title, text):
            self.title = title
            self.text = text
            self.doModal()
except:
    pass


# Valoraciones de enlaces, los valores más altos se mostrarán primero :

def valora_calidad(video, audio):
    prefs_video = ['hdmicro', 'hd1080', 'hd720', 'hdrip', 'dvdrip', 'rip', 'tc-screener', 'ts-screener']
    prefs_audio = ['dts', '5.1', 'rip', 'line', 'screener']

    video = ''.join(video.split()).lower()
    # pts = (9 - prefs_video.index(video) if video in prefs_video else 1) * 10
    if video in prefs_video:
        pts = (9 - prefs_video.index(video)) * 10
    else:
        pts = (9 - 1) * 10

    audio = ''.join(audio.split()).lower()
    # pts += 9 - prefs_audio.index(audio) if audio in prefs_audio else 1
    if audio in prefs_audio:
        pts = (9 - prefs_audio.index(audio)) * 10
    else:
        pts = (9 - 1) * 10

    return pts


def valora_idioma(idioma_0, idioma_1):
    prefs = ['spanish', 'latino', 'catalan', 'english', 'french']
    # pts = (9 - prefs.index(idioma_0) if idioma_0 in prefs else 1) * 10
    if idioma_0 in prefs:
        pts = (9 - prefs.index(idioma_0)) * 10
    else:
        pts = (9 - 1) * 10

    if idioma_1 != '':  # si hay subtítulos
        idioma_1 = idioma_1.replace(' SUB', '')

        # pts += 8 - prefs.index(idioma_1) if idioma_1 in prefs else 1
        if idioma_1 in prefs:
            pts += 8 - prefs.index(idioma_1)
        else:
            pts += 8 - 1

    else:
        pts += 9  # sin subtítulos por delante
    return pts


def plusdede_check(item):
    if item.tipo_esp == "lista":
        url_temp = "https://www.plusdede.com/listas/addmediapopup/" + item.tipo + "/" + item.idtemp + "?popup=1"
        data = httptools.downloadpage(url_temp).data
        logger.debug("DATA_CHECK_LISTA:" + data)

        patron = '<div class="lista model" data-model="10" data-id="([^"]+)">+'
        patron += '.*?<a href="/lista/[^"]+">([^<]+)</a>+'
        matches = re.compile(patron, re.DOTALL).findall(data)
        itemlist = []
        for id_lista, nombre_lista in matches:
            itemlist.append(Item(channel=item.channel, action="plusdede_check", tipo=item.tipo, tipo_esp="add_list",
                                 token=item.token, title=nombre_lista, idlista=id_lista, idtemp=item.idtemp))
        if len(itemlist) < 1:
            itemlist.append(Item(channel=item.channel, action="", title="No tienes ninguna lista creada por ti!"))
        return itemlist
    else:

        if item.tipo == "10" or item.tipo == "lista":
            url_temp = "https://www.plusdede.com/set/lista/" + item.idtemp + "/" + item.valor
        else:
            if (item.tipo_esp == "add_list"):
                url_temp = "https://www.plusdede.com/set/listamedia/" + item.idlista + "/add/" + item.tipo + "/" + item.idtemp
            else:
                url_temp = "https://www.plusdede.com/set/usermedia/" + item.tipo + "/" + item.idtemp + "/" + item.valor
        # httptools.downloadpage(url_temp, post="id="+item.idtemp)
        if item.tipo == "5":
            tipo_str = "series"
        elif item.tipo == "lista":
            tipo_str = "listas"
        else:
            tipo_str = "pelis"
        headers = {"Referer": "https://www.plusdede.com/" + tipo_str, "X-Requested-With": "XMLHttpRequest",
                   "X-CSRF-TOKEN": item.token}
        data = httptools.downloadpage(url_temp, post="id=" + item.idtemp, headers=headers,
                                      replace_headers=True).data.strip()
        logger.debug("URL_PLUSDEDECHECK_DATA=" + url_temp + " ITEM:TIPO=" + item.tipo)
        logger.debug("PLUSDEDECHECK_DATA=" + data)
        dialog = platformtools
        dialog.ok = platformtools.dialog_ok
        if data == "1":
            if item.valor != "nothing":
                dialog.ok('SUCCESS', 'Marca realizada con éxito!')
            elif item.valor == "nothing":
                dialog.ok('SUCCESS', 'Marca eliminada con éxito!')
        elif item.valor == "unfollow":
            dialog.ok('SUCCESS', 'Has dejado de seguir esta lista!')
        elif item.valor == "follow":
            dialog.ok('SUCCESS', 'Has comenzado a seguir esta lista!')
        elif item.tipo_esp == "add_list":
            dialog.ok('SUCCESS', 'Añadido a la lista!')
        else:
            dialog.ok('ERROR', 'No se pudo realizar la acción!')