"""Prompt text carried over from the original ``run_evals.py`` loop."""

from harness.loader import Question

# The original harness required a short canonical conclusion before any
# explanation. Keep that instruction so later live runs stay comparable
# to the scoring rubric, which looks for those labels.
SYSTEM_PROMPT = (
    "You are a Halachic expert. You must output EXACTLY the requested "
    "conclusion (e.g., YES, NO, PERMITTED, FORBIDDEN, PLAINTIFF, DEFENDANT, "
    "NO SUCH TEXT) followed by a brief 1-2 sentence explanation."
)


def build_user_prompt(question: Question) -> str:
    """Same user message the original loop sent to each model."""
    return f"{question.prompt}\n\nTask: {question.eval_task}"
