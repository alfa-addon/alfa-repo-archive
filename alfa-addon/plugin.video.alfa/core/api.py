# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Client for api.tvalacarta.info
# ------------------------------------------------------------

import urllib

import config
import jsontools
import logger
import scrapertools

MAIN_URL = ""
API_KEY = "nzgJy84P9w54H2w"
DEFAULT_HEADERS = [["User-Agent", config.PLUGIN_NAME + " " + config.get_platform()]]


# ---------------------------------------------------------------------------------------------------------
#  Common function for API calls
# ---------------------------------------------------------------------------------------------------------

# Make a remote call using post, ensuring api key is here
def remote_call(url, parameters={}, require_session=True):
    logger.info("url=" + url + ", parameters=" + repr(parameters))

    if not url.startswith("http"):
        url = MAIN_URL + "/" + url

    if not "api_key" in parameters:
        parameters["api_key"] = API_KEY

    # Add session token if not here
    # if not "s" in parameters and require_session:
    #    parameters["s"] = get_session_token()

    headers = DEFAULT_HEADERS
    post = urllib.urlencode(parameters)

    response_body = scrapertools.downloadpage(url, post, headers)

    return jsontools.load(response_body)


# ---------------------------------------------------------------------------------------------------------
#  Plugin service calls
# ---------------------------------------------------------------------------------------------------------

def plugins_get_all_packages():
    logger.info()

    parameters = {"plugin": config.PLUGIN_NAME, "platform": config.get_platform()}
    return remote_call("plugins/get_all_packages.php", parameters)


def plugins_get_latest_packages():
    logger.info()

    parameters = {"plugin": config.PLUGIN_NAME, "platform": config.get_platform()}
    return remote_call("plugins/get_latest_packages.php", parameters)
