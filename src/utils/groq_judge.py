"""Groq judge model for DeepEval metrics, used in place of the OpenAI default.

Groq exposes an OpenAI-compatible chat completions endpoint, so this wraps
that endpoint in DeepEval's DeepEvalBaseLLM interface. Enable it by setting
GROQ_API_KEY (and optionally GROQ_MODEL) in .env, then call get_judge_model()
from a test module and pass the result as model= to each metric.
"""
import os

from deepeval.models import DeepEvalBaseLLM
from openai import OpenAI

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"


def _is_usable_api_key(value: str | None) -> bool:
    """Reject empty values and the placeholders shipped in `.env.example`."""
    if not value:
        return False
    normalized = value.strip().lower()
    return bool(normalized) and "replace-with" not in normalized


class GroqJudge(DeepEvalBaseLLM):
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.environ.get("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        api_key = os.environ.get("GROQ_API_KEY")
        if not _is_usable_api_key(api_key):
            raise RuntimeError(
                "Missing GROQ_API_KEY. Set it in your .env file to use Groq as the judge model."
            )
        self.client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    def load_model(self):
        return self.client

    def generate(self, prompt: str, schema=None) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"} if schema else None,
        )
        return response.choices[0].message.content

    async def a_generate(self, prompt: str, schema=None) -> str:
        return self.generate(prompt, schema=schema)

    def get_model_name(self) -> str:
        return f"Groq {self.model_name}"


def get_judge_model() -> GroqJudge | None:
    """Returns a GroqJudge if GROQ_API_KEY is set, else None (fall back to DeepEval's OpenAI default)."""
    if _is_usable_api_key(os.environ.get("GROQ_API_KEY")):
        return GroqJudge()
    return None


def has_judge_credentials() -> bool:
    """Return whether either supported judge has non-placeholder credentials."""
    return _is_usable_api_key(
        os.environ.get("GROQ_API_KEY")
    ) or _is_usable_api_key(os.environ.get("OPENAI_API_KEY"))
