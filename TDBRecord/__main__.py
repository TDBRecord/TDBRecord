import TDBRecord as tdbra

import pathlib
import logging
import click
import json

__version__ = "1.1.0"

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
@click.option("--remote-streamlink", help="Remote streamlink Url", default="")
@click.option("--download-path", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path), help="Download folder", default=".")
@click.option("--save-path", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path), help="Save folder", default="download/")
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
def record(debug, user, platform, remote_streamlink, download_path, save_path, ffmpeg):
    """
    Standalone record command. Only record one user.
    """

    if debug: tdbra.loglevel = logging.DEBUG
    if remote_streamlink: tdbra.conf["remote_streamlink"] = remote_streamlink
    if ffmpeg: tdbra.conf["ffmpeg"] = ffmpeg
    else: tdbra.conf["ffmpeg"] = "ffmpeg"

    if download_path: tdbra.downloadPath = download_path
    tdbra.savePath = save_path
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
    config.write_text(json.dumps(tdbra.config.DEFAULT_CONFIG, indent=4))
    tdbra.logger.info("Config file generated")
