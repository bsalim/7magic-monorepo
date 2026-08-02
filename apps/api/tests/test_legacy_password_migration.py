"""Legacy PBKDF2 password verification.

Passwords were PBKDF2 before the argon2id migration, but verify_password only
understood argon2 afterwards, so every account created before the switch could
no longer log in. authenticate() already re-hashes on a successful login, so
verifying the old format is the one piece needed to migrate users transparently.
"""

from __future__ import annotations

import base64
import hashlib
import secrets

from app.core.security import (
    hash_password,
    password_needs_rehash,
    verify_password,
)

LEGACY_ITERATIONS = 260_000


def legacy_pbkdf2_hash(password: str) -> str:
    """Reproduces the pre-argon2 format: pbkdf2_sha256$iterations$salt$digest."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, LEGACY_ITERATIONS)
    return "$".join(
        [
            "pbkdf2_sha256",
            str(LEGACY_ITERATIONS),
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        ]
    )


def test_legacy_pbkdf2_password_still_verifies() -> None:
    stored = legacy_pbkdf2_hash("Admin123!")

    assert verify_password("Admin123!", stored) is True


def test_legacy_pbkdf2_rejects_the_wrong_password() -> None:
    stored = legacy_pbkdf2_hash("Admin123!")

    assert verify_password("wrong-password", stored) is False


def test_legacy_hash_is_flagged_for_rehashing() -> None:
    """So authenticate() upgrades the stored hash to argon2 on next login."""
    assert password_needs_rehash(legacy_pbkdf2_hash("Admin123!")) is True


def test_argon2_hash_round_trips_and_needs_no_rehash() -> None:
    stored = hash_password("Admin123!")

    assert verify_password("Admin123!", stored) is True
    assert password_needs_rehash(stored) is False


def test_malformed_hashes_are_rejected_rather_than_raising() -> None:
    for value in ("", "not-a-hash", "pbkdf2_sha256$notanint$a$b", "pbkdf2_sha256$1$2"):
        assert verify_password("Admin123!", value) is False
