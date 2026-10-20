"""OpenAI Chat Completions adapter.

The model id is an argument. The historical ``gpt-4o`` run is selected by
passing that id, not by hardcoding it here. The key is read from
``OPENAI_API_KEY`` at call time.
"""

from __future__ import annotations

import os

from harness.adapters.base import AdapterError, Completion, MissingAPIKey, ModelAdapter
from harness.models import API_KEY_ENV, DEFAULT_MAX_TOKENS

_PROVIDER = "openai"
_KEY_ENV = API_KEY_ENV[_PROVIDER]


class OpenAIAdapter(ModelAdapter):
    def __init__(
        self,
        *,
        model: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> None:
        if not model or not model.strip():
            raise ValueError("OpenAI model id is required.")
        self.provider = _PROVIDER
        self.model = model.strip()
        self.max_tokens = DEFAULT_MAX_TOKENS if max_tokens is None else max_tokens
        self.temperature = temperature

    def require_key(self) -> None:
        _read_key()

    def complete(self, *, system: str, user: str) -> Completion:
        api_key = _read_key()
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AdapterError(
                "The openai package is not installed. "
                "Install benchmark/requirements.txt before a live run."
            ) from exc

        client = OpenAI(api_key=api_key)
        kwargs: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        # Newer model ids expect max_completion_tokens. Temperature is omitted
        # unless the caller sets it, because several current GPT models reject
        # a hardcoded temperature.
        if self.max_tokens is not None:
            kwargs["max_completion_tokens"] = self.max_tokens
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature

        response = client.chat.completions.create(**kwargs)
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
            f"{_KEY_ENV} is not set. Live OpenAI runs read that variable and no other key source."
        )
    return value


def _message_text(response: object) -> str:
    try:
        content = response.choices[0].message.content  # type: ignore[attr-defined]
    except (AttributeError, IndexError, TypeError) as exc:
        raise AdapterError(f"OpenAI response had no message content: {exc}") from exc
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
            continue
        text = getattr(block, "text", None)
        if text is None and isinstance(block, dict):
            text = block.get("text")
        if text:
            parts.append(str(text))
    return "\n".join(parts).strip()
