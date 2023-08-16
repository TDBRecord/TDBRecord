import TDBRecord.command
import TDBRecord.m3u8
import TDBRecord.config


from prompt_toolkit import PromptSession, print_formatted_text
from streamlink import Streamlink
from pathlib import Path
import logging
__version__ = ""

streamlink = Streamlink()
psession = PromptSession()
input = psession.prompt
print = print_formatted_text
gc = None
# Logging
class PromptHandler(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        print_formatted_text(msg)

logFilePath = Path("record.log")
logger = logging.getLogger("TDBRecord")
logger.handlers = [PromptHandler()]
logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s # %(message)s'))
lm = "[{user}.{platform}] {msg}"
logger.setLevel(logging.INFO)
logging.getLogger("streamlink.plugins.afreeca").handlers = [PromptHandler()]
logging.getLogger("streamlink.plugins.afreeca").handlers[0].setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - afreecatv # %(message)s'))

def create_logger(name: str, platform: str) -> logging.Logger:
    ulogger = logging.getLogger(name)
    ulogger.handlers = [PromptHandler(), logging.FileHandler(logFilePath)]
    for handler in ulogger.handlers:
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - [{user}.{platform}] # %(message)s'.format(user=name, platform=platform)))
    ulogger.setLevel(logger.level)
    ulogger.handlers[1].setLevel(logging.DEBUG)
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
confPath = Path("config.json")
downloadPath = Path("download/")