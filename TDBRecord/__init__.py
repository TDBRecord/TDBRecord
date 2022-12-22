import TDBRecord.command
import TDBRecord.m3u8
import TDBRecord.config


from prompt_toolkit import PromptSession, print_formatted_text
from streamlink import Streamlink
from pathlib import Path
import logging

streamlink = Streamlink()
psession = PromptSession()
input = psession.prompt

# Logging
class PromptHandler(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        print_formatted_text(msg)

logger = logging.getLogger("TDBRecord")
logger.handlers = [PromptHandler()]
logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s # %(message)s'))
lm = "[{user}.{platform}] {msg}"
logger.setLevel(logging.INFO)

def create_logger(name: str, platform: str) -> logging.Logger:
    ulogger = logging.getLogger(name)
    ulogger.handlers = [PromptHandler()]
    ulogger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - [{user}.{platform}] # %(message)s'.format(user=name, platform=platform)))
    ulogger.setLevel(logger.level)
    ulogger.propagate = False
    return ulogger

def create_data(user: str, platform: str, thread = None) -> dict:
    return {
        "exit": False,
        "logger": create_logger(user, platform),
        "thread": thread,
    }




conf = {}
data = {}
downloadPath = Path(".")

""" data
{
    "user.platform": {
        "exit": false,
        "logger": logger,
    }
}
"""
