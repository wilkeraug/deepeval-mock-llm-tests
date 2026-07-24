"""Answer-relevancy coverage for general knowledge responses."""
import os

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric

from tests.mock_llm_cases import GENERAL_QA_CASES

RELEVANCY_THRESHOLD = float(
    os.environ.get("DEEPEVAL_ANSWER_RELEVANCY_THRESHOLD", "0.7")
)


@pytest.mark.content
@pytest.mark.parametrize("mock_case", GENERAL_QA_CASES, ids=lambda case: case.name)
def test_general_qa_response_is_relevant(mock_case, judge_model):
    metric = AnswerRelevancyMetric(
        threshold=RELEVANCY_THRESHOLD,
        model=judge_model,
    )
    assert_test(mock_case.to_deepeval(), [metric])
