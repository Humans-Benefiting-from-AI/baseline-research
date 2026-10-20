"""Build a mock or a live provider adapter.

Dry-run always returns :class:`MockAdapter`. Live construction does not
call the provider. The key check is separate and happens before any
completion, still without opening a socket.
"""

from __future__ import annotations

from harness.adapters.anthropic import AnthropicAdapter
from harness.adapters.base import ModelAdapter
from harness.adapters.google import GoogleAdapter
from harness.adapters.mock import MockAdapter
from harness.adapters.openai import OpenAIAdapter

__all__ = [
    "AnthropicAdapter",
    "GoogleAdapter",
    "MockAdapter",
    "ModelAdapter",
    "OpenAIAdapter",
    "build_adapter",
]


def build_adapter(
    provider: str,
    model: str,
    *,
    dry_run: bool,
    max_tokens: int | None,
    temperature: float | None,
) -> ModelAdapter:
    if dry_run:
        return MockAdapter(provider_label=provider, model=model)
    if provider == "openai":
        return OpenAIAdapter(
            model=model, max_tokens=max_tokens, temperature=temperature
        )
    if provider == "anthropic":
        return AnthropicAdapter(
            model=model, max_tokens=max_tokens, temperature=temperature
        )
    if provider == "google":
        return GoogleAdapter(
            model=model, max_tokens=max_tokens, temperature=temperature
        )
    raise ValueError(f"Unknown provider {provider!r}.")
