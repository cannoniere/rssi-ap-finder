import logging
import log
from config import settings

#logger = logging.getLogger(__name__)

def func(log_queue):
    logger = log.configure_queue_logger(__name__, log_queue)
    logger.warning('This is a warning from module.func')
    return
