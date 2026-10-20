"""Score a model answer against ``ground_truth``.

Rubric, applied in order. The first hit wins.

1. Exact. Markdown emphasis and punctuation are stripped, then the answer
   matches if it is the ground-truth label or begins with it
   (``**FORBIDDEN.**``, ``YES. ...``).
2. Leading disagreement. If that opening label is a different canonical
   label, the answer is wrong. A later mention of the expected label is
   not a keyword hit. ``**PERMITTED.** ... FORBIDDEN`` is wrong when the
   ground truth is FORBIDDEN.
3. Keyword. Used only when the answer does not open with a canonical
   label. The ground-truth phrase must appear on word boundaries.
   ``YES`` does not match inside ``yesterday``.
4. LLM-as-judge. Only when a judge is passed and ``enabled`` is true,
   and only after the checks above miss. A leading disagreement does
   not call the judge. The default run does not enable one.

The original ``run_evals.py`` loop used a raw substring check
(``ground_truth.lower() in response``). Whole-phrase matching replaces
that check so the closed label set in the 100-question file
(YES, NO, PERMITTED, FORBIDDEN, PLAINTIFF, DEFENDANT, NO SUCH TEXT)
is not credited accidentally. Provider errors and empty answers are
status ``error`` and ``empty``. They are not misses, the judge is not
called, and the report leaves them out of the accuracy denominator.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from harness.loader import Question

# Labels the shipped 100-question file actually uses. A shorter label is not
# credited when it is only the prefix of a longer one ("NO" inside
# "NO SUCH TEXT").
CANONICAL_LABELS = (
    "no such text",
    "permitted",
    "forbidden",
    "plaintiff",
    "defendant",
    "yes",
    "no",
)


class JudgeDisabled(RuntimeError):
    """An enabled judge method was used while judging is off."""


@dataclass(frozen=True)
class Score:
    """One rubric outcome.

    ``status`` is ``scored`` for an answer the rubric judged, ``error`` for
    a provider failure, and ``empty`` for a blank answer. Only ``scored``
    rows belong in the accuracy denominator. ``correct`` is 1 or 0; it is
    meaningful for ``scored`` rows.
    """

    correct: int
    method: str
    detail: str
    status: str = "scored"

    def to_dict(self) -> dict:
        return {
            "correct": self.correct if self.status == "scored" else None,
            "method": self.method,
            "status": self.status,
            "detail": self.detail,
        }


class LLMJudge:
    """Hook for a later judge model.

    ``enabled`` defaults to False. ``score_response`` does not call
    ``judge`` unless the automatic rubric missed and the hook is enabled.
    Enabling it on a live run sends one extra completion per miss through
    the same adapter. Dry-run leaves the hook disabled.
    """

    def __init__(self, adapter, *, enabled: bool = False) -> None:
        self.adapter = adapter
        self.enabled = enabled

    def judge(self, question: Question, response: str) -> Score:
        if not self.enabled:
            raise JudgeDisabled(
                "LLM-as-judge scoring is disabled. Pass --judge on a live run to enable it."
            )
        user = (
            "Score the candidate answer against the ground truth.\n"
            "Reply with a single line: CORRECT or INCORRECT.\n\n"
            f"Ground truth: {question.ground_truth}\n"
            f"Candidate answer:\n{response}"
        )
        completion = self.adapter.complete(
            system="You score Halachic eval answers. Reply CORRECT or INCORRECT only.",
            user=user,
        )
        verdict = completion.text.strip().splitlines()[0].strip().upper() if completion.text.strip() else ""
        if verdict.startswith("CORRECT"):
            return Score(1, "judge", "LLM-as-judge returned CORRECT.")
        return Score(0, "judge", "LLM-as-judge returned INCORRECT.")


def score_response(
    question: Question,
    response: str,
    *,
    judge: LLMJudge | None = None,
) -> Score:
    """Apply the rubric. A disabled or missing judge is not invoked."""
    if _is_transport_failure(response):
        return Score(
            0,
            "error",
            response.strip()[:500],
            status="error",
        )

    if not response or not response.strip():
        return Score(
            0,
            "empty",
            "Provider returned an empty answer.",
            status="empty",
        )

    prepared = _prepare(response)
    if not prepared:
        return Score(
            0,
            "empty",
            "Provider returned an empty answer.",
            status="empty",
        )

    if exact_match(question.ground_truth, response):
        return Score(1, "exact", "Leading conclusion matches the ground truth.")

    opened = _leading_label(prepared)
    if opened is not None and opened != _prepare(question.ground_truth):
        return Score(
            0,
            "mismatch",
            f"Leading label {opened.upper()} disagrees with {question.ground_truth}.",
        )

    if keyword_match(question.ground_truth, response):
        return Score(1, "keyword", "Ground-truth phrase appears as a whole phrase.")

    if judge is not None and judge.enabled:
        return judge.judge(question, response)

    return Score(0, "none", "No exact or whole-phrase keyword match.")


def exact_match(ground_truth: str, response: str) -> bool:
    opened = _leading_label(_prepare(response))
    expected = _prepare(ground_truth)
    return opened is not None and opened == expected


def keyword_match(ground_truth: str, response: str) -> bool:
    label = _prepare(ground_truth)
    text = _prepare(response)
    if not label or not text:
        return False
    for match in re.finditer(r"(?<!\w)" + re.escape(label) + r"(?!\w)", text):
        if _is_standalone(label, text, match.start()):
            return True
    return False


def _leading_label(prepared: str) -> str | None:
    """Canonical label at the start of a prepared answer, longest first."""
    if not prepared:
        return None
    for label in CANONICAL_LABELS:
        if re.match(re.escape(label) + r"(?!\w)", prepared) and _is_standalone(
            label, prepared, 0
        ):
            return label
    return None


def _prepare(text: str) -> str:
    """Drop markdown emphasis and punctuation, then collapse whitespace.

    ``**PERMITTED.**`` becomes ``permitted`` so the leading-label check
    sees the conclusion the model actually opened with.
    """
    without_emphasis = re.sub(r"[*_`]+", "", text)
    without_punctuation = re.sub(r"[^\w\s]+", " ", without_emphasis, flags=re.UNICODE)
    return re.sub(r"\s+", " ", without_punctuation.strip()).casefold()


def _is_standalone(label: str, text: str, start: int) -> bool:
    """False when this hit is only the opening of a longer canonical label."""
    for other in CANONICAL_LABELS:
        if other == label or not other.startswith(label + " "):
            continue
        end = start + len(other)
        if text.startswith(other, start) and (end == len(text) or not text[end].isalnum()):
            return False
    return True


def _is_transport_failure(response: str) -> bool:
    head = response.lstrip().upper()
    return head.startswith("ERROR:") or head.startswith("SKIPPED")
