# -*- coding: utf-8 -*-

import base64
import re

from core import logger
from core import scrapertools

HOSTER_KEY = "NTI2NzI5Cgo="


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []
    # Espera un poco como hace el player flash
    logger.info("waiting 3 secs")
    import time
    time.sleep(3)

    # Obtiene el id
    code = Extract_id(page_url)

    # Descarga el json con los detalles del vídeo
    # http://www.userporn.com/player_control/settings.php?v=dvthddkC7l4J&em=TRUE&fv=v1.1.45
    controluri = "http://userporn.com/player_control/settings.php?v=" + code + "&em=TRUE&fv=v1.1.45"
    datajson = scrapertools.cachePage(controluri)
    # logger.info("response="+datajson);

    # Convierte el json en un diccionario
    datajson = datajson.replace("false", "False").replace("true", "True")
    datajson = datajson.replace("null", "None")
    datadict = eval("(" + datajson + ")")

    # Formatos
    formatos = datadict["settings"]["res"]

    for formato in formatos:
        uri = base64.decodestring(formato["u"])
        resolucion = formato["l"]
        import videobb
        video_url = videobb.build_url(uri, HOSTER_KEY, datajson)
        video_urls.append(["%s [userporn]" % resolucion, video_url.replace(":80", "")])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls


def Extract_id(url):
    _VALID_URL = r'^((?:http://)?(?:\w+\.)?userporn\.com/(?:(?:(?:e/)|(?:video/))|(?:(?:flash/)|(?:f/)))?)?([0-9A-Za-z_-]+)(?(1).+)?$'
    # Extract video id from URL
    mobj = re.match(_VALID_URL, url)
    if mobj is None:
        logger.info('ERROR: URL invalida: %s' % url)
        return ""
    id = mobj.group(2)
    logger.info("extracted code=" + id)
    return id
