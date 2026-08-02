from __future__ import annotations

import time
from collections import deque
from functools import lru_cache

from app.core.config import get_settings


class LoginRateLimiter:
    """Sliding-window limiter for failed login attempts.

    In-memory and per-process: counts reset on restart and are not shared
    across workers. Sufficient while the API runs as a single process.
    """

    def __init__(self, *, max_attempts: int, window_seconds: int) -> None:
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._failures: dict[str, deque[float]] = {}

    def is_blocked(self, key: str, *, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        failures = self._failures.get(key)
        if failures is None:
            return False
        self._trim(failures, now)
        if not failures:
            del self._failures[key]
            return False
        return len(failures) >= self._max_attempts

    def record_failure(self, key: str, *, now: float | None = None) -> None:
        now = time.monotonic() if now is None else now
        failures = self._failures.setdefault(key, deque())
        self._trim(failures, now)
        failures.append(now)

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)

    def clear(self) -> None:
        self._failures.clear()

    def _trim(self, failures: deque[float], now: float) -> None:
        cutoff = now - self._window_seconds
        while failures and failures[0] <= cutoff:
            failures.popleft()


@lru_cache
def get_login_rate_limiter() -> LoginRateLimiter:
    settings = get_settings()
    return LoginRateLimiter(
        max_attempts=settings.login_max_attempts,
        window_seconds=settings.login_window_seconds,
    )
