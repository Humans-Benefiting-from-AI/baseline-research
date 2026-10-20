from __future__ import annotations

import pytest

from harness.adapters import (
    AnthropicAdapter,
    GoogleAdapter,
    MockAdapter,
    OpenAIAdapter,
    build_adapter,
)
from harness.adapters.base import MissingAPIKey
from harness.models import DEFAULT_MODEL_IDS, ConfigError, parse_providers, resolve_model_id


def test_dry_run_factory_returns_a_mock_for_each_provider():
    for provider in ("openai", "anthropic", "google"):
        adapter = build_adapter(
            provider,
            model="configured-id",
            dry_run=True,
            max_tokens=256,
            temperature=None,
        )
        assert isinstance(adapter, MockAdapter)
        assert adapter.model == "configured-id"
        assert adapter.provider == provider


def test_live_factory_builds_each_adapter_without_calling_it():
    built = {
        "openai": OpenAIAdapter,
        "anthropic": AnthropicAdapter,
        "google": GoogleAdapter,
    }
    for provider, cls in built.items():
        adapter = build_adapter(
            provider,
            model=f"custom-{provider}",
            dry_run=False,
            max_tokens=128,
            temperature=None,
        )
        assert isinstance(adapter, cls)
        assert adapter.model == f"custom-{provider}"


def test_model_id_resolution_prefers_cli_then_env_then_default(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "from-env")
    assert resolve_model_id("openai", "from-cli") == "from-cli"
    assert resolve_model_id("openai", None) == "from-env"
    monkeypatch.delenv("OPENAI_MODEL")
    assert resolve_model_id("openai", None) == DEFAULT_MODEL_IDS["openai"]
    assert resolve_model_id("anthropic", None) == DEFAULT_MODEL_IDS["anthropic"]
    assert resolve_model_id("google", None) == DEFAULT_MODEL_IDS["google"]


def test_defaults_are_not_the_historical_snapshots():
    assert "gpt-4o" not in DEFAULT_MODEL_IDS.values()
    assert not any("claude-3-5" in model for model in DEFAULT_MODEL_IDS.values())


def test_provider_list_parses_and_rejects_unknown_names():
    assert parse_providers("google, openai, openai") == ["google", "openai"]
    with pytest.raises(ConfigError):
        parse_providers("llama")


@pytest.mark.parametrize(
    "adapter_cls, env_name",
    [
        (OpenAIAdapter, "OPENAI_API_KEY"),
        (AnthropicAdapter, "ANTHROPIC_API_KEY"),
        (GoogleAdapter, "GOOGLE_API_KEY"),
    ],
)
def test_live_adapter_refuses_to_start_without_its_env_key(monkeypatch, adapter_cls, env_name):
    monkeypatch.delenv(env_name, raising=False)
    adapter = adapter_cls(model="some-model-id")
    with pytest.raises(MissingAPIKey, match=env_name):
        adapter.require_key()
    with pytest.raises(MissingAPIKey, match=env_name):
        adapter.complete(system="system", user="user")
