# Halachic Reasoning Evaluation (HRE) Harness

This directory contains the question JSONL files, the historical `hre_results.jsonl` run, and the evaluation harness in [`harness/`](harness/README.md).

The harness scores OpenAI, Anthropic, and Google. Model ids are arguments (or `OPENAI_MODEL`, `ANTHROPIC_MODEL`, and `GOOGLE_MODEL`). Dry-run is the default: a mock adapter, no network call, and no write to `hre_results.jsonl`.

```bash
cd benchmark
pip install -r requirements-dev.txt
python -m harness --limit 10
```

`python run_evals.py --limit 10` is the same entry point. Reports go to `benchmark/reports/` and carry the banner that the questions are not yet audited by Elie.

A live run (`--no-dry-run`) reads `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GOOGLE_API_KEY` from the environment only. Install `requirements.txt` before that. Usage, the rubric, and the report layout are in [`harness/README.md`](harness/README.md).
