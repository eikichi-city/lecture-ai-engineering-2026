from types import SimpleNamespace
from unittest.mock import Mock

from app import ask as ask_module


def _stub_client(monkeypatch, response):
    client = Mock()
    client.models.generate_content.return_value = response
    monkeypatch.setattr(ask_module.genai, "Client", Mock(return_value=client))
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-api-key")


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        text="answer",
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=5),
    )
    _stub_client(monkeypatch, response)

    assert ask_module.ask("question") == "answer"
    assert capsys.readouterr().out == "[usage] 入力トークン数: 12 / 出力トークン数: 5\n"


def test_ask_reports_unavailable_token_counts(monkeypatch, capsys):
    _stub_client(monkeypatch, SimpleNamespace(text="answer", usage_metadata=None))

    assert ask_module.ask("question") == "answer"
    assert capsys.readouterr().out == "[usage] 入力トークン数: 不明 / 出力トークン数: 不明\n"
