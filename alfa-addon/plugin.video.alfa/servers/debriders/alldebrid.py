# -*- coding: utf-8 -*-

from core import jsontools
from core import logger
from core import scrapertools


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s' , user='%s' , password='%s', video_password=%s)" % (
        page_url, user, "**************************"[0:len(password)], video_password))
    page_url = correct_url(page_url)

    url = 'http://www.alldebrid.com/service.php?pseudo=%s&password=%s&link=%s&nb=0&json=true&pw=' % (
        user, password, page_url)

    data = jsontools.load(scrapertools.downloadpage(url))

    video_urls = []
    if data and data["link"] and not data["error"]:
        extension = ".%s [alldebrid]" % data["filename"].rsplit(".", 1)[1]
        video_urls.append([extension, data["link"]])

    else:
        try:
            server_error = "Alldebrid: " + data["error"].decode("utf-8", "ignore")
            server_error = server_error.replace("This link isn't available on the hoster website.",
                                                "Enlace no disponible en el servidor de descarga") \
                .replace("Hoster unsupported or under maintenance.",
                         "Servidor no soportado o en mantenimiento")
        except:
            server_error = "Alldebrid: Error en el usuario/password o en la web"

        video_urls.append([server_error, ''])

    return video_urls


def correct_url(url):
    if "userporn.com" in url:
        url = url.replace("/e/", "/video/")

    if "putlocker" in url:
        url = url.replace("/embed/", "/file/")
    return url
