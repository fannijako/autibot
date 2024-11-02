import os

from discord import create_bot
from utils import load_env, set_logging



def main():
    load_env()
    set_logging()
    bot = create_bot()
    bot.run(os.environ.get('DISCORD_TOKEN'))


if __name__ == "__main__":
    main()
