from __future__ import annotations

from harness.loader import Question
from harness.scoring import LLMJudge, score_response


def _question(ground_truth: str = "YES") -> Question:
    return Question(
        id="hre-test-001",
        archetype="Temporal Source-Gating",
        prompt="A prompt.",
        eval_task="Answer YES or NO.",
        ground_truth=ground_truth,
        logic_explanation="Dates do not line up.",
    )


class SpyJudge(LLMJudge):
    def __init__(self) -> None:
        super().__init__(adapter=None, enabled=True)
        self.calls = 0

    def judge(self, question, response):
        self.calls += 1
        from harness.scoring import Score

        return Score(1, "judge", "spy")


def test_markdown_and_punctuation_still_match_the_leading_label():
    assert score_response(_question("FORBIDDEN"), "**FORBIDDEN.**").method == "exact"
    assert score_response(_question("PERMITTED"), "**PERMITTED.**").correct == 1
    assert score_response(_question("YES"), "*YES*").method == "exact"
    assert score_response(_question("DEFENDANT"), "_DEFENDANT_").method == "exact"
    assert score_response(_question("YES"), "YES! The citation is later.").method == "exact"


def test_disagreeing_leading_label_is_wrong_even_if_the_expected_label_appears_later():
    judge = SpyJudge()
    scored = score_response(
        _question("FORBIDDEN"),
        "**PERMITTED.** The rule of kavu'a treats a fixed item as a safek, so it is FORBIDDEN.",
        judge=judge,
    )
    assert scored.correct == 0
    assert scored.status == "scored"
    assert scored.method == "mismatch"
    assert "PERMITTED" in scored.detail
    assert "FORBIDDEN" in scored.detail
    assert judge.calls == 0


def test_exact_label_and_leading_conclusion():
    assert score_response(_question("FORBIDDEN"), "FORBIDDEN").method == "exact"
    scored = score_response(
        _question("YES"),
        "YES. The Chazon Ish is a 20th century work.",
    )
    assert scored.correct == 1
    assert scored.method == "exact"


def test_keyword_matches_a_later_whole_phrase():
    scored = score_response(
        _question("DEFENDANT"),
        "Counting the votes is the wrong structure. The ruling is DEFENDANT.",
    )
    assert scored.correct == 1
    assert scored.method == "keyword"


def test_short_labels_do_not_match_inside_other_words():
    assert score_response(_question("YES"), "The text is from yesterday.").correct == 0
    assert score_response(_question("NO"), "This is an anomaly in the citation.").correct == 0
    assert score_response(_question("NO"), "I do not know of such a passage.").method == "none"


def test_shorter_label_does_not_eat_a_longer_one():
    assert score_response(_question("NO"), "NO SUCH TEXT").correct == 0
    assert score_response(_question("NO SUCH TEXT"), "NO SUCH TEXT").method == "exact"


def test_multiword_label_matches_as_a_phrase():
    scored = score_response(_question("NO SUCH TEXT"), "NO SUCH TEXT")
    assert scored.method == "exact"
    later = score_response(
        _question("NO SUCH TEXT"),
        "After checking, the conclusion is NO SUCH TEXT.",
    )
    assert later.method == "keyword"


def test_error_marker_scores_zero_without_the_judge():
    judge = SpyJudge()
    scored = score_response(_question("YES"), "ERROR: model not found", judge=judge)
    assert scored.correct == 0
    assert scored.method == "error"
    assert scored.status == "error"
    assert judge.calls == 0


def test_empty_answer_is_its_own_status_and_skips_the_judge():
    judge = SpyJudge()
    scored = score_response(_question("YES"), "   ", judge=judge)
    assert scored.status == "empty"
    assert scored.method == "empty"
    assert scored.correct == 0
    assert judge.calls == 0


def test_disabled_judge_is_not_called_on_a_miss():
    judge = LLMJudge(adapter=object(), enabled=False)
    scored = score_response(_question("YES"), "The meat is fine.", judge=judge)
    assert scored.method == "none"
    assert scored.correct == 0


def test_enabled_judge_runs_only_after_a_miss():
    judge = SpyJudge()
    hit = score_response(_question("YES"), "YES", judge=judge)
    assert hit.method == "exact"
    assert judge.calls == 0
    miss = score_response(_question("YES"), "The meat is fine.", judge=judge)
    assert miss.method == "judge"
    assert judge.calls == 1
