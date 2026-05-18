from app.llm import format_prompt


def test_format_prompt_includes_context_history_and_query(fake_tokenizer):
    out = format_prompt(
        info="kontextus-szöveg",
        tokenizer=fake_tokenizer,
        prompt="Mi az autizmus?",
        chat_history="Felhasználó: szia\nBot: szia",
    )

    fake_tokenizer.apply_chat_template.assert_called_once()
    (chat,), kwargs = fake_tokenizer.apply_chat_template.call_args
    assert kwargs == {"tokenize": False, "add_generation_prompt": True}

    assert [m["role"] for m in chat] == ["system", "user"]
    user_content = chat[1]["content"]
    assert "kontextus-szöveg" in user_content
    assert "Felhasználó: szia" in user_content
    assert "Mi az autizmus?" in user_content

    assert "kontextus-szöveg" in out
    assert "Mi az autizmus?" in out


def test_format_prompt_defaults_empty_chat_history(fake_tokenizer):
    format_prompt(info="ctx", tokenizer=fake_tokenizer, prompt="q")
    (chat,), _ = fake_tokenizer.apply_chat_template.call_args
    assert "Korábbi beszélgetések:" in chat[1]["content"]
