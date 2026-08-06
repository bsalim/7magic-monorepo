# Wedding checklist generator

**Status: designed, not built.**

A 10-step onboarding wizard on the public site that generates a personalised
wedding checklist, captures the couple as a qualified lead, and gives the team a
CMS module to read submissions and edit the rules that produce them.

The visual design is approved and lives in Claude Design, project
`c2681576-1171-44bd-82f3-307adf9d1704`, file `7Magic Checklist Onboarding.dc.html`.
This spec covers what that file leaves undefined: persistence, identity, the rule
engine's content, and the CMS side.

## Goal

7Magic's only current lead paths are the contact form and the venue-pricing
modal. Both ask a couple for their details before giving them anything. The
checklist inverts that: the couple answers ten questions about their wedding and
receives a plan worth having, and the team receives a lead already carrying date,
city, guest count, budget, religion, adat, and what is already booked.

Three outcomes, in priority order:

1. A generated checklist that is *correct for this market* — especially the legal
   paperwork, which forks on nationality, religion and where the ceremony is.
2. A captured, qualified lead with explicit marketing consent.
3. Two conversion offers at the end of the plan: 5% off a venue, and a wedding
   planner consultation.

## Scope

**In.** The wizard, the generation engine and its launch content, the plan page,
lead capture with Google ID-token verification, the 5% venue banner, the planner
consult CTA, and two CMS sections.

**Out.** A persistent editable task workspace for couples — no accounts, no
ticking tasks off over months, no owners or reminders. The plan is read-only.
Automatic redemption of the 5% code; the team honours it manually. These are
separate specs if they are wanted later.

## Market context

The message catalogue serves Bali (42 mentions), Bintan, Batam, Jakarta,
Tangerang and Singapura. This is a cross-border destination business: Singaporean
and Chinese-Indonesian couples marrying in Bali, Bintan and Batam, alongside
Indonesian domestic couples.

That matters because the design file is written for Singapore — SGD default, ROM
solemnization, Guo Da Li, ang bao — which is *correct for a large share of
customers* and incomplete for the rest. The generator must serve both without
generating the wrong paperwork track for either.

---

## Architecture

```
Browser (SvelteKit, Svelte 5 runes)
  steps 1-9  ->  $state + localStorage('7m.checklist.v1')   [no network]
       |
       |-- enter step 10 --> POST /api/v1/wedding-plans/preview   (stores nothing)
       |                       -> ChecklistService.generate(answers, templates)
       |                     <-- sections[], timeline[], stats{}
       |
       |   couple toggles tasks off -> local Set<template_slug>
       |   full plan visible, unblurred
       |
       |-- submit (form OR Google) --> POST /api/v1/wedding-plans
       |                                 1. verify Google ID token, if used
       |                                 2. INSERT wedding_plans
       |                                 3. INSERT contact_leads  source='wedding_checklist'
       |                                 4. issue 5% venue code
       |                                 5. Resend email, plan rendered at send time
       |                                 6. Bird WhatsApp alert to the team
       |                              <-- { token }
       |                              redirect /wedding-checklist/{token}

GET /wedding-checklist/{token} -> SSR -> GET /api/v1/wedding-plans/{token}
                                          answers + recomputed sections + code
```

Steps 2-6 follow `LeadService`'s existing discipline: **row first, notifications
after**, both best-effort, neither able to fail the request. A Resend or Bird
outage costs a notification, never the couple's plan.

`ChecklistService.generate()` is a pure function of `(answers, templates) ->
sections`. No I/O and no ORM inside it; the caller loads templates. The whole
rule engine is therefore testable against a fixture list with no database.

### Plans are recomputed on view, not materialised

A plan stores its *answers* and its *disabled slugs*, and regenerates from the
current templates on every read. Editing a template therefore changes plans
already issued. That is the chosen behaviour: plans always reflect the planners'
latest thinking.

Two consequences are designed around:

- **The emailed copy is rendered at send time** and is a fixed artifact of what
  was promised on the day, even after templates move on.
- **Toggles key off stable template slugs**, never the design file's positional
  `si + "-" + ti` index, which would silently re-point a couple's switched-off
  tasks the first time a planner reorders a section.

---

## Data model

Five new tables. Content and submissions stay cleanly separated: planners edit
the left-hand group, couples fill the right.

```
checklist_sections                    wedding_plans
  id                                    id
  slug            unique                public_token   unique, indexed, 32 random bytes
  title_id, title_en                    name_a, name_b
  sort_order                            email, whatsapp
  is_planner_addition  bool             google_sub          nullable
                                        email_verified      bool
checklist_templates                     locale              'id' | 'en'
  id                                    currency            'IDR' | 'SGD' | 'USD'
  section_id      FK                    answers_json        JSONB
  slug            unique  <- toggle key disabled_slugs      JSONB   <- stable slugs
  title_id, title_en                    marketing_opt_in    bool
  note_id, note_en     nullable         marketing_opt_in_at datetime nullable
  lead_months     int                   discount_code       nullable
  booked_key      nullable              contact_lead_id     FK -> contact_leads
  sort_order                            created_at/updated_at (TimestampMixin)
  active          bool
                                      date_observances
                                        id
checklist_rules                         slug
  id                                    name_id, name_en
  template_id     FK                    starts_on, ends_on   date
  group           int   <- groups OR'd   applies_to           JSONB (cities / religions)
  fact            str                    severity             'blocking' | 'warning'
  operator        str
  value           str
```

Three decisions worth stating explicitly.

**Rules attach to templates only, never to sections.** A section renders when at
least one of its templates matched. "Tradisi Tionghoa" appears because its tasks
matched, not because of separate section-level gating. This removes an entire
class of inconsistency where a section shows up empty.

**Rules within a `group` are AND-ed; groups are OR-ed.** That is the minimum
expressiveness the content needs: "Muslim *or* Adat Jawa" is two groups, "foreign
national *and* marrying in Indonesia" is two rules in one group. Anything richer
becomes a scripting language planners cannot safely use.

**`answers_json` is stored whole and unparsed**, alongside the extracted columns.
The columns give the CMS something to sort and filter on; the blob means an old
submission stays readable after a question is reworded or removed.

`ContactLead` gains two new `source` values, `wedding_checklist` and
`planner_consult`, and needs no schema change — it already carries
`metadata_json` and a nullable `venue_id`.

---

## The rule engine

### Religion and adat are separate axes

The design file offers one list: Chinese, Christian, Catholic, Malay, Indian.
Those are not the same kind of thing. A Chinese-Indonesian couple is usually also
Christian, Catholic or Buddhist, and needs *both* the sangjit/teapai tasks and
the church tasks. Collapsing ethnicity and religion into one list makes that
couple unrepresentable, and they are a large share of the Bali and Bintan
destination market.

- **`religion`** — islam, kristen, katolik, hindu, buddha, konghucu, none
- **`adat`** — tionghoa, jawa, sunda, batak, minang, bali, melayu, none

Both multi-select, both independent.

### Fact vocabulary

Rules read only these. Everything else is derived.

| Fact | Values |
|------|--------|
| `religion` | islam, kristen, katolik, hindu, buddha, konghucu, none (multi) |
| `adat` | tionghoa, jawa, sunda, batak, minang, bali, melayu, none (multi) |
| `couple_nationality` | `wni_wni`, `wni_wna`, `wna_wna` |
| `legal_path` | `kua`, `catatan_sipil`, `rom_singapore`, `abroad_other`, `already_married` |
| `ceremony_city` | bali, bintan, batam, jakarta, tangerang, singapura, other |
| `events` | akad, resepsi, sangjit, teapai, pemberkatan, misa, pawiwahan, siraman, pengajian, midodareni, ngunduh_mantu, prewedding, engagement (multi) |
| `guests` | integer |
| `budget` | integer, in the chosen currency |
| `diets` | halal, vegetarian, no_pork, elderly, children, wheelchair (multi) |
| `priorities` | up to 3 (multi) |

Operators: `includes`, `not_includes`, `equals`, `not_equals`, `gte`, `lte`.

**"Sudah dipesan" is deliberately not a fact.** Step 8 does not gate anything.
Each answer maps through `checklist_templates.booked_key` to a single template,
which is then rendered already ticked rather than removed — the couple still sees
that the task exists and is handled. This is the design file's `bookedMap`
behaviour, moved into the content layer so planners can extend it.

**`budget` carries no launch rules.** Budget is stored with its `currency` and
displayed, but no template gates on it, because comparing a `gte` threshold
across IDR, SGD and USD needs an exchange rate the system does not hold. If
budget-gated content is wanted later, the rate belongs in a settings row and the
comparison must normalise before it evaluates. Until then the operator is
available for `guests`, which has no such problem.

### The five legal forks

This is the highest-value content in the feature and the reason a couple parts
with their email.

**`kua`** — WNI Muslim, akad in Indonesia. N1/N2/N4 obtained from RT/RW then
kelurahan; *numpang nikah* letter when marrying outside the couple's domicile;
**10 working days' notice**, or a dispensation from the kecamatan; *bimbingan
perkawinan* course; penghulu booking; two male witnesses; akad scheduled before
any reception.

**`catatan_sipil`** — WNI non-Muslim. Religious ceremony first, then civil
registration **within 60 days**. Akta lahir, KK, KTP, surat baptis or
permandian, N1-N4, passport photographs, two witnesses.

**`wni_wna` marrying in Indonesia** — the expensive fork. A **CNI / Surat
Keterangan Tidak Ada Halangan** from the foreign partner's embassy, sworn
translation, legalisation at Kemenkumham and Kemlu, then KUA or Catatan Sipil on
top. **Realistic lead time 2-3 months**, and the most common reason a Bali date
has to move.

**`rom_singapore`** — Singaporean couple registering at home and celebrating in
Bali, Bintan or Batam. The plan must generate **no Indonesian paperwork at all**
and say so explicitly. Instead: ROM notice at least 21 days ahead and valid for
3 months, solemniser, two witnesses, then a symbolic ceremony abroad. A confident
negative result is worth as much here as a task list.

**`already_married`** — skip the track entirely; add only "bring a certified copy
of the marriage certificate", which several Bali venues and villas require before
hosting a blessing.

### Destination logistics

**Bali** — desa adat / banjar permit and contribution for beach and villa events;
local noise curfew; vendor transport surcharge for Uluwatu and Nusa Dua; wet
season (Nov-Mar) indoor backup; buffer day before.

**Bintan and Batam** — ferry blocks from Tanah Merah and HarbourFront; **last
ferry time checked against reception end**, the classic failure; group ticket
booking; passports valid at least 6 months; monsoon Nov-Feb.

**All destinations** — guest room block, welcome bags, attire carried rather than
checked, steaming on arrival, vendor accommodation, rain backup.

### Date observances

A seeded `date_observances` table drives an inline warning on the Date step and a
banner on the plan.

| Observance | Applies to | Severity |
|---|---|---|
| Nyepi | Bali | blocking — the island closes, airport shut 24 hours |
| Idul Fitri and the Ramadan month | all Indonesian cities | warning |
| Galungan / Kuningan | Bali | warning — staff availability and traffic |
| Imlek | all, when `adat` includes tionghoa | warning |

Roughly 30 seeded rows covering the next five years. Highest ratio of planner
credibility to build cost in the feature.

### No prices in template copy at launch

KUA fees, banjar contributions and ferry fares vary and go stale. Per CLAUDE.md
and the unverified-prices note already recorded against articles 122-145,
template notes describe **process and lead time, never Rupiah figures**. Planners
can add verified figures through the CMS later.

---

## The wizard

Ten steps, the design's rail and layout unchanged. Location moves to step 3
because it gates both the legal fork and all destination content, and "where"
directly after "when" is the natural order. Email leaves step 1 for step 10.

| # | Step | Change from the design file |
|---|------|------------------------------|
| 1 | Pasangan | names and helpers as drawn; **plus nationality per partner**; email removed |
| 2 | Tanggal | as drawn; legal options become the five real forks; **plus observance warning** |
| 3 | Lokasi | *was Overseas.* City picker, venue type, guests flying in |
| 4 | Tamu | as drawn |
| 5 | Budget | **IDR default**, Rp presets; funding as drawn |
| 6 | Agama & Adat | *was Cultural.* Split into the two independent multi-selects |
| 7 | Acara | as drawn; options driven by step 6 |
| 8 | Sudah dipesan | as drawn |
| 9 | Prioritas | as drawn, maximum 3 |
| 10 | Review | plan, capture, 5% banner, consult CTA |

State is `$state` persisted to `localStorage`, restored on load, cleared after a
successful submit. Copy is Paraglide messages in `id.json` and `en.json`,
Indonesian authored first and English translated from it. A single bilingual
route `/wedding-checklist`, following `bali-event-organizer` rather than the
duplicated `articles`/`artikel` pattern.

---

## The end of the plan

Rendered in this order, which is a ladder from free value to the largest ask.

1. **Summary stats, timeline and the full checklist**, unblurred and ungated.
   This is the value demonstration; hiding it is the version that does not work.

2. **5% venue banner**, directly under the stats. The banner shows the offer; the
   code itself is revealed by the capture form. The code is generated per plan
   and stored on `wedding_plans.discount_code` with no automatic redemption — the
   team honours it manually when a couple quotes it.

3. **Capture form**, inline. Names prefilled from step 1, email and WhatsApp,
   `Sign in with Google` as an alternative, and the venue-deals opt-in.

   The opt-in ships **unchecked**, with copy that earns the tick: *"Ya,
   kirimkan penawaran venue yang cocok dengan tanggal dan budget kami."* Under UU
   PDP 27/2022 marketing consent should be explicit and separable from the
   service; a pre-ticked box is the pattern regulators single out. The consent
   flag and its timestamp are recorded on the row regardless.

   Google is **ID-token verification only** — the client button returns an ID
   token, the server verifies it against Google's JWKS and extracts email, name
   and `sub`. No session, no account, no OAuth redirect flow. Couples stay
   entirely separate from CMS staff `users`.

4. **"Kewalahan dengan daftar ini?"** consult CTA at the very bottom, after the
   couple has scrolled the whole list, which is when the feeling is real rather
   than manufactured. Posts a second `ContactLead` with `source='planner_consult'`
   carrying the plan token, so the planner opens the conversation already knowing
   the couple's date, city, budget and traditions.

Keeping these as two independently-sourced leads means the venue offer and the
consult offer can be measured separately.

---

## API

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/api/v1/wedding-plans/preview` | public | Generate sections from answers. Persists nothing. |
| POST | `/api/v1/wedding-plans` | public | Persist plan, create lead, notify, return token. |
| GET | `/api/v1/wedding-plans/{token}` | public | Answers plus recomputed plan plus code. |
| POST | `/api/v1/wedding-plans/{token}/consult` | public | Planner consultation lead. |
| GET | `/api/v1/admin/wedding-plans` | session | List and filter submissions. |
| GET | `/api/v1/admin/wedding-plans/{id}` | session | One submission in full. |
| CRUD | `/api/v1/admin/checklist-sections`, `/checklist-templates` | session | Content editing. |

Public endpoints live in `public.py`, admin endpoints in `admin.py`, business
logic in `app/services/checklist.py` and `app/services/wedding_plans.py`,
response shapes in `app/schemas/checklist.py`.

---

## CMS module

Two new sections in `apps/cms`, following the existing `venues` and `articles`
structure and proxying through `src/lib/server/api.ts`.

**`/wedding-plans`** — a list with columns couple, wedding date, city, guests,
budget, religion and adat, task count, consult requested, created. Filters on
city, date range, legal path, marketing opt-in and consult requested. The detail
view shows every answer, the generated plan exactly as the couple sees it, both
linked `ContactLead` rows, a WhatsApp deep link built with the existing
`apps/web/src/lib/whatsapp.ts` helper, and a contacted marker.

**`/checklist-templates`** — sections and templates with `id` and `en` copy,
lead-months, and a rules builder over the fact vocabulary. Plus a **preview
pane**: choose sample answers, see exactly what plan those templates generate.
Without it, editing rules is guesswork.

---

## Errors

| Failure | Behaviour |
|---------|-----------|
| Preview call fails | Error with retry. Wizard state untouched in `localStorage`. |
| Google verification fails | Silently fall back to the plain form. Answers preserved. |
| Submit fails | Error with retry. Nothing cleared. |
| Unknown plan token | 404 page with a link to start the wizard again. |
| Resend or Bird down | Logged and swallowed, exactly as `LeadService` does today. |
| Template deleted after a plan was issued | Its slug in `disabled_slugs` is ignored harmlessly. |

Both public POST endpoints are rate limited.

---

## Testing

`generate()` is pure, so pytest covers it directly against fixture templates:
each of the five legal forks, AND/OR rule grouping, booked-vendor mapping,
disabled-slug filtering, `lead_months` to dates against the wedding date, `id`
to `en` copy fallback, and observance matching including the Bali-only Nyepi
case.

Endpoint tests confirm that preview persists nothing, and that submit writes both
a `wedding_plans` row and a `ContactLead`. Notifiers are **mocked at the
boundary with no `.env` reads**, per commit `039c5fd`.

Vitest covers the wizard state machine, `localStorage` restore, step validation
and the two CTA posts. `pnpm check` for types.

---

## Build order

Each stage is independently useful and independently reviewable.

1. Migrations and models for the six tables.
2. `ChecklistService.generate()` plus its tests, against a small fixture set.
3. Seed the launch content: sections, templates, rules, observances.
4. Public endpoints: preview, submit, read, consult.
5. The wizard, steps 1-9.
6. The review step: plan render, 5% banner, capture form, Google verification,
   consult CTA.
7. CMS `/wedding-plans`.
8. CMS `/checklist-templates` with the preview pane.

Stage 3 is the largest and is content work rather than code — roughly 200
bilingual templates. It can proceed in parallel with stages 4-6 once stage 2
fixes the rule vocabulary.
