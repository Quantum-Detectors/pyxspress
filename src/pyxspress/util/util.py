"""
General utility module

Provides generic utility functions
"""

import logging

# Global stream handler used by this module for logging
console_handler = logging.StreamHandler()
module_name = "pyxspress"


def setup_basic_logging(log_level: int | str = logging.INFO) -> logging.Logger:
    """Set up logging for this module

    Args:
        log_level (int, optional): Log level for messages. Defaults to logging.INFO.

    Returns:
        logging.Logger: The module logger instance
    """
    logging_format = "[%(asctime)s][%(levelname)7s][%(name)s] %(message)s"
    formatter = logging.Formatter(logging_format)

    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)
    logger.addHandler(console_handler)

    return logger


def get_module_logger(sub_module: str | None = None) -> logging.Logger:
    """Get the module-wide logger

    Args:
        sub_module (str | None, optional): Optional sub-module to add to logger
                                           name. Defaults to None.

    Returns:
        logging.Logger: Module logger
    """
    if sub_module:
        return logging.getLogger(f"{module_name}.{sub_module}")
    else:
        return logging.getLogger(module_name)
