"""Write one Markdown report and one JSON summary per model."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from harness.banner import AUDIT_BANNER
from harness.loader import Question
from harness.scoring import Score

# The historical results file. Reports must never replace it.
PROTECTED_RESULTS_NAME = "hre_results.jsonl"


class UnsafeOutputError(ValueError):
    """The requested output path would overwrite the historical results file."""


@dataclass(frozen=True)
class ItemResult:
    question: Question
    response: str
    score: Score

    def to_dict(self) -> dict:
        scored = self.score.status == "scored"
        return {
            "id": self.question.id,
            "archetype": self.question.archetype,
            "ground_truth": self.question.ground_truth,
            "response": self.response,
            "status": self.score.status,
            "score": self.score.correct if scored else None,
            "method": self.score.method,
            "detail": self.score.detail,
        }


@dataclass
class ModelReport:
    provider: str
    model: str
    dry_run: bool
    judge_enabled: bool
    dataset: str
    items: list[ItemResult]

    @property
    def total(self) -> int:
        return len(self.items)

    @property
    def scored(self) -> int:
        return sum(1 for item in self.items if item.score.status == "scored")

    @property
    def errors(self) -> int:
        return sum(1 for item in self.items if item.score.status == "error")

    @property
    def empty(self) -> int:
        return sum(1 for item in self.items if item.score.status == "empty")

    @property
    def correct(self) -> int:
        return sum(
            item.score.correct for item in self.items if item.score.status == "scored"
        )

    @property
    def accuracy(self) -> float | None:
        """Correct divided by scored answers. Errors and empty answers are excluded."""
        if self.scored == 0:
            return None
        return self.correct / self.scored

    def by_archetype(self) -> dict[str, dict]:
        buckets: dict[str, dict] = {}
        for item in self.items:
            bucket = buckets.setdefault(
                item.question.archetype,
                {
                    "correct": 0,
                    "scored": 0,
                    "total": 0,
                    "errors": 0,
                    "empty": 0,
                },
            )
            bucket["total"] += 1
            if item.score.status == "error":
                bucket["errors"] += 1
            elif item.score.status == "empty":
                bucket["empty"] += 1
            else:
                bucket["scored"] += 1
                bucket["correct"] += item.score.correct
        for bucket in buckets.values():
            scored = bucket["scored"]
            bucket["accuracy"] = (bucket["correct"] / scored) if scored else None
        return buckets

    def to_dict(self) -> dict:
        return {
            "banner": AUDIT_BANNER,
            "provider": self.provider,
            "model": self.model,
            "dry_run": self.dry_run,
            "judge_enabled": self.judge_enabled,
            "dataset": self.dataset,
            "questions": self.total,
            "scored": self.scored,
            "correct": self.correct,
            "errors": self.errors,
            "empty": self.empty,
            "accuracy": self.accuracy,
            "rubric": (
                "exact leading label, then whole-phrase keyword match; "
                "LLM-as-judge disabled"
                if not self.judge_enabled
                else "exact leading label, then whole-phrase keyword match, then LLM-as-judge"
            ),
            "by_archetype": self.by_archetype(),
            "items": [item.to_dict() for item in self.items],
        }


def assert_safe_output(path: Path) -> None:
    """Refuse any path whose file name is the historical results file."""
    if path.name == PROTECTED_RESULTS_NAME:
        raise UnsafeOutputError(
            "Refusing to write hre_results.jsonl. That file is the historical "
            "run and this harness does not modify it."
        )


def write_reports(reports: list[ModelReport], output_dir: Path) -> list[Path]:
    """Write ``<provider>__<model>.md`` and ``.json`` plus a short index."""
    assert_safe_output(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    index_models = []
    for report in reports:
        stem = _stem(report.provider, report.model)
        json_path = output_dir / f"{stem}.json"
        md_path = output_dir / f"{stem}.md"
        assert_safe_output(json_path)
        assert_safe_output(md_path)
        json_path.write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_markdown(report), encoding="utf-8")
        written.extend([md_path, json_path])
        index_models.append(
            {
                "provider": report.provider,
                "model": report.model,
                "dry_run": report.dry_run,
                "questions": report.total,
                "scored": report.scored,
                "correct": report.correct,
                "errors": report.errors,
                "empty": report.empty,
                "accuracy": report.accuracy,
                "markdown": md_path.name,
                "json": json_path.name,
            }
        )

    index = {
        "banner": AUDIT_BANNER,
        "models": index_models,
    }
    index_json = output_dir / "index.json"
    index_md = output_dir / "index.md"
    assert_safe_output(index_json)
    index_json.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        AUDIT_BANNER,
        "",
        "# HRE run index",
        "",
        "| Provider | Model | Questions | Scored | Correct | Errors | Empty | Accuracy | Dry run |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in index_models:
        lines.append(
            f"| {row['provider']} | {row['model']} | {row['questions']} | "
            f"{row['scored']} | {row['correct']} | {row['errors']} | {row['empty']} | "
            f"{_format_accuracy(row['accuracy'])} | {row['dry_run']} |"
        )
    lines.append("")
    index_md.write_text("\n".join(lines), encoding="utf-8")
    written.extend([index_md, index_json])
    return written


def _markdown(report: ModelReport) -> str:
    mode = "dry-run mock; no API call" if report.dry_run else "live provider call"
    judge = "disabled" if not report.judge_enabled else "enabled"
    lines = [
        AUDIT_BANNER,
        "",
        f"# HRE report: {report.provider} / {report.model}",
        "",
        f"- Mode: {mode}",
        f"- Dataset: {report.dataset}",
        f"- Questions: {report.total}",
        f"- Scored: {report.scored}",
        f"- Correct: {report.correct}",
        f"- Errors: {report.errors}",
        f"- Empty: {report.empty}",
        f"- Accuracy: {_format_accuracy(report.accuracy)} "
        f"({report.correct}/{report.scored} scored; errors and empty answers are excluded)",
        f"- LLM-as-judge: {judge}",
        "- Rubric: markdown and punctuation are stripped, then an exact "
        "match on the leading ground-truth label counts. A different leading "
        "label is wrong even if the expected label appears later. Otherwise "
        "a whole-phrase keyword match counts. The judge hook runs only when "
        "enabled and only after those checks miss.",
        "",
        "## Accuracy by archetype",
        "",
        "| Archetype | Correct | Scored | Errors | Empty | Total | Accuracy |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for archetype, stats in sorted(report.by_archetype().items()):
        lines.append(
            f"| {archetype} | {stats['correct']} | {stats['scored']} | "
            f"{stats['errors']} | {stats['empty']} | {stats['total']} | "
            f"{_format_accuracy(stats['accuracy'])} |"
        )

    lines.extend(
        [
            "",
            "## Items",
            "",
            "| id | archetype | ground truth | status | score | method |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report.items:
        score_cell = "—" if item.score.status != "scored" else str(item.score.correct)
        lines.append(
            f"| {item.question.id} | {item.question.archetype} | "
            f"{item.question.ground_truth} | {item.score.status} | "
            f"{score_cell} | {item.score.method} |"
        )
    lines.append("")
    return "\n".join(lines)


def _format_accuracy(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1%}"


def _stem(provider: str, model: str) -> str:
    safe_model = re.sub(r"[^A-Za-z0-9._-]+", "_", model).strip("._") or "model"
    return f"{provider}__{safe_model}"
