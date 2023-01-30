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
    downloadPath = tdbra.downloadPath / f"{user}.{platform}/"
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
            logger.debug("Waiting for AD to start...")
            time.sleep(2)
            continue
        break

    logger.info("AD finished. Start recording...")
    logger.debug(f"{tdbra.conf['ffmpeg']} -y -hide_banner -loglevel error -i {m3uPlaylistUri} -c copy {downloadFullPath}")
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
        command.extend(["-http_proxy", tdbra.conf["proxy"]])
    ffmpeg = Popen(command, stdin=PIPE)
    while True:
        if tdbra.data[f"{user}.{platform}"]["exit"]:
            ffmpeg.communicate(input=b"q")
            for i in range(6):
                if ffmpeg.poll() is not None:
                    logger.info(f"FFMPEG Downloader finished with status {ffmpeg.poll()}.")
                    if downloadFullPath.exists(): downloadFullPath.unlink()
                    del(tdbra.data[f"{user}.{platform}"])
                    return
                time.sleep(1)
            ffmpeg.kill()
            logger.warning("FFMPEG Downloader killed.")
            if downloadFullPath.exists(): downloadFullPath.unlink()
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
    try:
        if session.streams(urlstore[platform].format(user=user)):
            return True
        else:
            return False
    except:
        tdbra.logger.error(f"Failed to check status of {user}.{platform}")
        return False
