import TDBRecord as tdbra

import pathlib
import subprocess
import json
from importlib import import_module

DEFAULT_CONFIG = {
    "version": "",
    "downloadPath": "./download/",
    "ffmpeg": "ffmpeg", # ffmpeg path, if not set, use PATH ffmpeg
    "proxy": "", # proxy url, if not set, use system proxy. e.g. http://proxy.example.com:8080/
    "users": [
        {
            "name": "ExampleUser1",
            "platform": "twitch | afreecatv | youtube",
            "proxy": True
        },
        {
            "name": "ExampleUser2",
            "platform": "twitch | afreecatv | youtube",
            "proxy": False
        }
    ],
}

PLATFORMS = ["twitch", "afreecatv", "youtube"]

def check_config(conf: dict = {}):
    tdbr = False
    proxy = False
    if not conf:
        if not tdbra.conf:
            tdbra.logger.error("No config found")
            raise ValueError("No config found")
        conf = tdbra.conf
        tdbr = True

    if not "version" in conf:
        tdbra.logger.error("Old config file is not compatible with new version. Please delete old config file and run `tdbrec config` to create new config file.")
        raise ValueError("Old config file is not compatible with new version. Please delete old config file and run `tdbrec config` to create new config file.")
    elif conf["version"].split(".")[0] != tdbra.__version__.split(".")[0]:
        tdbra.logger.error("Old config file is not compatible with new version. Please delete old config file and run `tdbrec config` to create new config file.")
        raise ValueError("Old config file is not compatible with new version. Please delete old config file and run `tdbrec config` to create new config file.")
    elif conf["version"].split(".")[1] != tdbra.__version__.split(".")[1]:
        tdbra.logger.warning("Old config file is not compatible with new version. Please run `tdbrec config` to update config file.")
        tdbra.logger.warning("If you updated to new release, then there may be new config options. Please use `tdbrec config` for new options.")

    if not conf["users"]:
        tdbra.logger.error("No user found in config file")
        raise ValueError("No user found in config file")
    
    for user in conf["users"]:
        if not user["name"]:
            tdbra.logger.error("User name not found in config file")
            raise ValueError("User name not found in config file")
        if not user["platform"]:
            tdbra.logger.error("User platform not found in config file")
            raise ValueError("User platform not found in config file")
        if user["platform"] not in PLATFORMS:
            tdbra.logger.error("User platform not found in config file")
            raise ValueError("User platform not found in config file")
        if "proxy" not in user:
            user["proxy"] = False
        proxy = user["proxy"]


    if not conf["downloadPath"]:
        tdbra.error("Download path not found in config file")
        raise ValueError("Download path not found in config file")
    else:
        downloadPath = pathlib.Path(conf["downloadPath"])
        downloadPath.mkdir(parents=True, exist_ok=True)

    if not conf["ffmpeg"]:
        conf["ffmpeg"] = "ffmpeg"
    
    if "gc" in conf:
        try:
            gc = import_module(conf["gc"])
        except ImportError:
            tdbra.logger.error("Cannot import gc module")
            raise ValueError("Cannot import gc module")
        tdbra.gc = gc
        tdbra.ls = gc.ls(tdbra.logger)

    # check ffmpeg is installed
    try:
        subprocess.run([conf["ffmpeg"], "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        tdbra.logger.error("ffmpeg not found")
        raise ValueError("ffmpeg not found")
    except FileNotFoundError:
        tdbra.logger.error("ffmpeg not found")
        raise ValueError("ffmpeg not found")

    if "proxy" in conf and (conf["proxy"] != "" and conf["proxy"] != None):
        conf["proxy"] = conf["proxy"].strip()
        tdbra.m3u8.sessionProxy.set_option("http-proxy", conf["proxy"])
        tdbra.logger.debug(f"Proxy set to {conf['proxy']}")
    elif proxy:
        tdbra.logger.error("Proxy not found in config file")
        raise ValueError("Proxy not found in config file")
    else:
        conf["proxy"] = None

    
    if tdbr: 
        tdbra.conf = conf
        tdbra.downloadPath = downloadPath
    

    return conf, downloadPath

def reload():
    try:
        conf = json.loads(tdbra.confPath.read_text())
    except json.JSONDecodeError:
        tdbra.logger.error("Cannot decode Json file. Config not updated.")
        return False
    except FileNotFoundError:
        tdbra.logger.error("Config file not found. Config not updated.")
        return False
    try:
        conf, downloadPath = check_config(conf)
        tdbra.conf = conf
        tdbra.downloadPath = downloadPath
        tdbra.logger.info("Config updated.")
        return True
    except Exception as e:
        tdbra.logger.error(f"Config check error with <{e}>. Config not updated.")
        return False
