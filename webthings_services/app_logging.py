####
# Code bases on article "Python Logging: An In-Depth Tutorial"
# https://www.toptal.com/python/in-depth-python-logging
####

import logging
import sys
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "app.log"


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler(file=LOG_FILE):
    file_handler = TimedRotatingFileHandler(file, encoding='utf-8', when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, level=logging.DEBUG, output_to_file=None):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)  # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    if output_to_file:
        logger.addHandler(get_file_handler(output_to_file))
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
