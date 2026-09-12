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
- Services run as `7magic`, a system user that owns the tree and nothing else
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
# 1. User and code. One system user per app keeps a compromise in one tenant
#    from reaching the others; www-data owns nothing here. Debian's adduser
#    rejects names that start with a digit unless told otherwise. The shell is
#    bash, not nologin: the GitHub Actions deploy key logs in as this user and
#    sshd runs its forced command through the login shell.
sudo adduser --system --group --home /home/7magic --shell /bin/bash \
     --allow-bad-names 7magic
sudo mkdir -p /var/www/7magic-monorepo
sudo chown 7magic:7magic /var/www/7magic-monorepo
sudo chmod 750 /var/www/7magic-monorepo
sudo -u 7magic git clone <repo> /var/www/7magic-monorepo

# 2. Environment files — one per app, alongside the code. They are gitignored,
#    so a later `git pull` leaves them alone.
cd /var/www/7magic-monorepo
sudo -u 7magic cp deploy/env/api.env.example apps/api/.env
sudo -u 7magic cp deploy/env/web.env.example apps/web/.env
sudo -u 7magic cp deploy/env/cms.env.example apps/cms/.env
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

`deploy/release.sh` does all of this and then waits for the three services to
answer. GitHub Actions runs it on every push to `main` that passes CI (see
`.github/workflows/ci.yml`): the workflow SSHes in as `7magic` with a key whose
`authorized_keys` entry forces that script, so the key can do nothing else. By
hand:

```bash
sudo -u 7magic bash /var/www/7magic-monorepo/deploy/release.sh
```

Step by step, as `7magic` from `/var/www/7magic-monorepo`:

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

**Run git in the tree as `7magic`, not as yourself.** git refuses to operate on
a checkout owned by another user ("dubious ownership"), and a build run as the
wrong user leaves files the service cannot read. The first `pnpm install` and
`uv sync` as `7magic` re-download into that user's own cache — the tree was
previously hardlinked into www-data's shared store, and that is expected.

**`ProtectHome=true` turns a missing `~/.postgresql` into a crash.** asyncpg
stats `~/.postgresql/postgresql.key` on every connect; behind `ProtectHome` that
is EACCES rather than ENOENT and every query 500s. The API unit sets
`HOME=/nonexistent` for that reason — keep it if you change the user.

**Postgres ordering.** The API unit has `After=postgresql.service`. If the
database is on another host, drop that and rely on `Restart=always` to retry.
