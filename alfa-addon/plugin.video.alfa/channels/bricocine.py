# -*- coding: utf-8 -*-

import os
import re
import urllib
import urllib2

import xbmcgui
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


## Cargar los datos con la librería 'requests'
def get_page(url):
    from lib import requests
    response = requests.get(url)
    return response.content


def browser(url):
    import mechanize

    # Utilizamos Browser mechanize para saltar problemas con la busqueda en bing
    br = mechanize.Browser()
    # Browser options
    br.set_handle_equiv(False)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(False)
    br.set_handle_robots(False)
    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    # br.set_debug_http(True)
    # br.set_debug_redirects(True)
    # br.set_debug_responses(True)

    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent',
                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/7.1.7 Safari/537.85.16')]
    # br.addheaders =[('Cookie','SRCHD=AF=QBRE; domain=.bing.com; expires=25 de febrero de 2018 13:00:28 GMT+1; MUIDB=3B942052D204686335322894D3086911; domain=www.bing.com;expires=24 de febrero de 2018 13:00:28 GMT+1')]
    # Open some site, let's pick a random one, the first that pops in mind
    r = br.open(url)
    response = r.read()
    print response
    if not ".ftrH,.ftrHd,.ftrD>" in response:
        r = br.open("http://anonymouse.org/cgi-bin/anon-www.cgi/" + url)
        print "prooooxy"
        response = r.read()
    return response


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(
        Item(channel=item.channel, title="[COLOR sandybrown][B]Pelis MicroHD[/B][/COLOR]", action="peliculas",
             url="http://www.bricocine.com/c/hd-microhd/", thumbnail="http://s6.postimg.org/5vgi38jf5/HD_brico10.jpg",
             fanart="http://s16.postimg.org/6g9tc2nyt/brico_pelifan.jpg"))
    itemlist.append(
        Item(channel=item.channel, title="[COLOR sandybrown][B]Pelis Bluray-Rip[/B][/COLOR]", action="peliculas",
             url="http://www.bricocine.com/c/bluray-rip/", thumbnail="http://s6.postimg.org/5w82dorpt/blueraybrico.jpg",
             fanart="http://i59.tinypic.com/11rdnjm.jpg"))
    itemlist.append(
        Item(channel=item.channel, title="[COLOR sandybrown][B]Pelis DVD-Rip[/B][/COLOR]", action="peliculas",
             url="http://www.bricocine.com/c/dvdrip/", thumbnail="http://s6.postimg.org/d2dlld4y9/dvd2.jpg",
             fanart="http://s6.postimg.org/hcehbq5w1/brico_blue_fan.jpg"))
    itemlist.append(Item(channel=item.channel, title="[COLOR sandybrown][B]Pelis 3D[/B][/COLOR]", action="peliculas",
                         url="http://www.bricocine.com/c/3d/",
                         thumbnail="http://www.eias3d.com/wp-content/uploads/2011/07/3d2_5.png",
                         fanart="http://s6.postimg.org/u18rvec0h/bric3dd.jpg"))
    import xbmc
    ###Para musica(si hay) y borra customkeys
    if xbmc.Player().isPlaying():
        xbmc.executebuiltin('xbmc.PlayMedia(Stop)')
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    try:
        os.remove(KEYMAPDESTFILE)
        print "Custom Keyboard.xml borrado"
        os.remove(TESTPYDESTFILE)
        print "Testpy borrado"
        os.remove(REMOTEDESTFILE)
        print "Remote borrado"
        os.remove(APPCOMMANDDESTFILE)
        print "Appcommand borrado"
        xbmc.executebuiltin('Action(reloadkeymaps)')
    except Exception as inst:
        xbmc.executebuiltin('Action(reloadkeymaps)')
        print "No hay customs"

    itemlist.append(Item(channel=item.channel, title="[COLOR sandybrown][B]Series[/B][/COLOR]", action="peliculas",
                         url="http://www.bricocine.com/c/series",
                         thumbnail="http://img0.mxstatic.com/wallpapers/bc795faa71ba7c490fcf3961f3b803bf_large.jpeg",
                         fanart="http://s6.postimg.org/z1ath370x/bricoseries.jpg", extra="Series"))
    import xbmc
    if xbmc.Player().isPlaying():
        print "PLAYIIING"
        xbmc.executebuiltin('xbmc.PlayMedia(Stop)')
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    SEARCHDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
    TRAILERDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "trailer.txt")
    try:
        os.remove(KEYMAPDESTFILE)
        print "Custom Keyboard.xml borrado"
        os.remove(TESTPYDESTFILE)
        print "Testpy borrado"
        os.remove(REMOTEDESTFILE)
        print "Remote borrado"
        os.remove(APPCOMMANDDESTFILE)
        print "Appcommand borrado"
        xbmc.executebuiltin('Action(reloadkeymaps)')
    except Exception as inst:
        xbmc.executebuiltin('Action(reloadkeymaps)')
        print "No hay customs"
    try:
        os.remove(SEARCHDESTFILE)
        print "Custom search.txt borrado"
    except:
        print "No hay search.txt"

    try:
        os.remove(TRAILERDESTFILE)
        print "Custom Trailer.txt borrado"
    except:
        print "No hay Trailer.txt"
    itemlist.append(Item(channel=item.channel, title="[COLOR sandybrown][B]Buscar[/B][/COLOR]", action="search", url="",
                         thumbnail="http://fc04.deviantart.net/fs70/i/2012/285/3/2/poltergeist___tv_wallpaper_by_elclon-d5hmmlp.png",
                         fanart="http://s6.postimg.org/f44w84o5t/bricosearch.jpg", extra="search"))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://www.bricocine.com/index.php/?s=%s" % texto

    try:
        return peliculas(item, texto.replace("+", " "))
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item, texto=""):
    logger.info()
    itemlist = []

    # Borra customkeys
    import xbmc
    if xbmc.Player().isPlaying():
        xbmc.executebuiltin('xbmc.PlayMedia(Stop)')

    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    TRAILERDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "trailer.txt")

    try:
        os.remove(KEYMAPDESTFILE)
        print "Custom Keyboard.xml borrado"
        os.remove(TESTPYDESTFILE)
        print "Testpy borrado"
        os.remove(REMOTEDESTFILE)
        print "Remote borrado"
        os.remove(APPCOMMANDDESTFILE)
        print "App borrado"
        xbmc.executebuiltin('Action(reloadkeymaps)')
    except Exception as inst:
        xbmc.executebuiltin('Action(reloadkeymaps)')
        print "No hay customs"

    try:
        os.remove(TRAILERDESTFILE)
        print "Trailer.txt borrado"
    except:
        print "No hay Trailer.txt"

    # Descarga la página
    data = get_page(item.url)
    data = re.sub(r"amp;", "", data)
    '''
    <div class="post-10888 post type-post status-publish format-standard hentry category-the-leftovers
        tag-ciencia-ficcion tag-drama tag-fantasia tag-misterio">
        <div class="entry">
            <a href="http://www.bricocine.com/10888/leftovers-temporada-1/">
                <img src="http://www.bricocine.com/wp-content/plugins/wp_movies/files/thumb_185_the_leftovers_.jpg"
                    alt="The Leftovers " />
            </a>
        </div>
        <div class="entry-meta">
            <div class="clearfix">
                <div itemprop="aggregateRating" itemscope itemtype="http://schema.org/AggregateRating" class="rating"
                    title="Puntos IMDB: 7.4">
                    <div class="rating-stars imdb-rating">
                        <div class="stars" style="width:74%"></div>
                    </div>
                    <div itemprop="ratingValue" class="rating-number"> 7.4</div>
                </div>
                <div itemprop="aggregateRating" itemscope itemtype="http://schema.org/AggregateRating" class="rating"
                    title="Puntos Bricocine: 6.2">
                    <div class="rating-stars brico-rating">
                        <div class="stars" style="width:62%"></div>
                    </div>
                    <div itemprop="ratingValue" class="rating-number"> 6.2</div>
                </div>
                <span class="vcard author none"> Publicado por
                    <a class="fn" href="" rel="author" target="_blank"></a>
                </span>
                <span class="date updated none">2014-10-07T23:36:17+00:00</span>
            </div>
        </div>
        <h2 class="title2 entry-title">
            <a href="http://www.bricocine.com/10888/leftovers-temporada-1/"> The Leftovers  &#8211; Temporada 1 </a>
        </h2>
    </div>
    '''
    patron = 'format-standard hentry category(.*?)">.*?'
    patron += '<div class="entry"> '
    patron += '<a href="(.*?)"> '
    patron += '<img src="(.*?)".*?'
    patron += 'class="rating-number">([^<]+)</div></div>.*?'
    patron += '<h2 class="title2 entry-title">.*?"> ([^<]+).*?</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches) == 0 and texto == "":
        itemlist.append(Item(channel=item.channel, title="[COLOR gold][B]No hay resultados...[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                             fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", folder=False))

    for tag, scrapedurl, scrapedthumbnail, scrapedcreatedate, scrapedtitle in matches:
        # fix para el buscador para que no muestre entradas con texto que no es correcto
        if texto.lower() not in scrapedtitle.lower():
            continue

        if scrapedthumbnail == "":
            scrapedthumbnail = "http://s6.postimg.org/aseij0y4x/briconoimage.png"
        title = scrapedtitle
        # Separa entre series y peliculas
        if not item.extra == "Series" and "index" not in item.url:
            title = re.sub(r"\(.*?\) |\[.*?\] |&#.*?;", "", title)

            try:
                scrapedyear = scrapertools.get_match(scrapedurl, '.*?www.bricocine.com/.*?/.*?(\d\d\d\d)')
            except:
                scrapedyear = ""
            title_fan = title.strip()

        if item.extra == "Series" and "index" not in item.url:
            title = re.sub(r"&#.*?;|Temporada.*?\d+ | Todas las Temporadas |\[.*?\]|\([0-9].*?\)|¡|!", "", title)
            title_fan = title.strip()
            scrapedyear = ""
        # Diferencia si viene de la búsqueda
        if "index" in item.url:
            # Se usa tag en busqueda para diferenciar series no bien tipificadas
            if ("3d" not in tag and not "dvdrip" in tag and not "bluray-rip" in tag and not "hd-microhd" in tag and
                    not "bdrip" in tag and not "estrenos" in tag and not "latino" in tag and not "hannibal" in tag):
                title = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|&#.*?;|\(.*?\)|\d\d\d\d", "", title)
                title_fan = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|&#.*?;|Temporada.*?\d+| Todas Las Temp.*?das", "", title)
                title = title.replace("Temporada", "[COLOR green]Temporada[/COLOR]")
                title = title.replace(title, "[COLOR white]" + title + "[/COLOR]")

                import xbmc
                # Crea el archivo search.txt.Regula el buen funcionaiento de la música y volver atras en la busqueda
                SEARCHDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
                urllib.urlretrieve(
                    "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/search.txt",
                    SEARCHDESTFILE)
                item.extra = "Series"
                scrapedyear = ""

            else:
                title = re.sub(r"\(.*?\)|\[.*?\]|&#.*?;|", "", scrapedtitle)
                title = title.strip()
                try:
                    scrapedyear = scrapertools.get_match(scrapedurl, '.*?www.bricocine.com/.*?/.*?(\d\d\d\d)')
                except:
                    scrapedyear = ""

                title_fan = title.strip()
                if item.extra == "Series":
                    item.extra = "peliculas"
                # print item.extra
                # Crea el archivo search.txt.Regula el buen funcionaiento de la música y volver atras en la busqueda
                import xbmc
                SEARCHDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
                urllib.urlretrieve(
                    "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/search.txt",
                    SEARCHDESTFILE)

        scrapedcreatedate = scrapedcreatedate.replace(scrapedcreatedate,
                                                      "[COLOR sandybrown][B]" + scrapedcreatedate + "[/B][/COLOR]")
        title = title.replace(title, "[COLOR white]" + title + "[/COLOR]")
        title = title + "(Puntuación:" + scrapedcreatedate + ")"
        show = title_fan + "|" + scrapedyear
        itemlist.append(Item(channel=item.channel, title=title, url=scrapedurl, action="fanart",
                             thumbnail=scrapedthumbnail, fanart="http://s15.postimg.org/id6ec47vf/bricocinefondo.jpg",
                             show=show, extra=item.extra, folder=True))

    # Paginación
    # <span class='current'>1</span><a href='http://www.bricocine.com/c/hd-microhd/page/2/'

    # Si falla no muestra ">> Página siguiente"
    try:
        next_page = scrapertools.get_match(data, "<span class='current'>\d+</span><a href='([^']+)'")
        title = "[COLOR red]Pagina siguiente>>[/COLOR]"
        itemlist.append(Item(channel=item.channel, title=title, url=next_page, action="peliculas",
                             fanart="http://s15.postimg.org/id6ec47vf/bricocinefondo.jpg", extra=item.extra,
                             thumbnail="http://s7.postimg.org/w2e0nr7hn/pdksiguiente.jpg", folder=True))
    except:
        pass

    return itemlist


def fanart(item):
    # Vamos a sacar todos los fanarts y arts posibles
    logger.info()
    itemlist = []
    url = item.url
    data = get_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|\[.*?\]|&nbsp;", "", data)
    title = item.show.split("|")[0].strip()
    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')

    print "ya esta bien"
    print item.extra
    title = title.replace('[BDRIP]', '')
    title = title.replace('á', 'a')
    title = title.replace('Á', 'A')
    title = title.replace('é', 'e')
    title = title.replace('É', 'E')
    title = title.replace('í', 'i')
    title = title.replace('Í', 'i')
    title = title.replace('ó', 'o')
    title = title.replace('Ó', 'o')
    title = title.replace('ú', 'u')
    title = title.replace('Ú', 'U')
    title = title.replace('ñ', 'n')
    title = title.replace('Ñ', 'N')

    print title
    if "temporada" in item.url or "Temporada" in item.show.split("|")[0] or item.extra == "Series":
        import xbmc
        # Establece destino customkey
        SEARCHDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
        TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
        KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
        REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
        APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
        TRAILERDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "trailer.txt")

        title = re.sub(r"&#.*?;|Temporada.*?\d+ | Todas las Temporadas ", "", title)
        title = title.replace("&", "y")
        if "Los originales" in title:
            title = (translate(title, "en"))
        if title == "Hope":
            title = "Raising hope"
        if title == "Invisibles":
            title = "The whispers"
        if title == "Secretos y mentiras":
            title = "Secrets and lies"
        if title == "Brotherhood":
            title = title + " " + "comedy"
        if title == "Las Palomas de Judea":
            title = "the dovekeepers"
        if title == "90210 Sensacion de vivir":
            title = "90210"

        plot = title
        title_tunes = re.sub(r"\(.*?\)", "", title)
        title_tunes = (translate(title_tunes, "en"))
        ###Prepara customkeys y borra cuando vuelve
        import xbmc
        if not xbmc.Player().isPlaying() and not os.path.exists(TRAILERDESTFILE):

            TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
            KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
            REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
            APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
            try:
                os.remove(KEYMAPDESTFILE)
                print "Custom Keyboard.xml borrado"
                os.remove(TESTPYDESTFILE)
                print "Testpy borrado"
                os.remove(REMOTEDESTFILE)
                print "Remote borrado"
                os.remove(APPCOMMANDDESTFILE)
                print "Appcommand borrado"
                xbmc.executebuiltin('Action(reloadkeymaps)')
            except Exception as inst:
                xbmc.executebuiltin('Action(reloadkeymaps)')
                print "No hay customs"

                try:
                    ###Busca música serie y caraga customkey. En la vuelta evita busqueda si ya suena música
                    url_bing = "http://www.bing.com/search?q=%s+theme+song+site:televisiontunes.com" % title_tunes.replace(
                        ' ', '+')
                    # Llamamos al browser de mechanize. Se reitera en todas las busquedas bing
                    data = browser(url_bing)

                    try:
                        subdata_tvt = scrapertools.get_match(data, '<li class="b_algo">(.*?)h="ID')
                    except:
                        pass
                    try:
                        url_tvt = scrapertools.get_match(subdata_tvt, '<a href="(.*?)"')
                    except:
                        url_tvt = ""

                    if "-theme-songs.html" in url_tvt:
                        url_tvt = ""
                    if "http://m.televisiontunes" in url_tvt:
                        url_tvt = url_tvt.replace("http://m.televisiontunes", "http://televisiontunes")

                    data = scrapertools.cachePage(url_tvt)
                    song = scrapertools.get_match(data, '<form name="song_name_form">.*?type="hidden" value="(.*?)"')
                    song = song.replace(" ", "%20")
                    print song
                    xbmc.executebuiltin('xbmc.PlayMedia(' + song + ')')
                    import xbmc, time
                    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
                    urllib.urlretrieve(
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/test.py",
                        TESTPYDESTFILE)
                    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")

                    urllib.urlretrieve(
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customkey.xml",
                        KEYMAPDESTFILE)
                    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
                    urllib.urlretrieve(
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/remote.xml",
                        REMOTEDESTFILE)
                    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
                    urllib.urlretrieve(
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customapp.xml",
                        APPCOMMANDDESTFILE)

                    xbmc.executebuiltin('Action(reloadkeymaps)')

                except:
                    pass
        try:
            os.remove(TRAILERDESTFILE)
            print "Trailer.txt borrado"
        except:
            print "No hay Trailer.txt"

        if os.path.exists(SEARCHDESTFILE):
            try:
                os.remove(KEYMAPDESTFILE)
                print "Custom Keyboard.xml borrado"
                os.remove(TESTPYDESTFILE)
                print "Testpy borrado"
                os.remove(REMOTEDESTFILE)
                print "Remote borrado"
                os.remove(APPCOMMANDDESTFILE)
                print "Appcommand borrado"
                os.remove(SEARCHDESTFILE)
                print "search.txt borrado"
                xbmc.executebuiltin('Action(reloadkeymaps)')
            except Exception as inst:
                xbmc.executebuiltin('Action(reloadkeymaps)')
                print "No hay customs"
        ###Busqueda en bing el id de imdb de la serie
        urlbing_imdb = "http://www.bing.com/search?q=%s+tv+serie+site:imdb.com" % title.replace(' ', '+')
        data = browser(urlbing_imdb)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        try:
            subdata_imdb = scrapertools.get_match(data, '<li class="b_algo">(.*?)h="ID')
        except:
            pass

        try:
            imdb_id = scrapertools.get_match(subdata_imdb, '<a href=.*?http.*?imdb.com/title/(.*?)/.*?"')
        except:
            imdb_id = ""
        ###Busca id de tvdb mediante imdb id
        urltvdb_remote = "http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=" + imdb_id + "&language=es"
        data = scrapertools.cachePage(urltvdb_remote)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        patron = '<Data><Series><seriesid>([^<]+)</seriesid>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        print matches
        if len(matches) == 0:
            ###Si no hay coincidencia busca en tvdb directamente


            if ":" in title or "(" in title:

                title = title.replace(" ", "%20")
                url_tvdb = "http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
                data = scrapertools.cachePage(url_tvdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                patron = '<Data><Series><seriesid>([^<]+)</seriesid>'
                matches = re.compile(patron, re.DOTALL).findall(data)

                if len(matches) == 0:
                    title = re.sub(r"(:.*)|\(.*?\)", "", title)
                    title = title.replace(" ", "%20")

                    url_tvdb = "http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
                    data = scrapertools.cachePage(url_tvdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                    patron = '<Data><Series><seriesid>([^<]+)</seriesid>'
                    matches = re.compile(patron, re.DOTALL).findall(data)

                    if len(matches) == 0:
                        postertvdb = item.thumbnail
                        extra = "http://s6.postimg.org/6flcihb69/brico1sinopsis.png"
                        show = "http://s6.postimg.org/4asrg755b/bricotvshows2.png"
                        fanart_info = "http://s6.postimg.org/77fsghaz3/bricotvshows4.jpg"
                        fanart_trailer = "http://s6.postimg.org/77fsghaz3/bricotvshows4.jpg"
                        category = ""
                        itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                             thumbnail=item.thumbnail, plot=plot,
                                             fanart="http://s6.postimg.org/77fsghaz3/bricotvshows4.jpg", extra=extra,
                                             category=category, show=show, folder=True))

            else:
                title = title.replace(" ", "%20")
                url_tvdb = "http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
                data = scrapertools.cachePage(url_tvdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                patron = '<Data><Series><seriesid>([^<]+)</seriesid>'
                matches = re.compile(patron, re.DOTALL).findall(data)
                if len(matches) == 0:
                    postertvdb = item.thumbnail
                    extra = "http://s6.postimg.org/6flcihb69/brico1sinopsis.png"
                    show = "http://s6.postimg.org/4asrg755b/bricotvshows2.png"
                    fanart_info = "http://s6.postimg.org/77fsghaz3/bricotvshows4.jpg"
                    fanart_trailer = "http://s6.postimg.org/77fsghaz3/bricotvshows4.jpg"
                    category = ""
                    itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                         thumbnail=item.thumbnail, plot=plot,
                                         fanart="http://s6.postimg.org/77fsghaz3/bricotvshows4.jpg", extra=extra,
                                         category=category, show=show, folder=True))

        # 1ºfanart mediante id tvdb

        for id in matches:
            category = id
            id_serie = id
            urltvdb_banners = "http://thetvdb.com/api/1D62F2F90030C444/series/" + id_serie + "/banners.xml"

            data = scrapertools.cachePage(urltvdb_banners)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            patron = '<Banners><Banner>.*?<VignettePath>(.*?)</VignettePath>'
            matches = re.compile(patron, re.DOTALL).findall(data)
            try:
                # intenta poster tvdb
                postertvdb = scrapertools.get_match(data, '<Banners><Banner>.*?<BannerPath>posters/(.*?)</BannerPath>')
                postertvdb = "http://thetvdb.com/banners/_cache/posters/" + postertvdb
            except:
                postertvdb = item.thumbnail

            if len(matches) == 0:
                extra = "http://s6.postimg.org/6flcihb69/brico1sinopsis.png"
                show = "http://s6.postimg.org/4asrg755b/bricotvshows2.png"
                fanart_info = "http://s6.postimg.org/77fsghaz3/bricotvshows4.jpg"
                fanart_trailer = "http://s6.postimg.org/77fsghaz3/bricotvshows4.jpg"
                itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                     thumbnail=postertvdb, fanart="http://s6.postimg.org/77fsghaz3/bricotvshows4.jpg",
                                     plot=plot, category=category, extra=extra, show=show, folder=True))

            for fan in matches:
                fanart = "http://thetvdb.com/banners/" + fan
                fanart_1 = fanart
                # Busca fanart para info, fanart para trailer y 2ºfanart
                patron = '<Banners><Banner>.*?<BannerPath>.*?</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>'
                matches = re.compile(patron, re.DOTALL).findall(data)
                if len(matches) == 0:
                    fanart_info = fanart_1
                    fanart_trailer = fanart_1
                    fanart_2 = fanart_1
                    show = fanart_1
                    extra = postertvdb
                    itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                         thumbnail=postertvdb, fanart=fanart_1, plot=plot, category=category,
                                         extra=extra, show=show, folder=True))
                for fanart_info, fanart_trailer, fanart_2 in matches:
                    fanart_info = "http://thetvdb.com/banners/" + fanart_info
                    fanart_trailer = "http://thetvdb.com/banners/" + fanart_trailer
                    fanart_2 = "http://thetvdb.com/banners/" + fanart_2
            # Busqueda de todos loas arts posibles
            for id in matches:
                url_fanartv = "http://webservice.fanart.tv/v3/tv/" + id_serie + "?api_key=dffe90fba4d02c199ae7a9e71330c987"
                data = scrapertools.cachePage(url_fanartv)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                patron = '"clearlogo":.*?"url": "([^"]+)"'
                matches = re.compile(patron, re.DOTALL).findall(data)
                if '"tvposter"' in data:
                    tvposter = scrapertools.get_match(data, '"tvposter":.*?"url": "([^"]+)"')
                if '"tvbanner"' in data:
                    tvbanner = scrapertools.get_match(data, '"tvbanner":.*?"url": "([^"]+)"')
                if '"tvthumb"' in data:
                    tvthumb = scrapertools.get_match(data, '"tvthumb":.*?"url": "([^"]+)"')
                if '"hdtvlogo"' in data:
                    hdtvlogo = scrapertools.get_match(data, '"hdtvlogo":.*?"url": "([^"]+)"')
                if '"hdclearart"' in data:
                    hdtvclear = scrapertools.get_match(data, '"hdclearart":.*?"url": "([^"]+)"')
                if len(matches) == 0:
                    item.thumbnail = postertvdb
                    if '"hdtvlogo"' in data:
                        if "showbackground" in data:

                            if '"hdclearart"' in data:
                                thumbnail = hdtvlogo
                                extra = hdtvclear
                                show = fanart_2
                            else:
                                thumbnail = hdtvlogo
                                extra = thumbnail
                                show = fanart_2
                            itemlist.append(
                                Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                     server="torrent", thumbnail=thumbnail, plot=plot, fanart=fanart_1,
                                     category=category, extra=extra, show=show, folder=True))


                        else:
                            if '"hdclearart"' in data:
                                thumbnail = hdtvlogo
                                extra = hdtvclear
                                show = fanart_2
                            else:
                                thumbnail = hdtvlogo
                                extra = thumbnail
                                show = fanart_2

                            itemlist.append(
                                Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                     server="torrent", thumbnail=thumbnail, plot=plot, fanart=fanart_1, extra=extra,
                                     show=show, category=category, folder=True))
                    else:
                        extra = "http://s6.postimg.org/6flcihb69/brico1sinopsis.png"
                        show = fanart_2
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=item.thumbnail, plot=plot, fanart=fanart_1,
                                             extra=extra, show=show, category=category, folder=True))

            for logo in matches:
                if '"hdtvlogo"' in data:
                    thumbnail = hdtvlogo
                elif not '"hdtvlogo"' in data:
                    if '"clearlogo"' in data:
                        thumbnail = logo
                else:
                    thumbnail = item.thumbnail
                if '"clearart"' in data:
                    clear = scrapertools.get_match(data, '"clearart":.*?"url": "([^"]+)"')
                    if "showbackground" in data:

                        extra = clear
                        show = fanart_2
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=thumbnail, plot=plot, fanart=fanart_1,
                                             extra=extra, show=show, category=category, folder=True))
                    else:
                        extra = clear
                        show = fanart_2
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=thumbnail, plot=plot, fanart=fanart_1,
                                             extra=extra, show=show, category=category, folder=True))

                if "showbackground" in data:

                    if '"clearart"' in data:
                        clear = scrapertools.get_match(data, '"clearart":.*?"url": "([^"]+)"')
                        extra = clear
                        show = fanart_2
                    else:
                        extra = logo
                        show = fanart_2
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=thumbnail, plot=plot, fanart=fanart_1,
                                             extra=extra, show=show, category=category, folder=True))

                if not '"clearart"' in data and not '"showbackground"' in data:
                    if '"hdclearart"' in data:
                        extra = hdtvclear
                        show = fanart_2
                    else:
                        extra = thumbnail
                        show = fanart_2
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                         server="torrent", thumbnail=thumbnail, plot=plot, fanart=fanart_1, extra=extra,
                                         show=show, category=category, folder=True))

    else:
        ###Películas
        title = title.decode('utf8').encode('latin1')
        title = title.replace("&", " y ")
        if title == "JustiCia":
            title = "Justi&cia"
        if title == "El milagro":
            title = "Miracle"
        if "La Saga Crepusculo" in title:
            title = re.sub(r"La Saga", "", title)

        year = item.show.split("|")[1]
        if "Saga" in title:
            title = title.replace('Saga completa', '')
            title = title.replace('Saga', '')
            title_collection = title.replace(" ", "+")
            url_collection = "http://api.themoviedb.org/3/search/collection?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title_collection + "+&language=es"
            data = scrapertools.cachePage(url_collection)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            try:
                id = scrapertools.get_match(data, '"page":1.*?"id":(.*?),')
            except:
                id = ""
            urlc_images = "http://api.themoviedb.org/3/collection/" + id + "?api_key=2e2160006592024ba87ccdf78c28f49f"
            data = scrapertools.cachePage(urlc_images)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            patron = '"poster_path":"(.*?)","backdrop_path":"(.*?)".*?"backdrop_path":"(.*?)".*?"backdrop_path":"(.*?)".*?"backdrop_path":"(.*?)"'
            matches = re.compile(patron, re.DOTALL).findall(data)
            scrapertools.printMatches(matches)
            if len(matches) == 0:
                posterdb = item.thumbnail
                extra = "http://s6.postimg.org/6flcihb69/brico1sinopsis.png"
                fanart_1 = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"
                fanart = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"
                fanart_info = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"
                fanart_trailer = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"
                fanart_2 = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"
            for posterdb, fanart_1, fanart_info, fanart_trailer, fanart_2 in matches:
                posterdb = "https://image.tmdb.org/t/p/original" + posterdb
                fanart_1 = "https://image.tmdb.org/t/p/original" + fanart_1
                fanart_info = "https://image.tmdb.org/t/p/original" + fanart_info
                fanart_trailer = "https://image.tmdb.org/t/p/original" + fanart_trailer
                fanart_2 = "https://image.tmdb.org/t/p/original" + fanart_2

        else:

            try:
                try:
                    ###Busqueda en Tmdb la peli por titulo y año
                    title_tmdb = title.replace(" ", "%20")
                    url_tmdb = "http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title_tmdb + "&year=" + year + "&language=es&include_adult=false"
                    data = scrapertools.cachePage(url_tmdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                    id = scrapertools.get_match(data, '"page":1.*?,"id":(.*?),')
                except:
                    if ":" in title or "(" in title:
                        title_tmdb = title.replace(" ", "%20")
                        url_tmdb = "http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title_tmdb + "&year=" + year + "&language=es&include_adult=false"
                        data = scrapertools.cachePage(url_tmdb)
                        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                        id = scrapertools.get_match(data, '"page":1.*?,"id":(.*?),')
                    else:
                        title_tmdb = title.replace(" ", "%20")
                        title_tmdb = re.sub(r"(:.*)|\(.*?\)", "", title_tmdb)
                        url_tmdb = "http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title_tmdb + "&year=" + year + "&language=es&include_adult=false"
                        data = scrapertools.cachePage(url_tmdb)
                        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                        id = scrapertools.get_match(data, '"page":1.*?,"id":(.*?),')


            except:
                ###Si no hay coincidencia realiza busqueda por bing del id Imdb
                urlbing_imdb = "http://www.bing.com/search?q=%s+%s+site:imdb.com" % (title.replace(' ', '+'), year)
                data = browser(urlbing_imdb)

                try:
                    subdata_imdb = scrapertools.get_match(data, '<li class="b_algo">(.*?)h="ID')
                    subdata_imdb = re.sub("http://anonymouse.org/cgi-bin/anon-www.cgi/", "", subdata_imdb)
                except:
                    pass

                try:
                    url_imdb = scrapertools.get_match(subdata_imdb, '<a href="([^"]+)"')
                except:
                    pass
                try:
                    id_imdb = scrapertools.get_match(url_imdb, '.*?www.imdb.com/.*?/(.*?)/')
                except:
                    pass
                try:
                    ###Busca id Tmdb mediante el id de Imdb
                    urltmdb_remote = "https://api.themoviedb.org/3/find/" + id_imdb + "?external_source=imdb_id&api_key=2e2160006592024ba87ccdf78c28f49f"

                    data = scrapertools.cachePage(urltmdb_remote)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                    id = scrapertools.get_match(data, '"movie_results".*?,"id":(\d+)')
                except:
                    id = ""

            ###Llegados aqui ya tenemos(o no) el id(Tmdb);Busca fanart_1
            urltmdb_fan1 = "http://api.themoviedb.org/3/movie/" + id + "?api_key=2e2160006592024ba87ccdf78c28f49f"
            data = scrapertools.cachePage(urltmdb_fan1)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            patron = '"adult".*?"backdrop_path":"(.*?)"'
            matches = re.compile(patron, re.DOTALL).findall(data)
            try:
                ###Prueba poster de Tmdb
                posterdb = scrapertools.get_match(data, '"adult".*?"poster_path":"(.*?)"')
                posterdb = "https://image.tmdb.org/t/p/original" + posterdb
            except:
                posterdb = item.thumbnail

            if len(matches) == 0:

                ###Si no encuentra fanart_1 en Tmdb realiza busqueda directamente en Imdb
                try:

                    urlbing_imdb = "http://www.bing.com/search?q=imdb+movie+%s+%s" % (title.replace(' ', '+'), year)

                    data = browser(urlbing_imdb)
                    try:
                        subdata_imdb = scrapertools.get_match(data, '<li class="b_algo">(.*?)h="ID')
                        subdata_imdb = re.sub("http://anonymouse.org/cgi-bin/anon-www.cgi/", "", subdata_imdb)
                    except:
                        pass
                    try:
                        url_imdb = scrapertools.get_match(subdata_imdb, '<a href="([^"]+)"')
                        url_imdb = re.sub("http://www.imdb.comhttp://anonymouse.org/cgi-bin/anon-www.cgi/", "",
                                          url_imdb)
                    except:
                        url_imdb = data
                    data = scrapertools.cachePage(url_imdb)

                    try:
                        poster_imdb = scrapertools.get_match(data, '<td rowspan="2" id="img_primary">.*?src="([^"]+)"')
                        poster_imdb = poster_imdb.replace("._.*?jpg", "._V1_SX640_SY720_.jpg")

                    except:
                        poster_imdb = posterdb

                    try:
                        url_photo = scrapertools.get_match(data,
                                                           '<div class="combined-see-more see-more">.*?<a href="([^"]+)"')
                        url_photos = "http://www.imdb.com" + url_photo
                        data = scrapertools.cachePage(url_photos)
                        try:
                            photo_imdb = scrapertools.get_match(data,
                                                                '<div class="media_index_thumb_list".*?src="([^"]+)"')
                            photo_imdb = re.sub(r"._.*?jpg", "._V1_SX1280_SY720_.jpg", photo_imdb)

                        except:
                            pass

                        try:
                            photo_imdb2 = scrapertools.get_match(data,
                                                                 '<div class="media_index_thumb_list".*?src=.*?src="([^"]+)"')
                            photo_imdb2 = re.sub(r"._.*?jpg", "._V1_SX1280_SY720_.jpg", photo_imdb2)
                        except:
                            pass
                        try:
                            photo_imdb3 = scrapertools.get_match(data,
                                                                 '<div class="media_index_thumb_list".*?src=.*?src=.*?src="([^"]+)"')
                            photo_imdb3 = re.sub(r"._.*?jpg", "._V1_SX1280_SY720_.jpg", photo_imdb3)
                        except:
                            pass
                        try:
                            photo_imdb4 = scrapertools.get_match(data,
                                                                 '<div class="media_index_thumb_list".*?src=.*?src=.*?src=.*?src="([^"]+)"')
                            photo_imdb4 = re.sub(r"._.*?jpg", "._V1_SX1280_SY720_.jpg", photo_imdb4)
                        except:
                            pass

                    except:
                        pass
                except:
                    pass

                extra = "http://s6.postimg.org/6flcihb69/brico1sinopsis.png"  # http://4.bp.blogspot.com/-0rYZjLStWrM/TcIqkbq-MaI/AAAAAAAACiM/7_qFGM4WvnA/s1600/BarraSeparadora-Sinopsis.png

                try:
                    fanart_1 = photo_imdb3
                except:
                    try:
                        fanart_1 = photo_imdb2
                    except:
                        try:
                            fanart_1 = photo_imdb1
                        except:
                            fanart_1 = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"

                try:
                    fanart_2 = photo_imdb4
                except:
                    try:
                        fanart_2 = photo_imdb2
                    except:
                        try:
                            fanart_2 = photo_imdb
                        except:
                            fanart_2 = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"
                try:
                    fanart_info = photo_imdb2
                except:
                    try:
                        fanart_info = photo_imdb
                    except:
                        fanart_info = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"

                try:
                    fanart_trailer = photo_imdb3
                except:
                    try:
                        fanart_trailer = photo_imdb2
                    except:
                        try:
                            fanart_trailer = photo_imdb
                        except:
                            fanart_trailer = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"

                try:
                    category = photo_imdb3
                except:
                    try:
                        category = photo_imdb
                    except:
                        try:
                            category = photo_imdb3
                        except:
                            category = "http://s6.postimg.org/yefi9ccsx/briconofotoventanuco.png"
                try:
                    fanart = photo_imdb
                except:
                    try:
                        fanart = photo_imdb2
                    except:
                        try:
                            fanart = photo_imdb3
                        except:
                            fanart = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"
                try:
                    show = photo_imdb4
                except:
                    try:
                        show = photo_imdb2
                    except:
                        try:
                            show = photo_imdb
                        except:
                            show = "http://img1.gtsstatic.com/wallpapers/55cb135265088aeee5147c2db20515d8_large.jpeg"




                            ###Encontrado fanart_1 en Tmdb
            for fan in matches:
                fanart = "https://image.tmdb.org/t/p/original" + fan
                fanart_1 = fanart
                ###Busca fanart para info, fanart para trailer y fanart_2(finvideos) en Tmdb
                urltmdb_images = "http://api.themoviedb.org/3/movie/" + id + "/images?api_key=2e2160006592024ba87ccdf78c28f49f"
                data = scrapertools.cachePage(urltmdb_images)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

                patron = '"backdrops".*?"file_path":".*?",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)"'
                matches = re.compile(patron, re.DOTALL).findall(data)

                if len(matches) == 0:
                    patron = '"backdrops".*?"file_path":"(.*?)",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)"'
                    matches = re.compile(patron, re.DOTALL).findall(data)
                    if len(matches) == 0:
                        fanart_info = fanart_1
                        fanart_trailer = fanart_1
                        fanart_2 = fanart_1
                for fanart_info, fanart_trailer, fanart_2 in matches:
                    fanart_info = "https://image.tmdb.org/t/p/original" + fanart_info
                    fanart_trailer = "https://image.tmdb.org/t/p/original" + fanart_trailer
                    fanart_2 = "https://image.tmdb.org/t/p/original" + fanart_2

                    if fanart_info == fanart:
                        ###Busca fanart_info en Imdb si coincide con fanart
                        try:
                            url_imdbphoto = "http://www.imdb.com/title/" + id_imdb + "/mediaindex"
                            photo_imdb = scrapertools.get_match(url_imdbphoto,
                                                                '<div class="media_index_thumb_list".*?src="([^"]+)"')
                            photo_imdb = photo_imdb.replace("@._V1_UY100_CR25,0,100,100_AL_.jpg",
                                                            "@._V1_SX1280_SY720_.jpg")
                            fanart_info = photo_imdb
                        except:
                            fanart_info = fanart_2

                            # Busqueda de todos los arts posibles

        url_fanartv = "http://webservice.fanart.tv/v3/movies/" + id + "?api_key=dffe90fba4d02c199ae7a9e71330c987"
        data = scrapertools.cachePage(url_fanartv)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        patron = '"hdmovielogo":.*?"url": "([^"]+)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if '"moviedisc"' in data:
            disc = scrapertools.get_match(data, '"moviedisc":.*?"url": "([^"]+)"')
        if '"movieposter"' in data:
            poster = scrapertools.get_match(data, '"movieposter":.*?"url": "([^"]+)"')
        if '"moviethumb"' in data:
            thumb = scrapertools.get_match(data, '"moviethumb":.*?"url": "([^"]+)"')
        if '"moviebanner"' in data:
            banner = scrapertools.get_match(data, '"moviebanner":.*?"url": "([^"]+)"')

        if len(matches) == 0:
            extra = "http://s6.postimg.org/6flcihb69/brico1sinopsis.png"
            show = fanart_2
            category = fanart_1
            itemlist.append(
                Item(channel=item.channel, title=item.title, action="findvideos_peli", url=item.url, server="torrent",
                     thumbnail=posterdb, fanart=fanart, extra=extra, show=show, category=category, folder=True))
        for logo in matches:
            if '"hdmovieclearart"' in data:
                clear = scrapertools.get_match(data, '"hdmovieclearart":.*?"url": "([^"]+)"')
                if '"moviebackground"' in data:
                    extra = clear
                    show = fanart_2
                    if '"moviebanner"' in data:
                        category = banner
                    else:
                        category = clear
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos_peli", url=item.url,
                                         server="torrent", thumbnail=logo, fanart=fanart_1, extra=extra, show=show,
                                         category=category, folder=True))
                else:
                    extra = clear
                    show = fanart_2
                    if '"moviebanner"' in data:
                        category = banner
                    else:
                        category = clear
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos_peli", url=item.url,
                                         server="torrent", thumbnail=logo, fanart=fanart_1, extra=extra, show=show,
                                         category=category, folder=True))

            if '"moviebackground"' in data:

                if '"hdmovieclearart"' in data:
                    clear = scrapertools.get_match(data, '"hdmovieclearart":.*?"url": "([^"]+)"')
                    extra = clear
                    show = fanart_2
                    if '"moviebanner"' in data:
                        category = banner
                    else:
                        category = clear

                else:
                    extra = logo
                    show = fanart_2
                    if '"moviebanner"' in data:
                        category = banner
                    else:
                        category = logo
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos_peli", url=item.url,
                                         server="torrent", thumbnail=logo, fanart=fanart_1, extra=extra, show=show,
                                         category=category, folder=True))

            if not '"hdmovieclearart"' in data and not '"moviebackground"' in data:
                extra = logo
                show = fanart_2
                if '"moviebanner"' in data:
                    category = banner
                else:
                    category = extra
                itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos_peli", url=item.url,
                                     server="torrent", thumbnail=logo, fanart=fanart_1, category=category, extra=extra,
                                     show=show, folder=True))
    ####Info item. Se añade item.show.split("|")[0] and item.extra != "Series" para salvar el error de cuando una serie no está perfectamente tipificada como tal en Bricocine
    title = "Info"
    title = title.replace(title, "[COLOR skyblue]" + title + "[/COLOR]")
    if not "temporada" in item.url and not "Temporada" in item.show.split("|")[0] and item.extra != "Series":
        thumbnail = posterdb
    if "temporada" in item.url or "Temporada" in item.show.split("|")[0] or item.extra == "Series":
        if '"tvposter"' in data:
            thumbnail = tvposter
        else:
            thumbnail = postertvdb

        if "tvbanner" in data:
            category = tvbanner
        else:
            category = show

    itemlist.append(
        Item(channel=item.channel, action="info", title=title, url=item.url, thumbnail=thumbnail, fanart=fanart_info,
             show=show, extra=extra, category=category, folder=False))

    ####Trailer item
    title = "[COLOR crimson]Trailer[/COLOR]"
    if "temporada" in item.url or "Temporada" in item.show.split("|")[0] or item.extra == "Series":
        if '"tvthumb"' in data:
            thumbnail = tvthumb
        else:
            thumbnail = postertvdb
        if '"tvbanner"' in data:
            extra = tvbanner
        elif '"tvthumb"' in data:
            extra = tvthumb
        else:
            extra = item.thumbnail
    else:
        if '"moviethumb"' in data:
            thumbnail = thumb
        else:
            thumbnail = posterdb

        if '"moviedisc"' in data:
            extra = disc
        else:
            if '"moviethumb"' in data:
                extra = thumb

            else:
                extra = posterdb

    itemlist.append(Item(channel=item.channel, action="trailer", title=title, url=item.url, thumbnail=thumbnail,
                         fulltitle=item.title, fanart=fanart_trailer, extra=extra, folder=True))
    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')
    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []
    ###Ubicacion Customkey
    import xbmc
    SEARCHDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    ###Carga Customkey en Finvideos cuando se trata de una busqueda
    if xbmc.Player().isPlaying():
        if not os.path.exists(TESTPYDESTFILE):
            import xbmc
            urllib.urlretrieve("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/search.txt",
                               SEARCHDESTFILE)
            urllib.urlretrieve("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/test.py",
                               TESTPYDESTFILE)
            urllib.urlretrieve(
                "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customkey.xml",
                KEYMAPDESTFILE)
            urllib.urlretrieve(
                "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/remote.xml",
                REMOTEDESTFILE)
            urllib.urlretrieve(
                "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customapp.xml",
                APPCOMMANDDESTFILE)

            xbmc.executebuiltin('Action(reloadkeymaps)')

    data = get_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;| - REPARADO", "", data)
    ###Borra Customkey cuando no hay música
    import xbmc
    if not xbmc.Player().isPlaying():
        TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
        KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
        REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
        APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
        try:
            os.remove(KEYMAPDESTFILE)
            print "Custom Keyboard.xml borrado"
            os.remove(TESTPYDESTFILE)
            print "Testpy borrado"
            os.remove(REMOTEDESTFILE)
            print "Remote borrado"
            os.remove(APPCOMMANDDESTFILE)
            print "Appcommand borrado"
            xbmc.executebuiltin('Action(reloadkeymaps)')
        except Exception as inst:
            xbmc.executebuiltin('Action(reloadkeymaps)')
            print "No hay customs"

    ###Busca video cuando hay torrents y magnet en la serie
    if 'id="magnet"' in data:
        if 'id="file"' in data:
            bloque_capitulos = scrapertools.get_match(data,
                                                      '<table class="table table-series">(.*?)<span class="block mtop clearfix">')
            patron = '<span class="title">([^<]+)-.*?(\d)(\d+)([^<]+)</span></td>.*?'
            patron += 'id="([^"]+)".*?href="([^"]+)".*?id="([^"]+)" href="([^"]+)"'
            matches = re.compile(patron, re.DOTALL).findall(bloque_capitulos)
            if len(matches) == 0:
                patron = '<span class="title">(.*?)(\d)(\d+)([^<]+)</span></td>.*?'
                patron += 'id="([^"]+)".*?href="([^"]+)".*?id="([^"]+)".*?href="([^"]+)"'
                matches = re.compile(patron, re.DOTALL).findall(bloque_capitulos)
                if len(matches) == 0:
                    show = item.show
                    extra = item.thumbnail
                    ###Se identifica como serie respetando en anterior item.category
                    category = item.category + "|" + "series"
                    itemlist.append(Item(channel=item.channel,
                                         title="[COLOR gold][B]Ooops!! Algo no va bien,pulsa para ser dirigido a otra busqueda, ...[/B][/COLOR]",
                                         action="findvideos_peli", url=item.url,
                                         thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                                         fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", extra=extra,
                                         show=show, category=category, plot=item.plot, folder=True))

            import base64
            for title_links, seasson, epi, calidad, title_torrent, url_torrent, title_magnet, url_magnet in matches:
                try:
                    season = scrapertools.get_match(data, '<title>.*?Temporada.*?(\d+).*?Torrent')
                except:
                    try:
                        ###Busqueda de season el las series que no vienen bien tipificadas como tal
                        season = scrapertools.get_match(data, '<span class="title">.*?-.*?(\d+)x')
                    except:
                        season = "0"
                epi = re.sub(r"101|201|301|401|501|601|701|801|901", "01", epi)
                epi = re.sub(r"102|202|302|402|502|602|702|802|902", "02", epi)
                epi = re.sub(r"103|203|303|403|503|603|703|803|903", "03", epi)
                epi = re.sub(r"104|204|304|404|504|604|704|804|904", "04", epi)
                epi = re.sub(r"105|205|305|405|505|605|705|805|905", "05", epi)
                epi = re.sub(r"106|206|306|406|506|606|706|806|906", "06", epi)
                epi = re.sub(r"107|207|307|407|507|607|707|807|907", "07", epi)
                epi = re.sub(r"108|208|308|408|508|608|708|808|908", "08", epi)
                epi = re.sub(r"109|209|309|409|509|609|709|809|909", "09", epi)
                epi = re.sub(r"110|210|310|410|510|610|710|810|910", "10", epi)
                epi = re.sub(r"111|211|311|411|511|611|711|811|911", "11", epi)
                epi = re.sub(r"112|212|312|412|512|612|712|812|912", "12", epi)
                epi = re.sub(r"113|213|313|413|513|613|713|813|913", "13", epi)
                epi = re.sub(r"114|214|314|414|514|614|714|814|914", "14", epi)
                epi = re.sub(r"115|215|315|415|515|615|715|815|915", "15", epi)
                epi = re.sub(r"116|216|316|416|516|616|716|816|916", "16", epi)
                epi = re.sub(r"117|217|317|417|517|617|717|817|917", "17", epi)
                epi = re.sub(r"118|218|318|418|518|618|718|818|918", "18", epi)
                epi = re.sub(r"119|219|319|419|519|619|719|819|919", "19", epi)
                epi = re.sub(r"120|220|320|420|520|620|720|820|920", "20", epi)
                epi = re.sub(r"121|221|321|421|521|621|721|821|921", "21", epi)
                epi = re.sub(r"122|222|322|422|522|622|722|822|922", "22", epi)
                epi = re.sub(r"123|223|323|423|523|623|723|823|923", "23", epi)
                epi = re.sub(r"124|224|324|424|524|624|724|824|924", "24", epi)
                epi = re.sub(r"125|225|325|425|525|625|725|825|925", "25", epi)
                epi = re.sub(r"126|226|326|426|526|626|726|826|926", "26", epi)
                epi = re.sub(r"127|227|327|427|527|627|727|827|927", "27", epi)
                epi = re.sub(r"128|228|328|428|528|628|728|828|928", "28", epi)
                epi = re.sub(r"129|229|329|429|529|629|729|829|929", "29", epi)
                epi = re.sub(r"130|230|330|430|530|630|730|830|930", "30", epi)

                seasson_epi = season + "x" + epi
                seasson_epi = seasson_epi.replace(seasson_epi, "[COLOR sandybrown]" + seasson_epi + "[/COLOR]")
                ###Ajuste de episodio para info_epi
                if "x0" in seasson_epi:
                    epi = epi.replace("0", "")

                title_links = title_links.replace("\\'s", "'s")
                title_torrent = "[" + title_torrent.replace("file", "torrent") + "]"
                title_torrent = title_torrent.replace(title_torrent, "[COLOR green]" + title_torrent + "[/COLOR]")
                title_magnet = "[" + "magnet" + "]"
                title_magnet = "[COLOR red]Opción[/COLOR]" + " " + title_magnet.replace(title_magnet,
                                                                                        "[COLOR crimson]" + title_magnet + "[/COLOR]")
                calidad = calidad.replace(calidad, "[COLOR sandybrown]" + calidad + "[/COLOR]")
                title_links = title_links.replace(title_links, "[COLOR orange]" + title_links + "[/COLOR]")
                title_torrent = title_links + " " + seasson_epi + calidad + "- " + title_torrent
                url_torrent = base64.decodestring(url_torrent.split('&u=')[1][::-1])
                url_magnet = base64.decodestring(url_magnet.split('&u=')[1][::-1])
                title_links = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|\[.*?\]|&nbsp;|REPARADO", "", title_links)
                title_links = title_links.replace('\[.*?\]', '')
                title_links = title_links.replace('á', 'a')
                title_links = title_links.replace('Á', 'A')
                title_links = title_links.replace('é', 'e')
                title_links = title_links.replace('í', 'i')
                title_links = title_links.replace('ó', 'o')
                title_links = title_links.replace('ú', 'u')
                title_links = title_links.replace(' ', '%20')

                extra = season + "|" + title_links + "|" + epi
                if "sinopsis.png" in item.extra:
                    item.extra = item.thumbnail
                if "bricotvshows2.png" in item.show:
                    item.show = item.fanart

                itemlist.append(Item(channel=item.channel, title=title_torrent, action="episodios", url=url_torrent,
                                     thumbnail=item.extra, fanart=item.show, plot=item.plot, extra=extra,
                                     category=item.category, folder=True))
                itemlist.append(Item(channel=item.channel, title=title_magnet, action="episodios", url=url_magnet,
                                     thumbnail=item.extra, fanart=item.show, extra=extra, plot=item.plot,
                                     category=item.category, folder=True))
            try:
                ###Comprueba si, aparte de cápitulos torrent/magnet hay algun torrent suelto sin magnet
                checktorrent = scrapertools.get_match(data,
                                                      'id="magnet".*?Descargar .torrent<\/a><\/li><\/ul><\/td><\/tr><tr><td><span class="title">.*?rel="nofollow">(.*?)<\/a><\/li><\/ul><\/td><\/tr><tr><td>')
            except:
                checktorrent = ""
            ###Busqueda Torrent si los encuentra sueltos
            if checktorrent == "Descargar .torrent":
                torrent_bloque = scrapertools.get_match(data,
                                                        'id="file".*?id="magnet".*?<span class="title">.*?<a id="file".*?a id="file".*?class="btn btn-primary".*?d="file"(.*?class="btn btn-primary".*?)</table>')

                patron = '<span class="title">([^<]+)- (\d)(\d+)([^<]+).*?'
                patron += 'id="file".*?href="([^"]+)"'
                matches = re.compile(patron, re.DOTALL).findall(torrent_bloque)
                if len(matches) == 0:
                    patron = '<span class="title">(.*?)(\d)(\d+)([^<]+)</span></td>.*?'
                    patron += 'id="([^"]+)".*?href="([^"]+)"'
                    matches = re.compile(patron, re.DOTALL).findall(bloque_capitulos)
                    if len(matches) == 0:
                        show = item.show
                        extra = item.thumbnail
                        category = item.category + "|" + "series"

                        itemlist.append(Item(channel=item.channel,
                                             title="[COLOR gold][B]Ooops!! Algo no va bien,pulsa para ser dirigido a otra busqueda, ...[/B][/COLOR]",
                                             action="findvideos_peli", url=item.url,
                                             thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                                             fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", extra=extra,
                                             show=show, category=category, plot=item.plot, folder=True))

                import base64

                for title_links, seasson, epi, calidad, url_torrent in matches:
                    ## torrent
                    try:
                        season = scrapertools.get_match(data, '<title>.*?Temporada.*?(\d+).*?Torrent')
                    except:
                        ###Busqueda de season el las series que no vienen bien tipificadas como tal
                        season = scrapertools.get_match(data, '<span class="title">.*?-.*?(\d+)x')
                    epi = re.sub(r"101|201|301|401|501|601|701|801|901", "01", epi)
                    epi = re.sub(r"102|202|302|402|502|602|702|802|902", "02", epi)
                    epi = re.sub(r"103|203|303|403|503|603|703|803|903", "03", epi)
                    epi = re.sub(r"104|204|304|404|504|604|704|804|904", "04", epi)
                    epi = re.sub(r"105|205|305|405|505|605|705|805|905", "05", epi)
                    epi = re.sub(r"106|206|306|406|506|606|706|806|906", "06", epi)
                    epi = re.sub(r"107|207|307|407|507|607|707|807|907", "07", epi)
                    epi = re.sub(r"108|208|308|408|508|608|708|808|908", "08", epi)
                    epi = re.sub(r"109|209|309|409|509|609|709|809|909", "09", epi)
                    epi = re.sub(r"110|210|310|410|510|610|710|810|910", "10", epi)
                    epi = re.sub(r"111|211|311|411|511|611|711|811|911", "11", epi)
                    epi = re.sub(r"112|212|312|412|512|612|712|812|912", "12", epi)
                    epi = re.sub(r"113|213|313|413|513|613|713|813|913", "13", epi)
                    epi = re.sub(r"114|214|314|414|514|614|714|814|914", "14", epi)
                    epi = re.sub(r"115|215|315|415|515|615|715|815|915", "15", epi)
                    epi = re.sub(r"116|216|316|416|516|616|716|816|916", "16", epi)
                    epi = re.sub(r"117|217|317|417|517|617|717|817|917", "17", epi)
                    epi = re.sub(r"118|218|318|418|518|618|718|818|918", "18", epi)
                    epi = re.sub(r"119|219|319|419|519|619|719|819|919", "19", epi)
                    epi = re.sub(r"120|220|320|420|520|620|720|820|920", "20", epi)
                    epi = re.sub(r"121|221|321|421|521|621|721|821|921", "21", epi)
                    epi = re.sub(r"122|222|322|422|522|622|722|822|922", "22", epi)
                    epi = re.sub(r"123|223|323|423|523|623|723|823|923", "23", epi)
                    epi = re.sub(r"124|224|324|424|524|624|724|824|924", "24", epi)
                    epi = re.sub(r"125|225|325|425|525|625|725|825|925", "25", epi)
                    epi = re.sub(r"126|226|326|426|526|626|726|826|926", "26", epi)
                    epi = re.sub(r"127|227|327|427|527|627|727|827|927", "27", epi)
                    epi = re.sub(r"128|228|328|428|528|628|728|828|928", "28", epi)
                    epi = re.sub(r"129|229|329|429|529|629|729|829|929", "29", epi)
                    epi = re.sub(r"130|230|330|430|530|630|730|830|930", "30", epi)
                    seasson_epi = season + "x" + epi
                    seasson_epi = seasson_epi.replace(seasson_epi, "[COLOR sandybrown]" + seasson_epi + "[/COLOR]")
                    if "x0" in seasson_epi:
                        epi = epi.replace("0", "")
                    title_torrent = "[torrent]"
                    title_torrent = title_torrent.replace(title_torrent, "[COLOR green]" + title_torrent + "[/COLOR]")
                    calidad = calidad.replace(calidad, "[COLOR sandybrown]" + calidad + "[/COLOR]")
                    title_links = title_links.replace(title_links, "[COLOR orange]" + title_links + "[/COLOR]")
                    title_torrent = title_links + " " + seasson_epi + calidad + "- " + title_torrent
                    url_torrent = base64.decodestring(url_torrent.split('&u=')[1][::-1])
                    title_links = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|\[.*?\]|&nbsp;|REPARADO", "", title_links)
                    title_links = title_links.replace('\[.*?\]', '')
                    title_links = title_links.replace('á', 'a')
                    title_links = title_links.replace('Á', 'A')
                    title_links = title_links.replace('é', 'e')
                    title_links = title_links.replace('í', 'i')
                    title_links = title_links.replace('ó', 'o')
                    title_links = title_links.replace('ú', 'u')
                    title_links = title_links.replace(' ', '%20')
                    extra = season + "|" + title_links + "|" + epi
                    itemlist.append(Item(channel=item.channel, title=title_torrent, action="episodios", url=url_torrent,
                                         thumbnail=item.extra, fanart=item.show, extra=extra, plot=item.plot,
                                         category=item.category, folder=True))
    else:
        ###Busqueda cuando hay Torrent pero no magnet en la serie
        if 'id="file"' in data and not 'id="magnet"' in data:

            patron = '<span class="title">([^<]+)- (\d)(\d+)([^<]+).*?'
            patron += 'id="([^"]+)".*?href="([^"]+)"'
            matches = re.compile(patron, re.DOTALL).findall(data)
            if len(matches) == 0:
                patron = '<span class="title">(.*?)(\d)(\d+)([^<]+)</span></td>.*?'
                patron += 'id="([^"]+)".*?href="([^"]+)"'
                matches = re.compile(patron, re.DOTALL).findall(bloque_capitulos)
                if len(matches) == 0:
                    show = item.show
                    extra = item.thumbnail
                    category = item.category + "|" + "series"
                    itemlist.append(Item(channel=item.channel,
                                         title="[COLOR gold][B]Ooops!! Algo no va bien,pulsa para ser dirigido a otra busqueda, ...[/B][/COLOR]",
                                         action="findvideos_peli", url=item.url,
                                         thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                                         fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", extra=extra,
                                         show=show, category=category, plot=item.plot, folder=True))
            import base64
            for title_links, seasson, epi, calidad, title_torrent, url_torrent in matches:
                try:
                    season = scrapertools.get_match(data, '<title>.*?Temporada.*?(\d+).*?Torrent')
                except:
                    ###Busqueda de season el las series que no vienen bien tipificadas como tal
                    season = scrapertools.get_match(data, '<span class="title">.*?-.*?(\d+)x')
                epi = re.sub(r"101|201|301|401|501|601|701|801|901", "01", epi)
                epi = re.sub(r"102|202|302|402|502|602|702|802|902", "02", epi)
                epi = re.sub(r"103|203|303|403|503|603|703|803|903", "03", epi)
                epi = re.sub(r"104|204|304|404|504|604|704|804|904", "04", epi)
                epi = re.sub(r"105|205|305|405|505|605|705|805|905", "05", epi)
                epi = re.sub(r"106|206|306|406|506|606|706|806|906", "06", epi)
                epi = re.sub(r"107|207|307|407|507|607|707|807|907", "07", epi)
                epi = re.sub(r"108|208|308|408|508|608|708|808|908", "08", epi)
                epi = re.sub(r"109|209|309|409|509|609|709|809|909", "09", epi)
                epi = re.sub(r"110|210|310|410|510|610|710|810|910", "10", epi)
                epi = re.sub(r"111|211|311|411|511|611|711|811|911", "11", epi)
                epi = re.sub(r"112|212|312|412|512|612|712|812|912", "12", epi)
                epi = re.sub(r"113|213|313|413|513|613|713|813|913", "13", epi)
                epi = re.sub(r"114|214|314|414|514|614|714|814|914", "14", epi)
                epi = re.sub(r"115|215|315|415|515|615|715|815|915", "15", epi)
                epi = re.sub(r"116|216|316|416|516|616|716|816|916", "16", epi)
                epi = re.sub(r"117|217|317|417|517|617|717|817|917", "17", epi)
                epi = re.sub(r"118|218|318|418|518|618|718|818|918", "18", epi)
                epi = re.sub(r"119|219|319|419|519|619|719|819|919", "19", epi)
                epi = re.sub(r"120|220|320|420|520|620|720|820|920", "20", epi)
                epi = re.sub(r"121|221|321|421|521|621|721|821|921", "21", epi)
                epi = re.sub(r"122|222|322|422|522|622|722|822|922", "22", epi)
                epi = re.sub(r"123|223|323|423|523|623|723|823|923", "23", epi)
                epi = re.sub(r"124|224|324|424|524|624|724|824|924", "24", epi)
                epi = re.sub(r"125|225|325|425|525|625|725|825|925", "25", epi)
                epi = re.sub(r"126|226|326|426|526|626|726|826|926", "26", epi)
                epi = re.sub(r"127|227|327|427|527|627|727|827|927", "27", epi)
                epi = re.sub(r"128|228|328|428|528|628|728|828|928", "28", epi)
                epi = re.sub(r"129|229|329|429|529|629|729|829|929", "29", epi)
                epi = re.sub(r"130|230|330|430|530|630|730|830|930", "30", epi)

                seasson_epi = season + "x" + epi
                seasson_epi = seasson_epi.replace(seasson_epi, "[COLOR sandybrown]" + seasson_epi + "[/COLOR]")
                if "x0" in seasson_epi:
                    epi = epi.replace("0", "")
                title_torrent = "[" + title_torrent.replace("file", "torrent") + "]"
                title_torrent = title_torrent.replace(title_torrent, "[COLOR green]" + title_torrent + "[/COLOR]")
                calidad = calidad.replace(calidad, "[COLOR sandybrown]" + calidad + "[/COLOR]")
                title_links = title_links.replace(title_links, "[COLOR orange]" + title_links + "[/COLOR]")
                title_torrent = title_links + " " + seasson_epi + calidad + "- " + title_torrent
                url_torrent = base64.decodestring(url_torrent.split('&u=')[1][::-1])
                title_links = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|\[.*?\]|&nbsp;|REPARADO", "", title_links)
                title_links = title_links.replace('\[.*?\]', '')
                title_links = title_links.replace('á', 'a')
                title_links = title_links.replace('Á', 'A')
                title_links = title_links.replace('é', 'e')
                title_links = title_links.replace('í', 'i')
                title_links = title_links.replace('ó', 'o')
                title_links = title_links.replace('ú', 'u')
                title_links = title_links.replace(' ', '%20')
                extra = season + "|" + title_links + "|" + epi
                itemlist.append(Item(channel=item.channel, title=title_torrent, action="episodios", url=url_torrent,
                                     thumbnail=item.extra, fanart=item.show, extra=extra, plot=item.plot,
                                     category=item.category, folder=True))
    ###Busqueda cuando hay Magnet pero no Torrent
    if 'id="magnet"' in data and not 'id="file"' in data:
        patron = '<span class="title">([^<]+)- (\d)(\d+)([^<]+).*?'
        patron += 'id="([^"]+)" href="([^"]+)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if len(matches) == 0:
            patron = '<span class="title">(.*?)(\d)(\d+)([^<]+)</span></td>.*?'
            patron += 'id="([^"]+)".*?href="([^"]+)"'
            matches = re.compile(patron, re.DOTALL).findall(bloque_capitulos)
            if len(matches) == 0:
                show = item.show
                extra = item.extra
                itemlist.append(Item(channel=item.channel,
                                     title="[COLOR gold][B]Ooops!! Algo no va bien,pulsa para ser dirigido a otra busqueda, ...[/B][/COLOR]",
                                     action="findvideos_peli", url=item.url,
                                     thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                                     fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", extra=extra, show=show,
                                     folder=True))
        import base64
        for title_links, seasson, epi, calidad, title_magnet, url_magnet in matches:
            try:
                season = scrapertools.get_match(data, '<title>.*?Temporada.*?(\d+).*?Torrent')
            except:
                ###Busqueda de season el las series que no vienen bien tipificadas como tal
                season = scrapertools.get_match(data, '<span class="title">.*?-.*?(\d+)x')
            epi = re.sub(r"101|201|301|401|501|601|701|801|901", "01", epi)
            epi = re.sub(r"102|202|302|402|502|602|702|802|902", "02", epi)
            epi = re.sub(r"103|203|303|403|503|603|703|803|903", "03", epi)
            epi = re.sub(r"104|204|304|404|504|604|704|804|904", "04", epi)
            epi = re.sub(r"105|205|305|405|505|605|705|805|905", "05", epi)
            epi = re.sub(r"106|206|306|406|506|606|706|806|906", "06", epi)
            epi = re.sub(r"107|207|307|407|507|607|707|807|907", "07", epi)
            epi = re.sub(r"108|208|308|408|508|608|708|808|908", "08", epi)
            epi = re.sub(r"109|209|309|409|509|609|709|809|909", "09", epi)
            epi = re.sub(r"110|210|310|410|510|610|710|810|910", "10", epi)
            epi = re.sub(r"111|211|311|411|511|611|711|811|911", "11", epi)
            epi = re.sub(r"112|212|312|412|512|612|712|812|912", "12", epi)
            epi = re.sub(r"113|213|313|413|513|613|713|813|913", "13", epi)
            epi = re.sub(r"114|214|314|414|514|614|714|814|914", "14", epi)
            epi = re.sub(r"115|215|315|415|515|615|715|815|915", "15", epi)
            epi = re.sub(r"116|216|316|416|516|616|716|816|916", "16", epi)
            epi = re.sub(r"117|217|317|417|517|617|717|817|917", "17", epi)
            epi = re.sub(r"118|218|318|418|518|618|718|818|918", "18", epi)
            epi = re.sub(r"119|219|319|419|519|619|719|819|919", "19", epi)
            epi = re.sub(r"120|220|320|420|520|620|720|820|920", "20", epi)
            epi = re.sub(r"121|221|321|421|521|621|721|821|921", "21", epi)
            epi = re.sub(r"122|222|322|422|522|622|722|822|922", "22", epi)
            epi = re.sub(r"123|223|323|423|523|623|723|823|923", "23", epi)
            epi = re.sub(r"124|224|324|424|524|624|724|824|924", "24", epi)
            epi = re.sub(r"125|225|325|425|525|625|725|825|925", "25", epi)
            epi = re.sub(r"126|226|326|426|526|626|726|826|926", "26", epi)
            epi = re.sub(r"127|227|327|427|527|627|727|827|927", "27", epi)
            epi = re.sub(r"128|228|328|428|528|628|728|828|928", "28", epi)
            epi = re.sub(r"129|229|329|429|529|629|729|829|929", "29", epi)
            epi = re.sub(r"130|230|330|430|530|630|730|830|930", "30", epi)

            seasson_epi = season + "x" + epi
            seasson_epi = seasson_epi.replace(seasson_epi, "[COLOR sandybrown]" + seasson_epi + "[/COLOR]")
            if "x0" in seasson_epi:
                epi = epi.replace("0", "")
            title_magnet = "[" + "magnet" + "]"
            title_magnet = "[COLOR red]Opción[/COLOR]" + " " + title_magnet.replace(title_magnet,
                                                                                    "[COLOR crimson]" + title_magnet + "[/COLOR]")
            calidad = calidad.replace(calidad, "[COLOR sandybrown]" + calidad + "[/COLOR]")
            title_links = title_links.replace(title_links, "[COLOR orange]" + title_links + "[/COLOR]")
            title_magnet = title_links + " " + seasson_epi + calidad + "- " + title_magnet
            url_magnet = base64.decodestring(url_magnet.split('&u=')[1][::-1])
            title_links = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|\[.*?\]|&nbsp;|REPARADO", "", title_links)
            title_links = title_links.replace('\[.*?\]', '')
            title_links = title_links.replace('á', 'a')
            title_links = title_links.replace('Á', 'A')
            title_links = title_links.replace('é', 'e')
            title_links = title_links.replace('í', 'i')
            title_links = title_links.replace('ó', 'o')
            title_links = title_links.replace('ú', 'u')
            title_links = title_links.replace(' ', '%20')
            extra = season + "|" + title_links + "|" + epi
            itemlist.append(
                Item(channel=item.channel, title=title_magnet, action="episodios", url=url_magnet, thumbnail=item.extra,
                     fanart=item.show, extra=extra, plot=item.plot, category=item.category, folder=True))
    ###No hay video
    if not 'id="file"' in data and not 'id="magnet"' in data:
        show = item.show
        extra = item.extra
        itemlist.append(Item(channel=item.channel,
                             title="[COLOR gold][B]Ooops!! Algo no va bien,pulsa para ser dirigido a otra busqueda, ...[/B][/COLOR]",
                             action="findvideos_peli", url=item.url,
                             thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                             fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", extra=extra, show=show,
                             folder=True))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    ###Borra Customkey si no hay música
    import xbmc
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    if not xbmc.Player().isPlaying() and os.path.exists(TESTPYDESTFILE):
        TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
        KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
        REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
        APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
        try:
            os.remove(KEYMAPDESTFILE)
            print "Custom Keyboard.xml borrado"
            os.remove(TESTPYDESTFILE)
            print "Testpy borrado"
            os.remove(REMOTEDESTFILE)
            print "Remote borrado"
            os.remove(APPCOMMANDDESTFILE)
            print "Appcommand borrado"
            xbmc.executebuiltin('Action(reloadkeymaps)')
        except Exception as inst:
            xbmc.executebuiltin('Action(reloadkeymaps)')
            print "No hay customs"

    season = item.extra.split("|")[0]
    title_links = item.extra.split("|")[1]
    epi = item.extra.split("|")[2]
    title_tag = "[COLOR yellow]Ver --[/COLOR]"
    item.title = item.title.replace("Ver --", "")
    if "magnet" in item.title:
        title_links = title_links.replace("%20", "")
        title_links = "[COLOR orange]" + title_links + " " + season + "x" + epi + "[/COLOR]"
        title = title_tag + title_links + " " + item.title
    else:
        item.title = re.sub(r"\[.*?\]", "", item.title)
        title = title_tag + "[COLOR orange]" + item.title + "[/COLOR]" + "[COLOR green][torrent][/COLOR]"

    if item.plot == "Sensación de vivir: La nueva generación":
        item.plot = "90210"
    if item.plot == "La historia del universo":
        item.plot = "how the universe works"
    try:
        # Nueva busqueda bing de Imdb serie id
        url_imdb = "http://www.bing.com/search?q=%s+tv+series+site:imdb.com" % item.plot.replace(' ', '+')
        data = browser(url_imdb)

        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        try:
            subdata_imdb = scrapertools.get_match(data, '<li class="b_algo">(.*?)h="ID')
        except:
            pass
        try:
            imdb_id = scrapertools.get_match(subdata_imdb, '<a href=.*?http.*?imdb.com/title/(.*?)/.*?"')
        except:
            imdb_id = ""
        ### Busca en Tmdb quinta imagen para episodios mediate Imdb id
        urltmdb_imdb = "https://api.themoviedb.org/3/find/" + imdb_id + "?api_key=2e2160006592024ba87ccdf78c28f49f&external_source=imdb_id"
        data = scrapertools.cachePage(urltmdb_imdb)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        id = scrapertools.get_match(data, '"tv_results":.*?,"id":(.*?),"')

    except:
        ###Si no hay coincidencia busca directamente en Tmdb por título
        if ":" in item.plot:
            try:
                item.plot = item.plot.replace(" ", "%20")
                url_tmdb = "http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + item.plot + "&language=es&include_adult=false"
                data = scrapertools.cachePage(url_tmdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                id = scrapertools.get_match(data, 'page":1.*?,"id":(.*?),"')
            except:
                try:
                    item.plot = re.sub(r"(:.*)", "", item.plot)
                    item.plot = item.plot.replace(" ", "%20")
                    url_tmdb = "http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + item.plot + "&language=es&include_adult=false"
                    data = scrapertools.cachePage(url_tmdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                    id = scrapertools.get_match(data, 'page":1.*?,"id":(.*?),"')
                except:
                    thumbnail = item.thumbnail
                    fanart = item.fanart
                    id = ""
        else:
            try:
                if "De la A a la Z" in item.plot:
                    item.plot = "A to Z"
                item.plot = item.plot.replace(" ", "%20")
                url_tmdb = "http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + item.plot + "&language=es&include_adult=false"
                data = scrapertools.cachePage(url_tmdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                id = scrapertools.get_match(data, 'page":1.*?,"id":(.*?),"')
            except:
                thumbnail = item.thumbnail
                fanart = item.fanart
                id = ""

    ###Teniendo (o no) el id Tmdb busca imagen
    urltmdb_images = "https://api.themoviedb.org/3/tv/" + id + "?api_key=2e2160006592024ba87ccdf78c28f49f"
    data = scrapertools.cachePage(urltmdb_images)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    try:
        backdrop = scrapertools.get_match(data, '"backdrop_path":"(.*?)"')
        fanart_3 = "https://image.tmdb.org/t/p/original" + backdrop
        fanart = fanart_3
    except:
        fanart_3 = item.fanart
        fanart = fanart_3
    ###Se hace también la busqueda de el thumb del episodio en Tmdb
    urltmdb_epi = "https://api.themoviedb.org/3/tv/" + id + "/season/" + item.extra.split("|")[0] + "/episode/" + \
                  item.extra.split("|")[2] + "/images?api_key=2e2160006592024ba87ccdf78c28f49f"
    data = scrapertools.cachePage(urltmdb_epi)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '{"id".*?"file_path":"(.*?)","height"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        thumbnail = item.thumbnail
        fanart = fanart_3
        itemlist.append(
            Item(channel=item.channel, title=title, action="play", url=item.url, server="torrent", thumbnail=thumbnail,
                 fanart=fanart, folder=False))

    for foto in matches:
        thumbnail = "https://image.tmdb.org/t/p/original" + foto

        extra = id + "|" + season
        itemlist.append(
            Item(channel=item.channel, title=title, action="play", url=item.url, thumbnail=thumbnail, fanart=fanart,
                 category=item.category, folder=False))
    ###Busca poster de temporada Tmdb
    urltmdb_temp = "http://api.themoviedb.org/3/tv/" + id + "/season/" + season + "/images?api_key=2e2160006592024ba87ccdf78c28f49f"
    data = get_page(urltmdb_temp)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '{"id".*?"file_path":"(.*?)","height"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        thumbnail = item.thumbnail
    for temp in matches:
        thumbnail = "https://image.tmdb.org/t/p/original" + temp
    ####Busca el fanart para el item info####
    urltmdb_faninfo = "http://api.themoviedb.org/3/tv/" + id + "/images?api_key=2e2160006592024ba87ccdf78c28f49f"
    data = get_page(urltmdb_faninfo)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '{"backdrops".*?"file_path":".*?","height".*?"file_path":"(.*?)",'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        fanart = item.fanart
    for fanart_4 in matches:
        fanart = "https://image.tmdb.org/t/p/original" + fanart_4
    show = item.category + "|" + item.thumbnail
    ### Item info de episodios
    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')
    title = "Info"
    title = title.replace(title, "[COLOR skyblue]" + title + "[/COLOR]")
    itemlist.append(Item(channel=item.channel, action="info_capitulos", title=title, url=item.url, thumbnail=thumbnail,
                         fanart=fanart, extra=item.extra, show=show, folder=False))

    return itemlist


def play(item):
    logger.info()
    itemlist = []
    ###Opción para trailers
    if "youtube" in item.url:
        itemlist.append(Item(channel=item.channel, action="play", server="youtube", url=item.url, fulltitle=item.title,
                             fanart="http://s23.postimg.org/84vkeq863/movietrailers.jpg", folder=False))

    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')
    itemlist.append(Item(channel=item.channel, title=item.title, action="play", url=item.url, server="torrent",
                         thumbnail=item.thumbnail, fanart=item.fanart, category=item.category, folder=False))

    return itemlist


def findvideos_peli(item):
    logger.info()

    itemlist = []
    data = get_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;| - REPARADO", "", data)

    # Busca video si hay magnet y torrent
    if 'id="magnet"' in data:
        if 'id="file"' in data:
            patron = '<span class="title">([^"]+)</span>.*?'
            patron += 'id="([^"]+)".*?href="([^"]+)".*?id="([^"]+)" href="([^"]+)"'

            matches = re.compile(patron, re.DOTALL).findall(data)
            if len(matches) == 0:
                itemlist.append(Item(channel=item.channel,
                                     title="[COLOR gold][B]El video ya no se encuentra en la web, prueba a encontrala por busqueda...[/B][/COLOR]",
                                     thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                                     fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", folder=False))
            import base64
            for title_links, title_torrent, url_torrent, title_magnet, url_magnet in matches:

                title_torrent = "[" + title_torrent.replace("file", "torrent") + "]"
                title_torrent = title_torrent.replace(title_torrent, "[COLOR green]" + title_torrent + "[/COLOR]")
                title_magnet = "[" + "magnet" + "]"
                title_magnet = "[COLOR red]Opción[/COLOR]" + " " + title_magnet.replace(title_magnet,
                                                                                        "[COLOR crimson]" + title_magnet + "[/COLOR]")
                title_links = title_links.replace(title_links, "[COLOR sandybrown]" + title_links + "[/COLOR]")
                title_links = re.sub(r"&#.*?;|\[HD .*?\]|\(.*?\)", "", title_links)
                title_tag = "[COLOR yellow]Ver --[/COLOR]"
                title_torrent = title_tag + title_links + "- " + title_torrent
                url_torrent = base64.decodestring(url_torrent.split('&u=')[1][::-1])
                url_magnet = base64.decodestring(url_magnet.split('&u=')[1][::-1])
                if "sinopsis.png" in item.extra and not "series" in item.category:
                    item.extra = "http://oi67.tinypic.com/28sxwrs.jpg"
                ###Se identifica si es una serie mal tipificada
                if "series" in item.category and not "Completa" in title_links:
                    try:
                        season = scrapertools.get_match(data, '<title>.*?Temporada.*?(\d+).*?Torrent')
                    except:
                        season = "1"
                    title_link = scrapertools.get_match(title_links, '(.*?) -')
                    epi = scrapertools.get_match(title_links, '-.*?(x\d+)')
                    if "x0" in epi:
                        epi = epi.replace("x0", "")
                    title_links = title_link
                    action = "episodios"
                    extra = season + "|" + title_links + "|" + epi
                    itemlist.append(Item(channel=item.channel, title=title_torrent, action=action, url=url_torrent,
                                         server="torrent", thumbnail=item.extra, fanart=item.show, extra=extra,
                                         category=item.category, plot=item.plot, folder=True))
                    itemlist.append(
                        Item(channel=item.channel, title=title_magnet, action=action, url=url_magnet, server="torrent",
                             thumbnail=item.extra, category=item.category, fanart=item.show, extra=extra,
                             plot=item.plot, folder=True))
                else:
                    action = "play"
                    itemlist.append(Item(channel=item.channel, title=title_torrent, action=action, url=url_torrent,
                                         server="torrent", thumbnail=item.extra, fanart=item.show, folder=False))
                    itemlist.append(
                        Item(channel=item.channel, title=title_magnet, action=action, url=url_magnet, server="torrent",
                             thumbnail=item.extra, fanart=item.show, folder=False))
    else:
        ###Busca video cuando hay torrent pero no magnet
        if 'id="file"' in data and not 'id="magnet"' in data:
            patron = '<span class="title">([^"]+)</span>.*?'
            patron += 'id="([^"]+)".*?href="([^"]+)".*?'

            matches = re.compile(patron, re.DOTALL).findall(data)
            if len(matches) == 0:
                itemlist.append(Item(channel=item.channel,
                                     title="[COLOR gold][B]El video ya no se encuentra en la web, prueba a encontrala por busqueda...[/B][/COLOR]",
                                     thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                                     fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", folder=False))
            import base64
            for title_links, title_torrent, url_torrent in matches:
                ## torrent
                title_torrent = "[" + title_torrent.replace("file", "torrent") + "]"
                title_torrent = title_torrent.replace(title_torrent, "[COLOR green]" + title_torrent + "[/COLOR]")
                title_links = title_links.replace(title_links, "[COLOR sandybrown]" + title_links + "[/COLOR]")
                title_links = re.sub(r"&#.*?;", "", title_links)
                title_tag = "[COLOR yellow]Ver --[/COLOR]"
                title_torrent = title_tag + title_links + "- " + title_torrent
                url_torrent = base64.decodestring(url_torrent.split('&u=')[1][::-1])
                if "sinopsis.png" in item.extra:
                    item.extra = "http://oi67.tinypic.com/28sxwrs.jpg"
                ###Se identifica si es una serie mal tipificada
                if "series" in item.category and not "Completa" in title_links:
                    try:
                        season = scrapertools.get_match(data, '<title>.*?Temporada.*?(\d+).*?Torrent')
                    except:
                        season = "1"
                    title_link = scrapertools.get_match(title_links, '(.*?) -')
                    epi = scrapertools.get_match(title_links, '-.*?(x\d+)')
                    if "x0" in epi:
                        epi = epi.replace("x0", "")
                    title_links = title_link
                    action = "episodios"
                    extra = season + "|" + title_links + "|" + epi
                    itemlist.append(Item(channel=item.channel, title=title_torrent, action=action, url=url_torrent,
                                         server="torrent", thumbnail=item.extra, fanart=item.show, extra=extra,
                                         category=item.category, plot=item.plot, folder=True))

                else:
                    action = "play"
                    itemlist.append(Item(channel=item.channel, title=title_torrent, action=action, url=url_torrent,
                                         server="torrent", thumbnail=item.extra, fanart=item.show, folder=False))
    ###Busca video cuando solo hay magnet y no torrent
    if 'id="magnet"' in data and not 'id="file"' in data:
        patron = '<span class="title">([^"]+)</span>.*?'
        patron += 'id="([^"]+)" href="([^"]+)"'

        matches = re.compile(patron, re.DOTALL).findall(data)
        if len(matches) == 0:
            itemlist.append(Item(channel=item.channel,
                                 title="[COLOR gold][B]El video ya no se encuentra en la web, prueba a encontrala por busqueda...[/B][/COLOR]",
                                 thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                                 fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", folder=False))
        import base64
        for title_links, title_magnet, url_magnet in matches:
            title_magnet = "[" + "magnet" + "]"
            title_links = title_links.replace(title_links, "[COLOR sandybrown]" + title_links + "[/COLOR]")
            title_links = re.sub(r"&#.*?;", "", title_links)
            title_tag = "[COLOR red]Ver --[/COLOR]"
            title_magnet = title_tag + title_links + "- " + title_magnet.replace(title_magnet,
                                                                                 "[COLOR crimson]" + title_magnet + "[/COLOR]")
            url_magnet = base64.decodestring(url_magnet.split('&u=')[1][::-1])
            if "sinopsis.png" in item.extra:
                item.extra = "http://oi67.tinypic.com/28sxwrs.jpg"
            ###Se identifica si es una serie mal tipificada
            if "series" in item.category and not "Completa" in title_links:
                try:
                    season = scrapertools.get_match(data, '<title>.*?Temporada.*?(\d+).*?Torrent')
                except:
                    season = "1"
                    title_link = scrapertools.get_match(title_links, '(.*?) -')
                    epi = scrapertools.get_match(title_links, '-.*?(x\d+)')
                    if "x0" in epi:
                        epi = epi.replace("x0", "")
                    title_links = title_link
                    action = "episodios"
                    extra = season + "|" + title_links + "|" + epi
                    itemlist.append(Item(channel=item.channel, title=title_torrent, action=action, url=url_torrent,
                                         server="torrent", thumbnail=item.extra, fanart=item.show, extra=extra,
                                         category=item.category, plot=item.plot, folder=True))

            else:
                action = "play"

                itemlist.append(
                    Item(channel=item.channel, title=title_magnet, action=action, url=url_magnet, server="torrent",
                         thumbnail=item.extra, fanart=item.show, folder=False))
    ###No hay torrent ni magnet
    if not 'id="file"' in data and not 'id="magnet"' in data:
        itemlist.append(Item(channel=item.channel,
                             title="[COLOR gold][B]El video ya no se encuentra en la web, prueba a encontrala por busqueda...[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                             fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", folder=False))
    return itemlist


def trailer(item):
    logger.info()
    ###Crea archivo control trailer.txt para evitar la recarga de la música cuando se vuelve de trailer
    import xbmc
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    if os.path.exists(TESTPYDESTFILE):
        TRAILERDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "trailer.txt")

        urllib.urlretrieve("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/trailer.txt",
                           TRAILERDESTFILE)

    itemlist = []
    data = get_page(item.url)

    # trailer
    patron = "<iframe width='.*?' height='.*?' src='([^']+)?"

    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        itemlist.append(
            Item(channel=item.channel, title="[COLOR gold][B]Esta pelicula no tiene trailer,lo sentimos...[/B][/COLOR]",
                 thumbnail="http://s6.postimg.org/fay99h9ox/briconoisethumb.png",
                 fanart="http://s6.postimg.org/uie8tu1jl/briconoisefan.jpg", folder=False))

    for url in matches:
        listavideos = servertools.findvideos(url)

        for video in listavideos:
            videotitle = scrapertools.unescape(video[0])
            url = video[1]
            server = video[2]

        title = "[COLOR crimson]Trailer - [/COLOR]"
        itemlist.append(Item(channel=item.channel, action="play", server="youtube", title=title + videotitle, url=url,
                             thumbnail=item.extra, fulltitle=item.title,
                             fanart="http://s23.postimg.org/84vkeq863/movietrailers.jpg", folder=False))
    return itemlist


def info(item):
    logger.info()
    url = item.url
    data = get_page(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    if "temporada" in item.url:
        ###Se prepara el Customkey para no permitir el forcerefresh y evitar conflicto con info
        import xbmc
        APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
        try:
            os.remove(APPCOMMANDDESTFILE)
        except:
            pass
        patron = '<title>([^<]+).*?Temporada.*?'
        patron += '<div class="description" itemprop="text.*?">.*?([^<]+).*?</div></div></div>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if len(matches) == 0:
            title = "[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
            plot = "Esta serie no tiene informacion..."
            plot = plot.replace(plot, "[COLOR yellow][B]" + plot + "[/B][/COLOR]")
            photo = "http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
            foto = "http://s6.postimg.org/ub7pb76c1/noinfo.png"
            info = ""
            quit = "Pulsa" + " [COLOR crimson][B]INTRO [/B][/COLOR]" + "para quitar"
        for title, plot in matches:
            plot_title = "Sinopsis" + "[CR]"
            plot_title = plot_title.replace(plot_title, "[COLOR red]" + plot_title + "[/COLOR]")
            plot = plot_title + plot
            plot = plot.replace(plot, "[COLOR white][B]" + plot + "[/B][/COLOR]")
            plot = re.sub(r'div class=".*?">', '', plot)
            plot = plot.replace("div>", "")
            plot = plot.replace('div class="margin_20b">', '')
            plot = plot.replace('div class="post-entry">', '')
            plot = plot.replace('p style="text-align: left;">', '')
            title = re.sub(r"&#.*?;", "", title)
            title = title.replace(title, "[COLOR sandybrown][B]" + title + "[/B][/COLOR]")
            title = title.replace("-", "")
            title = title.replace("Torrent", "")
            title = title.replace("amp;", "")
            title = title.replace("Descargar en Bricocine.com", "")
            try:
                scrapedinfo = scrapertools.get_match(data, 'Ficha técnica</h2><dl class="list"><dt>(.*?)hellip')
            except IndexError:
                scrapedinfo = scrapertools.get_match(data,
                                                     'Ficha técnica</h2><dl class="list"><dt>(.*?)</div><div class="quad-2"')
                scrapedinfo = scrapedinfo.replace("<br />", " ")
                scrapedinfo = scrapedinfo.replace("</dl>", "<dt>")
            scrpaedinfo = re.sub(r'<a href=".*?"|title=".*?"|item.*?=".*?"', '', scrapedinfo)

            infoformat = re.compile('(.*?</dt><dd.*?>).*?</dd><dt>', re.DOTALL).findall(scrapedinfo)
            for info in infoformat:
                scrapedinfo = scrapedinfo.replace(scrapedinfo, "[COLOR white][B]" + scrapedinfo + "[/COLOR]")
                scrapedinfo = scrapedinfo.replace(info, "[COLOR red][B]" + info + "[/B][/COLOR]")
            info = scrapedinfo
            info = re.sub(
                r'<a href=".*?">|title=".*?">|<span itemprop=.*?>|</span></span>|<span>|</a>|itemprop=".*?"|y otros.*?&',
                '', info)
            info = info.replace("</dt><dd>", ":")
            info = info.replace("</dt><dd >", ":")
            info = info.replace("</dt><dd > ", ":")
            info = info.replace("</dd><dt>", " ")
            info = info.replace("</span>", " ")

            info = info.replace("Actores:", "[COLOR red][B]Actores:[/B][/COLOR] ")
            photo = item.extra
            foto = item.category
            quit = "Pulsa" + " [COLOR crimson][B]INTRO [/B][/COLOR]" + "para quitar"
            ###Se carga Customkey no atras
            NOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "noback.xml")
            REMOTENOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remotenoback.xml")
            APPNOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "appnoback.xml")
            urllib.urlretrieve("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/noback.xml",
                               NOBACKDESTFILE)
            urllib.urlretrieve(
                "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/remotenoback.xml",
                REMOTENOBACKDESTFILE)
            urllib.urlretrieve(
                "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/appnoback.xml",
                APPNOBACKDESTFILE)
            xbmc.executebuiltin('Action(reloadkeymaps)')
    else:
        data = get_page(item.url)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        patron = '<div class="description" itemprop="text.*?">.*?([^<]+).*?</div></div></div>.*?'
        patron += '<span class="title">([^"]+)</span>'
        matches = re.compile(patron, re.DOTALL).findall(data)

        if len(matches) == 0:
            title = "[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
            plot = "Esta pelicula no tiene sinopsis..."
            plot = plot.replace(plot, "[COLOR yellow][B]" + plot + "[/B][/COLOR]")
            foto = "http://s6.postimg.org/ub7pb76c1/noinfo.png"
            photo = "http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
            info = ""
            quit = "Pulsa" + " [COLOR crimson][B]INTRO [/B][/COLOR]" + "para quitar"

        for plot, title in matches:
            title = title.upper()
            title = title.replace(title, "[COLOR sandybrown][B]" + title + "[/B][/COLOR]")
            title = re.sub(r"&#.*?;|\[HD .*?\]|", "", title)
            plot_title = "Sinopsis" + "[CR]"
            plot_title = plot_title.replace(plot_title, "[COLOR red]" + plot_title + "[/COLOR]")
            plot = plot_title + plot
            plot = plot.replace(plot, "[COLOR white][B]" + plot + "[/B][/COLOR]")
            plot = plot.replace('div class="margin_20b">', '')
            plot = plot.replace('div class="post-entry">', '')
            try:
                scrapedinfo = scrapertools.get_match(data, 'Ficha técnica</h2><dl class="list"><dt>(.*?)hellip')
            except IndexError:
                scrapedinfo = scrapertools.get_match(data,
                                                     'Ficha técnica</h2><dl class="list"><dt>(.*?)</div><div class="quad-2"')
                scrapedinfo = scrapedinfo.replace("<br />", " ")
                scrapedinfo = scrapedinfo.replace("</dl>", "<dt>")
            scrpaedinfo = re.sub(r'<a href=".*?"|title=".*?"|item.*?=".*?"', '', scrapedinfo)
            infoformat = re.compile('(.*?</dt><dd.*?>).*?</dd><dt>', re.DOTALL).findall(scrapedinfo)
            for info in infoformat:
                scrapedinfo = scrapedinfo.replace(scrapedinfo, "[COLOR white][B]" + scrapedinfo + "[/COLOR]")
                scrapedinfo = scrapedinfo.replace(info, "[COLOR red][B]" + info + "[/B][/COLOR]")
            info = scrapedinfo
            info = re.sub(
                r'<a href=".*?">|title=".*?">|<span itemprop=.*?>|</span></span>|<span>|</a>|itemprop=".*?"|y otros.*?&',
                '', info)
            info = info.replace("</dt><dd>", ":")
            info = info.replace("</dt><dd >", ":")
            info = info.replace("</dt><dd > ", ":")
            info = info.replace("</dd><dt>", " ")
            info = info.replace("</span>", " ")
            if "hellip" in data:
                info = info.replace("Actores:", "[COLOR red][B]Actores:[/B][/COLOR] ")

            foto = item.category
            photo = item.extra
            quit = "Pulsa" + " [COLOR crimson][B]INTRO [/B][/COLOR]" + "para quitar"

    ventana2 = TextBox1(title=title, plot=plot, info=info, thumbnail=photo, fanart=foto, quit=quit)
    ventana2.doModal()


ACTION_GESTURE_SWIPE_LEFT = 511
ACTION_SELECT_ITEM = 7


class TextBox1(xbmcgui.WindowDialog):
    """ Create a skinned textbox window """

    def __init__(self, *args, **kwargs):

        self.getTitle = kwargs.get('title')
        self.getPlot = kwargs.get('plot')
        self.getInfo = kwargs.get('info')
        self.getThumbnail = kwargs.get('thumbnail')
        self.getFanart = kwargs.get('fanart')
        self.getQuit = kwargs.get('quit')

        self.background = xbmcgui.ControlImage(70, 20, 1150, 630,
                                               'http://s6.postimg.org/58jknrvtd/backgroundventana5.png')
        self.title = xbmcgui.ControlTextBox(140, 60, 1130, 50)
        self.quit = xbmcgui.ControlTextBox(145, 90, 1030, 45)
        self.plot = xbmcgui.ControlTextBox(120, 150, 1056, 140)
        self.info = xbmcgui.ControlFadeLabel(120, 310, 1056, 100)
        self.thumbnail = xbmcgui.ControlImage(813, 43, 390, 100, self.getThumbnail)
        self.fanart = xbmcgui.ControlImage(120, 365, 1060, 250, self.getFanart)

        self.addControl(self.background)
        self.addControl(self.title)
        self.addControl(self.quit)
        self.addControl(self.plot)
        self.addControl(self.thumbnail)
        self.addControl(self.fanart)
        self.addControl(self.info)

        self.title.setText(self.getTitle)
        self.quit.setText(self.getQuit)
        try:
            self.plot.autoScroll(7000, 6000, 30000)
        except:
            ###Información de incompatibilidd autoscroll con versiones inferiores a isengrd
            print "Actualice a la ultima version de kodi para mejor info"
            import xbmc
            xbmc.executebuiltin(
                'Notification([COLOR red][B]Actualiza Kodi a su última versión[/B][/COLOR], [COLOR skyblue]para mejor info[/COLOR],8000,"https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/kodi-icon.png")')
        self.plot.setText(self.getPlot)
        self.info.addLabel(self.getInfo)

    def get(self):

        self.show()

    def onAction(self, action):
        if action == ACTION_SELECT_ITEM or action == ACTION_GESTURE_SWIPE_LEFT:
            ###Se vuelven a cargar Customkey al salir de info
            import os, sys
            import xbmc
            APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
            NOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "noback.xml")
            REMOTENOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remotenoback.xml")
            APPNOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "appnoback.xml")
            TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
            try:
                os.remove(NOBACKDESTFILE)
                os.remove(REMOTENOBACKDESTFILE)
                os.remove(APPNOBACKDESTFILE)
                if os.path.exists(TESTPYDESTFILE):
                    urllib.urlretrieve(
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customapp.xml",
                        APPCOMMANDDESTFILE)
                xbmc.executebuiltin('Action(reloadkeymaps)')
            except:
                pass
            self.close()


def info_capitulos(item):
    logger.info()
    import xbmc
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    try:
        os.remove(APPCOMMANDDESTFILE)
    except:
        pass
    url = item.url
    data = scrapertools.cache_page(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    if "series" in item.category:
        item.category = item.category.split("|")[0]
    else:
        item.category = item.show.split("|")[0]
    item.thumbnail = item.show.split("|")[1]
    capitulo = item.extra.split("|")[2]
    capitulo = re.sub(r"(0)\d;", "", capitulo)
    url = "http://thetvdb.com/api/1D62F2F90030C444/series/" + item.show.split("|")[0] + "/default/" + \
          item.extra.split("|")[0] + "/" + capitulo + "/es.xml"
    data = scrapertools.cache_page(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '<Data>.*?<EpisodeName>([^<]+)</EpisodeName>.*?'
    patron += '<Overview>(.*?)</Overview>.*?'

    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        title = "[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
        plot = "Este capitulo no tiene informacion..."
        plot = plot.replace(plot, "[COLOR yellow][B]" + plot + "[/B][/COLOR]")
        image = "http://s6.postimg.org/ub7pb76c1/noinfo.png"
        foto = "http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        quit = "Pulsa" + " [COLOR greenyellow][B]INTRO [/B][/COLOR]" + "para quitar"
    else:

        for name_epi, info in matches:
            if "<filename>episodes" in data:
                foto = scrapertools.get_match(data, '<Data>.*?<filename>(.*?)</filename>')
                fanart = "http://thetvdb.com/banners/" + foto
            else:
                fanart = item.show.split("|")[1]
                if item.show.split("|")[1] == item.thumbnail:
                    fanart = "http://s6.postimg.org/4asrg755b/bricotvshows2.png"

            plot = info
            plot = (translate(plot, "es"))
            plot = plot.replace(plot, "[COLOR yellow][B]" + plot + "[/B][/COLOR]")
            name_epi = re.sub(r"&#.*?;|&amp;", "", name_epi)
            plot = re.sub(r"&#.*?;", "", plot)
            title = name_epi.upper()
            title = title.replace(title, "[COLOR sandybrown][B]" + title + "[/B][/COLOR]")
            image = fanart
            foto = item.show.split("|")[1]
            if not ".png" in item.show.split("|")[1]:
                foto = "http://s6.postimg.org/6flcihb69/brico1sinopsis.png"
            quit = "Pulsa" + " [COLOR greenyellow][B]INTRO [/B][/COLOR]" + "para quitar"
            NOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "noback.xml")
            REMOTENOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remotenoback.xml")
            APPNOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "appnoback.xml")
            TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
            urllib.urlretrieve("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/noback.xml",
                               NOBACKDESTFILE)
            urllib.urlretrieve(
                "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/remotenoback.xml",
                REMOTENOBACKDESTFILE)
            urllib.urlretrieve(
                "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/appnoback.xml",
                APPNOBACKDESTFILE)
            xbmc.executebuiltin('Action(reloadkeymaps)')
    ventana = TextBox2(title=title, plot=plot, thumbnail=image, fanart=foto, quit=quit)
    ventana.doModal()


ACTION_GESTURE_SWIPE_LEFT = 511
ACTION_SELECT_ITEM = 7


class TextBox2(xbmcgui.WindowDialog):
    """ Create a skinned textbox window """

    def __init__(self, *args, **kwargs):
        self.getTitle = kwargs.get('title')
        self.getPlot = kwargs.get('plot')
        self.getThumbnail = kwargs.get('thumbnail')
        self.getFanart = kwargs.get('fanart')
        self.getQuit = kwargs.get('quit')

        self.background = xbmcgui.ControlImage(70, 20, 1150, 630, 'http://s6.postimg.org/n3ph1uxn5/ventana.png')
        self.title = xbmcgui.ControlTextBox(120, 60, 430, 50)
        self.quit = xbmcgui.ControlTextBox(145, 110, 1030, 45)
        self.plot = xbmcgui.ControlTextBox(120, 150, 1056, 100)
        self.thumbnail = xbmcgui.ControlImage(120, 300, 1056, 300, self.getThumbnail)
        self.fanart = xbmcgui.ControlImage(780, 43, 390, 100, self.getFanart)

        self.addControl(self.background)
        self.addControl(self.title)
        self.addControl(self.quit)
        self.addControl(self.plot)
        self.addControl(self.thumbnail)
        self.addControl(self.fanart)

        self.title.setText(self.getTitle)
        self.quit.setText(self.getQuit)
        try:
            self.plot.autoScroll(7000, 6000, 30000)
        except:
            print "Actualice a la ultima version de kodi para mejor info"
            import xbmc
            xbmc.executebuiltin(
                'Notification([COLOR red][B]Actualiza Kodi a su última versión[/B][/COLOR], [COLOR skyblue]para mejor info[/COLOR],8000,"https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/kodi-icon.png")')
        self.plot.setText(self.getPlot)

    def get(self):
        self.show()

    def onAction(self, action):
        if action == ACTION_SELECT_ITEM or action == ACTION_GESTURE_SWIPE_LEFT:
            import os, sys
            import xbmc
            APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
            NOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "noback.xml")
            REMOTENOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remotenoback.xml")
            APPNOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "appnoback.xml")
            TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
            try:
                os.remove(NOBACKDESTFILE)
                os.remove(REMOTENOBACKDESTFILE)
                os.remove(APPNOBACKDESTFILE)
                xbmc.executebuiltin('Action(reloadkeymaps)')
                if os.path.exists(TESTPYDESTFILE):
                    urllib.urlretrieve(
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customapp.xml",
                        APPCOMMANDDESTFILE)
                xbmc.executebuiltin('Action(reloadkeymaps)')
            except:
                xbmc.executebuiltin('Action(reloadkeymaps)')
            self.close()


def translate(to_translate, to_langage="auto", langage="auto"):
    ###Traducción atraves de Google
    '''Return the translation using google translate
        you must shortcut the langage you define (French = fr, English = en, Spanish = es, etc...)
        if you don't define anything it will detect it or use english by default
        Example:
        print(translate("salut tu vas bien?", "en"))
        hello you alright?'''
    agents = {
        'User-Agent': "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
    before_trans = 'class="t0">'
    link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_langage, langage, to_translate.replace(" ", "+"))
    request = urllib2.Request(link, headers=agents)
    page = urllib2.urlopen(request).read()
    result = page[page.find(before_trans) + len(before_trans):]
    result = result.split("<")[0]
    return result


if __name__ == '__main__':
    to_translate = 'Hola como estas?'
    print("%s >> %s" % (to_translate, translate(to_translate)))
    print("%s >> %s" % (to_translate, translate(to_translate, 'fr')))
# should print Hola como estas >> Hello how are you
# and Hola como estas? >> Bonjour comment allez-vous?
