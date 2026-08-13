# Venue tour funnel — design

Date: 2026-08-13
Status: approved

## Problem

`/tour` opens with a grid of branch cards — "pick a branch" — so a couple who has
already chosen a venue must first pick an office, then find their venue again in a
121-item dropdown. The page reads as booking a visit to a 7Magic office. It is not:
a tour visits the venue.

The data model already says so. `event_registrations.venue_id` is the destination,
and `event_service.register` deliberately skips the branch's opening hours and
closed dates because "a venue tour is arranged at a venue rather than at the branch
office". Only the funnel disagrees.

Two further gaps:

- The venue detail page links to `/tour?venue={id}`, but the branch picker sits in
  the way, so the preselection survives only by riding a query param through an
  extra page.
- There is no "Free Venue Tour" entry in the top nav at all. `PublicHeader.svelte`
  ends at Tentang plus a Layanan dropdown; the right-hand side is the language
  switcher and the gold contact button. The `/free-venue-tour` landing page exists
  but nothing in the header points at it.

## What the visitor sees

One form, three entry points.

**From a venue page — `/tour?venue=42`.** The venue is settled, so the form does not
ask again. A locked confirmation line names the venue and its city, with a "change
venue" link that clears the param and reveals the fields. Then name, email, mobile,
visit date, party size.

**From the top nav — `/tour`.** The venue is unknown, so the form leads with it:

- **Venue name** — free text, backed by a suggestion list of the active venues.
  Typing anything and submitting it is valid; picking a suggestion keeps the real
  `venue_id` and auto-fills the city.
- **City** — dropdown, required, built from the distinct cities of active venues.
  This is what routes the lead to a branch.
- Then the same name / email / mobile / date / party-size fields.

**From a branch link — `/tour/jakarta`.** The identical form with the branch fixed by
the slug, and that branch's `tour_intro_html`, arrival instructions and parking notes
rendered above it. The city dropdown still shows: the venue may be in another city,
because the branch handles the booking rather than hosting it.

The branch-card grid is deleted outright. It was the source of the confusion.
`/free-venue-tour` keeps its own per-city buttons into `/tour/{slug}`, unchanged.

## The nav link

`Free Venue Tour` is appended to the `links` array in `PublicHeader.svelte`, making
it the last text link in the nav row — which puts it just before the Layanan
dropdown, since `links` renders ahead of `menus`. Going into `links` rather than
into its own markup is what makes the mobile sheet pick it up for free; the sheet
renders the same array. It points straight at `/tour`, not at the
`/free-venue-tour` landing page: the label promises a booking, and that page's copy
is hardcoded English, which would strand an Indonesian visitor.

The label is the same English phrase in both locales — `nav_free_venue_tour` carries
the identical string in `id.json` and `en.json`. The mobile sheet renders the same
array and so picks it up with no further change.

## Copy

Indonesian is canonical; English is the translation. Deliberately free of numbers,
percentages and named discounts — prices are business data. "Ratusan venue" counts
the network including venues not yet published on the site, which is why it is
hardcoded rather than counted from the venue table.

| Message | Indonesian | English |
|---|---|---|
| `tour_pitch_title` | Kami yang kenal venue-nya. Anda yang dapat penawarannya. | We know the venues. You get the deal. |
| `tour_pitch_body` | 7Magic bekerja langsung dengan ratusan venue di Jakarta, Bali, Bogor, Tangerang, Batam dan Singapura. Kami yang mengatur semuanya dengan pihak venue, dan kami ikut menemani Anda saat survei. | 7Magic works directly with hundreds of venues across Jakarta, Bali, Bogor, Tangerang, Batam and Singapore. We arrange everything with the venue, and we come with you on the visit. |
| `tour_pitch_1` | **Kami yang mengatur, bukan Anda yang menelepon.** Kami hubungi venue-nya, sesuaikan jadwalnya dengan Anda, dan pastikan tim mereka sudah siap menyambut. Tidak perlu mengejar formulir kontak atau menunggu balasan yang tak kunjung datang. | **We arrange it — you don't chase it.** We contact the venue, fit the date around you, and make sure their team is expecting you. No contact forms, no waiting on a reply that never comes. |
| `tour_pitch_2` | **Hubungan baik kami, keuntungan Anda.** Karena kami membawa banyak pasangan ke venue yang sama setiap tahun, kami tahu ruang mana yang masih bisa dinegosiasikan dan apa yang bisa diminta. | **Our relationship, your advantage.** Because we bring couples to the same venues year after year, we know where there's room to negotiate and what's worth asking for. |
| `tour_pitch_3` | **Gratis, dan tanpa ikatan.** Survei venue tidak dipungut biaya sepeser pun, dan Anda tidak wajib memesan apa pun setelahnya. | **Free, with no strings.** The visit costs nothing, and you're under no obligation to book anything afterwards. |
| `tour_pitch_venue` | Kami sudah bekerja dengan {venue}. Beri tahu kami kapan Anda ingin datang, dan sisanya kami yang urus. | We already work with {venue}. Tell us when you'd like to visit and we'll handle the rest. |
| `tour_field_venue_hint` | Venue belum ada di daftar? Tulis saja namanya — jaringan kami lebih luas dari yang tampil di situs. | Venue not on the list? Just type its name — our network is wider than what's shown on the site. |

`tour_pitch_venue` replaces `tour_pitch_body` when a venue is locked in.
`tour_field_venue_hint` sits directly under the free-text venue input, where it
explains why a venue missing from the suggestions is still bookable.

The pitch block sits between the `<h1>` and the form. On `/tour/[slug]`, a branch's
`tour_intro_html` replaces it when set, so a branch that has written its own pitch
does not get two competing ones.

## API

A generic sibling to the existing branch-scoped pair, in `app/api/v1/public/tour.py`:

- `GET /api/v1/public/tour` — the active venues (id, name, city), the distinct city
  list, and whether any branch currently has an open tour event. That flag decides
  between rendering the form and rendering "not taking bookings right now";
  `event_service.open_tour_scope` already computes it in one query.
- `POST /api/v1/public/tour/register` — the existing `PublicRegistration` body plus
  `venue_name` and `city`.

The two `/tour/branches/...` endpoints stay as they are, gaining the same two body
fields.

**Branch resolution** lives in `event_service`, not the router — routers hold no
queries. In order:

1. An active, bookable branch whose `city` matches the submitted city and which has
   an open event.
2. Otherwise an open org-wide event (`branch_id IS NULL`).
3. Otherwise 409 `no_open_event`.

Lowest branch id breaks ties. Only `jakarta` is seeded today, so the org-wide
fallback is the path most cities take in practice; the city match is what keeps the
routing correct as branches are added.

A branch reaching `notification_recipients` must come from `branch_service`, which
loads `opening_hours`, `closures` and `settings` via `selectin`. Resolving a branch
by city has to go through the same service or the sync helpers raise
`MissingGreenlet`.

## Data model

One Alembic revision, two nullable columns on `event_registrations`, no backfill:

- `venue_name` `String(300)` — the typed name when there is no FK.
- `city` `String(80)` — the city the guest picked, or the chosen venue's city.

`RegistrationResponse.venue_name` then means "the venue, named" and coalesces
`venue.name` → `venue_name`.

One extra rule in `event_service.register`: free text that case-insensitively
matches an active venue's name links the FK anyway, so a hand-typed
"The Ritz-Carlton Pacific Place" does not arrive orphaned from the catalogue.

## Web

- `TourForm.svelte` — new shared component under `$lib/components/`, holding the
  whole form and taking the venue / city / branch context as props. Both `/tour` and
  `/tour/[slug]` render it, so the two entry points cannot drift.
- `routes/tour/+page.svelte` — branch-card grid deleted, form in its place.
- `routes/tour/+page.server.ts` — loads from the new endpoint; its POST action posts
  to the new register route.
- `routes/tour/[slug]/+page.svelte` — swaps its inline form for `TourForm`.
- `PublicHeader.svelte` — one entry appended to `links`.
- `messages/{id,en}.json` — `nav_free_venue_tour`, the seven copy strings above, and
  labels for the venue-name and city fields.

The venue detail page needs no change: it already links `/tour?venue={venue.id}`.

## CMS and email

Four places read the venue off a registration and all four take the coalesce:

- the detail response, `app/api/v1/admin/event_registrations.py:76`
- the CSV export, same file around `:122`
- both templates in `app/domains/events/emails.py`

The CMS registration list shows the city beside the venue when there is no FK, so a
front-desk staffer can tell a catalogued venue from a typed one at a glance.

## Tests

API:

- city matches a branch with an open event → that branch's event
- city matches no branch → the org-wide event
- nothing open → 409 `no_open_event`
- an exactly-typed venue name links the FK
- unmatched free text stores the string with `venue_id` NULL
- the existing duplicate-email guard still fires

Web: extend `PublicHeader.test.ts` for the nav link.

## Out of scope

- `branch_id` on venues — precise routing, but a migration, a CMS field and a
  121-row backfill before it works at all.
- Per-venue tour landing pages — 121 crawlable pages that all say the same thing.
- Translating `/free-venue-tour` into Indonesian.
