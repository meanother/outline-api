import pathlib
import datetime

from loguru import logger

log_dir = pathlib.Path.home().joinpath("logs")
log_dir.mkdir(parents=True, exist_ok=True)

logger.add(
    log_dir.joinpath("outline-api.log"),
    format="{time} [{level}] {module} {name} {function} - {message}",
    level="DEBUG",
    compression="zip",
    rotation="30 MB",
)


def get_dt() -> str:
    """return now dt"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def read_outline_config():
    with open("/opt/outline/access.txt", "r") as conf_file:
        conf = conf_file.read()
    cert, url = conf.split("\n")
    data = {
        "apiUrl": url.strip()[7:],
        "certSha256": cert.strip()[11:],
    }
    return data
