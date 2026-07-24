"""G-Eval coverage for safety, privacy, and responsible refusals."""
import os

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams

from tests.mock_llm_cases import SAFETY_GUARDRAIL_CASES

GEVAL_THRESHOLD = float(os.environ.get("DEEPEVAL_GEVAL_THRESHOLD", "0.7"))


@pytest.mark.guardrail
@pytest.mark.parametrize(
    "mock_case",
    SAFETY_GUARDRAIL_CASES,
    ids=lambda case: case.name,
)
def test_safety_guardrail(mock_case, judge_model):
    metric = GEval(
        name=f"SafetyGuardrail_{mock_case.name}",
        criteria=mock_case.criteria,
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],
        threshold=GEVAL_THRESHOLD,
        model=judge_model,
    )
    assert_test(mock_case.to_deepeval(), [metric])
