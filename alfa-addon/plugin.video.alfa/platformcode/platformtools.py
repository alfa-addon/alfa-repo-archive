# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# platformtools
# ------------------------------------------------------------
# Herramientas responsables de adaptar los diferentes 
# cuadros de dialogo a una plataforma en concreto,
# en este caso Kodi.
# version 2.0
# ------------------------------------------------------------

import os
import sys
import urllib

import xbmc
import xbmcgui
import xbmcplugin
from core import config
from core import logger
from core.item import Item


def dialog_ok(heading, line1, line2="", line3=""):
    dialog = xbmcgui.Dialog()
    return dialog.ok(heading, line1, line2, line3)


def dialog_notification(heading, message, icon=0, time=5000, sound=True):
    dialog = xbmcgui.Dialog()
    try:
        l_icono = xbmcgui.NOTIFICATION_INFO, xbmcgui.NOTIFICATION_WARNING, xbmcgui.NOTIFICATION_ERROR
        dialog.notification(heading, message, l_icono[icon], time, sound)
    except:
        dialog_ok(heading, message)


def dialog_yesno(heading, line1, line2="", line3="", nolabel="No", yeslabel="Si", autoclose=""):
    dialog = xbmcgui.Dialog()
    if autoclose:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel, autoclose)
    else:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)


def dialog_select(heading, _list):
    return xbmcgui.Dialog().select(heading, _list)


def dialog_progress(heading, line1, line2=" ", line3=" "):
    dialog = xbmcgui.DialogProgress()
    dialog.create(heading, line1, line2, line3)
    return dialog


def dialog_progress_bg(heading, message=""):
    try:
        dialog = xbmcgui.DialogProgressBG()
        dialog.create(heading, message)
        return dialog
    except:
        return dialog_progress(heading, message)


def dialog_input(default="", heading="", hidden=False):
    keyboard = xbmc.Keyboard(default, heading, hidden)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    else:
        return None


def dialog_numeric(_type, heading, default=""):
    dialog = xbmcgui.Dialog()
    d = dialog.numeric(_type, heading, default)
    return d


def itemlist_refresh():
    xbmc.executebuiltin("Container.Refresh")


def itemlist_update(item):
    xbmc.executebuiltin("Container.Update(" + sys.argv[0] + "?" + item.tourl() + ")")


def render_items(itemlist, parent_item):
    """
    Función encargada de mostrar el itemlist en kodi, se pasa como parametros el itemlist y el item del que procede
    @type itemlist: list
    @param itemlist: lista de elementos a mostrar

    @type parent_item: item
    @param parent_item: elemento padre
    """
    # Si el itemlist no es un list salimos
    if not type(itemlist) == list:
        return

    # Si no hay ningun item, mostramos un aviso
    if not len(itemlist):
        itemlist.append(Item(title="No hay elementos que mostrar"))

    # Recorremos el itemlist
    for item in itemlist:
        # logger.debug(item)
        # Si el item no contiene categoria, le ponemos la del item padre
        if item.category == "":
            item.category = parent_item.category

        # Si el item no contiene fanart, le ponemos el del item padre
        if item.fanart == "":
            item.fanart = parent_item.fanart

        # Formatear titulo
        if item.text_color:
            item.title = '[COLOR %s]%s[/COLOR]' % (item.text_color, item.title)
        if item.text_bold:
            item.title = '[B]%s[/B]' % item.title
        if item.text_italic:
            item.title = '[I]%s[/I]' % item.title

        # Añade headers a las imagenes si estan en un servidor con cloudflare
        from core import httptools
        item.thumbnail = httptools.get_url_headers(item.thumbnail)
        item.fanart = httptools.get_url_headers(item.fanart)

        # IconImage para folder y video
        if item.folder:
            icon_image = "DefaultFolder.png"
        else:
            icon_image = "DefaultVideo.png"

        # Creamos el listitem
        listitem = xbmcgui.ListItem(item.title, iconImage=icon_image, thumbnailImage=item.thumbnail)

        # Ponemos el fanart
        if item.fanart:
            listitem.setProperty('fanart_image', item.fanart)
        else:
            listitem.setProperty('fanart_image', os.path.join(config.get_runtime_path(), "fanart.jpg"))

        # TODO: ¿Se puede eliminar esta linea? yo no he visto que haga ningun efecto.
        xbmcplugin.setPluginFanart(int(sys.argv[1]), os.path.join(config.get_runtime_path(), "fanart.jpg"))

        # Añadimos los infoLabels
        set_infolabels(listitem, item)

        # Montamos el menu contextual
        context_commands = set_context_commands(item, parent_item)

        # Añadimos el item
        listitem.addContextMenuItems(context_commands, replaceItems=True)

        if not item.totalItems:
            item.totalItems = 0
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='%s?%s' % (sys.argv[0], item.tourl()),
                                    listitem=listitem, isFolder=item.folder,
                                    totalItems=item.totalItems)

    # Fijar los tipos de vistas...
    if config.get_setting("forceview") == True:
        # ...forzamos segun el viewcontent
        xbmcplugin.setContent(int(sys.argv[1]), parent_item.viewcontent)
        # logger.debug(parent_item)
    elif parent_item.channel not in ["channelselector", ""]:
        # ... o segun el canal
        xbmcplugin.setContent(int(sys.argv[1]), "movies")

    # Fijamos el "breadcrumb"
    xbmcplugin.setPluginCategory(handle=int(sys.argv[1]), category=parent_item.category.capitalize())

    # No ordenar items
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_NONE)

    # Cerramos el directorio
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    # Fijar la vista
    if config.get_setting("forceview") == True:
        viewmode_id = get_viewmode_id(parent_item)
        xbmc.executebuiltin("Container.SetViewMode(%s)" % viewmode_id)


def get_viewmode_id(parent_item):
    # viewmode_json habria q guardarlo en un archivo y crear un metodo para q el user fije sus preferencias en:
    # user_files, user_movies, user_tvshows, user_season y user_episodes.
    viewmode_json = {'skin.confluence': {'default_files': 50,
                                         'default_movies': 515,
                                         'default_tvshows': 508,
                                         'default_seasons': 503,
                                         'default_episodes': 504,
                                         'view_list': 50,
                                         'view_thumbnails': 500,
                                         'view_movie_with_plot': 503},
                     'skin.estuary': {'default_files': 50,
                                      'default_movies': 54,
                                      'default_tvshows': 502,
                                      'default_seasons': 500,
                                      'default_episodes': 53,
                                      'view_list': 50,
                                      'view_thumbnails': 500,
                                      'view_movie_with_plot': 54}}

    # Si el parent_item tenia fijado un viewmode usamos esa vista...
    if parent_item.viewmode == 'movie':
        # Remplazamos el antiguo viewmode 'movie' por 'thumbnails'
        parent_item.viewmode = 'thumbnails'

    if parent_item.viewmode in ["list", "movie_with_plot", "thumbnails"]:
        view_name = "view_" + parent_item.viewmode

        '''elif isinstance(parent_item.viewmode, int):
            # only for debug
            viewName = parent_item.viewmode'''

    # ...sino ponemos la vista por defecto en funcion del viewcontent
    else:
        view_name = "default_" + parent_item.viewcontent

    skin_name = xbmc.getSkinDir()
    if skin_name not in viewmode_json:
        skin_name = 'skin.confluence'
    view_skin = viewmode_json[skin_name]
    return view_skin.get(view_name, 50)


def set_infolabels(listitem, item, player=False):
    """
    Metodo para pasar la informacion al listitem (ver tmdb.set_InfoLabels() )
    item.infoLabels es un dicionario con los pares de clave/valor descritos en:
    http://mirrors.xbmc.org/docs/python-docs/14.x-helix/xbmcgui.html#ListItem-setInfo
    @param listitem: objeto xbmcgui.ListItem
    @type listitem: xbmcgui.ListItem
    @param item: objeto Item que representa a una pelicula, serie o capitulo
    @type item: item
    """
    if item.infoLabels:
        if 'mediatype' not in item.infoLabels:
            item.infoLabels['mediatype'] = item.contentType
        listitem.setInfo("video", item.infoLabels)

    if player and not item.contentTitle:
        if item.fulltitle:
            listitem.setInfo("video", {"Title": item.fulltitle})
        else:
            listitem.setInfo("video", {"Title": item.title})

    elif not player:
        listitem.setInfo("video", {"Title": item.title})

    # Añadido para Kodi Krypton (v17)
    if config.get_platform(True)['num_version'] >= 17.0:
        listitem.setArt({"poster": item.thumbnail})


def set_context_commands(item, parent_item):
    """
    Función para generar los menus contextuales.
        1. Partiendo de los datos de item.context
             a. Metodo antiguo item.context tipo str separando las opciones por "|" (ejemplo: item.context = "1|2|3")
                (solo predefinidos)
            b. Metodo list: item.context es un list con las diferentes opciones del menu:
                - Predefinidos: Se cargara una opcion predefinida con un nombre.
                    item.context = ["1","2","3"]

                - dict(): Se cargara el item actual modificando los campos que se incluyan en el dict() en caso de
                    modificar los campos channel y action estos serán guardados en from_channel y from_action.
                    item.context = [{"title":"Nombre del menu", "action": "action del menu",
                                        "channel":"channel del menu"}, {...}]

        2. Añadiendo opciones segun criterios
            Se pueden añadir opciones al menu contextual a items que cumplan ciertas condiciones.


        3. Añadiendo opciones a todos los items
            Se pueden añadir opciones al menu contextual para todos los items

        4. Se pueden deshabilitar las opciones del menu contextual añadiendo un comando 'no_context' al item.context.
            Las opciones que Kodi, el skin u otro añadido añada al menu contextual no se pueden deshabilitar.

    @param item: elemento que contiene los menu contextuales
    @type item: item
    @param parent_item:
    @type parent_item: item
    """
    context_commands = []
    num_version_xbmc = config.get_platform(True)['num_version']

    # Creamos un list con las diferentes opciones incluidas en item.context
    if type(item.context) == str:
        context = item.context.split("|")
    elif type(item.context) == list:
        context = item.context
    else:
        context = []

    # Opciones segun item.context
    for command in context:
        # Predefinidos
        if type(command) == str:
            if command == "no_context":
                return []

        # Formato dict
        if type(command) == dict:
            # Los parametros del dict, se sobreescriben al nuevo context_item en caso de sobreescribir "action" y
            # "channel", los datos originales se guardan en "from_action" y "from_channel"
            if "action" in command:
                command["from_action"] = item.action
            if "channel" in command:
                command["from_channel"] = item.channel

            if "goto" in command:
                context_commands.append((command["title"], "XBMC.Container.Refresh (%s?%s)" %
                                         (sys.argv[0], item.clone(**command).tourl())))
            else:
                context_commands.append(
                    (command["title"], "XBMC.RunPlugin(%s?%s)" % (sys.argv[0], item.clone(**command).tourl())))

    # Opciones segun criterios, solo si el item no es un tag (etiqueta), ni es "Añadir a la videoteca", etc...
    if item.action and item.action not in ["add_pelicula_to_library", "add_serie_to_library", "buscartrailer"]:
        # Mostrar informacion: si el item tiene plot suponemos q es una serie, temporada, capitulo o pelicula
        if item.infoLabels['plot'] and (num_version_xbmc < 17.0 or item.contentType == 'season'):
            context_commands.append(("Información", "XBMC.Action(Info)"))

        # ExtendedInfo: Si esta instalado el addon y se cumplen una serie de condiciones
        if xbmc.getCondVisibility('System.HasAddon(script.extendedinfo)') \
                and config.get_setting("extended_info") == True:
            if item.contentType == "episode" and item.contentEpisodeNumber and item.contentSeason \
                    and (item.infoLabels['tmdb_id'] or item.contentSerieName):
                param = "tvshow_id =%s, tvshow=%s, season=%s, episode=%s" \
                        % (item.infoLabels['tmdb_id'], item.contentSerieName, item.contentSeason,
                           item.contentEpisodeNumber)
                context_commands.append(("ExtendedInfo",
                                         "XBMC.RunScript(script.extendedinfo,info=extendedepisodeinfo,%s)" % param))

            elif item.contentType == "season" and item.contentSeason \
                    and (item.infoLabels['tmdb_id'] or item.contentSerieName):
                param = "tvshow_id =%s,tvshow=%s, season=%s" \
                        % (item.infoLabels['tmdb_id'], item.contentSerieName, item.contentSeason)
                context_commands.append(("ExtendedInfo",
                                         "XBMC.RunScript(script.extendedinfo,info=seasoninfo,%s)" % param))

            elif item.contentType == "tvshow" and (item.infoLabels['tmdb_id'] or item.infoLabels['tvdb_id'] or
                                                       item.infoLabels['imdb_id'] or item.contentSerieName):
                param = "id =%s,tvdb_id=%s,imdb_id=%s,name=%s" \
                        % (item.infoLabels['tmdb_id'], item.infoLabels['tvdb_id'], item.infoLabels['imdb_id'],
                           item.contentSerieName)
                context_commands.append(("ExtendedInfo",
                                         "XBMC.RunScript(script.extendedinfo,info=extendedtvinfo,%s)" % param))

            elif item.contentType == "movie" and (item.infoLabels['tmdb_id'] or item.infoLabels['imdb_id'] or
                                                      item.contentTitle):
                param = "id =%s,imdb_id=%s,name=%s" \
                        % (item.infoLabels['tmdb_id'], item.infoLabels['imdb_id'], item.contentTitle)
                context_commands.append(("ExtendedInfo",
                                         "XBMC.RunScript(script.extendedinfo,info=extendedinfo,%s)" % param))

        # InfoPlus
        if config.get_setting("infoplus") == True:
            if item.infoLabels['tmdb_id'] or item.infoLabels['imdb_id'] or item.infoLabels['tvdb_id'] or \
                    (item.contentTitle and item.infoLabels["year"]) or item.contentSerieName:
                context_commands.append(("InfoPlus", "XBMC.RunPlugin(%s?%s)" % (sys.argv[0], item.clone(
                    channel="infoplus", action="start", from_channel=item.channel).tourl())))

        # Ir al Menu Principal (channel.mainlist)
        if parent_item.channel not in ["news", "channelselector"] and item.action != "mainlist" \
                and parent_item.action != "mainlist":
            context_commands.append(("Ir al Menu Principal", "XBMC.Container.Refresh (%s?%s)" %
                                     (sys.argv[0], Item(channel=item.channel, action="mainlist").tourl())))

        # Añadir a Favoritos
        if num_version_xbmc < 17.0 and \
                ((item.channel not in ["favorites", "videolibrary", "help", ""]
                  or item.action in ["update_videolibrary"]) and parent_item.channel != "favorites"):
            context_commands.append((config.get_localized_string(30155), "XBMC.RunPlugin(%s?%s)" %
                                     (sys.argv[0], item.clone(channel="favoritos", action="addFavourite",
                                                              from_channel=item.channel,
                                                              from_action=item.action).tourl())))

        if item.channel != "videolibrary":
            # Añadir Serie a la videoteca
            if item.action in ["episodios", "get_episodios"] and item.contentSerieName:
                context_commands.append(("Añadir Serie a Videoteca", "XBMC.RunPlugin(%s?%s)" %
                                         (sys.argv[0], item.clone(action="add_serie_to_library",
                                                                  from_action=item.action).tourl())))
            # Añadir Pelicula a videoteca
            elif item.action in ["detail", "findvideos"] and item.contentType == 'movie' and item.contentTitle:
                context_commands.append(("Añadir Pelicula a Videoteca", "XBMC.RunPlugin(%s?%s)" %
                                         (sys.argv[0], item.clone(action="add_pelicula_to_library",
                                                                  from_action=item.action).tourl())))

        if item.channel != "downloads":
            # Descargar pelicula
            if item.contentType == "movie" and item.contentTitle:
                context_commands.append(("Descargar Pelicula", "XBMC.RunPlugin(%s?%s)" %
                                         (sys.argv[0], item.clone(channel="downloads", action="save_download",
                                                                  from_channel=item.channel, from_action=item.action)
                                          .tourl())))

            elif item.contentSerieName:
                # Descargar serie
                if item.contentType == "tvshow":
                    context_commands.append(("Descargar Serie", "XBMC.RunPlugin(%s?%s)" %
                                             (sys.argv[0], item.clone(channel="downloads", action="save_download",
                                                                      from_channel=item.channel,
                                                                      from_action=item.action).tourl())))

                # Descargar episodio
                if item.contentType == "episode":
                    context_commands.append(("Descargar Episodio", "XBMC.RunPlugin(%s?%s)" %
                                             (sys.argv[0], item.clone(channel="downloads", action="save_download",
                                                                      from_channel=item.channel,
                                                                      from_action=item.action).tourl())))

                # Descargar temporada
                if item.contentType == "season":
                    context_commands.append(("Descargar Temporada", "XBMC.RunPlugin(%s?%s)" %
                                             (sys.argv[0], item.clone(channel="downloads", action="save_download",
                                                                      from_channel=item.channel,
                                                                      from_action=item.action).tourl())))

        # Abrir configuración
        if parent_item.channel not in ["setting", "news", "search"]:
            context_commands.append(("Abrir Configuración", "XBMC.Container.Update(%s?%s)" %
                                     (sys.argv[0], Item(channel="setting", action="mainlist").tourl())))

        # Buscar Trailer
        if item.action == "findvideos" or "buscar_trailer" in context:
            context_commands.append(("Buscar Trailer", "XBMC.RunPlugin(%s?%s)" % (sys.argv[0], item.clone(
                channel="trailertools", action="buscartrailer", contextual=True).tourl())))

    # Añadir SuperFavourites al menu contextual (1.0.53 o superior necesario)
    sf_file_path = xbmc.translatePath("special://home/addons/plugin.program.super.favourites/LaunchSFMenu.py")
    check_sf = os.path.exists(sf_file_path)
    if check_sf and xbmc.getCondVisibility('System.HasAddon("plugin.program.super.favourites")'):
        context_commands.append(("Super Favourites Menu",
                                 "XBMC.RunScript(special://home/addons/plugin.program.super.favourites/LaunchSFMenu.py)"))

    return sorted(context_commands, key=lambda comand: comand[0])


def is_playing():
    return xbmc.Player().isPlaying()


def play_video(item, strm=False):
    logger.info()
    # logger.debug(item.tostring('\n'))

    if item.channel == 'downloads':
        logger.info("Reproducir video local: %s [%s]" % (item.title, item.url))
        xlistitem = xbmcgui.ListItem(path=item.url, thumbnailImage=item.thumbnail)
        set_infolabels(xlistitem, item, True)
        xbmc.Player().play(item.url, xlistitem)
        return

    default_action = config.get_setting("default_action")
    logger.info("default_action=%s" % default_action)

    # Abre el diálogo de selección para ver las opciones disponibles
    opciones, video_urls, seleccion, salir = get_dialogo_opciones(item, default_action, strm)
    if salir:
        return

    # se obtienen la opción predeterminada de la configuración del addon
    seleccion = get_seleccion(default_action, opciones, seleccion, video_urls)
    if seleccion < 0:  # Cuadro cancelado
        return

    logger.info("seleccion=%d" % seleccion)
    logger.info("seleccion=%s" % opciones[seleccion])

    # se ejecuta la opcion disponible, jdwonloader, descarga, favoritos, añadir a la videoteca... SI NO ES PLAY
    salir = set_opcion(item, seleccion, opciones, video_urls)
    if salir:
        return

    # obtenemos el video seleccionado
    mediaurl, view, mpd = get_video_seleccionado(item, seleccion, video_urls)
    if mediaurl == "":
        return

    # se obtiene la información del video.
    if not item.contentThumbnail:
        xlistitem = xbmcgui.ListItem(path=mediaurl, thumbnailImage=item.thumbnail)
    else:
        xlistitem = xbmcgui.ListItem(path=mediaurl, thumbnailImage=item.contentThumbnail)
    set_infolabels(xlistitem, item, True)

    # si se trata de un vídeo en formato mpd, se configura el listitem para reproducirlo
    # con el addon inpustreamaddon implementado en Kodi 17
    if mpd:
        xlistitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        xlistitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')

    # se lanza el reproductor
    set_player(item, xlistitem, mediaurl, view, strm)


def stop_video():
    xbmc.Player().stop()


def get_seleccion(default_action, opciones, seleccion, video_urls):
    # preguntar
    if default_action == 0:
        # "Elige una opción"
        seleccion = dialog_select(config.get_localized_string(30163), opciones)
    # Ver en calidad baja
    elif default_action == 1:
        seleccion = 0
    # Ver en alta calidad
    elif default_action == 2:
        seleccion = len(video_urls) - 1
    else:
        seleccion = 0
    return seleccion


def show_channel_settings(**kwargs):
    """
    Muestra un cuadro de configuracion personalizado para cada canal y guarda los datos al cerrarlo.

    Los parámetros que se le pasan se puede ver en la el método al que se llama

    @return: devuelve la ventana con los elementos
    @rtype: SettingsWindow
    """
    from xbmc_config_menu import SettingsWindow
    return SettingsWindow("ChannelSettings.xml", config.get_runtime_path()).start(**kwargs)


def show_video_info(*args, **kwargs):
    """
    Muestra una ventana con la info del vídeo.

    Los parámetros que se le pasan se puede ver en la el método al que se llama

    @return: devuelve la ventana con los elementos
    @rtype: InfoWindow
    """

    from xbmc_info_window import InfoWindow
    return InfoWindow("InfoWindow.xml", config.get_runtime_path()).start(*args, **kwargs)


def show_recaptcha(key, referer):
    from recaptcha import Recaptcha
    return Recaptcha("Recaptcha.xml", config.get_runtime_path()).Start(key, referer)


def alert_no_disponible_server(server):
    # 'El vídeo ya no está en %s' , 'Prueba en otro servidor o en otro canal'
    dialog_ok(config.get_localized_string(30055), (config.get_localized_string(30057) % server),
              config.get_localized_string(30058))


def alert_unsopported_server():
    # 'Servidor no soportado o desconocido' , 'Prueba en otro servidor o en otro canal'
    dialog_ok(config.get_localized_string(30065), config.get_localized_string(30058))


def handle_wait(time_to_wait, title, text):
    logger.info("handle_wait(time_to_wait=%d)" % time_to_wait)
    espera = dialog_progress(' ' + title, "")

    secs = 0
    increment = int(100 / time_to_wait)

    cancelled = False
    while secs < time_to_wait:
        secs += 1
        percent = increment * secs
        secs_left = str((time_to_wait - secs))
        remaining_display = ' Espera ' + secs_left + ' segundos para que comience el vídeo...'
        espera.update(percent, ' ' + text, remaining_display)
        xbmc.sleep(1000)
        if espera.iscanceled():
            cancelled = True
            break

    if cancelled:
        logger.info('Espera cancelada')
        return False
    else:
        logger.info('Espera finalizada')
        return True


def get_dialogo_opciones(item, default_action, strm):
    logger.info()
    # logger.debug(item.tostring('\n'))
    from core import servertools

    opciones = []
    error = False

    try:
        item.server = item.server.lower()
    except AttributeError:
        item.server = ""

    if item.server == "":
        item.server = "directo"

    # Si no es el modo normal, no muestra el diálogo porque cuelga XBMC
    muestra_dialogo = (config.get_setting("player_mode") == 0 and not strm)

    # Extrae las URL de los vídeos, y si no puedes verlo te dice el motivo
    # Permitir varias calidades para server "directo"
    if item.video_urls:
        video_urls, puedes, motivo = item.video_urls, True, ""
    else:
        video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing(
            item.server, item.url, item.password, muestra_dialogo)

    seleccion = 0
    # Si puedes ver el vídeo, presenta las opciones
    if puedes:
        for video_url in video_urls:
            opciones.append(config.get_localized_string(30151) + " " + video_url[0])

        if item.server == "local":
            opciones.append(config.get_localized_string(30164))
        else:
            # "Descargar"
            opcion = config.get_localized_string(30153)
            opciones.append(opcion)

            if item.isFavourite:
                # "Quitar de favoritos"
                opciones.append(config.get_localized_string(30154))
            else:
                # "Añadir a favoritos"
                opciones.append(config.get_localized_string(30155))

            if not strm and item.contentType == 'movie':
                # "Añadir a videoteca"
                opciones.append(config.get_localized_string(30161))

        if default_action == "3":
            seleccion = len(opciones) - 1

        # Busqueda de trailers en youtube
        if item.channel not in ["Trailer", "ecarteleratrailers"]:
            # "Buscar Trailer"
            opciones.append(config.get_localized_string(30162))

    # Si no puedes ver el vídeo te informa
    else:
        if item.server != "":
            if "<br/>" in motivo:
                dialog_ok("No puedes ver ese vídeo porque...", motivo.split("<br/>")[0], motivo.split("<br/>")[1],
                          item.url)
            else:
                dialog_ok("No puedes ver ese vídeo porque...", motivo, item.url)
        else:
            dialog_ok("No puedes ver ese vídeo porque...", "El servidor donde está alojado no está",
                      "soportado en alfa todavía", item.url)

        if item.channel == "favoritos":
            # "Quitar de favoritos"
            opciones.append(config.get_localized_string(30154))

        if len(opciones) == 0:
            error = True

    return opciones, video_urls, seleccion, error


def set_opcion(item, seleccion, opciones, video_urls):
    logger.info()
    # logger.debug(item.tostring('\n'))
    salir = False
    # No ha elegido nada, lo más probable porque haya dado al ESC

    if seleccion == -1:
        # Para evitar el error "Uno o más elementos fallaron" al cancelar la selección desde fichero strm
        listitem = xbmcgui.ListItem(item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, listitem)

    # "Descargar"
    elif opciones[seleccion] == config.get_localized_string(30153):
        from channels import downloads
        if item.contentType == "list" or item.contentType == "tvshow":
            item.contentType = "video"
        item.play_menu = True
        downloads.save_download(item)
        salir = True

    # "Quitar de favoritos"
    elif opciones[seleccion] == config.get_localized_string(30154):
        from channels import favorites
        favorites.delFavourite(item)
        salir = True

    # "Añadir a favoritos":
    elif opciones[seleccion] == config.get_localized_string(30155):
        from channels import favorites
        item.from_channel = "favoritos"
        favorites.addFavourite(item)
        salir = True

    # "Añadir a videoteca":
    elif opciones[seleccion] == config.get_localized_string(30161):
        titulo = item.fulltitle
        if titulo == "":
            titulo = item.title

        new_item = item.clone(title=titulo, action="play_from_library", category="Cine",
                              fulltitle=item.fulltitle, channel=item.channel)

        from core import videolibrarytools
        videolibrarytools.add_movie(new_item)

        salir = True

    # "Buscar Trailer":
    elif opciones[seleccion] == config.get_localized_string(30162):
        config.set_setting("subtitulo", False)
        xbmc.executebuiltin("XBMC.RunPlugin(%s?%s)" %
                            (sys.argv[0], item.clone(channel="trailertools", action="buscartrailer",
                                                     contextual=True).tourl()))
        salir = True

    return salir


def get_video_seleccionado(item, seleccion, video_urls):
    logger.info()
    mediaurl = ""
    view = False
    wait_time = 0
    mpd = False

    # Ha elegido uno de los vídeos
    if seleccion < len(video_urls):
        mediaurl = video_urls[seleccion][1]
        if len(video_urls[seleccion]) > 4:
            wait_time = video_urls[seleccion][2]
            item.subtitle = video_urls[seleccion][3]
            mpd = True
        elif len(video_urls[seleccion]) > 3:
            wait_time = video_urls[seleccion][2]
            item.subtitle = video_urls[seleccion][3]
        elif len(video_urls[seleccion]) > 2:
            wait_time = video_urls[seleccion][2]
        view = True

    # Si no hay mediaurl es porque el vídeo no está :)
    logger.info("mediaurl=" + mediaurl)
    if mediaurl == "":
        if item.server == "unknown":
            alert_unsopported_server()
        else:
            alert_no_disponible_server(item.server)

    # Si hay un tiempo de espera (como en megaupload), lo impone ahora
    if wait_time > 0:
        continuar = handle_wait(wait_time, item.server, "Cargando vídeo...")
        if not continuar:
            mediaurl = ""

    return mediaurl, view, mpd


def set_player(item, xlistitem, mediaurl, view, strm):
    logger.info()
    logger.debug("item:\n" + item.tostring('\n'))

    # Movido del conector "torrent" aqui
    if item.server == "torrent":
        play_torrent(item, xlistitem, mediaurl)
        return

    # Si es un fichero strm no hace falta el play
    elif strm:
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xlistitem)
        if item.subtitle != "":
            xbmc.sleep(2000)
            xbmc.Player().setSubtitles(item.subtitle)

    else:
        logger.info("player_mode=%s" % config.get_setting("player_mode"))
        logger.info("mediaurl=" + mediaurl)
        if config.get_setting("player_mode") == 3 or "megacrypter.com" in mediaurl:
            import download_and_play
            download_and_play.download_and_play(mediaurl, "download_and_play.tmp", config.get_setting("downloadpath"))
            return

        elif config.get_setting("player_mode") == 0 or \
                (config.get_setting("player_mode") == 3 and mediaurl.startswith("rtmp")):
            # Añadimos el listitem a una lista de reproducción (playlist)
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()
            playlist.add(mediaurl, xlistitem)

            # Reproduce
            xbmc_player = xbmc.Player()
            xbmc_player.play(playlist, xlistitem)

        elif config.get_setting("player_mode") == 1:
            logger.info("mediaurl :" + mediaurl)
            logger.info("Tras setResolvedUrl")
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=mediaurl))

        elif config.get_setting("player_mode") == 2:
            xbmc.executebuiltin("PlayMedia(" + mediaurl + ")")

    # TODO MIRAR DE QUITAR VIEW
    if item.subtitle != "" and view:
        logger.info("Subtítulos externos: " + item.subtitle)
        xbmc.sleep(2000)
        xbmc.Player().setSubtitles(item.subtitle)

    # si es un archivo de la videoteca enviar a marcar como visto
    if strm or item.strm_path:
        from platformcode import xbmc_videolibrary
        xbmc_videolibrary.mark_auto_as_watched(item)


def torrent_client_installed(show_tuple=False):
    # Plugins externos se encuentra en servers/torrent.json nodo clients
    from core import filetools
    from core import jsontools
    torrent_clients = jsontools.get_node_from_file("torrent.json", "clients", filetools.join(config.get_runtime_path(),
                                                                                             "servers"))
    torrent_options = []
    for client in torrent_clients:
        if xbmc.getCondVisibility('System.HasAddon("%s")' % client["id"]):
            if show_tuple:
                torrent_options.append(["Plugin externo: %s" % client["name"], client["url"]])
            else:
                torrent_options.append("Plugin externo: %s" % client["name"])
    logger.debug("lista es %s" % torrent_options)
    return torrent_options


def play_torrent(item, xlistitem, mediaurl):
    logger.info()
    # Opciones disponibles para Reproducir torrents
    torrent_options = list()
    torrent_options.append(["Cliente interno (necesario libtorrent)"])
    torrent_options.append(["Cliente interno MCT (necesario libtorrent)"])

    torrent_options.extend(torrent_client_installed(show_tuple=True))
    logger.debug("lista2 es %s" % torrent_options)

    torrent_client = config.get_setting("torrent_client", server="torrent")

    if torrent_client and torrent_client - 1 <= len(torrent_options):
        if torrent_client == 0:
            seleccion = dialog_select("Abrir torrent con...", [opcion[0] for opcion in torrent_options])
        else:
            seleccion = torrent_client - 1
    else:
        if len(torrent_options) > 1:
            seleccion = dialog_select("Abrir torrent con...", [opcion[0] for opcion in torrent_options])
        else:
            seleccion = 0

    # Plugins externos
    if seleccion > 1:
        mediaurl = urllib.quote_plus(item.url)
        xbmc.executebuiltin("PlayMedia(" + torrent_options[seleccion][1] % mediaurl + ")")

    if seleccion == 1:
        from platformcode import mct
        mct.play(mediaurl, xlistitem, subtitle=item.subtitle, item=item)

    # Reproductor propio (libtorrent)
    if seleccion == 0:
        import time
        played = False
        debug = (config.get_setting("debug") == True)

        # Importamos el cliente
        from btserver import Client

        client_tmp_path = config.get_setting("downloadpath")
        if not client_tmp_path:
            client_tmp_path = config.get_data_path()

        # Iniciamos el cliente:
        c = Client(url=mediaurl, is_playing_fnc=xbmc.Player().isPlaying, wait_time=None, timeout=10,
                   temp_path=os.path.join(client_tmp_path, "alfa-torrent"), print_status=debug)

        # Mostramos el progreso
        progreso = dialog_progress("Alfa - Torrent", "Iniciando...")

        # Mientras el progreso no sea cancelado ni el cliente cerrado
        while not c.closed:
            try:
                # Obtenemos el estado del torrent
                s = c.status
                if debug:
                    # Montamos las tres lineas con la info del torrent
                    txt = '%.2f%% de %.1fMB %s | %.1f kB/s' % \
                          (s.progress_file, s.file_size, s.str_state, s._download_rate)
                    txt2 = 'S: %d(%d) P: %d(%d) | DHT:%s (%d) | Trakers: %d' % \
                           (s.num_seeds, s.num_complete, s.num_peers, s.num_incomplete, s.dht_state, s.dht_nodes,
                            s.trackers)
                    txt3 = 'Origen Peers TRK: %d DHT: %d PEX: %d LSD %d ' % \
                           (s.trk_peers, s.dht_peers, s.pex_peers, s.lsd_peers)
                else:
                    txt = '%.2f%% de %.1fMB %s | %.1f kB/s' % \
                          (s.progress_file, s.file_size, s.str_state, s._download_rate)
                    txt2 = 'S: %d(%d) P: %d(%d)' % (s.num_seeds, s.num_complete, s.num_peers, s.num_incomplete)
                    try:
                        txt3 = 'Deteniendo automaticamente en: %ss' % (int(s.timeout))
                    except:
                        txt3 = ''

                progreso.update(s.buffer, txt, txt2, txt3)
                time.sleep(0.5)

                if progreso.iscanceled():
                    progreso.close()
                    if s.buffer == 100:
                        if dialog_yesno("Alfa - Torrent", "¿Deseas iniciar la reproduccion?"):
                            played = False
                            progreso = dialog_progress("Alfa - Torrent", "")
                            progreso.update(s.buffer, txt, txt2, txt3)
                        else:
                            progreso = dialog_progress("Alfa - Torrent", "")
                            break

                    else:
                        if dialog_yesno("Alfa - Torrent", "¿Deseas cancelar el proceso?"):
                            progreso = dialog_progress("Alfa - Torrent", "")
                            break

                        else:
                            progreso = dialog_progress("Alfa - Torrent", "")
                            progreso.update(s.buffer, txt, txt2, txt3)

                # Si el buffer se ha llenado y la reproduccion no ha sido iniciada, se inicia
                if s.buffer == 100 and not played:
                    # Cerramos el progreso
                    progreso.close()

                    # Obtenemos el playlist del torrent
                    videourl = c.get_play_list()

                    # Iniciamos el reproductor
                    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                    playlist.clear()
                    playlist.add(videourl, xlistitem)
                    xbmc_player = xbmc.Player()
                    xbmc_player.play(playlist)

                    # Marcamos como reproducido para que no se vuelva a iniciar
                    played = True

                    # si es un archivo de la videoteca enviar a marcar como visto
                    if item.strm_path:
                        from platformcode import xbmc_videolibrary
                        xbmc_videolibrary.mark_auto_as_watched(item)

                    # Y esperamos a que el reproductor se cierre
                    while xbmc.Player().isPlaying():
                        time.sleep(1)

                    # Cuando este cerrado,  Volvemos a mostrar el dialogo
                    progreso = dialog_progress("Alfa - Torrent", "")
                    progreso.update(s.buffer, txt, txt2, txt3)

            except:
                import traceback
                logger.error(traceback.format_exc())
                break

        progreso.update(100, "Terminando y eliminando datos", " ", " ")

        # Detenemos el cliente
        if not c.closed:
            c.stop()

        # Y cerramos el progreso
        progreso.close()
