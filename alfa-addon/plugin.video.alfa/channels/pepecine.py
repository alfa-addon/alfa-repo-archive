# -*- coding: utf-8 -*-

import re
import urlparse

from core import config
from core import httptools
from core import jsontools
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item, InfoLabels

__url_base__ = "http://pepecine.net"
__chanel__ = "pepecine"
fanart_host = "https://d12.usercdn.com/i/02278/u875vjx9c0xs.png"


def mainlist(item):
    logger.info()

    itemlist = []
    url_peliculas = urlparse.urljoin(__url_base__, "plugins/ultimas-peliculas-updated.php")
    itemlist.append(
        Item(channel=__chanel__, title="Películas", text_color="0xFFEB7600", text_bold=True, fanart=fanart_host,
             thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/movies.png"))
    itemlist.append(Item(channel=__chanel__, action="listado", title="     Novedades", page=0, viewcontent="movies",
                         text_color="0xFFEB7600", extra="movie", fanart=fanart_host, url=url_peliculas,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/movies.png"))
    itemlist.append(Item(channel=__chanel__, action="sub_filtrar", title="     Filtrar películas por género",
                         text_color="0xFFEB7600", extra="movie", fanart=fanart_host, url=url_peliculas,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/movies_filtrar.png"))
    itemlist.append(Item(channel=__chanel__, action="search", title="     Buscar películas por título",
                         text_color="0xFFEB7600", extra="movie", fanart=fanart_host, url=url_peliculas,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/movies_buscar.png"))

    url_series = urlparse.urljoin(__url_base__, "plugins/series-episodios-updated.php")
    itemlist.append(
        Item(channel=__chanel__, title="Series", text_color="0xFFEB7600", text_bold=True, fanart=fanart_host,
             thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv.png"))
    itemlist.append(Item(channel=__chanel__, action="listado", title="     Novedades", page=0, viewcontent="tvshows",
                         text_color="0xFFEB7600", extra="series", fanart=fanart_host, url=url_series,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv.png"))
    itemlist.append(Item(channel=__chanel__, action="sub_filtrar", title="     Filtrar series por género",
                         text_color="0xFFEB7600", extra="series", fanart=fanart_host, url=url_series,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv_filtrar.png"))
    itemlist.append(Item(channel=__chanel__, action="search", title="     Buscar series por título",
                         text_color="0xFFEB7600", extra="series", fanart=fanart_host, url=url_series,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv_buscar.png"))
    itemlist.append(Item(channel=__chanel__, action="listado", title="     Ultimos episodios actualizados",
                         text_color="0xFFEB7600", extra="series_novedades", fanart=fanart_host,
                         url=urlparse.urljoin(__url_base__, "plugins/ultimos-capitulos-updated.php"),
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv.png"))

    return itemlist


def sub_filtrar(item):
    logger.info()
    itemlist = []
    generos = ("acción", "animación", "aventura", "ciencia ficción", "comedia", "crimen",
               "documental", "drama", "familia", "fantasía", "guerra", "historia", "misterio",
               "música", "musical", "romance", "terror", "thriller", "western")
    thumbnail = ('https://d12.usercdn.com/i/02278/spvnq8hghtok.jpg',
                 'https://d12.usercdn.com/i/02278/olhbpe7phjas.jpg',
                 'https://d12.usercdn.com/i/02278/8xm23q2vewtt.jpg',
                 'https://d12.usercdn.com/i/02278/o4vuvd7q4bau.jpg',
                 'https://d12.usercdn.com/i/02278/v7xq7k9bj3dh.jpg',
                 'https://d12.usercdn.com/i/02278/yo5uj9ff7jmg.jpg',
                 'https://d12.usercdn.com/i/02278/ipeodwh6vw6t.jpg',
                 'https://d12.usercdn.com/i/02278/0c0ra1wb11ro.jpg',
                 'https://d12.usercdn.com/i/02278/zn85t6f2oxdv.jpg',
                 'https://d12.usercdn.com/i/02278/ipk94gsdqzwa.jpg',
                 'https://d12.usercdn.com/i/02278/z5hsi6fr4yri.jpg',
                 'https://d12.usercdn.com/i/02278/nq0jvyp7vlb9.jpg',
                 'https://d12.usercdn.com/i/02278/tkbe7p3rjmps.jpg',
                 'https://d12.usercdn.com/i/02278/is60ge4zv1ve.jpg',
                 'https://d12.usercdn.com/i/02278/86ubk310hgn8.jpg',
                 'https://d12.usercdn.com/i/02278/ph1gfpgtljf7.jpg',
                 'https://d12.usercdn.com/i/02278/bzp3t2edgorg.jpg',
                 'https://d12.usercdn.com/i/02278/31i1xkd8m30b.jpg',
                 'https://d12.usercdn.com/i/02278/af05ulgs20uf.jpg')

    if item.extra == "movie":
        viewcontent = "movies"
    else:
        viewcontent = "tvshows"

    for g, t in zip(generos, thumbnail):
        itemlist.append(item.clone(action="listado", title=g.capitalize(), filtro=("genero", g), thumbnail=t,
                                   viewcontent=viewcontent))

    return itemlist


def search(item, texto):
    logger.info("search:" + texto)
    # texto = texto.replace(" ", "+")
    item.filtro = ("search", texto.lower())
    try:
        return listado(item)
        # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = urlparse.urljoin(__url_base__, "plugins/ultimas-peliculas-updated.php")
            item.extra = "movie"

        elif categoria == 'infantiles':
            item.url = urlparse.urljoin(__url_base__, "plugins/ultimas-peliculas-updated.php")
            item.filtro = ("genero", "animación")
            item.extra = "movie"

        elif categoria == 'series':
            item.url = urlparse.urljoin(__url_base__, "plugins/ultimos-capitulos-updated.php")
            item.extra = "series_novedades"

        else:
            return []

        item.action = "listado"
        itemlist = listado(item)
        if itemlist[-1].action == "listado":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def listado(item):
    logger.info()
    itemlist = []

    try:
        data_dict = jsontools.load(httptools.downloadpage(item.url).data)
    except:
        return itemlist  # Devolvemos lista vacia

    # Filtrado y busqueda
    if item.filtro:
        for i in data_dict["result"][:]:
            if (item.filtro[0] == "genero" and item.filtro[1] not in i['genre'].lower()) or \
                    (item.filtro[0] == "search" and item.filtro[1] not in i['title'].lower()):
                data_dict["result"].remove(i)

    if not item.page:
        item.page = 0

    offset = int(item.page) * 30
    limit = offset + 30

    for i in data_dict["result"][offset:limit]:
        infoLabels = InfoLabels()
        idioma = ''

        if item.extra == "movie":
            action = "findvideos"
            # viewcontent = 'movies'
            infoLabels["title"] = i["title"]
            title = '%s (%s)' % (i["title"], i['year'])
            url = urlparse.urljoin(__url_base__, "ver-pelicula-online/" + str(i["id"]))

        elif item.extra == "series":
            action = "get_temporadas"
            # viewcontent = 'seasons'
            title = i["title"]
            infoLabels['tvshowtitle'] = i["title"]
            url = urlparse.urljoin(__url_base__, "episodio-online/" + str(i["id"]))

        else:  # item.extra=="series_novedades":
            action = "findvideos"
            # viewcontent = 'episodes'
            infoLabels['tvshowtitle'] = i["title"]
            infoLabels['season'] = i['season']
            infoLabels['episode'] = i['episode'].zfill(2)
            flag = scrapertools.find_single_match(i["label"], '(\s*\<img src=.*\>)')
            idioma = i["label"].replace(flag, "")
            title = '%s %sx%s (%s)' % (i["title"], infoLabels["season"], infoLabels["episode"], idioma)
            url = urlparse.urljoin(__url_base__, "episodio-online/" + str(i["id"]))

        if i.has_key("poster") and i["poster"]:
            thumbnail = re.compile("/w\d{3}/").sub("/w500/", i["poster"])
        else:
            thumbnail = item.thumbnail
        if i.has_key("background") and i["background"]:
            fanart = i["background"]
        else:
            fanart = item.fanart

        # Rellenamos el diccionario de infoLabels
        infoLabels['title_id'] = i['id']  # title_id: identificador de la pelicula/serie en pepecine.com
        if i['genre']: infoLabels['genre'] = i['genre']
        if i['year']: infoLabels['year'] = i['year']
        # if i['tagline']: infoLabels['plotoutline']=i['tagline']
        if i['plot']:
            infoLabels['plot'] = i['plot']
        else:
            infoLabels['plot'] = ""
        if i['runtime']: infoLabels['duration'] = int(i['runtime']) * 60
        if i['imdb_rating']:
            infoLabels['rating'] = i['imdb_rating']
        elif i['tmdb_rating']:
            infoLabels['rating'] = i['tmdb_rating']
        if i['tmdb_id']: infoLabels['tmdb_id'] = i['tmdb_id']
        if i['imdb_id']: infoLabels['imdb_id'] = i['imdb_id']

        newItem = Item(channel=item.channel, action=action, title=title, url=url, extra=item.extra,
                       fanart=fanart, thumbnail=thumbnail, viewmode="movie_with_plot",  # viewcontent=viewcontent,
                       language=idioma, text_color="0xFFFFCE9C", infoLabels=infoLabels)
        newItem.year = i['year']
        newItem.contentTitle = i['title']
        if 'season' in infoLabels and infoLabels['season']:
            newItem.contentSeason = infoLabels['season']
        if 'episode' in infoLabels and infoLabels['episode']:
            newItem.contentEpisodeNumber = infoLabels['episode']
        itemlist.append(newItem)

    # Obtenemos los datos basicos mediante multihilos
    tmdb.set_infoLabels(itemlist)

    # Paginacion
    if len(data_dict["result"]) > limit:
        itemlist.append(item.clone(text_color="0xFF994D00", title=">> Pagina siguiente >>", page=item.page + 1))

    return itemlist


def get_temporadas(item):
    logger.info()

    itemlist = []
    infoLabels = {}

    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url).data)
    patron = 'vars.title =(.*?)};'
    try:
        data_dict = jsontools.load(scrapertools.get_match(data, patron) + '}')
    except:
        return itemlist  # Devolvemos lista vacia

    if item.extra == "serie_add":
        itemlist = get_episodios(item)

    else:
        if len(data_dict["season"]) == 1:
            # Si solo hay una temporada ...
            item.infoLabels['season'] = data_dict["season"][0]["number"]
            itemlist = get_episodios(item)

        else:  # ... o si hay mas de una temporada
            item.viewcontent = "seasons"
            data_dict["season"].sort(key=lambda x: (x['number']))  # ordenamos por numero de temporada
            for season in data_dict["season"]:
                # filtramos enlaces por temporada
                enlaces = filter(lambda l: l["season"] == season['number'], data_dict["link"])
                if enlaces:
                    item.infoLabels['season'] = season['number']
                    title = '%s Temporada %s' % (item.title, season['number'])

                    itemlist.append(item.clone(action="get_episodios", title=title,
                                               text_color="0xFFFFCE9C", viewmode="movie_with_plot"))

                    # Obtenemos los datos de todas las temporadas mediante multihilos
                    tmdb.set_infoLabels(itemlist)

        if config.get_videolibrary_support() and itemlist:
            infoLabels = {'tmdb_id': item.infoLabels['tmdb_id'], 'tvdb_id': item.infoLabels['tvdb_id'],
                          'imdb_id': item.infoLabels['imdb_id']}
            itemlist.append(
                Item(channel=item.channel, title="Añadir esta serie a la videoteca", text_color="0xFFe5ffcc",
                     action="add_serie_to_library", extra='get_episodios###serie_add', url=item.url,
                     contentSerieName=data_dict["title"], infoLabels=infoLabels,
                     thumbnail='https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv.png'))

    return itemlist


def get_episodios(item):
    logger.info()
    itemlist = []
    # infoLabels = item.infoLabels

    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url).data)
    patron = 'vars.title =(.*?)};'
    try:
        data_dict = jsontools.load(scrapertools.get_match(data, patron) + '}')
    except:
        return itemlist  # Devolvemos lista vacia

    # Agrupar enlaces por episodios temXcap
    temXcap_dict = {}
    for link in data_dict['link']:
        try:
            season = str(int(link['season']))
            episode = str(int(link['episode'])).zfill(2)
        except:
            continue

        if int(season) != item.infoLabels["season"] and item.extra != "serie_add":
            # Descartamos episodios de otras temporadas, excepto si los queremos todos
            continue

        title_id = link['title_id']
        id = season + "x" + episode
        if id in temXcap_dict:
            l = temXcap_dict[id]
            l.append(link)
            temXcap_dict[id] = l
        else:
            temXcap_dict[id] = [link]

    # Ordenar lista de enlaces por temporada y capitulo
    temXcap_list = temXcap_dict.items()
    temXcap_list.sort(key=lambda x: (int(x[0].split("x")[0]), int(x[0].split("x")[1])))
    for episodio in temXcap_list:
        title = '%s (%s)' % (item.contentSerieName, episodio[0])
        item.infoLabels['season'], item.infoLabels['episode'] = episodio[0].split('x')
        itemlist.append(item.clone(action="findvideos", title=title,
                                   viewmode="movie_with_plot", text_color="0xFFFFCE9C"))

    if item.extra != "serie_add":
        # Obtenemos los datos de todos los capitulos de la temporada mediante multihilos
        tmdb.set_infoLabels(itemlist)
        for i in itemlist:
            # Si el capitulo tiene nombre propio añadirselo al titulo del item
            title = "%s: %s" % (i.title, i.infoLabels['title'])
            i.title = title

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url).data)
    patron = 'vars.title =(.*?)};'
    try:
        data_dict = jsontools.load(scrapertools.get_match(data, patron) + '}')
    except:
        return itemlist  # Devolvemos lista vacia

    lista_servers = servertools.get_servers_list()

    for link in data_dict["link"]:
        if item.contentType == 'episode' \
                and (item.contentSeason != link['season'] or item.contentEpisodeNumber != link['episode']):
            # Si buscamos enlaces de un episodio descartamos los q no sean de este episodio
            continue

        url = link["url"]
        flag = scrapertools.find_single_match(link["label"], '(\s*\<img src=.*\>)')
        idioma = link["label"].replace(flag, "")
        if link["quality"] != "?":
            calidad = (' [' + link["quality"] + ']')
        else:
            calidad = ""
        video = find_videos(link["url"], lista_servers)

        if video["servidor"] != "":
            servidor = video["servidor"]
            url = video["url"]
            title = "Ver en " + servidor.capitalize() + calidad + ' (' + idioma + ')'
            itemlist.append(item.clone(action="play", viewmode="list", server=servidor, title=title,
                                       text_color="0xFF994D00", url=url, folder=False))

    if config.get_videolibrary_support() and itemlist and item.contentType == "movie":
        infoLabels = {'tmdb_id': item.infoLabels['tmdb_id'],
                      'title': item.infoLabels['title']}
        itemlist.append(Item(channel=item.channel, title="Añadir esta película a la videoteca",
                             action="add_pelicula_to_library", url=item.url, infoLabels=infoLabels,
                             text_color="0xFFe5ffcc",
                             thumbnail='https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv.png'))

    return itemlist


def find_videos(url, lista_servers):
    # logger.info()
    ret = {'titulo': "",
           'url': "",
           'servidor': ""}

    # Ejecuta el find_videos en cada servidor hasta que encuentra una coicidencia
    for serverid in lista_servers:
        try:
            servers_module = __import__("servers." + serverid)
            server_module = getattr(servers_module, serverid)
            devuelve = server_module.find_videos(url)

            if devuelve:
                ret["titulo"] = devuelve[0][0]
                ret["url"] = devuelve[0][1]
                ret["servidor"] = devuelve[0][2]
                # reordenar el listado, es probable q el proximo enlace sea del mismo servidor
                lista_servers.remove(serverid)
                lista_servers.insert(0, serverid)
                break

        except ImportError:
            logger.error("No existe conector para #" + serverid + "#")
            # import traceback
            # logger.info(traceback.format_exc())
        except:
            logger.error("Error en el conector #" + serverid + "#")
            import traceback
            logger.error(traceback.format_exc())

    return ret


def episodios(item):
    # Necesario para las actualizaciones automaticas
    return get_temporadas(Item(channel=__chanel__, url=item.url, show=item.show, extra="serie_add"))
