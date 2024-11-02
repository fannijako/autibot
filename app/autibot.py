"""
Module for running the bot. Entrypoint for the Docker container.
Sets up logging and the bot.
"""

import os

from discord_bot import initiate_bot, bot_on_ready, bot_on_message
from utils import set_logging, load_env


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

    load_env()
    set_logging()
    bot = initiate_bot()
    bot.run(os.environ.get('DISCORD_TOKEN'))


    @bot.event
    async def on_ready():
        bot_on_ready(bot)


    @bot.event
    async def on_message(message):
        bot_on_message(bot, message)


if __name__ == "__main__":
    main()
