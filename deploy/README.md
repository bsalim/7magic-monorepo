# Server configuration

systemd units and environment templates for running 7Magic on a single host.

```
deploy/
├── systemd/     unit files -> /etc/systemd/system/
├── env/         environment templates -> apps/<app>/.env
└── caddy/       reverse proxy config -> /etc/caddy/
```

`7magic.target` is the single handle for all three — see [Build and release](#build-and-release).

| Service | Runs | Port |
|---|---|---|
| `7magic-api` | FastAPI under gunicorn with uvicorn workers | 8003 |
| `7magic-web` | SvelteKit public site (adapter-node) | 6273 |
| `7magic-cms` | SvelteKit admin (adapter-node) | 6173 |

All three bind to `127.0.0.1`. Caddy terminates TLS and is the only ingress.

## Assumptions

Change these in the unit files if your host differs.

- Code deployed to `/var/www/7magic-monorepo`
- Services run as `www-data`
- Environment files at `/var/www/7magic-monorepo/apps/{api,web,cms}/.env`
- Node at `/usr/bin/node` (v22+), Python venv at `apps/api/.venv`

## Prerequisites this repo needed

Two things were missing before these units could work. Both are now fixed in
the repo, but they explain why the units look the way they do.

**gunicorn was not a dependency, and the worker class moved.** The API only had
`uvicorn`. Worse, `uvicorn.workers.UvicornWorker` — the class every older guide
tells you to use — **was removed in uvicorn 0.46**, which this project is on. It
now ships separately as `uvicorn-worker`, so the unit uses
`uvicorn_worker.UvicornWorker`. Both packages were added via `uv add`.

**Both SvelteKit apps used `adapter-auto`.** That adapter only targets managed
platforms (Vercel, Netlify, Cloudflare) and fails on a plain VPS — it produces
no runnable server. Both now use `@sveltejs/adapter-node`, which emits
`build/index.js` that `node` runs directly with no pnpm at runtime.

## Install

```bash
# 1. Code
sudo mkdir -p /var/www/7magic-monorepo
sudo chown -R www-data:www-data /var/www/7magic-monorepo
sudo -u www-data git clone <repo> /var/www/7magic-monorepo

# 2. Environment files — one per app, alongside the code. They are gitignored,
#    so a later `git pull` leaves them alone.
cd /var/www/7magic-monorepo
sudo -u www-data cp deploy/env/api.env.example apps/api/.env
sudo -u www-data cp deploy/env/web.env.example apps/web/.env
sudo -u www-data cp deploy/env/cms.env.example apps/cms/.env
sudo chmod 600 apps/{api,web,cms}/.env
# then fill in DATABASE_URL, VENUE_READ_API_KEY, R2 credentials, ORIGIN hosts

# 3. Units. The three services are WantedBy=7magic.target, so enabling them
#    links them under the target; enabling the target is what starts it at boot.
sudo cp deploy/systemd/*.service deploy/systemd/*.target /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable 7magic-api 7magic-web 7magic-cms
sudo systemctl enable --now 7magic.target

# 4. Reverse proxy
sudo cp deploy/caddy/Caddyfile.example /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

## Build and release

Run as `www-data` from `/var/www/7magic-monorepo`:

```bash
git pull

# API
cd apps/api && uv sync --frozen && uv run alembic upgrade head && cd ../..

# Web and CMS
pnpm install --frozen-lockfile
pnpm --filter @7magic/web run build
pnpm --filter @7magic/cms run build

sudo systemctl restart 7magic.target
```

`7magic.target` groups all three. The `.target` suffix is not optional —
`systemctl restart 7magic` looks for `7magic.service`, which does not exist, and
fails. Restart and stop propagate to the three services through their
`PartOf=7magic.target`; start comes from the target's `Wants=`.

The API reloads workers without dropping connections:

```bash
sudo systemctl reload 7magic-api    # SIGHUP
```

The Node services have no graceful reload — `restart` drops in-flight requests.
That is acceptable for a marketing site; if it stops being acceptable, run two
instances per app on different ports and cycle them behind Caddy.

## Operating

```bash
systemctl list-dependencies 7magic.target   # all three at a glance
systemctl status 7magic-api
journalctl -u 7magic-web -f
journalctl -u 7magic-api --since "10 min ago" -p err
```

## Gotchas worth knowing

**`ORIGIN` must be set** for both Node services. Without it adapter-node
rejects every form POST with "Cross-site POST form submissions are forbidden",
and the CMS login silently fails. It must match the public HTTPS host exactly —
including `www.` or its absence.

**`VENUE_READ_API_KEY` must be identical** in `api.env` and `web.env`. The
venue endpoints are key-guarded; a mismatch produces 404s on every venue detail
page rather than an auth error, which is a confusing way to find out.

**`ProtectSystem=strict` makes the filesystem read-only.** The API unit lists
`ReadWritePaths=/var/www/7magic-monorepo/apps/api` for that reason. If you add a feature
that writes anywhere else — an upload cache, a log file — add the path there or
it fails with a bare permission error.

**Environment files are not shell.** systemd reads them literally, so
`KEY="value"` puts the quotes *in* the value and `$OTHER` is not expanded.

**Postgres ordering.** The API unit has `After=postgresql.service`. If the
database is on another host, drop that and rely on `Restart=always` to retry.
