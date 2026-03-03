import functools
import logging


@functools.lru_cache
def retrieve_logger(
        name: str,
        level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)

    logger.setLevel(level)

    channel = logging.StreamHandler()
    channel.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    channel.setFormatter(formatter)

    logger.addHandler(channel)

    return logger
