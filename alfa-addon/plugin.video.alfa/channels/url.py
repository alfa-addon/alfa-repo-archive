# -*- coding: utf-8 -*-

from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="search",
                         title="Entra aquí y teclea la URL [Enlace a servidor online/descarga]"))
    itemlist.append(
        Item(channel=item.channel, action="search", title="Entra aquí y teclea la URL [Enlace directo a un vídeo]"))
    itemlist.append(Item(channel=item.channel, action="search",
                         title="Entra aquí y teclea la URL [Búsqueda de enlaces en una url]"))

    return itemlist


# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item, texto):
    logger.info("texto=" + texto)

    if not texto.startswith("http://"):
        texto = "http://" + texto

    itemlist = []

    if "servidor" in item.title:
        itemlist = servertools.find_video_items(data=texto)
        for item in itemlist:
            item.channel = "url"
            item.action = "play"
    elif "directo" in item.title:
        itemlist.append(
            Item(channel=item.channel, action="play", url=texto, server="directo", title="Ver enlace directo"))
    else:
        data = scrapertools.downloadpage(texto)
        itemlist = servertools.find_video_items(data=data)
        for item in itemlist:
            item.channel = "url"
            item.action = "play"

    if len(itemlist) == 0:
        itemlist.append(Item(channel=item.channel, action="search", title="No hay ningún vídeo compatible en esa URL"))

    return itemlist
