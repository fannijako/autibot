"""
Module for running the bot. Entrypoint for the Docker container.
"""

import os
import logging

import discord
from discord.ext import commands

from app.chatbot import ChatBot


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
logging.info('Bot initialized.')

chatbot = ChatBot()


@bot.event
async def on_ready() -> None:
    """
    Event handler for when the bot is ready (connected to Discord and ready to respond).

    Params:
        None
    Returns:
        None
    """

    logging.info(f'{bot.user} has connected to Discord!')


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    Event handler for when a message is sent in a channel without the ! prefix.
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

    if not message.content.startswith('!'):
        try:
            async with message.channel.typing():
                response = await chatbot.process_rag_query(message.author, message.content)
            await message.channel.send(response)

        except Exception as e:
            logging.error(f'Error processing message: {str(e)}')

            await message.channel.send(chatbot.error_message)

    await bot.process_commands(message)


@bot.command()
async def clear_history(ctx: commands.Context) -> None:
    """
    Clear the conversation history for the user

    Params:
        ctx (commands.Context): The context of the command.
    Returns:
        None
    """

    logging.info(f'Clearing history for user {ctx.author.id}')

    chatbot.clear_history(ctx.author.id)
    await ctx.send("A beszélgetési előzményeid sikeresen törlésre kerültek!")


@bot.command()
async def show_history(ctx: commands.Context) -> None:
    """
    Show the current conversation history

    Params:
        ctx (commands.Context): The context of the command.
    Returns:
        None
    """

    logging.info(f'Showing history for user {ctx.author.id}')

    history = chatbot.get_conversation_history(ctx.author.id)

    if history:
        await ctx.send(f"A beszélgetési előzményeid:\n```\n{history}\n```")
    else:
        await ctx.send("Nincs aktív beszélgetésed elmentve. Indíts új beszélgetést!")


bot.run(os.environ.get('DISCORD_TOKEN'))
