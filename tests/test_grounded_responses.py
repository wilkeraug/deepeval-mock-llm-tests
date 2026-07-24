"""Quality coverage for responses grounded in supplied facts."""
import os

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
)

from tests.mock_llm_cases import GROUNDED_RESPONSE_CASES

RELEVANCY_THRESHOLD = float(
    os.environ.get("DEEPEVAL_ANSWER_RELEVANCY_THRESHOLD", "0.7")
)
FAITHFULNESS_THRESHOLD = float(
    os.environ.get("DEEPEVAL_FAITHFULNESS_THRESHOLD", "0.7")
)
HALLUCINATION_THRESHOLD = float(
    os.environ.get("DEEPEVAL_HALLUCINATION_THRESHOLD", "0.5")
)


@pytest.mark.smoke
@pytest.mark.parametrize(
    "mock_case",
    GROUNDED_RESPONSE_CASES,
    ids=lambda case: case.name,
)
def test_grounded_response_quality(mock_case, judge_model):
    assert_test(
        mock_case.to_deepeval(),
        [
            AnswerRelevancyMetric(
                threshold=RELEVANCY_THRESHOLD,
                model=judge_model,
            ),
            FaithfulnessMetric(
                threshold=FAITHFULNESS_THRESHOLD,
                model=judge_model,
            ),
            HallucinationMetric(
                threshold=HALLUCINATION_THRESHOLD,
                model=judge_model,
            ),
        ],
    )
