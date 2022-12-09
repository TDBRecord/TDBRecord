import TDBRecord as tdbra

import pathlib

DEFAULT_CONFIG = {
    "remote_streamlink": "", # Remote streamlink server, if not set, use local streamlink e.g. "http://www.example.com/api/get"
    "users": [
        {
            "name": "ExampleUser1",
            "platform": "twitch | afreecatv"
        },
        {
            "name": "ExampleUser2",
            "platform": "twitch | afreecatv"
        }
    ],
    "downloadPath": "/mnt/download/"
}

PLATFORMS = ["twitch", "afreecatv"]

def check_config():
    if not tdbra.conf["users"]:
        tdbra.logger.error("No user found in config file")
        raise ValueError("No user found in config file")
    
    for user in tdbra.conf["users"]:
        if not user["name"]:
            tdbra.logger.error("User name not found in config file")
            raise ValueError("User name not found in config file")
        if not user["platform"]:
            tdbra.logger.error("User platform not found in config file")
            raise ValueError("User platform not found in config file")
        if user["platform"] not in PLATFORMS:
            tdbra.logger.error("User platform not found in config file")
            raise ValueError("User platform not found in config file")
    
    if not tdbra.conf["downloadPath"]:
        tdbra.logger.error("Download path not found in config file")
        raise ValueError("Download path not found in config file")
    tdbra.downloadPath = pathlib.Path(tdbra.conf["downloadPath"])
    tdbra.downloadPath.mkdir(parents=True, exist_ok=True)
    pass