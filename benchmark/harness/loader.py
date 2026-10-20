"""Load and validate HRE ``.jsonl`` question files."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_FIELDS = (
    "id",
    "archetype",
    "prompt",
    "eval_task",
    "ground_truth",
    "logic_explanation",
)

# Present on the v2 set. Older rows omit it.
OPTIONAL_FIELDS = ("trap",)


class QuestionLoadError(ValueError):
    """The question file is missing, unreadable, or fails validation."""


@dataclass(frozen=True)
class Question:
    """One HRE item.

    ``extras`` keeps forward-compatible keys so a later dataset column is
    not dropped on the floor. Scoring uses ``ground_truth`` only.
    """

    id: str
    archetype: str
    prompt: str
    eval_task: str
    ground_truth: str
    logic_explanation: str
    trap: str | None = None
    extras: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        payload = {
            "id": self.id,
            "archetype": self.archetype,
            "prompt": self.prompt,
            "eval_task": self.eval_task,
            "ground_truth": self.ground_truth,
            "logic_explanation": self.logic_explanation,
        }
        if self.trap is not None:
            payload["trap"] = self.trap
        payload.update(self.extras)
        return payload


def load_questions(path: Path, *, limit: int | None = None) -> list[Question]:
    """Read a JSONL dataset, validate every row, and optionally keep the first N.

    ``limit`` is applied after validation so a bad row is never skipped by
    cutting the file short. ``None`` keeps every row.
    """
    if limit is not None and limit < 1:
        raise QuestionLoadError("--limit must be a positive integer.")

    dataset = Path(path)
    if not dataset.is_file():
        raise QuestionLoadError(f"Question file not found: {dataset}")

    questions: list[Question] = []
    seen_ids: set[str] = set()

    with dataset.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                continue
            questions.append(_parse_line(raw_line, line_number, seen_ids))

    if not questions:
        raise QuestionLoadError(f"No questions found in {dataset}")

    if limit is not None:
        return questions[:limit]
    return questions


def _parse_line(raw_line: str, line_number: int, seen_ids: set[str]) -> Question:
    try:
        payload = json.loads(raw_line)
    except json.JSONDecodeError as exc:
        raise QuestionLoadError(
            f"Line {line_number} is not valid JSON: {exc.msg}"
        ) from exc

    if not isinstance(payload, dict):
        raise QuestionLoadError(f"Line {line_number} must be a JSON object.")

    for name in REQUIRED_FIELDS:
        value = payload.get(name)
        if not isinstance(value, str) or not value.strip():
            raise QuestionLoadError(
                f"Line {line_number} is missing a non-empty string field {name!r}."
            )

    question_id = payload["id"].strip()
    if question_id in seen_ids:
        raise QuestionLoadError(
            f"Line {line_number} repeats question id {question_id!r}."
        )
    seen_ids.add(question_id)

    trap = payload.get("trap")
    if trap is not None and not isinstance(trap, str):
        raise QuestionLoadError(f"Line {line_number} field 'trap' must be a string.")

    known = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)
    extras = {key: value for key, value in payload.items() if key not in known}

    return Question(
        id=question_id,
        archetype=payload["archetype"].strip(),
        prompt=payload["prompt"].strip(),
        eval_task=payload["eval_task"].strip(),
        ground_truth=payload["ground_truth"].strip(),
        logic_explanation=payload["logic_explanation"].strip(),
        trap=trap.strip() if isinstance(trap, str) else None,
        extras=extras,
    )
