# 7magic Monorepo

Minimal starting point for the 7magic article and marketplace platform.

## Apps

- `apps/web` — SvelteKit public wedding website.
- `apps/cms` — SvelteKit CMS/backend management app.
- `apps/api` — FastAPI JSON API for the website and CMS.

## Development

```bash
pnpm install
cd apps/api && uv sync
cd ../..
./rundev.sh
```

Local Caddy (`~/Caddyfile`) terminates TLS and proxies these names:

- Web: `https://7magic.localhost`
- CMS: `https://cms.7magic.localhost`
- API: `https://api.7magic.localhost`
- API health: `https://api.7magic.localhost/api/v1/health`

Without the proxy the same services are reachable directly on
`http://localhost:5182` (web), `http://localhost:5181` (cms) and
`http://127.0.0.1:8003` (api) — set `PUBLIC_API_BASE_URL=http://127.0.0.1:8003`
when running that way.

## Design docs

Per-feature specs and implementation plans live in `docs/superpowers/`.
