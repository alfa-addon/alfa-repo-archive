# -*- coding: utf-8 -*-

import re
import urlparse

from channels import renumbertools
from core import httptools
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item

HOST = "https://animeflv.ru/"


def mainlist(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, action="novedades_episodios", title="Últimos episodios", url=HOST))
    itemlist.append(Item(channel=item.channel, action="novedades_anime", title="Últimos animes", url=HOST))
    itemlist.append(Item(channel=item.channel, action="listado", title="Animes", url=HOST + "animes/nombre/lista"))

    itemlist.append(Item(channel=item.channel, title="Buscar por:"))
    itemlist.append(Item(channel=item.channel, action="search", title="    Título"))
    itemlist.append(Item(channel=item.channel, action="search_section", title="    Género", url=HOST + "animes",
                         extra="genre"))

    itemlist = renumbertools.show_option(item.channel, itemlist)

    return itemlist


def clean_title(title):
    year_pattern = r'\([\d -]+?\)'

    return re.sub(year_pattern, '', title).strip()


def search(item, texto):
    logger.info()
    itemlist = []
    item.url = urlparse.urljoin(HOST, "search_suggest")
    texto = texto.replace(" ", "+")
    post = "value=%s" % texto
    data = httptools.downloadpage(item.url, post=post).data

    try:
        dict_data = jsontools.load(data)

        for e in dict_data:
            title = clean_title(scrapertools.htmlclean(e["name"]))
            url = e["url"]
            plot = e["description"]
            thumbnail = HOST + e["thumb"]
            new_item = item.clone(action="episodios", title=title, url=url, plot=plot, thumbnail=thumbnail)

            if "Pelicula" in e["genre"]:
                new_item.contentType = "movie"
                new_item.contentTitle = title
            else:
                new_item.show = title
                new_item.context = renumbertools.context(item)

            itemlist.append(new_item)

    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

    return itemlist


def search_section(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)

    patron = 'id="%s_filter"[^>]+><div class="inner">(.*?)</div></div>' % item.extra
    data = scrapertools.find_single_match(data, patron)
    matches = re.compile('<a href="([^"]+)"[^>]+>(.*?)</a>', re.DOTALL).findall(data)

    for url, title in matches:
        url = "%s/nombre/lista" % url
        itemlist.append(Item(channel=item.channel, action="listado", title=title, url=url,
                             context=renumbertools.context(item)))

    return itemlist


def newest(categoria):
    itemlist = []

    if categoria == 'anime':
        itemlist = novedades_episodios(Item(url=HOST))

    return itemlist


def novedades_episodios(item):
    logger.info()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)
    data = scrapertools.find_single_match(data, '<ul class="ListEpisodios[^>]+>(.*?)</ul>')

    matches = re.compile('href="([^"]+)"[^>]+>.+?<img src="([^"]+)".+?"Capi">(.*?)</span>'
                         '<strong class="Title">(.*?)</strong>', re.DOTALL).findall(data)
    itemlist = []

    for url, thumbnail, str_episode, show in matches:

        try:
            episode = int(str_episode.replace("Ep. ", ""))
        except ValueError:
            season = 1
            episode = 1
        else:
            season, episode = renumbertools.numbered_for_tratk(item.channel, item.show, 1, episode)

        title = "%s: %sx%s" % (show, season, str(episode).zfill(2))
        url = urlparse.urljoin(HOST, url)
        thumbnail = urlparse.urljoin(HOST, thumbnail)

        new_item = Item(channel=item.channel, action="findvideos", title=title, url=url, show=show, thumbnail=thumbnail,
                        fulltitle=title)

        itemlist.append(new_item)

    return itemlist


def novedades_anime(item):
    logger.info()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)
    data = scrapertools.find_single_match(data, '<ul class="ListAnimes[^>]+>(.*?)</ul>')

    matches = re.compile('<img src="([^"]+)".+?<a href="([^"]+)">(.*?)</a>', re.DOTALL).findall(data)
    itemlist = []

    for thumbnail, url, title in matches:
        url = urlparse.urljoin(HOST, url)
        thumbnail = urlparse.urljoin(HOST, thumbnail)
        title = clean_title(title)

        new_item = Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail,
                        fulltitle=title)

        new_item.show = title
        new_item.context = renumbertools.context(item)

        itemlist.append(new_item)

    return itemlist


def listado(item):
    logger.info()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)
    # logger.debug("datito %s" % data)

    url_pagination = scrapertools.find_single_match(data, '<li class="current">.*?</li>[\s]<li><a href="([^"]+)">')

    data = scrapertools.find_single_match(data, '</div><div class="full">(.*?)<div class="pagination')

    matches = re.compile('<img.+?src="([^"]+)".+?<a href="([^"]+)">(.*?)</a>.+?'
                         '<div class="full item_info genres_info">(.*?)</div>.+?class="full">(.*?)</p>',
                         re.DOTALL).findall(data)

    itemlist = []

    for thumbnail, url, title, genres, plot in matches:

        title = clean_title(title)
        url = urlparse.urljoin(HOST, url)
        thumbnail = urlparse.urljoin(HOST, thumbnail)

        new_item = Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail,
                        fulltitle=title, plot=plot)

        if "Pelicula Anime" in genres:
            new_item.contentType = "movie"
            new_item.contentTitle = title
        else:
            new_item.show = title
            new_item.context = renumbertools.context(item)

        itemlist.append(new_item)

    if url_pagination:
        url = urlparse.urljoin(HOST, url_pagination)
        title = ">> Pagina Siguiente"

        itemlist.append(Item(channel=item.channel, action="listado", title=title, url=url))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)

    if item.plot == "":
        item.plot = scrapertools.find_single_match(data, 'Description[^>]+><p>(.*?)</p>')

    data = scrapertools.find_single_match(data, '<div class="Sect Episodes full">(.*?)</div>')
    matches = re.compile('<a href="([^"]+)"[^>]+>(.+?)</a', re.DOTALL).findall(data)

    for url, title in matches:
        title = title.strip()
        url = urlparse.urljoin(item.url, url)
        thumbnail = item.thumbnail

        try:
            episode = int(scrapertools.find_single_match(title, "Episodio (\d+)"))
        except ValueError:
            season = 1
            episode = 1
        else:
            season, episode = renumbertools.numbered_for_tratk(item.channel, item.show, 1, episode)

        title = "%s: %sx%s" % (item.title, season, str(episode).zfill(2))

        itemlist.append(item.clone(action="findvideos", title=title, url=url, thumbnail=thumbnail, fulltitle=title,
                                   fanart=thumbnail, contentType="episode"))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []

    _id = scrapertools.find_single_match(item.url, 'https://animeflv.ru/ver/([^/]+)/')
    post = "embed_id=%s" % _id
    data = httptools.downloadpage("https://animeflv.ru/get_video_info", post=post).data
    dict_data = jsontools.load(data)

    headers = dict()
    headers["Referer"] = item.url
    data = httptools.downloadpage("https:" + dict_data["value"], headers=headers).data
    dict_data = jsontools.load(data)

    list_videos = dict_data["playlist"][0]["sources"]

    if isinstance(list_videos, list):
        for video in list_videos:
            itemlist.append(Item(channel=item.channel, action="play", url=video["file"], show=re.escape(item.show),
                                 title="Ver en calidad [%s]" % video["label"], plot=item.plot, fulltitle=item.title,
                                 thumbnail=item.thumbnail))

    else:
        for video in list_videos.values():
            itemlist.append(Item(channel=item.channel, action="play", url=video["file"], show=re.escape(item.show),
                                 title="Ver en calidad [%s]" % video["label"], plot=item.plot, fulltitle=item.title,
                                 thumbnail=item.thumbnail))

    return itemlist
