"""Run the dataset through one adapter per provider and score the answers."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

from harness.adapters import build_adapter
from harness.adapters.base import MissingAPIKey
from harness.loader import Question, load_questions
from harness.models import API_KEY_ENV, DEFAULT_MAX_TOKENS
from harness.prompts import SYSTEM_PROMPT, build_user_prompt
from harness.report import ItemResult, ModelReport, UnsafeOutputError, assert_safe_output, write_reports
from harness.retry import call_with_retry
from harness.scoring import LLMJudge, Score, score_response


@dataclass(frozen=True)
class RunConfig:
    dataset: Path
    output_dir: Path
    providers: list[str]
    model_ids: dict[str, str]
    limit: int | None = None
    dry_run: bool = True
    judge_enabled: bool = False
    max_tokens: int | None = DEFAULT_MAX_TOKENS
    temperature: float | None = None
    sleep_seconds: float = 1.0


def execute(config: RunConfig) -> list[ModelReport]:
    """Load questions, complete them, score them, and write reports.

    Dry-run (the default) uses the mock adapter for every provider and
    does not sleep, read API keys, or import provider SDKs.
    """
    assert_safe_output(config.output_dir)
    questions = load_questions(config.dataset, limit=config.limit)
    adapters = []
    for provider in config.providers:
        adapter = build_adapter(
            provider,
            config.model_ids[provider],
            dry_run=config.dry_run,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
        if not config.dry_run:
            # Fail before the first paid call if any selected key is missing.
            adapter.require_key()
        adapters.append(adapter)

    judge_enabled = config.judge_enabled and not config.dry_run
    reports: list[ModelReport] = []
    for adapter in adapters:
        # The judge, when enabled, reuses the adapter under test. It stays
        # disabled in dry-run so the mock is not asked to grade itself.
        judge = LLMJudge(adapter, enabled=judge_enabled)
        items: list[ItemResult] = []
        for index, question in enumerate(questions):
            completion = _complete(adapter, question)
            score = _score_completion(question, completion, judge)
            items.append(
                ItemResult(question=question, response=completion.text, score=score)
            )
            if not config.dry_run and config.sleep_seconds > 0 and index < len(questions) - 1:
                time.sleep(config.sleep_seconds)
        reports.append(
            ModelReport(
                provider=adapter.provider,
                model=adapter.model,
                dry_run=config.dry_run,
                judge_enabled=judge_enabled,
                dataset=str(config.dataset),
                items=items,
            )
        )

    write_reports(reports, config.output_dir)
    return reports


def _backoff_sleep(seconds: float) -> None:
    time.sleep(seconds)


def _complete(adapter, question: Question):
    from harness.adapters.base import Completion

    try:
        return call_with_retry(
            lambda: adapter.complete(
                system=SYSTEM_PROMPT, user=build_user_prompt(question)
            ),
            sleep=_backoff_sleep,
        )
    except MissingAPIKey:
        raise
    except Exception as exc:
        message = _redact(str(exc))
        return Completion(
            text=f"ERROR: {message}",
            model=getattr(adapter, "model", ""),
            provider=getattr(adapter, "provider", ""),
            mock=False,
            status="error",
            detail=message[:500],
        )


def _score_completion(question: Question, completion, judge: LLMJudge) -> Score:
    if completion.status == "error":
        detail = completion.detail or completion.text.strip()[:500]
        return Score(0, "error", detail or "Provider returned an error.", status="error")
    score = score_response(question, completion.text, judge=judge)
    if score.status == "empty" and completion.detail:
        return Score(0, "empty", completion.detail, status="empty")
    return score


def _redact(text: str) -> str:
    redacted = text
    for env_name in API_KEY_ENV.values():
        value = os.environ.get(env_name, "")
        if value:
            redacted = redacted.replace(value, f"${env_name}")
    return redacted


def historical_results_path(benchmark_dir: Path) -> Path:
    return benchmark_dir / "hre_results.jsonl"


def guard_historical_file(benchmark_dir: Path, output_dir: Path) -> None:
    """Extra check used by the CLI before a run starts."""
    historical = historical_results_path(benchmark_dir).resolve()
    target = output_dir.resolve()
    if target == historical or target.name == "hre_results.jsonl":
        raise UnsafeOutputError(
            "Refusing to write hre_results.jsonl. That file is the historical run."
        )
