# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools
from core.item import Item

host = 'http://javus.net/'


def mainlist(item):
    if item.url == "":
        item.url = host

    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<a href="([^"]+)" title="([^"]+)" rel="nofollow" class="post-image post-image-left".*?\s*<div class="featured-thumbnail"><img width="203" height="150" src="([^"]+)" class="attachment-featured size-featured wp-post-image" alt="" title="" \/><\/div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        url = scrapedurl
        title = scrapedtitle.decode('utf-8')
        thumbnail = scrapedthumbnail
        fanart = ''

        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, fanart=fanart))

    # Paginacion
    title = ''
    siguiente = scrapertools.find_single_match(data, "<a rel='nofollow' href='([^']+)' class='inactive'>Next <")
    ultima = scrapertools.find_single_match(data, "<a rel='nofollow' class='inactive' href='([^']+)'>Last <")
    if siguiente != ultima:
        titlen = 'Pagina Siguiente >>> '
        fanart = ''
        itemlist.append(Item(channel=item.channel, action="mainlist", title=titlen, url=siguiente, fanart=fanart))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    if texto != '':
        return todas(item)
    else:
        return []
