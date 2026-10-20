"""Retry behavior for 503 and disconnects. No provider SDK is imported."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness.adapters.base import AdapterError, Completion, MissingAPIKey
from harness.loader import Question
from harness.report import ItemResult, ModelReport, write_reports
from harness.retry import QUOTA_ERROR_MESSAGE, call_with_retry, is_quota_error, is_retryable
from harness.runner import RunConfig, execute
from harness.scoring import Score


class _StatusError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


def test_503_and_disconnect_are_retryable_and_other_errors_are_not():
    assert is_retryable(_StatusError("UNAVAILABLE", 503))
    assert is_retryable(RuntimeError("503 UNAVAILABLE. The model is overloaded."))
    assert is_retryable(ConnectionError("Server disconnected"))
    assert is_retryable(RuntimeError("RemoteProtocolError: peer closed connection"))
    assert not is_retryable(_StatusError("bad request", 400))
    assert not is_retryable(AdapterError("sdk missing"))
    assert not is_retryable(MissingAPIKey("OPENAI_API_KEY is not set"))
    assert not is_retryable(_StatusError("429 RESOURCE_EXHAUSTED", 429))
    assert is_quota_error(_StatusError("429 RESOURCE_EXHAUSTED", 429))
    assert is_quota_error(RuntimeError("RESOURCE_EXHAUSTED"))
    assert not is_quota_error(_StatusError("503 high demand", 503))


def test_retry_waits_then_stops_after_two_retries():
    calls = {"n": 0}
    sleeps: list[float] = []

    def fn():
        calls["n"] += 1
        raise _StatusError("503 high demand", 503)

    with pytest.raises(_StatusError):
        call_with_retry(fn, sleep=sleeps.append)
    assert calls["n"] == 3
    assert sleeps == [1.0, 2.0]


def test_retry_returns_the_successful_attempt():
    calls = {"n": 0}
    sleeps: list[float] = []

    def fn():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("connection reset by peer")
        return "YES"

    assert call_with_retry(fn, sleep=sleeps.append) == "YES"
    assert calls["n"] == 3
    assert sleeps == [1.0, 2.0]


def test_429_is_not_retried():
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        raise _StatusError("429 RESOURCE_EXHAUSTED", 429)

    with pytest.raises(_StatusError):
        call_with_retry(fn, sleep=lambda _seconds: pytest.fail("slept"))
    assert calls["n"] == 1


def test_429_is_recorded_as_quota_billing_and_excluded(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        "harness.runner._backoff_sleep", lambda _seconds: pytest.fail("slept")
    )
    adapter = _Scripted(
        [_StatusError("429 RESOURCE_EXHAUSTED. Quota exceeded for this project.", 429)]
    )
    monkeypatch.setattr("harness.runner.build_adapter", lambda *_args, **_kwargs: adapter)
    dataset = tmp_path / "questions.jsonl"
    _dataset(dataset)

    reports = execute(_config(dataset, tmp_path / "reports"))

    assert adapter.calls == 1
    report = reports[0]
    assert report.errors == 1
    assert report.scored == 0
    assert report.accuracy is None
    item = report.items[0]
    assert item.score.status == "error"
    assert item.score.detail == QUOTA_ERROR_MESSAGE
    assert "quota/billing" in item.response
    assert "not retried" in item.score.detail.lower()


def test_non_retryable_error_is_not_repeated():
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        raise _StatusError("model not found", 404)

    with pytest.raises(_StatusError):
        call_with_retry(fn, sleep=lambda _seconds: pytest.fail("slept"))
    assert calls["n"] == 1


class _Scripted:
    provider = "google"
    model = "gemini-test"

    def __init__(self, outcomes: list):
        self.outcomes = outcomes
        self.calls = 0

    def require_key(self) -> None:
        return None

    def complete(self, *, system: str, user: str) -> Completion:
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _dataset(path: Path, count: int = 1) -> None:
    rows = []
    for index in range(count):
        row = {
            "id": f"hre-test-{index + 1:03d}",
            "archetype": "Temporal Source-Gating",
            "prompt": "A prompt.",
            "eval_task": "Answer YES or NO.",
            "ground_truth": "YES",
            "logic_explanation": "Dates do not line up.",
        }
        rows.append(json.dumps(row))
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _config(dataset: Path, output_dir: Path, *, judge_enabled: bool = False) -> RunConfig:
    return RunConfig(
        dataset=dataset,
        output_dir=output_dir,
        providers=["google"],
        model_ids={"google": "gemini-test"},
        dry_run=False,
        judge_enabled=judge_enabled,
        sleep_seconds=0,
    )


def test_live_path_retries_503_then_scores(tmp_path: Path, monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr("harness.runner._backoff_sleep", sleeps.append)
    adapter = _Scripted(
        [
            _StatusError("503 high demand", 503),
            _StatusError("503 high demand", 503),
            Completion(text="YES", model="gemini-test", provider="google"),
        ]
    )
    monkeypatch.setattr("harness.runner.build_adapter", lambda *_args, **_kwargs: adapter)
    dataset = tmp_path / "questions.jsonl"
    _dataset(dataset)
    output_dir = tmp_path / "reports"

    reports = execute(_config(dataset, output_dir))

    assert adapter.calls == 3
    assert sleeps == [1.0, 2.0]
    assert reports[0].correct == 1
    assert reports[0].scored == 1
    assert reports[0].errors == 0
    assert reports[0].accuracy == 1


def test_exhausted_503s_are_an_error_and_excluded_from_accuracy(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("harness.runner._backoff_sleep", lambda _seconds: None)
    adapter = _Scripted([_StatusError("503 high demand", 503) for _ in range(3)])
    monkeypatch.setattr("harness.runner.build_adapter", lambda *_args, **_kwargs: adapter)
    dataset = tmp_path / "questions.jsonl"
    _dataset(dataset)

    reports = execute(_config(dataset, tmp_path / "reports"))

    assert adapter.calls == 3
    report = reports[0]
    assert report.errors == 1
    assert report.scored == 0
    assert report.accuracy is None
    assert report.items[0].score.status == "error"
    assert "503" in report.items[0].response


def test_judge_retries_a_disconnect_then_scores(tmp_path: Path, monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr("harness.runner._backoff_sleep", sleeps.append)
    adapter = _Scripted(
        [
            Completion(text="The meat is fine.", model="gemini-test", provider="google"),
            ConnectionError("server disconnected"),
            Completion(text="CORRECT", model="gemini-test", provider="google"),
        ]
    )
    monkeypatch.setattr("harness.runner.build_adapter", lambda *_args, **_kwargs: adapter)
    dataset = tmp_path / "questions.jsonl"
    _dataset(dataset)
    output_dir = tmp_path / "reports"

    reports = execute(_config(dataset, output_dir, judge_enabled=True))

    assert adapter.calls == 3
    assert sleeps == [1.0]
    assert reports[0].items[0].score.method == "judge"
    assert reports[0].correct == 1
    assert reports[0].scored == 1
    assert reports[0].errors == 0
    assert (output_dir / "google__gemini-test.json").is_file()


def test_judge_503_is_an_error_and_the_run_still_writes_reports(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("harness.runner._backoff_sleep", lambda _seconds: None)
    adapter = _Scripted(
        [
            Completion(text="YES", model="gemini-test", provider="google"),
            Completion(text="The meat is fine.", model="gemini-test", provider="google"),
            _StatusError("503 high demand", 503),
            _StatusError("503 high demand", 503),
            _StatusError("503 high demand", 503),
        ]
    )
    monkeypatch.setattr("harness.runner.build_adapter", lambda *_args, **_kwargs: adapter)
    dataset = tmp_path / "questions.jsonl"
    _dataset(dataset, count=2)
    output_dir = tmp_path / "reports"

    reports = execute(_config(dataset, output_dir, judge_enabled=True))

    assert adapter.calls == 5
    report = reports[0]
    assert report.items[0].score.method == "exact"
    assert report.items[0].score.correct == 1
    assert report.items[1].score.status == "error"
    assert report.items[1].score.method == "error"
    assert "503" in report.items[1].score.detail
    assert report.scored == 1
    assert report.errors == 1
    assert report.accuracy == 1
    assert (output_dir / "google__gemini-test.json").is_file()


def test_report_excludes_error_and_empty_from_accuracy(tmp_path: Path):
    question = Question(
        id="hre-test-001",
        archetype="Temporal Source-Gating",
        prompt="A prompt.",
        eval_task="Answer YES or NO.",
        ground_truth="YES",
        logic_explanation="Dates.",
    )
    other = Question(
        id="hre-test-002",
        archetype="Temporal Source-Gating",
        prompt="Another prompt.",
        eval_task="Answer YES or NO.",
        ground_truth="NO",
        logic_explanation="Dates.",
    )
    report = ModelReport(
        provider="anthropic",
        model="claude-test",
        dry_run=False,
        judge_enabled=False,
        dataset="questions.jsonl",
        items=[
            ItemResult(question, "YES", Score(1, "exact", "match")),
            ItemResult(other, "YES", Score(0, "none", "miss")),
            ItemResult(
                question,
                "ERROR: 503 high demand",
                Score(0, "error", "503 high demand", status="error"),
            ),
            ItemResult(
                question,
                "",
                Score(0, "empty", "Provider returned an empty answer.", status="empty"),
            ),
        ],
    )
    output_dir = tmp_path / "reports"
    write_reports([report], output_dir)

    assert report.scored == 2
    assert report.correct == 1
    assert report.errors == 1
    assert report.empty == 1
    assert report.accuracy == 0.5

    markdown = (output_dir / "anthropic__claude-test.md").read_text(encoding="utf-8")
    index = (output_dir / "index.md").read_text(encoding="utf-8")
    payload = json.loads((output_dir / "anthropic__claude-test.json").read_text(encoding="utf-8"))
    assert "- Errors: 1" in markdown
    assert "- Empty: 1" in markdown
    assert "50.0% (1/2 scored" in markdown
    assert "| error |" in markdown
    assert "| empty |" in markdown
    assert "| Errors | Empty |" in index
    assert "| anthropic | claude-test | 4 | 2 | 1 | 1 | 1 | 50.0% | False |" in index
    assert payload["accuracy"] == 0.5
    assert payload["errors"] == 1
    assert payload["empty"] == 1
    assert payload["items"][2]["score"] is None
    assert payload["items"][2]["status"] == "error"
    assert payload["items"][3]["status"] == "empty"
