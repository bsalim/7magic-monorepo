# Branches, events, and Book a Tour

**Status: designed, not built.**

Port the branch, event and event-registration modules from the Aire Wellness
platform (`../airewellness-platform`) into 7magic, adapted to a single-company,
multi-branch business, and use them to ship a public **Book a Tour** flow: a
couple picks a 7Magic branch, books a visit, and the branch's team is notified.

This is a *port*, not a copy. Aire is a multi-tenant Postgres SaaS with UUID keys
and a booking/payments engine. 7magic is one company, int keys, SQLite in dev.
The parts of Aire that exist only to serve tenancy or bookings are deliberately
dropped — this spec is explicit about each one, so a future reader does not
"restore" something that was removed on purpose.

## Goal

Three outcomes, in priority order:

1. **7magic learns about branches.** Today the codebase assumes one location.
   The business now runs several, and one admin oversees all of them.
2. **A couple can book a tour of a specific branch** from the public site, and
   that branch's team hears about it immediately.
3. **The admin surface does not repeat Aire's mistake.** Aire's
   `apps/api/app/api/v1/admin/resources.py` reached **7,842 lines** holding
   services, staff, members, bookings and dashboards in one module. The
   structural rules in this spec exist to make that outcome impossible here.

## Scope

**In.** Branch CRUD with per-branch settings, opening hours and closures. Events
scoped to a branch, their registrations (including extra guests), attendance
marking, CSV export, and the three per-event email templates. Branch-scoped
permissions on every admin route. The public `/tour` pages, the registration
endpoint, the guest confirmation email, and the branch notification.

**Out, and why.**

| Dropped | Reason |
|---|---|
| `organizations` / `organization_settings` tables, `organization_id` on every row | 7magic is one company. Tenancy plumbing costs a join and a scoping bug on every query, and buys nothing until 7Magic franchises. The branch layer is the useful half. |
| Aire's `_current_organization_id` ContextVar | Only exists to carry the tenant through a 7,842-line module. With no tenant and small routers, an explicit dependency argument is clearer and testable. |
| ~22 of Aire's 30 `branch_settings` columns | GST rates, deposit policy, cash-register variance thresholds, booking cutoffs, slot intervals. 7magic has no bookings, no payments and no register. |
| A branch switcher in the CMS header | Decided against: branch is a **column and a filter** on every list, not ambient state. See "CMS surface". |
| Aire's `AdminUser.branch_id` "home branch" column | Redundant here. Permission rows already answer "which branches?"; a second, sometimes-disagreeing source of truth is a bug waiting to happen. |

---

## Architecture

```
apps/web (public)                     apps/cms (admin)
  /tour            branch picker        /branches        list + filter
  /tour/[slug]     tour form            /branches/[id]   settings, hours, closures
       |                                /events          list + branch filter
       |                                /events/[id]     detail + registrations
       v                                      |
  POST /api/v1/public/tour/...                v
                                  GET/POST/PATCH /api/v1/admin/...
       \                                      /
        \                                    /
         v                                  v
        app/domains/branches/       app/domains/events/
          models schemas service      models schemas service emails sanitize
                        \              /
                         v            v
                     Postgres (prod) / SQLite (dev)
```

### Module layout, and the rule that keeps it thin

New code follows Aire's *good* pattern — domain packages — rather than 7magic's
current flat `models/ services/ schemas/`. Two conventions will coexist: the
existing article/venue/showcase code stays where it is. That is a deliberate
trade. Branches and events are cohesive feature slices with their own emails,
sanitizer and permission rules; splitting one feature across four top-level
directories is what makes a codebase hard to navigate later.

```
app/domains/branches/{__init__,models,schemas,service}.py
app/domains/events/{__init__,models,schemas,service,emails,sanitize}.py

app/api/v1/admin/_shared.py             envelopes, iso helpers, branch-scope dependency
app/api/v1/admin/branches.py            branch CRUD, settings, hours, closures
app/api/v1/admin/events.py              event CRUD only
app/api/v1/admin/event_registrations.py list, create, update, attendance, export
app/api/v1/admin/event_emails.py        templates and preview
app/api/v1/public/tour.py               branch list, event read, register
```

**The rule, to be written into `CLAUDE.md`:**

> A router module holds HTTP concerns only — request validation, status codes,
> response shaping, permission checks. Every query and every business rule lives
> in the domain's `service.py`. Routers are named for one resource and split by
> resource when they pass ~400 lines. A module that serves more than one resource
> family is already wrong, regardless of its length.

The length trigger is secondary. Aire's file did not fail because it was long; it
grew long because nothing said which resources belonged in it.

`_shared.py` holds only helpers used by three or more routers. Aire's equivalent
carries that same threshold in its docstring and it held — keep it.

### Data model

All new tables: integer primary key, plus a `public_id` UUID where the row is
addressable from outside (branches, events, registrations), following the
existing `Venue` model. `sqlalchemy.JSON`, never `JSONB` or `ARRAY`, so the
SQLite dev database keeps working.

**`branches`** — slug (unique), name, address_line1/2, city, country_code,
timezone, public_phone, public_email, whatsapp_number, instagram/facebook URLs,
`website_url` (per-branch override of the site origin used in generated links),
`active`, `bookable`, `is_default`, timestamps, `deleted_at`.

At most one branch may be `is_default`. Aire enforces this with a Postgres
partial unique index; that has no SQLite equivalent, so **the service layer
clears the flag on every other row inside the same transaction as it sets one.**
A test asserts the invariant after two consecutive writes.

**`branch_settings`** — 1:1 with a branch, created with the branch:
`sender_display_name`, `reply_to_email`, `tour_notification_recipients` (JSON
list of emails), `tour_intro_html`, `arrival_instructions`, `parking_notes`.
Everything Aire keeps here about money, tax and booking cutoffs is out.

**`branch_opening_hours`** — branch_id, `day_of_week`, `opens_at_local`,
`closes_at_local`, `active`, `sort_order`. Day numbering is **ISO 1–7 (Monday =
1)**, stated once here because Aire carries two competing conventions and paid
for it.

**`branch_closures`** — branch_id, `starts_at_local`, `ends_at_local`,
`full_day`, `reason` (internal), `public_label` (shown to guests), `active`.
Aire stores both local and UTC copies of each bound; 7magic stores local only
and converts using the branch timezone at read time. One source of truth cannot
drift out of sync with itself.

**`events`** — `branch_id` (nullable: null means the event belongs to every
branch), name, `description_html` (sanitized), venue, `event_start_at`,
`event_end_at`, `registration_opens_at`, `registration_closes_at`, `capacity`,
`cover_image_url`, `color`, `is_active`, `created_by_user_id`, `deleted_at`.

**`event_registrations`** — event_id, guest_name, email, mobile, `party_size`,
`visit_date`, `visit_slot`, `status` (`registered` | `attended` | `no_show` |
`cancelled`), `follow_up`, `follow_up_at`, `notes`, `source` (`public` |
`cms`), `attended_at`, `attended_by_user_id`.

**`event_registration_guests`** — registration_id, name, email, mobile. The
party members beyond the person who filled the form.

**`event_email_templates`** — (event_id, kind) unique, kind ∈ `thank_you` |
`no_show` | `cancel`; subject, body, enabled. Plain text with `{placeholder}`
tokens: `first_name`, `event_name`, `visit_date`, `visit_slot`,
`confirmed_visit_date`, `venue`, `branch_name`. An unknown token renders
literally rather than raising — an admin typo must not break a send.

**`user_roles`** — **altered**: add nullable `branch_id`. `NULL` means the role
applies org-wide; a value scopes it to that branch. This is Aire's
`admin_user_roles` shape, and it is the whole tenancy model 7magic needs.

### Permissions

A resolver reads a user's `user_roles` rows once per request into an access set
answering two questions:

- `has(permission, branch_id=None)` — org-wide grant, or a grant on that branch.
- `branches_with(permission)` — the branch ids this user may act on.

A FastAPI dependency, `require_branch_scope(permission)`, yields that set.
Every branch-scoped list filters `branch_id IN (scope)`; every write asserts the
target branch is in the scope and returns `403 branch_forbidden` otherwise.
Org-wide users get an unbounded scope and no filter is applied.

Roles for launch: `owner` and `admin` (org-wide, full access), `branch_manager`
(branch-scoped, full access to its branch's events and registrations),
`branch_staff` (branch-scoped, may read events and manage registrations, may not
edit branch settings). Permission strings: `branch:read`, `branch:write`,
`event:read`, `event:write`, `registration:read`, `registration:write`.

**The migration seeds every existing user with org-wide rows**, so the current
single admin sees no change. No CMS screen for assigning users to branches ships
in this spec — that is a follow-up. The enforcement layer ships now because
retrofitting scoping onto live endpoints later means re-auditing every one.

### Request flow: a couple books a tour

1. `GET /api/v1/public/tour/branches` → active, bookable branches with city,
   address and public contact details.
2. `GET /api/v1/public/tour/branches/{slug}` → that branch plus its open tour
   event, its opening hours, and closures within the booking window. The page
   renders a date picker that excludes closed days and offers slots derived from
   opening hours.
3. `POST /api/v1/public/tour/branches/{slug}/register` with name, email, mobile,
   visit date, slot and extra guests. On success the API, in one transaction,
   writes the registration and its guests, then after commit sends the guest a
   confirmation and emails the branch's `tour_notification_recipients`.

Email sends happen **after commit and never block the response's success**: a
Resend outage must not cost a lead. Failures are logged and the endpoint still
returns 201. This mirrors how `services/leads.py` already treats its WhatsApp
alert.

### Registration rules and error codes

One function decides whether an event is open, and both the GET payload and the
POST share it — so the page a guest sees and the answer they get on submit can
never disagree. This is the one piece of Aire logic worth copying almost
verbatim (`apps/api/app/api/v1/public/events.py:_registration_block`).

| Condition | Code | Status |
|---|---|---|
| Registration window not yet open | `registration_not_open` | 409 |
| Registration window closed | `registration_closed` | 409 |
| Event already finished (end, or start when no end) | `event_ended` | 409 |
| Party size exceeds remaining capacity | `event_full` | 409 |
| Chosen date falls in a closure or a day with no opening hours | `branch_closed` | 409 |
| Same email already registered for this event | `already_registered` | 409 |
| Malformed email | `validation_error` | 422 |

Every comparison is against a full timestamp, not a calendar date: an event whose
window closes at 19:00 stays open all afternoon.

`description_html` and template bodies pass through the ported `sanitize_html`
allowlist before storage. Untrusted HTML is never stored raw and never rendered
with `{@html}` without having passed it.

### CMS surface

`apps/cms/src/routes/branches` — a list, and a detail page with tabs for
details, settings, opening hours and closures.

`apps/cms/src/routes/events` — a list, and a detail page holding the event form
plus its registrations table (search, status filter, mark attended / no-show,
follow-up toggle, notes, CSV export) and the three email templates with a
preview.

**Branch is a column and a filter, not a mode.** Every list shows a Branch column
and a filter control defaulting to "all branches I can see". There is no header
switcher and no branch in the URL. The consequence, accepted deliberately: event
and registration *forms* must carry an explicit branch picker, because there is
no ambient branch to inherit.

Copy is bilingual on the public side (id canonical, en secondary, Paraglide
messages as elsewhere). CMS copy is Indonesian only, matching the existing CMS.

### Testing

Pytest, against the existing async fixtures:

- **Access resolver** — org-wide vs branch-scoped users; `branches_with` returns
  exactly the granted branches; a branch-scoped user gets 403 writing to another
  branch, and that branch's rows are absent from their list responses.
- **Default-branch invariant** — setting `is_default` on a second branch clears
  the first.
- **Registration rules** — one test per error code in the table above, plus the
  boundary case that an event open until 19:00 accepts a 14:00 registration.
- **Emails** — recipients resolve from branch settings; a send failure still
  returns 201 and persists the registration.
- **Sanitizer** — a script tag in `description_html` does not survive the round
  trip.

Vitest covers the tour form's date/slot derivation from opening hours and
closures. `pnpm check` must stay at zero errors.

### Migration

One Alembic revision creating the eight new tables, adding
`user_roles.branch_id`, seeding a default branch from today's implicit single
location, and seeding org-wide role rows for existing users. It must run on both
SQLite and Postgres: no `JSONB`, no `ARRAY`, no partial indexes, and column adds
via `batch_alter_table` so SQLite can rebuild the table.

## Open follow-ups (explicitly not in this spec)

- Splitting the existing 574-line `app/api/v1/endpoints/admin.py` into
  per-resource modules under the same rule. It is trending toward the same
  failure but is unrelated to this migration; mixing them makes both harder to
  review.
- A CMS screen for assigning users to branches and roles.
- Recurring events and multi-day tour scheduling. Aire has neither.
