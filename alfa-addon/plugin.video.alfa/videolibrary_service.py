# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Service for updating new episodes on library series
# ------------------------------------------------------------

import datetime
import imp
import math
import threading

from core import config
from core import filetools
from core import logger
from core import videolibrarytools
from platformcode import platformtools


def update(path, p_dialog, i, t, serie, overwrite):
    logger.info("Actualizando " + path)
    insertados_total = 0

    # logger.debug("%s: %s" %(serie.contentSerieName,str(list_canales) ))
    for channel, url in serie.library_urls.items():
        serie.channel = channel
        serie.url = url

        heading = 'Actualizando videoteca....'
        p_dialog.update(int(math.ceil((i + 1) * t)), heading, "%s: %s" % (serie.contentSerieName,
                                                                          serie.channel.capitalize()))
        try:
            pathchannels = filetools.join(config.get_runtime_path(), "channels", serie.channel + '.py')
            logger.info("Cargando canal: " + pathchannels + " " +
                        serie.channel)

            if serie.library_filter_show:
                serie.show = serie.library_filter_show.get(channel, serie.contentSerieName)

            obj = imp.load_source(serie.channel, pathchannels)
            itemlist = obj.episodios(serie)

            try:
                if int(overwrite) == 3:
                    # Sobrescribir todos los archivos (tvshow.nfo, 1x01.nfo, 1x01 [canal].json, 1x01.strm, etc...)
                    insertados, sobreescritos, fallidos = videolibrarytools.save_tvshow(serie, itemlist)
                else:
                    insertados, sobreescritos, fallidos = videolibrarytools.save_episodes(path, itemlist, serie,
                                                                                          silent=True,
                                                                                          overwrite=overwrite)
                insertados_total += insertados

            except Exception, ex:
                logger.error("Error al guardar los capitulos de la serie")
                template = "An exception of type %s occured. Arguments:\n%r"
                message = template % (type(ex).__name__, ex.args)
                logger.error(message)

        except Exception, ex:
            logger.error("Error al obtener los episodios de: %s" % serie.show)
            template = "An exception of type %s occured. Arguments:\n%r"
            message = template % (type(ex).__name__, ex.args)
            logger.error(message)

    return insertados_total > 0


def check_for_update(overwrite=True):
    logger.info("Actualizando series...")
    p_dialog = None
    serie_actualizada = False
    update_when_finished = False
    hoy = datetime.date.today()

    try:
        if config.get_setting("update", "videolibrary") != 0 or overwrite:
            config.set_setting("updatelibrary_last_check", hoy.strftime('%Y-%m-%d'), "videolibrary")

            heading = 'Actualizando videoteca....'
            p_dialog = platformtools.dialog_progress_bg('alfa', heading)
            p_dialog.update(0, '')

            import glob
            show_list = glob.glob(filetools.join(videolibrarytools.TVSHOWS_PATH, u'/*/tvshow.nfo'))

            if show_list:
                t = float(100) / len(show_list)

            for i, tvshow_file in enumerate(show_list):
                head_nfo, serie = videolibrarytools.read_nfo(tvshow_file)
                path = filetools.dirname(tvshow_file)

                logger.info("serie=" + serie.contentSerieName)
                p_dialog.update(int(math.ceil((i + 1) * t)), heading, serie.contentSerieName)

                interval = int(serie.active)  # Podria ser del tipo bool

                if not serie.active:
                    # si la serie no esta activa descartar
                    continue

                # obtenemos las fecha de actualizacion y de la proxima programada para esta serie
                update_next = serie.update_next
                if update_next:
                    y, m, d = update_next.split('-')
                    update_next = datetime.date(int(y), int(m), int(d))
                else:
                    update_next = hoy

                update_last = serie.update_last
                if update_last:
                    y, m, d = update_last.split('-')
                    update_last = datetime.date(int(y), int(m), int(d))
                else:
                    update_last = hoy

                # si la serie esta activa ...
                if overwrite or config.get_setting("updatetvshows_interval", "videolibrary") == 0:
                    # ... forzar actualizacion independientemente del intervalo
                    serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)

                elif interval == 1 and update_next <= hoy:
                    # ...actualizacion diaria
                    serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)
                    if not serie_actualizada and update_last <= hoy - datetime.timedelta(days=7):
                        # si hace una semana q no se actualiza, pasar el intervalo a semanal
                        interval = 7
                        update_next = hoy + datetime.timedelta(days=interval)

                elif interval == 7 and update_next <= hoy:
                    # ...actualizacion semanal
                    serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)
                    if not serie_actualizada:
                        if update_last <= hoy - datetime.timedelta(days=14):
                            # si hace 2 semanas q no se actualiza, pasar el intervalo a mensual
                            interval = 30

                        update_next += datetime.timedelta(days=interval)

                elif interval == 30 and update_next <= hoy:
                    # ...actualizacion mensual
                    serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)
                    if not serie_actualizada:
                        update_next += datetime.timedelta(days=interval)

                if interval != int(serie.active) or update_next.strftime('%Y-%m-%d') != serie.update_next:
                    serie.active = interval
                    serie.update_next = update_next.strftime('%Y-%m-%d')
                    serie.channel = "videolibrary"
                    serie.action = "get_seasons"
                    filetools.write(tvshow_file, head_nfo + serie.tojson())

                if serie_actualizada:
                    if config.get_setting("search_new_content", "videolibrary") == 0:
                        # Actualizamos la videoteca de Kodi: Buscar contenido en la carpeta de la serie
                        if config.is_xbmc():
                            from platformcode import xbmc_videolibrary
                            xbmc_videolibrary.update(folder=filetools.basename(path))
                    else:
                        update_when_finished = True

            if config.get_setting("search_new_content", "videolibrary") == 1 and update_when_finished:
                # Actualizamos la videoteca de Kodi: Buscar contenido en todas las series
                if config.is_xbmc():
                    from platformcode import xbmc_videolibrary
                    xbmc_videolibrary.update()

            p_dialog.close()

        else:
            logger.info("No actualiza la videoteca, está desactivado en la configuración de alfa")

    except Exception, ex:
        logger.error("Se ha producido un error al actualizar las series")
        template = "An exception of type %s occured. Arguments:\n%r"
        message = template % (type(ex).__name__, ex.args)
        logger.error(message)

        if p_dialog:
            p_dialog.close()


def start(thread=True):
    if thread:
        t = threading.Thread(target=start, args=[False])
        t.setDaemon(True)
        t.start()
    else:
        import time

        update_wait = [0, 10000, 20000, 30000, 60000]
        wait = update_wait[int(config.get_setting("update_wait", "videolibrary"))]
        if wait > 0:
            time.sleep(wait)

        if not config.get_setting("update", "videolibrary") == 2:
            check_for_update(overwrite=False)

        # Se ejecuta ciclicamente
        while True:
            monitor_update()
            time.sleep(3600)  # cada hora


def monitor_update():
    update_setting = config.get_setting("update", "videolibrary")
    if update_setting == 2 or update_setting == 3:  # "Actualizar "Cada dia" o "Una vez al dia"
        hoy = datetime.date.today()
        last_check = config.get_setting("updatelibrary_last_check", "videolibrary")
        if last_check:
            y, m, d = last_check.split('-')
            last_check = datetime.date(int(y), int(m), int(d))
        else:
            last_check = hoy - datetime.timedelta(days=1)

        update_start = config.get_setting("everyday_delay", "videolibrary") * 4

        # logger.info("Ultima comprobacion: %s || Fecha de hoy:%s || Hora actual: %s" %
        #             (last_check, hoy, datetime.datetime.now().hour))
        # logger.info("Atraso del inicio del dia: %i:00" % update_start)

        if last_check < hoy and datetime.datetime.now().hour >= int(update_start):
            logger.info("Inicio actualizacion programada: %s" % datetime.datetime.now())
            check_for_update(overwrite=False)


if __name__ == "__main__":
    # Se ejecuta en cada inicio
    import xbmc

    # modo adulto:
    # Conversion de False y True al sitema actual 0: Nunca, 1:Siempre, 2:Solo hasta que se reinicie Kodi
    # y si es == 2 lo desactivamos.
    if config.get_setting("adult_mode") == False or config.get_setting("adult_mode") == 2:
        config.set_setting("adult_mode", 0)
    elif config.get_setting("adult_mode") == True:
        config.set_setting("adult_mode", 1)

    update_wait = [0, 10000, 20000, 30000, 60000]
    wait = update_wait[int(config.get_setting("update_wait", "videolibrary"))]
    if wait > 0:
        xbmc.sleep(wait)

    if not config.get_setting("update", "videolibrary") == 2:
        check_for_update(overwrite=False)

    # Se ejecuta ciclicamente
    if config.get_platform(True)['num_version'] >= 14:
        monitor = xbmc.Monitor()  # For Kodi >= 14
    else:
        monitor = None  # For Kodi < 14

    if monitor:
        while not monitor.abortRequested():
            monitor_update()
            if monitor.waitForAbort(3600):  # cada hora
                break
    else:
        while not xbmc.abortRequested:
            monitor_update()
            xbmc.sleep(3600)
