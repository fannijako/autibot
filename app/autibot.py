import os

import discord
from discord.ext import commands
from langchain_huggingface import HuggingFaceEndpoint
from transformers import AutoTokenizer

from utils import load_env
from vector_db import create_astra_client, get_information_to_query


load_env()
model_id = "HuggingFaceH4/zephyr-7b-beta"
tokenizer = AutoTokenizer.from_pretrained(model_id)

llm = HuggingFaceEndpoint(
    repo_id=model_id,
    huggingfacehub_api_token=os.environ['HUGGINGFACE_TOKEN'],
    max_new_tokens=512,
    stop_sequences=[tokenizer.eos_token],
    streaming=True,
)

astra_client = create_astra_client()

def format_prompt(prompt):
    info = get_information_to_query(astra_client, prompt)

    chat = [
        {
            "role": "system", 
            "content":  """
                        Egy segítőkész AI asszisztens vagy, aki autizmussal élő személyeknek 
                        vagy a hozzátartozóiknak információval szolgál az általad elérhető 
                        adatbázisok alapján.
                        """
        },
        {"role": "user", 
            "content": f"""
                        Az alábbi információkat kaptad a megosztott hivatalos dokumentumokból: {info}: 
                        
                        Ezek alapján válaszolj a következő kérdésre: {prompt}
                        
                        Ne adj hozzá semmit a válaszodhoz, csak a kérdésedre adott választ!
                        
                        Válaszod:
                        """
        }
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