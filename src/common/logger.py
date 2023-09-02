from logging.config import dictConfig

from yaml import safe_load


def init_logger(filepath: str) -> None:
    with open(filepath) as f:
        config = safe_load(f)
    dictConfig(config)
