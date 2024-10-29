import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from langflow.load import run_flow_from_json


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
    
    await message.channel.send(run_flow_from_json(flow=os.path.join(os.path.dirname(os.path.abspath(__file__)), "AskAI.json"),
                            input_value="message",
                            fallback_to_env_vars=True,
                            tweaks={
                                "TextInput-NfsD4": {
                                    "input_value": message.content
                                }}))
    
    # Process commands if you want to add them later
    await bot.process_commands(message)

bot.run(os.environ.get('DISCORD_TOKEN')) 