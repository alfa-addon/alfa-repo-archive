# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# Updater process
# --------------------------------------------------------------------------------

import os
import time

import config
import logger
import scrapertools
import versiontools


# Método antiguo, muestra un popup con la versión
def checkforupdates():
    logger.info()

    # Valores por defecto
    numero_version_publicada = 0
    tag_version_publicada = ""

    # Lee la versión remota
    from core import api
    latest_packages = api.plugins_get_latest_packages()
    for latest_package in latest_packages["body"]:
        if latest_package["package"] == "plugin":
            numero_version_publicada = latest_package["version"]
            tag_version_publicada = latest_package["tag"]
            break

    logger.info("version remota=" + str(numero_version_publicada))

    # Lee la versión local
    numero_version_local = versiontools.get_current_plugin_version()
    logger.info("version local=" + str(numero_version_local))

    hayqueactualizar = numero_version_publicada > numero_version_local
    logger.info("-> hayqueactualizar=" + repr(hayqueactualizar))

    # Si hay actualización disponible, devuelve la Nueva versión para que cada plataforma se encargue de mostrar los avisos
    if hayqueactualizar:
        return tag_version_publicada
    else:
        return None


# Método nuevo, devuelve el nº de actualizaciones disponibles además de indicar si hay nueva versión del plugin
def get_available_updates():
    logger.info()

    # Cuantas actualizaciones hay?
    number_of_updates = 0
    new_published_version_tag = ""

    # Lee la versión remota
    from core import api
    latest_packages = api.plugins_get_latest_packages()

    for latest_package in latest_packages["body"]:

        if latest_package["package"] == "plugin":
            if latest_package["version"] > versiontools.get_current_plugin_version():
                number_of_updates = number_of_updates + 1
                new_published_version_tag = latest_package["tag"]

        elif latest_package["package"] == "channels":
            if latest_package["version"] > versiontools.get_current_channels_version():
                number_of_updates = number_of_updates + 1

        elif latest_package["package"] == "servers":
            if latest_package["version"] > versiontools.get_current_servers_version():
                number_of_updates = number_of_updates + 1

    return new_published_version_tag, number_of_updates


def update(item):
    logger.info()

    # Valores por defecto
    published_version_url = ""
    published_version_filename = ""

    # Lee la versión remota
    from core import api
    latest_packages = api.plugins_get_latest_packages()
    for latest_package in latest_packages["body"]:
        if latest_package["package"] == "plugin":
            published_version_url = latest_package["url"]
            published_version_filename = latest_package["filename"]
            published_version_number = latest_package["version"]
            break

    # La URL viene del API, y lo descarga en "userdata"
    remotefilename = published_version_url
    localfilename = os.path.join(config.get_data_path(), published_version_filename)

    download_and_install(remotefilename, localfilename)


def download_and_install(remote_file_name, local_file_name):
    logger.info("from " + remote_file_name + " to " + local_file_name)

    if os.path.exists(local_file_name):
        os.remove(local_file_name)

    # Descarga el fichero
    inicio = time.clock()
    from core import downloadtools
    downloadtools.downloadfile(remote_file_name, local_file_name, continuar=False)
    fin = time.clock()
    logger.info("Descargado en %d segundos " % (fin - inicio + 1))

    logger.info("descomprime fichero...")
    import ziptools
    unzipper = ziptools.ziptools()

    # Lo descomprime en "addons" (un nivel por encima del plugin)
    installation_target = os.path.join(config.get_runtime_path(), "..")
    logger.info("installation_target=%s" % installation_target)

    unzipper.extract(local_file_name, installation_target)

    # Borra el zip descargado
    logger.info("borra fichero...")
    os.remove(local_file_name)
    logger.info("...fichero borrado")


def update_channel(channel_name):
    logger.info(channel_name)

    import channeltools
    remote_channel_url, remote_version_url = channeltools.get_channel_remote_url(channel_name)
    local_channel_path, local_version_path, local_compiled_path = channeltools.get_channel_local_path(channel_name)

    # Version remota
    try:
        data = scrapertools.cachePage(remote_version_url)
        logger.info("remote_data=" + data)
        remote_version = int(scrapertools.find_single_match(data, '<version>([^<]+)</version>'))
        addon_condition = int(scrapertools.find_single_match(data, "<addon_version>([^<]*)</addon_version>")
                              .replace(".", "").ljust(len(str(versiontools.get_current_plugin_version())), '0'))
    except:
        remote_version = 0
        addon_condition = 0

    logger.info("remote_version=%d" % remote_version)

    # Version local
    if os.path.exists(local_version_path):
        infile = open(local_version_path)
        from core import jsontools
        data = jsontools.load(infile.read())
        infile.close()

        local_version = data.get('version', 0)
    else:
        local_version = 0

    logger.info("local_version=%d" % local_version)

    # Comprueba si ha cambiado
    updated = (remote_version > local_version) and (versiontools.get_current_plugin_version() >= addon_condition)

    if updated:
        logger.info("downloading...")
        download_channel(channel_name)

    return updated


def download_channel(channel_name):
    logger.info(channel_name)

    import channeltools
    remote_channel_url, remote_version_url = channeltools.get_channel_remote_url(channel_name)
    local_channel_path, local_version_path, local_compiled_path = channeltools.get_channel_local_path(channel_name)

    # Descarga el canal
    try:
        updated_channel_data = scrapertools.cachePage(remote_channel_url)
        outfile = open(local_channel_path, "wb")
        outfile.write(updated_channel_data)
        outfile.flush()
        outfile.close()
        logger.info("Grabado a " + local_channel_path)
    except:
        import traceback
        logger.error(traceback.format_exc())

    # Descarga la version (puede no estar)
    try:
        updated_version_data = scrapertools.cachePage(remote_version_url)
        outfile = open(local_version_path, "w")
        outfile.write(updated_version_data)
        outfile.flush()
        outfile.close()
        logger.info("Grabado a " + local_version_path)
    except:
        import traceback
        logger.error(traceback.format_exc())

    if os.path.exists(local_compiled_path):
        os.remove(local_compiled_path)

    from platformcode import platformtools
    platformtools.dialog_notification(channel_name + " actualizado", "Se ha descargado una nueva versión")
