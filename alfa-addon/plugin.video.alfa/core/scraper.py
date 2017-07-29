# -*- coding: utf-8 -*-

from core import config
from core import logger
from core.item import InfoLabels
from platformcode import platformtools

# Este modulo es una interface para poder implementar diferentes scrapers
# contendra todos las funciones comunes

dict_default = None
scraper = None


def find_and_set_infoLabels(item):
    """
        función que se llama para buscar y setear los infolabels
        :param item:
        :return: boleano que indica si se ha podido encontrar el 'code'
    """
    global scraper
    scraper = None
    # logger.debug("item:\n" + item.tostring('\n'))

    list_opciones_cuadro = ["Introducir otro nombre", "Completar información"]
    # Si se añaden más scrapers hay q declararlos aqui-> "modulo_scraper": "Texto_en_cuadro"
    scrapers_disponibles = {'tmdb': "Buscar en TheMovieDB.org",
                            'tvdb': "Buscar en TheTvDB.com"}

    # Obtener el Scraper por defecto de la configuracion segun el tipo de contenido
    if item.contentType == "movie":
        scraper_actual = ['tmdb'][config.get_setting("scraper_movies", "videolibrary")]
        tipo_contenido = "película"
        title = item.contentTitle
        # Completar lista de opciones para este tipo de contenido
        list_opciones_cuadro.append(scrapers_disponibles['tmdb'])

    else:
        scraper_actual = ['tmdb', 'tvdb'][config.get_setting("scraper_tvshows", "videolibrary")]
        tipo_contenido = "serie"
        title = item.contentSerieName
        # Completar lista de opciones para este tipo de contenido
        list_opciones_cuadro.append(scrapers_disponibles['tmdb'])
        list_opciones_cuadro.append(scrapers_disponibles['tvdb'])

    # Importamos el scraper
    try:
        scraper = __import__('core.%s' % scraper_actual, fromlist=["core.%s" % scraper_actual])
    except ImportError:
        exec "import core." + scraper_actual + " as scraper"
    except:
        import traceback
        logger.error(traceback.format_exc())

    while scraper:
        # Llamamos a la funcion find_and_set_infoLabels del scraper seleccionado
        scraper_result = scraper.find_and_set_infoLabels(item)

        # Verificar si existe 'code'
        if scraper_result and item.infoLabels['code']:
            # code correcto
            logger.info("Identificador encontrado: %s" % item.infoLabels['code'])
            scraper.completar_codigos(item)
            return True
        elif scraper_result:
            # Contenido encontrado pero no hay 'code'
            msg = "Identificador no encontrado para: %s" % title
        else:
            # Contenido no encontrado
            msg = "No se ha encontrado informacion para: %s" % title

        logger.info(msg)
        # Mostrar cuadro con otras opciones:
        if scrapers_disponibles[scraper_actual] in list_opciones_cuadro:
            list_opciones_cuadro.remove(scrapers_disponibles[scraper_actual])
        index = platformtools.dialog_select(msg, list_opciones_cuadro)

        if index < 0:
            logger.debug("Se ha pulsado 'cancelar' en la ventana '%s'" % msg)
            return False

        elif index == 0:
            # Pregunta el titulo
            title = platformtools.dialog_input(title, "Introduzca el nombre de la %s a buscar" % tipo_contenido)
            if title:
                if item.contentType == "movie":
                    item.contentTitle = title
                else:
                    item.contentSerieName = title
            else:
                logger.debug("he pulsado 'cancelar' en la ventana 'Introduzca el nombre correcto'")
                return False

        elif index == 1:
            # Hay q crear un cuadro de dialogo para introducir los datos
            logger.info("Completar información")
            if cuadro_completar(item):
                # code correcto
                logger.info("Identificador encontrado: %s" % str(item.infoLabels['code']))
                return True
                # raise

        elif list_opciones_cuadro[index] in scrapers_disponibles.values():
            # Obtener el nombre del modulo del scraper
            for k, v in scrapers_disponibles.items():
                if list_opciones_cuadro[index] == v:
                    if scrapers_disponibles[scraper_actual] not in list_opciones_cuadro:
                        list_opciones_cuadro.append(scrapers_disponibles[scraper_actual])
                    # Importamos el scraper k
                    scraper_actual = k
                    try:
                        scraper = None
                        scraper = __import__('core.%s' % scraper_actual, fromlist=["core.%s" % scraper_actual])
                    except ImportError:
                        exec "import core." + scraper_actual + " as scraper_module"
                    break

    logger.error("Error al importar el modulo scraper %s" % scraper_actual)


def cuadro_completar(item):
    logger.info()

    global dict_default
    dict_default = {}

    COLOR = ["0xFF8A4B08", "0xFFF7BE81"]
    # Creamos la lista de campos del infoLabel
    controls = [("title", "text", "Titulo:"),
                ("originaltitle", "text", "Titulo original"),
                ("year", "text", "Año"),
                ("identificadores", "label", "Identificadores:"),
                ("tmdb_id", "text", "    The Movie Database ID"),
                ("url_tmdb", "text", "        URL Tmdb", "+!eq(-1,'')"),
                ("tvdb_id", "text", "    The TVDB ID", "+eq(-7,'Serie')"),
                ("url_tvdb", "text", "        URL TVDB", "+!eq(-1,'')+eq(-8,'Serie')"),
                ("imdb_id", "text", "    IMDb ID"),
                ("otro_id", "text", "    Otro ID", "+eq(-1,'')"),
                ("urls", "label", "Imágenes (urls):"),
                ("fanart", "text", "    Fondo"),
                ("thumbnail", "text", "    Miniatura")]

    if item.infoLabels["mediatype"] == "movie":
        mediatype_default = 0
    else:
        mediatype_default = 1

    listado_controles = [{'id': "mediatype",
                          'type': "list",
                          'label': "Tipo de contenido",
                          'color': COLOR[1],
                          'default': mediatype_default,
                          'enabled': True,
                          'visible': True,
                          'lvalues': ["Película", "Serie"]
                          }]

    for i, c in enumerate(controls):
        color = COLOR[0]
        dict_default[c[0]] = item.infoLabels.get(c[0], '')

        enabled = True

        if i > 0 and c[1] != 'label':
            color = COLOR[1]
            enabled = "!eq(-%s,'')" % i
            if len(c) > 3:
                enabled += c[3]

        # default para casos especiales
        if c[0] == "url_tmdb" and item.infoLabels["tmdb_id"] and 'tmdb' in item.infoLabels["url_scraper"]:
            dict_default[c[0]] = item.infoLabels["url_scraper"]

        elif c[0] == "url_tvdb" and item.infoLabels["tvdb_id"] and 'thetvdb.com' in item.infoLabels["url_scraper"]:
            dict_default[c[0]] = item.infoLabels["url_scraper"]

        if not dict_default[c[0]] or dict_default[c[0]] == 'None' or dict_default[c[0]] == 0:
            dict_default[c[0]] = ''
        elif isinstance(dict_default[c[0]], (int, float, long)):
            # Si es numerico lo convertimos en str
            dict_default[c[0]] = str(dict_default[c[0]])

        listado_controles.append({'id': c[0],
                                  'type': c[1],
                                  'label': c[2],
                                  'color': color,
                                  'default': dict_default[c[0]],
                                  'enabled': enabled,
                                  'visible': True})

    # logger.debug(dict_default)
    if platformtools.show_channel_settings(listado_controles, caption="Completar información", item=item,
                                           callback="core.scraper.callback_cuadro_completar",
                                           custom_button={"visible": False}):
        return True

    else:
        return False


def callback_cuadro_completar(item, dict_values):
    # logger.debug(dict_values)
    global dict_default

    if dict_values.get("title", None):
        # Adaptar dict_values a infoLabels validos
        dict_values['mediatype'] = ['movie', 'tvshow'][dict_values['mediatype']]
        for k, v in dict_values.items():
            if k in dict_default and dict_default[k] == dict_values[k]:
                del dict_values[k]

        if isinstance(item.infoLabels, InfoLabels):
            infoLabels = item.infoLabels
        else:
            infoLabels = InfoLabels()

        infoLabels.update(dict_values)
        item.infoLabels = infoLabels

        if item.infoLabels['code']:
            return True

    return False


def get_nfo(item):
    """
    Devuelve la información necesaria para que se scrapee el resultado en la videoteca de kodi,

    @param item: elemento que contiene los datos necesarios para generar la info
    @type item: Item
    @rtype: str
    @return:
    """
    logger.info()
    if "infoLabels" in item and "noscrap_id" in item.infoLabels:
        # Crea el fichero xml con los datos que se obtiene de item ya que no hay ningún scraper activo
        info_nfo = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'

        if "season" in item.infoLabels and "episode" in item.infoLabels:
            info_nfo += '<episodedetails><title>%s</title>' % item.infoLabels['title']
            info_nfo += '<showtitle>%s</showtitle>' % item.infoLabels['tvshowtitle']
            info_nfo += '<thumb>%s</thumb>' % item.thumbnail

            info_nfo += '</episodedetails>\n'

        elif item.infoLabels["mediatype"] == "tvshow":
            info_nfo += '<tvshow><title>%s</title>' % item.infoLabels['title']
            info_nfo += '<thumb aspect="poster">%s</thumb>' % item.thumbnail
            info_nfo += '<fanart><thumb>%s</thumb></fanart>' % item.fanart

            info_nfo += '</tvshow>\n'

        else:
            info_nfo += '<movie><title>%s</title>' % item.infoLabels['title']
            info_nfo += '<thumb aspect="poster">%s</thumb>' % item.thumbnail
            info_nfo += '<fanart><thumb>%s</thumb></fanart>' % item.fanart

            info_nfo += '</movie>\n'

        return info_nfo
    else:
        return scraper.get_nfo(item)


def sort_episode_list(episodelist):
    scraper_actual = ['tmdb', 'tvdb'][config.get_setting("scraper_tvshows", "videolibrary")]

    if scraper_actual == "tmdb":
        episodelist.sort(key=lambda e: (int(e.contentSeason), int(e.contentEpisodeNumber)))

    elif scraper_actual == "tvdb":
        episodelist.sort(key=lambda e: (int(e.contentEpisodeNumber), int(e.contentSeason)))

    return episodelist
