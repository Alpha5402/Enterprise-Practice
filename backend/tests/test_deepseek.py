"""DeepSeek LangChain integration tests."""

import pytest

from app.ai.deepseek import create_deepseek_chat_model
from app.core.config import Settings
from app.rag.exceptions import RagConfigurationError


def test_deepseek_chat_model_requires_api_key() -> None:
    """DeepSeek LangChain model creation fails clearly without credentials."""
    with pytest.raises(RagConfigurationError):
        create_deepseek_chat_model(Settings(deepseek_api_key=""))


def test_deepseek_chat_model_uses_configured_model() -> None:
    """DeepSeek LangChain model uses configured model name."""
    model = create_deepseek_chat_model(
        Settings(
            deepseek_api_key="test-key",
            deepseek_model="deepseek-chat",
            deepseek_base_url="https://api.deepseek.com",
        )
    )

    assert model.model_name == "deepseek-chat"

