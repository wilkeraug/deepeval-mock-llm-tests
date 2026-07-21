"""Socket.IO client for the Miles chatbot — Python port of
src/utils/chatbot-client.js, kept close to the original so both projects talk
to the server the same way.
"""
import os
import time

import socketio

from .env_config import get_resolved_test_user_config, get_server_url, normalize_current_env
from .jwt_minter import mint_token


class ChatbotSocketIOClient:
    def __init__(self, origin: str, auth_token: str, **options):
        self.origin = origin
        self.auth_token = auth_token
        self.path = options.get("path", "/socket.io")
        self.connect_timeout = options.get("connect_timeout_s", 10)
        self.sio = socketio.Client(reconnection=False)
        self._last_message = None
        self._messages = []

        @self.sio.on("message")
        def _on_message(data):
            self._last_message = data
            self._messages.append(data)

    def connect(self):
        self.sio.connect(
            self.origin,
            auth={"token": self.auth_token},
            socketio_path=self.path.strip("/") and f"/{self.path.strip('/')}" or "/socket.io",
            transports=["websocket", "polling"],
            wait_timeout=self.connect_timeout,
        )

    def send_message(self, message: dict) -> dict:
        ack_result = {}

        def _ack(response):
            ack_result["value"] = response

        self.sio.emit("message", message, callback=_ack)
        return ack_result

    def get_full_response(self, response_type: str = "ai_chat_response", timeout: float = 30.0) -> dict:
        self._messages = []
        start = time.time()
        while time.time() - start < timeout:
            for msg in self._messages:
                if msg.get("type") == response_type:
                    return msg
            self.sio.sleep(0.1)
        raise TimeoutError(f'Timeout waiting for message type "{response_type}"')

    def reset_session(self, new_auth_token: str):
        self.auth_token = new_auth_token
        self.sio.disconnect()
        self.connect()

    def disconnect(self):
        if self.sio.connected:
            self.sio.disconnect()

    def is_connected(self) -> bool:
        return self.sio.connected


def get_socket_config() -> dict:
    """Python port of getSocketConfig() from chatbot-client.js."""
    required_vars = ["CURRENT_ENV", "JWT_SECRET", "JWT_ALGORITHM", "JWT_EXPIRES_IN"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Please ensure these variables are defined in your .env file."
        )

    normalized_env = normalize_current_env()
    server_url = get_server_url()
    user_config = get_resolved_test_user_config()
    user_data = {
        "mbsID": user_config["mbsID"],
        "lrID": user_config["lrID"],
        "name": user_config["name"],
        "email": user_config["email"],
        "nmls": user_config["nmls"],
    }
    app_name = user_config["appName"]
    token = mint_token(user_data, {"appName": app_name})

    def mint(**overrides):
        return mint_token(user_data, {"appName": app_name, **overrides})

    return {
        "env": normalized_env,
        "server_url": server_url,
        "jwt": token,
        "socket_path": os.environ.get("SOCKET_IO_PATH", "/hwapp/hwy-ai-server/socket/"),
        "test_timeout": 60,
        "mint_token": mint,
    }
