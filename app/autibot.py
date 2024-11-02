"""
Module for running the bot. Entrypoint for the Docker container.
Sets up logging and the bot.
"""

from discord_bot import initiate_bot
from utils import set_logging


def main() -> None:
    """
    Main function to run the bot.
    Entrypoint for the Docker container.
    Initializes logging and the bot.

    Params:
        None
    Returns:
        None
    """

    set_logging()
    initiate_bot()


if __name__ == "__main__":
    main()
