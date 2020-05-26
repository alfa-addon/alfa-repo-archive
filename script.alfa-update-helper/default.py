# -*- coding: utf-8 -*-
# -*- Update Helper -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import xbmc
import xbmcgui
import xbmcaddon
import os
import re
import json
import requests
import shutil
import traceback
from zipfile import ZipFile
import xmltodict
from threading import Thread
result = True

addons_path = xbmc.translatePath("special://home/addons")
addonid = "plugin.video.alfa"
scriptid = "script.alfa_update_helper"
installed = bool(xbmc.getCondVisibility("System.HasAddon(%s)" % addonid))
installed_path = os.path.join(addons_path, "%s" % addonid)
addons_service = os.path.join(installed_path, 'videolibrary_service.py')
pkg_path = os.path.join(addons_path, "packages")

base_url = ["https://github.com/alfa-addon/alfa-repo/raw/master/plugin.video.alfa/", \
            "https://bitbucket.org/alfa_addon/alfa-repo/raw/master/plugin.video.alfa/"]
xml = xmltodict.parse(requests.get("%s%s" % (base_url[1], "addon.xml")).content)
current_version = xml["addon"]["@version"]
updated_filename = "%s-%s.zip" % (addonid, current_version)
pkg_updated = os.path.join(pkg_path, updated_filename)
heading = "Alfa Update Helper"
progress = 0
auto_update = xbmcaddon.Addon(scriptid).getSetting("auto_update")


def clean_packages():
    for pkg_name in os.listdir(pkg_path):
        if addonid in pkg_name or "script.module.html5lib" in pkg_name:
            try:
                if os.path.exists(os.path.join(pkg_path, pkg_name)):
                    os.remove(os.path.join(pkg_path, pkg_name))
                    xbmc.log("[%s] %s has been deleted" % (scriptid, pkg_name), xbmc.LOGNOTICE)
            except Exception as e:
                xbmc.log("[%s] *** Error deleting package %s: %s" % (scriptid, pkg_name, str(e)), xbmc.LOGERROR)
                return False
    return True


def check_dependencies():

    dependencies = ['script.module.html5lib', 'script.module.beautifulsoup4']
    
    for dependency in dependencies:
        found = bool(xbmc.getCondVisibility("System.hasAddon(%s)" % dependency))
        if not found:
            try:
                xbmc.executebuiltin('InstallAddon(%s)' % dependency)
                timeout = 30
                xbmc.log("[%s] Installing dependencie %s..." % (scriptid, dependency), xbmc.LOGNOTICE)
                while not found and timeout > 0:
                    xbmc.sleep(1000)
                    found = bool(xbmc.getCondVisibility("System.hasAddon(%s)" % dependency))
                    timeout -= 1
                if timeout == 0:
                    xbmc.log("[%s] *** Error Installing dependency %s..." % (scriptid, dependency), xbmc.LOGERROR)
                    raise Exception("Failed to install dependency")
    
            except:
                return False
        xbmc.sleep(3000)

    return True


def get_zip(info, retry=False):
    for url in base_url:
        xbmc.log("[%s] Downloading from: %s%s" % (scriptid, url, updated_filename), xbmc.LOGNOTICE)
        reponse = requests.get("%s%s" % (url, updated_filename))
        if reponse.status_code == 200:
            zip_data = reponse.content
            with open(pkg_updated, "wb") as f:
                f.write(zip_data)
            
            ret = None
            try:
                with ZipFile(pkg_updated, "r") as zf:
                    ret = zf.testzip()
            except Exception as e:
                ret = str(e)
            if ret is None:
                xbmc.log("[%s] .zip verified" % (scriptid), xbmc.LOGNOTICE)
                break
            
            xbmc.sleep(1000)
            os.remove(pkg_updated)
            if not retry:
                xbmc.log("[%s] *** Corrupted .zip, error: %s, retrying..." % (scriptid, str(ret)), xbmc.LOGERROR)
                info.update(progress, heading, "Error en la descarga, reintentando...")
                xbmc.sleep(30000)
                get_zip(info, retry=True)
            else:
                xbmc.log("[%s] *** Error again in .zip, error: %s" % (scriptid, str(ret)), xbmc.LOGERROR)
        else:
            xbmc.log("[%s] *** Error downloading, retrying... %s%s" % (scriptid, url, updated_filename), xbmc.LOGERROR)
    
    else:
        info.update(progress, heading, "Error irrecuperable en la descarga, reintentalo más tarde...")
        result = False
        xbmc.log("[%s] *** Unrecoverable downloading error, try later..." % (scriptid), xbmc.LOGERROR)
        raise Exception("Unrecoverable downloading error, try later...")


def backup_and_remove():
    xbmc.log("[%s] backing and removing installed version..." % (scriptid), xbmc.LOGNOTICE)
    backup_path = os.path.join(addons_path, "temp", addonid)
    if os.path.exists(backup_path):
        shutil.rmtree(backup_path, ignore_errors=True)

    shutil.copytree(installed_path, backup_path)
    shutil.rmtree(installed_path, ignore_errors=True)


def extract_and_install():
    xbmc.log("[%s] Installing updated version version..." % (scriptid), xbmc.LOGNOTICE)
    with ZipFile(pkg_updated, "r") as zf:
        zf.extractall(addons_path)

    xbmc.executebuiltin('UpdateLocalAddons')
    xbmc.sleep(2000)
    method = "Addons.SetAddonEnabled"
    xbmc.executeJSONRPC(
        '{"jsonrpc": "2.0", "id":1, "method": "%s", "params": {"addonid": "%s", "enabled": true}}' % (method, addonid))


def run(auto=False):

    global result, progress

    info = xbmcgui.DialogProgressBG()
    info.create(heading, "")
    try:
        if auto:
            try:
                dialog = xbmcgui.Dialog()
                message = "[COLOR hotpink][B]Se ha detectado un error en la instalación de Alfa. "
                message += "Déjanos que lo arreglemos por ti...[/B][/COLOR]"
                dialog.notification(heading, message, xbmcgui.NOTIFICATION_WARNING, 10000, True)
            except:
                pass

        info.update(progress, heading, "Limpiando paquetes antiguos...")
        clean_packages()
        xbmc.sleep(3000)
        info.update(progress, heading, "Verificando Dependencias")
        if check_dependencies():
            progress += 25
            info.update(progress, heading, "Descargando última versión...")
            get_zip(info)
            if installed:
                progress += 25
                info.update(progress, heading, "Creando copia de seguridad...")
                backup_and_remove()
            else:
                progress += 50
            info.update(progress, heading, "Actualizando...")
            extract_and_install()
            progress += 25
            xbmc.sleep(1000)
            clean_packages()
            info.update(progress, heading, "Se completó el proceso")

        else:
            raise Exception("Failed to install dependency")
    except:
        info.update(0, heading, "Ha ocurrido un error, no se pudo actualizar")
        result = False
        xbmc.log("[%s] *** Unrecoverable error while updating..." % (scriptid), xbmc.LOGERROR)
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
    
    xbmc.sleep(3000)
    info.close()

    if result:
        profile = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "Profiles.GetCurrentProfile"}'))
        xbmc.log("[%s] Reloading Profile..." % scriptid, xbmc.LOGNOTICE)
        user = profile["result"]["label"]
        xbmc.executebuiltin('LoadProfile(%s)' % user)
        #xbmc.executebuiltin('RunPlugin(plugin://plugin.video.alfa/videolibrary_service.py)')


def force_corrupted_zip():
    # Tries to overload BitBucket so there are chances to get corrupted downloaded .zips.  TO BE USED ONLY FOR TESTING
    def download_zip(url, i):
        reponse = requests.get("%s%s" % (url, updated_filename))
        info.update(progress + i, heading, "Lanzando nueva descarga .zip ...")
        if reponse.status_code == 200:
            zip_data = reponse.content
            zip_name = pkg_updated.replace('.zip', '_' + str(i+1) + '.zip')
            with open(zip_name, "wb") as f:
                f.write(zip_data)
            
            xbmc.log('[%s] Verifying new .zip download: %s...' % (scriptid, str(i+1)), xbmc.LOGNOTICE)
            ret = None
            try:
                with ZipFile(zip_name, "r") as zf:
                    ret = zf.testzip()
            except Exception as e:
                ret = str(e)
            xbmc.sleep(1000)
            if ret is not None:
                xbmc.log("[%s] *** Corrupted .zip found %s, error %s..." % (scriptid, zip_name, str(ret)), xbmc.LOGERROR)
                info.update(progress + i, heading, "Descarga .zip CORRUPTA...")
                os.rename(zip_name, zip_name.replace('.zip', '_CORRUPTED.zip'))
    
    global result, heading, info, progress
    
    info = xbmcgui.DialogProgressBG()
    info.create(heading, "")
    progress = 1

    threads_list = []
    url = base_url[1]
    x = 100                                                                     # Defines number of concurrent downloads to stress web
    info.update(0, heading, "Proceso de descarga masiva de %s .zip's comenzado ..." % str(x))
    
    for i in range(x):
        z = Thread(target=download_zip, args=(url, i))
        z.setDaemon = True
        z.start()
        threads_list.append(z)

    while [thread_x for thread_x in threads_list if thread_x.isAlive()]:
        xbmc.sleep(5000)
        continue
    info.update(100, heading, "Proceso de descarga masiva de %s .zip's terminado ..." % str(x))
    xbmc.sleep(5000)
    info.close()


def monitor_update():
    zip_name = pkg_updated

    if os.path.exists(zip_name):
        ret = None
        try:
            with ZipFile(zip_name, "r") as zf:
                ret = zf.testzip()
        except Exception as e:
            ret = str(e)
        
        addon_error = bool(xbmc.getCondVisibility("System.HasAddon(%s)" % addonid))     # Alfa active?
        xbmc.log("[%s] *** Addon installed: [%s]. Corrupted .zip found %s, error %s..." % \
                        (scriptid, str(addon_error), zip_name, str(ret)), xbmc.LOGERROR)
        if ret is not None and 'Error 32' not in ret and 'Error 5' not in ret \
                        and not addon_error:                                    # if Verify error, but not locked .zip, and Alfa inactive...
            xbmc.sleep(1000)
            if clean_packages():                                                # Ckeck if .zip is in use by Kodi, then we wait to next pass
                xbmc.log("[%s] *** Corrupted .zip found %s, reinstallation starts..." % (scriptid, zip_name), xbmc.LOGERROR)
                run(auto=True)                                                  #... re-install Alfa
            

def monitor():
    xbmc.log('[%s] auto_update [%s]' % (scriptid, str(auto_update)), xbmc.LOGNOTICE)

    if auto_update == 'true':
        xbmc.log('[%s] Starting monitor...' % scriptid, xbmc.LOGNOTICE)
        num_version = xbmc.getInfoLabel('System.BuildVersion')
        num_version = float(re.match("\d+\.\d+", num_version).group(0))
        if num_version >= 14:
            monitor = xbmc.Monitor()                                            # For Kodi >= 14
        else:
            monitor = None                                                      # For Kodi < 14

        if monitor:
            while not monitor.abortRequested():
                monitor_update()
                if monitor.waitForAbort(60):                                    # Every 1 minute
                    break
        else:
            while not xbmc.abortRequested:
                monitor_update()
                xbmc.sleep(60000)
    

if sys.argv[0] == "":
    monitor()
else:
    xbmc.log('[%s] Starting update...' % scriptid, xbmc.LOGNOTICE)
    t = Thread(target=run)
    #t = Thread(target=force_corrupted_zip)                                      # Replace for run() when wanting to force corrupted .zips
    t.setDaemon = True
    t.start()
    t.join()

if not result:
    xbmc.log("[%s] Failed..." % scriptid, xbmc.LOGERROR)