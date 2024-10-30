import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv(os.path.dirname(os.path.abspath(__file__)) + '/.env')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return    
    
    await message.channel.send(message.content)
    

bot.run(os.environ.get('DISCORD_TOKEN')) 