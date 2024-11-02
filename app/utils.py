"""
Module for utility functions.
Loading environment variables and setting up logging.
"""

import os
import logging

from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler


MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"


def load_env() -> None:
    """
    Loads the environment variables from the .env file.

    Params:
        None

    Returns:
        None
    """

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(project_root, '.env'))


def set_logging() -> None:
    """
    Sets up the logging for the application with hourly rotation and 24 hours backup.

    Params:
        None

    Returns:
        None
    """

    os.makedirs('logs', exist_ok=True)

    file_handler = TimedRotatingFileHandler(
        filename='logs/autibot.log',
        when='H',
        interval=1,
        backupCount=24,
        encoding='utf-8'
    )

    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(file_handler)
