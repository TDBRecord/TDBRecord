import TDBRecord as tdbra

import pathlib
import logging
import click
import json

__version__ = "1.0.4"

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
    if debug: tdbra.logger.setLevel(logging.DEBUG)
    tdbra.conf = json.loads(config.read_text())

    tdbra.logger.addHandler(logging.FileHandler(logfile))
    tdbra.logger.info("TDBRecord started!")

    tdbra.config.check_config()
    tdbra.command.start()

@main.command()
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--remote-streamlink", is_flag=True, help="Use remote streamlink")
@click.option("--download-path", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path), help="Download file", default="download/")
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
def record(debug, user, platform, remote_streamlink, download):
    """
    Standalone record command. Only record one user.
    """
    if debug: tdbra.loglevel = logging.DEBUG
    tdbra.conf["remote_streamlink"] = remote_streamlink
    tdbra.downloadPath = download.resolve()
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
