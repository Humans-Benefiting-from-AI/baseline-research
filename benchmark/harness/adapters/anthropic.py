"""Anthropic Messages adapter.

The model id is an argument. The Claude 3.5 snapshots used for the first
results file are not hardcoded. The key is read from ``ANTHROPIC_API_KEY``
at call time.
"""

from __future__ import annotations

import os

from harness.adapters.base import AdapterError, Completion, MissingAPIKey, ModelAdapter
from harness.models import API_KEY_ENV

_PROVIDER = "anthropic"
_KEY_ENV = API_KEY_ENV[_PROVIDER]


class AnthropicAdapter(ModelAdapter):
    def __init__(
        self,
        *,
        model: str,
        max_tokens: int | None = 256,
        temperature: float | None = None,
    ) -> None:
        if not model or not model.strip():
            raise ValueError("Anthropic model id is required.")
        self.provider = _PROVIDER
        self.model = model.strip()
        # The Messages API requires max_tokens.
        self.max_tokens = 256 if max_tokens is None else max_tokens
        self.temperature = temperature

    def require_key(self) -> None:
        _read_key()

    def complete(self, *, system: str, user: str) -> Completion:
        api_key = _read_key()
        try:
            import anthropic
        except ImportError as exc:
            raise AdapterError(
                "The anthropic package is not installed. "
                "Install benchmark/requirements.txt before a live run."
            ) from exc

        client = anthropic.Anthropic(api_key=api_key)
        kwargs: dict = {
            "model": self.model,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "max_tokens": self.max_tokens,
        }
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature

        response = client.messages.create(**kwargs)
        return Completion(
            text=_message_text(response),
            model=self.model,
            provider=self.provider,
            mock=False,
        )


def _read_key() -> str:
    value = os.environ.get(_KEY_ENV, "").strip()
    if not value:
        raise MissingAPIKey(
            f"{_KEY_ENV} is not set. Live Anthropic runs read that variable and no other key source."
        )
    return value


def _message_text(response: object) -> str:
    try:
        blocks = response.content  # type: ignore[attr-defined]
    except AttributeError as exc:
        raise AdapterError(f"Anthropic response had no content: {exc}") from exc
    parts: list[str] = []
    for block in blocks:
        # Skip thinking blocks on models that return them beside the answer.
        block_type = getattr(block, "type", None)
        if block_type not in (None, "text"):
            continue
        text = getattr(block, "text", None)
        if text:
            parts.append(str(text))
    return "\n".join(parts).strip()
