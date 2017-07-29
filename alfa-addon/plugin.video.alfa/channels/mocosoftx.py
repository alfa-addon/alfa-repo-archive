# -*- coding: utf-8 -*-

import re
import urllib
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import platformtools

MAIN_HEADERS = []
MAIN_HEADERS.append(["Host", "mocosoftx.com"])
MAIN_HEADERS.append(["User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:8.0) Gecko/20100101 Firefox/8.0"])
MAIN_HEADERS.append(["Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"])
MAIN_HEADERS.append(["Accept-Language", "es-es,es;q=0.8,en-us;q=0.5,en;q=0.3"])
MAIN_HEADERS.append(["Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7"])
MAIN_HEADERS.append(["Connection", "keep-alive"])


# Login:
# <form action="http://mocosoftx.com/foro/login2/" method="post" accept-charset="ISO-8859-1" onsubmit="hashLoginPassword(this, '3e468fdsab5d9');" >
# pst: user=blablabla&passwrd=&cookielength=-1&hash_passwrd=78e88DSe408508d22f
# doForm.hash_passwrd.value = hex_sha1(hex_sha1(doForm.user.value.php_to8bit().php_strtolower() + doForm.passwrd.value.php_to8bit()) + cur_session_id);
def login():
    # Averigua el id de sesión
    data = scrapertools.cache_page("http://mocosoftx.com/foro/login/")
    cur_session_id = scrapertools.get_match(data,
                                            'form action="[^"]+" name="frmLogin" id="frmLogin" method="post" accept-charset="ISO-8859-1"  onsubmit="hashLoginPassword\(this, \'([a-z0-9]+)\'')
    cur_session_id = "c95633073dc6afaa813d33b2bfeda520"
    logger.info("cur_session_id=" + cur_session_id)

    # Calcula el hash del password
    email = config.get_setting("mocosoftxuser", "mocosoftx")
    password = config.get_setting("mocosoftxpassword", "mocosoftx")
    logger.info("email=" + email)
    logger.info("password=" + password)

    # doForm.hash_passwrd.value = hex_sha1(hex_sha1(doForm.user.value.php_to8bit().php_strtolower() + doForm.passwrd.value.php_to8bit()) + cur_session_id);
    hash_passwrd = scrapertools.get_sha1(scrapertools.get_sha1(email.lower() + password.lower()) + cur_session_id)
    logger.info("hash_passwrd=" + hash_passwrd)

    # Hace el submit del email
    # post = "user="+email+"&passwrd=&cookieneverexp=on&hash_passwrd="+hash_passwrd
    post = urllib.urlencode({'user': email, "passwrd": password}) + "&cookieneverexp=on&hash_passwrd="
    logger.info("post=" + post)

    headers = []
    headers.append(["Host", "mocosoftx.com"])
    headers.append(["User-Agent",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"])
    headers.append(["Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"])
    headers.append(["Accept-Language", "es-ES,es;q=0.8,en;q=0.6,gl;q=0.4"])
    headers.append(["Accept-Encoding", "gzip, deflate"])
    headers.append(["Connection", "keep-alive"])
    headers.append(["Referer", "http://mocosoftx.com/foro/login/"])
    headers.append(["Origin", "http://mocosoftx.com"])
    headers.append(["Content-Type", "application/x-www-form-urlencoded"])
    headers.append(["Content-Length", str(len(post))])
    headers.append(["Cache-Control", "max-age=0"])
    headers.append(["Upgrade-Insecure-Requests", "1"])

    data = scrapertools.cache_page("http://mocosoftx.com/foro/login2/", post=post, headers=headers)
    logger.info("data=" + data)

    return True


def mainlist(item):
    logger.info()
    itemlist = []

    if config.get_setting("mocosoftxuser", "mocosoftx") == "":
        itemlist.append(
            Item(channel=item.channel, title="Habilita tu cuenta en la configuración...", action="settingCanal",
                 url=""))
    else:
        if login():
            item.url = "http://mocosoftx.com/foro/forum/"
            itemlist = foro(item)
            itemlist.append(Item(channel=item.channel, action="settingCanal", title="Configuración...", url=""))
        else:
            itemlist.append(
                Item(channel=item.channel, title="Cuenta incorrecta, revisa la configuración...", action="", url="",
                     folder=False))

    return itemlist


def settingCanal(item):
    return platformtools.show_channel_settings()


def foro(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url, headers=MAIN_HEADERS)

    # Extrae los foros y subforos
    patron = '<h4><a href="([^"]+)"[^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = unicode(scrapedtitle, "iso-8859-1", errors="replace").encode("utf-8")
        title = ">> Foro " + scrapedtitle
        url = urlparse.urljoin(item.url, scrapedurl)
        # http://mocosoftx.com/foro/fotos-hentai/?PHPSESSID=nflddqf9nvbm2dd92
        if "PHPSESSID" in url:
            url = scrapertools.get_match(url, "(.*?)\?PHPSESSID=")
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, title=title, action="foro", url=url, plot=plot, thumbnail=thumbnail,
                             folder=True))

    # Extrae los hilos individuales
    patron = '<td class="icon2 windowbgb">[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</td>[^<]+'
    patron += '<td class="subject windowbgb2">[^<]+'
    patron += '<div >[^<]+'
    patron += '<span id="msg_\d+"><a href="([^"]+)">([^>]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url, scrapedurl)
        if "PHPSESSID" in url:
            url = scrapertools.get_match(url, "(.*?)\?PHPSESSID=")
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(
            Item(channel=item.channel, title=title, action="findvideos", url=url, plot=plot, thumbnail=thumbnail,
                 folder=True))

    # Extrae la marca de siguiente página
    # <a class="navPages" href="http://mocosoftx.com/foro/peliculas-xxx-online-(completas)/20/?PHPSESSID=rpejdrj1trngh0sjdp08ds0ef7">2</a>
    patronvideos = '<strong>\d+</strong[^<]+<a class="navPages" href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        scrapedtitle = ">> Página siguiente"
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        if "PHPSESSID" in scrapedurl:
            scrapedurl = scrapertools.get_match(scrapedurl, "(.*?)\?PHPSESSID=")
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(Item(channel=item.channel, title=scrapedtitle, action="foro", url=scrapedurl, plot=scrapedplot,
                             thumbnail=scrapedthumbnail, folder=True))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    # Busca el thumbnail y el argumento
    data = scrapertools.cache_page(item.url)
    logger.info("data=" + data)

    try:
        thumbnail = scrapertools.get_match(data, '<div class="post">.*?<img src="([^"]+)"')
    except:
        thumbnail = ""

    plot = ""

    # Ahora busca los vídeos
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.plot = plot
        videoitem.thumbnail = thumbnail
        videoitem.fulltitle = item.title

        parsed_url = urlparse.urlparse(videoitem.url)
        fichero = parsed_url.path
        partes = fichero.split("/")
        titulo = partes[len(partes) - 1]
        videoitem.title = titulo + " - [" + videoitem.server + "]"

    if not itemlist:

        patron = '<a href="([^"]+)" class="bbc_link" target="_blank"><span style="color: orange;" class="bbc_color">'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if matches:
            data = scrapertools.cache_page(matches[0])
            logger.info(data)
            itemlist = servertools.find_video_items(data=data)
            for videoitem in itemlist:
                videoitem.channel = item.channel
                videoitem.plot = plot
                videoitem.thumbnail = thumbnail
                videoitem.fulltitle = item.title

                parsed_url = urlparse.urlparse(videoitem.url)
                fichero = parsed_url.path
                partes = fichero.split("/")
                titulo = partes[len(partes) - 1]
                videoitem.title = titulo + " - [" + videoitem.server + "]"

    return itemlist
