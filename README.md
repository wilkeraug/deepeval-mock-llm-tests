# Chatbot DeepEval Project

DeepEval-based evaluation suite for the same Miles chatbot backend used by the
sibling `AI Chatbot - MOD POD` Jest project. This project targets the
**identical servers, JWT auth, and test users** (ported from that project's
`src/utils/env-config.js` / `jwt-minter.js` / `chatbot-client.js`), but asserts
with LLM-judge metrics (relevance, faithfulness, hallucination, custom G-Eval
rubrics) instead of phrase matching.

This complements, it does not replace, the Jest phrase-assertion suite —
see that project's `tests/*/00_README.md` for the deterministic checks that
should stay as-is (report URL presence, exact mandatory-field prompts,
guardrail refusals).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in JWT_SECRET, server URLs, test user IDs (same values as the JS
# project's .env), and OPENAI_API_KEY for the judge model
```

## Judge model

DeepEval's built-in metrics (`AnswerRelevancyMetric`, `FaithfulnessMetric`,
`HallucinationMetric`, `GEval`) default to calling `gpt-4o` via the OpenAI API
as the judge. Set `OPENAI_API_KEY` in `.env` to use that default.

To use an Anthropic model as the judge instead, configure a DeepEval custom
model wrapper (see https://deepeval.com/docs/metrics-introduction#using-a-custom-llm)
and pass `model=<your_wrapper>` to each metric instead of relying on the
default.

## Running tests

```bash
pytest                                  # full suite
pytest -m smoke                         # smoke tests only
pytest tests/report_creation/           # one domain
deepeval test run tests/report_creation/test_loan_comparison.py  # DeepEval CLI runner (nicer diff output)
```

## Project layout

```
src/utils/
  env_config.py      # CURRENT_ENV / server URL / test user resolution (port of env-config.js)
  jwt_minter.py       # JWT minting for socket auth (port of jwt-minter.js)
  chatbot_client.py   # Socket.IO client + getSocketConfig() (port of chatbot-client.js)
tests/
  conftest.py         # pytest fixtures: chatbot_client (connect + resetSession per test)
  report_creation/     # DeepEval coverage mirroring tests/ReportCreation/ in the JS project
  help_center/         # Open-ended Q&A coverage where phrase arrays don't fit well
```

## Metrics included

| Metric | Use |
|---|---|
| `AnswerRelevancyMetric` | Response actually addresses the user's request |
| `FaithfulnessMetric` | Response doesn't contradict the input data given (loan terms, prices) |
| `HallucinationMetric` | Response doesn't invent facts not present in context |
| `GEval` (custom) | Rubric-based checks mirroring specific Miles-spec behaviors (e.g. "asks for missing mandatory field") |

Thresholds are configured via env vars in `.env` (`DEEPEVAL_*_THRESHOLD`) so
they can be tuned per environment without code changes.

## Adding a new test

1. Pick the matching folder under `tests/` (or create one, following the
   naming used in the JS project's `tests/<Domain>/` folders).
2. Use the `chatbot_client` fixture — it connects and resets session per test,
   same guarantee as `beforeEach(() => client.resetSession(...))` in Jest.
3. Use `send_and_get_text(client, prompt)` from `tests/conftest.py` to get the
   bot's reply text.
4. Build an `LLMTestCase` and pick metrics: prebuilt ones for general
   quality, `GEval` for a specific Miles-spec behavioral rule.
