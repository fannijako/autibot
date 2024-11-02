import discord
import logging
from discord.ext import commands

from llm import get_llama_response, create_tokenizer, create_llm_client
from vector_db import create_astra_client


def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    return bot


ASTRA_CLIENT = None
TOKENIZER = None
LLM = None


@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')

    global ASTRA_CLIENT, TOKENIZER, LLM

    ASTRA_CLIENT = create_astra_client()
    TOKENIZER = create_tokenizer()
    LLM = create_llm_client(TOKENIZER)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    try:
        logging.info(f'Received message: {message.content}')

        async with message.channel.typing():
            response = await get_llama_response(ASTRA_CLIENT, LLM, TOKENIZER, message.content)
            await message.channel.send(response)

    except Exception as e:
        logging.error(f'Error processing message: {str(e)}')
        await message.channel.send(f"Sorry, I encountered an error: {str(e)}")

    await bot.process_commands(message)
