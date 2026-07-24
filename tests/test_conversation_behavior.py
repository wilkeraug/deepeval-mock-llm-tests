"""G-Eval coverage for conversational behavior and instruction following."""
import os

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams

from tests.mock_llm_cases import CONVERSATION_BEHAVIOR_CASES

GEVAL_THRESHOLD = float(os.environ.get("DEEPEVAL_GEVAL_THRESHOLD", "0.7"))


@pytest.mark.coreflow
@pytest.mark.parametrize(
    "mock_case",
    CONVERSATION_BEHAVIOR_CASES,
    ids=lambda case: case.name,
)
def test_conversation_behavior(mock_case, judge_model):
    metric = GEval(
        name=f"ConversationBehavior_{mock_case.name}",
        criteria=mock_case.criteria,
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],
        threshold=GEVAL_THRESHOLD,
        model=judge_model,
    )
    assert_test(mock_case.to_deepeval(), [metric])
