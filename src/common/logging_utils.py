import logging, os

def get_logger(name: str) -> logging.Logger:
    level = os.environ.get("LOG_LEVEL","INFO").upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
        logger.addHandler(h)
    logger.setLevel(level)
    return logger