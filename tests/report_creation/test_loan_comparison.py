"""DeepEval coverage for Loan Comparison report creation.

Complements (does not replace) the phrase-assertion Jest suite in the JS
project's tests/ReportCreation/report-creation.test.js. Where that suite
checks "did the bot say one of these known-good phrases", these tests check
semantic quality: relevance, faithfulness to the input data, and absence of
hallucination.
"""
import os

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase

from tests.conftest import send_and_get_text

CLIENT_NAME = f"DE {os.environ.get('TEST_CLIENT_NAME', 'Automation Client')}"
ADDRESS = os.environ.get("LOCATION_SCENARIO", "City, State, USA")

LC_PRICE = os.environ.get("TEST_LOAN_COMPARISON_PURCHASE_PRICE", "450000")
LC_DOWN_1 = os.environ.get("TEST_LOAN_COMPARISON_DOWN_PAYMENT_1", "90000")
LC_RATE_1 = os.environ.get("TEST_LOAN_COMPARISON_INTEREST_RATE_1", "6.5%")
LC_TERM_1 = os.environ.get("TEST_LOAN_COMPARISON_LOAN_TERM_1", "30 years")
LC_DOWN_2 = os.environ.get("TEST_LOAN_COMPARISON_DOWN_PAYMENT_2", "112500")
LC_RATE_2 = os.environ.get("TEST_LOAN_COMPARISON_INTEREST_RATE_2", "7%")
LC_TERM_2 = os.environ.get("TEST_LOAN_COMPARISON_LOAN_TERM_2", "15 years")

RELEVANCY_THRESHOLD = float(os.environ.get("DEEPEVAL_ANSWER_RELEVANCY_THRESHOLD", "0.7"))
FAITHFULNESS_THRESHOLD = float(os.environ.get("DEEPEVAL_FAITHFULNESS_THRESHOLD", "0.7"))
HALLUCINATION_THRESHOLD = float(os.environ.get("DEEPEVAL_HALLUCINATION_THRESHOLD", "0.5"))


@pytest.mark.smoke
def test_loan_comparison_report_is_relevant_and_faithful(chatbot_client):
    prompt = (
        f"Create a loan comparison report for {CLIENT_NAME} at {ADDRESS}, "
        f"purchase price {LC_PRICE}. Option 1: down payment {LC_DOWN_1}, "
        f"rate {LC_RATE_1}, term {LC_TERM_1}. Option 2: down payment {LC_DOWN_2}, "
        f"rate {LC_RATE_2}, term {LC_TERM_2}."
    )
    actual_output = send_and_get_text(chatbot_client, prompt)

    input_facts = (
        f"Client: {CLIENT_NAME}. Address: {ADDRESS}. Purchase price: {LC_PRICE}. "
        f"Option 1 — down payment {LC_DOWN_1}, rate {LC_RATE_1}, term {LC_TERM_1}. "
        f"Option 2 — down payment {LC_DOWN_2}, rate {LC_RATE_2}, term {LC_TERM_2}."
    )

    test_case = LLMTestCase(
        input=prompt,
        actual_output=actual_output,
        retrieval_context=[input_facts],
        context=[input_facts],
    )

    assert_test(
        test_case,
        [
            AnswerRelevancyMetric(threshold=RELEVANCY_THRESHOLD),
            FaithfulnessMetric(threshold=FAITHFULNESS_THRESHOLD),
            HallucinationMetric(threshold=HALLUCINATION_THRESHOLD),
        ],
    )
