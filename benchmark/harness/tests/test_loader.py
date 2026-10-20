from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness.loader import QuestionLoadError, load_questions

BENCHMARK_DIR = Path(__file__).resolve().parents[2]
DATASET = BENCHMARK_DIR / "hre_eval_100.jsonl"
LABELS = {
    "YES",
    "NO",
    "PERMITTED",
    "FORBIDDEN",
    "PLAINTIFF",
    "DEFENDANT",
    "NO SUCH TEXT",
}


def _write(path: Path, rows: list[dict]) -> None:
    text = "".join(json.dumps(row) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _row(**overrides) -> dict:
    base = {
        "id": "hre-test-001",
        "archetype": "Temporal Source-Gating",
        "prompt": "A prompt.",
        "eval_task": "Answer YES or NO.",
        "ground_truth": "YES",
        "logic_explanation": "Because the dates do not line up.",
    }
    base.update(overrides)
    return base


def test_real_dataset_loads_one_hundred_labeled_questions():
    questions = load_questions(DATASET)
    assert len(questions) == 100
    assert len({question.id for question in questions}) == 100
    assert {question.ground_truth for question in questions} <= LABELS
    assert all(question.prompt and question.eval_task for question in questions)


def test_limit_keeps_the_first_n_after_validation(tmp_path: Path):
    path = tmp_path / "questions.jsonl"
    _write(path, [_row(id=f"id-{index}") for index in range(4)])
    questions = load_questions(path, limit=2)
    assert [question.id for question in questions] == ["id-0", "id-1"]


def test_optional_trap_and_unknown_extra_are_kept(tmp_path: Path):
    path = tmp_path / "questions.jsonl"
    _write(path, [_row(trap="A simplistic guess.", source="lecture-12")])
    question = load_questions(path)[0]
    assert question.trap == "A simplistic guess."
    assert question.extras == {"source": "lecture-12"}


def test_blank_lines_are_skipped(tmp_path: Path):
    path = tmp_path / "questions.jsonl"
    path.write_text(json.dumps(_row()) + "\n\n", encoding="utf-8")
    assert len(load_questions(path)) == 1


@pytest.mark.parametrize(
    "mutator, message",
    [
        (lambda row: row.pop("ground_truth"), "ground_truth"),
        (lambda row: row.update({"id": "  "}), "id"),
        (lambda row: row.update({"prompt": 3}), "prompt"),
    ],
)
def test_required_fields_are_validated(tmp_path: Path, mutator, message):
    path = tmp_path / "questions.jsonl"
    row = _row()
    mutator(row)
    _write(path, [row])
    with pytest.raises(QuestionLoadError, match=message):
        load_questions(path)


def test_duplicate_ids_are_rejected(tmp_path: Path):
    path = tmp_path / "questions.jsonl"
    _write(path, [_row(id="same"), _row(id="same")])
    with pytest.raises(QuestionLoadError, match="repeats"):
        load_questions(path)


def test_invalid_json_reports_the_line(tmp_path: Path):
    path = tmp_path / "questions.jsonl"
    path.write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(QuestionLoadError, match="Line 1"):
        load_questions(path)


def test_limit_must_be_positive(tmp_path: Path):
    path = tmp_path / "questions.jsonl"
    _write(path, [_row()])
    with pytest.raises(QuestionLoadError, match="limit"):
        load_questions(path, limit=0)
