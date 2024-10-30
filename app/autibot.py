import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from llama_cpp import Llama
import psutil


load_dotenv(os.path.dirname(os.path.abspath(__file__)) + '/.env')

physical_cores = psutil.cpu_count(logical=False)
optimal_threads = max(1, physical_cores - 1)  # Use optimal thread count

llm = Llama(
    model_path="./models/llama-2-7b-chat.Q2_K.gguf",
    n_ctx=2048,  # Context window
    n_threads=optimal_threads  # Use optimal thread count
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def get_llama_response(prompt):
    response = llm.create_completion(
        prompt,
        max_tokens=512,
        temperature=0.7,
        stop=["User:", "\n"],
        echo=False
    )
    return response['choices'][0]['text'].strip()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    try:
        async with message.channel.typing():
            response = await get_llama_response(message.content)
            await message.channel.send(response)
    except Exception as e:
        await message.channel.send(f"Sorry, I encountered an error: {str(e)}")
    
    await bot.process_commands(message)

bot.run(os.environ.get('DISCORD_TOKEN')) 