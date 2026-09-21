import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level_file=logging.DEBUG,
    level_stdout=logging.INFO,
    log_file: Optional[Path] = None,
):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Allow all levels, handlers will filter

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    # Set up formatter
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    # Stream (stdout) handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level_stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        if not log_file.exists():
            log_file.touch()
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setLevel(level_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
