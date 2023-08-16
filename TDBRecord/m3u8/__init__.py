import TDBRecord as tdbra

from subprocess import Popen, PIPE, DEVNULL
from streamlink import Streamlink
from requests import get
from pathlib import Path
import time

session = Streamlink()
sessionProxy = Streamlink()

urlstore = {
    "twitch": "https://twitch.tv/{user}",
    "afreecatv": "https://play.afreecatv.com/{user}",
    "youtube": "https://www.youtube.com/@{user}/live",
}

def worker(user: str, platform: str) -> None:
    """
    Standalone video downloader
    """
    logger = tdbra.data[f"{user}.{platform}"]["logger"]
    logger.setLevel(tdbra.logger.level)
    downloadPath = tdbra.downloadPath / f"{user}.{platform}"
    downloadPath.mkdir(parents=True, exist_ok=True)
    filename = f"{platform}.{user}.{time.strftime('%y%m%d.%H%M%S')}"

    downloadFullPath = downloadPath / f"{filename}.mp4"
    m3uPlaylistUri = stream(user, platform)
    logger.info("FFMPEG Downloader started.")

    # Downloader
    m3ud = get(m3uPlaylistUri)
    if "twitch-ad-quartile" in m3ud.text:
        while True:
            if tdbra.data[f"{user}.{platform}"]["exit"]:
                logger.info("FFMPEG Downloader stopped.")
                del(tdbra.data[f"{user}.{platform}"])
                return

            m3ud = get(m3uPlaylistUri)
            if "twitch-ad-quartile" in m3ud.text:
                logger.debug("Waiting for AD to record...")
                time.sleep(2)
                continue
            break
        logger.info("AD finished. Start recording...")

    tdbra.downloadPath.mkdir(parents=True, exist_ok=True)
    tdbra.logger.debug(f"Download path: {downloadFullPath}")
    command = [
        tdbra.conf["ffmpeg"],
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        m3uPlaylistUri,
        "-c",
        "copy",
        str(downloadFullPath),
    ]
    if checkProxy(user, platform):
        command.insert(1, "-http_proxy")
        command.insert(2, tdbra.conf["proxy"])
    raw = ""
    for i in command:
        raw += f"{i} "
    logger.debug(f"FFMPEG Downloader command: {raw}")
    #logger.debug(f"FFMPEG Downloader command as list: {command}")
    
    ffmpeg = Popen(command, stdin=PIPE)
    tdbra.data[f"{user}.{platform}"]["ffmpeg"] = ffmpeg
    
    while True:
        if tdbra.data[f"{user}.{platform}"]["exit"]:
            logger.debug("Trying to stop FFMPEG Downloader...")
            ffmpeg.communicate(input=b"q")
            for i in range(6):
                logger.debug(f"Waiting for FFMPEG Downloader to finish... ({i+1}/6)")
                if ffmpeg.poll() is not None:
                    logger.info(f"FFMPEG Downloader finished with status {ffmpeg.poll()}.")
                    del(tdbra.data[f"{user}.{platform}"])
                    return
                time.sleep(1)
            ffmpeg.kill()
            logger.warning("FFMPEG Downloader killed.")
            del(tdbra.data[f"{user}.{platform}"])
            return
        if ffmpeg.poll() is not None:
            logger.info(f"FFMPEG Downloader finished with status {ffmpeg.poll()}.")
            tdbra.data[f"{user}.{platform}"]["end"] = True
            break
        time.sleep(1)
    if tdbra.gc:
        tdbra.autocheck(tdbra.ls, user, platform, downloadFullPath, logger)

    del(tdbra.data[f"{user}.{platform}"])

def stream(user: str, platform: str) -> str:
    if checkProxy(user, platform):
        return sessionProxy.streams(urlstore[platform].format(user=user))["best"].url
    else:    
        return session.streams(urlstore[platform].format(user=user))["best"].url

def checkStatus(user: str, platform: str) -> bool:
    try:
        if checkProxy(user, platform):
            return bool(sessionProxy.streams(urlstore[platform].format(user=user)))
        else:
            return bool(session.streams(urlstore[platform].format(user=user)))
    except Exception as e:
        tdbra.logger.error(f"Cannot check status of {user}.{platform}: {e}")
        if tdbra.debug: raise e
        return False

def checkProxy(user: str, platform: str) -> bool:
    for i in tdbra.conf["users"]:
        if i["name"] == user and i["platform"] == platform and i["proxy"]:
            return True

    return False