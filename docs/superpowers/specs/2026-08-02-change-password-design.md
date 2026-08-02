# Change password from the CMS

**Date:** 2026-08-02
**Status:** Approved

## Problem

There is no way to change an admin password. `auth.py` exposes only `/login`,
`/me` and `/logout`, and the CMS has no account screen. Passwords can only be
set out of band, by `scripts/seed_admin_user.py` or by
`scripts/reset_admin_passwords.py` — which resets *every* admin to the
hardcoded `Admin123` and was written as a pre-launch tool.

## Scope

A signed-in admin changes their own password from the CMS.

Out of scope: editing profile fields (name, email, username), password reset by
email, admin-changes-another-admin's-password, and any user management UI.

## Decisions

| Decision | Choice | Why |
|---|---|---|
| Page contents | Password form only | Smallest surface that closes the gap. Profile editing needs its own endpoint and can come later. |
| Sessions after change | Revoke all others, keep current | Kicks out a stolen session or a forgotten device without signing out the person doing the rotation. |
| Password rule | Minimum 8 characters, no composition rules | Length over character-class rules; forced symbols mostly produce `Admin123!`. |
| Nav placement | Account dropdown only | The sidebar is about content. The sidebar `nav` array is untouched. |
| Legacy PBKDF2 | Not supported in this flow | See below. |

### Why argon2-only verification is safe here

`verify_password` understands both argon2 and the legacy PBKDF2 hashes, but
this flow does not need the legacy branch. Reaching it requires a valid
session, which means the user logged in, and `authenticate_admin_user`
re-hashes to argon2 whenever `password_needs_rehash` is true — which it is for
every PBKDF2 hash, since argon2's `check_needs_rehash` raises `InvalidHashError`
on them. Any legacy hash has therefore already upgraded itself before this
endpoint can be called.

Login keeps its legacy fallback. Removing PBKDF2 globally would permanently
lock out any account still holding such a hash, and the live DB has not been
checked for those.

## API

### `app/schemas/auth.py`

```python
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=1, max_length=255)
```

The bounds are deliberately loose. The 8-character rule is enforced in the
service so the failure is returned through `error_response`. `main.py`
registers a handler for `AuthError` only — there is no
`RequestValidationError` handler — so a pydantic 422 would arrive at the CMS
as a generic `API request failed: 422` with no usable message.

### `app/core/security.py`

```python
def verify_password_argon2(password: str, password_hash: str) -> bool
```

argon2 only, no PBKDF2 branch. `verify_password` is left unchanged.

### `app/services/auth.py`

```python
MIN_PASSWORD_LENGTH = 8

class WeakPasswordError(Exception): ...
class PasswordUnchangedError(Exception): ...

async def change_user_password(
    session: AsyncSession, *, user_id: int, current_password: str, new_password: str
) -> None
```

1. Load the user by id; missing → `InvalidTokenSubjectError`.
2. `verify_password_argon2(current_password, user.password_hash)` false →
   `InvalidCredentialsError`.
3. `len(new_password) < MIN_PASSWORD_LENGTH` → `WeakPasswordError`.
4. `new_password == current_password` → `PasswordUnchangedError`.
5. `user.password_hash = hash_password(new_password)`, commit.

### `app/services/sessions.py`

```python
async def revoke_other_sessions(db: AsyncSession, *, user_id: int, keep_token: str) -> int
```

`DELETE FROM user_sessions WHERE user_id = :user_id AND token_hash != :keep`,
returning the deleted row count.

### `app/api/v1/endpoints/auth.py`

`POST /api/v1/auth/change-password`, depending on `require_admin_user` and also
reading the `Authorization` header directly so `extract_bearer_token` yields the
token to keep.

| Case | Status | Body |
|---|---|---|
| Success | 200 | `{"status": "ok", "revoked_sessions": n}` |
| Wrong current password | 401 | `invalid_credentials` |
| New password under 8 chars | 400 | `weak_password`, `details: {"min_length": 8}` |
| New password same as current | 400 | `password_unchanged` |
| Missing or invalid session | 401 | `missing_token` / `invalid_token` (existing behaviour) |

The password commit happens before revocation. If revocation then failed, the
password would be changed with stale sessions still alive; the opposite order
would sign every device out on a change that subsequently failed.

No rate limiting. The endpoint requires a valid session, so there is no
unauthenticated guessing surface — unlike `/login`, which is throttled by
`LoginRateLimiter`.

## CMS

### `src/routes/settings/profile/+page.server.ts`

`load` redirects to `/login` when `locals.token` is absent, matching
`promotions/+page.server.ts`. The default action reads `current_password`,
`new_password` and `confirm_password`, verifies the two new values match before
calling the API, and maps `ApiRequestError` to `fail(status, { message })`.

### `src/routes/settings/profile/+page.svelte`

A card with three `type="password"` inputs and a submit button, following the
structure of the promotions page. Success shows a sonner toast; failures render
the returned message inline.

### `src/lib/components/AdminShell.svelte`

One `DropdownMenu.Item` linking to `/settings/profile`, placed above the
sign-out form. The `nav` array is not modified.

No cookie work: the current session survives by design, so `cms_session` stays
valid.

## Testing

`apps/api/tests/test_change_password.py` covers:

- success returns 200 and the stored hash actually changed
- wrong current password → 401 `invalid_credentials`
- new password under 8 characters → 400 `weak_password`
- new password identical to current → 400 `password_unchanged`
- no bearer token → 401
- other sessions are deleted while the current token still resolves

The CMS has no test harness — no `*.test.ts` files exist and
`apps/cms/package.json` defines no `test` script. The CMS half is verified with
`pnpm check` and by running the app. Standing up a vitest config for the CMS is
out of scope for this change.
