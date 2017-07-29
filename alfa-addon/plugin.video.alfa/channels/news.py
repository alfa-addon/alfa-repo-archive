# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Channel for recent videos on several channels
# ------------------------------------------------------------

import glob
import os
import re
import time
from threading import Thread

from core import channeltools
from core import config
from core import logger
from core import scrapertools
from core.item import Item
from platformcode import platformtools

THUMBNAILS = {'0': 'posters', '1': 'banners', '2': 'squares'}

__perfil__ = config.get_setting('perfil', "news")

# Fijar perfil de color
perfil = [['0xFF0B7B92', '0xFF89FDFB', '0xFFACD5D4'],
          ['0xFFB31313', '0xFFFF9000', '0xFFFFEE82'],
          ['0xFF891180', '0xFFCB22D7', '0xFFEEA1EB'],
          ['0xFFA5DEE5', '0xFFE0F9B5', '0xFFFEFDCA'],
          ['0xFFF23557', '0xFF22B2DA', '0xFFF0D43A']]

color1, color2, color3 = perfil[__perfil__]

list_newest = []
channels_id_name = {}


def mainlist(item):
    logger.info()

    itemlist = []
    list_canales = get_channels_list()

    if list_canales['peliculas']:
        thumbnail = config.get_thumb("thumb_channels_movie.png")
    new_item = Item(channel=item.channel, action="novedades", extra="peliculas", title="Películas",
                    thumbnail=thumbnail)

    new_item.context = [{"title": "Canales incluidos en: %s" % new_item.title,
                         "extra": new_item.extra,
                         "action": "setting_channel",
                         "channel": new_item.channel}]
    new_item.category = "Novedades en %s" % new_item.extra
    itemlist.append(new_item)

    if list_canales['infantiles']:
        thumbnail = config.get_thumb("thumb_channels_children.png")
    new_item = Item(channel=item.channel, action="novedades", extra="infantiles", title="Para niños",
                    thumbnail=thumbnail)
    new_item.context = [{"title": "Canales incluidos en: %s" % new_item.title,
                         "extra": new_item.extra,
                         "action": "setting_channel",
                         "channel": new_item.channel}]
    new_item.category = "Novedades en %s" % new_item.extra
    itemlist.append(new_item)

    if list_canales['series']:
        thumbnail = config.get_thumb("thumb_channels_tvshow.png")
    new_item = Item(channel=item.channel, action="novedades", extra="series", title="Episodios de series",
                    thumbnail=thumbnail)
    new_item.context = [{"title": "Canales incluidos en: %s" % new_item.title,
                         "extra": new_item.extra,
                         "action": "setting_channel",
                         "channel": new_item.channel}]
    new_item.category = "Novedades en %s" % new_item.extra
    itemlist.append(new_item)

    if list_canales['anime']:
        thumbnail = config.get_thumb("thumb_channels_anime.png")
    new_item = Item(channel=item.channel, action="novedades", extra="anime", title="Episodios de anime",
                    thumbnail=thumbnail)
    new_item.context = [{"title": "Canales incluidos en: %s" % new_item.title,
                         "extra": new_item.extra,
                         "action": "setting_channel",
                         "channel": new_item.channel}]
    new_item.category = "Novedades en %s" % new_item.extra
    itemlist.append(new_item)

    if list_canales['documentales']:
        thumbnail = config.get_thumb("thumb_channels_documentary.png")
    new_item = Item(channel=item.channel, action="novedades", extra="documentales", title="Documentales",
                    thumbnail=thumbnail)
    new_item.context = [{"title": "Canales incluidos en: %s" % new_item.title,
                         "extra": new_item.extra,
                         "action": "setting_channel",
                         "channel": new_item.channel}]
    new_item.category = "Novedades en %s" % new_item.extra
    itemlist.append(new_item)

    return itemlist


def get_channels_list():
    logger.info()

    list_canales = {'peliculas': [], 'infantiles': [], 'series': [], 'anime': [], 'documentales': []}

    # Rellenar listas de canales disponibles
    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.json')
    channel_language = config.get_setting("channel_language")

    if channel_language == "":
        channel_language = "all"

    for infile in sorted(glob.glob(channels_path)):
        channel_id = os.path.basename(infile)[:-5]
        channel_parameters = channeltools.get_channel_parameters(channel_id)

        # No incluir si es un canal inactivo
        if not channel_parameters["active"]:
            continue

        # No incluir si es un canal para adultos, y el modo adulto está desactivado
        if channel_parameters["adult"] and config.get_setting("adult_mode") == 0:
            continue

        # No incluir si el canal es en un idioma filtrado
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        # Incluir en cada categoria, si en su configuracion el canal esta activado para mostrar novedades
        for categoria in list_canales:
            include_in_newest = config.get_setting("include_in_newest_" + categoria, channel_id)
            if include_in_newest:
                channels_id_name[channel_id] = channel_parameters["title"]
                list_canales[categoria].append((channel_id, channel_parameters["title"]))

    return list_canales


def novedades(item):
    logger.info()

    global list_newest
    threads = []
    list_newest = []
    start_time = time.time()

    multithread = config.get_setting("multithread", "news")
    logger.info("multithread= " + str(multithread))

    if not multithread:
        if platformtools.dialog_yesno("Búsqueda concurrente desactivada",
                                      "La búsqueda concurrente de novedades proporciona",
                                      "una mayor velocidad y su desactivación solo es aconsejable en caso de fallo.",
                                      "¿Desea activar la búsqueda concurrente ahora?"):
            if config.set_setting("multithread", True, "news"):
                multithread = True

    progreso = platformtools.dialog_progress(item.category, "Buscando canales...")
    list_canales = get_channels_list()

    import math
    # fix float porque la division se hace mal en python 2.x
    number_of_channels = float(100) / len(list_canales[item.extra])

    for index, channel in enumerate(list_canales[item.extra]):
        channel_id, channel_title = channel
        percentage = int(math.ceil((index + 1) * number_of_channels))

        # if progreso.iscanceled():
        #     progreso.close()
        #     logger.info("Búsqueda cancelada")
        #     return itemlist

        # Modo Multi Thread
        if multithread:
            t = Thread(target=get_newest, args=[channel_id, item.extra], name=channel_title)
            t.start()
            threads.append(t)
            progreso.update(percentage, "", "Buscando en '%s'..." % channel_title)

        # Modo single Thread
        else:
            logger.info("Obteniendo novedades de channel_id=" + channel_id)
            progreso.update(percentage, "", "Buscando en '%s'..." % channel_title)
            get_newest(channel_id, item.extra)

    # Modo Multi Thread: esperar q todos los hilos terminen
    if multithread:
        pendent = [a for a in threads if a.isAlive()]
        t = float(100) / len(pendent)
        while pendent:
            index = (len(threads) - len(pendent)) + 1
            percentage = int(math.ceil(index * t))

            list_pendent_names = [a.getName() for a in pendent]
            mensaje = "Buscando en %s" % (", ".join(list_pendent_names))
            progreso.update(percentage, "Finalizado en %d/%d canales..." % (len(threads) - len(pendent), len(threads)),
                            mensaje)
            logger.debug(mensaje)

            if progreso.iscanceled():
                logger.info("Busqueda de novedades cancelada")
                break

            time.sleep(0.5)
            pendent = [a for a in threads if a.isAlive()]

    mensaje = "Resultados obtenidos: %s | Tiempo: %2.f segundos" % (len(list_newest), time.time()-start_time)
    progreso.update(100, mensaje, " ", " ")
    logger.info(mensaje)
    start_time = time.time()
    # logger.debug(start_time)

    result_mode = config.get_setting("result_mode", "news")
    if result_mode == 0:  # Agrupados por contenido
        ret = group_by_content(list_newest)
    elif result_mode == 1:  # Agrupados por canales
        ret = group_by_channel(list_newest)
    else:  # Sin agrupar
        ret = no_group(list_newest)

    while time.time() - start_time < 2:
        # mostrar cuadro de progreso con el tiempo empleado durante almenos 2 segundos
        time.sleep(0.5)

    progreso.close()
    return ret


def get_newest(channel_id, categoria):
    logger.info("channel_id=" + channel_id + ", categoria=" + categoria)

    global list_newest

    # Solicitamos las novedades de la categoria (item.extra) buscada en el canal channel
    # Si no existen novedades para esa categoria en el canal devuelve una lista vacia
    try:

        puede = True
        try:
            modulo = __import__('channels.%s' % channel_id, fromlist=["channels.%s" % channel_id])
        except:
            try:
                exec "import channels." + channel_id + " as modulo"
            except:
                puede = False

        if not puede:
            return

        logger.info("running channel " + modulo.__name__ + " " + modulo.__file__)
        list_result = modulo.newest(categoria)
        logger.info("canal= %s %d resultados" % (channel_id, len(list_result)))

        for item in list_result:
            # logger.info("item="+item.tostring())
            item.channel = channel_id
            list_newest.append(item)

    except:
        logger.error("No se pueden recuperar novedades de: " + channel_id)
        import traceback
        logger.error(traceback.format_exc())


def get_title(item):
    if item.contentSerieName:  # Si es una serie
        title = item.contentSerieName
        if not scrapertools.get_season_and_episode(title) and item.contentEpisodeNumber:
            if not item.contentSeason:
                item.contentSeason = '1'
            title = "%s - %sx%s" % (title, item.contentSeason, str(item.contentEpisodeNumber).zfill(2))

    elif item.contentTitle:  # Si es una pelicula con el canal adaptado
        title = item.contentTitle
    elif item.fulltitle:  # Si el canal no esta adaptado
        title = item.fulltitle
    else:  # Como ultimo recurso
        title = item.title

    # Limpiamos el titulo de etiquetas de formato anteriores
    title = re.compile("\[/*COLO.*?\]", re.DOTALL).sub("", title)
    title = re.compile("\[/*B\]", re.DOTALL).sub("", title)
    title = re.compile("\[/*I\]", re.DOTALL).sub("", title)

    return title


def no_group(list_result_canal):
    itemlist = []
    global channels_id_name

    for i in list_result_canal:
        i.title = get_title(i) + " [" + channels_id_name[i.channel] + "]"
        i.text_color = color3

        itemlist.append(i.clone())

    return sorted(itemlist, key=lambda it: it.title.lower())


def group_by_channel(list_result_canal):
    global channels_id_name
    dict_canales = {}
    itemlist = []

    for i in list_result_canal:
        if i.channel not in dict_canales:
            dict_canales[i.channel] = []
        # Formatear titulo
        i.title = get_title(i)
        # Añadimos el contenido al listado de cada canal
        dict_canales[i.channel].append(i)

    # Añadimos el contenido encontrado en la lista list_result
    for c in sorted(dict_canales):
        itemlist.append(Item(channel="news", title=channels_id_name[c] + ':', text_color=color1, text_bold=True))

        for i in dict_canales[c]:
            if i.contentQuality:
                i.title += ' (%s)' % i.contentQuality
            if i.language:
                i.title += ' [%s]' % i.language
            i.title = '    %s' % i.title
            i.text_color = color3
            itemlist.append(i.clone())

    return itemlist


def group_by_content(list_result_canal):
    global channels_id_name
    dict_contenidos = {}
    list_result = []

    for i in list_result_canal:
        # Formatear titulo
        i.title = get_title(i)

        # Eliminar tildes y otros caracteres especiales para la key
        import unicodedata
        try:
            new_key = i.title.lower().strip().decode("UTF-8")
            new_key = ''.join((c for c in unicodedata.normalize('NFD', new_key) if unicodedata.category(c) != 'Mn'))

        except:
            new_key = i.title

        if new_key in dict_contenidos:
            # Si el contenido ya estaba en el diccionario añadirlo a la lista de opciones...
            dict_contenidos[new_key].append(i)
        else:  # ...sino añadirlo al diccionario
            dict_contenidos[new_key] = [i]

    # Añadimos el contenido encontrado en la lista list_result
    for v in dict_contenidos.values():
        title = v[0].title
        if len(v) > 1:
            # Eliminar de la lista de nombres de canales los q esten duplicados
            canales_no_duplicados = []
            for i in v:
                if i.channel not in canales_no_duplicados:
                    canales_no_duplicados.append(channels_id_name[i.channel])

            if len(canales_no_duplicados) > 1:
                canales = ', '.join([i for i in canales_no_duplicados[:-1]])
                title += " (En %s y %s)" % (canales, canales_no_duplicados[-1])
            else:
                title += " (En %s)" % (', '.join([i for i in canales_no_duplicados]))

            new_item = v[0].clone(channel="news", title=title, action="show_channels",
                                  sub_list=[i.tourl() for i in v], extra=channels_id_name)
        else:
            new_item = v[0].clone(title=title)

        new_item.text_color = color3
        list_result.append(new_item)

    return sorted(list_result, key=lambda it: it.title.lower())


def show_channels(item):
    logger.info()
    global channels_id_name
    channels_id_name = item.extra
    itemlist = []

    for i in item.sub_list:
        new_item = Item()
        new_item = new_item.fromurl(i)
        # logger.debug(new_item.tostring())
        if new_item.contentQuality:
            new_item.title += ' (%s)' % new_item.contentQuality
        if new_item.language:
            new_item.title += ' [%s]' % new_item.language
        new_item.title += ' (%s)' % channels_id_name[new_item.channel]
        new_item.text_color = color1

        itemlist.append(new_item.clone())

    return itemlist


def menu_opciones(item):
    itemlist = list()
    itemlist.append(Item(channel=item.channel, title="Canales incluidos en:",
                         thumbnail=config.get_thumb("thumb_setting_0.png"),
                         folder=False))
    itemlist.append(Item(channel=item.channel, action="setting_channel", extra="peliculas", title="    - Películas ",
                         thumbnail=config.get_thumb("thumb_channels_movie.png"),
                         folder=False))
    itemlist.append(Item(channel=item.channel, action="setting_channel", extra="infantiles", title="    - Para niños",
                         thumbnail=config.get_thumb("thumb_channels_children.png"),
                         folder=False))
    itemlist.append(Item(channel=item.channel, action="setting_channel", extra="series",
                         title="    - Episodios de series",
                         thumbnail=config.get_thumb("thumb_channels_tvshow.png"),
                         folder=False))
    itemlist.append(Item(channel=item.channel, action="setting_channel", extra="anime",
                         title="    - Episodios de anime",
                         thumbnail=config.get_thumb("thumb_channels_anime.png"),
                         folder=False))
    itemlist.append(Item(channel=item.channel, action="setting_channel", extra="documentales",
                         title="    - Documentales",
                         thumbnail=config.get_thumb("thumb_channels_documentary.png"),
                         folder=False))
    itemlist.append(Item(channel=item.channel, action="settings", title="Otros ajustes",
                         thumbnail=config.get_thumb("thumb_setting_0.png"),
                         folder=False))
    return itemlist


def settings(item):
    return platformtools.show_channel_settings(caption="configuración -- Novedades")


def setting_channel(item):
    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.json')
    channel_language = config.get_setting("channel_language")

    if channel_language == "":
        channel_language = "all"

    list_controls = []
    for infile in sorted(glob.glob(channels_path)):
        channel_id = os.path.basename(infile)[:-5]
        channel_parameters = channeltools.get_channel_parameters(channel_id)

        # No incluir si es un canal inactivo
        if not channel_parameters["active"]:
            continue

        # No incluir si es un canal para adultos, y el modo adulto está desactivado
        if channel_parameters["adult"] and config.get_setting("adult_mode") == 0:
            continue

        # No incluir si el canal es en un idioma filtrado
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        # No incluir si en su configuracion el canal no existe 'include_in_newest'
        include_in_newest = config.get_setting("include_in_newest_" + item.extra, channel_id)
        if include_in_newest is None:
            continue

        control = {'id': channel_id,
                   'type': "bool",
                   'label': channel_parameters["title"],
                   'default': include_in_newest,
                   'enabled': True,
                   'visible': True}

        list_controls.append(control)

    caption = "Canales incluidos en Novedades " + item.title.replace("Canales incluidos en: ", "- ").strip()
    return platformtools.show_channel_settings(list_controls=list_controls, callback="save_settings", item=item,
                                               caption=caption, custom_button={"visible": False})


def save_settings(item, dict_values):
    for v in dict_values:
        config.set_setting("include_in_newest_" + item.extra, dict_values[v], v)
