from unittest.mock import MagicMock, patch

import pytest

from utils.gemini_client import generate_text


def test_generate_text_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        generate_text("こんにちは")


def test_generate_text_returns_response_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    mock_response = MagicMock()
    mock_response.text = "生成されたテキスト"

    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response

    with patch(
        "utils.gemini_client.genai.Client", return_value=mock_client_instance
    ) as mock_client_cls:
        result = generate_text("プロンプト")

    mock_client_cls.assert_called_once_with(api_key="dummy-key")
    mock_client_instance.models.generate_content.assert_called_once_with(
        model="gemini-2.5-flash",
        contents="プロンプト",
    )
    assert result == "生成されたテキスト"


def test_generate_text_raises_when_response_text_is_none(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    mock_response = MagicMock()
    mock_response.text = None

    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response

    with patch(
        "utils.gemini_client.genai.Client", return_value=mock_client_instance
    ):
        with pytest.raises(RuntimeError, match="生成結果が空でした"):
            generate_text("プロンプト")
