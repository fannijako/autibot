from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.chatbot import ChatBot


@pytest.fixture(name="chatbot")
def chatbot_fixture(fake_astra_client, fake_llm, fake_tokenizer):
    """A ChatBot wired to fully-mocked external services."""
    with patch("app.chatbot.create_astra_client", return_value=fake_astra_client), \
         patch("app.chatbot.create_llm_client", return_value=fake_llm), \
         patch("app.chatbot.create_tokenizer", return_value=fake_tokenizer), \
         patch("app.chatbot.load_env"), \
         patch("app.chatbot.set_logging"):
        bot = ChatBot(max_history_length=3, history_expiry=timedelta(hours=1))
    return bot


def test_add_to_history_appends(chatbot):
    chatbot.add_to_history(1, "Felhasználó", "szia")
    assert len(chatbot.chat_histories[1]) == 1
    _, role, message = chatbot.chat_histories[1][0]
    assert role == "Felhasználó"
    assert message == "szia"


def test_add_to_history_trims_to_max_length(chatbot):
    for i in range(5):
        chatbot.add_to_history(1, "Felhasználó", f"msg-{i}")

    assert len(chatbot.chat_histories[1]) == 3
    messages = [m for _, _, m in chatbot.chat_histories[1]]
    assert messages == ["msg-2", "msg-3", "msg-4"]


def test_add_to_history_drops_expired_entries(chatbot):
    """Expired entries are dropped via the public API (add_to_history calls cleanup)."""
    now = datetime.now()
    chatbot.chat_histories[1] = [
        (now - timedelta(hours=2), "Felhasználó", "régi"),
        (now - timedelta(minutes=10), "Bot", "friss"),
    ]
    chatbot.add_to_history(1, "Felhasználó", "új")

    messages = [m for _, _, m in chatbot.chat_histories[1]]
    assert messages == ["friss", "új"]


def test_clear_history_empties(chatbot):
    chatbot.add_to_history(1, "Felhasználó", "szia")
    chatbot.clear_history(1)
    assert chatbot.chat_histories[1] == []


def test_get_conversation_history_formats_roles_and_messages(chatbot):
    chatbot.add_to_history(1, "Felhasználó", "kérdés")
    chatbot.add_to_history(1, "Bot", "válasz")
    formatted = chatbot.get_conversation_history(1)
    assert formatted == "Felhasználó: kérdés\nBot: válasz"


def test_get_conversation_history_empty_user(chatbot):
    assert chatbot.get_conversation_history(999) == ""


async def test_process_rag_query_end_to_end(chatbot):
    """End-to-end RAG flow with all external services mocked.

    Verifies: retrieval is called, the LLM response is returned to the caller,
    and both the user query and the bot answer are appended to history.
    """
    with patch(
        "app.llm.get_information_to_query",
        return_value=[{"$similarity": 0.9, "$vectorize": "releváns dokumentum"}],
    ) as mock_retrieve:
        response = await chatbot.process_rag_query(42, "Mi az autizmus?")

    mock_retrieve.assert_called_once()
    assert response == "Ez egy mock válasz."

    messages = [(role, msg) for _, role, msg in chatbot.chat_histories[42]]
    assert messages == [
        ("Felhasználó", "Mi az autizmus?"),
        ("Bot", "Ez egy mock válasz."),
    ]
