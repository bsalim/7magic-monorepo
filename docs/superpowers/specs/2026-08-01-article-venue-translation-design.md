# Article and Venue Translation — Design

Date: 2026-08-01
Status: approved

## Problem

The platform stores content in two languages but only one is populated.

**Articles.** Migration `07b0d23ad522` reshaped `articles` so a single row carries both
languages: `title_id`/`summary_id`/`body_id` are canonical and required, and
`title_en`/`summary_en`/`body_en` are nullable. `Article.title_for()`, `summary_for()` and
`body_for()` fall back to Indonesian when the English field is blank, and `has_translation()`
reports whether a row genuinely exists in a locale. All 112 published articles have empty
English fields, so every English reader is served Indonesian.

**Venues.** Venues use a different shape: `venues.description` is canonical and
`venue_translations(venue_id, locale, description, packages)` holds alternates. The
translations table is empty, and all 122 venue descriptions are written in **English** — the
opposite of the intended arrangement, where Indonesian is canonical.

## Goals

1. Populate English for all 112 articles with prose that reads as though written by an
   English-speaking wedding blogger, not as translated output.
2. Invert the venue data so Indonesian is canonical and the existing English is preserved as
   a proper `en` translation row.
3. Ship both as Alembic revisions so any environment converges on the same content.

## Non-goals

- English article slugs. `articles.slug` is a single shared column, so an English article
  keeps the Indonesian slug in its URL. Changing that requires a schema change plus redirect
  handling and is deliberately out of scope.
- Translating `venues.packages`. It is NULL on all 122 rows.
- Any change to `Article`/`Venue` models, services, or API surface. This is data only.

## Approach

### Delivery shape

Each phase is one Alembic revision plus one sidecar JSON data file:

```
apps/api/migrations/versions/<rev>_translate_articles_to_en.py
apps/api/migrations/data/article_translations_en.json

apps/api/migrations/versions/<rev>_reverse_venue_descriptions_to_id.py
apps/api/migrations/data/venue_descriptions_id.json
```

The revision file stays short and reviewable; the translated prose lives in its own file so it
diffs and reviews independently of migration logic. Both JSON files are keyed by **`public_id`**
(UUID), not the integer `id`, because integer ids are not stable across environments.

### Phase 1 — Articles

For each article, produce `title_en`, `summary_en` and `body_en`. The revision loads the JSON,
looks each row up by `public_id`, and issues an `UPDATE`. `downgrade()` sets the three columns
back to NULL, which is exactly the pre-migration state.

**HTML integrity is a hard requirement.** Bodies are Quill markup — `<p>`, `<h2 id="section-…">`,
`<ol><li data-list="bullet">`, `<span class="ql-…">`. Only text nodes are translated. The tag
stream, attribute values, and especially the `id` attributes on headings must come through
byte-identical to the Indonesian source, because those anchors are slug-derived and are linked
to from tables of contents. Every translated body is checked by stripping text and comparing the
remaining tag sequence against the source before it is accepted into the JSON.

### Phase 2 — Venues

For each venue: write the current English `description` into a new `venue_translations` row with
`locale = 'en'`, then overwrite `venues.description` with a fresh Indonesian translation.

The overwrite is unconditional — a straight `UPDATE` from the JSON on all 122 rows. This was an
explicit decision. The tradeoff, accepted knowingly: if a venue description is edited between
the JSON being generated and the migration running, that edit is silently discarded.

`downgrade()` copies the English back from `venue_translations` into `venues.description` and
deletes the `en` rows.

## Voice

The two content types need different registers, and each can be wrong independently.

### Articles — casual, second person

The Indonesian source is a Gen-Z wedding blog: chatty, second person, mixed Indonesian-English
slang, rhetorical hooks, em-dashes. The English must carry the same energy rather than flatten
into neutral prose.

Source: *"Pernah kepikiran buat nikah di tempat yang gak pasaran, lebih intimate, dan serasa
'rumah sendiri'?"*

Target: *"Ever pictured getting married somewhere that isn't the usual banquet hall — smaller,
warmer, more like your own place?"*

Rules:

- Re-express idioms, never carry them across literally. `gak pasaran` is not "not mainstream";
  it is "not the usual" or "off the beaten path" depending on what the sentence is doing.
- Keep contractions and direct address. The reader is "you".
- Preserve the hooks, asides and rhetorical questions. Dropping them is what makes translated
  prose read as machine output.
- Indonesian wedding terms with no clean English equivalent (`akad`, `siraman`, `seserahan`,
  `ngunduh mantu`, `lamaran`) stay in Indonesian, italicised, with a short gloss on first use in
  the article. This matters most for the 28 "Tradisi wedding" articles.
- Proper nouns, venue names, prices, capacities and dates are never altered.
- No translator's notes, no "this article will explain" scaffolding that was not in the source.

### Venues — factual, informative

Venue descriptions are listing copy: room counts, event space, dining outlets, location. The
Indonesian should read as natural informative marketing prose, not as a literal gloss.

- Hospitality vocabulary that Indonesian speakers genuinely use in English stays in English:
  *ballroom*, *rooftop*, *check-in*, *suite*, *lounge*.
- Numbers, units, capacities and proper nouns are preserved exactly. Square feet stays square
  feet; it is not silently converted.
- District and landmark names keep their local form (Mega Kuningan, SCBD, Bundaran HI).

## Execution

1. Write the style guide, then translate a **pilot** of 8 articles — spanning Wedding Venue,
   Wedding Preparation, Tradisi wedding and Photography, and spanning short to long — plus
   **5 venues**.
2. Present the pilot for approval. Both registers get reviewed in the same round.
3. Once the voice is signed off, fan out parallel subagents over the remaining 104 articles and
   117 venues, each working against the approved style guide.
4. Assemble and validate the JSON files, then write the two revisions.

Pilot first because the corpus is large — roughly 1.01M characters of article HTML — and
discovering the register is wrong after translating all of it means redoing all of it.

## Verification

`scripts/validate_article_translations.py` is the reusable gate. It checks tag-stream
equality, `public_id` resolution, title length, leftover Indonesian, and number localisation
as hard failures, and reports lost non-ASCII characters as review warnings rather than
failures — dropping an emoji is a bug, but re-expressing `sore → malam` as "afternoon rolling
into evening" is the idiomatic rewrite the guide asks for.

## Outcome

All checks below passed on 2026-08-01.

- **112 / 112 articles** translated; validator clean, one reviewed warning (article 81's `→`
  became prose, which reads better).
- **120 / 122 venues** reversed. Ids 129 and 130 were skipped: they are known stray test rows.
- `alembic upgrade head` then `downgrade` restored both tables to a byte-identical baseline,
  confirmed by md5 over `articles.body_id` and `venues.description`. The canonical Indonesian
  is never touched by either revision.
- The API suite passes (108 tests).

Two classes of defect were found and fixed after the first assembly, both invisible to a
tag-only check:

1. **24 numbers** kept Indonesian separators inside English prose. `5.000 guests` reads as
   five. The guide now states that the rule protects the value, not the punctuation.
2. **9 uses of "dowry"** named a payment flowing the wrong direction. `sinamot` is a Batak
   bride price and `mahar` a bridal gift from the groom; both were corrected, and article 86
   had collapsed "Mahar atau mas kawin" into a single wrong gloss.

### Known content issues in the source, not fixed here

Translation faithfully reproduced these, so they now appear in both languages. Each is a
content fix for the CMS, not a migration concern:

- **Article 116** contains a leftover instruction to the writer: *"Bagian ini kita rewrite
  total agar lebih millennial…"*.
- Article 55's title says 8 villas while the intro promises 10 recommendations.
- The "officially largest hotel ballroom in North Jakarta" line is copy-pasted onto the
  Lausanne and Zurich ballrooms in article 7, where it is not true.
- Article 90 claims a congregation hall offers 179 meeting rooms.
