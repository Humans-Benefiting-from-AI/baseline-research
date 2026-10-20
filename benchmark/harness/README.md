# HRE evaluation harness

Runs the Halachic Reasoning Eval JSONL through pluggable model adapters and writes a Markdown report plus a JSON summary for each model.

Every report starts with:

> Questions not yet audited for halachic accuracy by Elie; results are not authoritative.

Dry-run is the default. It uses a mock adapter and does not contact OpenAI, Anthropic, or Google. The historical file `benchmark/hre_results.jsonl` is not read or written.

## Setup

From the `benchmark` directory:

```bash
pip install -r requirements-dev.txt
```

`requirements-dev.txt` installs pytest. Provider SDKs (`openai`, `anthropic`, `google-genai`, `python-dotenv`) are listed in `requirements.txt` and are imported only when a live adapter's `complete` method runs.

## Dry run

```bash
cd benchmark
python -m harness --limit 10
```

The same entry point as the original script:

```bash
python run_evals.py --limit 10
```

Defaults:

- Dataset: `hre_eval_100.jsonl`
- Providers: OpenAI, Anthropic, and Google
- Model ids: `gpt-5.6-sol`, `claude-sonnet-5-5`, `gemini-3.8-flash` (override; these are not the `gpt-4o` / Claude 3.5 snapshots from the first results file)
- Output: `benchmark/reports/` (gitignored)
- Scoring: exact leading label, then whole-phrase keyword match. Provider errors and empty answers are status `error` or `empty` and are left out of accuracy.
- Output token cap: 1024 (`--max-tokens` to override). Claude thinking tokens count against this cap.
- Retries: a live call that fails with HTTP 503 or a disconnect is tried up to 2 more times, waiting 1s and then 2s.
- LLM-as-judge: off

`--limit N` validates the file, then scores the first N questions. Use it for a smoke run.

```bash
python -m harness --limit 10 \
  --openai-model gpt-4o \
  --anthropic-model claude-3-5-sonnet-20240620 \
  --google-model gemini-3.8-flash
```

Environment overrides, used when the matching flag is omitted:

- `OPENAI_MODEL`
- `ANTHROPIC_MODEL`
- `GOOGLE_MODEL`

Keys, read only by a live adapter, and only from the environment:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`

A `benchmark/.env` file is loaded into the environment when `python-dotenv` is installed. Adapters do not take keys on the command line.

## Live run

Live calls are off unless you pass `--no-dry-run`. That path is not used by the tests and is not part of a dry-run check. It spends API credits.

```bash
python -m harness --no-dry-run --limit 10
```

`--judge` turns on the LLM-as-judge hook after the automatic rubric misses. The hook stays off during dry-run even if the flag is present. Temperature is omitted unless you pass `--temperature`. The original loop sent `temperature=0.0`; pass that flag on a model that still accepts it.

## Scoring

The 100-question file uses a closed label set: `YES`, `NO`, `PERMITTED`, `FORBIDDEN`, `PLAINTIFF`, `DEFENDANT`, `NO SUCH TEXT`.

1. Exact: bold, italics, and punctuation are stripped, then the answer matches if it is the label or starts with it (`**FORBIDDEN.**`, `YES.`).
2. A different opening label is wrong. `**PERMITTED.**` followed later by `FORBIDDEN` does not get credit when the ground truth is `FORBIDDEN`.
3. Keyword: only when the answer does not open with a canonical label. The label must appear as a whole phrase. `YES` does not match `yesterday`, `NO` does not match `anomaly`, and `NO` does not match `NO SUCH TEXT`.
4. Judge: disabled unless `--judge` is set on a live run. A leading-label disagreement does not call it.

Provider errors (`ERROR:` / `SKIPPED`, or a failed call) are status `error`. A blank answer is status `empty`. Both are listed in `index.md` and in each model report, and neither is included in the accuracy denominator.

A live 503 or disconnect is retried up to 2 times before it is recorded as `error`. HTTP 429 `RESOURCE_EXHAUSTED` is status `error` with a `quota/billing` message and is not retried.

## Reports

For each model the harness writes:

- `reports/<provider>__<model>.md`
- `reports/<provider>__<model>.json`

`reports/index.md` and `reports/index.json` list the models from that run. Each file carries the audit banner.

## Tests

```bash
cd benchmark
pytest
```

The tests run in dry-run and block socket connects. They do not call a provider.
