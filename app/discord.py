"""
Module for interacting with the Discord bot.
Initialization, on_ready and on_message event handlers.
"""

import discord
import logging
import os

from discord.ext import commands

from llm import (
    get_llama_response,
    create_tokenizer,
    create_llm_client
    )

from vector_db import create_astra_client


ASTRA_CLIENT = None
TOKENIZER = None
LLM = None


def initiate_bot() -> None:
    """
    Initializes the bot and runs it.

    Params:
        None
    Returns:
        None
    """

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    logging.info('Bot initialized.')
    bot.run(os.environ.get('DISCORD_TOKEN'))


@bot.event
async def on_ready() -> None:
    """
    Event handler for when the bot is ready (connected to Discord and ready to respond).
    Creates the Astra client, tokenizer and LLM client as global variables.

    Params:
        None
    Returns:
        None
    """

    logging.info(f'{bot.user} has connected to Discord!')

    global ASTRA_CLIENT, TOKENIZER, LLM

    ASTRA_CLIENT = create_astra_client()
    TOKENIZER = create_tokenizer()
    LLM = create_llm_client(TOKENIZER)


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    Event handler for when a message is sent in a channel.
    Processes the message and sends a response if the message is not from the bot itself.

    Calls the Vector DB to provide context, 
    generates the prompt, formats it
    and sends it to the LLM to generate a response to the message.

    Params:
        message (discord.Message): The message sent by a user.
    Returns:
        None
    """

    if message.author == bot.user:
        return

    logging.info(f'Received message: {message.content}')

    try:
        async with message.channel.typing():
            response = await get_llama_response(ASTRA_CLIENT, LLM, TOKENIZER, message.content)
            logging.info(f'Generated response: {response}')
            await message.channel.send(response)

    except Exception as e:
        logging.error(f'Error processing message: {str(e)}')
        await message.channel.send(f"""Elnézést, hibába ütköztem. Próbáld újra később.
                                   Ha akkor is fennáll a hiba, akkor írj fannijako@gmail.com email címre.""")

    await bot.process_commands(message)
