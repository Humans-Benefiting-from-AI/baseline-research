"""Dry-run adapter. It never imports a provider SDK and never opens a socket."""

from __future__ import annotations

from harness.adapters.base import Completion, ModelAdapter

# Wording avoids the canonical HRE labels (YES, NO, PERMITTED, FORBIDDEN,
# PLAINTIFF, DEFENDANT, NO SUCH TEXT) so a dry-run is not scored as a hit.
MOCK_TEXT = (
    "[dry-run mock] Provider was not contacted. "
    "This row is a pipeline placeholder."
)


class MockAdapter(ModelAdapter):
    """Stand-in used whenever ``--dry-run`` is on (the default)."""

    def __init__(self, *, provider_label: str, model: str) -> None:
        self.provider = provider_label
        self.model = model
        self.calls = 0

    def complete(self, *, system: str, user: str) -> Completion:
        if not system or not user:
            raise ValueError("Mock adapter expected a system prompt and a user prompt.")
        self.calls += 1
        return Completion(
            text=MOCK_TEXT,
            model=self.model,
            provider=self.provider,
            mock=True,
        )
