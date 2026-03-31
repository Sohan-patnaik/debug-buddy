import logging
import sys
from typing import Optional


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_to_file: Optional[str] = None
) -> logging.Logger:
    """
    Create and return a configured logger.

    Args:
        name (str): Name of the logger (usually __name__)
        level (int): Logging level (DEBUG, INFO, etc.)
        log_to_file (str, optional): File path to log into

    Returns:
        logging.Logger
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger


    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_to_file:
        file_handler = logging.FileHandler(log_to_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger