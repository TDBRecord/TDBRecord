import TDBRecord as tdbra

from subprocess import Popen, PIPE, DEVNULL
from streamlink import Streamlink
from requests import get
from pathlib import Path
import time

session = Streamlink()

urlstore = {
    "twitch": "https://twitch.tv/{user}",
    "afreecatv": "https://play.afreecatv.com/{user}",
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
        downloadFullPath
    ]
    if tdbra.conf["proxy"]:
        command.insert(1, "-http_proxy")
        command.insert(2, tdbra.conf["proxy"])
    raw = ""
    for i in command:
        raw += f"{i} "
    logger.debug(f"FFMPEG Downloader command: {raw}")
    
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
    if tdbra.conf["remote_streamlink"] and platform == "twitch":
        return get(f"{tdbra.conf['remote_streamlink']}/{user}?quality=best").text
    else:
        return session.streams(urlstore[platform].format(user=user))["best"].url

def checkStatus(user: str, platform: str) -> bool:
    if tdbra.conf["proxy"]:
        session.set_option("http-proxy", tdbra.conf["proxy"])
    try:
        if session.streams(urlstore[platform].format(user=user)):
            return True
        else:
            return False
    except:
        tdbra.logger.error(f"Failed to check status of {user}.{platform}")
        return False
