"""
Module for the chatbot.
Handling the conversation history and the RAG approach.
"""

import logging

from collections import defaultdict
from datetime import datetime, timedelta

from app.llm import (
    get_llama_response,
    create_tokenizer,
    create_llm_client
    )

from app.utils import (
    set_logging,
    load_env
    )

from app.vector_db import create_astra_client


class ChatBot:
    """
    Class for the chatbot. Defines the chat history and the RAG approach.

    Params:
        max_history_length (int): The maximum length of the chat history.
        history_expiry (timedelta): The expiry time for the chat history.
        error_message (str): The error message to send to the user.

    Attributes:
        astra_client (DataAPIClient): The Astra client.
        llm (HuggingFaceEndpoint): The LLM client.
        tokenizer (AutoTokenizer): The tokenizer.
        chat_histories (defaultdict): The chat histories.

    Methods:
        add_to_history: Add a message to the user's chat history.
        _clean_old_history: Remove expired messages from history.
        clear_history: Clear the conversation history for the given user.
        get_conversation_history: Give the conversation history for the given user.
        process_rag_query: Process a query using RAG approach with conversation history.
    """

    def __init__(self,
                 max_history_length: int = 10,
                 history_expiry: timedelta = timedelta(hours=1),
                 error_message: str = """Elnézést, hibába ütköztem. Próbáld újra később.
                                        Ha akkor is fennáll a hiba, akkor írj a
                                        fanni.jako@mensa.hu email címre."""):
        load_env()
        set_logging()

        self.astra_client = create_astra_client()
        self.llm = create_llm_client()
        self.tokenizer = create_tokenizer()
        self.chat_histories = defaultdict(list)

        self.error_message = error_message
        self.max_history_length = max_history_length
        self.history_expiry = history_expiry

        logging.info('ChatBot initialized with the following parameters:')
        logging.info(f'max_history_length: {self.max_history_length}')
        logging.info(f'history_expiry: {self.history_expiry}')
        logging.info(f'error_message: {self.error_message}')

    def add_to_history(self, user_id: int, role: str, message: str) -> None:
        """
        Add a message to the user's chat history

        Params:
            user_id (int): The ID of the user.
            role (str): The role of the message sender.
            message (str): The message to add to the history.

        Returns:
            None
        """

        logging.info(f'Adding message to history for user {user_id}')

        self._clean_old_history(user_id)

        self.chat_histories[user_id].append((datetime.now(), role, message))

        if len(self.chat_histories[user_id]) > self.max_history_length:
            self.chat_histories[user_id].pop(0)
            logging.info(f'Popped oldest message from history for user {user_id} '
                         'due to reaching max length limit.')

    def _clean_old_history(self, user_id: int) -> None:
        """
        Remove expired messages from history

        Params:
            user_id (int): The ID of the user.

        Returns:
            None
        """

        logging.info(f'Automatically cleaning old history for user {user_id}')

        current_time = datetime.now()

        self.chat_histories[user_id] = [
            (timestamp, role, message)
            for timestamp, role, message in self.chat_histories[user_id]
            if current_time - timestamp < self.history_expiry
        ]

    def clear_history(self, user_id: int) -> None:
        """
        Clear the conversation history for the given user

        Params:
            user_id (int): The ID of the user.

        Returns:
            None
        """

        logging.info(f'Clearing history for user {user_id}')

        self.chat_histories[user_id].clear()

    def get_conversation_history(self, user_id: int) -> str:
        """
        Give the conversation history for the given user

        Params:
            user_id (int): The ID of the user.

        Returns:
            str: The formatted conversation history.
        """

        logging.info(f'Getting conversation history for user {user_id}')

        history = self.chat_histories[user_id]

        formatted_history = []
        for _, role, message in history:
            formatted_history.append(f"{role}: {message}")

        return "\n".join(formatted_history)

    async def process_rag_query(self, user_id: int, query: str) -> str:
        """
        Process a query using RAG approach with conversation history

        Params:
            user_id (int): The ID of the user.
            query (str): The query to process.

        Returns:
            str: The response from the LLM.
        """

        response = await get_llama_response(self.astra_client,
                                            self.llm,
                                            self.tokenizer,
                                            query,
                                            self.get_conversation_history(user_id))

        logging.info(f'Generated response: {response}')

        self.add_to_history(user_id, "Felhasználó", query)
        self.add_to_history(user_id, "Bot", response)

        return response
