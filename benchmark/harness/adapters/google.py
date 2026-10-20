"""Google Gemini adapter (``google-genai``).

The model id is an argument. The key is read from ``GOOGLE_API_KEY`` at
call time. Temperature is omitted unless the caller sets it: Gemini 3.6
and later reject a custom temperature.
"""

from __future__ import annotations

import os

from harness.adapters.base import AdapterError, Completion, MissingAPIKey, ModelAdapter
from harness.models import API_KEY_ENV

_PROVIDER = "google"
_KEY_ENV = API_KEY_ENV[_PROVIDER]


class GoogleAdapter(ModelAdapter):
    def __init__(
        self,
        *,
        model: str,
        max_tokens: int | None = 256,
        temperature: float | None = None,
    ) -> None:
        if not model or not model.strip():
            raise ValueError("Google model id is required.")
        self.provider = _PROVIDER
        self.model = model.strip()
        self.max_tokens = max_tokens
        self.temperature = temperature

    def require_key(self) -> None:
        _read_key()

    def complete(self, *, system: str, user: str) -> Completion:
        api_key = _read_key()
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise AdapterError(
                "The google-genai package is not installed. "
                "Install benchmark/requirements.txt before a live Gemini run."
            ) from exc

        client = genai.Client(api_key=api_key)
        config_kwargs: dict = {
            "system_instruction": system,
        }
        if self.max_tokens is not None:
            config_kwargs["max_output_tokens"] = self.max_tokens
        if self.temperature is not None:
            config_kwargs["temperature"] = self.temperature

        response = client.models.generate_content(
            model=self.model,
            contents=user,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        text = getattr(response, "text", None) or ""
        return Completion(
            text=str(text).strip(),
            model=self.model,
            provider=self.provider,
            mock=False,
        )


def _read_key() -> str:
    value = os.environ.get(_KEY_ENV, "").strip()
    if not value:
        raise MissingAPIKey(
            f"{_KEY_ENV} is not set. Live Gemini runs read that variable and no other key source."
        )
    return value
