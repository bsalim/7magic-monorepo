from __future__ import annotations

from app.core.rate_limit import LoginRateLimiter


def test_blocks_key_after_max_failures_within_window() -> None:
    limiter = LoginRateLimiter(max_attempts=3, window_seconds=900)

    assert limiter.is_blocked("1.2.3.4:admin@example.com", now=0.0) is False
    limiter.record_failure("1.2.3.4:admin@example.com", now=0.0)
    limiter.record_failure("1.2.3.4:admin@example.com", now=1.0)
    assert limiter.is_blocked("1.2.3.4:admin@example.com", now=2.0) is False
    limiter.record_failure("1.2.3.4:admin@example.com", now=2.0)

    assert limiter.is_blocked("1.2.3.4:admin@example.com", now=3.0) is True


def test_failures_outside_window_do_not_count() -> None:
    limiter = LoginRateLimiter(max_attempts=2, window_seconds=100)

    limiter.record_failure("key", now=0.0)
    limiter.record_failure("key", now=1.0)
    assert limiter.is_blocked("key", now=2.0) is True

    assert limiter.is_blocked("key", now=101.0) is False


def test_keys_are_tracked_independently() -> None:
    limiter = LoginRateLimiter(max_attempts=1, window_seconds=100)

    limiter.record_failure("blocked-key", now=0.0)

    assert limiter.is_blocked("blocked-key", now=1.0) is True
    assert limiter.is_blocked("other-key", now=1.0) is False


def test_reset_clears_failures_for_key() -> None:
    limiter = LoginRateLimiter(max_attempts=1, window_seconds=100)

    limiter.record_failure("key", now=0.0)
    assert limiter.is_blocked("key", now=1.0) is True

    limiter.reset("key")

    assert limiter.is_blocked("key", now=1.0) is False


def test_clear_removes_all_state() -> None:
    limiter = LoginRateLimiter(max_attempts=1, window_seconds=100)

    limiter.record_failure("a", now=0.0)
    limiter.record_failure("b", now=0.0)

    limiter.clear()

    assert limiter.is_blocked("a", now=1.0) is False
    assert limiter.is_blocked("b", now=1.0) is False
