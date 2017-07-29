# -*- coding: utf-8 -*-

import re
import threading

from core import config
from core import filetools
from core import httptools
from core import logger
from core import scrapertools
from core.item import Item

__perfil__ = config.get_setting('perfil', "copiapop")

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00', '0xFFFE2E2E', '0xFF088A08'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E', '0xFFFE2E2E', '0xFF088A08'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE', '0xFFFE2E2E', '0xFF088A08']]

if __perfil__ - 1 >= 0:
    color1, color2, color3, color4, color5 = perfil[__perfil__ - 1]
else:
    color1 = color2 = color3 = color4 = color5 = ""

adult_content = config.get_setting("adult_content", "copiapop")


def login(pagina):
    logger.info()

    try:
        user = config.get_setting("%suser" % pagina.split(".")[0], "copiapop")
        password = config.get_setting("%spassword" % pagina.split(".")[0], "copiapop")
        if pagina == "copiapop.com":
            if user == "" and password == "":
                return False, "Para ver los enlaces de copiapop es necesario registrarse en copiapop.com"
            elif user == "" or password == "":
                return False, "Copiapop: Usuario o contraseña en blanco. Revisa tus credenciales"
        else:
            if user == "" or password == "":
                return False, "DiskoKosmiko: Usuario o contraseña en blanco. Revisa tus credenciales"

        data = httptools.downloadpage("http://%s" % pagina).data
        if re.search(r'(?i)%s' % user, data):
            return True, ""

        token = scrapertools.find_single_match(data, 'name="__RequestVerificationToken".*?value="([^"]+)"')
        post = "__RequestVerificationToken=%s&UserName=%s&Password=%s" % (token, user, password)
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        url_log = "http://%s/action/Account/Login" % pagina
        data = httptools.downloadpage(url_log, post, headers).data
        if "redirectUrl" in data:
            logger.info("Login correcto")
            return True, ""
        else:
            logger.error("Error en el login")
            return False, "Nombre de usuario no válido. Comprueba tus credenciales"
    except:
        import traceback
        logger.error(traceback.format_exc())
        return False, "Error durante el login. Comprueba tus credenciales"


def mainlist(item):
    logger.info()
    itemlist = []
    item.text_color = color1

    logueado, error_message = login("copiapop.com")

    if not logueado:
        itemlist.append(item.clone(title=error_message, action="configuracion", folder=False))
    else:
        item.extra = "http://copiapop.com"
        itemlist.append(item.clone(title="Copiapop", action="", text_color=color2))
        itemlist.append(
            item.clone(title="     Búsqueda", action="search", url="http://copiapop.com/action/SearchFiles"))
        itemlist.append(item.clone(title="     Colecciones", action="colecciones",
                                   url="http://copiapop.com/action/home/MoreNewestCollections?pageNumber=1"))
        itemlist.append(item.clone(title="     Búsqueda personalizada", action="filtro",
                                   url="http://copiapop.com/action/SearchFiles"))
        itemlist.append(item.clone(title="     Mi cuenta", action="cuenta"))

    item.extra = "http://diskokosmiko.mx/"
    itemlist.append(item.clone(title="DiskoKosmiko", action="", text_color=color2))
    itemlist.append(item.clone(title="     Búsqueda", action="search", url="http://diskokosmiko.mx/action/SearchFiles"))
    itemlist.append(item.clone(title="     Colecciones", action="colecciones",
                               url="http://diskokosmiko.mx/action/home/MoreNewestCollections?pageNumber=1"))
    itemlist.append(item.clone(title="     Búsqueda personalizada", action="filtro",
                               url="http://diskokosmiko.mx/action/SearchFiles"))
    itemlist.append(item.clone(title="     Mi cuenta", action="cuenta"))
    itemlist.append(item.clone(action="", title=""))

    folder_thumb = filetools.join(config.get_data_path(), 'thumbs_copiapop')
    files = filetools.listdir(folder_thumb)
    if files:
        itemlist.append(
            item.clone(title="Eliminar caché de imágenes (%s)" % len(files), action="delete_cache", text_color="red"))
    itemlist.append(item.clone(title="Configuración del canal", action="configuracion", text_color="gold"))

    return itemlist


def search(item, texto):
    logger.info()
    item.post = "Mode=List&Type=Video&Phrase=%s&SizeFrom=0&SizeTo=0&Extension=&ref=pager&pageNumber=1" % texto.replace(
        " ", "+")
    try:
        return listado(item)
    except:
        import sys, traceback
        for line in sys.exc_info():
            logger.error("%s" % line)
        logger.error(traceback.format_exc())
        return []


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def listado(item):
    logger.info()
    itemlist = []

    data_thumb = httptools.downloadpage(item.url, item.post.replace("Mode=List", "Mode=Gallery")).data
    if not item.post:
        data_thumb = ""
        item.url = item.url.replace("/gallery,", "/list,")

    data = httptools.downloadpage(item.url, item.post).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)

    folder = filetools.join(config.get_data_path(), 'thumbs_copiapop')
    patron = '<div class="size">(.*?)</div></div></div>'
    bloques = scrapertools.find_multiple_matches(data, patron)
    for block in bloques:
        if "adult_info" in block and not adult_content:
            continue
        size = scrapertools.find_single_match(block, '<p>([^<]+)</p>')
        scrapedurl, scrapedtitle = scrapertools.find_single_match(block,
                                                                  '<div class="name"><a href="([^"]+)".*?>([^<]+)<')
        scrapedthumbnail = scrapertools.find_single_match(block, "background-image:url\('([^']+)'")
        if scrapedthumbnail:
            try:
                thumb = scrapedthumbnail.split("-", 1)[0].replace("?", "\?")
                if data_thumb:
                    url_thumb = scrapertools.find_single_match(data_thumb, "(%s[^']+)'" % thumb)
                else:
                    url_thumb = scrapedthumbnail
                scrapedthumbnail = filetools.join(folder, "%s.jpg" % url_thumb.split("e=", 1)[1][-20:])
            except:
                scrapedthumbnail = ""

        if scrapedthumbnail:
            t = threading.Thread(target=download_thumb, args=[scrapedthumbnail, url_thumb])
            t.setDaemon(True)
            t.start()

        else:
            scrapedthumbnail = item.extra + "/img/file_types/gallery/movie.png"

        scrapedurl = item.extra + scrapedurl
        title = "%s (%s)" % (scrapedtitle, size)
        if "adult_info" in block:
            title += " [COLOR %s][+18][/COLOR]" % color4
        plot = scrapertools.find_single_match(block, '<div class="desc">(.*?)</div>')
        if plot:
            plot = scrapertools.decodeHtmlentities(plot)

        new_item = Item(channel=item.channel, action="findvideos", title=title, url=scrapedurl,
                        thumbnail=scrapedthumbnail, contentTitle=scrapedtitle, text_color=color2,
                        extra=item.extra, infoLabels={'plot': plot}, post=item.post)
        if item.post:
            try:
                new_item.folderurl, new_item.foldername = scrapertools.find_single_match(block,
                                                                                         '<p class="folder"><a href="([^"]+)".*?>([^<]+)<')
            except:
                pass
        else:
            new_item.folderurl = item.url.rsplit("/", 1)[0]
            new_item.foldername = item.foldername
            new_item.fanart = item.thumbnail

        itemlist.append(new_item)

    next_page = scrapertools.find_single_match(data, '<div class="pageSplitterBorder" data-nextpage-number="([^"]+)"')
    if next_page:
        if item.post:
            post = re.sub(r'pageNumber=(\d+)', "pageNumber=" + next_page, item.post)
            url = item.url
        else:
            url = re.sub(r',\d+\?ref=pager', ",%s?ref=pager" % next_page, item.url)
            post = ""
        itemlist.append(Item(channel=item.channel, action="listado", title=">> Página Siguiente (%s)" % next_page,
                             url=url, post=post, extra=item.extra))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(action="play", title="Reproducir/Descargar", server="copiapop"))
    usuario = scrapertools.find_single_match(item.url, '%s/([^/]+)/' % item.extra)
    url_usuario = item.extra + "/" + usuario

    if item.folderurl and not item.folderurl.startswith(item.extra):
        item.folderurl = item.extra + item.folderurl
    if item.post:
        itemlist.append(item.clone(action="listado", title="Ver colección: %s" % item.foldername,
                                   url=item.folderurl + "/gallery,1,1?ref=pager", post=""))

    data = httptools.downloadpage(item.folderurl).data
    token = scrapertools.find_single_match(data,
                                           'data-action="followChanged.*?name="__RequestVerificationToken".*?value="([^"]+)"')
    collection_id = item.folderurl.rsplit("-", 1)[1]
    post = "__RequestVerificationToken=%s&collectionId=%s" % (token, collection_id)
    url = "%s/action/Follow/Follow" % item.extra
    title = "Seguir Colección: %s" % item.foldername
    if "dejar de seguir" in data:
        title = "Dejar de seguir la colección: %s" % item.foldername
        url = "%s/action/Follow/UnFollow" % item.extra
    itemlist.append(item.clone(action="seguir", title=title, url=url, post=post, text_color=color5, folder=False))

    itemlist.append(
        item.clone(action="colecciones", title="Ver colecciones del usuario: %s" % usuario, url=url_usuario))

    return itemlist


def colecciones(item):
    logger.info()
    from core import jsontools
    itemlist = []

    usuario = False
    data = httptools.downloadpage(item.url).data
    if "Ver colecciones del usuario" not in item.title and not item.index:
        data = jsontools.load(data)["Data"]
        content = data["Content"]
        content = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", content)
    else:
        usuario = True
        if item.follow:
            content = scrapertools.find_single_match(data,
                                                     'id="followed_collections"(.*?)<div id="recommended_collections"')
        else:
            content = scrapertools.find_single_match(data,
                                                     '<div id="collections".*?<div class="collections_list(.*?)<div class="collections_list')
        content = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", content)

    patron = '<a class="name" href="([^"]+)".*?>([^<]+)<.*?src="([^"]+)".*?<p class="info">(.*?)</p>'
    matches = scrapertools.find_multiple_matches(content, patron)

    index = ""
    if item.index and item.index != "0":
        matches = matches[item.index:item.index + 20]
        if len(matches) > item.index + 20:
            index = item.index + 20
    elif len(matches) > 20:
        matches = matches[:20]
        index = 20

    folder = filetools.join(config.get_data_path(), 'thumbs_copiapop')
    for url, scrapedtitle, thumb, info in matches:
        url = item.extra + url + "/gallery,1,1?ref=pager"
        title = "%s  (%s)" % (scrapedtitle, scrapertools.htmlclean(info))
        try:
            scrapedthumbnail = filetools.join(folder, "%s.jpg" % thumb.split("e=", 1)[1][-20:])
        except:
            try:
                scrapedthumbnail = filetools.join(folder, "%s.jpg" % thumb.split("/thumbnail/", 1)[1][-20:])
                thumb = thumb.replace("/thumbnail/", "/")
            except:
                scrapedthumbnail = ""
        if scrapedthumbnail:
            t = threading.Thread(target=download_thumb, args=[scrapedthumbnail, thumb])
            t.setDaemon(True)
            t.start()
        else:
            scrapedthumbnail = thumb

        itemlist.append(Item(channel=item.channel, action="listado", title=title, url=url,
                             thumbnail=scrapedthumbnail, text_color=color2, extra=item.extra,
                             foldername=scrapedtitle))

    if not usuario and data.get("NextPageUrl"):
        url = item.extra + data["NextPageUrl"]
        itemlist.append(item.clone(title=">> Página Siguiente", url=url, text_color=""))
    elif index:
        itemlist.append(item.clone(title=">> Página Siguiente", url=item.url, index=index, text_color=""))

    return itemlist


def seguir(item):
    logger.info()
    data = httptools.downloadpage(item.url, item.post)
    message = "Colección seguida"
    if "Dejar" in item.title:
        message = "La colección ya no se sigue"
    if data.sucess and config.get_platform() != "plex":
        from platformcode import platformtools
        platformtools.dialog_notification("Acción correcta", message)


def cuenta(item):
    logger.info()
    import urllib
    itemlist = []

    web = "copiapop"
    if "diskokosmiko" in item.extra:
        web = "diskokosmiko"
        logueado, error_message = login("diskokosmiko.mx")
        if not logueado:
            itemlist.append(item.clone(title=error_message, action="configuracion", folder=False))
            return itemlist

    user = config.get_setting("%suser" % web, "copiapop")
    user = unicode(user, "utf8").lower().encode("utf8")
    url = item.extra + "/" + urllib.quote(user)
    data = httptools.downloadpage(url).data
    num_col = scrapertools.find_single_match(data, 'name="Has_collections" value="([^"]+)"')
    if num_col != "0":
        itemlist.append(item.clone(action="colecciones", url=url, index="0", title="Ver mis colecciones",
                                   text_color=color5))
    else:
        itemlist.append(item.clone(action="", title="No tienes ninguna colección", text_color=color4))

    num_follow = scrapertools.find_single_match(data, 'name="Follows_collections" value="([^"]+)"')
    if num_follow != "0":
        itemlist.append(item.clone(action="colecciones", url=url, index="0", title="Colecciones que sigo",
                                   text_color=color5, follow=True))
    else:
        itemlist.append(item.clone(action="", title="No sigues ninguna colección", text_color=color4))

    return itemlist


def filtro(item):
    logger.info()

    list_controls = []
    valores = {}

    dict_values = None
    list_controls.append({'id': 'search', 'label': 'Texto a buscar', 'enabled': True, 'color': '0xFFC52020',
                          'type': 'text', 'default': '', 'visible': True})
    list_controls.append({'id': 'tipo', 'label': 'Tipo de búsqueda', 'enabled': True, 'color': '0xFFFF8000',
                          'type': 'list', 'default': -1, 'visible': True})
    list_controls[1]['lvalues'] = ['Aplicación', 'Archivo', 'Documento', 'Imagen', 'Música', 'Vídeo', 'Todos']
    valores['tipo'] = ['Application', 'Archive', 'Document', 'Image', 'Music', 'Video', '']

    list_controls.append({'id': 'ext', 'label': 'Extensión', 'enabled': True, 'color': '0xFFF4FA58',
                          'type': 'text', 'default': '', 'visible': True})
    list_controls.append({'id': 'tmin', 'label': 'Tamaño mínimo (MB)', 'enabled': True, 'color': '0xFFCC2EFA',
                          'type': 'text', 'default': '0', 'visible': True})
    list_controls.append({'id': 'tmax', 'label': 'Tamaño máximo (MB)', 'enabled': True, 'color': '0xFF2ECCFA',
                          'type': 'text', 'default': '0', 'visible': True})

    # Se utilizan los valores por defecto/guardados
    web = "copiapop"
    if "diskokosmiko" in item.extra:
        web = "diskokosmiko"
    valores_guardados = config.get_setting("filtro_defecto_" + web, item.channel)
    if valores_guardados:
        dict_values = valores_guardados
    item.valores = valores
    from platformcode import platformtools
    return platformtools.show_channel_settings(list_controls=list_controls, dict_values=dict_values,
                                               caption="Filtra la búsqueda", item=item, callback='filtrado')


def filtrado(item, values):
    values_copy = values.copy()
    web = "copiapop"
    if "diskokosmiko" in item.extra:
        web = "diskokosmiko"
    # Guarda el filtro para que sea el que se cargue por defecto
    config.set_setting("filtro_defecto_" + web, values_copy, item.channel)

    tipo = item.valores["tipo"][values["tipo"]]
    search = values["search"]
    ext = values["ext"]
    tmin = values["tmin"]
    tmax = values["tmax"]

    if not tmin.isdigit():
        tmin = "0"
    if not tmax.isdigit():
        tmax = "0"

    item.valores = ""
    item.post = "Mode=List&Type=%s&Phrase=%s&SizeFrom=%s&SizeTo=%s&Extension=%s&ref=pager&pageNumber=1" \
                % (tipo, search, tmin, tmax, ext)
    item.action = "listado"
    return listado(item)


def download_thumb(filename, url):
    from core import downloadtools

    lock = threading.Lock()
    lock.acquire()
    folder = filetools.join(config.get_data_path(), 'thumbs_copiapop')
    if not filetools.exists(folder):
        filetools.mkdir(folder)
    lock.release()

    if not filetools.exists(filename):
        downloadtools.downloadfile(url, filename, silent=True)

    return filename


def delete_cache(url):
    folder = filetools.join(config.get_data_path(), 'thumbs_copiapop')
    filetools.rmdirtree(folder)
    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("Container.Refresh")
