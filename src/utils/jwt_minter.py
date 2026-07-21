"""JWT minting — Python port of the JS project's src/utils/jwt-minter.js."""
import os
import uuid
from datetime import timedelta

import jwt

_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def _expires_in_to_timedelta(value: str) -> timedelta:
    value = (value or "24h").strip()
    unit = value[-1]
    if unit in _UNIT_SECONDS:
        return timedelta(seconds=int(value[:-1]) * _UNIT_SECONDS[unit])
    return timedelta(seconds=int(value))


def mint_token(user_data: dict, options: dict | None = None) -> str:
    options = options or {}
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET not found in environment variables")

    if not user_data.get("mbsID") and not user_data.get("lrID"):
        raise RuntimeError("userData.mbsID or userData.lrID is required")

    session_id = options.get("sessionId") or f"DEEPEVAL_TESTS-{uuid.uuid4()}"

    payload = {
        "userData": {
            "mbsID": user_data.get("mbsID"),
            "lrID": user_data.get("lrID"),
            "name": user_data.get("name", "Test User"),
            "email": user_data.get("email", "test@example.com"),
            "nmls": user_data.get("nmls", "000000"),
        },
        "sessionId": session_id,
        "appName": options.get("appName", "test-client"),
    }

    expires_in = options.get("expiresIn") or os.environ.get("JWT_EXPIRES_IN", "24h")
    exp_delta = _expires_in_to_timedelta(expires_in)

    algorithm = os.environ.get("JWT_ALGORITHM", "HS256")

    # PyJWT adds iat/exp automatically when passed via `exp`/`iat` claims.
    import time

    now = int(time.time())
    payload["iat"] = now
    payload["exp"] = now + int(exp_delta.total_seconds())

    if os.environ.get("JWT_ISSUER"):
        payload["iss"] = os.environ["JWT_ISSUER"]
    if os.environ.get("JWT_AUDIENCE"):
        payload["aud"] = os.environ["JWT_AUDIENCE"]

    return jwt.encode(payload, secret, algorithm=algorithm)
