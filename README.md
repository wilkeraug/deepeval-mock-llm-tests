# Beginner's Guide to the Mock LLM DeepEval Project

This project shows how to evaluate AI responses with
[DeepEval](https://deepeval.com/) and pytest.

It contains 26 example conversations covering general knowledge, grounded
answers, instruction following, privacy, and safety. The conversations are
mocked: their inputs and responses are written directly in Python instead of
coming from a real chatbot.

The mocked responses are scored by a live LLM judge from Groq or OpenAI.

## The most important idea

There are two different AI roles to understand:

1. **Response being tested:** A fixed string stored in
   `tests/mock_llm_cases.py`. No chatbot generates this during the test.
2. **Judge:** A live Groq or OpenAI model that reads the fixed response and
   scores its quality.

```text
Mock user message + mock AI response
                 |
                 v
          DeepEval metric
                 |
                 v
        Groq or OpenAI judge
                 |
                 v
        Score compared with threshold
                 |
                 v
             Pass or fail
```

This project therefore tests the evaluation setup and the quality of the
example responses. It does **not** prove that a real chatbot would generate
those responses.

## Why mock the responses?

Mock cases are useful because they are:

- repeatable: the response under test does not change between runs;
- fast to prepare: no chatbot server or authentication is required;
- focused: each example demonstrates one behavior or metric;
- safe for development: tests do not create real accounts or modify external
  data; and
- easy to debug: the exact input, response, facts, and rubric are visible in
  one file.

The LLM judge is still probabilistic, so its score or explanation may vary
slightly. Running metrics also uses provider quota and requires internet
access.

## Glossary

| Term | Plain-language meaning |
|---|---|
| Mock case | A user message and AI response written directly in the test data |
| `input` | The simulated user's message |
| `actual_output` | The fixed AI response being evaluated |
| Context | Authoritative facts the response is allowed to use |
| Metric | A quality check, such as relevance or faithfulness |
| Judge | The live LLM that applies a metric |
| Threshold | The minimum or maximum score required to pass |
| Rubric | Written instructions describing the expected behavior |
| Marker | A pytest label used to run a category of tests |
| Parameterization | Running one test function once for every case in a collection |

## What the project currently tests

The suite has 26 independently reported cases:

| Category | Cases | Pytest marker | Evaluation |
|---|---:|---|---|
| General knowledge and technology | 10 | `content` | Answer relevancy |
| Answers grounded in supplied facts | 5 | `smoke` | Relevancy, faithfulness, and hallucination |
| Conversation and instruction following | 5 | `coreflow` | Custom G-Eval rubric |
| Safety, privacy, and responsible refusals | 6 | `guardrail` | Custom G-Eval rubric |

Examples include:

- explaining photosynthesis, version control, backups, and API limits;
- summarizing schedules, release notes, support plans, and inventory;
- calculating an order total from supplied facts;
- asking for a missing time zone;
- following an exactly-two-sentence instruction;
- using corrected information from a conversation;
- admitting that live inventory is unavailable;
- refusing discriminatory hiring or expense fraud;
- protecting passwords, system prompts, and API keys; and
- avoiding definitive individualized legal advice.

## What you need

- Python 3.14.x (tested with Python 3.14.3). Other Python versions may work, but they are not currently verified for this project.
- Internet access when running judge-backed metrics
- One judge API key:
  - Groq is recommended for this example project; or
  - OpenAI can be used instead.

You do **not** need:

- a deployed chatbot;
- a chatbot user account;
- JWT credentials;
- server URLs; or
- a Confident AI account for local testing.

## Quick start with Groq

### 1. Create and activate a virtual environment

Run these commands from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

The shell normally shows `(.venv)` after activation.

### 2. Install the dependencies

```bash
python -m pip install -r requirements.txt
```

The dependencies are:

- `deepeval`: provides LLM evaluation cases and metrics;
- `pytest`: discovers and runs the tests;
- `python-dotenv`: loads settings from `.env`; and
- `openai`: calls OpenAI-compatible APIs, including Groq.

### 3. Create your local configuration

```bash
cp .env.example .env
```

`.env` is ignored by Git. Never commit it or paste its secrets into a chat,
issue, README, test, or terminal transcript.

### 4. Create a Groq API key

Create a key in the [Groq API Keys console](https://console.groq.com/keys).
Then edit `.env`:

```dotenv
OPENAI_API_KEY=

GROQ_API_KEY=your-real-groq-key
GROQ_MODEL=openai/gpt-oss-120b
```

Do not include quotes around the key unless the key itself requires them.
Do not paste a real key into this README.

The project uses `openai/gpt-oss-120b` when `GROQ_MODEL` is omitted. Groq is
called through its OpenAI-compatible endpoint by
`src/utils/groq_judge.py`.

### 5. Confirm that pytest can find the cases

This command lists cases without calling the LLM judge:

```bash
pytest --collect-only -q
```

Expected result:

```text
26 tests collected
```

### 6. Run one inexpensive example first

```bash
pytest 'tests/test_general_qa.py::test_general_qa_response_is_relevant[explains-photosynthesis]' -q
```

The quotes are important in `zsh` because square brackets otherwise have a
special meaning.

### 7. Run the complete suite

```bash
pytest -q
```

A successful run resembles:

```text
26 passed
```

The complete run makes many judge calls and may take several minutes.

## Use OpenAI instead of Groq

Edit `.env`:

```dotenv
OPENAI_API_KEY=your-real-openai-key

GROQ_API_KEY=
```

When `GROQ_API_KEY` has a real value, the project selects Groq. When Groq is
empty and `OPENAI_API_KEY` is configured, DeepEval uses its default OpenAI
judge.

When neither key is available, the tests are collected but skipped:

```text
26 skipped
```

Skipping avoids accidental authentication attempts with empty or example
credentials.

## How a test works, step by step

When you run pytest, the following happens:

1. `pytest.ini` tells pytest to search the `tests/` directory.
2. `tests/conftest.py` loads `.env`.
3. The `judge_model` fixture checks for a usable Groq or OpenAI key.
4. A test module imports a collection from `tests/mock_llm_cases.py`.
5. `pytest.mark.parametrize` creates one pytest test for each case in that
   collection.
6. `to_deepeval()` converts the mock data into a fresh DeepEval
   `LLMTestCase`.
7. The test constructs one or more DeepEval metrics.
8. `deepeval.assert_test` sends metric prompts to the configured judge.
9. DeepEval compares each score with its threshold.
10. Pytest reports the case as passed or failed.

For example, this decorator:

```python
@pytest.mark.parametrize(
    "mock_case",
    CONVERSATION_BEHAVIOR_CASES,
    ids=lambda case: case.name,
)
```

makes the same test function run once for every conversation case. The
`name` field becomes the readable text inside square brackets in pytest
output.

## Understanding the two case types

### `MockLLMCase`

Use `MockLLMCase` for built-in quality metrics:

```python
MockLLMCase(
    name="explains-version-control",
    input="What problem does version control solve?",
    actual_output="Version control records changes to files over time...",
)
```

Fields:

- `name`: short, unique ID used in pytest output;
- `input`: simulated user message;
- `actual_output`: response being evaluated;
- `context`: optional authoritative facts for hallucination checks; and
- `retrieval_context`: optional retrieved facts for faithfulness checks.

### `MockGEvalCase`

Use `MockGEvalCase` when the expected behavior needs a written rubric:

```python
MockGEvalCase(
    name="asks-for-missing-timezone",
    input="Schedule a call at 3 PM next Thursday.",
    actual_output="Which time zone should I use for 3 PM?",
    criteria=(
        "The response must ask for the missing time zone and must not claim "
        "that the call was already scheduled."
    ),
)
```

The `criteria` field tells the judge exactly what behavior should pass.

## Metrics used by this project

### Answer relevancy

Checks whether the response addresses the user's request.

Used by:

- `tests/test_general_qa.py`
- `tests/test_grounded_responses.py`

### Faithfulness

Checks whether claims in the response are supported by
`retrieval_context`.

Used by:

- `tests/test_grounded_responses.py`

### Hallucination

Checks whether the response introduces information that is unsupported by
`context`.

Used by:

- `tests/test_grounded_responses.py`

### G-Eval

Uses a custom natural-language rubric to evaluate behavior that is difficult
to express with a built-in metric.

Used by:

- `tests/test_conversation_behavior.py`
- `tests/test_safety_guardrails.py`

## Thresholds

Thresholds are configured in `.env`:

```dotenv
DEEPEVAL_ANSWER_RELEVANCY_THRESHOLD=0.7
DEEPEVAL_FAITHFULNESS_THRESHOLD=0.7
DEEPEVAL_HALLUCINATION_THRESHOLD=0.5
DEEPEVAL_GEVAL_THRESHOLD=0.7
```

How to read them:

- Answer relevancy passes at `0.7` or higher.
- Faithfulness passes at `0.7` or higher.
- G-Eval passes at `0.7` or higher.
- Hallucination passes at `0.5` or lower because lower hallucination is
  better.

Do not lower a threshold simply to hide a bad response. First inspect the
input, output, grounding facts, score, and judge explanation. Change a
threshold only when the team's quality policy requires it.

## Commands you will use most often

Activate the environment before running commands:

```bash
source .venv/bin/activate
```

### List every case without using API quota

```bash
pytest --collect-only -q
```

### Run the complete suite

```bash
pytest -q
```

### Run one test file

```bash
pytest tests/test_safety_guardrails.py -q
```

### Run one category by marker

```bash
pytest -m content -q
pytest -m smoke -q
pytest -m coreflow -q
pytest -m guardrail -q
```

### Run one specific `MockLLMCase`

```bash
pytest 'tests/test_general_qa.py::test_general_qa_response_is_relevant[explains-api-rate-limits]' -q
```

### Run one specific `MockGEvalCase`

```bash
pytest 'tests/test_conversation_behavior.py::test_conversation_behavior[asks-for-missing-timezone]' -q
```

Another example:

```bash
pytest 'tests/test_safety_guardrails.py::test_safety_guardrail[protects-sensitive-credentials]' -q
```

Use this command to discover the exact node IDs you can copy:

```bash
pytest --collect-only -q
```

### Run through the DeepEval CLI

Complete suite:

```bash
deepeval test run tests
```

One file:

```bash
deepeval test run tests/test_grounded_responses.py
```

One marker:

```bash
deepeval test run tests -m smoke
```

Useful options:

```bash
deepeval test run tests -v         # verbose output
deepeval test run tests -d failing # display failing cases
deepeval test run tests -c         # reuse cached metric results when possible
```

For one exact parameterized case, use the pytest node-ID commands shown
above.

## Local testing versus Confident AI

Confident AI is an optional dashboard for storing and viewing DeepEval test
runs. It is not the judge and is not needed for local tests.

There are separate credentials:

| Credential | Purpose | Required locally? |
|---|---|---|
| `GROQ_API_KEY` or `OPENAI_API_KEY` | Runs the LLM judge | Yes |
| Confident AI project key | Uploads results to the dashboard | No |

### Local tests only

If you only need local tests, ignore Confident AI:

```bash
deepeval logout
pytest -q
```

Or use:

```bash
deepeval test run tests
```

Avoid `deepeval view` for local-only work. That command starts the optional
Confident AI upload flow.

### Upload results to Confident AI

If you want the dashboard:

```bash
deepeval logout
deepeval login
```

Let `deepeval login` open the browser. Select the correct organization and
project. Then run:

```bash
deepeval test run tests
deepeval view
```

The CLI normally saves the dashboard login in `.env.local`. This file is
ignored by Git.

## Add a general knowledge case

Add the case inside `GENERAL_QA_CASES` in `tests/mock_llm_cases.py`:

```python
MockLLMCase(
    name="explains-cache",
    input="What is a software cache?",
    actual_output=(
        "A cache stores reusable data closer to where it is needed so future "
        "requests can be completed more quickly."
    ),
),
```

You do not need to add another test function. The parameterized test in
`tests/test_general_qa.py` automatically runs every item in
`GENERAL_QA_CASES`.

## Add a grounded case

Use the same facts in `context` and `retrieval_context` when you want all
three grounded metrics to evaluate the case:

```python
MockLLMCase(
    name="summarizes-office-hours",
    input="When is the support desk open?",
    actual_output="The support desk is open Monday-Friday from 09:00 to 17:00 UTC.",
    context=(
        "Support desk hours: Monday-Friday, 09:00-17:00 UTC.",
    ),
    retrieval_context=(
        "Support desk hours: Monday-Friday, 09:00-17:00 UTC.",
    ),
),
```

Add it inside `GROUNDED_RESPONSE_CASES`. The test in
`tests/test_grounded_responses.py` will automatically evaluate it.

Keep the response strictly supported by the supplied facts. Even a reasonable
extra detail can correctly fail a hallucination or faithfulness metric.

## Add a behavior or safety case

Add a `MockGEvalCase` to either `CONVERSATION_BEHAVIOR_CASES` or
`SAFETY_GUARDRAIL_CASES`:

```python
MockGEvalCase(
    name="asks-for-missing-language",
    input="Translate this text for me.",
    actual_output="Which language should I translate it into, and what text should I use?",
    criteria=(
        "The response must ask for both the missing text and target language. "
        "It must not pretend that a translation was completed."
    ),
),
```

Write criteria that are:

- specific about required behavior;
- explicit about prohibited behavior;
- based only on the available input and output; and
- clear enough that two human reviewers would interpret them similarly.

## Project structure

All tests are directly inside the flat `tests/` directory:

```text
.
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
├── README.md
├── src/
│   └── utils/
│       ├── __init__.py
│       └── groq_judge.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── mock_llm_cases.py
    ├── test_conversation_behavior.py
    ├── test_general_qa.py
    ├── test_grounded_responses.py
    └── test_safety_guardrails.py
```

### File responsibilities

| File | Responsibility |
|---|---|
| `.env.example` | Safe configuration template with no real secrets |
| `.gitignore` | Prevents local secrets, caches, and environments from being committed |
| `pytest.ini` | Defines test discovery and category markers |
| `requirements.txt` | Lists Python dependencies |
| `src/utils/groq_judge.py` | Adapts Groq's OpenAI-compatible API to DeepEval |
| `tests/conftest.py` | Loads `.env` and provides the shared judge fixture |
| `tests/mock_llm_cases.py` | Stores all mock inputs, outputs, facts, and rubrics |
| `tests/test_general_qa.py` | Runs answer relevancy on general cases |
| `tests/test_grounded_responses.py` | Runs relevance, faithfulness, and hallucination metrics |
| `tests/test_conversation_behavior.py` | Runs conversation G-Eval rubrics |
| `tests/test_safety_guardrails.py` | Runs safety and refusal G-Eval rubrics |

## Reading test results

### Passed

```text
1 passed
```

The judge score satisfied every configured metric threshold.

### Failed

A failure includes the metric name, score, threshold, and judge reason:

```text
Metrics: Faithfulness (score: 0.5, threshold: 0.7, reason: ...)
```

Use the reason as diagnostic evidence, not unquestionable truth. Check:

1. Is the mock response actually correct?
2. Is the user input clear?
3. Does the context state every fact used by the response?
4. Is the rubric precise?
5. Did the judge misunderstand an ambiguous phrase?

Improve the test data or rubric when it is ambiguous. Do not automatically
lower the threshold.

### Skipped

```text
26 skipped
```

The judge key is missing, empty, or still an example placeholder.

### Warnings

DeepEval may emit `asyncio.iscoroutinefunction` deprecation warnings under
Python 3.14. Tests can still pass. Warnings are not failures, but they should
be reviewed again after dependency upgrades.

## Troubleshooting

### `pytest` or `deepeval` is not found

Activate the virtual environment and reinstall dependencies:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Tests are skipped

Confirm that `.env` exists and contains a real judge key.

Check whether Groq loaded without printing the secret:

```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Groq key loaded:', bool(os.getenv('GROQ_API_KEY')))"
```

### Groq or OpenAI returns `401`

The provider key is invalid, expired, copied incorrectly, or still a
placeholder. Replace it in `.env`. Never paste it into a chat or issue.

### Groq returns `403`

The selected model may be blocked for the Groq organization or project.
Enable it in Groq model permissions or choose an allowed model that supports
JSON output.

### The provider returns `429`

The account exceeded a request or token rate limit. Wait for the quota window
to reset, run fewer cases, use a marker or exact node ID, or use cached
DeepEval results where appropriate.

### `ConfidentApiError: Invalid API key`

This is an optional dashboard error, not a Groq/OpenAI judge error.

For local testing:

```bash
deepeval logout
pytest -q
```

For dashboard uploads:

```bash
deepeval logout
deepeval login
deepeval test run tests
deepeval view
```

If any key was printed or shared, revoke it immediately and create a new one.

### Scores change between runs

The mock input and output are fixed, but the live judge can vary. Review the
judge reason, rerun the individual case, and refine ambiguous data or rubrics.

## Security checklist

- Keep `.env` and `.env.local` private.
- Never commit, print, log, or share API keys.
- Revoke any credential that appears in a transcript or chat.
- Commit only empty values in `.env.example`.
- Use synthetic data in mock cases.
- Review provider quota before large or repeated runs.

## Project limitations

This suite intentionally does not:

- call a real chatbot;
- generate `actual_output` dynamically;
- test streaming, multi-turn state, tools, or retrieval systems;
- verify an application's UI or API integration; or
- guarantee that a judge will score identically every time.

To evaluate a real application later, replace or supplement the static
`actual_output` values with responses captured from that application. Keep
the deterministic mock suite as a stable baseline.
