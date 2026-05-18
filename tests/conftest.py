import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def fake_astra_client():
    """A MagicMock standing in for an astrapy DataAPIClient."""
    return MagicMock(name="DataAPIClient")


@pytest.fixture
def fake_llm():
    """A MagicMock LLM whose .invoke() returns a deterministic string."""
    llm = MagicMock(name="HuggingFaceEndpoint")
    llm.invoke.return_value = "Ez egy mock válasz."
    return llm


@pytest.fixture
def fake_tokenizer():
    """A MagicMock tokenizer that echoes the chat list back as a string."""
    tokenizer = MagicMock(name="AutoTokenizer")
    tokenizer.apply_chat_template.side_effect = lambda chat, **_: "\n".join(
        f"{m['role']}: {m['content']}" for m in chat
    )
    return tokenizer
