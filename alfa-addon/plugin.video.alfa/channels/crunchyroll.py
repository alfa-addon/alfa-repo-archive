# -*- coding: utf-8 -*-

import re
import urllib

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core.item import Item

__perfil__ = config.get_setting('perfil', "crunchyroll")

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00', '0xFFFE2E2E', '0xFF088A08'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E', '0xFFFE2E2E', '0xFF088A08'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE', '0xFFFE2E2E', '0xFF088A08']]

if __perfil__ - 1 >= 0:
    color1, color2, color3, color4, color5 = perfil[__perfil__ - 1]
else:
    color1 = color2 = color3 = color4 = color5 = ""

host = "http://www.crunchyroll.com"
proxy_u = "http://anonymouse.org/cgi-bin/anon-www.cgi/"
proxy_e = "http://proxyanonimo.es/browse.php?u="


def login():
    logger.info()

    langs = ['deDE', 'ptPT', 'frFR', 'itIT', 'enUS', 'esLA', 'esES']
    lang = langs[config.get_setting("crunchyrollidioma", "crunchyroll")]
    httptools.downloadpage("http://www.crunchyroll.com/ajax/", "req=RpcApiTranslation_SetLang&locale=%s" % lang)

    login_page = "https://www.crunchyroll.com/login"
    user = config.get_setting("crunchyrolluser", "crunchyroll")
    password = config.get_setting("crunchyrollpassword", "crunchyroll")
    if not user or not password:
        return False, "", ""
    data = httptools.downloadpage(login_page).data

    if not "<title>Redirecting" in data:
        token = scrapertools.find_single_match(data, 'name="login_form\[_token\]" value="([^"]+)"')
        redirect_url = scrapertools.find_single_match(data, 'name="login_form\[redirect_url\]" value="([^"]+)"')
        post = "login_form%5Bname%5D=" + user + "&login_form%5Bpassword%5D=" + password + \
               "&login_form%5Bredirect_url%5D=" + redirect_url + "&login_form%5B_token%5D=" + token

        data = httptools.downloadpage(login_page, post).data
        if not "<title>Redirecting" in data:
            if "Usuario %s no disponible" % user in data:
                return False, "El usuario de crunchyroll no existe.", ""
            elif '<li class="error">Captcha' in data:
                return False, "Es necesario resolver un captcha. Loguéate desde un navegador y vuelve a intentarlo", ""
            else:
                return False, "No se ha podido realizar el login.", ""

    data = httptools.downloadpage(host).data
    premium = scrapertools.find_single_match(data, ',"premium_status":"([^"]+)"')
    premium = premium.replace("_", " ").replace("free trial", "Prueba Gratuita").capitalize()
    locate = scrapertools.find_single_match(data, 'title="Your detected location is (.*?)."')
    if locate:
        premium += " - %s" % locate
    return True, "", premium


def mainlist(item):
    logger.info()
    itemlist = []
    item.text_color = color1

    proxy_usa = config.get_setting("proxy_usa", "crunchyroll")
    proxy_spain = config.get_setting("proxy_spain", "crunchyroll")
    item.login = False
    error_message = ""
    global host
    if not proxy_usa and not proxy_spain:
        item.login, error_message, premium = login()
    elif proxy_usa:
        item.proxy = "usa"
        host = proxy_u + host
    elif proxy_spain:
        httptools.downloadpage("http://proxyanonimo.es/")
        item.proxy = "spain"
        host = proxy_e + host

    if not item.login and error_message:
        itemlist.append(item.clone(title=error_message, action="configuracion", folder=False, text_color=color4))
    elif item.login:
        itemlist.append(item.clone(title="Tipo de cuenta: %s" % premium, action="", text_color=color4))
    elif item.proxy:
        itemlist.append(item.clone(title="Usando proxy: %s" % item.proxy.capitalize(), action="", text_color=color4))

    itemlist.append(item.clone(title="Anime", action="", text_color=color2))
    item.contentType = "tvshow"
    itemlist.append(
        item.clone(title="     Novedades", action="lista", url=host + "/videos/anime/updated/ajax_page?pg=0", page=0))
    itemlist.append(
        item.clone(title="     Popular", action="lista", url=host + "/videos/anime/popular/ajax_page?pg=0", page=0))
    itemlist.append(item.clone(title="     Emisiones Simultáneas", action="lista",
                               url=host + "/videos/anime/simulcasts/ajax_page?pg=0", page=0))
    itemlist.append(item.clone(title="     Índices", action="indices"))

    itemlist.append(item.clone(title="Drama", action="", text_color=color2))
    itemlist.append(
        item.clone(title="     Popular", action="lista", url=host + "/videos/drama/popular/ajax_page?pg=0", page=0))
    itemlist.append(item.clone(title="     Índice Alfabético", action="indices",
                               url="http://www.crunchyroll.com/videos/drama/alpha"))

    if item.proxy != "usa":
        itemlist.append(item.clone(action="calendario", title="Calendario de Estrenos Anime", text_color=color4,
                                   url=host + "/simulcastcalendar"))
    itemlist.append(item.clone(title="Configuración del canal", action="configuracion", text_color="gold"))

    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()

    user = config.get_setting("crunchyrolluser", "crunchyroll")
    password = config.get_setting("crunchyrollpassword", "crunchyroll")
    sub = config.get_setting("crunchyrollsub", "crunchyroll")

    config.set_setting("crunchyrolluser", user)
    config.set_setting("crunchyrollpassword", password)
    values = [6, 5, 4, 3, 2, 1, 0]
    config.set_setting("crunchyrollsub", str(values[sub]))
    platformtools.itemlist_refresh()

    return ret


def lista(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    next = item.url.replace("?pg=%s" % item.page, "?pg=%s" % str(item.page + 1))
    data_next = httptools.downloadpage(next).data
    patron = '<li id="media_group_(\d+)".*?title="([^"]+)".*?href="([^"]+)".*?src="([^"]+)"' \
             '.*?<span class="series-data.*?>\s*([^<]+)</span>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for id, title, url, thumb, videos in matches:
        if item.proxy == "spain":
            url = "http://proxyanonimo.es" + url.replace("&amp;b=12", "")
        elif not item.proxy:
            url = host + url
        thumb = urllib.unquote(thumb.replace("/browse.php?u=", "").replace("_thumb", "_full").replace("&amp;b=12", ""))
        scrapedtitle = "%s (%s)" % (title, videos.strip())
        plot = scrapertools.find_single_match(data, '%s"\).data.*?description":"([^"]+)"' % id)
        plot = unicode(plot, 'unicode-escape', "ignore")
        itemlist.append(item.clone(action="episodios", url=url, title=scrapedtitle, thumbnail=thumb,
                                   contentTitle=title, contentSerieName=title, infoLabels={'plot': plot},
                                   text_color=color2))

    if '<li id="media_group' in data_next:
        itemlist.append(item.clone(action="lista", url=next, title=">> Página Siguiente", page=item.page + 1,
                                   text_color=""))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\t|\s{2,}', '', data)
    patron = '<li id="showview_videos.*?href="([^"]+)".*?(?:src|data-thumbnailUrl)="([^"]+)".*?media_id="([^"]+)" ' \
             'style="width: (.*?)%.*?<span class="series-title.*?>\s*(.*?)</span>.*?<p class="short-desc".*?>' \
             '\s*(.*?)</p>.*?description":"([^"]+)"'
    if data.count('class="season-dropdown') > 1:
        bloques = scrapertools.find_multiple_matches(data, 'class="season-dropdown[^"]+" title="([^"]+)"(.*?)</ul>')
        for season, b in bloques:
            matches = scrapertools.find_multiple_matches(b, patron)
            if matches:
                itemlist.append(item.clone(action="", title=season, text_color=color3))
            for url, thumb, media_id, visto, title, subt, plot in matches:
                if item.proxy == "spain":
                    url = urllib.unquote(url.replace("/browse.php?u=", "").replace("&amp;b=12", ""))
                elif not item.proxy:
                    url = host + url
                url = url.replace(proxy_u, "")
                thumb = urllib.unquote(
                    thumb.replace("/browse.php?u=", "").replace("_wide.", "_full.").replace("&amp;b=12", ""))
                title = "     %s - %s" % (title, subt)
                if visto != "0":
                    title += " [COLOR %s][V][/COLOR]" % color5
                itemlist.append(
                    Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumb, media_id=media_id,
                         server="crunchyroll", text_color=item.text_color, contentTitle=item.contentTitle,
                         contentSerieName=item.contentSerieName, contentType="tvshow"))
    else:
        matches = scrapertools.find_multiple_matches(data, patron)
        for url, thumb, media_id, visto, title, subt, plot in matches:
            if item.proxy == "spain":
                url = urllib.unquote(url.replace("/browse.php?u=", "").replace("&amp;b=12", ""))
            elif not item.proxy:
                url = host + url
            url = url.replace(proxy_u, "")
            thumb = urllib.unquote(
                thumb.replace("/browse.php?u=", "").replace("_wide.", "_full.").replace("&amp;b=12", ""))
            title = "%s - %s" % (title, subt)
            if visto != "0":
                title += " [COLOR %s][V][/COLOR]" % color5
            itemlist.append(
                Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumb, media_id=media_id,
                     server="crunchyroll", text_color=item.text_color, contentTitle=item.contentTitle,
                     contentSerieName=item.contentSerieName, contentType="tvshow"))

    return itemlist


def indices(item):
    logger.info()
    itemlist = []

    if not item.url:
        itemlist.append(item.clone(title="Alfabético", url="http://www.crunchyroll.com/videos/anime/alpha"))
        itemlist.append(item.clone(title="Géneros", url="http://www.crunchyroll.com/videos/anime"))
        itemlist.append(item.clone(title="Temporadas", url="http://www.crunchyroll.com/videos/anime"))

    else:
        data = httptools.downloadpage(item.url).data
        if "Alfabético" in item.title:
            bloque = scrapertools.find_single_match(data, '<div class="content-menu cf ">(.*?)</div>')
            matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?>([^<]+)<')
            for url, title in matches:
                if "todo" in title:
                    continue
                if item.proxy == "spain":
                    url = proxy_e + host + url
                elif item.proxy == "usa":
                    url = proxy_u + host + url
                else:
                    url = host + url

                itemlist.append(item.clone(action="alpha", title=title, url=url, page=0))
        elif "Temporadas" in item.title:
            bloque = scrapertools.find_single_match(data,
                                                    '<div class="season-selectors cf selectors">(.*?)<div id="container"')
            matches = scrapertools.find_multiple_matches(bloque, 'href="#([^"]+)".*?title="([^"]+)"')
            for url, title in matches:
                url += "/ajax_page?pg=0"
                if item.proxy == "spain":
                    url = proxy_e + host + url
                elif item.proxy == "usa":
                    url = proxy_u + host + url
                else:
                    url = host + url

                itemlist.append(item.clone(action="lista", title=title, url=url, page=0))
        else:
            bloque = scrapertools.find_single_match(data, '<div class="genre-selectors selectors">(.*?)</div>')
            matches = scrapertools.find_multiple_matches(bloque, '<input id="([^"]+)".*?title="([^"]+)"')
            for url, title in matches:
                url = "%s/genres/ajax_page?pg=0&tagged=%s" % (item.url, url)
                if item.proxy == "spain":
                    url = proxy_e + url.replace("&", "%26")
                elif item.proxy == "usa":
                    url = proxy_u + url

                itemlist.append(item.clone(action="lista", title=title, url=url, page=0))

    return itemlist


def alpha(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<div class="wrapper hover-toggle-queue.*?title="([^"]+)".*?href="([^"]+)".*?src="([^"]+)"' \
             '.*?<span class="series-data.*?>\s*([^<]+)</span>.*?<p.*?>(.*?)</p>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for title, url, thumb, videos, plot in matches:
        if item.proxy == "spain":
            url = "http://proxyanonimo.es" + url.replace("&amp;b=12", "")
        elif not item.proxy:
            url = host + url
        thumb = urllib.unquote(thumb.replace("/browse.php?u=", "").replace("_small", "_full").replace("&amp;b=12", ""))
        scrapedtitle = "%s (%s)" % (title, videos.strip())
        itemlist.append(item.clone(action="episodios", url=url, title=scrapedtitle, thumbnail=thumb,
                                   contentTitle=title, contentSerieName=title, infoLabels={'plot': plot},
                                   text_color=color2))

    return itemlist


def calendario(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<div class="specific-date">.*?datetime="\d+-(\d+)-(\d+).*?class="day-name">.*?>\s*([^<]+)</time>(.*?)</section>'
    bloques = scrapertools.find_multiple_matches(data, patron)
    for mes, dia, title, b in bloques:
        patron = 'class="available-time">([^<]+)<.*?<cite itemprop="name">(.*?)</cite>.*?href="([^"]+)"' \
                 '.*?>\s*(.*?)\s*</a>(.*?)</article>'
        matches = scrapertools.find_multiple_matches(b, patron)
        if matches:
            title = "%s/%s - %s" % (dia, mes, title.strip())
            itemlist.append(item.clone(action="", title=title))
        for hora, title, url, subt, datos in matches:
            subt = subt.replace("Available", "Disponible").replace("Episode", "Episodio").replace("in ", "en ")
            subt = re.sub(r"\s{2,}", " ", subt)
            if "<time" in subt:
                subt = re.sub(r"<time.*?>", "", subt).replace("</time>", "")

            scrapedtitle = "   [%s] %s - %s" % (hora, scrapertools.htmlclean(title), subt)
            scrapedtitle = re.sub(r"\[email&#160;protected\]|\[email\xc2\xa0protected\]", "Idolm@ster", scrapedtitle)

            if "Disponible" in scrapedtitle:
                if item.proxy == "spain":
                    url = urllib.unquote(url.replace("/browse.php?u=", "").replace("&amp;b=12", ""))
                action = "play"
                server = "crunchyroll"
            else:
                action = ""
                server = ""
            thumb = scrapertools.find_single_match(datos, '<img class="thumbnail" src="([^"]+)"')
            if not thumb:
                thumb = scrapertools.find_single_match(datos, 'src="([^"]+)"')
            if thumb:
                thumb = urllib.unquote(thumb.replace("/browse.php?u=", "").replace("_thumb", "_full") \
                                       .replace("&amp;b=12", "").replace("_large", "_full"))
            itemlist.append(item.clone(action=action, url=url, title=scrapedtitle, contentTitle=title, thumbnail=thumb,
                                       text_color=color2, contentSerieName=title, server=server))

    next = scrapertools.find_single_match(data, 'js-pagination-next"\s*href="([^"]+)"')
    if next:
        if item.proxy == "spain":
            next = "http://proxyanonimo.es" + url.replace("&amp;b=12", "")
        else:
            next = host + next
        itemlist.append(item.clone(action="calendario", url=next, title=">> Siguiente Semana"))
    prev = scrapertools.find_single_match(data, 'js-pagination-last"\s*href="([^"]+)"')
    if prev:
        if item.proxy == "spain":
            prev = "http://proxyanonimo.es" + url.replace("&amp;b=12", "")
        else:
            prev = host + prev
        itemlist.append(item.clone(action="calendario", url=prev, title="<< Semana Anterior"))

    return itemlist


def play(item):
    logger.info()
    if item.login and not "[V]" in item.title:
        post = "cbelapsed=60&h=&media_id=%s" % item.media_id + "&req=RpcApiVideo_VideoView&cbcallcount=1&ht=0" \
                                                               "&media_type=1&video_encode_id=0&playhead=10000"
        httptools.downloadpage("http://www.crunchyroll.com/ajax/", post)

    return [item]
