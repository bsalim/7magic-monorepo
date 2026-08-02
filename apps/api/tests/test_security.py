from __future__ import annotations

from argon2 import PasswordHasher

from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    password_needs_rehash,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    password_hash = hash_password("Admin123")

    assert password_hash.startswith("$argon2id$")
    assert verify_password("Admin123", password_hash)
    assert not verify_password("wrong", password_hash)


def test_verify_password_rejects_malformed_hash() -> None:
    assert not verify_password("anything", "not-a-hash")
    assert not verify_password("anything", "")


def test_password_needs_rehash_detects_weak_parameters() -> None:
    weak_hash = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1).hash("pw")

    assert password_needs_rehash(weak_hash)
    assert not password_needs_rehash(hash_password("pw"))
    assert password_needs_rehash("not-a-hash")


def test_session_tokens_are_unique_and_hash_to_hex_sha256() -> None:
    token_a = generate_session_token()
    token_b = generate_session_token()

    assert token_a != token_b
    assert len(token_a) >= 43
    assert hash_session_token(token_a) == hash_session_token(token_a)
    assert hash_session_token(token_a) != hash_session_token(token_b)
    assert len(hash_session_token(token_a)) == 64
    assert all(c in "0123456789abcdef" for c in hash_session_token(token_a))
