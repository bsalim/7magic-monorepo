from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

SESSION_TOKEN_BYTES = 32

# Passwords were PBKDF2 before the argon2id migration. Accounts created back then
# still carry these hashes, so verification has to understand them or those users
# can never log in again. authenticate() re-hashes to argon2 on a successful
# login, so each legacy hash upgrades itself the first time it is used.
LEGACY_PBKDF2_ALGORITHM = "pbkdf2_sha256"

_password_hasher = PasswordHasher()

# Verified against when a login email has no account, so response timing does
# not reveal whether an email is registered.
DUMMY_PASSWORD_HASH = _password_hasher.hash("dummy-password-for-timing")


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def _verify_legacy_pbkdf2(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt_raw, digest_raw = password_hash.split("$", 3)
        iterations = int(iterations_raw)
        salt = base64.urlsafe_b64decode(salt_raw.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_raw.encode("ascii"))
    except (ValueError, TypeError):
        return False

    if algorithm != LEGACY_PBKDF2_ALGORITHM:
        return False

    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(candidate, expected)


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith(f"{LEGACY_PBKDF2_ALGORITHM}$"):
        return _verify_legacy_pbkdf2(password, password_hash)

    try:
        return _password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def verify_password_argon2(password: str, password_hash: str) -> bool:
    # Deliberately has no PBKDF2 branch, unlike verify_password. Only a
    # signed-in user reaches this, and logging in already rehashes a legacy
    # hash to argon2, so nothing that gets here can still be PBKDF2.
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    try:
        return _password_hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return True


def generate_session_token() -> str:
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
