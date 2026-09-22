import logging
import sys
import colorlog
from game.core.settings import LOGGER_FILE_PATH

def setup_logger():
    log = logging.getLogger()
    if log.hasHandlers():
        return  # do not configure more than once

    level = logging.DEBUG  # change to INFO if prod
    log.setLevel(level)

    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(
        filename=LOGGER_FILE_PATH,
        mode="w",
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    log.addHandler(file_handler)

    if sys.stdout is not None:
        console_formatter = colorlog.ColoredFormatter(
            fmt="%(cyan)s%(asctime)s%(reset)s [%(log_color)s%(levelname)s%(reset)s] "
                "%(white)s%(message)s%(reset)s (%(cyan)s%(filename)s:%(lineno)d%(reset)s)",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            }
        )
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        log.addHandler(console_handler)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        log.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception
