# Geo-IP locale redirect — design

Date: 2026-09-12
Status: approved

## Problem

The Indonesian homepage lives at the root `/`, English at `/en` (`vite.config.ts`:
"Indonesian stays at the root so existing URLs and their SEO are untouched").
`strategy: ['url', 'preferredLanguage', 'baseLocale']` in the Paraglide config means
the `url` strategy always resolves an unprefixed path unambiguously, so
`preferredLanguage` never actually fires for `/` — a visitor's browser language is
never consulted. A first-time visitor from outside Indonesia who lands on `/`
today gets Indonesian copy regardless of where they are or what language their
browser is set to, and the only way to reach English is to already know `/en`
exists.

The ask: detect that a visitor is outside Indonesia and send them to `/en`
instead — without breaking how search engines and link-preview bots see the
site, and without fighting a visitor who deliberately switches locale.

## Decisions

**Source of country data: Cloudflare's `CF-IPCountry` header, not a MaxMind DB.**
Production runs `deploy/nginx/` behind Cloudflare (confirmed: Cloudflare
terminates TLS, origin is meant to be locked to Cloudflare's IP ranges per
`deploy/nginx/README.md`). Cloudflare adds `CF-IPCountry` to every proxied
request on every plan including Free, continuously maintained by Cloudflare
itself. This avoids a MaxMind GeoLite2 account/license key, a scheduled
download/refresh job, and a binary DB file to ship and reload — all of which
buy nothing here since the data source (Cloudflare) is already in the request
path. MaxMind would only be needed if traffic ever reached the app bypassing
Cloudflare, which the deployment is already meant to prevent.

**Scope: the bare homepage (`/`) only.** Every other route is left untouched —
no redirect logic for `/wedding-venue/*`, `/articles`, `/artikel/*`,
`/wedding-showcases/*`, or any of the Indonesian-language SEO landers
(`/paket-sangjit`, `/perjanjian-pranikah`, `/bali-wedding-planning`,
`/bali-event-organizer`). Reasoning: whether a real, well-translated English
counterpart exists for a given piece of content is only known via the
`alternates` map each page's `load` computes (the same map `+layout.svelte`
already uses for hreflang) — that data isn't available in `hooks.server.ts`,
which runs before routing/data-loading. Scoping to the homepage sidesteps that
entirely: nobody is ever redirected away from a deep link (a shared article, a
venue page, an ad landing page) that they specifically navigated to.

**Bot/crawler handling: always exempt, checked before the country lookup.**
Googlebot, Bingbot, and link-unfurling bots (Slackbot, Twitterbot, WhatsApp,
LinkedInBot, etc.) crawl from US/EU IPs, so redirecting on `CF-IPCountry` alone
would mean crawlers stop seeing (and indexing) the canonical Indonesian
homepage at `/` — the exact SEO harm this feature must not cause. Detected via
the `isbot` npm package (small, maintained list of known bot user agents)
rather than a hand-rolled regex.

**Override: one sticky cookie, not a one-time flag.** `hooks.server.ts` already
resolves `locale` for every request via `paraglideMiddleware`. It will
set/refresh a `pref_locale` cookie to that resolved value on *every* response,
site-wide (not just `/`). The homepage geo-check then only runs when this
cookie is absent. This makes a manual switch via `LanguageSwitcher.svelte` win
permanently with zero changes to that component: clicking the switcher back to
`/` is a full reload that resolves `locale='id'` for that request, which
overwrites the cookie to `id` on that same response — so the next visit to `/`
sees the cookie and skips the geo-check entirely, regardless of country.

**Redirect mechanics:** `302` (not `301` — the decision is per-visitor and
day-one traffic patterns may change; `301` risks a browser or intermediary
caching "/ → /en" as a permanent fact for everyone), with
`Cache-Control: private, no-store` on the redirect response itself. Combined
with the `Set-Cookie` header every response now carries, this keeps the
response out of any shared cache. No caching config in this repo's nginx/Caddy
setup caches `/` today, so there is no origin-side fix needed — but a
Cloudflare dashboard Cache Rule enabling "Cache Everything" for `/` (if one
exists; not visible from the repo) should be checked manually before shipping,
since dashboard-level rules aren't something this change can verify or fix.

**Country match: exactly `CF-IPCountry !== 'ID'`.** Malaysia, Singapore, and
Brunei are redirected too under this literal rule, even though they're
Bahasa-adjacent markets with real Bali-tourism interest. Flagged, not solved
here — an allowlist of exempted countries is a trivial follow-up if traffic
data ever shows it's costing conversions. An unknown/missing/malformed
`CF-IPCountry` (e.g. `XX`, `T1` for Tor exit nodes, or a header that's simply
absent) fails open to Indonesian — never redirect on uncertain data.

**Dev-only override for local testing.** Local dev (`rundev.sh`, Caddy on
`*.localhost`) never sits behind Cloudflare, so there is no real
`CF-IPCountry` to test against without a VPN. A debug override (e.g.
`?debug_country=US` query param or an `X-Debug-Country` header) is honored
only outside production, so the redirect path can be exercised locally.

## Request flow (`hooks.server.ts`)

1. `paraglideMiddleware` resolves `locale` as it does today.
2. Set/refresh the `pref_locale` cookie to that resolved `locale`
   (`Path=/`, `SameSite=Lax`, `httpOnly`, `Max-Age` ~1 year) — every request,
   every path.
3. Only when `event.request.method === 'GET'` and `event.url.pathname === '/'`,
   evaluate in order, redirecting on first match and otherwise falling
   through to Indonesian:
   - `pref_locale` cookie already present → no redirect.
   - `isbot(userAgent)` → no redirect.
   - `CF-IPCountry` missing / not a 2-letter code (or the dev-only override,
     outside production) → resolve the country; if absent, no redirect.
   - Country `=== 'ID'` → no redirect.
   - Otherwise → `302` to `/en`, `Cache-Control: private, no-store`, with the
     `pref_locale=en` cookie from step 2 already on the response.

`reroute` in `hooks.ts` strips the `/en` prefix before SvelteKit resolves a
route, but `handle` in `hooks.server.ts` sees the original, pre-reroute
`event.url` — so `event.url.pathname === '/'` correctly matches only the bare
Indonesian homepage, never `/en` itself. A visitor who lands directly on `/en`
is never redirected toward Indonesian; this feature only ever pushes traffic
one direction, off the id-canonical root.

## Files touched

- `apps/web/src/hooks.server.ts` — cookie refresh + geo-redirect logic (all of
  the new behavior).
- `apps/web/package.json` — add `isbot`.

Nothing else changes: `LanguageSwitcher.svelte`, `+page.server.ts`,
`vite.config.ts`, the hreflang logic in `+layout.svelte`, and the deploy
configs are all untouched.

## Testing

Vitest exercises `handle` directly with a mocked `RequestEvent`, covering:
- Indonesian visitor (`CF-IPCountry: ID`) → no redirect.
- Non-Indonesian visitor, no cookie → `302` to `/en`, cookie set to `en`.
- Bot user agent, non-Indonesian country → no redirect regardless of country.
- `pref_locale` cookie already present (either value) → no redirect,
  regardless of country or bot status.
- `CF-IPCountry` missing or malformed → no redirect (fail open).
- Any non-`/` path, or non-GET method → geo logic never runs (cookie refresh
  still happens).
- Dev-only country override is honored outside production and ignored in a
  production build.

Manual verification after deploying: since `CF-IPCountry` is set by Cloudflare
at the edge and can't be forged by the client, real verification needs either
a non-Indonesian network/VPN or a debug session confirming the header's
presence via logs.
