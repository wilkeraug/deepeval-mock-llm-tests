"""Environment resolution — Python port of the JS project's src/utils/env-config.js.

Keeps the same CURRENT_ENV semantics so this project targets the identical
servers/users as the Jest chatbot-test-project.
"""
import os

ENV_ALIAS = {
    "test": "test",
    "stage": "staging",
    "staging": "staging",
    "prod": "prod",
    "production": "prod",
    "local": "local",
}

SERVER_VAR_BY_ENV = {
    "local": "LOCAL_SERVER",
    "test": "TEST_SERVER",
    "staging": "STAGE_SERVER",
    "prod": "PROD_SERVER",
}

USER_PREFIX_BY_ENV = {
    "local": "TEST",
    "test": "TEST",
    "staging": "STAGE",
    "prod": "PROD",
}


def normalize_current_env() -> str:
    raw_env = os.environ.get("CURRENT_ENV", "").strip().lower()
    normalized = ENV_ALIAS.get(raw_env)
    if not normalized:
        raise RuntimeError(
            f'Unsupported CURRENT_ENV value "{os.environ.get("CURRENT_ENV", "")}". '
            "Use one of: local, test, stage, staging, prod, production."
        )
    return normalized


def get_server_url() -> str:
    normalized = normalize_current_env()
    env_server_var = SERVER_VAR_BY_ENV[normalized]
    server_url = os.environ.get("SERVER_URL") or os.environ.get(env_server_var)
    if not server_url:
        raise RuntimeError(
            f'Missing server URL for CURRENT_ENV="{os.environ.get("CURRENT_ENV")}". '
            f"Set {env_server_var} or override with SERVER_URL in your .env file."
        )
    return server_url


def get_resolved_test_user_config() -> dict:
    normalized = normalize_current_env()
    prefix = USER_PREFIX_BY_ENV[normalized]

    required_vars = [f"{prefix}_USER_ID", f"{prefix}_USER_NAME", f"{prefix}_USER_EMAIL"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        raise RuntimeError(
            f'Missing required environment variables for CURRENT_ENV="{os.environ.get("CURRENT_ENV")}": '
            f"{', '.join(missing)}"
        )

    return {
        "mbsID": os.environ.get(f"{prefix}_USER_ID"),
        "lrID": os.environ.get(f"{prefix}_USER_LR_ID"),
        "name": os.environ.get(f"{prefix}_USER_NAME"),
        "email": os.environ.get(f"{prefix}_USER_EMAIL"),
        "nmls": os.environ.get(f"{prefix}_USER_NMLS", "000000"),
        "appName": os.environ.get(f"{prefix}_APP_NAME", "mbs-bot"),
    }
