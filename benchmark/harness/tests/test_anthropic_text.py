"""Anthropic content parsing. No SDK and no network."""

from __future__ import annotations

from harness.adapters.anthropic import _message_text
from harness.adapters.base import Completion
from harness.loader import Question
from harness.runner import _score_completion
from harness.scoring import LLMJudge


class _Block:
    def __init__(self, block_type: str, text: str | None = None, thinking: str | None = None):
        self.type = block_type
        self.text = text
        self.thinking = thinking


class _Response:
    def __init__(self, content: list, stop_reason: str = "end_turn"):
        self.content = content
        self.stop_reason = stop_reason


def test_text_block_after_thinking_is_the_answer():
    response = _Response(
        [
            _Block("thinking", thinking="The trace considers YES, then checks dates."),
            _Block("text", text="YES. The Chazon Ish is a later work."),
        ]
    )
    assert _message_text(response) == "YES. The Chazon Ish is a later work."


def test_thinking_only_response_is_empty():
    response = _Response(
        [_Block("thinking", thinking="YES. This trace never became a text block.")],
        stop_reason="max_tokens",
    )
    assert _message_text(response) == ""


def test_empty_text_after_max_tokens_stays_empty_and_keeps_the_note():
    question = Question(
        id="hre-test-001",
        archetype="Temporal Source-Gating",
        prompt="A prompt.",
        eval_task="Answer YES or NO.",
        ground_truth="YES",
        logic_explanation="Dates.",
    )
    completion = Completion(
        text="",
        model="claude-test",
        provider="anthropic",
        detail=(
            "Anthropic stopped at max_tokens before a text answer. "
            "Thinking blocks are not scored."
        ),
    )
    judge = LLMJudge(adapter=object(), enabled=True)
    score = _score_completion(question, completion, judge)
    assert score.status == "empty"
    assert "max_tokens" in score.detail
    assert "Thinking blocks are not scored." in score.detail


def test_dict_blocks_skip_thinking():
    response = _Response(
        [
            {"type": "thinking", "thinking": "internal", "text": "NO"},
            {"type": "redacted_thinking", "data": "hidden"},
            {"type": "text", "text": "FORBIDDEN"},
        ]
    )
    assert _message_text(response) == "FORBIDDEN"
