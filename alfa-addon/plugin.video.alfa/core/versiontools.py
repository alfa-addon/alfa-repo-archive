# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# Version Tools
# --------------------------------------------------------------------------------

import os

import config
import scrapertools


def get_current_plugin_version():
    return 4300


def get_current_plugin_version_tag():
    return "4.3.0-beta1"


def get_current_plugin_date():
    return "30/06/2017"


def get_current_channels_version():
    f = open(os.path.join(config.get_runtime_path(), "channels", "version.xml"))
    data = f.read()
    f.close()

    return int(scrapertools.find_single_match(data, "<version>([^<]+)</version>"))


def get_current_servers_version():
    f = open(os.path.join(config.get_runtime_path(), "servers", "version.xml"))
    data = f.read()
    f.close()

    return int(scrapertools.find_single_match(data, "<version>([^<]+)</version>"))
