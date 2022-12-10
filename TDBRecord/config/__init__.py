import TDBRecord as tdbra

import pathlib
import subprocess

DEFAULT_CONFIG = {
    "remote_streamlink": "", # Remote streamlink server, if not set, use local streamlink e.g. "http://www.example.com/api/get"
    "downloadPath": "/mnt/download/",
    "ffmpeg": "ffmpeg", # ffmpeg path, if not set, use PATH ffmpeg
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

    if not tdbra.conf["ffmpeg"]:
        tdbra.conf["ffmpeg"] = "ffmpeg"
    
    # check ffmpeg is installed
    try:
        subprocess.run([tdbra.conf["ffmpeg"], "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        tdbra.logger.error("ffmpeg not found")
        raise ValueError("ffmpeg not found")
    except FileNotFoundError:
        tdbra.logger.error("ffmpeg not found")
        raise ValueError("ffmpeg not found")

    pass