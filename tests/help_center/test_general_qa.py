"""DeepEval coverage for open-ended HelpCenter-style questions, where
acceptable phrasing varies too much for a fixed phrase array.
"""
import os

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric

from tests.conftest import send_and_get_text
from deepeval.test_case import LLMTestCase

RELEVANCY_THRESHOLD = float(os.environ.get("DEEPEVAL_ANSWER_RELEVANCY_THRESHOLD", "0.7"))


@pytest.mark.content
def test_bot_explains_what_a_loan_comparison_report_is(chatbot_client):
    prompt = "What is a loan comparison report and when would I use one?"
    actual_output = send_and_get_text(chatbot_client, prompt)

    test_case = LLMTestCase(input=prompt, actual_output=actual_output)

    assert_test(test_case, [AnswerRelevancyMetric(threshold=RELEVANCY_THRESHOLD)])
