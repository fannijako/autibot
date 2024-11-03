"""
Module for interacting with the LLM.
Client creation, prompt formatting and response generation based on
the Astra Vector Database similarity search results and the chat history.
"""

import os
import logging

from astrapy import DataAPIClient
from langchain_huggingface import HuggingFaceEndpoint
from transformers import AutoTokenizer

from app.utils import MODEL_ID
from app.vector_db import get_information_to_query


def create_tokenizer() -> AutoTokenizer:
    """
    Creates a tokenizer for the LLM.

    Params:
        None
    Returns:
        AutoTokenizer: The tokenizer.
    """
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    logging.info('Tokenizer created.')
    return tokenizer


def create_llm_client(max_new_tokens: int = 512, streaming: bool = True) -> HuggingFaceEndpoint:
    """
    Creates an LLM client.

    Params:
        max_new_tokens (int): The maximum number of new tokens to generate.
        streaming (bool): Whether to stream the response.

    Returns:
        HuggingFaceEndpoint: The LLM client.
    """
    llm = HuggingFaceEndpoint(
            repo_id=MODEL_ID,
            huggingfacehub_api_token=os.environ.get('HUGGINGFACE_TOKEN'),
            max_new_tokens=max_new_tokens,
            streaming=streaming,
        )
    logging.info('LLM client created.')

    return llm


def format_prompt(info: str, tokenizer: AutoTokenizer, prompt: str, chat_history: str = "") -> str:
    """
    Formats the prompt for the LLM.

    Params:
        info (str): The information to query.
        tokenizer (AutoTokenizer): The tokenizer.
        prompt (str): The prompt.
        chat_history (str): The chat history.

    Returns:
        str: The formatted prompt.
    """

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
                        Az alábbi információkat kaptad a megosztott
                        hivatalos dokumentumokból: {info}:

                        Korábbi beszélgetések: {chat_history}

                        Ezek alapján válaszolj a következő kérdésre: {prompt}

                        Ne adj hozzá semmit a válaszodhoz, csak a kérdésedre adott választ!

                        Magyarul válaszolj és adj kerek mondatokat!
                        Ha egy mondatot nem tudsz befejezni, ne kezdj bele.

                        Amennyiben releváns, megadhatod a pontos referenciát
                        a megosztott hivatalos dokumentumokból.

                        Válaszod:
                        """},
    ]

    formatted_prompt = tokenizer.apply_chat_template(
        chat,
        tokenize=False,
        add_generation_prompt=True
    )

    logging.info(f'Prompt formatted: {formatted_prompt}.')

    return formatted_prompt


async def get_llama_response(astra_client: DataAPIClient,
                             llm: HuggingFaceEndpoint,
                             tokenizer: AutoTokenizer,
                             prompt: str,
                             conversation_history: str) -> str:
    """
    Gets the response from the LLM.

    Params:
        astra_client (DataAPIClient): The Astra client.
        llm (HuggingFaceEndpoint): The LLM client.
        tokenizer (AutoTokenizer): The tokenizer.
        prompt (str): The prompt.
        conversation_history (str): The conversation history.
    Returns:
        str: The response from the LLM.
    """

    information = get_information_to_query(astra_client, prompt)
    logging.info(f'Information to query: {information}.')

    context = "\n".join([info.get("$vectorize") for info in information])

    response = llm.invoke(
        format_prompt(context, tokenizer, prompt, conversation_history)
    )

    logging.info(f'Response: {response}.')

    return response
