# -*- coding: utf-8 -*-

import os
import re

from core import config
from core import logger
from core import scrapertools
from core.item import Item


def strip_tags(value):
    return re.sub(r'<[^>]*?>', '', value)


def mainlist(item):
    logger.info()
    user = config.get_setting("filesmonsteruser")
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="unusualporn", title="Canal unusualporn.net",
                         thumbnail="http://filesmonster.biz/img/logo.png"))
    itemlist.append(Item(channel=item.channel, action="files_monster", title="Canal files-monster.org",
                         thumbnail="http://files-monster.org/template/static/images/logo.jpg"))
    itemlist.append(Item(channel=item.channel, action="filesmonster", title="Canal filesmonster.filesdl.net",
                         thumbnail="http://filesmonster.biz/img/logo.png"))
    if user != '': itemlist.append(
        Item(channel=item.channel, action="favoritos", title="Favoritos en filesmonster.com del usuario " + user,
             folder=True))

    return itemlist


def filesmonster(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="videos", title="Ultimos vídeos",
                         thumbnail="http://photosex.biz/imager/w_400/h_400/9f869c6cb63e12f61b58ffac2da822c9.jpg",
                         url="http://filesmonster.filesdl.net"))
    itemlist.append(Item(channel=item.channel, action="categorias", title="Categorias",
                         thumbnail="http://photosex.biz/imager/w_400/h_500/e48337cd95bbb6c2c372ffa6e71441ac.jpg",
                         url="http://filesmonster.filesdl.net"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar en filesmonster.fliesdl.net",
                         url="http://filesmonster.filesdl.net/posts/search?q=%s"))
    return itemlist


def unusualporn(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="videos_2", title="Últimos vídeos", url="http://unusualporn.net/",
                         thumbnail="http://photosex.biz/imager/w_400/h_500/e48337cd95bbb6c2c372ffa6e71441ac.jpg"))
    itemlist.append(Item(channel=item.channel, action="categorias_2", title="Categorías", url="http://unusualporn.net/",
                         thumbnail="http://photosex.biz/imager/w_400/h_500/e48337cd95bbb6c2c372ffa6e71441ac.jpg"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar en unusualporn",
                         url="http://unusualporn.net/search/%s"))
    return itemlist


def files_monster(item):
    logger.info()

    itemlist = []
    itemlist.append(
        Item(channel=item.channel, action="videos_3", title="Últimos vídeos", url="http://www.files-monster.org/",
             thumbnail="http://photosex.biz/imager/w_400/h_500/e48337cd95bbb6c2c372ffa6e71441ac.jpg"))
    itemlist.append(
        Item(channel=item.channel, action="categorias_3", title="Categorías", url="http://www.files-monster.org/",
             thumbnail="http://photosex.biz/imager/w_400/h_500/e48337cd95bbb6c2c372ffa6e71441ac.jpg"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar en files-monster.org",
                         url="http://files-monster.org/search?search=%s"))
    return itemlist


def favoritos(item):
    user = config.get_setting("filesmonsteruser")
    password = config.get_setting("filesmonsterpassword")
    logger.info()
    name_file = os.path.splitext(os.path.basename(__file__))[0]
    fname = os.path.join(config.get_data_path(), "settings_channels", name_file + "_favoritos.txt")
    fa = open(fname, 'a+')
    fa.close()
    f = open(fname, 'r')
    lines = f.readlines()
    f.close()
    itemlist = []
    post2 = "username=" + user + "&password=" + password
    login_url = "http://filesmonster.com/api/public/login"
    data1 = scrapertools.cache_page(login_url, post=post2)
    partes1 = data1.split('"')
    estado = partes1[3]
    if estado != 'success': itemlist.append(Item(channel=item.channel,
                                                 title="No pudo accederse con tus datos de acceso de Filesmonster.com, introdúcelos en con el apartado figuración. Error: " + estado + data1))
    url_favoritos = "http://filesmonster.com/?favorites=1"
    data2 = scrapertools.cache_page(url_favoritos, post=post2)
    data2 = scrapertools.find_single_match(data2, 'favorites-table(.*?)pager')
    patronvideos = '<a href="([^"]+)">([^<]+)</a>.*?del=([^"]+)"'
    matches = re.compile(patronvideos, re.DOTALL).findall(data2)
    contador = 0
    for url, title, borrar in matches:
        contador = contador + 1
        imagen = ''
        for linea in lines:
            partes2 = linea.split("@")
            parte_url = partes2[0]
            parte_imagen = partes2[1]
            if (parte_url == url): imagen = parte_imagen.rstrip('\n').rstrip('\r')

        if url.find("?fid=") == -1:
            itemlist.append(
                Item(channel=item.channel, action="play", server="filesmonster", title=title, fulltitle=item.title,
                     url=url, thumbnail=imagen, folder=False))
        else:
            itemlist.append(
                Item(channel=item.channel, action="detail", server="filesmonster", title=title, fulltitle=title,
                     thumbnail=imagen, url=url, folder=True))
        itemlist.append(Item(channel=item.channel, action="quitar_favorito",
                             title="(-) quitar de mis favoritos en filesmonster.com", thumbnail=imagen,
                             url="http://filesmonster.com/?favorites=1&del=" + borrar, plot=borrar))
        itemlist.append(Item(channel=item.channel, title="", folder=True))
    if contador == 0 and estado == 'success':
        itemlist.append(
            Item(channel=item.channel, title="No tienes ningún favorito, navega por las diferentes fuentes y añádelos"))
    return itemlist


def quitar_favorito(item):
    logger.info()
    itemlist = []

    data = scrapertools.downloadpage(item.url)
    itemlist.append(Item(channel=item.channel, action="favoritos",
                         title="El vídeo ha sido eliminado de tus favoritos, pulsa para volver a tu lista de favoritos"))

    return itemlist


def anadir_favorito(item):
    logger.info()
    name_file = os.path.splitext(os.path.basename(__file__))[0]
    fname = os.path.join(config.get_data_path(), "settings_channels", name_file + "_favoritos.txt")
    user = config.get_setting("filesmonsteruser")
    password = config.get_setting("filesmonsterpassword")
    itemlist = []
    post2 = "username=" + user + "&password=" + password
    login_url = "http://filesmonster.com/api/public/login"
    data1 = scrapertools.cache_page(login_url, post=post2)
    if item.plot == 'el archivo':
        id1 = item.url.split('?id=')
        id = id1[1]
        que = "file"
    if item.plot == 'la carpeta':
        id1 = item.url.split('?fid=')
        id = id1[1]
        que = "folder"
    url = "http://filesmonster.com/ajax/add_to_favorites"
    post3 = "username=" + user + "&password=" + password + "&id=" + id + "&obj_type=" + que
    data2 = scrapertools.cache_page(url, post=post3)
    if data2 == 'Already in Your favorites': itemlist.append(Item(channel=item.channel, action="favoritos",
                                                                  title="" + item.plot + " ya estaba en tu lista de favoritos (" + user + ") en Filesmonster"))
    if data2 != 'You are not logged in' and data2 != 'Already in Your favorites':
        itemlist.append(Item(channel=item.channel, action="favoritos",
                             title="Se ha añadido correctamente " + item.plot + " a tu lista de favoritos (" + user + ") en Filesmonster",
                             plot=data1 + data2))
        f = open(fname, "a+")
        if (item.plot == 'la carpeta'):
            ruta = "http://filesmonster.com/folders.php?"
        if (item.plot == 'el archivo'):
            ruta = "http://filesmonster.com/download.php"
        laruta = ruta + item.url
        laruta = laruta.replace("http://filesmonster.com/folders.php?http://filesmonster.com/folders.php?",
                                "http://filesmonster.com/folders.php?")
        laruta = laruta.replace("http://filesmonster.com/download.php?http://filesmonster.com/download.php?",
                                "http://filesmonster.com/download.php?")
        f.write(laruta + '@' + item.thumbnail + '\n')
        f.close()
    if data2 == 'You are not logged in': itemlist.append(Item(channel=item.channel, action="favoritos",
                                                              title="No ha sido posible añadir " + item.plot + " a tu lista de favoritos (" + user + " no logueado en Filesmonster)", ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = scrapertools.downloadpage(item.url)
    data = scrapertools.find_single_match(data,
                                          'Categories <b class="caret"></b></a>(.*?)RSS <b class="caret"></b></a>')

    patronvideos = '<a href="([^"]+)">([^<]+)</a>'

    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for url, title in matches:
        itemlist.append(Item(channel=item.channel, action="videos", title=title, url=url))

    return itemlist


def categorias_2(item):
    logger.info()
    itemlist = []

    data = scrapertools.downloadpage(item.url)

    patronvideos = '<li class="cat-item cat-item-[\d]+"><a href="([^"]+)" title="[^"]+">([^<]+)</a><a class="rss_s" title="[^"]+" target="_blank" href="[^"]+"></a></li>'

    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for url, title in matches:
        itemlist.append(Item(channel=item.channel, action="videos_2", title=title, url=url))

    return itemlist


def categorias_3(item):
    logger.info()
    itemlist = []

    data = scrapertools.downloadpage(item.url)

    patronvideos = '<li><a href="([^"]+)">([^<]+)</a></li>'

    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for url, title in matches:
        itemlist.append(Item(channel=item.channel, action="videos_3", title=title, url=url))

    return itemlist


def search(item, texto):
    logger.info("texto:" + texto)
    original = item.url
    item.url = item.url % texto
    try:
        if original == 'http://filesmonster.filesdl.net/posts/search?q=%s':
            return videos(item)
        if original == 'http://unusualporn.net/search/%s':
            return videos_2(item)
        if original == 'http://files-monster.org/search?search=%s':
            return videos_3(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def videos(item):
    logger.info()
    itemlist = []

    url = item.url
    while url and len(itemlist) < 25:
        data = scrapertools.downloadpage(url)
        patronvideos = '<div class="panel-heading">.*?<a href="([^"]+)">([^<]+).*?</a>.*?<div class="panel-body" style="text-align: center;">.*?<img src="([^"]+)".*?'
        matches = re.compile(patronvideos, re.DOTALL).findall(data)

        for url, title, thumbnail in matches:
            title = title.strip()
            itemlist.append(
                Item(channel=item.channel, action="detail", title=title, fulltitle=title, url=url, thumbnail=thumbnail))

        url = scrapertools.find_single_match(data, '<li><a href="([^"]+)">Next</a></li>').replace("&amp;", "&")

    # Enlace para la siguiente pagina
    if url:
        itemlist.append(Item(channel=item.channel, action="videos", title=">> Página Siguiente", url=url))

    return itemlist


def videos_2(item):
    logger.info()
    itemlist = []
    url_limpia = item.url.split("?")[0]
    url = item.url
    while url and len(itemlist) < 25:
        data = scrapertools.downloadpage(url)
        patronvideos = 'data-link="([^"]+)" data-title="([^"]+)" src="([^"]+)" border="0" />';
        matches = re.compile(patronvideos, re.DOTALL).findall(data)

        for url, title, thumbnail in matches:
            itemlist.append(Item(channel=item.channel, action="detail_2", title=title, fulltitle=title, url=url,
                                 thumbnail=thumbnail))

        url = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)" />').replace("&amp;", "&")

    # Enlace para la siguiente pagina
    if url:
        itemlist.append(Item(channel=item.channel, action="videos_2", title=">> Página Siguiente", url=url))

    return itemlist


def videos_3(item):
    logger.info()
    itemlist = []

    url = item.url
    url_limpia = item.url.split("?")[0]
    while url and len(itemlist) < 25:
        data = scrapertools.downloadpage(url)
        patronvideos = '<a href="([^"]+)">.*?<img src="([^"]+)" border="0" title=".*?([^"]+).*?" height="70" />'
        matches = re.compile(patronvideos, re.DOTALL).findall(data)

        for url, thumbnail, title in matches:
            itemlist.append(Item(channel=item.channel, action="detail_2", title=title, fulltitle=title, url=url,
                                 thumbnail=thumbnail))

        url = scrapertools.find_single_match(data,
                                             '<a style="text-decoration:none;" href="([^"]+)">&rarr;</a>').replace(
            "&amp;", "&")

    # Enlace para la siguiente pagina
    if url:
        itemlist.append(
            Item(channel=item.channel, action="videos_3", title=">> Página Siguiente", url=url_limpia + url))

    return itemlist


def detail(item):
    logger.info()
    itemlist = []

    data = scrapertools.downloadpage(item.url)
    patronvideos = '["|\'](http\://filesmonster.com/download.php\?[^"\']+)["|\']'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for url in matches:
        title = "Archivo %d: %s [filesmonster]" % (len(itemlist) + 1, item.fulltitle)
        itemlist.append(
            Item(channel=item.channel, action="play", server="filesmonster", title=title, fulltitle=item.fulltitle,
                 url=url, thumbnail=item.thumbnail, folder=False))
        itemlist.append(Item(channel=item.channel, action="anadir_favorito",
                             title="(+) Añadir el vídeo a tus favoritos en filesmonster", url=url,
                             thumbnail=item.thumbnail, plot="el archivo", folder=True))
        itemlist.append(Item(channel=item.channel, title=""));

    patronvideos = '["|\'](http\://filesmonster.com/folders.php\?[^"\']+)["|\']'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    for url in matches:
        if not url == item.url:
            logger.info(url)
            logger.info(item.url)
            title = "Carpeta %d: %s [filesmonster]" % (len(itemlist) + 1, item.fulltitle)
            itemlist.append(Item(channel=item.channel, action="detail", title=title, fulltitle=item.fulltitle, url=url,
                                 thumbnail=item.thumbnail, folder=True))
            itemlist.append(Item(channel=item.channel, action="anadir_favorito",
                                 title="(+) Añadir la carpeta a tus favoritos en filesmonster", url=url,
                                 thumbnail=item.thumbnail, plot="la carpeta", folder=True))
            itemlist.append(Item(channel=item.channel, title=""));

    return itemlist


def detail_2(item):
    logger.info()
    itemlist = []

    # descarga la pagina
    data = scrapertools.downloadpageGzip(item.url)
    data = data.split('<span class="filesmonsterdlbutton">Download from Filesmonster</span>')
    data = data[0]
    # descubre la url
    patronvideos = 'href="http://filesmonster.com/download.php(.*?)".(.*?)'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    for match2 in matches:
        url = "http://filesmonster.com/download.php" + match2[0]
        title = "Archivo %d: %s [filesmonster]" % (len(itemlist) + 1, item.fulltitle)
        itemlist.append(
            Item(channel=item.channel, action="play", server="filesmonster", title=title, fulltitle=item.fulltitle,
                 url=url, thumbnail=item.thumbnail, folder=False))
        itemlist.append(Item(channel=item.channel, action="anadir_favorito",
                             title="(+) Añadir el vídeo a tus favoritos en filesmonster", url=match2[0],
                             thumbnail=item.thumbnail, plot="el archivo", folder=True))
        itemlist.append(Item(channel=item.channel, title=""));

    patronvideos = '["|\'](http\://filesmonster.com/folders.php\?[^"\']+)["|\']'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    for url in matches:
        if not url == item.url:
            logger.info(url)
            logger.info(item.url)
            title = "Carpeta %d: %s [filesmonster]" % (len(itemlist) + 1, item.fulltitle)
            itemlist.append(Item(channel=item.channel, action="detail", title=title, fulltitle=item.fulltitle, url=url,
                                 thumbnail=item.thumbnail, folder=True))
            itemlist.append(Item(channel=item.channel, action="anadir_favorito",
                                 title="(+) Añadir la carpeta a tus favoritos en filesmonster", url=url,
                                 thumbnail=item.thumbnail, plot="la carpeta", folder=True))
            itemlist.append(Item(channel=item.channel, title=""));

    return itemlist
