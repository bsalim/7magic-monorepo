# Bird as a mail provider, and one HTML layout for every transactional email

**Status: designed, not built.**

Two changes to how 7magic sends mail, in order:

1. **Transport.** Transactional email is hardcoded to Resend in one module.
   Put both providers behind an interface and let `MAIL_PROVIDER` choose, so
   moving to Bird — which already carries WhatsApp — is an env var, not a
   rewrite.
2. **Presentation.** Tour emails go out as bare plain text and lead
   notifications as an inline-styled fragment with no header, footer or
   branding. Give every transactional email one extensible HTML shell.

The two are separable but meet at one point: the provider interface carries
both an HTML body and a plain-text alternative, so the layout has somewhere to
go and the text version never stops shipping.

## Goal

- `MAIL_PROVIDER=bird` sends through Bird; `MAIL_PROVIDER=resend` keeps today's
  behaviour byte for byte. Switching back is one variable and a restart.
- An unconfigured provider — no key, or a key with no resolvable region — boots
  fine and degrades to a logged warning, exactly as Resend does today.
- Every transactional email shares one header/footer/logo shell, and adding a
  new email means writing its body, not another document.
- CMS editors keep their plain-text textareas. They never write HTML.

## Scope

**In.** A provider interface with `ResendMailer` and `BirdMailer` behind it;
config for provider selection and Bird's key; a shared HTML layout module;
the lead notification and both tour emails (guest confirmation, branch alert)
rendered through it; a plain-text alternative on every send.

**Out, and why.**

| Dropped | Reason |
|---|---|
| Fallback chaining (try Bird, fall back to Resend) | Considered and rejected. It doubles the failure surface, makes "which provider sent it" unanswerable from logs, and requires both accounts funded forever. One active provider, chosen at boot. |
| Deleting the Resend path | The key is still in production env and Bird has not yet sent a single production email. Keeping both is what makes the switch reversible; that is the whole point of the interface. |
| The `messagebird-sdk` package | Verified unnecessary: a plain `httpx` POST to `/v1/email/messages` returned `202 accepted` in testing. The app is async throughout and `services/whatsapp.py` already talks to Bird over raw httpx; an SDK would add a dependency, a sync-first client and a second HTTP stack to reach an endpoint that takes six JSON fields. |
| A template engine (Jinja) for email bodies | The CMS templates are plain text with `{placeholder}` tokens, and `domains/events/emails.py` is explicit that an unknown token must render literally rather than raise mid-send. A real engine would reintroduce exactly that failure. |
| Retries and a send queue | Every send here is already best-effort on top of committed data. Retry logic without a durable queue buys little and hides latency in the request path. |
| Per-branch sending domains | One verified sending domain until the business actually needs more; `from` is a single configured address. |

---

## Architecture

```
  callers (unchanged imports)
  ───────────────────────────
  api/v1/public/tour.py ──▶ send_email(to, subject, text, reply_to)
  services/leads.py     ──▶ EmailNotifier.send_lead_notification(...)
                                      │
                                      ▼
                        app/services/email/service.py
                          builds EmailMessage, picks the mailer
                                      │
                     ┌────────────────┴────────────────┐
                     ▼                                 ▼
            resend.py ResendMailer            bird.py BirdMailer
            POST api.resend.com/emails        POST {region}.platform.bird.com
            Authorization: Bearer               /v1/email/messages
                                              Authorization: Bearer
                     │                                 │
                     └────────────────┬────────────────┘
                                      ▼
                              layout.py renders the
                              html both providers send
```

### Module layout

`app/services/email.py` becomes `app/services/email/`. Callers import from
`app.services.email` exactly as they do now — the package `__init__` re-exports
the same three names — so **no call site changes** and the diff stays inside
one directory.

| File | Holds | Must not |
|---|---|---|
| `__init__.py` | Re-exports `send_email`, `EmailNotifier`, `render_lead_email` | Contain logic |
| `base.py` | `EmailMessage` dataclass, `Mailer` protocol | Know about any provider |
| `resend.py` | `ResendMailer` | Know about Bird |
| `bird.py` | `BirdMailer` | Know about Resend |
| `service.py` | `get_mailer()`, `send_email()`, `EmailNotifier` | Build provider payloads |
| `layout.py` | The HTML shell, text→HTML formatting, and `render_lead_email` with its `_row` helper | Perform I/O |

`render_lead_email` and `_row` move out of today's `email.py` into `layout.py`
unchanged in behaviour — they are presentation, and keeping them next to the
shell they now render inside is what stops a second field-table helper being
written later.

The split is what keeps a second provider from being a third branch inside one
function. Each provider owns its payload shape and nothing else; `service.py`
owns the two public behaviours and never sees a wire format.

Articles, venues and showcases stay in the flat `app/services` layout per
CLAUDE.md — this is a directory for one service that grew a second
implementation, not a new domain package.

### The interface

```python
@dataclass(frozen=True)
class EmailMessage:
    to: list[str]
    subject: str
    text: str                    # always present; the alternative part
    html: str | None = None      # None for a text-only send
    reply_to: str | None = None

class Mailer(Protocol):
    @property
    def configured(self) -> bool: ...
    async def send(self, message: EmailMessage) -> None: ...
```

`text` is required rather than optional. A send with no plain-text alternative
is a deliverability problem, and making it non-optional means no future caller
can forget it.

`send` raises on transport failure. Swallowing belongs to the caller, because
the two callers want different things — see below.

### Behaviours that must not change

Three contracts are load-bearing, and each has a caller depending on it:

1. **`send_email()` raises.** `api/v1/public/tour.py:270-286` wraps both calls
   in `try/except` and logs with the registration id. It decides for itself
   that an outage must not fail the request. Making the function swallow would
   silently delete that log line.
2. **`send_lead_notification()` returns a bool and never raises.**
   `services/leads.py` treats `False` as "saved, not notified".
3. **Unconfigured is a warning, not an error.** A dev machine with no key
   posts no live mail, and the API boots regardless. This extends to Bird:
   `MAIL_PROVIDER=bird` with no key logs and no-ops rather than raising at
   import or at boot.

### Configuration

| Setting | Env | Default | Used by |
|---|---|---|---|
| `mail_provider` | `MAIL_PROVIDER` | `resend` | `get_mailer()` |
| `bird_mail_api_key` | `BIRD_MAIL_API_KEY`, falls back to `BIRD_ACCESS_KEY` / `BIRD_API_KEY` | unset | Bird |
| `bird_mail_category` | `BIRD_MAIL_CATEGORY` | `transactional` | Bird |
| `email_logo_url` | `EMAIL_LOGO_URL` | `""` | `layout.py` |

`resend_api_key`, `lead_notification_email` and `lead_notification_from` are
untouched, and `lead_notification_from` is used by **both** providers — Bird
accepts the same RFC 5322 mailbox string. `mail_provider` takes a
`Literal["resend", "bird"]` so a typo fails at boot with a readable Pydantic
error rather than silently sending nothing.

No channel id and no workspace id: the email API is addressed by region alone
(see below). This is the whole config surface — one key and a category.

The separate `BIRD_MAIL_API_KEY` (rather than reusing `BIRD_ACCESS_KEY`) exists
so the mail key can be rotated or scoped without touching WhatsApp; the
fallback means a single-key setup still works with no extra config.

### Bird's send contract

**Verified against the live API, not inferred from documentation.** An earlier
draft of this spec designed against Bird's *Channels* API
(`/workspaces/{ws}/channels/{ch}/messages`, `AccessKey` auth, a
`{username, displayName}` sender). That is a different, more general surface.
Bird has a dedicated Email API, and it is far closer to Resend:

`POST {base}/v1/email/messages`

- **Auth:** `Authorization: Bearer <key>` — the same scheme
  `services/whatsapp.py` already uses.
- **Base URL:** `https://{region}.platform.bird.com`, derived from the
  `bk_{region}_{token}` key prefix. `resolve_base_url()` in
  `services/whatsapp.py` already computes exactly this; reuse it rather than
  writing a second copy.
- **Body:** flat, and near-identical to Resend's —
  `{"from": ..., "to": [...], "subject": ..., "html": ..., "text": ...,
  "reply_to": [...]}`.
- **Addresses** accept a plain string, an RFC 5322 mailbox string
  (`"7Magic Wedding <hello@7magicwedding.com>"`), or `{"email", "name"}`.
  Today's `lead_notification_from` therefore passes through **verbatim**, and
  both providers share the one setting.
- **`reply_to` is a list**, unlike Resend's scalar. `BirdMailer` wraps the
  single value; the shared `EmailMessage` keeps it scalar because that is what
  every caller has.
- **Success is `202`** with a JSON body carrying `id` and `status: accepted`.
  Treat any 2xx as success; anything else is a failure with the body logged,
  truncated, as `whatsapp.py` already does.
- **Category defaults to `marketing`.** The 202 response to an unset send comes
  back `"category":"marketing"`, which is the wrong bucket for a booking
  confirmation and can affect how it is filtered and what unsubscribe handling
  applies. `BirdMailer` sends `category` explicitly, defaulting to
  `transactional`.
- **`configured`** requires the key and a resolvable base URL. Nothing else —
  a malformed key that yields no region is the only other way to be
  unconfigured.

**No channel, no workspace id, and no domain verification needed to test.**
Bird's sandbox sender `onboarding@messagebird.dev` sends immediately on a bare
key; a verified domain is needed only to send *as* `7magicwedding.com`. The
Bird path can therefore be exercised end-to-end before any DNS work, which the
earlier draft assumed was impossible.

---

## The HTML layout

`layout.py` renders one shell every transactional email passes through.

### Constraints that drive the markup

Email clients are not browsers. Outlook renders through Word; Gmail strips
`<style>` blocks; roughly half of clients block remote images until the reader
opts in. So:

- **Tables for layout, not flexbox or grid.** A `<div>`-based layout collapses
  in Outlook.
- **Inline styles only.** No `<style>` block, no classes, no external CSS.
- **One column, max 600px.** The width that survives every client and phone.
- **The email must read correctly with images off.** This is why the logo
  degrades to a styled text wordmark when `EMAIL_LOGO_URL` is unset, rather
  than leaving a broken-image gap where the branding should be.
- **No web fonts.** System font stack, matching `render_lead_email` today.

### Surface

```python
def paragraphs(text: str) -> str:
    """Escape CMS-authored plain text and structure it: blank lines become
    <p>, single newlines become <br>."""

def render_email(
    *,
    heading: str,
    body_html: str,
    preheader: str | None = None,
    footer_note: str | None = None,
) -> str:
    """Wrap a rendered body in the header/footer shell."""
```

`paragraphs()` escapes first and structures second. That ordering is the whole
safety argument: CMS template text and registrant-supplied values both flow
through here, and neither is trusted. Note this is a *different* job from
`core/html.py`, which sanitises an allowlist of tags authors are permitted to
write — here authors write no HTML at all, so escaping everything is correct
and no allowlist is involved.

`preheader` is the hidden line clients show next to the subject in the inbox
list. Left unset, clients scrape whatever text comes first, which is usually
the logo alt text.

### What each email becomes

| Email | Today | After |
|---|---|---|
| Lead notification (`leads.py`) | `render_lead_email` — a bare `<div>` with a field table | The same field table, as a block inside the shell |
| Tour guest confirmation (`domains/events/emails.py`) | plain text only | `paragraphs(text)` in the shell; the original text ships as the alternative |
| Tour branch alert | plain text only | Same |

`render_lead_email` keeps its name and signature and starts returning the
wrapped document, so `EmailNotifier` needs no change beyond passing a `text`
alternative alongside it.

`registration_confirmation()` and `branch_alert()` in
`domains/events/emails.py` return `(subject, text)` today. They keep returning
exactly that; `service.py` does the wrapping. Rendering stays in the domain,
presentation stays in the layout, and the domain module gains no knowledge of
HTML.

---

## Testing

Mirroring `tests/test_whatsapp_notifier.py`, which uses a `RecordingTransport`
to capture the request instead of reaching Bird. No test may perform a live
send.

**Provider selection**
- `MAIL_PROVIDER=resend` posts to `api.resend.com/emails`.
- `MAIL_PROVIDER=bird` posts to `{region}.platform.bird.com/v1/email/messages`,
  with the region taken from the key prefix.
- Both send `Authorization: Bearer`.
- An invalid `MAIL_PROVIDER` fails at settings construction.

**Bird payload**
- `to` is a list; a multi-recipient branch alert produces one entry each.
- HTML sends carry both `html` and `text`; text-only sends omit `html`.
- `reply_to` is wrapped in a list, and the key is absent entirely when unset.
- `from` is passed through verbatim as the configured RFC 5322 string.
- `category` is always present and defaults to `transactional`, never
  Bird's own `marketing` default.
- `202` counts as success. `4xx` returns failure with the body logged.

**The three preserved contracts**
- `send_email()` raises on transport error, under both providers.
- `send_lead_notification()` returns `False` and does not raise on transport
  error, under both providers.
- Unconfigured — including a key whose prefix yields no region — logs a
  warning, sends nothing, and raises nothing.

**Layout**
- `paragraphs()` escapes `<`, `>` and `&` before structuring, so a registrant
  named `<script>` cannot inject markup.
- Blank lines produce separate `<p>`; single newlines produce `<br>`.
- An unknown `{placeholder}` still renders literally, per the existing
  contract in `domains/events/emails.py`.
- With `EMAIL_LOGO_URL` unset the header renders the text wordmark and no
  `<img>`; with it set, an `<img>` with non-empty `alt`.
- Every tour email still produces a non-empty plain-text alternative.

## A note on the WhatsApp module

An earlier draft flagged `services/whatsapp.py:166`'s `Bearer` header as a bug,
on the strength of Bird's Channels API documentation specifying `AccessKey`.
**That was wrong.** Bird's own Python SDK sets `Authorization: Bearer`, and the
live `/v1/email/messages` call accepted it. `whatsapp.py` needs no change, and
`bird.py` uses `Bearer` for the same reason.

Recorded here because the note is the sort of thing a future reader would
otherwise re-derive from the same documentation and reach the same wrong
conclusion.

## Package naming, recorded so nobody repeats it

Bird's PyPI distribution is **`messagebird-sdk`**, but it *imports* as `bird`.
`pip install bird` / `uv add bird` fetches an unrelated signal-processing
project (`github.com/mmoussallam/bird`, v0.1.2), which fails to build with
`ModuleNotFoundError: No module named 'numpy'`. The failure looks like a broken
build environment and is actually the wrong package entirely.

This project needs neither — `bird.py` uses `httpx` — but the trap is worth
one paragraph.

## Open items

- **`EMAIL_LOGO_URL` is unset**, so the header ships as a text wordmark. Paste
  an absolute https URL — `media.7magicwedding.com` already serves the R2
  bucket — and it becomes an image with no code change.
- **Sending as `7magicwedding.com` needs domain verification** in Bird (DKIM,
  SPF, return-path CNAME). Not a blocker: the sandbox sender works today, so
  the code can ship and be tested before the DNS lands.
- **`RESEND_API_KEY` is absent from `apps/api/.env`.** Local email is already a
  silent no-op today; worth knowing when testing that nothing arriving is the
  expected result, not a regression introduced here.
