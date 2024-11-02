import os

from langchain_huggingface import HuggingFaceEndpoint
from transformers import AutoTokenizer

from utils import MODEL_ID
from vector_db import get_information_to_query


def create_tokenizer():
    return AutoTokenizer.from_pretrained(MODEL_ID)


def create_llm_client(tokenizer, max_new_tokens=512, streaming=True):
    return HuggingFaceEndpoint(
        repo_id=MODEL_ID,
        huggingfacehub_api_token=os.environ.get('HUGGINGFACE_TOKEN'),
        max_new_tokens=max_new_tokens,
        stop_sequences=[tokenizer.eos_token],
        streaming=streaming,
    )


def format_prompt(info, tokenizer, prompt):

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


def get_llama_response(astra_client, llm, tokenizer, prompt):
    info = get_information_to_query(astra_client, prompt)

    response = llm.invoke(
        format_prompt(info, tokenizer, prompt)
    )

    return response
