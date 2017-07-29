# -*- coding: utf-8 -*-

import re

from core import config
from core import httptools
from core import jsontools as json
from core import logger
from core import scrapertools
from core import tmdb
from core.item import Item

sid = config.get_setting("sid_playmax", "playmax")
apikey = "0ea143087685e9e0a23f98ae"
__modo_grafico__ = config.get_setting('modo_grafico', 'playmax')
__perfil__ = config.get_setting('perfil', "playmax")
__menu_info__ = config.get_setting('menu_info', 'playmax')

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00', '0xFFFE2E2E', '0xFF088A08'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E', '0xFFFE2E2E', '0xFF088A08'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE', '0xFFFE2E2E', '0xFF088A08']]

if __perfil__ - 1 >= 0:
    color1, color2, color3, color4, color5 = perfil[__perfil__ - 1]
else:
    color1 = color2 = color3 = color4 = color5 = ""

host = "https://playmax.mx"


def login():
    logger.info()

    try:
        user = config.get_setting("playmaxuser", "playmax")
        password = config.get_setting("playmaxpassword", "playmax")
        if user == "" and password == "":
            return False, "Para ver los enlaces de este canal es necesario registrarse en playmax.mx"
        elif user == "" or password == "":
            return False, "Usuario o contraseña en blanco. Revisa tus credenciales"

        data = httptools.downloadpage("https://playmax.mx/ucp.php?mode=login").data
        if re.search(r'(?i)class="hb_user_data" title="%s"' % user, data):
            if not config.get_setting("sid_playmax", "playmax"):
                sid_ = scrapertools.find_single_match(data, 'sid=([^"]+)"')
                if not sid_:
                    sid_ = scrapertools.find_single_match(config.get_cookie_data(), 'playmax.*?_sid\s*([A-z0-9]+)')
                config.set_setting("sid_playmax", sid_, "playmax")
            return True, ""

        confirm_id = scrapertools.find_single_match(data, 'name="confirm_id" value="([^"]+)"')
        sid_log = scrapertools.find_single_match(data, 'name="sid" value="([^"]+)"')
        post = "username=%s&password=%s&autologin=on&agreed=true&change_lang=0&confirm_id=%s&login=&sid=%s" \
               "&redirect=index.php&login=Entrar" % (user, password, confirm_id, sid_log)
        data = httptools.downloadpage("https://playmax.mx/ucp.php?mode=login", post=post).data
        if "contraseña incorrecta" in data:
            logger.error("Error en el login")
            return False, "Contraseña errónea. Comprueba tus credenciales"
        elif "nombre de usuario incorrecto" in data:
            logger.error("Error en el login")
            return False, "Nombre de usuario no válido. Comprueba tus credenciales"
        else:
            logger.info("Login correcto")
            sid_ = scrapertools.find_single_match(data, 'sid=([^"]+)"')
            if not sid_:
                sid_ = scrapertools.find_single_match(config.get_cookie_data(), 'playmax.*?_sid\s*([A-z0-9]+)')
            config.set_setting("sid_playmax", sid_, "playmax")
            # En el primer logueo se activa la busqueda global y la seccion novedades
            if not config.get_setting("primer_log", "playmax"):
                config.set_setting("include_in_global_search", True, "playmax")
                config.set_setting("include_in_newest_peliculas", True, "playmax")
                config.set_setting("include_in_newest_series", True, "playmax")
                config.set_setting("include_in_newest_infantiles", True, "playmax")
                config.set_setting("primer_log", False, "playmax")
            return True, ""
    except:
        import traceback
        logger.error(traceback.format_exc())
        return False, "Error en el login. Comprueba tus credenciales o si la web está operativa"


def mainlist(item):
    logger.info()
    itemlist = []
    item.text_color = color1

    logueado, error_message = login()

    if not logueado:
        config.set_setting("include_in_global_search", False, "playmax")
        itemlist.append(item.clone(title=error_message, action="configuracion", folder=False))
        return itemlist

    itemlist.append(item.clone(title="Películas", action="", text_color=color2))
    item.contentType = "movie"
    itemlist.append(
        item.clone(title="     Novedades", action="fichas", url=host + "/catalogo.php?tipo[]=2&ad=2&ordenar="
                                                                       "novedades&con_dis=on"))
    itemlist.append(
        item.clone(title="     Populares", action="fichas", url=host + "/catalogo.php?tipo[]=2&ad=2&ordenar="
                                                                       "pop&con_dis=on"))
    itemlist.append(item.clone(title="     Índices", action="indices"))

    itemlist.append(item.clone(title="Series", action="", text_color=color2))
    item.contentType = "tvshow"
    itemlist.append(item.clone(title="     Nuevos capítulos", action="fichas", url=host + "/catalogo.php?tipo[]=1&ad=2&"
                                                                                          "ordenar=novedades&con_dis=on"))
    itemlist.append(item.clone(title="     Nuevas series", action="fichas", url=host + "/catalogo.php?tipo[]=1&ad=2&"
                                                                                       "ordenar=año&con_dis=on"))
    itemlist.append(item.clone(title="     Índices", action="indices"))

    item.contentType = "movie"
    itemlist.append(item.clone(title="Documentales", action="fichas", text_color=color2,
                               url=host + "/catalogo.php?&tipo[]=3&ad=2&ordenar=novedades&con_dis=on"))
    itemlist.append(item.clone(title="Listas", action="listas", text_color=color2,
                               url=host + "/listas.php?apikey=%s&sid=%s&start=0" % (apikey, sid), extra="listas"))
    itemlist.append(item.clone(action="search", title="Buscar...", text_color=color2))
    itemlist.append(item.clone(action="acciones_cuenta", title="Tus fichas", text_color=color4))
    itemlist.append(item.clone(title="Configuración del canal", action="configuracion", text_color="gold"))

    return itemlist


def search(item, texto):
    logger.info()
    item.url = "%s/buscar.php?apikey=%s&sid=%s&buscar=%s&modo=[fichas]&start=0" % (host, apikey, sid, texto)
    try:
        return busqueda(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def busqueda(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = json.Xml2Json(data).result

    for f in data["Data"]["Fichas"]["Ficha"]:
        title = "%s  (%s)" % (f["Title"], f["Year"])
        infolab = {'year': f["Year"]}
        thumbnail = f["Poster"]
        url = "%s/ficha.php?f=%s" % (host, f["Id"])
        action = "findvideos"
        if __menu_info__:
            action = "menu_info"
        if f["IsSerie"] == "1":
            tipo = "tvshow"
            show = f["Title"]
            if not __menu_info__:
                action = "episodios"
        else:
            tipo = "movie"
            show = ""

        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, text_color=color2,
                             contentTitle=f["Title"], show=show, contentType=tipo, infoLabels=infolab,
                             thumbnail=thumbnail))

    if __modo_grafico__:
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    total = int(data["Data"]["totalResultsFichas"])
    actualpage = int(scrapertools.find_single_match(item.url, "start=(\d+)"))
    if actualpage + 20 < total:
        next_page = item.url.replace("start=%s" % actualpage, "start=%s" % (actualpage + 20))
        itemlist.append(Item(channel=item.channel, action="busqueda", title=">> Página Siguiente",
                             url=next_page, thumbnail=item.thumbnail))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'series':
            item.channel = "playmax"
            item.extra = "newest"
            item.url = host + "/catalogo.php?tipo[]=1&ad=2&ordenar=novedades&con_dis=on"
            item.contentType = "tvshow"
            itemlist = fichas(item)

            if itemlist[-1].action == "fichas":
                itemlist.pop()
        elif categoria == 'peliculas':
            item.channel = "playmax"
            item.extra = "newest"
            item.url = host + "/catalogo.php?tipo[]=2&ad=2&ordenar=novedades&con_dis=on"
            item.contentType = "movie"
            itemlist = fichas(item)

            if itemlist[-1].action == "fichas":
                itemlist.pop()
        elif categoria == 'infantiles':
            item.channel = "playmax"
            item.extra = "newest"
            item.url = host + "/catalogo.php?tipo[]=2&genero[]=60&ad=2&ordenar=novedades&con_dis=on"
            item.contentType = "movie"
            itemlist = fichas(item)

            if itemlist[-1].action == "fichas":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def indices(item):
    logger.info()
    itemlist = []

    tipo = "2"
    if item.contentType == "tvshow":
        tipo = "1"
    if "Índices" in item.title:
        if item.contentType == "tvshow":
            itemlist.append(item.clone(title="Populares", action="fichas", url=host + "/catalogo.php?tipo[]=1&ad=2&"
                                                                                      "ordenar=pop&con_dis=on"))
        itemlist.append(item.clone(title="Más vistas", action="fichas", url=host + "/catalogo.php?tipo[]=%s&ad=2&"
                                                                                   "ordenar=siempre&con_dis=on" % tipo))
        itemlist.append(item.clone(title="Mejor valoradas", action="fichas", url=host + "/catalogo.php?tipo[]=%s&ad=2&"
                                                                                        "ordenar=valoracion&con_dis=on" % tipo))
        itemlist.append(item.clone(title="Géneros", url=host + "/catalogo.php"))
        itemlist.append(item.clone(title="Idiomas", url=host + "/catalogo.php"))
        if item.contentType == "movie":
            itemlist.append(item.clone(title="Por calidad", url=host + "/catalogo.php"))
        itemlist.append(item.clone(title="Por año"))
        itemlist.append(item.clone(title="Por país", url=host + "/catalogo.php"))

        return itemlist

    if "Géneros" in item.title:
        data = httptools.downloadpage(item.url).data
        patron = '<div class="sel gen" value="([^"]+)">([^<]+)</div>'
        matches = scrapertools.find_multiple_matches(data, patron)
        for value, genero in matches:
            url = item.url + "?tipo[]=%s&generos[]=%s&ad=2&ordenar=novedades&con_dis=on" % (tipo, value)
            itemlist.append(item.clone(action="fichas", title=genero, url=url))
    elif "Idiomas" in item.title:
        data = httptools.downloadpage(item.url).data
        bloque = scrapertools.find_single_match(data, 'oname="Idioma">Cualquier(.*?)<input')
        patron = '<div class="sel" value="([^"]+)">([^<]+)</div>'
        matches = scrapertools.find_multiple_matches(bloque, patron)
        for value, idioma in matches:
            url = item.url + "?tipo[]=%s&ad=2&ordenar=novedades&con_dis=on&e_idioma=%s" % (tipo, value)
            itemlist.append(item.clone(action="fichas", title=idioma, url=url))
    elif "calidad" in item.title:
        data = httptools.downloadpage(item.url).data
        bloque = scrapertools.find_single_match(data, 'oname="Calidad">Cualquier(.*?)<input')
        patron = '<div class="sel" value="([^"]+)">([^<]+)</div>'
        matches = scrapertools.find_multiple_matches(bloque, patron)
        for value, calidad in matches:
            url = item.url + "?tipo[]=%s&ad=2&ordenar=novedades&con_dis=on&e_calidad=%s" % (tipo, value)
            itemlist.append(item.clone(action="fichas", title=calidad, url=url))
    elif "país" in item.title:
        data = httptools.downloadpage(item.url).data
        bloque = scrapertools.find_single_match(data, 'oname="País">Todos(.*?)<input')
        patron = '<div class="sel" value="([^"]+)">([^<]+)</div>'
        matches = scrapertools.find_multiple_matches(bloque, patron)
        for value, pais in matches:
            url = item.url + "?tipo[]=%s&ad=2&ordenar=novedades&con_dis=on&pais=%s" % (tipo, value)
            itemlist.append(item.clone(action="fichas", title=pais, url=url))
    else:
        from datetime import datetime
        year = datetime.now().year
        for i in range(year, 1899, -1):
            url = "%s/catalogo.php?tipo[]=%s&del=%s&al=%s&año=personal&ad=2&ordenar=novedades&con_dis=on" \
                  % (host, tipo, i, i)
            itemlist.append(item.clone(action="fichas", title=str(i), url=url))

    return itemlist


def fichas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    fichas_marca = {'1': 'Siguiendo', '2': 'Pendiente', '3': 'Favorita', '4': 'Vista', '5': 'Abandonada'}
    patron = '<div class="c_fichas_image">.*?href="\.([^"]+)".*?src="\.([^"]+)".*?' \
             '<div class="c_fichas_data".*?marked="([^"]*)".*?serie="([^"]*)".*?' \
             '<div class="c_fichas_title">(?:<div class="c_fichas_episode">([^<]+)</div>|)([^<]+)</div>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, marca, serie, episodio, scrapedtitle in matches:
        tipo = "movie"
        scrapedurl = host + scrapedurl.rsplit("-dc=")[0]
        if not "-dc=" in scrapedurl:
            scrapedurl += "-dc="
        scrapedthumbnail = host + scrapedthumbnail
        action = "findvideos"
        if __menu_info__:
            action = "menu_info"
        if serie:
            tipo = "tvshow"
        if episodio:
            title = "%s - %s" % (episodio.replace("X", "x"), scrapedtitle)
        else:
            title = scrapedtitle

        if marca:
            title += "  [COLOR %s][%s][/COLOR]" % (color4, fichas_marca[marca])

        new_item = Item(channel=item.channel, action=action, title=title, url=scrapedurl,
                        thumbnail=scrapedthumbnail, contentTitle=scrapedtitle, contentType=tipo,
                        text_color=color2)
        if new_item.contentType == "tvshow":
            new_item.show = scrapedtitle
            if not __menu_info__:
                new_item.action = "episodios"

        itemlist.append(new_item)

    if itemlist and (item.extra == "listas_plus" or item.extra == "sigo"):
        follow = scrapertools.find_single_match(data, '<div onclick="seguir_lista.*?>(.*?)<')
        title = "Seguir Lista"
        if follow == "Siguiendo":
            title = "Dejar de seguir lista"
        item.extra = ""
        url = host + "/data.php?mode=seguir_lista&apikey=%s&sid=%s&lista=%s" % (
        apikey, sid, item.url.rsplit("/l", 1)[1])
        itemlist.insert(0, item.clone(action="acciones_cuenta", title=title, url=url, text_color=color4,
                                      lista=item.title, folder=False))

    next_page = scrapertools.find_single_match(data, 'href="([^"]+)" class="next"')
    if next_page:
        next_page = host + next_page.replace("&amp;", "&")
        itemlist.append(Item(channel=item.channel, action="fichas", title=">> Página Siguiente", url=next_page))

        try:
            total = int(scrapertools.find_single_match(data, '<span class="page-dots">.*href.*?>(\d+)'))
        except:
            total = 0
        if not config.get_setting("last_page", item.channel) and config.is_xbmc() and total > 2 \
                and item.extra != "newest":
            itemlist.append(item.clone(action="select_page", title="Ir a página... (Total:%s)" % total, url=next_page,
                                       text_color=color5))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)

    if not item.infoLabels["tmdb_id"]:
        item.infoLabels["tmdb_id"] = scrapertools.find_single_match(data,
                                                                    '<a href="https://www.themoviedb.org/[^/]+/(\d+)')
        item.infoLabels["year"] = scrapertools.find_single_match(data, 'class="e_new">(\d{4})')
    if not item.infoLabels["genre"]:
        item.infoLabels["genre"] = ", ".join(scrapertools.find_multiple_matches(data,
                                                                                '<a itemprop="genre"[^>]+>([^<]+)</a>'))
    if not item.infoLabels["plot"]:
        item.infoLabels["plot"] = scrapertools.find_single_match(data, 'itemprop="description">([^<]+)</div>')

    dc = scrapertools.find_single_match(data, "var dc_ic = '\?dc=([^']+)'")
    patron = '<div class="f_cl_l_c f_cl_l_c_id[^"]+" c_id="([^"]+)" .*?c_num="([^"]+)" c_name="([^"]+)"' \
             '.*?load_f_links\(\d+\s*,\s*(\d+).*?<div class="([^"]+)" onclick="marcar_capitulo'
    matches = scrapertools.find_multiple_matches(data, patron)
    lista_epis = []
    for c_id, episodio, title, ficha, status in matches:
        episodio = episodio.replace("X", "x")
        if episodio in lista_epis:
            continue
        lista_epis.append(episodio)
        url = "https://playmax.mx/c_enlaces_n.php?ficha=%s&c_id=%s&dc=%s" % (ficha, c_id, dc)
        title = "%s - %s" % (episodio, title)
        if "_mc a" in status:
            title = "[COLOR %s]%s[/COLOR] %s" % (color5, u"\u0474".encode('utf-8'), title)

        new_item = Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=item.thumbnail,
                        fanart=item.fanart, show=item.show, infoLabels=item.infoLabels, text_color=color2,
                        referer=item.url, contentType="episode")
        try:
            new_item.infoLabels["season"], new_item.infoLabels["episode"] = episodio.split('x', 1)
        except:
            pass
        itemlist.append(new_item)

    itemlist.sort(key=lambda it: (it.infoLabels["season"], it.infoLabels["episode"]), reverse=True)
    if __modo_grafico__:
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    library_path = config.get_videolibrary_path()
    if config.get_videolibrary_support() and not item.extra:
        title = "Añadir serie a la videoteca"
        if item.infoLabels["imdb_id"] and not library_path.lower().startswith("smb://"):
            try:
                from core import filetools
                path = filetools.join(library_path, "SERIES")
                files = filetools.walk(path)
                for dirpath, dirname, filename in files:
                    if item.infoLabels["imdb_id"] in dirpath:
                        for f in filename:
                            if f != "tvshow.nfo":
                                continue
                            from core import videolibrarytools
                            head_nfo, it = videolibrarytools.read_nfo(filetools.join(dirpath, dirname, f))
                            canales = it.library_urls.keys()
                            canales.sort()
                            if "playmax" in canales:
                                canales.pop(canales.index("playmax"))
                                canales.insert(0, "[COLOR red]playmax[/COLOR]")
                            title = "Serie ya en tu videoteca. [%s] ¿Añadir?" % ",".join(canales)
                            break
            except:
                import traceback
                logger.error(traceback.format_exc())
                pass

        itemlist.append(item.clone(action="add_serie_to_library", title=title, text_color=color5,
                                   extra="episodios###library"))
    if itemlist and not __menu_info__:
        ficha = scrapertools.find_single_match(item.url, '-f(\d+)-')
        itemlist.extend(acciones_fichas(item, sid, ficha))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.contentType == "movie":
        # Descarga la página
        data = httptools.downloadpage(item.url).data
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)

        if not item.infoLabels["tmdb_id"]:
            item.infoLabels["tmdb_id"] = scrapertools.find_single_match(data, '<a href="https://www.themoviedb.org/'
                                                                              '[^/]+/(\d+)')
            item.infoLabels["year"] = scrapertools.find_single_match(data, 'class="e_new">(\d{4})')

        if __modo_grafico__:
            tmdb.set_infoLabels_item(item, __modo_grafico__)
        if not item.infoLabels["plot"]:
            item.infoLabels["plot"] = scrapertools.find_single_match(data, 'itemprop="description">([^<]+)</div>')
        if not item.infoLabels["genre"]:
            item.infoLabels["genre"] = ", ".join(scrapertools.find_multiple_matches(data, '<a itemprop="genre"[^>]+>'
                                                                                          '([^<]+)</a>'))

        ficha = scrapertools.find_single_match(item.url, '-f(\d+)-')
        if not ficha:
            ficha = scrapertools.find_single_match(item.url, 'f=(\d+)')
        cid = "0"
    else:
        ficha, cid = scrapertools.find_single_match(item.url, 'ficha=(\d+)&c_id=(\d+)')

    url = "https://playmax.mx/c_enlaces_n.php?apikey=%s&sid=%s&ficha=%s&cid=%s" % (apikey, sid, ficha, cid)
    data = httptools.downloadpage(url).data
    data = json.Xml2Json(data).result

    for k, v in data["Data"].items():
        try:
            if type(v) is dict:
                if k == "Online":
                    order = 1
                elif k == "Download":
                    order = 0
                else:
                    order = 2

                itemlist.append(item.clone(action="", title=k, text_color=color3, order=order))
                if type(v["Item"]) is str:
                    continue
                elif type(v["Item"]) is dict:
                    v["Item"] = [v["Item"]]
                for it in v["Item"]:
                    thumbnail = "%s/styles/prosilver/imageset/%s.png" % (host, it['Host'])
                    title = "   %s - %s/%s" % (it['Host'].capitalize(), it['Quality'], it['Lang'])
                    calidad = int(scrapertools.find_single_match(it['Quality'], '(\d+)p'))
                    calidadaudio = it['QualityA'].replace("...", "")
                    subtitulos = it['Subtitles'].replace("Sin subtítulos", "")
                    if subtitulos:
                        title += " (%s)" % subtitulos
                    if calidadaudio:
                        title += "  [Audio:%s]" % calidadaudio

                    likes = 0
                    if it["Likes"] != "0" or it["Dislikes"] != "0":
                        likes = int(it["Likes"]) - int(it["Dislikes"])
                        title += "  (%s ok, %s ko)" % (it["Likes"], it["Dislikes"])
                    if type(it["Url"]) is dict:
                        for i, enlace in enumerate(it["Url"]["Item"]):
                            titulo = title + "  (Parte %s)" % (i + 1)
                            itemlist.append(item.clone(title=titulo, url=enlace, action="play", calidad=calidad,
                                                       thumbnail=thumbnail, order=order, like=likes, ficha=ficha,
                                                       cid=cid, folder=False))
                    else:
                        url = it["Url"]
                        itemlist.append(item.clone(title=title, url=url, action="play", calidad=calidad,
                                                   thumbnail=thumbnail, order=order, like=likes, ficha=ficha,
                                                   cid=cid, folder=False))
        except:
            pass

    if not config.get_setting("order_web", "playmax"):
        itemlist.sort(key=lambda it: (it.order, it.calidad, it.like), reverse=True)
    else:
        itemlist.sort(key=lambda it: it.order, reverse=True)
    if itemlist:
        itemlist.extend(acciones_fichas(item, sid, ficha))

    if not itemlist and item.contentType != "movie":
        url = url.replace("apikey=%s&" % apikey, "")
        data = httptools.downloadpage(url).data
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)

        patron = '<div id="f_fde_c"[^>]+>(.*?update_fecha\(\d+\)">)</div>'
        estrenos = scrapertools.find_multiple_matches(data, patron)
        for info in estrenos:
            info = "Estreno en " + scrapertools.htmlclean(info)
            itemlist.append(item.clone(action="", title=info))

    if not itemlist:
        itemlist.append(item.clone(action="", title="No hay enlaces disponibles"))

    return itemlist


def menu_info(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)

    item.infoLabels["tmdb_id"] = scrapertools.find_single_match(data, '<a href="https://www.themoviedb.org/[^/]+/(\d+)')
    item.infoLabels["year"] = scrapertools.find_single_match(data, 'class="e_new">(\d{4})')
    item.infoLabels["plot"] = scrapertools.find_single_match(data, 'itemprop="description">([^<]+)</div>')
    item.infoLabels["genre"] = ", ".join(scrapertools.find_multiple_matches(data,
                                                                            '<a itemprop="genre"[^>]+>([^<]+)</a>'))
    if __modo_grafico__:
        tmdb.set_infoLabels_item(item, __modo_grafico__)

    action = "findvideos"
    title = "Ver enlaces"
    if item.contentType == "tvshow":
        action = "episodios"
        title = "Ver capítulos"
    itemlist.append(item.clone(action=action, title=title))

    carpeta = "CINE"
    tipo = "película"
    action = "add_pelicula_to_library"
    extra = ""
    if item.contentType == "tvshow":
        carpeta = "SERIES"
        tipo = "serie"
        action = "add_serie_to_library"
        extra = "episodios###library"

    library_path = config.get_videolibrary_path()
    if config.get_videolibrary_support():
        title = "Añadir %s a la videoteca" % tipo
        if item.infoLabels["imdb_id"] and not library_path.lower().startswith("smb://"):
            try:
                from core import filetools
                path = filetools.join(library_path, carpeta)
                files = filetools.walk(path)
                for dirpath, dirname, filename in files:
                    if item.infoLabels["imdb_id"] in dirpath:
                        namedir = dirpath.replace(path, '')[1:]
                        for f in filename:
                            if f != namedir + ".nfo" and f != "tvshow.nfo":
                                continue
                            from core import videolibrarytools
                            head_nfo, it = videolibrarytools.read_nfo(filetools.join(dirpath, f))
                            canales = it.library_urls.keys()
                            canales.sort()
                            if "playmax" in canales:
                                canales.pop(canales.index("playmax"))
                                canales.insert(0, "[COLOR red]playmax[/COLOR]")
                            title = "%s ya en tu videoteca. [%s] ¿Añadir?" % (tipo.capitalize(), ",".join(canales))
                            break
            except:
                import traceback
                logger.error(traceback.format_exc())
                pass

        itemlist.append(item.clone(action=action, title=title, text_color=color5, extra=extra))

    token_auth = config.get_setting("token_trakt", "tvmoviedb")
    if token_auth and item.infoLabels["tmdb_id"]:
        extra = "movie"
        if item.contentType != "movie":
            extra = "tv"
        itemlist.append(item.clone(channel="tvmoviedb", title="[Trakt] Gestionar con tu cuenta", action="menu_trakt",
                                   extra=extra))
    itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                               text_color="magenta", context=""))

    itemlist.append(item.clone(action="", title=""))
    ficha = scrapertools.find_single_match(item.url, '-f(\d+)-')
    if not ficha:
        ficha = scrapertools.find_single_match(item.url, 'f=(\d+)')

    itemlist.extend(acciones_fichas(item, sid, ficha, season=True))
    itemlist.append(item.clone(action="acciones_cuenta", title="Añadir a una lista", text_color=color3, ficha=ficha))

    return itemlist


def acciones_fichas(item, sid, ficha, season=False):
    marcarlist = []
    new_item = item.clone()
    new_item.infoLabels.pop("duration", None)
    estados = [{'following': 'seguir'}, {'favorite': 'favorita'}, {'view': 'vista'}, {'slope': 'pendiente'}]
    url = "https://playmax.mx/ficha.php?apikey=%s&sid=%s&f=%s" % (apikey, sid, ficha)
    data = httptools.downloadpage(url).data
    data = json.Xml2Json(data).result

    try:
        marked = data["Data"]["User"]["Marked"]
        if new_item.contentType == "episode":
            for epi in data["Data"]["Episodes"]["Season_%s" % new_item.infoLabels["season"]]["Item"]:
                if int(epi["Episode"]) == new_item.infoLabels["episode"]:
                    epi_marked = epi["EpisodeViewed"].replace("yes", "ya")
                    epi_id = epi["Id"]
                    marcarlist.append(new_item.clone(action="marcar", title="Capítulo %s visto. ¿Cambiar?" % epi_marked,
                                                     text_color=color3, epi_id=epi_id))
                    break
    except:
        pass

    try:
        tipo = new_item.contentType.replace("movie", "Película").replace("episode", "Serie").replace("tvshow", "Serie")
        for status in estados:
            for k, v in status.items():
                if k != marked:
                    title = "Marcar %s como %s" % (tipo.lower(), v)
                    action = "marcar"
                else:
                    title = "%s marcada como %s" % (tipo, v)
                    action = ""
                if k == "following" and tipo == "Película":
                    continue
                elif k == "following" and tipo == "Serie":
                    title = title.replace("seguir", "seguida")
                    if k != marked:
                        title = "Seguir serie"
                        action = "marcar"
                    marcarlist.insert(1, new_item.clone(action=action, title=title, text_color=color4, ficha=ficha,
                                                        folder=False))
                    continue

                marcarlist.append(new_item.clone(action="marcar", title=title, text_color=color3, ficha=ficha,
                                                 folder=False))
    except:
        pass

    try:
        if season and item.contentType == "tvshow":
            seasonlist = []
            for k, v in data["Data"]["Episodes"].items():
                vistos = False
                season = k.rsplit("_", 1)[1]
                if type(v) is str:
                    continue
                elif type(v["Item"]) is not list:
                    v["Item"] = [v["Item"]]

                for epi in v["Item"]:
                    if epi["EpisodeViewed"] == "no":
                        vistos = True
                        seasonlist.append(
                            new_item.clone(action="marcar", title="Marcar temporada %s como vista" % season,
                                           text_color=color1, season=int(season), ficha=ficha, folder=False))
                        break

                if not vistos:
                    seasonlist.append(
                        new_item.clone(action="marcar", title="Temporada %s ya vista. ¿Revertir?" % season,
                                       text_color=color1, season=int(season), ficha=ficha, folder=False))

            seasonlist.sort(key=lambda it: it.season, reverse=True)
            marcarlist.extend(seasonlist)
    except:
        pass
    return marcarlist


def acciones_cuenta(item):
    logger.info()
    itemlist = []

    if "Tus fichas" in item.title:
        itemlist.append(item.clone(title="Capítulos", url="tf_block_c a", contentType="tvshow"))
        itemlist.append(item.clone(title="Series", url="tf_block_s", contentType="tvshow"))
        itemlist.append(item.clone(title="Películas", url="tf_block_p"))
        itemlist.append(item.clone(title="Documentales", url="tf_block_d"))
        return itemlist
    elif "Añadir a una lista" in item.title:
        data = httptools.downloadpage(host + "/c_listas.php?apikey=%s&sid=%s" % (apikey, sid)).data
        data = json.Xml2Json(data).result
        itemlist.append(item.clone(title="Crear nueva lista", folder=False))
        if data["Data"]["TusListas"] != "\t":
            import random
            data = data["Data"]["TusListas"]["Item"]
            if type(data) is not list:
                data = [data]
            for child in data:
                image = ""
                title = "%s (%s fichas)" % (child["Title"], child["FichasInList"])
                images = []
                for i in range(1, 5):
                    if "sinimagen.png" not in child["Poster%s" % i]:
                        images.append(child["Poster%s" % i].replace("/100/", "/400/"))
                if images:
                    image = images[random.randint(0, len(images) - 1)]
                url = host + "/data.php?mode=add_listas&apikey=%s&sid=%s&ficha_id=%s" % (apikey, sid, item.ficha)
                post = "lista_id[]=%s" % child["Id"]
                itemlist.append(item.clone(title=title, url=url, post=post, thumbnail=image, folder=False))

        return itemlist
    elif "Crear nueva lista" in item.title:
        from platformcode import platformtools
        nombre = platformtools.dialog_input("", "Introduce un nombre para la lista")
        if nombre:
            dict_priv = {0: 'Pública', 1: 'Privada'}
            priv = platformtools.dialog_select("Privacidad de la lista", ['Pública', 'Privada'])
            if priv != -1:
                url = host + "/data.php?mode=create_list&apikey=%s&sid=%s" % (apikey, sid)
                post = "name=%s&private=%s" % (nombre, priv)
                data = httptools.downloadpage(url, post)
                platformtools.dialog_notification("Lista creada correctamente",
                                                  "Nombre: %s - %s" % (nombre, dict_priv[priv]))
                platformtools.itemlist_refresh()
        return
    elif re.search(r"(?i)Seguir Lista", item.title):
        from platformcode import platformtools
        data = httptools.downloadpage(item.url)
        platformtools.dialog_notification("Operación realizada con éxito", "Lista: %s" % item.lista)
        return
    elif item.post:
        from platformcode import platformtools
        data = httptools.downloadpage(item.url, item.post).data
        platformtools.dialog_notification("Ficha añadida a la lista", "Lista: %s" % item.title)
        platformtools.itemlist_refresh()
        return

    data = httptools.downloadpage("https://playmax.mx/tusfichas.php").data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)

    bloque = scrapertools.find_single_match(data, item.url + '">(.*?)(?:<div class="tf_blocks|<div class="tf_o_move">)')
    matches = scrapertools.find_multiple_matches(bloque, '<div class="tf_menu_mini">([^<]+)<(.*?)<cb></cb></div>')
    for category, contenido in matches:
        itemlist.append(item.clone(action="", title=category, text_color=color3))

        patron = '<div class="c_fichas_image">.*?href="\.([^"]+)".*?src="\.([^"]+)".*?serie="([^"]*)".*?' \
                 '<div class="c_fichas_title">(?:<div class="c_fichas_episode">([^<]+)</div>|)([^<]+)</div>'
        entradas = scrapertools.find_multiple_matches(contenido, patron)
        for scrapedurl, scrapedthumbnail, serie, episodio, scrapedtitle in entradas:
            tipo = "movie"
            scrapedurl = host + scrapedurl
            scrapedthumbnail = host + scrapedthumbnail
            action = "findvideos"
            if __menu_info__:
                action = "menu_info"
            if serie:
                tipo = "tvshow"
            if episodio:
                title = "      %s - %s" % (episodio.replace("X", "x"), scrapedtitle)
            else:
                title = "      " + scrapedtitle

            new_item = Item(channel=item.channel, action=action, title=title, url=scrapedurl,
                            thumbnail=scrapedthumbnail, contentTitle=scrapedtitle, contentType=tipo,
                            text_color=color2)
            if new_item.contentType == "tvshow":
                new_item.show = scrapedtitle
                if not __menu_info__:
                    new_item.action = "episodios"

            itemlist.append(new_item)

    return itemlist


def marcar(item):
    logger.info()

    if "Capítulo" in item.title:
        url = "%s/data.php?mode=capitulo_visto&apikey=%s&sid=%s&c_id=%s" % (host, apikey, sid, item.epi_id)
        message = item.title.replace("no", "marcado como").replace("ya", "cambiado a no").replace(" ¿Cambiar?", "")
    elif "temporada" in item.title.lower():
        type_marcado = "1"
        if "como vista" in item.title:
            message = "Temporada %s marcada como vista" % item.season
        else:
            type_marcado = "2"
            message = "Temporada %s marcada como no vista" % item.season
        url = "%s/data.php?mode=temporada_vista&apikey=%s&sid=%s&ficha=%s&t_id=%s&type=%s" \
              % (host, apikey, sid, item.ficha, item.season, type_marcado)
    else:
        message = item.title.replace("Marcar ", "Marcada ").replace("Seguir serie", "Serie en seguimiento")
        if "favorita" in item.title:
            url = "%s/data.php?mode=marcar_ficha&apikey=%s&sid=%s&ficha=%s&tipo=%s" \
                  % (host, apikey, sid, item.ficha, "3")
        elif "pendiente" in item.title:
            url = "%s/data.php?mode=marcar_ficha&apikey=%s&sid=%s&ficha=%s&tipo=%s" \
                  % (host, apikey, sid, item.ficha, "2")
        elif "vista" in item.title:
            url = "%s/data.php?mode=marcar_ficha&apikey=%s&sid=%s&ficha=%s&tipo=%s" \
                  % (host, apikey, sid, item.ficha, "4")
        elif "Seguir" in item.title:
            url = "%s/data.php?mode=marcar_ficha&apikey=%s&sid=%s&ficha=%s&tipo=%s" \
                  % (host, apikey, sid, item.ficha, "2")
            data = httptools.downloadpage(url)
            url = "%s/data.php?mode=marcar_ficha&apikey=%s&sid=%s&ficha=%s&tipo=%s" \
                  % (host, apikey, sid, item.ficha, "1")

    data = httptools.downloadpage(url)
    if data.sucess and config.get_platform() != "plex" and item.action != "play":
        from platformcode import platformtools
        platformtools.dialog_notification("Acción correcta", message)


def listas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = json.Xml2Json(data).result
    if item.extra == "listas":
        itemlist.append(Item(channel=item.channel, title="Listas más seguidas", action="listas", text_color=color1,
                             url=item.url + "&orden=1", extra="listas_plus"))
        itemlist.append(Item(channel=item.channel, title="Listas con más fichas", action="listas", text_color=color1,
                             url=item.url + "&orden=2", extra="listas_plus"))
        itemlist.append(Item(channel=item.channel, title="Listas aleatorias", action="listas", text_color=color1,
                             url=item.url + "&orden=3", extra="listas_plus"))
        if data["Data"]["ListasSiguiendo"] != "\t":
            itemlist.append(Item(channel=item.channel, title="Listas que sigo", action="listas", text_color=color1,
                                 url=item.url, extra="sigo"))
        if data["Data"]["TusListas"] != "\t":
            itemlist.append(Item(channel=item.channel, title="Mis listas", action="listas", text_color=color1,
                                 url=item.url, extra="mislistas"))

        return itemlist

    elif item.extra == "sigo":
        data = data["Data"]["ListasSiguiendo"]["Item"]
    elif item.extra == "mislistas":
        data = data["Data"]["TusListas"]["Item"]
    else:
        data = data["Data"]["Listas"]["Item"]

    if type(data) is not list:
        data = [data]
    import random
    for child in data:
        image = ""
        title = "%s (%s fichas)" % (child["Title"], child["FichasInList"])
        images = []
        for i in range(1, 5):
            if "sinimagen.png" not in child["Poster%s" % i]:
                images.append(child["Poster%s" % i].replace("/100/", "/400/"))
        if images:
            image = images[random.randint(0, len(images) - 1)]
        url = host + "/l%s" % child["Id"]
        itemlist.append(Item(channel=item.channel, action="fichas", url=url, text_color=color3,
                             thumbnail=image, title=title, extra=item.extra))

    if len(itemlist) == 20:
        start = scrapertools.find_single_match(item.url, 'start=(\d+)')
        end = int(start) + 20
        url = re.sub(r'start=%s' % start, 'start=%s' % end, item.url)
        itemlist.append(item.clone(title=">> Página Siguiente", url=url))

    return itemlist


def play(item):
    logger.info()
    from core import servertools

    devuelve = servertools.findvideos(item.url, True)
    if devuelve:
        item.url = devuelve[0][1]
        item.server = devuelve[0][2]

    if config.get_setting("mark_play", "playmax"):
        if item.contentType == "movie":
            marcar(item.clone(title="marcar como vista"))
        else:
            marcar(item.clone(title="Capítulo", epi_id=item.cid))

    return [item]


def select_page(item):
    import xbmcgui
    dialog = xbmcgui.Dialog()
    number = dialog.numeric(0, "Introduce el número de página")
    if number != "":
        number = int(number) * 60
        item.url = re.sub(r'start=(\d+)', "start=%s" % number, item.url)

    return fichas(item)
