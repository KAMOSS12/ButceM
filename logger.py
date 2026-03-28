"""
BütçeM - Merkezi Loglama Sistemi
Rotating file handler ile %APPDATA%/ButceM/logs/ altına yazar.
Geliştirme modunda script dizinine yazar.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler


def _get_log_dir():
    """Log dizinini belirle."""
    if getattr(sys, 'frozen', False):
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            return os.path.join(appdata, 'ButceM', 'logs')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')


def get_logger(name="butcem"):
    """Modül bazlı logger döndür."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_level = logging.DEBUG if not getattr(sys, 'frozen', False) else logging.INFO
    logger.setLevel(log_level)

    log_dir = _get_log_dir()
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "butcem.log")
        file_handler = RotatingFileHandler(
            log_path, maxBytes=1_048_576, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass

    return logger
