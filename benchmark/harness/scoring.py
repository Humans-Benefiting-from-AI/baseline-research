"""Score a model answer against ``ground_truth``.

Rubric, applied in order. The first hit wins.

1. Exact. The normalized answer is the ground-truth label, or it begins
   with that label on a word boundary (``YES. ...``, ``FORBIDDEN, ...``).
2. Keyword. The ground-truth phrase occurs later in the answer, again on
   word boundaries. Short labels such as ``YES`` and ``NO`` do not match
   inside longer words (``yesterday``, ``anomaly``, ``know``).
3. LLM-as-judge. Only when a judge is passed and ``enabled`` is true.
   The default run does not construct an enabled judge, and a disabled
   judge is never called.

The original ``run_evals.py`` loop used a raw substring check
(``ground_truth.lower() in response``). Whole-phrase matching replaces
that check so the closed label set in the 100-question file
(YES, NO, PERMITTED, FORBIDDEN, PLAINTIFF, DEFENDANT, NO SUCH TEXT)
is not credited accidentally. Answers that start with ``ERROR:`` or
``SKIPPED`` score 0 and do not fall through to the judge.
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
    correct: int
    method: str
    detail: str

    def to_dict(self) -> dict:
        return {
            "correct": self.correct,
            "method": self.method,
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
        return Score(0, "error", "Provider returned an error or a skip marker.")

    if exact_match(question.ground_truth, response):
        return Score(1, "exact", "Leading conclusion matches the ground truth.")

    if keyword_match(question.ground_truth, response):
        return Score(1, "keyword", "Ground-truth phrase appears as a whole phrase.")

    if judge is not None and judge.enabled:
        return judge.judge(question, response)

    return Score(0, "none", "No exact or whole-phrase keyword match.")


def exact_match(ground_truth: str, response: str) -> bool:
    label = _normalize(ground_truth)
    text = _normalize(response)
    if not label or not text:
        return False
    if text == label:
        return True
    match = re.match(re.escape(label) + r"(?!\w)", text)
    return match is not None and _is_standalone(label, text, match.start())


def keyword_match(ground_truth: str, response: str) -> bool:
    label = _normalize(ground_truth)
    text = _normalize(response)
    if not label or not text:
        return False
    for match in re.finditer(r"(?<!\w)" + re.escape(label) + r"(?!\w)", text):
        if _is_standalone(label, text, match.start()):
            return True
    return False


def _is_standalone(label: str, text: str, start: int) -> bool:
    """False when this hit is only the opening of a longer canonical label."""
    for other in CANONICAL_LABELS:
        if other == label or not other.startswith(label + " "):
            continue
        end = start + len(other)
        if text.startswith(other, start) and (end == len(text) or not text[end].isalnum()):
            return False
    return True


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).casefold()


def _is_transport_failure(response: str) -> bool:
    head = response.lstrip().upper()
    return head.startswith("ERROR:") or head.startswith("SKIPPED")
