# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Common Library Tools
# ------------------------------------------------------------

import errno
import math
import os

from core import config
from core import filetools
from core import logger
from core import scraper
from core import scrapertools
from core.item import Item
from platformcode import platformtools

FOLDER_MOVIES = config.get_setting("folder_movies")
FOLDER_TVSHOWS = config.get_setting("folder_tvshows")
VIDEOLIBRARY_PATH = config.get_videolibrary_path()
MOVIES_PATH = filetools.join(VIDEOLIBRARY_PATH, FOLDER_MOVIES)
TVSHOWS_PATH = filetools.join(VIDEOLIBRARY_PATH, FOLDER_TVSHOWS)

if not FOLDER_MOVIES or not FOLDER_TVSHOWS or not VIDEOLIBRARY_PATH \
        or not filetools.exists(MOVIES_PATH) or not filetools.exists(TVSHOWS_PATH):
    config.verify_directories_created()

addon_name = "plugin://plugin.video.%s/" % config.PLUGIN_NAME


def read_nfo(path_nfo, item=None):
    """
    Metodo para leer archivos nfo.
        Los arcivos nfo tienen la siguiente extructura: url_scraper | xml + item_json
        [url_scraper] y [xml] son opcionales, pero solo uno de ellos ha de existir siempre.
    @param path_nfo: ruta absoluta al archivo nfo
    @type path_nfo: str
    @param item: Si se pasa este parametro el item devuelto sera una copia de este con
        los valores de 'infoLabels', 'library_playcounts' y 'path' leidos del nfo
    @type: Item
    @return: Una tupla formada por la cabecera (head_nfo ='url_scraper'|'xml') y el objeto 'item_json'
    @rtype: tuple (str, Item)
    """
    head_nfo = ""
    it = None

    data = filetools.read(path_nfo)

    if data:
        head_nfo = data.splitlines()[0] + "\n"
        data = "\n".join(data.splitlines()[1:])

        it_nfo = Item().fromjson(data)

        if item:
            it = item.clone()
            it.infoLabels = it_nfo.infoLabels
            if 'library_playcounts' in it_nfo:
                it.library_playcounts = it_nfo.library_playcounts
            if it_nfo.path:
                it.path = it_nfo.path
        else:
            it = it_nfo

        if 'fanart' in it.infoLabels:
            it.fanart = it.infoLabels['fanart']

    return head_nfo, it


def save_movie(item):
    """
    guarda en la libreria de peliculas el elemento item, con los valores que contiene.
    @type item: item
    @param item: elemento que se va a guardar.
    @rtype insertados: int
    @return:  el número de elementos insertados
    @rtype sobreescritos: int
    @return:  el número de elementos sobreescritos
    @rtype fallidos: int
    @return:  el número de elementos fallidos o -1 si ha fallado todo
    """
    logger.info()
    # logger.debug(item.tostring('\n'))
    insertados = 0
    sobreescritos = 0
    fallidos = 0
    path = ""

    # Itentamos obtener el titulo correcto:
    # 1. contentTitle: Este deberia ser el sitio correcto, ya que title suele contener "Añadir a la videoteca..."
    # 2. fulltitle
    # 3. title
    if not item.contentTitle:
        # Colocamos el titulo correcto en su sitio para que scraper lo localize
        if item.fulltitle:
            item.contentTitle = item.fulltitle
        else:
            item.contentTitle = item.title

    # Si llegados a este punto no tenemos titulo, salimos
    if not item.contentTitle or not item.channel:
        logger.debug("NO ENCONTRADO contentTitle")
        return 0, 0, -1  # Salimos sin guardar

    scraper_return = scraper.find_and_set_infoLabels(item)

    # Llegados a este punto podemos tener:
    #  scraper_return = True: Un item con infoLabels con la información actualizada de la peli
    #  scraper_return = False: Un item sin información de la peli (se ha dado a cancelar en la ventana)
    #  item.infoLabels['code'] == "" : No se ha encontrado el identificador de IMDB necesario para continuar, salimos
    if not scraper_return or not item.infoLabels['code']:
        # TODO de momento si no hay resultado no añadimos nada,
        # aunq podriamos abrir un cuadro para introducir el identificador/nombre a mano
        logger.debug("NO ENCONTRADO EN SCRAPER O NO TIENE code")
        return 0, 0, -1

    _id = item.infoLabels['code'][0]

    # progress dialog
    p_dialog = platformtools.dialog_progress('alfa', 'Añadiendo película...')

    if config.get_setting("original_title_folder", "videolibrary") == 1 and item.infoLabels['originaltitle']:
        base_name = item.infoLabels['originaltitle']
    else:
        base_name = item.contentTitle

    base_name = unicode(filetools.validate_path(base_name.replace('/', '-')), "utf8").lower().encode("utf8")

    subcarpetas = os.listdir(MOVIES_PATH)

    for c in subcarpetas:
        code = scrapertools.find_single_match(c, '\[(.*?)\]')
        if code and code in item.infoLabels['code']:
            path = c
            _id = code
            break

    if not path:
        # Crear carpeta
        path = filetools.join(MOVIES_PATH, ("%s [%s]" % (base_name, _id)).strip())
        logger.info("Creando directorio pelicula:" + path)
        if not filetools.mkdir(path):
            logger.debug("No se ha podido crear el directorio")
            return 0, 0, -1

    nfo_path = filetools.join(path, "%s [%s].nfo" % (base_name, _id))
    strm_path = filetools.join(path, "%s.strm" % base_name)
    json_path = filetools.join(path, ("%s [%s].json" % (base_name, item.channel.lower())))

    nfo_exists = filetools.exists(nfo_path)
    strm_exists = filetools.exists(strm_path)
    json_exists = filetools.exists(json_path)

    if not nfo_exists:
        # Creamos .nfo si no existe
        logger.info("Creando .nfo: " + nfo_path)
        head_nfo = scraper.get_nfo(item)

        item_nfo = Item(title=item.contentTitle, channel="videolibrary", action='findvideos',
                        library_playcounts={"%s [%s]" % (base_name, _id): 0}, infoLabels=item.infoLabels,
                        library_urls={})

    else:
        # Si existe .nfo, pero estamos añadiendo un nuevo canal lo abrimos
        head_nfo, item_nfo = read_nfo(nfo_path)

    if not strm_exists:
        # Crear base_name.strm si no existe
        item_strm = Item(channel='videolibrary', action='play_from_library',
                         strm_path=strm_path.replace(MOVIES_PATH, ""), contentType='movie',
                         contentTitle=item.contentTitle)
        strm_exists = filetools.write(strm_path, '%s?%s' % (addon_name, item_strm.tourl()))
        item_nfo.strm_path = strm_path.replace(MOVIES_PATH, "")

    # Solo si existen item_nfo y .strm continuamos
    if item_nfo and strm_exists:

        if json_exists:
            logger.info("El fichero existe. Se sobreescribe")
            sobreescritos += 1
        else:
            insertados += 1

        if filetools.write(json_path, item.tojson()):
            p_dialog.update(100, 'Añadiendo película...', item.contentTitle)
            item_nfo.library_urls[item.channel] = item.url

            if filetools.write(nfo_path, head_nfo + item_nfo.tojson()):
                # actualizamos la videoteca de Kodi con la pelicula
                if config.is_xbmc():
                    from platformcode import xbmc_videolibrary
                    xbmc_videolibrary.update(FOLDER_MOVIES, filetools.basename(path) + "/")

                p_dialog.close()
                return insertados, sobreescritos, fallidos

    # Si llegamos a este punto es por q algo ha fallado
    logger.error("No se ha podido guardar %s en la videoteca" % item.contentTitle)
    p_dialog.update(100, 'Fallo al añadir...', item.contentTitle)
    p_dialog.close()
    return 0, 0, -1


def save_tvshow(item, episodelist):
    """
    guarda en la libreria de series la serie con todos los capitulos incluidos en la lista episodelist
    @type item: item
    @param item: item que representa la serie a guardar
    @type episodelist: list
    @param episodelist: listado de items que representan los episodios que se van a guardar.
    @rtype insertados: int
    @return:  el número de episodios insertados
    @rtype sobreescritos: int
    @return:  el número de episodios sobreescritos
    @rtype fallidos: int
    @return:  el número de episodios fallidos o -1 si ha fallado toda la serie
    """
    logger.info()
    # logger.debug(item.tostring('\n'))
    path = ""

    # Si llegados a este punto no tenemos titulo o code, salimos
    if not (item.contentSerieName or item.infoLabels['code']) or not item.channel:
        logger.debug("NO ENCONTRADO contentSerieName NI code")
        return 0, 0, -1  # Salimos sin guardar

    scraper_return = scraper.find_and_set_infoLabels(item)

    # Llegados a este punto podemos tener:
    #  scraper_return = True: Un item con infoLabels con la información actualizada de la serie
    #  scraper_return = False: Un item sin información de la peli (se ha dado a cancelar en la ventana)
    #  item.infoLabels['code'] == "" : No se ha encontrado el identificador de IMDB necesario para continuar, salimos
    if not scraper_return or not item.infoLabels['code']:
        # TODO de momento si no hay resultado no añadimos nada,
        # aunq podriamos abrir un cuadro para introducir el identificador/nombre a mano
        logger.debug("NO ENCONTRADO EN SCRAPER O NO TIENE code")
        return 0, 0, -1

    _id = item.infoLabels['code'][0]

    if config.get_setting("original_title_folder", "videolibrary") == 1 and item.infoLabels['originaltitle']:
        base_name = item.infoLabels['originaltitle']
    elif item.infoLabels['title']:
        base_name = item.infoLabels['title']
    else:
        base_name = item.contentSerieName

    base_name = unicode(filetools.validate_path(base_name.replace('/', '-')), "utf8").lower().encode("utf8")

    subcarpetas = os.listdir(TVSHOWS_PATH)

    for c in subcarpetas:
        code = scrapertools.find_single_match(c, '\[(.*?)\]')
        if code and code in item.infoLabels['code']:
            path = filetools.join(TVSHOWS_PATH, c)
            _id = code
            break

    if not path:
        path = filetools.join(TVSHOWS_PATH, ("%s [%s]" % (base_name, _id)).strip())
        logger.info("Creando directorio serie: " + path)
        try:
            filetools.mkdir(path)
        except OSError, exception:
            if exception.errno != errno.EEXIST:
                raise

    tvshow_path = filetools.join(path, "tvshow.nfo")
    if not filetools.exists(tvshow_path):
        # Creamos tvshow.nfo, si no existe, con la head_nfo, info de la serie y marcas de episodios vistos
        logger.info("Creando tvshow.nfo: " + tvshow_path)
        head_nfo = scraper.get_nfo(item)

        item_tvshow = Item(title=item.contentTitle, channel="videolibrary", action="get_seasons",
                           fanart=item.infoLabels['fanart'], thumbnail=item.infoLabels['thumbnail'],
                           infoLabels=item.infoLabels, path=path.replace(TVSHOWS_PATH, ""))
        item_tvshow.library_playcounts = {}
        item_tvshow.library_urls = {item.channel: item.url}

    else:
        # Si existe tvshow.nfo, pero estamos añadiendo un nuevo canal actualizamos el listado de urls
        head_nfo, item_tvshow = read_nfo(tvshow_path)
        item_tvshow.channel = "videolibrary"
        item_tvshow.action = "get_seasons"
        item_tvshow.library_urls[item.channel] = item.url

    # FILTERTOOLS
    # si el canal tiene filtro de idiomas, añadimos el canal y el show
    if episodelist and "list_language" in episodelist[0]:
        # si ya hemos añadido un canal previamente con filtro, añadimos o actualizamos el canal y show
        if "library_filter_show" in item_tvshow:
            item_tvshow.library_filter_show[item.channel] = item.show
        # no habia ningún canal con filtro y lo generamos por primera vez
        else:
            item_tvshow.library_filter_show = {item.channel: item.show}

    if item.channel != "downloads":
        item_tvshow.active = 1  # para que se actualice a diario cuando se llame a videolibrary_service

    filetools.write(tvshow_path, head_nfo + item_tvshow.tojson())

    if not episodelist:
        # La lista de episodios esta vacia
        return 0, 0, 0

    # Guardar los episodios
    '''import time
    start_time = time.time()'''
    insertados, sobreescritos, fallidos = save_episodes(path, episodelist, item)
    '''msg = "Insertados: %d | Sobreescritos: %d | Fallidos: %d | Tiempo: %2.2f segundos" % \
          (insertados, sobreescritos, fallidos, time.time() - start_time)
    logger.debug(msg)'''

    return insertados, sobreescritos, fallidos, path


def save_episodes(path, episodelist, serie, silent=False, overwrite=True):
    """
    guarda en la ruta indicada todos los capitulos incluidos en la lista episodelist
    @type path: str
    @param path: ruta donde guardar los episodios
    @type episodelist: list
    @param episodelist: listado de items que representan los episodios que se van a guardar.
    @type serie: item
    @param serie: serie de la que se van a guardar los episodios
    @type silent: bool
    @param silent: establece si se muestra la notificación
    @param overwrite: permite sobreescribir los ficheros existentes
    @type overwrite: bool
    @rtype insertados: int
    @return:  el número de episodios insertados
    @rtype sobreescritos: int
    @return:  el número de episodios sobreescritos
    @rtype fallidos: int
    @return:  el número de episodios fallidos
    """
    logger.info()

    # No hay lista de episodios, no hay nada que guardar
    if not len(episodelist):
        logger.info("No hay lista de episodios, salimos sin crear strm")
        return 0, 0, 0

    insertados = 0
    sobreescritos = 0
    fallidos = 0
    news_in_playcounts = {}

    # Listamos todos los ficheros de la serie, asi evitamos tener que comprobar si existe uno por uno
    ficheros = os.listdir(path)
    ficheros = [filetools.join(path, f) for f in ficheros]

    # Silent es para no mostrar progreso (para videolibrary_service)
    if not silent:
        # progress dialog
        p_dialog = platformtools.dialog_progress('alfa', 'Añadiendo episodios...')
        p_dialog.update(0, 'Añadiendo episodio...')

    new_episodelist = []
    # Obtenemos el numero de temporada y episodio y descartamos los q no lo sean
    for e in episodelist:
        try:
            season_episode = scrapertools.get_season_and_episode(e.title)

            e.infoLabels = serie.infoLabels
            e.contentSeason, e.contentEpisodeNumber = season_episode.split("x")
            new_episodelist.append(e)
        except:
            continue

    # No hay lista de episodios, no hay nada que guardar
    if not len(new_episodelist):
        logger.info("No hay lista de episodios, salimos sin crear strm")
        return 0, 0, 0

    # fix float porque la division se hace mal en python 2.x
    t = float(100) / len(new_episodelist)

    for i, e in enumerate(scraper.sort_episode_list(new_episodelist)):
        if not silent:
            p_dialog.update(int(math.ceil((i + 1) * t)), 'Añadiendo episodio...', e.title)

        season_episode = "%sx%s" % (e.contentSeason, str(e.contentEpisodeNumber).zfill(2))
        strm_path = filetools.join(path, "%s.strm" % season_episode)
        nfo_path = filetools.join(path, "%s.nfo" % season_episode)
        json_path = filetools.join(path, ("%s [%s].json" % (season_episode, e.channel)).lower())

        strm_exists = strm_path in ficheros
        nfo_exists = nfo_path in ficheros
        json_exists = json_path in ficheros

        if not strm_exists:
            # Si no existe season_episode.strm añadirlo
            item_strm = Item(action='play_from_library', channel='videolibrary',
                             strm_path=strm_path.replace(TVSHOWS_PATH, ""), infoLabels={})
            item_strm.contentSeason = e.contentSeason
            item_strm.contentEpisodeNumber = e.contentEpisodeNumber
            item_strm.contentType = e.contentType
            item_strm.contentTitle = season_episode

            # FILTERTOOLS
            if item_strm.list_language:
                # si tvshow.nfo tiene filtro se le pasa al item_strm que se va a generar
                if "library_filter_show" in serie:
                    item_strm.library_filter_show = serie.library_filter_show

                if item_strm.library_filter_show == "":
                    logger.error("Se ha producido un error al obtener el nombre de la serie a filtrar")

            # logger.debug("item_strm" + item_strm.tostring('\n'))
            # logger.debug("serie " + serie.tostring('\n'))
            strm_exists = filetools.write(strm_path, '%s?%s' % (addon_name, item_strm.tourl()))

        item_nfo = None
        if not nfo_exists and e.infoLabels["code"]:
            # Si no existe season_episode.nfo añadirlo
            scraper.find_and_set_infoLabels(e)
            head_nfo = scraper.get_nfo(e)

            item_nfo = e.clone(channel="videolibrary", url="", action='findvideos',
                               strm_path=strm_path.replace(TVSHOWS_PATH, ""))

            nfo_exists = filetools.write(nfo_path, head_nfo + item_nfo.tojson())

        # Solo si existen season_episode.nfo y season_episode.strm continuamos
        if nfo_exists and strm_exists:
            if not json_exists or overwrite:
                # Obtenemos infoLabel del episodio
                if not item_nfo:
                    head_nfo, item_nfo = read_nfo(nfo_path)

                e.infoLabels = item_nfo.infoLabels

                if filetools.write(json_path, e.tojson()):
                    if not json_exists:
                        logger.info("Insertado: %s" % json_path)
                        insertados += 1
                        # Marcamos episodio como no visto
                        news_in_playcounts[season_episode] = 0
                        # Marcamos la temporada como no vista
                        news_in_playcounts["season %s" % e.contentSeason] = 0
                        # Marcamos la serie como no vista
                        # logger.debug("serie " + serie.tostring('\n'))
                        news_in_playcounts[serie.contentTitle] = 0

                    else:
                        logger.info("Sobreescrito: %s" % json_path)
                        sobreescritos += 1
                else:
                    logger.info("Fallido: %s" % json_path)
                    fallidos += 1

        else:
            logger.info("Fallido: %s" % json_path)
            fallidos += 1

        if not silent and p_dialog.iscanceled():
            break

    if not silent:
        p_dialog.close()

    if news_in_playcounts:
        # Si hay nuevos episodios los marcamos como no vistos en tvshow.nfo ...
        tvshow_path = filetools.join(path, "tvshow.nfo")
        try:
            import datetime
            head_nfo, tvshow_item = read_nfo(tvshow_path)
            tvshow_item.library_playcounts.update(news_in_playcounts)

            if tvshow_item.active == 30:
                tvshow_item.active = 1
            update_last = datetime.date.today()
            tvshow_item.update_last = update_last.strftime('%Y-%m-%d')
            update_next = datetime.date.today() + datetime.timedelta(days=int(tvshow_item.active))
            tvshow_item.update_next = update_next.strftime('%Y-%m-%d')

            filetools.write(tvshow_path, head_nfo + tvshow_item.tojson())
        except:
            logger.error("Error al actualizar tvshow.nfo")
            fallidos = -1
        else:
            # ... si ha sido correcto actualizamos la videoteca de Kodi
            if config.is_xbmc() and not silent:
                from platformcode import xbmc_videolibrary
                xbmc_videolibrary.update(FOLDER_TVSHOWS, filetools.basename(path))

    if fallidos == len(episodelist):
        fallidos = -1

    logger.debug("%s [%s]: insertados= %s, sobreescritos= %s, fallidos= %s" %
                 (serie.contentSerieName, serie.channel, insertados, sobreescritos, fallidos))
    return insertados, sobreescritos, fallidos


def add_movie(item):
    """
        guarda una pelicula en la libreria de cine. La pelicula puede ser un enlace dentro de un canal o un video
        descargado previamente.

        Para añadir episodios descargados en local, el item debe tener exclusivamente:
            - contentTitle: titulo de la pelicula
            - title: titulo a mostrar junto al listado de enlaces -findvideos- ("Reproducir video local HD")
            - infoLabels["tmdb_id"] o infoLabels["imdb_id"]
            - contentType == "movie"
            - channel = "downloads"
            - url : ruta local al video

        @type item: item
        @param item: elemento que se va a guardar.
    """
    logger.info()

    new_item = item.clone(action="findvideos")
    insertados, sobreescritos, fallidos = save_movie(new_item)

    if fallidos == 0:
        platformtools.dialog_ok(config.get_localized_string(30131), new_item.contentTitle,
                                config.get_localized_string(30135))  # 'se ha añadido a la videoteca'
    else:
        platformtools.dialog_ok(config.get_localized_string(30131),
                                "ERROR, la pelicula NO se ha añadido a la videoteca")


def add_tvshow(item, channel=None):
    """
        Guarda contenido en la libreria de series. Este contenido puede ser uno de estos dos:
            - La serie con todos los capitulos incluidos en la lista episodelist.
            - Un solo capitulo descargado previamente en local.

        Para añadir episodios descargados en local, el item debe tener exclusivamente:
            - contentSerieName (o show): Titulo de la serie
            - contentTitle: titulo del episodio para extraer season_and_episode ("1x01 Piloto")
            - title: titulo a mostrar junto al listado de enlaces -findvideos- ("Reproducir video local")
            - infoLabels["tmdb_id"] o infoLabels["imdb_id"]
            - contentType != "movie"
            - channel = "downloads"
            - url : ruta local al video

        @type item: item
        @param item: item que representa la serie a guardar
        @type channel: modulo
        @param channel: canal desde el que se guardara la serie.
            Por defecto se importara item.from_channel o item.channel

    """
    logger.info("show=#" + item.show + "#")

    if item.channel == "downloads":
        itemlist = [item.clone()]

    else:
        # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
        item.action = item.extra
        if isinstance(item.extra, str) and "###" in item.extra:
            item.action = item.extra.split("###")[0]
            item.extra = item.extra.split("###")[1]

        if item.from_action:
            item.__dict__["action"] = item.__dict__.pop("from_action")
        if item.from_channel:
            item.__dict__["channel"] = item.__dict__.pop("from_channel")

        if not channel:
            try:
                channel = __import__('channels.%s' % item.channel, fromlist=["channels.%s" % item.channel])
            except ImportError:
                exec "import channels." + item.channel + " as channel"

        # Obtiene el listado de episodios
        itemlist = getattr(channel, item.action)(item)

    insertados, sobreescritos, fallidos, path = save_tvshow(item, itemlist)

    if not insertados and not sobreescritos and not fallidos:
        platformtools.dialog_ok("Videoteca", "ERROR, la serie NO se ha añadido a la videoteca",
                                "No se ha podido obtener ningun episodio")
        logger.error("La serie %s no se ha podido añadir a la videoteca. No se ha podido obtener ningun episodio"
                     % item.show)

    elif fallidos == -1:
        platformtools.dialog_ok("Videoteca", "ERROR, la serie NO se ha añadido a la videoteca")
        logger.error("La serie %s no se ha podido añadir a la videoteca" % item.show)

    elif fallidos > 0:
        platformtools.dialog_ok("Videoteca", "ERROR, la serie NO se ha añadido completa a la videoteca")
        logger.error("No se han podido añadir %s episodios de la serie %s a la videoteca" % (fallidos, item.show))

    else:
        platformtools.dialog_ok("Videoteca", "La serie se ha añadido a la videoteca")
        logger.info("Se han añadido %s episodios de la serie %s a la videoteca" %
                    (insertados, item.show))
        if config.is_xbmc():
            if config.get_setting("sync_trakt_new_tvshow", "videolibrary"):
                import xbmc
                from platformcode import xbmc_videolibrary
                if config.get_setting("sync_trakt_new_tvshow_wait", "videolibrary"):
                    # Comprobar que no se esta buscando contenido en la videoteca de Kodi
                    while xbmc.getCondVisibility('Library.IsScanningVideo()'):
                        xbmc.sleep(1000)
                # Se lanza la sincronizacion para la videoteca de Kodi
                xbmc_videolibrary.sync_trakt_kodi()
                # Se lanza la sincronización para la videoteca del addon
                xbmc_videolibrary.sync_trakt_addon(path)
