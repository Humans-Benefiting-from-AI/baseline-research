"""Adapter interface shared by the mock and the three provider clients."""

from __future__ import annotations

from dataclasses import dataclass


class MissingAPIKey(RuntimeError):
    """A live adapter was asked to run without its environment variable set."""


class AdapterError(RuntimeError):
    """The provider SDK is missing or returned a response we cannot read."""


@dataclass(frozen=True)
class Completion:
    """Text returned for one question. ``mock`` is True for the dry-run adapter."""

    text: str
    model: str
    provider: str
    mock: bool = False


class ModelAdapter:
    """One model behind a ``complete`` call.

    Subclasses must not perform network I/O in ``__init__`` or at import
    time. Live subclasses read the API key from the environment only when
    ``complete`` is called.
    """

    provider: str
    model: str

    def complete(self, *, system: str, user: str) -> Completion:
        raise NotImplementedError

    def require_key(self) -> None:
        """Live adapters check the env var before the run starts.

        The mock adapter does not need a key. The default is a no-op so a
        dry-run never touches the environment.
        """
        return None
