import pytest
from dotenv import load_dotenv

from src.utils.groq_judge import get_judge_model, has_judge_credentials

load_dotenv()


@pytest.fixture(scope="session")
def judge_model():
    """Select the configured metric judge or skip API-backed evaluations."""
    if not has_judge_credentials():
        pytest.skip(
            "Set OPENAI_API_KEY or GROQ_API_KEY to run DeepEval judge metrics."
        )
    return get_judge_model()
