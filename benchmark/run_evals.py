#!/usr/bin/env python3
"""Halachic Reasoning Eval entry point.

The evaluation loop that used to live in this file now lives in
``benchmark/harness``. This script delegates to that CLI so the existing
command still works.

Dry-run is the default: a mock adapter for OpenAI, Anthropic, and Google,
no network call, and no write to ``hre_results.jsonl``. The historical
results file in this directory is left untouched.

Examples, from this directory::

    python run_evals.py --limit 10
    python run_evals.py --limit 10 --openai-model gpt-4o
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCHMARK_DIR = Path(__file__).resolve().parent
if str(_BENCHMARK_DIR) not in sys.path:
    sys.path.insert(0, str(_BENCHMARK_DIR))

from harness.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
