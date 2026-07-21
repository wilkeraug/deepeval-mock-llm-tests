import os
import sys

import pytest
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.chatbot_client import ChatbotSocketIOClient, get_socket_config  # noqa: E402

load_dotenv()


@pytest.fixture
def chatbot_config():
    return get_socket_config()


@pytest.fixture
def chatbot_client(chatbot_config):
    client = ChatbotSocketIOClient(
        chatbot_config["server_url"],
        chatbot_config["jwt"],
        path=chatbot_config["socket_path"],
    )
    client.connect()
    # Fresh, isolated session per test — same as beforeEach resetSession() in the JS suite.
    client.reset_session(chatbot_config["mint_token"]())

    yield client

    if client.is_connected():
        client.disconnect()


def send_and_get_text(client: "ChatbotSocketIOClient", message_text: str, timeout: float = 30.0) -> str:
    """Send a chat message and return the bot's full response text.

    Mirrors the sendAndGetText() helper pattern used across the JS test suite.
    """
    client.send_message({"type": "chat", "text": message_text})
    response = client.get_full_response(timeout=timeout)
    return response.get("data", {}).get("text", "") if isinstance(response.get("data"), dict) else str(response.get("data", ""))
