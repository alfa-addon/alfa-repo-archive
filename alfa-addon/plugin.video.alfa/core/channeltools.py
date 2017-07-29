# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# channeltools - Herramientas para trabajar con canales
# ------------------------------------------------------------

import os

import config
import jsontools
import logger

DEFAULT_UPDATE_URL = "/channels/"
dict_channels_parameters = dict()


def is_adult(channel_name):
    logger.info("channel_name=" + channel_name)
    channel_parameters = get_channel_parameters(channel_name)
    return channel_parameters["adult"]


def get_channel_parameters(channel_name):
    global dict_channels_parameters

    if channel_name not in dict_channels_parameters:
        try:
            channel_parameters = get_channel_json(channel_name)
            # logger.debug(channel_parameters)
            if channel_parameters:
                # cambios de nombres y valores por defecto
                channel_parameters["title"] = channel_parameters.pop("name")
                channel_parameters["channel"] = channel_parameters.pop("id")

                # si no existe el key se declaran valor por defecto para que no de fallos en las funciones que lo llaman
                channel_parameters["update_url"] = channel_parameters.get("update_url", DEFAULT_UPDATE_URL)
                channel_parameters["language"] = channel_parameters.get("language", "all")
                channel_parameters["adult"] = channel_parameters.get("adult", False)
                channel_parameters["active"] = channel_parameters.get("active", False)
                channel_parameters["include_in_global_search"] = channel_parameters.get("include_in_global_search",
                                                                                        False)
                channel_parameters["categories"] = channel_parameters.get("categories", list())

                channel_parameters["thumbnail"] = channel_parameters.get("thumbnail", "")
                channel_parameters["banner"] = channel_parameters.get("banner", "")
                channel_parameters["fanart"] = channel_parameters.get("fanart", "")

                # Imagenes: se admiten url y archivos locales dentro de "resources/images"
                if channel_parameters.get("thumbnail") and "://" not in channel_parameters["thumbnail"]:
                    channel_parameters["thumbnail"] = os.path.join(config.get_runtime_path(), "resources", "media",
                                                                   "channels", "thumb", channel_parameters["thumbnail"])
                if channel_parameters.get("banner") and "://" not in channel_parameters["banner"]:
                    channel_parameters["banner"] = os.path.join(config.get_runtime_path(), "resources", "media",
                                                                "channels", "banner", channel_parameters["banner"])
                if channel_parameters.get("fanart") and "://" not in channel_parameters["fanart"]:
                    channel_parameters["fanart"] = os.path.join(config.get_runtime_path(), "resources", "media",
                                                                "channels", "fanart", channel_parameters["fanart"])

                # Obtenemos si el canal tiene opciones de configuración
                channel_parameters["has_settings"] = False
                if 'settings' in channel_parameters:
                    # if not isinstance(channel_parameters['settings'], list):
                    #     channel_parameters['settings'] = [channel_parameters['settings']]

                    # if "include_in_global_search" in channel_parameters['settings']:
                    #     channel_parameters["include_in_global_search"] = channel_parameters['settings']
                    #     ["include_in_global_search"].get('default', False)
                    #
                    # found = False
                    # for el in channel_parameters['settings']:
                    #     for key in el.items():
                    #         if 'include_in' not in key:
                    #             channel_parameters["has_settings"] = True
                    #             found = True
                    #             break
                    #     if found:
                    #         break

                    for s in channel_parameters['settings']:
                        if 'id' in s:
                            if s['id'] == "include_in_global_search":
                                channel_parameters["include_in_global_search"] = True
                            elif not s['id'].startswith("include_in_") and \
                                    (s.get('enabled', False) or s.get('visible', False)):
                                channel_parameters["has_settings"] = True

                    del channel_parameters['settings']

                # Compatibilidad
                if 'compatible' in channel_parameters:
                    # compatible python
                    python_compatible = True
                    if 'python' in channel_parameters["compatible"]:
                        import sys
                        python_condition = channel_parameters["compatible"]['python']
                        if sys.version_info < tuple(map(int, (python_condition.split(".")))):
                            python_compatible = False

                    # compatible addon_version
                    addon_version_compatible = True
                    if 'addon_version' in channel_parameters["compatible"]:
                        import versiontools
                        addon_version_condition = channel_parameters["compatible"]['addon_version']
                        addon_version = int(addon_version_condition.replace(".", "").ljust(len(str(
                            versiontools.get_current_plugin_version())), '0'))
                        if versiontools.get_current_plugin_version() < addon_version:
                            addon_version_compatible = False

                    channel_parameters["compatible"] = python_compatible and addon_version_compatible
                else:
                    channel_parameters["compatible"] = True

                dict_channels_parameters[channel_name] = channel_parameters

            else:
                # para evitar casos donde canales no están definidos como configuración
                # lanzamos la excepcion y asi tenemos los valores básicos
                raise Exception

        except Exception, ex:
            logger.error(channel_name + ".json error \n%s" % ex)
            channel_parameters = dict()
            channel_parameters["channel"] = ""
            channel_parameters["adult"] = False
            channel_parameters['active'] = False
            channel_parameters["compatible"] = True
            channel_parameters["language"] = ""
            channel_parameters["update_url"] = DEFAULT_UPDATE_URL
            return channel_parameters

    return dict_channels_parameters[channel_name]


def get_channel_json(channel_name):
    # logger.info("channel_name=" + channel_name)
    import filetools
    try:
        channel_path = filetools.join(config.get_runtime_path(), "channels", channel_name + ".json")
        # logger.info("channel_data=" + channel_path)
        channel_json = jsontools.load(filetools.read(channel_path))
        # logger.info("channel_json= %s" % channel_json)

    except Exception, ex:
        template = "An exception of type %s occured. Arguments:\n%r"
        message = template % (type(ex).__name__, ex.args)
        logger.error(" %s" % message)
        channel_json = None

    return channel_json


def get_channel_controls_settings(channel_name):
    # logger.info("channel_name=" + channel_name)
    dict_settings = {}

    list_controls = get_channel_json(channel_name).get('settings', list())

    for c in list_controls:
        if 'id' not in c or 'type' not in c or 'default' not in c:
            # Si algun control de la lista  no tiene id, type o default lo ignoramos
            continue

        # new dict with key(id) and value(default) from settings
        dict_settings[c['id']] = c['default']

    return list_controls, dict_settings


def get_channel_setting(name, channel, default=None):
    """
    Retorna el valor de configuracion del parametro solicitado.

    Devuelve el valor del parametro 'name' en la configuracion propia del canal 'channel'.

    Busca en la ruta \addon_data\plugin.video.alfa\settings_channels el archivo channel_data.json y lee
    el valor del parametro 'name'. Si el archivo channel_data.json no existe busca en la carpeta channels el archivo
    channel.json y crea un archivo channel_data.json antes de retornar el valor solicitado. Si el parametro 'name'
    tampoco existe en el el archivo channel.json se devuelve el parametro default.


    @param name: nombre del parametro
    @type name: str
    @param channel: nombre del canal
    @type channel: str
    @param default: valor devuelto en caso de que no exista el parametro name
    @type default: cualquiera

    @return: El valor del parametro 'name'
    @rtype: El tipo del valor del parametro

    """
    file_settings = os.path.join(config.get_data_path(), "settings_channels", channel + "_data.json")
    dict_settings = {}
    dict_file = {}
    if os.path.exists(file_settings):
        # Obtenemos configuracion guardada de ../settings/channel_data.json
        try:
            dict_file = jsontools.load(open(file_settings, "rb").read())
            if isinstance(dict_file, dict) and 'settings' in dict_file:
                dict_settings = dict_file['settings']
        except EnvironmentError:
            logger.error("ERROR al leer el archivo: %s" % file_settings)

    if not dict_settings or name not in dict_settings:
        # Obtenemos controles del archivo ../channels/channel.json
        try:
            list_controls, default_settings = get_channel_controls_settings(channel)
        except:
            default_settings = {}

        if name in default_settings:  # Si el parametro existe en el channel.json creamos el channel_data.json
            default_settings.update(dict_settings)
            dict_settings = default_settings
            dict_file['settings'] = dict_settings
            # Creamos el archivo ../settings/channel_data.json
            json_data = jsontools.dump(dict_file)
            try:
                open(file_settings, "wb").write(json_data)
            except EnvironmentError:
                logger.error("ERROR al salvar el archivo: %s" % file_settings)

    # Devolvemos el valor del parametro local 'name' si existe, si no se devuelve default
    return dict_settings.get(name, default)


def set_channel_setting(name, value, channel):
    """
    Fija el valor de configuracion del parametro indicado.

    Establece 'value' como el valor del parametro 'name' en la configuracion propia del canal 'channel'.
    Devuelve el valor cambiado o None si la asignacion no se ha podido completar.

    Si se especifica el nombre del canal busca en la ruta \addon_data\plugin.video.alfa\settings_channels el
    archivo channel_data.json y establece el parametro 'name' al valor indicado por 'value'.
    Si el parametro 'name' no existe lo añade, con su valor, al archivo correspondiente.

    @param name: nombre del parametro
    @type name: str
    @param value: valor del parametro
    @type value: str
    @param channel: nombre del canal
    @type channel: str

    @return: 'value' en caso de que se haya podido fijar el valor y None en caso contrario
    @rtype: str, None

    """
    # Creamos la carpeta si no existe
    if not os.path.exists(os.path.join(config.get_data_path(), "settings_channels")):
        os.mkdir(os.path.join(config.get_data_path(), "settings_channels"))

    file_settings = os.path.join(config.get_data_path(), "settings_channels", channel + "_data.json")
    dict_settings = {}

    dict_file = None

    if os.path.exists(file_settings):
        # Obtenemos configuracion guardada de ../settings/channel_data.json
        try:
            dict_file = jsontools.load(open(file_settings, "r").read())
            dict_settings = dict_file.get('settings', {})
        except EnvironmentError:
            logger.error("ERROR al leer el archivo: %s" % file_settings)

    dict_settings[name] = value

    # comprobamos si existe dict_file y es un diccionario, sino lo creamos
    if dict_file is None or not dict_file:
        dict_file = {}

    dict_file['settings'] = dict_settings

    # Creamos el archivo ../settings/channel_data.json
    try:
        json_data = jsontools.dump(dict_file)
        open(file_settings, "w").write(json_data)
    except EnvironmentError:
        logger.error("ERROR al salvar el archivo: %s" % file_settings)
        return None

    return value


def get_channel_module(channel_name, package="channels"):
    # Sustituye al que hay en servertools.py ...
    # ...pero añade la posibilidad de incluir un paquete diferente de "channels"
    if "." not in channel_name:
        channel_module = __import__('%s.%s' % (package, channel_name), None, None, ['%s.%s' % (package, channel_name)])
    else:
        channel_module = __import__(channel_name, None, None, [channel_name])
    return channel_module


def get_channel_remote_url(channel_name):
    channel_parameters = get_channel_parameters(channel_name)
    remote_channel_url = channel_parameters["update_url"] + channel_name + ".py"
    remote_version_url = channel_parameters["update_url"] + channel_name + ".json"

    logger.info("remote_channel_url=" + remote_channel_url)
    logger.info("remote_version_url=" + remote_version_url)

    return remote_channel_url, remote_version_url


def get_channel_local_path(channel_name):
    if channel_name != "channelselector":
        local_channel_path = os.path.join(config.get_runtime_path(), 'channels', channel_name + ".py")
        local_version_path = os.path.join(config.get_runtime_path(), 'channels', channel_name + ".json")
        local_compiled_path = os.path.join(config.get_runtime_path(), 'channels', channel_name + ".pyo")
    else:
        local_channel_path = os.path.join(config.get_runtime_path(), channel_name + ".py")
        local_version_path = os.path.join(config.get_runtime_path(), channel_name + ".json")
        local_compiled_path = os.path.join(config.get_runtime_path(), channel_name + ".pyo")

    logger.info("local_channel_path=" + local_channel_path)
    logger.info("local_version_path=" + local_version_path)
    logger.info("local_compiled_path=" + local_compiled_path)

    return local_channel_path, local_version_path, local_compiled_path
