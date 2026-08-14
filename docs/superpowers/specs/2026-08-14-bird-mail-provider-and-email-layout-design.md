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
- An unconfigured provider — no key, or Bird with no channel id — boots fine
  and degrades to a logged warning, exactly as Resend does today.
- Every transactional email shares one header/footer/logo shell, and adding a
  new email means writing its body, not another document.
- CMS editors keep their plain-text textareas. They never write HTML.

## Scope

**In.** A provider interface with `ResendMailer` and `BirdMailer` behind it;
config for provider selection and Bird's channel; a shared HTML layout module;
the lead notification and both tour emails (guest confirmation, branch alert)
rendered through it; a plain-text alternative on every send.

**Out, and why.**

| Dropped | Reason |
|---|---|
| Fallback chaining (try Bird, fall back to Resend) | Considered and rejected. It doubles the failure surface, makes "which provider sent it" unanswerable from logs, and requires both accounts funded forever. One active provider, chosen at boot. |
| Deleting the Resend path | The key is still in production env and Bird's channel is not verified yet. Keeping both is what makes the switch reversible; that is the whole point of the interface. |
| Fixing `services/whatsapp.py`'s `Bearer` header | It is a real discrepancy with Bird's documented `AccessKey` (see "A note on the WhatsApp module"), but it is a WhatsApp bug on an unexercised path. Folding it into a mail feature mixes two unrelated risks. Tracked separately. |
| A template engine (Jinja) for email bodies | The CMS templates are plain text with `{placeholder}` tokens, and `domains/events/emails.py` is explicit that an unknown token must render literally rather than raise mid-send. A real engine would reintroduce exactly that failure. |
| Retries and a send queue | Every send here is already best-effort on top of committed data. Retry logic without a durable queue buys little and hides latency in the request path. |
| Per-branch sending domains | Bird binds one verified domain per channel. One channel until the business actually needs more. |

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
            POST api.resend.com/emails        POST {base}/workspaces/{ws}
            Authorization: Bearer             /channels/{ch}/messages
                                              Authorization: AccessKey
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
   `MAIL_PROVIDER=bird` with no channel id logs and no-ops rather than raising
   at import or at boot.

### Configuration

| Setting | Env | Default | Used by |
|---|---|---|---|
| `mail_provider` | `MAIL_PROVIDER` | `resend` | `get_mailer()` |
| `bird_mail_api_key` | `BIRD_MAIL_API_KEY`, falls back to `BIRD_ACCESS_KEY` / `BIRD_API_KEY` | unset | Bird |
| `bird_email_channel_id` | `BIRD_EMAIL_CHANNEL_ID` | unset | Bird |
| `mail_from_username` | `MAIL_FROM_USERNAME` | `noreply` | Bird |
| `mail_from_display_name` | `MAIL_FROM_DISPLAY_NAME` | `7Magic Wedding` | Bird |
| `email_logo_url` | `EMAIL_LOGO_URL` | `""` | `layout.py` |

`resend_api_key`, `lead_notification_email` and `lead_notification_from` are
untouched. `mail_provider` takes a `Literal["resend", "bird"]` so a typo fails
at boot with a readable Pydantic error rather than silently sending nothing.

The separate `BIRD_MAIL_API_KEY` (rather than reusing `BIRD_ACCESS_KEY`) exists
so the mail key can be rotated or scoped without touching WhatsApp; the
fallback means a single-key setup still works with no extra config.

### Bird's send contract

`POST {base}/workspaces/{workspaceId}/channels/{channelId}/messages`

- **Auth:** `Authorization: AccessKey <key>`.
- **Base URL:** reuse `resolve_base_url()` from `services/whatsapp.py`, which
  derives the region host from the `bk_{region}_{token}` key prefix. Bird's
  quickstart documents `https://api.bird.com`; both resolve, and reusing the
  existing helper keeps one rule for one vendor.
- **Body:** `{"receiver": {"contacts": [{"identifierKey": "emailaddress",
  "identifierValue": ...}]}, "body": {"type": "html", "html": {"html": ...,
  "text": ..., "metadata": {...}}}}`. Type `text` with `body.text.text` when
  there is no HTML.
- **From:** `metadata.emailFrom` takes `{username, displayName}` — the local
  part and display name only, because the domain is fixed by the verified
  channel. Today's `lead_notification_from` is a full RFC address
  (`7Magic Website <onboarding@resend.dev>`) and **cannot be passed through**;
  hence the two `MAIL_FROM_*` settings.
- **Reply-to:** `metadata.headers["reply-to"]`, not a top-level field.
- **Success is `202`,** not `200` — accepted for processing. Treat any 2xx as
  success; anything else is a failure with the body logged, truncated, as
  `whatsapp.py` already does.
- **`configured`** requires key *and* workspace id *and* channel id *and* a
  resolvable base URL. Any one missing means there is no URL to POST to.

Bird also needs a channel created in the dashboard against a verified sending
domain (DKIM, SPF and a return-path CNAME). That is account setup, not code;
the code's job is to no-op cleanly until the channel id appears.

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
- `MAIL_PROVIDER=resend` posts to Resend's endpoint with a `Bearer` header.
- `MAIL_PROVIDER=bird` posts to the workspace/channel path with an `AccessKey`
  header.
- An invalid `MAIL_PROVIDER` fails at settings construction.

**Bird payload**
- Recipients land in `receiver.contacts[]` with `identifierKey: emailaddress`;
  a multi-recipient branch alert produces one contact each.
- HTML sends carry both `body.html.html` and `body.html.text`.
- `reply_to` lands in `metadata.headers["reply-to"]`, and is absent when unset.
- `emailFrom` carries username and display name, never a full RFC address.
- `202` counts as success. `4xx` returns failure with the body logged.

**The three preserved contracts**
- `send_email()` raises on transport error, under both providers.
- `send_lead_notification()` returns `False` and does not raise on transport
  error, under both providers.
- Unconfigured — and Bird-with-no-channel-id specifically — logs a warning,
  sends nothing, and raises nothing.

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

`services/whatsapp.py:166` sends `Authorization: Bearer`, while Bird's
documentation specifies `AccessKey` for the same platform. `BIRD_WHATSAPP_CHANNEL_ID`
is blank in `apps/api/.env`, so that path has likely never completed a live
send and the discrepancy would not have surfaced.

This spec deliberately does not change it. `bird.py` uses `AccessKey` as
documented; whether WhatsApp needs the same correction is a separate question
answered by one live send, not by this feature.

## Open items

- **`BIRD_EMAIL_CHANNEL_ID` does not exist yet.** The channel must be created
  in Bird against a verified domain. Until then `MAIL_PROVIDER` stays `resend`
  and the Bird path is exercised only by tests.
- **`EMAIL_LOGO_URL` is unset**, so the header ships as a text wordmark. Paste
  an absolute https URL — `media.7magicwedding.com` already serves the R2
  bucket — and it becomes an image with no code change.
- **`RESEND_API_KEY` is absent from `apps/api/.env`.** Local email is already a
  silent no-op today; worth knowing when testing that nothing arriving is the
  expected result, not a regression introduced here.
