import logging


def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = logging.Formatter("%(asctime)s |:| %(levelname)s |:| %(message)s", "%Y-%m-%d %H:%M:%S")

    ch.setFormatter(formatter)
    
    logger.addHandler(ch)

    return logger
