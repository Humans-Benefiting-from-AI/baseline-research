"""Provider names, credential env vars, and overridable model ids.

The first results file was produced with ``gpt-4o`` and a Claude 3.5
Sonnet snapshot. Those ids are not the defaults here. Pass them (or any
other id) with the CLI flags or the ``*_MODEL`` environment variables.
"""

from __future__ import annotations

import os

PROVIDERS = ("openai", "anthropic", "google")

# Credential variables. Adapters read these and nothing else.
API_KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
}

# Optional overrides for the model id. CLI flags win over these.
MODEL_ENV = {
    "openai": "OPENAI_MODEL",
    "anthropic": "ANTHROPIC_MODEL",
    "google": "GOOGLE_MODEL",
}

# Current Chat Completions / Messages / Gemini ids as of October 2026.
# They are defaults only. Every call site takes the resolved id as an argument.
DEFAULT_MODEL_IDS = {
    "openai": "gpt-5.6-sol",
    "anthropic": "claude-sonnet-5-5",
    "google": "gemini-3.8-flash",
}


class ConfigError(ValueError):
    """A CLI or environment setting cannot be used."""


def resolve_model_id(provider: str, explicit: str | None) -> str:
    """CLI value, then ``*_MODEL`` env var, then the packaged default."""
    if provider not in PROVIDERS:
        raise ConfigError(
            f"Unknown provider {provider!r}. Choose from: {', '.join(PROVIDERS)}."
        )
    if explicit is not None and explicit.strip():
        return explicit.strip()
    from_env = os.environ.get(MODEL_ENV[provider], "").strip()
    if from_env:
        return from_env
    return DEFAULT_MODEL_IDS[provider]


def parse_providers(raw: str) -> list[str]:
    """Parse a comma-separated provider list. Default is all three."""
    names = [part.strip().lower() for part in raw.split(",") if part.strip()]
    if not names:
        raise ConfigError("At least one provider is required.")
    unknown = [name for name in names if name not in PROVIDERS]
    if unknown:
        raise ConfigError(
            f"Unknown provider(s): {', '.join(unknown)}. "
            f"Choose from: {', '.join(PROVIDERS)}."
        )
    # Preserve order, drop duplicates.
    seen: list[str] = []
    for name in names:
        if name not in seen:
            seen.append(name)
    return seen
