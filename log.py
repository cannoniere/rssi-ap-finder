#!/usr/bin/env python3

import logging
import logging.handlers
import multiprocessing as mp
from config import settings

STOP = settings.stop
LOGGING_LEVEL = settings.logging_level

global log_queue

def configure_queue_logger(name) -> logging.Logger:
    """
    This logger does not write to console directly.
    It sends all log records to the multiprocessing.Queue.
    """
    logger = logging.getLogger(name.strip('_'))
    logger.setLevel(LOGGING_LEVEL)
    logger.propagate = False

    # Avoid duplicate handlers if this is called more than once
    logger.handlers.clear()

    queue_handler = logging.handlers.QueueHandler()
    queue_handler.setLevel(LOGGING_LEVEL)

    logger.addHandler(queue_handler)
    return logger


def configure_console_logger() -> logging.Logger:
    """
    This logger writes records to the console.
    It is used only by the listener process.
    """
    logger = logging.getLogger("console_logger")
    logger.setLevel(LOGGING_LEVEL)
    logger.propagate = False

    logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOGGING_LEVEL)

    formatter = logging.Formatter(
#        fmt="%(asctime)s | %(processName)s | %(levelname)s | %(message)s",
        fmt="%(asctime)s.%(msecs)03d | %(processName)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d_%H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


def log_listener_process(log_queue: mp.Queue) -> None:
    """
    Reads LogRecord objects from the queue and writes them to console.
    """
    console_logger = configure_console_logger()

    while True:
        record = log_queue.get()

        if record is STOP:
            break

        # Handle the original record using the console logger's handlers.
        console_logger.handle(record)
