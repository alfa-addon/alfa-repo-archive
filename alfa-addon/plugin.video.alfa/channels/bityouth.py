# -*- coding: utf-8 -*-

import os
import re
import urllib
import urllib2
import urlparse

from core import logger
from core import scrapertools
from core.item import Item

try:
    import xbmc
    import xbmcgui
except:
    pass

host = "http://bityouth.com/"


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
    # br.addheaders =[('Cookie','SRCHD=D=4210979&AF=NOFORM; domain=.bing.com; expires=Wednesday, 09-Nov-06 23:12:40 GMT; MUIDB=36F71C46589F6EAD0BE714175C9F68FC; domain=www.bing.com;	expires=15 de enero de 2018 08:43:26 GMT+1')]
    # Open some site, let's pick a random one, the first that pops in mind
    r = br.open(url)
    response = r.read()
    # if "z{a:1}" in response:
    if not ".ftrH,.ftrHd,.ftrD>" in response:
        print "proooxyy"
        r = br.open("http://anonymouse.org/cgi-bin/anon-www.cgi/" + url)
        response = r.read()
    return response
    ###def proxy(url):
    '''from lib import requests
    proxies = {"http": "http://anonymouse.org/cgi-bin/anon-www.cgi/"+url}
    print "zorro"
    print proxies
    rsp = requests.get(url, proxies=proxies,stream=True)
    print rsp.raw._fp.fp._sock.getpeername()
    print rsp.content
    response = rsp.content
    return response'''


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="[COLOR skyblue][B]Generos[/B][/COLOR]", action="generos",
                         url="http://bityouth.com", thumbnail="http://s6.postimg.org/ybey4gxu9/bityougenerosthum3.png",
                         fanart="http://s18.postimg.org/l4judlx09/bityougenerosfan.jpg"))
    itemlist.append(Item(channel=item.channel, title="[COLOR skyblue][B]Puntuacion[/B][/COLOR]", action="scraper",
                         url="http://bityouth.com/more_elements/0/?o=pd",
                         thumbnail="http://s6.postimg.org/n1qtn9i6p/bityoupuntothum4.png",
                         fanart="http://s6.postimg.org/qrh9oof9t/bityoupuntofan.jpg"))
    itemlist.append(Item(channel=item.channel, title="[COLOR skyblue][B]Novedades[/B][/COLOR]", action="scraper",
                         url="http://bityouth.com/more_elements/0/?o=",
                         thumbnail="http://s6.postimg.org/bry3sbd5d/bityounovedathum2.png",
                         fanart="http://s6.postimg.org/ys4r4naz5/bityounovedadfan.jpg"))
    import xbmc
    if xbmc.Player().isPlaying():
        xbmc.executebuiltin('xbmc.PlayMedia(Stop)')
    SEARCHDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
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
    itemlist.append(Item(channel=item.channel, title="[COLOR skyblue][B]Series[/B][/COLOR]", action="scraper",
                         url="http://bityouth.com/more_elements/0/genero/serie_de_tv?o=",
                         thumbnail="http://s6.postimg.org/59j1km53l/bityouseriesthum.png",
                         fanart="http://s6.postimg.org/45yx8nkgh/bityouseriesfan3.jpg"))
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
    itemlist.append(Item(channel=item.channel, title="[COLOR skyblue][B]Buscar...[/B][/COLOR]", action="search", url="",
                         thumbnail="http://s6.postimg.org/48isvho41/bityousearchthum.png",
                         fanart="http://s6.postimg.org/ic5hcegk1/bityousearchfan.jpg", plot="search"))

    return itemlist


def search(item, texto):
    logger.info()

    itemlist = []

    if item.url == "":
        item.url = "http://bityouth.com/busqueda/"

    item.url = item.url + texto
    item.url = item.url.replace(" ", "%20")

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<div class="title">.*?title="([^<]+)" '
    patron += 'href="([^"]+)".*?'
    patron += '<h2 itemprop="name">([^<]+)</h2>.*?'
    patron += '<img itemprop="image" src="([^"]+)".*?'
    patron += '<a href="/year/(\d+)".*?'
    patron += '<div id="sinopsys">(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) == 0:
        itemlist.append(Item(channel=item.channel, title="[COLOR gold][B]Sin resultados...[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/jp5jx97ip/bityoucancel.png",
                             fanart="http://s6.postimg.org/vfjhen0b5/bityounieve.jpg", folder=False))

    for scrapedrate, scrapedurl, scrapedtitle, scrapedthumbnail, scrapedyear, scrapedplot in matches:
        title_fan = scrapedtitle.strip()
        if " /10" in scrapedrate:
            scrapedrate = scrapedrate.replace(" /10", " [COLOR red]Sin Puntuacion[/COLOR] ")
            scrapedrate = scrapedrate.replace("Valoracion", "")
        trailer = scrapedtitle + " " + scrapedyear + " trailer"
        trailer = urllib.quote(trailer)
        scrapedtitle = scrapedtitle.replace(scrapedtitle, "[COLOR white]" + scrapedtitle + "[/COLOR]")
        scrapedrate = scrapedrate.replace(scrapedrate, "[COLOR gold][B]" + scrapedrate + "[/B][/COLOR]")
        scrapedrate = scrapedrate.replace("Valoracion", "[COLOR skyblue]Valoracion[/COLOR]")
        if not "serie_de_tv" in item.url:
            scrapedtitle = scrapedtitle.replace("(Serie de TV)", "[COLOR royalblue](Serie de TV)[/COLOR]")
        else:
            scrapedtitle = scrapedtitle.replace("(Serie de TV)", "")

        scrapedtitle = scrapedtitle.replace("torrent", "")
        scrapedtitle = scrapedtitle.replace("torrent", "")
        title = scrapedtitle + "--" + scrapedrate
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)

        if "Miniserie de TV" in scrapedplot:
            extra = "series"
        else:
            extra = ""
        if "_serie_de_tv" in scrapedurl or "Miniserie de TV" in scrapedplot:
            import xbmc
            SEARCHDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
            urllib.urlretrieve("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/search.txt",
                               SEARCHDESTFILE)
        show = title_fan + "|" + scrapedyear + "|" + trailer
        itemlist.append(Item(channel=item.channel, action="fanart", title=title, url=url, thumbnail=thumbnail,
                             fanart="http://s6.postimg.org/y1uehu24x/bityougeneralfan.jpg", plot=trailer, show=show,
                             extra=extra, folder=True))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<li><a href="([^<]+)" title.*?Bityouth">([^<]+)</a></li>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if "Acción" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/tbbxshsgh/bityouaccionthumb.png"
            fanart = "http://s6.postimg.org/iagsnh07l/bityouaccion.jpg"
        elif "Animación" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/4w3prftjl/bityouanimacionthum.png"
            fanart = "http://s6.postimg.org/n06qc2r81/bityouanimacionfan.jpg"
        elif "Aventuras" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/bdr7ootap/bityouadventurethum.png"
            fanart = "http://s6.postimg.org/lzb30ozm9/bityouadventurefan.jpg"
        elif "Bélica" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/5fdeegac1/bityouguerrathum.png"
            fanart = "http://s6.postimg.org/acqyzkcb5/bityouguerrafan.jpg"
        elif "Ciencia" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/cxwjn31ox/bityoucienciaficcionthum.png"
            fanart = "http://s6.postimg.org/gszxpnkup/cienciaficcionbityoufan.jpg"
        elif "Cine" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/y7orbo7dd/bityoucinenegrothum.png"
            fanart = "http://s6.postimg.org/m4jfo3wb5/bityoucinenegrofan.jpg"
        elif "Comedia" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/jea3qwzm9/bityouxomediathum.png"
            fanart = "http://s6.postimg.org/v4o18asep/bityoucomediafan2.png"
        elif "Docu" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/ifyc2dbo1/bityoudocuthumb.png"
            fanart = "http://s6.postimg.org/xn9q8ze4x/bityoudocufan.jpg"
        elif "Drama" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/5r41ip5jl/bityoudramathumb.png "
            fanart = "http://s6.postimg.org/wawmku635/bityoudramafan.jpg"
        elif "Fant" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/9sl4ocxu9/bityoufantasiathum.png"
            fanart = "http://s6.postimg.org/xiakd1w7l/bityoufantasiafan.jpg"
        elif "Infantil" in scrapedtitle:
            thumbnail = "http://s6.postimg.org/j6e75o7rl/bityouinfathumb.png"
            fanart = "http://s6.postimg.org/f4s22w95d/bityouanimacionfan.jpg"
        elif "Intriga" in scrapedtitle:
            thumbnail = "http://s22.postimg.org/vpmmbystd/bityouintrigthum.png"
            fanart = "http://s27.postimg.org/zee2hh7xv/bityouintrigfan.jpg"
        elif "Musical" in scrapedtitle:
            thumbnail = "http://s8.postimg.org/u3wlw5eet/bityoumusithum.png"
            fanart = "http://s17.postimg.org/l21xuwt5r/bityoumusifan.jpg"
        elif "Romance" in scrapedtitle:
            thumbnail = "http://s4.postimg.org/q6v7eq6e5/bityouromancethum.png"
            fanart = "http://s9.postimg.org/3o4qd4dsf/bityouromancefan.jpg"
        elif "Terror" in scrapedtitle:
            thumbnail = "http://s9.postimg.org/yntipquvj/bityouterrorthum.png"
            fanart = "http://s3.postimg.org/wwq3dnpgz/bityouterrorfan.jpg"
        elif "Thr" in scrapedtitle:
            thumbnail = "http://s17.postimg.org/eldin5an3/bityouthrithum.png"
            fanart = "http://s2.postimg.org/fnqykvb9l/bityouthrifan.jpg"
        elif "West" in scrapedtitle:
            thumbnail = "http://s23.postimg.org/hjq6wjakb/bityouwesterthum.png"
            fanart = "http://s7.postimg.org/wzrh42ltn/bityouwesterfan.jpg"

        scrapedtitle = scrapedtitle.replace("ó", "o")
        scrapedtitle = scrapedtitle.replace("é", "e")
        url = "http://bityouth.com/more_elements/0/genero/" + scrapedtitle

        itemlist.append(
            Item(channel=item.channel, action="scraper", title=scrapedtitle, thumbnail=thumbnail, fanart=fanart,
                 url=url, folder=True))

    return itemlist


def scraper(item):
    logger.info()
    itemlist = []
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

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|&amp;", "", data)

    patron = '<div class="title">.*?title="([^<]+)" '
    patron += 'href="([^"]+)".*?'
    patron += '<h2 itemprop="name">([^<]+)</h2>.*?'
    patron += '<img itemprop="image" src="([^"]+)".*?'
    patron += '<a href="/year/(\d+)".*?'
    patron += '<div id="sinopsys">(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedrate, scrapedurl, scrapedtitle, scrapedthumbnail, scrapedyear, scrapedplot in matches:
        title_fan = scrapedtitle.strip()
        if " /10" in scrapedrate:
            scrapedrate = scrapedrate.replace(" /10", " [COLOR red]Sin Puntuacion[/COLOR] ")
            scrapedrate = scrapedrate.replace("Valoracion", "")
        trailer = scrapedtitle + " " + scrapedyear + " trailer"
        trailer = urllib.quote(trailer)
        scrapedtitle = scrapedtitle.replace(scrapedtitle, "[COLOR white]" + scrapedtitle + "[/COLOR]")
        scrapedrate = scrapedrate.replace(scrapedrate, "[COLOR gold][B]" + scrapedrate + "[/B][/COLOR]")
        scrapedrate = scrapedrate.replace("Valoracion", "[COLOR skyblue]Valoracion[/COLOR]")
        if not "serie_de_tv" in item.url:
            scrapedtitle = scrapedtitle.replace("(Serie de TV)", "[COLOR royalblue](Serie de TV)[/COLOR]")
        else:
            scrapedtitle = scrapedtitle.replace("(Serie de TV)", "")

        scrapedtitle = scrapedtitle.replace("torrent", "")

        title = scrapedtitle + "--" + scrapedrate
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        if "Miniserie de TV" in scrapedplot:
            extra = "series"
        else:
            extra = ""
        show = title_fan + "|" + scrapedyear + "|" + trailer
        itemlist.append(Item(channel=item.channel, action="fanart", title=title, url=url, thumbnail=thumbnail,
                             fanart="http://s6.postimg.org/y1uehu24x/bityougeneralfan.jpg", plot=trailer, extra=extra,
                             show=show, folder=True))

    # paginacion
    data = scrapertools.cache_page(item.url)
    if not "<div class=\"title\">" in data:
        itemlist.append(Item(channel=item.channel, title="[COLOR gold][B]No hay mas paginas...[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/f4es4kyfl/bityou_Sorry.png",
                             fanart="http://s6.postimg.org/y1uehu24x/bityougeneralfan.jpg", folder=False))
    else:

        current_page_number = int(scrapertools.get_match(item.url, 'more_elements/(\d+)'))
        item.url = re.sub(r"more_elements/\d+", "more_elements/{0}", item.url)

        next_page_number = current_page_number + 40
        next_page = item.url.format(next_page_number)

        title = "[COLOR skyblue]Pagina siguiente>>[/COLOR]"

        itemlist.append(Item(channel=item.channel, title=title, url=next_page,
                             fanart="http://s6.postimg.org/y1uehu24x/bityougeneralfan.jpg",
                             thumbnail="http://s6.postimg.org/kbzv91f0x/bityouflecha2.png",
                             action="scraper", folder=True))

    return itemlist


def fanart(item):
    # Vamos a sacar todos los fanarts y arts posibles
    logger.info()
    itemlist = []
    url = item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|\[.*?\]|&nbsp;", "", data)
    year = item.show.split("|")[1]
    title = item.show.split("|")[0]
    trailer = item.show.split("|")[2]
    print "joder"
    print title
    if title == "Érase una vez (Serie de TV)":
        title = "Once upon in time"

    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')
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
    if not "_serie_de_tv" in item.url and not item.extra == "series":
        title = title.replace("(Serie de TV)", "")
        title = title.replace("torrent", "")

        try:
            try:
                ###Busqueda en Tmdb la peli por titulo y año
                title_tmdb = title.replace(" ", "%20")
                url_tmdb = "http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title_tmdb + "&year=" + year + "&language=es&include_adult=false"
                data = scrapertools.cachePage(url_tmdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                id = scrapertools.get_match(data, '"page":1.*?,"id":(.*?),')
                plot = scrapertools.get_match(data, '"page":1.*?,"overview":"(.*?)",')
            except:
                if ":" in title or "(" in title:
                    title_tmdb = title.replace(" ", "%20")
                    url_tmdb = "http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title_tmdb + "&year=" + year + "&language=es&include_adult=false"
                    data = scrapertools.cachePage(url_tmdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                    id = scrapertools.get_match(data, '"page":1.*?,"id":(.*?),')
                    plot = scrapertools.get_match(data, '"page":1.*?,"overview":"(.*?)",')
                else:
                    title_tmdb = title.replace(" ", "%20")
                    title_tmdb = re.sub(r"(:.*)|\(.*?\)", "", title_tmdb)
                    url_tmdb = "http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title_tmdb + "&year=" + year + "&language=es&include_adult=false"
                    data = scrapertools.cachePage(url_tmdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                    id = scrapertools.get_match(data, '"page":1.*?,"id":(.*?),')
                    plot = scrapertools.get_match(data, '"page":1.*?,"overview":"(.*?)",')


        except:
            ###Si no hay coincidencia realiza busqueda por bing del id Imdb
            urlbing_imdb = "http://www.bing.com/search?q=%s+%s+site:imdb.com" % (title.replace(' ', '+'), year)
            data = browser(urlbing_imdb)
            '''if "z{a:1}"in data:
                data = proxy(urlbing_imdb)'''
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
                urltmdb_remote = "https://api.themoviedb.org/3/find/" + id_imdb + "?external_source=imdb_id&api_key=2e2160006592024ba87ccdf78c28f49f&language=es&include_adult=false"

                data = scrapertools.cachePage(urltmdb_remote)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                id = scrapertools.get_match(data, '"movie_results".*?,"id":(\d+)')
                plot = scrapertools.get_match(data, '"movie_results".*?,"overview":"(.*?)",')
            except:
                id = ""
                plot = ""

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
                '''if "z{a:1}"in data:
                    data = proxy(urlbing_imdb)'''
                try:
                    subdata_imdb = scrapertools.get_match(data, '<li class="b_algo">(.*?)h="ID')
                    subdata_imdb = re.sub("http://anonymouse.org/cgi-bin/anon-www.cgi/", "", subdata_imdb)
                except:
                    pass
                try:
                    url_imdb = scrapertools.get_match(subdata_imdb, '<a href="([^"]+)"')
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
                        photo_imdb = scrapertools.get_match(data, '<div class="media_index_thumb_list".*?src="([^"]+)"')
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
            extra = "http://s6.postimg.org/rv2mu3pap/bityouthsinopsis2.png"

            try:
                fanart_1 = photo_imdb3
            except:
                try:
                    fanart_1 = photo_imdb2
                except:
                    try:
                        fanart_1 = photo_imdb1
                    except:
                        fanart_1 = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"

            try:
                fanart_2 = photo_imdb4
            except:
                try:
                    fanart_2 = photo_imdb2
                except:
                    try:
                        fanart_2 = photo_imdb
                    except:
                        fanart_2 = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
            try:
                fanart_info = photo_imdb2
            except:
                try:
                    fanart_info = photo_imdb
                except:
                    fanart_info = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"

            try:
                fanart_trailer = photo_imdb3
            except:
                try:
                    fanart_trailer = photo_imdb2
                except:
                    try:
                        fanart_trailer = photo_imdb
                    except:
                        fanart_trailer = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"

            try:
                category = photo_imdb3
            except:
                try:
                    category = photo_imdb
                except:
                    try:
                        category = photo_imdb3
                    except:
                        category = "http://s6.postimg.org/mh3umjzkh/bityouthnofanventanuco.jpg"
            try:
                fanart = photo_imdb
            except:
                try:
                    fanart = photo_imdb2
                except:
                    try:
                        fanart = photo_imdb3
                    except:
                        fanart = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
            try:
                show = photo_imdb4
            except:
                try:
                    show = photo_imdb2
                except:
                    try:
                        show = photo_imdb
                    except:
                        show = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"

        ###Encontrado fanart_1 en Tmdb
        for fan in matches:

            fanart = "https://image.tmdb.org/t/p/original" + fan
            fanart_1 = fanart
            print "faan"
            print fanart_1
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
                    category = ""
            for fanart_info, fanart_trailer, fanart_2 in matches:
                fanart_info = "https://image.tmdb.org/t/p/original" + fanart_info
                fanart_trailer = "https://image.tmdb.org/t/p/original" + fanart_trailer
                fanart_2 = "https://image.tmdb.org/t/p/original" + fanart_2
                category = ""

                if fanart_info == fanart:
                    ###Busca fanart_info en Imdb si coincide con fanart
                    try:
                        url_imdbphoto = "http://www.imdb.com/title/" + id_imdb + "/mediaindex"
                        photo_imdb = scrapertools.get_match(url_imdbphoto,
                                                            '<div class="media_index_thumb_list".*?src="([^"]+)"')
                        photo_imdb = photo_imdb.replace("@._V1_UY100_CR25,0,100,100_AL_.jpg", "@._V1_SX1280_SY720_.jpg")
                        fanart_info = photo_imdb
                    except:
                        fanart_info = fanart_2

        # fanart_2 y arts

        url = "http://webservice.fanart.tv/v3/movies/" + id + "?api_key=dffe90fba4d02c199ae7a9e71330c987"
        data = scrapertools.cachePage(url)
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
            extra = "http://s6.postimg.org/rv2mu3pap/bityouthsinopsis2.png"
            show = fanart_2
            if category == "":
                category = fanart_1
            itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos_pelis", url=item.url,
                                 thumbnail=posterdb, fanart=fanart, extra=extra, show=show, category=category,
                                 folder=True))

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
                    itemlist.append(
                        Item(channel=item.channel, title=item.title, action="findvideos_pelis", url=item.url,
                             thumbnail=logo, fanart=fanart_1, extra=extra, show=show, category=category, folder=True))
                else:
                    extra = clear
                    show = fanart_2
                    if '"moviebanner"' in data:
                        category = banner
                    else:
                        category = clear
                    itemlist.append(
                        Item(channel=item.channel, title=item.title, action="findvideos_pelis", url=item.url,
                             thumbnail=logo, fanart=fanart_1, extra=extra, show=show, category=category, folder=True))

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
                    itemlist.append(
                        Item(channel=item.channel, title=item.title, action="findvideos_pelis", url=item.url,
                             thumbnail=logo, fanart=fanart_1, extra=extra, show=show, category=category, folder=True))

            if not '"hdmovieclearart"' in data and not '"moviebackground"' in data:
                extra = logo
                show = fanart_2
                if '"moviebanner"' in data:
                    category = banner
                else:
                    category = fanart_1
                itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos_pelis", url=item.url,
                                     thumbnail=logo, fanart=fanart_1, category=category, extra=extra, show=show,
                                     folder=True))

    if "_serie_de_tv" in item.url or item.extra == "series":
        # Establece destino customkey
        import xbmc
        SEARCHDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
        TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
        KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
        REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
        APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
        TRAILERDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "trailer.txt")
        item.title = item.title.replace("(Serie de TV)", "")
        title = re.sub(r"\(.*?\)", "", title).strip()
        title_tunes = (translate(title, "en"))

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
                    import xbmc
                    ###Busca música serie y caraga customkey. En la vuelta evita busqueda si ya suena música
                    url_bing = "http://www.bing.com/search?q=%s+theme+song+site:televisiontunes.com" % title_tunes.replace(
                        ' ', '+')
                    # Llamamos al browser de mechanize. Se reitera en todas las busquedas bing
                    data = browser(url_bing)
                    '''if "z{a:1}"in data:
                        data = proxy(url_bing)'''
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

                    xbmc.executebuiltin('xbmc.PlayMedia(' + song + ')')
                    import xbmc, time
                    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
                    urllib.urlretrieve(
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bityouth/test.py",
                        TESTPYDESTFILE)
                    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")

                    urllib.urlretrieve(
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bityouth/customkey.xml",
                        KEYMAPDESTFILE)
                    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
                    urllib.urlretrieve(
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bityouth/remote.xml",
                        REMOTEDESTFILE)
                    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
                    urllib.urlretrieve(
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bityouth/customapp.xml",
                        APPCOMMANDDESTFILE)

                    xbmc.executebuiltin('Action(reloadkeymaps)')

                except:
                    pass
        try:
            os.remove(TRAILERDESTFILE)
            print "Trailer.txt borrado"
            xbmc.executebuiltin('Action(reloadkeymaps)')
        except:
            print "No hay Trailer.txt"
            xbmc.executebuiltin('Action(reloadkeymaps)')
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
                print "No hay customs"
                xbmc.executebuiltin('Action(reloadkeymaps)')

        # Busqueda bing de Imdb serie id
        url_imdb = "http://www.bing.com/search?q=%s+%s+tv+series+site:imdb.com" % (title.replace(' ', '+'), year)
        print url_imdb
        data = browser(url_imdb)
        '''if "z{a:1}"in data:
            data = proxy(url_imdb)'''
        print "perro"
        print data
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

        try:
            subdata_imdb = scrapertools.get_match(data, '<li class="b_algo">(.*?)h="ID')
            print "ostia"
            print subdata_imdb
        except:
            pass
            print "joder"
        try:
            imdb_id = scrapertools.get_match(subdata_imdb, '<a href=.*?http.*?imdb.com/title/(.*?)/.*?"')
            print "siii?"
            print imdb_id
        except:
            imdb_id = ""
        ### Busca id de tvdb mediante imdb id
        urltvdb_remote = "http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=" + imdb_id + "&language=es"
        data = scrapertools.cachePage(urltvdb_remote)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
        patron = '<Data><Series><seriesid>([^<]+)</seriesid>.*?<Overview>(.*?)</Overview>'
        matches = re.compile(patron, re.DOTALL).findall(data)

        if len(matches) == 0:
            ###Si no hay coincidencia busca en tvdb directamente
            if ":" in title or "(" in title:
                title = title.replace(" ", "%20")
                url_tvdb = "http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
                data = scrapertools.cachePage(url_tvdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                patron = '<Data><Series><seriesid>([^<]+)</seriesid>.*?<Overview>(.*?)</Overview>'
                matches = re.compile(patron, re.DOTALL).findall(data)
                if len(matches) == 0:
                    title = re.sub(r"(:.*)|\(.*?\)", "", title)
                    title = title.replace(" ", "%20")
                    url_tvdb = "http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
                    data = scrapertools.cachePage(url_tvdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                    patron = '<Data><Series><seriesid>([^<]+)</seriesid>.*?<Overview>(.*?)</Overview>'
                    matches = re.compile(patron, re.DOTALL).findall(data)

                    if len(matches) == 0:
                        plot = ""
                        postertvdb = item.thumbnail
                        extra = "http://s6.postimg.org/rv2mu3pap/bityouthsinopsis2.png"
                        fanart_info = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                        fanart_trailer = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                        category = ""
                        show = title + "|" + year + "|" + "http://s6.postimg.org/mh3umjzkh/bityouthnofanventanuco.jpg"
                        itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="finvideos",
                                             thumbnail=item.thumbnail,
                                             fanart="http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg", extra=extra,
                                             category=category, show=show, plot=plot, folder=True))

            else:
                title = title.replace(" ", "%20")
                url_tvdb = "http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
                data = scrapertools.cachePage(url_tvdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                patron = '<Data><Series><seriesid>([^<]+)</seriesid>.*?<Overview>(.*?)</Overview>'
                matches = re.compile(patron, re.DOTALL).findall(data)
                if len(matches) == 0:
                    plot = ""
                    postertvdb = item.thumbnail
                    extra = "http://s6.postimg.org/rv2mu3pap/bityouthsinopsis2.png"
                    show = title + "|" + year + "|" + "http://s6.postimg.org/mh3umjzkh/bityouthnofanventanuco.jpg"
                    fanart_info = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                    fanart_trailer = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                    category = ""
                    itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                         thumbnail=item.thumbnail,
                                         fanart="http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg", extra=extra,
                                         category=category, show=show, plot=plot, folder=True))
        # fanart
        for id, info in matches:
            try:
                info = (translate(info, "es"))
            except:
                pass

            category = id
            plot = info
            id_serie = id

            url = "http://thetvdb.com/api/1D62F2F90030C444/series/" + id_serie + "/banners.xml"

            data = scrapertools.cachePage(url)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            patron = '<Banners><Banner>.*?<VignettePath>(.*?)</VignettePath>'
            matches = re.compile(patron, re.DOTALL).findall(data)
            try:
                postertvdb = scrapertools.get_match(data, '<Banners><Banner>.*?<BannerPath>posters/(.*?)</BannerPath>')
                postertvdb = "http://thetvdb.com/banners/_cache/posters/" + postertvdb
            except:
                postertvdb = item.thumbnail

            if len(matches) == 0:
                extra = "http://s6.postimg.org/rv2mu3pap/bityouthsinopsis2.png"
                show = title + "|" + year + "|" + "http://s6.postimg.org/mh3umjzkh/bityouthnofanventanuco.jpg"
                fanart_info = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                fanart_trailer = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                     thumbnail=postertvdb, fanart="http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg",
                                     category=category, extra=extra, show=show, folder=True))

            for fan in matches:
                fanart = "http://thetvdb.com/banners/" + fan
                fanart_1 = fanart
                patron = '<Banners><Banner>.*?<BannerPath>.*?</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>'
                matches = re.compile(patron, re.DOTALL).findall(data)
                if len(matches) == 0:
                    fanart_info = fanart_1
                    fanart_trailer = fanart_1
                    fanart_2 = fanart_1
                    show = title + "|" + year + "|" + fanart_1
                    extra = postertvdb
                    itemlist.append(Item(channel=item.channel, title=item.title, url=item.url, action="findvideos",
                                         thumbnail=postertvdb, fanart=fanart_1, category=category, extra=extra,
                                         show=show, folder=True))
                for fanart_info, fanart_trailer, fanart_2 in matches:
                    fanart_info = "http://thetvdb.com/banners/" + fanart_info
                    fanart_trailer = "http://thetvdb.com/banners/" + fanart_trailer
                    fanart_2 = "http://thetvdb.com/banners/" + fanart_2
        # clearart, fanart_2 y logo
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
                            show = title + "|" + year + "|" + fanart_2
                        else:
                            thumbnail = hdtvlogo
                            extra = thumbnail
                            show = title + "|" + year + "|" + fanart_2
                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=thumbnail, fanart=fanart_1, category=category,
                                             extra=extra, show=show, plot=item.plot, folder=True))


                    else:
                        if '"hdclearart"' in data:
                            thumbnail = hdtvlogo
                            extra = hdtvclear
                            show = title + "|" + year + "|" + fanart_2
                        else:
                            thumbnail = hdtvlogo
                            extra = thumbnail
                            show = title + "|" + year + "|" + fanart_2

                        itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                             server="torrent", thumbnail=thumbnail, fanart=fanart_1, extra=extra,
                                             show=show, category=category, plot=item.plot, folder=True))
                else:
                    extra = "http://s6.postimg.org/rv2mu3pap/bityouthsinopsis2.png"
                    show = title + "|" + year + "|" + fanart_2
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                         server="torrent", thumbnail=item.thumbnail, fanart=fanart_1, extra=extra,
                                         show=show, category=category, plot=item.plot, folder=True))
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
                    show = title + "|" + year + "|" + fanart_2
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                         server="torrent", thumbnail=thumbnail, fanart=fanart_1, extra=extra, show=show,
                                         category=category, plot=item.plot, folder=True))
                else:
                    extra = clear
                    show = title + "|" + year + "|" + fanart_2
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                         server="torrent", thumbnail=thumbnail, fanart=fanart_1, extra=extra, show=show,
                                         category=category, plot=item.plot, folder=True))

            if "showbackground" in data:

                if '"clearart"' in data:
                    clear = scrapertools.get_match(data, '"clearart":.*?"url": "([^"]+)"')
                    extra = clear
                    show = title + "|" + year + "|" + fanart_2
                else:
                    extra = logo
                    show = title + "|" + year + "|" + fanart_2
                    itemlist.append(Item(channel=item.channel, title=item.title, action="findvideos", url=item.url,
                                         server="torrent", thumbnail=thumbnail, fanart=fanart_1, extra=extra, show=show,
                                         category=category, plot=item.plot, folder=True))

            if not '"clearart"' in data and not '"showbackground"' in data:
                if '"hdclearart"' in data:
                    extra = hdtvclear
                    show = title + "|" + year + "|" + fanart_2
                else:
                    extra = thumbnail
                    show = title + "|" + year + "|" + fanart_2
                itemlist.append(
                    Item(channel=item.channel, title=item.title, action="findvideos", url=item.url, server="torrent",
                         thumbnail=thumbnail, fanart=fanart_1, extra=extra, show=show, category=category,
                         plot=item.plot, folder=True))

    title = "Info"
    if not "_serie_de_tv" in item.url and not item.extra == "series":
        thumbnail = posterdb
    if "_serie_de_tv" in item.url or item.extra == "series":
        if '"tvposter"' in data:
            thumbnail = tvposter
        else:
            thumbnail = postertvdb

        if "tvbanner" in data:
            category = tvbanner
        else:
            category = item.show.split("|")[2]

    title = title.replace(title, "[COLOR cyan]" + title + "[/COLOR]")
    itemlist.append(
        Item(channel=item.channel, action="info", title=title, url=item.url, thumbnail=thumbnail, fanart=fanart_info,
             extra=extra, plot=plot, category=category, show=show, folder=False))
    ###trailer


    title = "[COLOR gold]Trailer[/COLOR]"

    if "_serie_de_tv" in item.url or item.extra == "series":
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

    itemlist.append(
        Item(channel=item.channel, action="trailer", title=title, url=item.url, thumbnail=thumbnail, plot=item.plot,
             fanart=fanart_trailer, extra=extra, show=trailer, folder=True))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    import xbmc
    SEARCHDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
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

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<a class="btn btn-success" href="([^"]+)" role="button".*?'
    patron += '<td><div style="width:125px.*?<td><small>([^<]+)</small>.*?'
    patron += '<td><small>([^<]+)</small>.*?'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) == 0:
        itemlist.append(Item(channel=item.channel,
                             title="[COLOR gold][B]Lo sentimos el torrent aún no está disponible...[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/f4es4kyfl/bityou_Sorry.png",
                             fanart="http://s6.postimg.org/guxt62fyp/bityounovideo.jpg", folder=False))

    for scrapedurl, scrapedcalidad, scrapedsize in matches:

        scrapedurl = urlparse.urljoin(host, scrapedurl)
        season = scrapedcalidad
        season = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|V.O.S|Cast|Temp.|Cap.\d+| ", "", season)
        epi = scrapedcalidad
        epi = re.sub(r"\n|\r|\t|\s{2}|V.O.S|Cast|&nbsp;|Temp.\d+|Cap.| ", "", epi)
        title = scrapertools.get_match(item.title, '(.*?)--')
        title_info = scrapertools.get_match(data, '<meta name="title" content="(.*?) -')
        title_info = title_info.replace("(Serie de TV)", "")
        title_info = title_info.replace("torrent", "")
        title_info = title_info.replace(" ", "%20")
        scrapedcalidad = scrapedcalidad.replace(scrapedcalidad, "[COLOR skyblue][B]" + scrapedcalidad + "[/B][/COLOR]")
        scrapedsize = scrapedsize.replace(scrapedsize, "[COLOR gold][B]" + scrapedsize + "[/B][/COLOR]")
        title = title.replace(title,
                              "[COLOR white][B]" + title + "[/B][/COLOR]") + "-(" + scrapedcalidad + "/" + scrapedsize + ")"

        if "bityouthsinopsis2.png" in item.extra:
            item.extra = item.thumbnail
        if "bityouthnofanventanuco.jpg" in item.show.split("|")[2]:
            fanart = item.fanart
        else:
            fanart = item.show.split("|")[2]

        extra = season + "|" + title_info + "|" + epi
        itemlist.append(
            Item(channel=item.channel, title=title, action="episodios", url=scrapedurl, thumbnail=item.extra,
                 fanart=item.show.split("|")[2], extra=extra, show=item.show, category=item.category, folder=True))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
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

    season = item.extra.split("|")[0]
    title = item.show.split("|")[0]
    if title == "Invisibles":
        title = "The whispers"
    epi = item.extra.split("|")[2]
    year = item.show.split("|")[1]
    title_tag = "[COLOR yellow]Ver --[/COLOR]"
    item.title = item.title.replace("amp", "")
    title_clean = title_tag + item.title
    if ":" in title:
        try:
            title = title.replace(" ", "%20")
            url_tmdb = "http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title + "&year=" + year + "&language=es&include_adult=false"
            data = scrapertools.cachePage(url_tmdb)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            id_tmdb = scrapertools.get_match(data, 'page":1.*?,"id":(.*?),"')
        except:
            try:
                title = re.sub(r"(:.*)", "", title)
                title = title.replace(" ", "%20")
                url_tmdb = "http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title + "&year=" + year + "&language=es&include_adult=false"
                data = scrapertools.cachePage(url_tmdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
                id_tmdb = scrapertools.get_match(data, 'page":1.*?,"id":(.*?),"')
            except:
                thumbnail = item.thumbnail
                fanart = item.fanart
                id_tmdb = ""
    else:
        try:
            title = title.replace(" ", "%20")
            url_tmdb = "http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title + "&year=" + year + "&language=es&include_adult=false"
            data = scrapertools.cachePage(url_tmdb)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            id_tmdb = scrapertools.get_match(data, 'page":1.*?,"id":(.*?),"')
        except:
            thumbnail = item.thumbnail
            fanart = item.fanart
            id_tmdb = ""
    ###Teniendo (o no) el id Tmdb busca imagen
    urltmdb_images = "https://api.themoviedb.org/3/tv/" + id_tmdb + "?api_key=2e2160006592024ba87ccdf78c28f49f"
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
    urltmdb_epi = "https://api.themoviedb.org/3/tv/" + id_tmdb + "/season/" + season + "/episode/" + epi + "/images?api_key=2e2160006592024ba87ccdf78c28f49f"
    data = scrapertools.cachePage(urltmdb_epi)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '{"id".*?"file_path":"(.*?)","height"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        thumbnail = item.thumbnail
        fanart = fanart_3
        itemlist.append(Item(channel=item.channel, title=title_clean, action="play", url=item.url, server="torrent",
                             thumbnail=thumbnail, fanart=fanart, folder=False))

    for foto in matches:
        thumbnail = "https://image.tmdb.org/t/p/original" + foto
        itemlist.append(Item(channel=item.channel, title=title_clean, action="play", url=item.url, server="torrent",
                             thumbnail=thumbnail, fanart=fanart, category=item.category, folder=False))
        ###thumb temporada###
    urltmdb_temp = "http://api.themoviedb.org/3/tv/" + id_tmdb + "/season/" + season + "/images?api_key=2e2160006592024ba87ccdf78c28f49f"
    data = scrapertools.cachePage(urltmdb_temp)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '{"id".*?"file_path":"(.*?)","height"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        thumbnail = item.thumbnail
    for temp in matches:
        thumbnail = "https://image.tmdb.org/t/p/original" + temp
    ####fanart info####
    urltmdb_faninfo = "http://api.themoviedb.org/3/tv/" + id_tmdb + "/images?api_key=2e2160006592024ba87ccdf78c28f49f"
    data = scrapertools.cachePage(urltmdb_faninfo)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '{"backdrops".*?"file_path":".*?","height".*?"file_path":"(.*?)",'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        fanart = item.fanart
    for fanart_4 in matches:
        fanart = "https://image.tmdb.org/t/p/original" + fanart_4

    show = item.category + "|" + item.thumbnail

    title = "Info"
    title = title.replace(title, "[COLOR skyblue]" + title + "[/COLOR]")
    itemlist.append(Item(channel=item.channel, action="info_capitulos", title=title, url=item.url, thumbnail=thumbnail,
                         fanart=fanart, extra=item.extra, show=show, folder=False))

    return itemlist


def findvideos_pelis(item):
    logger.info()
    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<td><a class="btn btn-success" href="([^"]+)" role="button".*?'
    patron += '<td><div style="width:125px.*?<td><small>([^<]+)</small>.*?'
    patron += '<td><small>([^<]+)</small>.*?'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) == 0:
        itemlist.append(Item(channel=item.channel,
                             title="[COLOR gold][B]Lo sentimos el torrent aún no está disponible...[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/f4es4kyfl/bityou_Sorry.png",
                             fanart="http://s6.postimg.org/guxt62fyp/bityounovideo.jpg", folder=False))

    for scrapedurl, scrapedcalidad, scrapedsize in matches:

        scrapedurl = urlparse.urljoin(host, scrapedurl)

        title = scrapertools.get_match(data, '<meta name="title" content="(.*?) -')
        title = title.replace("(Serie de TV)", "")
        title = title.replace("torrent", "")
        title_info = scrapertools.get_match(data, '<meta name="title" content="(.*?) -')
        title_info = title_info.replace("(Serie de TV)", "")
        title_info = title_info.replace("torrent", "")
        scrapedcalidad = scrapedcalidad.replace(scrapedcalidad, "[COLOR skyblue][B]" + scrapedcalidad + "[/B][/COLOR]")
        scrapedsize = scrapedsize.replace(scrapedsize, "[COLOR gold][B]" + scrapedsize + "[/B][/COLOR]")
        title = title.replace(title,
                              "[COLOR white][B]" + title + "[/B][/COLOR]") + "-(" + scrapedcalidad + "/" + scrapedsize + ")"
        if "bityouthsinopsis2.png" in item.extra:
            item.extra = item.thumbnail

        itemlist.append(Item(channel=item.channel, title=title, url=scrapedurl, fanart=item.show, thumbnail=item.extra,
                             action="play", folder=False))

    return itemlist


def trailer(item):
    logger.info()
    itemlist = []
    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    if os.path.exists(TESTPYDESTFILE):
        TRAILERDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "trailer.txt")
        urllib.urlretrieve("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/trailer.txt",
                           TRAILERDESTFILE)
    youtube_trailer = "https://www.youtube.com/results?search_query=" + item.show + "español"

    data = scrapertools.cache_page(youtube_trailer)

    patron = '<a href="/watch?(.*?)".*?'
    patron += 'title="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches) == 0:
        itemlist.append(Item(channel=item.channel, title="[COLOR gold][B]No hay Trailer[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/jp5jx97ip/bityoucancel.png",
                             fanart="http://s6.postimg.org/vfjhen0b5/bityounieve.jpg", folder=False))

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = "https://www.youtube.com/watch" + scrapedurl
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace(scrapedtitle, "[COLOR khaki][B]" + scrapedtitle + "[/B][/COLOR]")
        itemlist.append(Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, server="youtube",
                             fanart="http://s6.postimg.org/g4gxuw91r/bityoutrailerfn.jpg", thumbnail=item.extra,
                             action="play", folder=False))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.server == "youtube":
        itemlist.append(Item(channel=item.channel, title=item.plot, url=item.url, server="youtube", fanart=item.fanart,
                             thumbnail=item.thumbnail, action="play", folder=False))

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<td><a class="btn btn-success" href="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl in matches:
        itemlist.append(Item(channel=item.channel, title=item.title, server="torrent", url=scrapedurl,
                             fanart="http://s9.postimg.org/lmwhrdl7z/aquitfanart.jpg", thumbnail=item.thumbnail,
                             action="play", folder=True))

    return itemlist


def info(item):
    logger.info()
    url = item.url
    if "_serie_de_tv" in item.url:
        import xbmc
        APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
        try:
            os.remove(APPCOMMANDDESTFILE)
        except:
            pass

    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|Descarga el torrent.*?en Bityouth.", "", data)
    title = scrapertools.get_match(data, '<meta name="title" content="(.*?) -')
    title = title.upper()
    title = title.replace(title, "[COLOR gold][B]" + title + "[/B][/COLOR]")
    title = title.replace("TORRENT", "")
    try:
        try:
            plot = scrapertools.get_match(data, '<div itemprop="description">(.*?)<a href="#enlaces">')
        except:
            plot = item.plot

        plot = plot.replace(plot, "[COLOR bisque][B]" + plot + "[/B][/COLOR]")
        plot = plot.replace("</i>", "")
        plot = plot.replace("</br>", "")
        plot = plot.replace("<br/>", "")
        plot = plot.replace("&#8220", "")
        plot = plot.replace("<b>", "")
        plot = plot.replace("</b>", "")
        plot = plot.replace(" &#8203;&#8203;", "")
        plot = scrapertools.decodeHtmlentities(plot)
        plot = plot.replace("&quot;", "")
    except:

        title = "[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
        plot = "Esta serie no tiene informacion..."
        plot = plot.replace(plot, "[COLOR yellow][B]" + plot + "[/B][/COLOR]")
        photo = "http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        foto = "http://s6.postimg.org/ub7pb76c1/noinfo.png"
        info = ""
        quit = "Pulsa" + " [COLOR blue][B]INTRO [/B][/COLOR]" + "para quitar"
    try:
        scrapedinfo = scrapertools.get_match(data, '<div class="col-sm-5 col-md-5 col-lg-4">(.*?)Título Original:')
        infoformat = re.compile('(.*?:).*?</strong>(.*?)<strong>', re.DOTALL).findall(scrapedinfo)
        for info, info2 in infoformat:
            scrapedinfo = scrapedinfo.replace(info2, "[COLOR bisque]" + info2 + "[/COLOR]")
            scrapedinfo = scrapedinfo.replace(info, "[COLOR aqua][B]" + info + "[/B][/COLOR]")
        info = scrapedinfo
        info = re.sub(
            r'<p class=".*?">|<strong>|</strong>|<a href="/year/.*?">| title=".*?"|alt=".*?"|>#2015|</a>|<span itemprop=".*?".*?>|<a.*?itemprop=".*?".*?">|</span>|<a href="/genero/.*?"|<a href=".*?"|itemprop="url">|"|</div><div class="col-sm-7 col-md-7 col-lg-8">|>,',
            '', info)
        info = info.replace("</p>", " ")
        info = info.replace("#", ",")
        info = info.replace(">", "")
    except:
        info = "[COLOR skyblue][B]Sin informacion adicional...[/B][/COLOR]"
    if "_serie_de_tv" in item.url:
        foto = item.show.split("|")[2]

    else:
        foto = item.category
        if item.show == item.thumbnail:
            foto = "http://s6.postimg.org/mh3umjzkh/bityouthnofanventanuco.jpg"
    photo = item.extra
    quit = "Pulsa" + " [COLOR blue][B]INTRO [/B][/COLOR]" + "para quitar"
    if "_serie_de_tv" in item.url:
        NOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "noback.xml")
        REMOTENOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remotenoback.xml")
        APPNOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "appnoback.xml")
        urllib.urlretrieve("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/noback.xml",
                           NOBACKDESTFILE)
        urllib.urlretrieve(
            "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bityouth/remotenoback.xml",
            REMOTENOBACKDESTFILE)
        urllib.urlretrieve("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/appnoback.xml",
                           APPNOBACKDESTFILE)
        xbmc.executebuiltin('Action(reloadkeymaps)')

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
            import os
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
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bityouth/customapp.xml",
                        APPCOMMANDDESTFILE)
                xbmc.executebuiltin('Action(reloadkeymaps)')
            except:
                xbmc.executebuiltin('Action(reloadkeymaps)')
            self.close()


def info_capitulos(item):
    logger.info()
    import xbmc
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    try:
        os.remove(APPCOMMANDDESTFILE)
    except:
        pass
    item.category = item.show.split("|")[0]
    item.thumbnail = item.show.split("|")[1]

    url = "http://thetvdb.com/api/1D62F2F90030C444/series/" + item.show.split("|")[0] + "/default/" + \
          item.extra.split("|")[0] + "/" + item.extra.split("|")[2] + "/es.xml"
    data = scrapertools.cache_page(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '<Data>.*?<EpisodeName>([^<]+)</EpisodeName>.*?'
    patron += '<Overview>(.*?)</Overview>.*?'

    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) == 0:
        title = "[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
        plot = "Este capitulo no tiene informacion..."
        plot = plot.replace(plot, "[COLOR yellow][B]" + plot + "[/B][/COLOR]")
        foto = "http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        image = "http://s6.postimg.org/ub7pb76c1/noinfo.png"
        quit = "Pulsa" + " [COLOR greenyellow][B]INTRO [/B][/COLOR]" + "para quitar"

    else:

        for name_epi, info in matches:
            if "<filename>episodes" in data:
                foto = scrapertools.get_match(data, '<Data>.*?<filename>(.*?)</filename>')
                fanart = "http://thetvdb.com/banners/" + foto
            else:
                fanart = item.show.split("|")[1]

            plot = info
            plot = plot.replace(plot, "[COLOR burlywood][B]" + plot + "[/B][/COLOR]")
            title = name_epi.upper()
            title = title.replace(title, "[COLOR skyblue][B]" + title + "[/B][/COLOR]")
            image = fanart
            foto = item.show.split("|")[1]
            if not ".png" in item.show.split("|")[1]:
                foto = "http://s6.postimg.org/rv2mu3pap/bityouthsinopsis2.png"
            quit = "Pulsa" + " [COLOR greenyellow][B]INTRO [/B][/COLOR]" + "para quitar"
            NOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "noback.xml")
            REMOTENOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remotenoback.xml")
            APPNOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "appnoback.xml")
            TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
            urllib.urlretrieve("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/noback.xml",
                               NOBACKDESTFILE)
            urllib.urlretrieve(
                "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bityouth/remotenoback.xml",
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
        self.quit = xbmcgui.ControlTextBox(145, 90, 1030, 45)
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
            import os
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
                        "https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bityouth/customapp.xml",
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
