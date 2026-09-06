import logging
import os
from logging.handlers import RotatingFileHandler

# LOG_DIR OneDrive-aware si existe, sino local (evita logs en _internal en frozen)
try:
    from utils.constants import APP_DIR, detectar_onedrive
    od = detectar_onedrive()
    if od:
        LOG_DIR = os.path.join(od, "Academia", "logs")
    else:
        LOG_DIR = os.path.join(APP_DIR, "logs")
except Exception:
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logger(name: str = "academia") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "academia.log"),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
