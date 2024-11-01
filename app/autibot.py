import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from transformers import AutoTokenizer
from langchain_core.prompts import PromptTemplate


load_dotenv(os.path.dirname(os.path.abspath(__file__)) + '/.env')

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)

llm = HuggingFaceEndpoint(
    repo_id=model_id,
    huggingfacehub_api_token=os.environ['HUGGINGFACE_TOKEN'],
    max_new_tokens=512,
    stop_sequences=[tokenizer.eos_token],
    streaming=True,
)

def format_prompt(prompt):
    chat = [
        {
            "role": "system", 
            "content": "Egy segítőkész AI asszisztens vagy."},
        {"role": "user", "content": prompt},
    ]

    formatted_prompt = tokenizer.apply_chat_template(
        chat, 
        tokenize=False, 
        add_generation_prompt=True
    )

    return formatted_prompt


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def get_llama_response(prompt):
    response = llm.invoke(
        format_prompt(prompt)
    )
    return response

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