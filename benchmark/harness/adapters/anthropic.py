"""Anthropic Messages adapter.

The model id is an argument. The Claude 3.5 snapshots used for the first
results file are not hardcoded. The key is read from ``ANTHROPIC_API_KEY``
at call time.

Current Claude models spend part of ``max_tokens`` on thinking blocks.
The visible answer is the following ``text`` block. The default cap is
1024 so that block is not dropped the way it was at 256.
"""

from __future__ import annotations

import os

from harness.adapters.base import AdapterError, Completion, MissingAPIKey, ModelAdapter
from harness.models import API_KEY_ENV, DEFAULT_MAX_TOKENS

_PROVIDER = "anthropic"
_KEY_ENV = API_KEY_ENV[_PROVIDER]


class AnthropicAdapter(ModelAdapter):
    def __init__(
        self,
        *,
        model: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> None:
        if not model or not model.strip():
            raise ValueError("Anthropic model id is required.")
        self.provider = _PROVIDER
        self.model = model.strip()
        # The Messages API requires max_tokens. Thinking tokens count against it.
        self.max_tokens = DEFAULT_MAX_TOKENS if max_tokens is None else max_tokens
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
        text = _message_text(response)
        detail = ""
        if not text and getattr(response, "stop_reason", None) == "max_tokens":
            detail = (
                "Anthropic stopped at max_tokens before a text answer. "
                "Thinking blocks are not scored."
            )
        return Completion(
            text=text,
            model=self.model,
            provider=self.provider,
            mock=False,
            detail=detail,
        )


def _read_key() -> str:
    value = os.environ.get(_KEY_ENV, "").strip()
    if not value:
        raise MissingAPIKey(
            f"{_KEY_ENV} is not set. Live Anthropic runs read that variable and no other key source."
        )
    return value


def _message_text(response: object) -> str:
    """Return visible answer text, skipping thinking blocks.

    Adaptive thinking puts one or more ``thinking`` blocks before the
    ``text`` block. Reading only the first block, or treating a thinking
    trace as the answer, drops or mis-scores the conclusion.
    """
    try:
        blocks = response.content  # type: ignore[attr-defined]
    except AttributeError as exc:
        raise AdapterError(f"Anthropic response had no content: {exc}") from exc
    parts: list[str] = []
    for block in blocks:
        block_type, text = _block_type_and_text(block)
        if block_type in ("thinking", "redacted_thinking"):
            continue
        if block_type not in (None, "text"):
            continue
        if isinstance(text, str) and text.strip():
            parts.append(text.strip())
    return "\n".join(parts).strip()


def _block_type_and_text(block: object) -> tuple[object, object]:
    if isinstance(block, dict):
        return block.get("type"), block.get("text")
    return getattr(block, "type", None), getattr(block, "text", None)
