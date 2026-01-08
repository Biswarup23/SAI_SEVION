import logging, os
from logging.handlers import TimedRotatingFileHandler
import platformdirs
from sai_devion.config import APP_NAME

def setup_logging():
    log_dir = platformdirs.user_log_dir(APP_NAME, "SAI_GEN")
    # log_dir = './log'

    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, "app.log")
    # print("LOG PATH:", log_path)

    handler = TimedRotatingFileHandler(log_path, when="midnight", backupCount=14, encoding="utf-8")

    logging.basicConfig(
        handlers=[handler],
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("=== App Started ===")
