# -*- coding: utf-8 -*-

import os

from core import channeltools
from core import config
from core import jsontools
from core import logger
from core.item import Item
from platformcode import platformtools

__channel__ = "autoplay"

autoplay_node = {}


def context():
    '''
    Agrega la opcion Configurar AutoPlay al menu contextual

    :return:
    '''

    _context = ""

    if config.is_xbmc():
        _context = [{"title": "Configurar AutoPlay",
                     "action": "autoplay_config",
                     "channel": "autoplay"}]
    return _context


context = context()


def show_option(channel, itemlist, text_color='yellow', thumbnail=None, fanart=None):
    '''
    Agrega la opcion Configurar AutoPlay en la lista recibida

    :param channel: str
    :param itemlist: list (lista donde se desea integrar la opcion de configurar AutoPlay)
    :param text_color: str (color para el texto de la opcion Configurar Autoplay)
    :param thumbnail: str (direccion donde se encuentra el thumbnail para la opcion Configurar Autoplay)
    :return:
    '''
    logger.info()
    if thumbnail == None:
        thumbnail = 'https://s7.postimg.org/65ooga04b/Auto_Play.png'
    if fanart == None:
        fanart = 'https://s7.postimg.org/65ooga04b/Auto_Play.png'

    plot_autoplay = 'AutoPlay permite auto reproducir los enlaces directamente, basándose en la configuracion de tus ' \
                    'servidores y calidades preferidas. '
    itemlist.append(
        Item(channel=__channel__,
             title="Configurar AutoPlay",
             action="autoplay_config",
             text_color=text_color,
             thumbnail=thumbnail,
             fanart=fanart,
             plot=plot_autoplay,
             from_channel=channel
             ))
    return itemlist


def start(itemlist, item):
    '''
    Metodo principal desde donde se reproduce automaticamente los enlaces
    - En caso la opcion de personalizar activa utilizara las opciones definidas por el usuario.
    - En caso contrario intentara reproducir cualquier enlace que cuente con el idioma preferido.

    :param itemlist: list (lista de items listos para reproducir, o sea con action='play')
    :param item: item (el item principal del canal)
    :return: intenta autoreproducir, en caso de fallar devuelve el itemlist que recibio en un principio
    '''
    logger.info()
    global autoplay_node

    if not config.is_xbmc():
        platformtools.dialog_notification('AutoPlay ERROR', 'Sólo disponible para XBMC/Kodi')
        return itemlist
    else:
        if not autoplay_node:
            # Obtiene el nodo AUTOPLAY desde el json
            autoplay_node = jsontools.get_node_from_file('autoplay', 'AUTOPLAY')

        # Agrega servidores y calidades que no estaban listados a autoplay_node
        new_options = check_value(item.channel, itemlist)

        # Obtiene el nodo del canal desde autoplay_node
        channel_node = autoplay_node.get(item.channel, {})
        # Obtiene los ajustes des autoplay para este canal
        settings_node = channel_node.get('settings', {})

        if settings_node['active']:
            url_list_valid = []
            autoplay_list = []
            favorite_servers = []
            favorite_quality = []

            # Guarda el valor actual de "Accion al seleccionar vídeo:" en preferencias
            user_config_setting = config.get_setting("default_action")
            # Habilita la accion "Ver en calidad alta" (si el servidor devuelve más de una calidad p.e. gdrive)
            if user_config_setting != 2:
                config.set_setting("default_action", 2)

            # Informa que AutoPlay esta activo
            platformtools.dialog_notification('AutoPlay Activo', '', sound=False)

            # Prioridades a la hora de ordenar itemlist:
            #       0: Servidores y calidades
            #       1: Calidades y servidores
            #       2: Solo servidores
            #       3: Solo calidades
            #       4: No ordenar
            if settings_node['custom_servers'] and settings_node['custom_quality']:
                priority = settings_node['priority']  # 0: Servidores y calidades o 1: Calidades y servidores
            elif settings_node['custom_servers']:
                priority = 2  # Solo servidores
            elif settings_node['custom_quality']:
                priority = 3  # Solo calidades
            else:
                priority = 4  # No ordenar

            # Obtiene las listas servidores, calidades disponibles desde el nodo del json de AutoPlay
            server_list = channel_node.get('servers', [])
            quality_list = channel_node.get('quality', [])

            # Se guardan los textos de cada servidor y calidad en listas p.e. favorite_servers = ['openload',
            # 'streamcloud']
            for num in range(1, 4):
                favorite_servers.append(channel_node['servers'][settings_node['server_%s' % num]])
                favorite_quality.append(channel_node['quality'][settings_node['quality_%s' % num]])

            # Se filtran los enlaces de itemlist y que se correspondan con los valores de autoplay
            for item in itemlist:
                autoplay_elem = dict()

                # Comprobamos q se trata de un item de video
                if 'server' not in item:
                    continue

                # Agrega la opcion configurar AutoPlay al menu contextual
                if 'context' not in item:
                    item.context = list()
                if not filter(lambda x: x['action'] == 'autoplay_config', context):
                    item.context.append({"title": "Configurar AutoPlay",
                                         "action": "autoplay_config",
                                         "channel": "autoplay",
                                         "from_channel": item.channel})

                # Si no tiene calidad definida le asigna calidad 'default'
                if item.quality == '':
                    item.quality = 'default'

                # Se crea la lista para configuracion personalizada
                if priority < 2:  # 0: Servidores y calidades o 1: Calidades y servidores

                    # si el servidor y la calidad no se encuentran en las listas de favoritos o la url esta repetida,
                    # descartamos el item
                    if item.server not in favorite_servers or item.quality not in favorite_quality \
                            or item.url in url_list_valid:
                        continue
                    autoplay_elem["indice_server"] = favorite_servers.index(item.server)
                    autoplay_elem["indice_quality"] = favorite_quality.index(item.quality)

                elif priority == 2:  # Solo servidores

                    # si el servidor no se encuentra en la lista de favoritos o la url esta repetida,
                    # descartamos el item
                    if item.server not in favorite_servers or item.url in url_list_valid:
                        continue
                    autoplay_elem["indice_server"] = favorite_servers.index(item.server)

                elif priority == 3:  # Solo calidades

                    # si la calidad no se encuentra en la lista de favoritos o la url esta repetida,
                    # descartamos el item
                    if item.quality not in favorite_quality or item.url in url_list_valid:
                        continue
                    autoplay_elem["indice_quality"] = favorite_quality.index(item.quality)

                else:  # No ordenar

                    # si la url esta repetida, descartamos el item
                    if item.url in url_list_valid:
                        continue

                # Si el item llega hasta aqui lo añadimos al listado de urls validas y a autoplay_list
                url_list_valid.append(item.url)
                autoplay_elem['videoitem'] = item
                # autoplay_elem['server'] = item.server
                # autoplay_elem['quality'] = item.quality
                autoplay_list.append(autoplay_elem)

            # Ordenamos segun la prioridad
            if priority == 0:  # Servidores y calidades
                autoplay_list.sort(key=lambda orden: (orden['indice_server'], orden['indice_quality']))

            elif priority == 1:  # Calidades y servidores
                autoplay_list.sort(key=lambda orden: (orden['indice_quality'], orden['indice_server']))

            elif priority == 2:  # Solo servidores
                autoplay_list.sort(key=lambda orden: orden['indice_server'])

            elif priority == 3:  # Solo calidades
                autoplay_list.sort(key=lambda orden: orden['indice_quality'])

            # Si hay elementos en la lista de autoplay se intenta reproducir cada elemento, hasta encontrar uno
            # funcional o fallen todos
            if autoplay_list:
                played = False
                max_intentos = 5
                max_intentos_servers = {}

                # Si se esta reproduciendo algo detiene la reproduccion
                if platformtools.is_playing():
                    platformtools.stop_video()

                for autoplay_elem in autoplay_list:
                    if not platformtools.is_playing() and not played:
                        videoitem = autoplay_elem['videoitem']

                        if videoitem.server not in max_intentos_servers:
                            max_intentos_servers[videoitem.server] = max_intentos

                        # Si se han alcanzado el numero maximo de intentos de este servidor saltamos al siguiente
                        if max_intentos_servers[videoitem.server] == 0:
                            continue

                        lang = " "
                        if hasattr(videoitem, 'language') and videoitem.language != "":
                            lang = " '%s' " % videoitem.language

                        platformtools.dialog_notification("AutoPlay", "%s%s%s" % (
                            videoitem.server.upper(), lang, videoitem.quality.upper()), sound=False)
                        # TODO videoitem.server es el id del server, pero podria no ser el nombre!!!

                        # Intenta reproducir los enlaces
                        # Si el canal tiene metodo play propio lo utiliza
                        channel = __import__('channels.%s' % item.channel, None, None, ["channels.%s" % item.channel])
                        if hasattr(channel, 'play'):
                            resolved_item = getattr(channel, 'play')(videoitem)
                            if len(resolved_item) > 0:
                                if isinstance(resolved_item[0], list):
                                    videoitem.video_urls = resolved_item
                                else:
                                    videoitem = resolved_item[0]

                        # si no directamente reproduce
                        platformtools.play_video(videoitem)

                        try:
                            if platformtools.is_playing():
                                played = True
                                break
                        except:  # TODO evitar el informe de que el conector fallo o el video no se encuentra
                            logger.debug(str(len(autoplay_list)))

                        # Si hemos llegado hasta aqui es por q no se ha podido reproducir
                        max_intentos_servers[videoitem.server] -= 1

                        # Si se han alcanzado el numero maximo de intentos de este servidor
                        # preguntar si queremos seguir probando o lo ignoramos
                        if max_intentos_servers[videoitem.server] == 0:
                            text = "Parece que los enlaces de %s no estan funcionando." % videoitem.server.upper()
                            if not platformtools.dialog_yesno("AutoPlay", text,
                                                              "¿Desea ignorar todos los enlaces de este servidor?"):
                                max_intentos_servers[videoitem.server] = max_intentos

            else:
                platformtools.dialog_notification('AutoPlay No Fue Posible', 'No Hubo Coincidencias')
            if new_options:
                platformtools.dialog_notification("AutoPlay", "Nueva Calidad/Servidor disponible en la "
                                                              "configuracion", sound=False)

            # Restaura si es necesario el valor previo de "Accion al seleccionar vídeo:" en preferencias
            if user_config_setting != 2:
                config.set_setting("default_action", user_config_setting)

        # devuelve la lista de enlaces para la eleccion manual
        return itemlist


def init(channel, list_servers, list_quality):
    '''
    Comprueba la existencia de canal en el archivo de configuracion de Autoplay y si no existe lo añade. 
    Es necesario llamar a esta funcion al entrar a cualquier canal que incluya la funcion Autoplay.
    
    :param channel: (str) id del canal
    :param list_servers: (list) lista inicial de servidores validos para el canal. No es necesario incluirlos todos, 
        ya que la lista de servidores validos se ira actualizando dinamicamente.
    :param list_quality: (list) lista inicial de calidades validas para el canal. No es necesario incluirlas todas, 
        ya que la lista de calidades validas se ira actualizando dinamicamente.
    :return: (bool) True si la inicializacion ha sido correcta.
    '''
    logger.info()
    change = False
    result = True

    if not config.is_xbmc():
        platformtools.dialog_notification('AutoPlay ERROR', 'Sólo disponible para XBMC/Kodi')
        result = False
    else:
        autoplay_path = os.path.join(config.get_data_path(), "settings_channels", 'autoplay_data.json')
        if os.path.exists(autoplay_path):
            autoplay_node = jsontools.get_node_from_file('autoplay', "AUTOPLAY")
        else:
            change = True
            autoplay_node = {"AUTOPLAY": {}}

        if channel not in autoplay_node:
            change = True

            # Se comprueba que no haya calidades ni servidores duplicados
            list_servers = list(set(list_servers))
            list_quality = list(set(list_quality))

            # Creamos el nodo del canal y lo añadimos
            channel_node = {"servers": list_servers,
                            "quality": list_quality,
                            "settings": {
                                "active": False,
                                "custom_servers": False,
                                "custom_quality": False,
                                "priority": 0}}
            for n in range(1, 4):
                s = c = 0
                if len(list_servers) >= n:
                    s = n - 1
                if len(list_quality) >= n:
                    c = n - 1

                channel_node["settings"]["server_%s" % n] = s
                channel_node["settings"]["quality_%s" % n] = c

            autoplay_node[channel] = channel_node

        if change:
            result, json_data = jsontools.update_node(autoplay_node, 'autoplay', 'AUTOPLAY')

            if result:
                heading = "AutoPlay Disponible"
                msj = "Seleccione '<Configurar AutoPlay>' para activarlo."
                icon = 0
            else:
                heading = "Error al iniciar AutoPlay"
                msj = "Consulte su log para obtener mas información."
                icon = 1

            platformtools.dialog_notification(heading, msj, icon, sound=False)

    return result


def check_value(channel, itemlist):
    ''' comprueba la existencia de un valor en la lista de servidores o calidades
        si no existiera los agrega a la lista en el json

    :param channel: str
    :param values: list (una de servidores o calidades)
    :param value_type: str (server o quality)
    :return: list
    '''
    logger.info()
    global autoplay_node
    change = False

    if not autoplay_node:
        # Obtiene el nodo AUTOPLAY desde el json
        autoplay_node = jsontools.get_node_from_file('autoplay', 'AUTOPLAY')

    channel_node = autoplay_node.get(channel)

    server_list = channel_node.get('servers')
    if not server_list:
        server_list = channel_node['servers'] = list()

    quality_list = channel_node.get('quality')
    if not quality_list:
        quality_list = channel_node['quality'] = list()

    for item in itemlist:
        if item.server not in server_list:
            server_list.append(item.server)
            change = True
        if item.quality not in quality_list:
            quality_list.append(item.quality)
            change = True

    if change:
        change, json_data = jsontools.update_node(autoplay_node, 'autoplay', 'AUTOPLAY')

    return change


def autoplay_config(item):
    logger.info()
    global autoplay_node
    dict_values = {}
    list_controls = []
    channel_parameters = channeltools.get_channel_parameters(item.from_channel)
    channel_name = channel_parameters['title']

    if not autoplay_node:
        # Obtiene el nodo AUTOPLAY desde el json
        autoplay_node = jsontools.get_node_from_file('autoplay', 'AUTOPLAY')

    channel_node = autoplay_node.get(item.from_channel, {})
    settings_node = channel_node.get('settings', {})

    allow_option = True

    active_settings = {"id": "active", "label": "AutoPlay (activar/desactivar la auto-reproduccion)",
                       "color": "0xffffff99", "type": "bool", "default": False, "enabled": allow_option,
                       "visible": allow_option}
    list_controls.append(active_settings)
    dict_values['active'] = settings_node.get('active', False)

    # Idioma
    status_language = config.get_setting("filter_languages", item.from_channel)
    if not status_language:
        status_language = 0

    set_language = {"id": "language", "label": "Idioma para AutoPlay (Opcional)", "color": "0xffffff99",
                    "type": "list", "default": 0, "enabled": "eq(-1,true)", "visible": True,
                    "lvalues": get_languages(item.from_channel)}

    list_controls.append(set_language)
    dict_values['language'] = status_language

    separador = {"id": "label", "label": "         "
                                         "_________________________________________________________________________________________",
                 "type": "label", "enabled": True, "visible": True}
    list_controls.append(separador)

    # Seccion servidores Preferidos
    server_list = channel_node.get("servers", [])
    if not server_list:
        enabled = False
        server_list = ["No disponible"]
    else:
        enabled = "eq(-3,true)"

    custom_servers_settings = {"id": "custom_servers", "label": "      Servidores Preferidos", "color": "0xff66ffcc",
                               "type": "bool", "default": False, "enabled": enabled, "visible": True}
    list_controls.append(custom_servers_settings)
    if dict_values['active'] and enabled:
        dict_values['custom_servers'] = settings_node.get('custom_servers', False)
    else:
        dict_values['custom_servers'] = False

    for num in range(1, 4):
        pos1 = num + 3
        default = num - 1
        if default > len(server_list) - 1:
            default = 0
        set_servers = {"id": "server_%s" % num, "label": u"          \u2665 Servidor Favorito %s" % num,
                       "color": "0xfffcab14", "type": "list", "default": default,
                       "enabled": "eq(-%s,true)+eq(-%s,true)" % (pos1, num), "visible": True,
                       "lvalues": server_list}
        list_controls.append(set_servers)

        dict_values["server_%s" % num] = settings_node.get("server_%s" % num, 0)
        if settings_node.get("server_%s" % num, 0) > len(server_list) - 1:
            dict_values["server_%s" % num] = 0

    # Seccion Calidades Preferidas
    quality_list = channel_node.get("quality", [])
    if not quality_list:
        enabled = False
        quality_list = ["No disponible"]
    else:
        enabled = "eq(-7,true)"

    custom_quality_settings = {"id": "custom_quality", "label": "      Calidades Preferidas", "color": "0xff66ffcc",
                               "type": "bool", "default": False, "enabled": enabled, "visible": True}
    list_controls.append(custom_quality_settings)
    if dict_values['active'] and enabled:
        dict_values['custom_quality'] = settings_node.get('custom_quality', False)
    else:
        dict_values['custom_quality'] = False

    for num in range(1, 4):
        pos1 = num + 7
        default = num - 1
        if default > len(quality_list) - 1:
            default = 0

        set_quality = {"id": "quality_%s" % num, "label": u"          \u2665 Calidad Favorita %s" % num,
                       "color": "0xfff442d9", "type": "list", "default": default,
                       "enabled": "eq(-%s,true)+eq(-%s,true)" % (pos1, num), "visible": True,
                       "lvalues": quality_list}
        list_controls.append(set_quality)
        dict_values["quality_%s" % num] = settings_node.get("quality_%s" % num, 0)
        if settings_node.get("quality_%s" % num, 0) > len(quality_list) - 1:
            dict_values["quality_%s" % num] = 0

    # Seccion Prioridades
    priority_list = ["Servidor y Calidad", "Calidad y Servidor"]
    set_priority = {"id": "priority", "label": "   Prioridad (Indica el orden para Auto-Reproducir)",
                    "color": "0xffffff99", "type": "list", "default": 0,
                    "enabled": True, "visible": "eq(-4,true)+eq(-8,true)+eq(-11,true)", "lvalues": priority_list}
    list_controls.append(set_priority)
    dict_values["priority"] = settings_node.get("priority", 0)

    # Abrir cuadro de dialogo
    platformtools.show_channel_settings(list_controls=list_controls, dict_values=dict_values, callback='save',
                                        item=item, caption='%s - AutoPlay' % channel_name)


def save(item, dict_data_saved):
    '''
    Guarda los datos de la ventana de configuracion
    
    :param item: item
    :param dict_data_saved: dict  
    :return:
    '''
    logger.info()
    global autoplay_node

    if not autoplay_node:
        # Obtiene el nodo AUTOPLAY desde el json
        autoplay_node = jsontools.get_node_from_file('autoplay', 'AUTOPLAY')

    channel_node = autoplay_node.get(item.from_channel)
    config.set_setting("filter_languages", dict_data_saved.pop("language"), item.from_channel)
    channel_node['settings'] = dict_data_saved

    result, json_data = jsontools.update_node(autoplay_node, 'autoplay', 'AUTOPLAY')

    return result


def get_languages(channel):
    '''
    Obtiene los idiomas desde el json del canal

    :param channel: str
    :return: list
    '''
    logger.info()
    list_language = ['No filtrar']
    list_controls, dict_settings = channeltools.get_channel_controls_settings(channel)
    for control in list_controls:
        if control["id"] == 'filter_languages':
            list_language = control["lvalues"]

    return list_language


def is_active():
    '''
    Devuelve un booleano q indica si esta activo o no autoplay en el canal desde el que se llama

    :return: True si esta activo autoplay para el canal desde el que se llama, False en caso contrario.
    '''
    logger.info()
    global autoplay_node

    if not config.is_xbmc():
        return False

    if not autoplay_node:
        # Obtiene el nodo AUTOPLAY desde el json
        autoplay_node = jsontools.get_node_from_file('autoplay', 'AUTOPLAY')

        # Obtine el canal desde el q se hace la llamada
        import inspect
        module = inspect.getmodule(inspect.currentframe().f_back)
        canal = module.__name__.split('.')[1]
        logger.debug(canal)

        # Obtiene el nodo del canal desde autoplay_node
        channel_node = autoplay_node.get(canal, {})
        # Obtiene los ajustes des autoplay para este canal
        settings_node = channel_node.get('settings', {})

        return settings_node.get('active', False)
