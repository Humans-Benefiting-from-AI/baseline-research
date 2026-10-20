"""Retry a provider call on 503 and disconnect errors.

The first live Gemini run failed 8 of 10 calls with HTTP 503 (high demand).
Each call is tried once, then up to two more times. The waits are 1 second
and then 2 seconds. Other failures are not retried.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import TypeVar

from harness.adapters.base import AdapterError, MissingAPIKey

MAX_RETRIES = 2
BACKOFF_SECONDS = (1.0, 2.0)

T = TypeVar("T")

_DISCONNECT_MARKERS = (
    "disconnect",
    "connection reset",
    "connection aborted",
    "remoteprotocolerror",
    "server disconnected",
    "apiconnectionerror",
    "connecterror",
    "broken pipe",
)


def is_retryable(exc: BaseException) -> bool:
    """True for HTTP 503 and for dropped connections. Not for other errors."""
    if isinstance(exc, (MissingAPIKey, AdapterError)):
        return False
    status = _status_code(exc)
    if status == 503:
        return True
    text = f"{type(exc).__name__} {exc}".lower()
    if re.search(r"\b503\b", text):
        return True
    return any(marker in text for marker in _DISCONNECT_MARKERS)


def call_with_retry(
    fn: Callable[[], T],
    *,
    sleep: Callable[[float], None],
    max_retries: int = MAX_RETRIES,
) -> T:
    """Call ``fn``. On a retryable error, wait and try again.

    ``max_retries`` is the number of extra attempts after the first call.
    The exception from the last attempt propagates.
    """
    if max_retries < 0:
        raise ValueError("max_retries cannot be negative.")
    attempt = 0
    while True:
        try:
            return fn()
        except MissingAPIKey:
            raise
        except Exception as exc:
            if attempt >= max_retries or not is_retryable(exc):
                raise
            delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
            sleep(delay)
            attempt += 1


def _status_code(exc: BaseException) -> int | None:
    for attr in ("status_code", "status", "code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
    response = getattr(exc, "response", None)
    if response is None:
        return None
    value = getattr(response, "status_code", None)
    if isinstance(value, int):
        return value
    return None
