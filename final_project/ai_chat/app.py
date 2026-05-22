from final_project.ai_chat.chat.context_limiter import ContextLimiter
from final_project.ai_chat.chat.history import ChatHistory
from final_project.ai_chat.chat.service import ChatService
from final_project.ai_chat.config.loader import load_config
from final_project.ai_chat.console.cli import ConsoleChatApp
from final_project.ai_chat.llm.openai_client import OpenAICompatibleClient


def create_app() -> ConsoleChatApp:
    config = load_config()
    client = OpenAICompatibleClient(
        api_key=config.api_key,
        base_url=config.api_host,
        model=config.model,
        temperature=config.temperature,
    )
    history = ChatHistory(system_prompt=config.system_prompt)
    limiter = ContextLimiter(
        limit_messages=config.limit_messages,
        limit_chars=config.limit_chars,
    )
    service = ChatService(client=client, history=history, limiter=limiter)
    return ConsoleChatApp(chat_service=service, streaming=config.streaming)
