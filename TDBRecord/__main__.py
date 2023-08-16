import TDBRecord as tdbra

import requests
import pathlib
import logging
import click
import json

__version__ = "1.2.0-pre7"
tdbra.__version__ = __version__


def check_update():
    # check from pypi
    try:
        pypi_version = requests.get("https://pypi.org/pypi/TDBRecord/json").json()["info"]["version"]
    except:
        tdbra.logger.error("Cannot check update")
        return
    if "pre" in __version__: 
        tdbra.logger.info("You are using pre-release version. Please check update manually.")
        tdbra.logger.info("Current version: {version}".format(version=__version__))
        tdbra.logger.info("Latest version: {version}".format(version=pypi_version))
    elif pypi_version != __version__:
        tdbra.logger.info("New version available: {version}".format(version=pypi_version))
        tdbra.logger.info("Please update TDBRecord by 'pip install TDBRecord --upgrade'")
    return



@click.version_option(prog_name="TDBRecord", version=__version__)
@click.group()
def main():
    """
    TDB Record Application for OpenSourceUsers
    """
    pass

@main.command()
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--config", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path), help="Config file", default="config.json")
@click.option("--logfile", type=click.Path(file_okay=True, dir_okay=False, path_type=pathlib.Path), help="Log file", default="record.log")
def start(debug, config, logfile):
    """
    Start TDBRecord server for multiple users.
    """
    check_update()

    tdbra.confPath = config
    if debug: tdbra.logger.setLevel(logging.DEBUG)
    tdbra.conf = json.loads(tdbra.confPath.read_text())

    tdbra.logFilePath = logfile
    tdbra.logger.addHandler(logging.FileHandler(tdbra.logFilePath))
    tdbra.logger.handlers[1].setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s # %(message)s'))
    tdbra.logger.handlers[1].setLevel(logging.DEBUG)
    logging.getLogger("streamlink.plugins.afreeca").addHandler(logging.FileHandler(tdbra.logFilePath))
    logging.getLogger("streamlink.plugins.afreeca").handlers[1].setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - afreecatv # %(message)s'))
    logging.getLogger("streamlink.plugins.afreeca").handlers[1].setLevel(logging.INFO)
    tdbra.logger.info("TDBRecord started!")

    tdbra.config.check_config()
    tdbra.command.start()

@main.command()
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--proxy", help="Proxy Url", default=None)
@click.option("--download-path", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path), help="Download folder", default="download/")
@click.option("--ffmpeg", type=str, help="FFmpeg path", default="ffmpeg")
@click.argument(
    "user",
    type=str,
    required=True,
)
@click.argument(
    "platform",
    type=str,
    required=True,
)
def record(debug, user, platform, proxy, download_path, ffmpeg):
    """
    Standalone record command. Only record one user.
    """

    check_update()

    if debug: tdbra.loglevel = logging.DEBUG
    if proxy: tdbra.conf["proxy"] = proxy
    if ffmpeg: tdbra.conf["ffmpeg"] = ffmpeg
    else: tdbra.conf["ffmpeg"] = "ffmpeg"

    if download_path: tdbra.downloadPath = download_path
    tdbra.command.record(user, platform)

@main.command()
def config():
    """
    Generate config file
    """
    config = pathlib.Path("config.json")
    if config.exists():
        print("Config file already exists")
        return
    tdbra.config.DEFAULT_CONFIG["version"] = __version__
    
    config.write_text(json.dumps(tdbra.config.DEFAULT_CONFIG, indent=4))
    tdbra.logger.info("Config file generated")
