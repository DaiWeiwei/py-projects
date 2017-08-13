# coding=utf-8
import Queue
from robot.api import logger

LOG_QUEQUE = Queue.Queue()


def cache_log(msg, level="INFO"):
    LOG_QUEQUE.put([msg, level])


def write_cached_log():
    try:
        log = LOG_QUEQUE.get(False)
        if not log:
            return
        logger.write(log[0], log[1])
    except:
        pass

