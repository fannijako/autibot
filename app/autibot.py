import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.dirname(os.path.abspath(__file__)) + '/.env')

# Create bot instance with command prefix '!'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    # Prevent bot from responding to its own messages
    if message.author == bot.user:
        return

    # Send "Hello World" whenever a user sends a message
    await message.channel.send('Hello World')
    
    # Process commands if you want to add them later
    await bot.process_commands(message)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run(os.environ.get('DISCORD_TOKEN')) 