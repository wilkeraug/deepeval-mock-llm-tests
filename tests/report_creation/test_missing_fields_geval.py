"""GEval rubric test — mirrors the LC_MANDATORY_FIELD_PHRASES checks in the JS
suite, but judges intent ("did the bot ask for the missing field") instead of
matching a fixed phrase list. Useful when acceptable phrasings are too varied
to enumerate.
"""
import os

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from tests.conftest import send_and_get_text

CLIENT_NAME = f"DE {os.environ.get('TEST_CLIENT_NAME', 'Automation Client')}"


def _asks_for_missing_field_metric() -> GEval:
    # Constructed lazily (per-test) rather than at module import time, since
    # GEval eagerly initializes its judge model and requires OPENAI_API_KEY
    # to even be *collected* by pytest otherwise.
    return GEval(
        name="AsksForMissingMandatoryField",
        criteria=(
            "Determine whether the AI response asks the user for the property price, "
            "since the input request for a loan comparison report omitted it. "
            "The response should not attempt to create the report without this field."
        ),
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        threshold=0.7,
    )


@pytest.mark.coreflow
def test_bot_asks_for_missing_property_price(chatbot_client):
    prompt = (
        f"Create a loan comparison report for {CLIENT_NAME}, "
        "down payment 90000, rate 6.5%, term 30 years."
    )
    actual_output = send_and_get_text(chatbot_client, prompt)

    test_case = LLMTestCase(input=prompt, actual_output=actual_output)

    assert_test(test_case, [_asks_for_missing_field_metric()])
