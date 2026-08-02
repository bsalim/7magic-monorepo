# Session Auth Design — Django-style DB Sessions + Argon2

**Date:** 2026-06-12
**Status:** Approved
**Scope:** `apps/api` (FastAPI) and `apps/cms` (SvelteKit). The public web app is unaffected.

## Goal

Replace the hand-rolled JWT bearer auth with opaque, revocable, server-side database
sessions (Django's session model), and replace PBKDF2 password hashing with argon2id.

This removes the token signing secret from the system entirely (closing the
`dev-change-me` default-secret vulnerability), makes logout a real revocation, and
upgrades password hashing to the current OWASP-preferred algorithm.

## Decisions (validated with the user)

| Decision | Choice |
|---|---|
| Existing PBKDF2 hashes | Pre-launch: reset the DB; seed script sets every admin password to argon2(`Admin123`). No PBKDF2 compatibility kept. |
| Session expiry | Sliding 14 days of inactivity; extension throttled to at most once per hour. |
| Cookie ownership | Unchanged: the CMS server stores the token in its httpOnly `cms_session` cookie and forwards it as a Bearer header. The API never sets cookies. |
| Token storage | DB stores only `sha256(token)`. The raw token is returned once at login and never persisted. |

## Architecture

### Removed

- All JWT code in `apps/api/app/core/security.py` (`sign_auth_token`,
  `decode_auth_token`, base64url helpers, `TOKEN_ALGORITHM`).
- All PBKDF2 code (`hash_password`/`verify_password` PBKDF2 implementation and
  constants).
- `Settings.auth_token_secret` and `Settings.auth_token_ttl_seconds`, plus
  `AUTH_TOKEN_SECRET`/`AUTH_TOKEN_TTL_SECONDS` in `.env.example`.
- The unused `RefreshToken` model in `apps/api/app/models/user.py` and its
  `refresh_tokens` table (dead weight from the initial schema; dropped in the same
  migration).

### Added

- Dependency: `argon2-cffi` in `apps/api/pyproject.toml`.
- `apps/api/app/core/security.py` (rewritten): argon2id `hash_password(password)`,
  `verify_password(password, password_hash)`, and `password_needs_rehash(password_hash)`
  using `argon2.PasswordHasher` with library defaults (argon2id, 64 MiB, time_cost=3,
  parallelism=4). Also `hash_session_token(token) -> str` returning the hex sha256.
- `apps/api/app/models/session.py`: `Session` model (table `sessions`).
- `apps/api/app/services/sessions.py`: session lifecycle (create / resolve+slide /
  revoke / lazy-delete expired).
- `Settings.session_ttl_seconds` (default `60 * 60 * 24 * 14`) and a module constant
  `SESSION_REFRESH_INTERVAL_SECONDS = 3600` for the sliding-window throttle.
- Alembic migration: create `sessions`, drop `refresh_tokens`.
- Seed/reset script in `apps/api/scripts/` that sets every user holding the `admin`
  role to argon2(`Admin123`).

## Data model

```
sessions
  id            uuid PK (default uuid4)
  token_hash    char(64) NOT NULL UNIQUE   -- hex sha256 of the raw token
  user_id       int NOT NULL FK users.id ON DELETE CASCADE
  created_at    timestamptz NOT NULL
  last_seen_at  timestamptz NOT NULL
  expires_at    timestamptz NOT NULL (indexed)
```

Raw token: `secrets.token_urlsafe(32)` (256 bits, 43 chars). It travels:
API login response → CMS `cms_session` httpOnly cookie → Bearer header on
CMS→API requests.

## Request flows

### Login — `POST /api/v1/auth/login`

1. Look up user by normalized email; verify password with argon2
   (`InvalidCredentialsError` on mismatch, as today). When the user does not exist,
   verify against a static dummy argon2 hash so response timing does not reveal
   whether the email exists.
2. Existing checks unchanged: active, admin role.
3. If `password_needs_rehash`, re-hash and persist (future-proofing for parameter bumps).
4. Create session row: `expires_at = now + session_ttl_seconds`.
5. Response shape unchanged: `{access_token: <raw token>, token_type: "bearer",
   expires_in: <session_ttl_seconds>, user: {...}}`. The CMS login action therefore
   needs no changes.

### Authenticated requests — `require_admin_user` and `GET /me`

1. Extract bearer token (unchanged `extract_bearer_token`).
2. `resolve_session(session_db, token)`: look up by `sha256(token)`.
   - Not found → 401 `invalid_token`.
   - `expires_at < now` → delete the row, 401 `invalid_token` (lazy cleanup).
   - Else, if `last_seen_at` is older than `SESSION_REFRESH_INTERVAL_SECONDS`:
     set `last_seen_at = now`, `expires_at = now + session_ttl_seconds` (sliding
     window, throttled to one write per hour per session).
3. Load the user and re-check active + admin role exactly as today
   (`resolve_admin_token_user` adapted to take a user id instead of JWT claims).
   Error codes unchanged.

### Logout — `POST /api/v1/auth/logout`

Becomes a real revocation: requires the bearer token, deletes the matching session
row, returns `{"status": "ok"}`. Unknown/expired token still returns ok (idempotent).
The CMS logout route already calls this with the token — no CMS change.

### CMS changes (the only one)

`apps/cms/src/hooks.server.ts`: after `/me` succeeds, re-set the `cms_session`
cookie with the same value and a fresh `maxAge` so the browser cookie slides along
with the server-side session. Login, logout, layout guard, and cookie options
(httpOnly, SameSite=lax, secure outside dev) are untouched.

## Error handling

Error contract is unchanged: `missing_token`/`invalid_token` → 401,
`inactive_user`/`admin_required` → 403, same envelope via `error_response`. Expired
sessions are indistinguishable from invalid ones in responses (both `invalid_token`),
matching current behavior. Cleanup of expired rows is lazy (on lookup); no background
job pre-launch.

## Seeding / reset

Script `apps/api/scripts/reset_admin_passwords.py` (run manually, pre-launch only):
sets `password_hash = argon2("Admin123")` for every user with the `admin` role and
deletes all rows in `sessions`. The live DB is Postgres; the script uses the
configured `DATABASE_URL`.

## Testing

Rewrite `apps/api/tests/test_auth_contracts.py`:

- Login → `/me` → logout round-trip with an argon2-seeded admin.
- Logout invalidates the token (subsequent `/me` → 401 `invalid_token`).
- Expired session → 401 and the row is deleted.
- Sliding window: a request with `last_seen_at` older than 1 hour pushes
  `expires_at` forward; a fresh session does not write.
- Carried over: bad password → 401, non-admin → 403, inactive → 403,
  admin-role-removed mid-session → 403.
- Unit tests for `hash_password`/`verify_password` round-trip and
  `password_needs_rehash` against a hash made with weaker parameters.

## Out of scope (follow-ups)

- Login rate limiting / brute-force lockout (still recommended from the security
  assessment).
- "Log out all devices" / session listing UI.
- Background job for purging expired sessions (lazy delete suffices pre-launch).
