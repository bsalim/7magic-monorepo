# WhatsApp lead capture via Bird

**Status: partially built.**

- **Outbound team alerts — done.** Both lead paths notify the team over WhatsApp
  (`app/services/whatsapp.py`). Waiting only on the `lead_alert` template being
  approved in Bird; until then every alert fails with `WhatsAppTemplateNotFound`
  and is logged, harmlessly.
- **Inbound capture and the CMS inbox — blocked.** The account's API cannot
  receive WhatsApp at all. Resolve "Open with Bird" below before planning these.

## Goal

Today every WhatsApp CTA on the site is a `wa.me` deep link
(`apps/web/src/lib/whatsapp.ts`). The conversation happens inside WhatsApp on
someone's phone, so the platform never learns that the CTA converted, which page
sent the couple, or which venue they asked about. Contact-form leads are captured
properly; WhatsApp leads are invisible.

Three things were agreed:

1. Capture inbound WhatsApp messages as leads.
2. Notify the team over WhatsApp when any lead arrives.
3. A two-way inbox in the CMS.

Email notifications stay on Resend. Bird carries WhatsApp only.

## What was verified live (2026-08-03)

A real send succeeded, so the account and billing work:

```
message wam_01kz3bkbs1f8qbrvdc5brwffe2
  template  bird_otp (category: authentication)
  from      +13124493047   <- Bird's shared sender, shown as "Bird Authify"
  to        +65XXXXXXXX
  status    accepted -> delivered in ~3s
  cost      USD 0.021
```

Facts established by that test and by reading the shipped SDK:

- **Base URL is `https://us1.platform.bird.com`**, derived from the
  `bk_{region}_{token}` key. Not `api.bird.com` — that host 404s/401s for this
  key, which is what made the first probes fail.
- **The Python SDK is distributed as `messagebird-sdk`; the import package is
  `bird`.** PyPI `bird` is an unrelated signal-processing library.
- **Templates are the only supported WhatsApp content type.** `whatsapp.send()`
  takes `to`, `template`, `language`, `components` — there is no free-form text
  parameter.
- **Bird picks the sender from the template's category.** There is no
  7Magic-owned number involved, and none can be configured.
- **There is no inbound WhatsApp event.** The SDK's full WhatsApp event list is
  `accepted, sent, delivered, read, failed, rejected`. Email by contrast does
  have `email.received`, so the omission is deliberate, not an oversight.

> An earlier note in this investigation claimed Bird's product page documented a
> `whatsapp.received` event. The shipped SDK contradicts it. Trust the SDK.

## The two Bird products

Bird sells two different things under one brand, and the API key only reaches
one of them.

| | Developer API (**account has this**) | CRM / Channels API |
|---|---|---|
| Docs | `bird.com/docs` | `docs.bird.com/api/channels-api` |
| Auth | `bk_{region}_…` API key | `Authorization: AccessKey …` |
| Addressing | none — key implies the sender | workspace UUID + channel UUID |
| Sender | Bird's shared pool | your own migrated WABA number |
| WhatsApp content | templates only | templates *and* free-form in-window |
| Inbound | none | webhook subscriptions |
| Team inbox | none | Inbox app |

Goals 1 and 3 require the CRM / Channels product. Goal 2 works on the developer
API today.

## Design (assuming Channels API access)

Unchanged by the findings above; it just needs the right product underneath.

### Components

- **`app/services/whatsapp.py` — `BirdClient`.** Mirrors `EmailNotifier`: a
  `configured` property, log-and-return-`False` on failure, never raises at the
  caller. A provider outage must cost a notification, never a lead.
- **`app/api/v1/endpoints/webhooks.py`.** Public `POST /api/v1/webhooks/bird`.
  Signature verification is its only gate, so it must read the raw body before
  any parsing.
- **`app/services/conversations.py` — `ConversationService`.** Owns find-or-create
  of the thread, message append, and lead creation on first contact.
- **`LeadService`** gains a Bird call next to each existing Resend call.

### Data model

`whatsapp_conversations` — one row per phone number: `phone_number` (unique),
`contact_name`, `lead_id` → `contact_leads`, `last_message_at`, `unread_count`,
`status`, and `service_window_expires_at`. That last column decides whether the
CMS may send a free-form reply or must fall back to a paid template.

`whatsapp_messages` — `conversation_id`, `bird_message_id` (**unique**),
`direction`, `body`, `media_json`, `status`, `error_json`, `sent_at`. The unique
constraint is the idempotency key: webhook delivery retries must be silent
no-ops.

`contact_leads` needs no schema change — `source='whatsapp'` and attribution in
`metadata_json`.

### Inbound flow

1. Verify the signature; reject stale timestamps.
2. Insert the message keyed on its provider ID. Already present → `200`, done.
3. Upsert the conversation; refresh `last_message_at` and the service window.
4. First message in a thread → create the lead, with attribution.
5. Notify the team (Resend email, plus Bird WhatsApp).

Steps 4 and 5 are strictly downstream of step 2, matching the ordering already
documented in `services/leads.py`.

### Attribution

Match the first inbound message against the `venues` table by name rather than
parsing the pre-filled CTA prose. Venue names are stable; the Indonesian copy in
the CTAs is not. A miss means no venue link, never a failed capture.

### Error handling

A bad signature is `401`. An unhandled event type is logged and returns `200` —
a `4xx` would make the provider retry it for hours. Failed outbound sends are
persisted with `status='failed'` and the provider error so they surface in the
CMS instead of vanishing.

### Testing

Following `apps/api/tests/`, with `httpx` mocked: valid / invalid / stale
signatures; replayed webhook producing no duplicate; first message creating a
lead; second message attaching without creating a second lead; venue attribution
hit and miss; outbound blocked once the service window has closed.

## Production wiring

The webhook URL is **`https://api.7magicwedding.com/api/v1/webhooks/bird`** —
`main.py:49` mounts the v1 router at `/api/v1`, and a `webhooks` router with
`prefix="/webhooks"` lands there.

Nothing to create on the server: `deploy/nginx/sites-available/api.7magicwedding.com.conf:57`
already proxies `location /` to `127.0.0.1:8003`.

One trap: that hostname is behind Cloudflare. An unattended machine-to-machine
POST can be blocked by Bot Fight Mode or a managed WAF rule, producing silent
`403`s that look like the provider failing. Add a skip rule for
`http.request.uri.path eq "/api/v1/webhooks/bird"` before testing.

### Signature scheme

If the account ends up on the developer API, its `whsec_`-prefixed secret is the
Svix convention: HMAC-SHA256 over `{svix-id}.{svix-timestamp}.{raw_body}`, keyed
with the base64 portion after `whsec_`, five-minute tolerance. The SDK wraps this
as `client.webhooks.unwrap(raw_body, headers)`, so we would not hand-roll it.
**Svix does not sign the URL**, so no proxy-header reconstruction is involved.

The Channels API uses a different scheme — `messagebird-signature` over
`timestamp\nurl\nsha256(body)` — which *does* cover the URL. Whichever product
we land on, verify against a real test delivery before trusting either.

## Config already in place

`apps/api/app/core/config.py`, all optional so the API boots unconfigured:

| Setting | Notes |
|---|---|
| `BIRD_API_KEY` | also accepts `BIRD_ACCESS_KEY`; `bk_{region}_…` |
| `BIRD_WORKSPACE_ID` | `ws_`-prefixed, not the UUID the Channels docs describe |
| `BIRD_WHATSAPP_CHANNEL_ID` | empty; only exists once a WABA channel does |
| `BIRD_WEBHOOK_SIGNING_KEY` | `whsec_`-prefixed |
| `WHATSAPP_TEAM_NUMBER` | E.164, must not be the WABA number itself |

Also in `deploy/env/api.env.example`. If the account stays on the developer API,
`BIRD_WHATSAPP_CHANNEL_ID` is dead config and should be dropped.

## Open with Bird

1. Can this account access WhatsApp Business / Channels — our own WABA number
   rather than the shared sender?
2. Is the Inbox app included? This decides the rollout: the agreed plan was for
   the team to work in Bird's inbox after the number migrates and before the CMS
   inbox ships. With no interim inbox, migrating would leave them unable to reply
   at all, and the CMS inbox would have to be built *before* cutover, not after.
3. What is the Indonesian rate card — per-message template pricing plus the
   platform fee? Service replies inside the 24-hour window are free under Meta's
   rules, and every conversation here is customer-initiated, so that window
   should cover most traffic.
4. Does Bird handle migrating an existing number, or is that on us?

## Number migration (independent of the above)

`+62 896 2861 4447` is currently in the consumer WhatsApp app. Moving it to a
WABA is effectively one-way: it stops working in that app, and chat history does
not transfer — export it first if it matters. Customers see no change; the
number stays the same throughout.

The long pole is Meta business verification, not the API work: 3–7 business days
if the business is already verified in Meta Business Manager, two to three weeks
if verification starts from scratch with Indonesian entity documents.
