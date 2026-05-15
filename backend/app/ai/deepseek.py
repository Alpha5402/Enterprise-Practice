"""DeepSeek chat model integration through LangChain."""

from langchain_deepseek import ChatDeepSeek

from app.core.config import Settings, settings
from app.rag.exceptions import RagConfigurationError


def create_deepseek_chat_model(app_settings: Settings = settings) -> ChatDeepSeek:
    """Create the configured DeepSeek chat model via LangChain."""
    if not app_settings.deepseek_api_key:
        raise RagConfigurationError("DEEPSEEK_API_KEY is required for DeepSeek model calls")
    return ChatDeepSeek(
        model=app_settings.deepseek_model,
        api_key=app_settings.deepseek_api_key,
        base_url=app_settings.deepseek_base_url,
    )
