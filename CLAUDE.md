# 7magic Monorepo

Wedding platform for the Indonesian market: a public site, an admin CMS, and the
JSON API both consume. pnpm workspace for the two SvelteKit apps, `uv` for the
Python API.

| Path | What it is |
|------|------------|
| `apps/api` | FastAPI + SQLAlchemy 2.0 async. Python ≥3.12, managed with `uv`. |
| `apps/web` | SvelteKit public site (Svelte 5 runes, Tailwind, bits-ui). |
| `apps/cms` | SvelteKit admin app. Same stack, session-cookie auth. |
| `apps/web/content` | Article markdown, imported into the DB by a script — not read at runtime. |
| `deploy/` | systemd units, Caddy config and env templates for `/var/www/7magic-monorepo`. |
| `docs/superpowers/` | Design specs and implementation plans, one per feature. |
| `docs/marketing/` | Editorial calendar, ads keywords, article-image picks. |

## Running it

```bash
pnpm install
cd apps/api && uv sync && cd ../..
./rundev.sh          # starts api, web and cms together
```

Local Caddy (`~/Caddyfile`) terminates TLS in front of all three:
`https://7magic.localhost`, `https://cms.7magic.localhost`,
`https://api.7magic.localhost`. Direct ports are 5182 / 5181 / 8003.

Two API base URLs exist and they are not interchangeable:

- `PUBLIC_API_BASE_URL` — the https origin, used by the browser. An http call
  from an https page is blocked as mixed content.
- `PUBLIC_API_INTERNAL_URL` — the loopback port, used by SSR. Node cannot
  resolve a `*.localhost` subdomain; only the browser does, per RFC 6761.

| Task | Command |
|------|---------|
| API tests | `cd apps/api && uv run pytest` (or `pnpm test` from the root) |
| Web/CMS tests | `pnpm --filter @7magic/web test` (vitest) |
| Type/svelte check | `pnpm check` |
| Lint API | `cd apps/api && uv run ruff check .` |
| Migration | `cd apps/api && uv run alembic revision --autogenerate -m "..."`, then `alembic upgrade head` |

## How the domain fits together

**Content is bilingual, Indonesian is canonical.** `baseLocale` is `id`, with
`en` secondary. Two different mechanisms, easy to confuse:

- Articles and showcases carry paired columns (`title_id`/`title_en`,
  `body_id`/`body_en`). English falls back to Indonesian when null.
- Venues keep canonical text on the row and override per locale in the
  `venue_translations` table (unique on `venue_id` + `locale`).

UI strings are a third thing again: Paraglide messages in
`apps/web/messages/{id,en}.json`, compiled into the gitignored
`apps/web/src/lib/paraglide/`.

**Images live on R2, never on disk.** `services/images.py` renders responsive
webp/jpeg variants on upload; `services/storage.py` puts them in the bucket and
the row stores a variants JSON blob with srcsets. Anything under
`apps/web/static/img/` is either landing-page art committed on purpose or scrape
input staged for a script — `static/img/ig/` is gitignored for that reason.

**Auth** is DB-backed sessions with argon2 hashing (`models/session.py`,
`services/sessions.py`), sliding refresh under a hard 30-day cap. The CMS keeps
the cookie server-side and proxies through `apps/cms/src/lib/server/api.ts`.

**API layout**: `app/api/v1/endpoints/` splits into `public.py` (site reads),
`venues.py` (venue search and detail, also used by a partner integration),
`admin.py` (CMS writes, auth required), plus `auth.py`, `health.py` and
`fixtures.py`. Business logic belongs in `app/services/`, response shapes in
`app/schemas/`.

**Branches and events live in domain packages.** `app/domains/branches/` and
`app/domains/events/` each own their models, schemas, service and (for events)
email rendering. Articles, venues and showcases predate this and stay in the flat
`app/models|services|schemas` layout; do not migrate them opportunistically.

**Anything rendered with `{@html}` is sanitized on write.** `core/html.py` holds
the allowlist; `event.description_html` and `branch_settings.tour_intro_html` both
go through it in their service's write path. It sits in core, not in a domain,
because both write into the same `{@html}` on the public tour page. Add a field
there and you must sanitize it too — the render site does not re-check.

**Routers are one resource each, and hold no queries.** `app/api/v1/admin/` has a
module per resource (`branches.py`, `events.py`, `event_registrations.py`,
`event_emails.py`) carrying HTTP concerns only — validation, status codes,
response shaping, permission checks. Every query and business rule belongs in the
domain's `service.py`. Split a router by resource when it passes ~400 lines. The
platform this was ported from let one admin module absorb every resource and it
reached 7,842 lines; the resource-per-module rule is what prevents that, and the
line count is only the alarm.

**Permissions are branch-scoped.** A `user_roles` row with `branch_id IS NULL` is
org-wide; a row with a branch is scoped to it. Routers never read role rows —
they depend on `BranchScope` from `app/api/v1/admin/_shared.py` and call
`scope.assert_branch(permission, branch_id)` before any write, and pass
`scope.branches_with(permission)` to the service on any list. `branches_with`
returning `None` means *unbounded*, not *none*.

**Opening hours are ISO days: Monday = 1, Sunday = 7.**

**Sync helpers that walk relationships need them preloaded.** `branch_accepts_date`
and `notification_recipients` read `opening_hours`, `closures` and `settings`
without awaiting. Under asyncio, touching an unloaded relationship raises
`MissingGreenlet` instead of emitting a SELECT, so a branch reaching them must
come from `branch_service` (which loads all three via `selectin`) or be refreshed
first.

**Scripts** in `apps/api/scripts/` are one-shot importers and backfills, not part
of the app. They talk to the DB and R2 directly and are usually run once — read
the module docstring before re-running one.

## Conventions

- Small, focused changes that follow the structure already in the file.
- Comments explain *why* a non-obvious choice was made, not what the line does.
  The existing code is consistent about this; match it.
- Indonesian user-facing copy is the source of truth; English is a translation.
- Prices and dates in content are business data — never invent them.
- Search with `rg`.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **7magic-monorepo**. Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/7magic-monorepo/context` | Codebase overview, check index freshness |
| `gitnexus://repo/7magic-monorepo/clusters` | All functional areas |
| `gitnexus://repo/7magic-monorepo/processes` | All execution flows |
| `gitnexus://repo/7magic-monorepo/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
