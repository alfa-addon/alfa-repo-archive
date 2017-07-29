# -*- coding: utf-8 -*-

import re

from core import httptools
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data

    if "The file is being converted" in data:
        return False, "El fichero está en proceso"
    elif "no longer exists" in data:
        return False, "El fichero ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    video_id = scrapertools.get_match(page_url, "http://www.nowvideo.../video/([a-z0-9]+)")

    if premium:
        # Lee la página de login
        login_url = "http://www.nowvideo.eu/login.php"
        data = httptools.downloadpage(login_url).data

        # Hace el login
        login_url = "http://www.nowvideo.eu/login.php?return="
        post = "user=" + user + "&pass=" + password + "&register=Login"
        headers = {"Referer": "http://www.nowvideo.eu/login.php"}
        data = httptools.downloadpage(login_url, post, headers=headers).data

        # Descarga la página del vídeo 
        data = httptools.downloadpage(page_url).data

        # URL a invocar: http://www.nowvideo.eu/api/player.api.php?user=aaa&file=rxnwy9ku2nwx7&pass=bbb&cid=1&cid2=undefined&key=83%2E46%2E246%2E226%2Dc7e707c6e20a730c563e349d2333e788&cid3=undefined
        # En la página:
        '''
        flashvars.domain="http://www.nowvideo.eu";
        flashvars.file="rxnwy9ku2nwx7";
        flashvars.filekey="83.46.246.226-c7e707c6e20a730c563e349d2333e788";
        flashvars.advURL="0";
        flashvars.autoplay="false";
        flashvars.cid="1";
        flashvars.user="aaa";
        flashvars.key="bbb";
        flashvars.type="1";
        '''
        flashvar_file = scrapertools.get_match(data, 'flashvars.file="([^"]+)"')
        flashvar_filekey = scrapertools.get_match(data, 'flashvars.filekey=([^;]+);')
        flashvar_filekey = scrapertools.get_match(data, 'var ' + flashvar_filekey + '="([^"]+)"')
        flashvar_user = scrapertools.get_match(data, 'flashvars.user="([^"]+)"')
        flashvar_key = scrapertools.get_match(data, 'flashvars.key="([^"]+)"')
        flashvar_type = scrapertools.get_match(data, 'flashvars.type="([^"]+)"')

        # http://www.nowvideo.eu/api/player.api.php?user=aaa&file=rxnwy9ku2nwx7&pass=bbb&cid=1&cid2=undefined&key=83%2E46%2E246%2E226%2Dc7e707c6e20a730c563e349d2333e788&cid3=undefined
        url = "http://www.nowvideo.eu/api/player.api.php?user=" + flashvar_user + "&file=" + flashvar_file + "&pass=" + flashvar_key + "&cid=1&cid2=undefined&key=" + flashvar_filekey.replace(
            ".", "%2E").replace("-", "%2D") + "&cid3=undefined"
        data = httptools.downloadpage(url).data

        location = scrapertools.get_match(data, 'url=([^\&]+)&')
        location = location + "?client=FLASH"

        video_urls.append([scrapertools.get_filename_from_url(location)[-4:] + " [premium][nowvideo]", location])
    else:
        url = page_url.replace("http://www.nowvideo.sx/video/", "http://embed.nowvideo.sx/embed/?v=")
        data = httptools.downloadpage(url).data

        videourls = scrapertools.find_multiple_matches(data, 'src\s*:\s*[\'"]([^\'"]+)[\'"]')
        if not videourls:
            videourls = scrapertools.find_multiple_matches(data, '<source src=[\'"]([^\'"]+)[\'"]')
        for videourl in videourls:
            if videourl.endswith(".mpd"):
                id = scrapertools.find_single_match(videourl, '/dash/(.*?)/')
                videourl = "http://www.nowvideo.sx/download.php%3Ffile=mm" + "%s.mp4" % id

            videourl = re.sub(r'/dl(\d)*/', '/dl/', videourl)
            ext = scrapertools.get_filename_from_url(videourl)[-4:]
            videourl = videourl.replace("%3F", "?") + \
                       "|User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
            video_urls.append([ext + " [nowvideo]", videourl])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
