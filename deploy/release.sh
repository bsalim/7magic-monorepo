#!/usr/bin/env bash
# Release the checkout on the server: pull, install, migrate, build, restart,
# then refuse to report success until all three services answer.
#
# Runs as the 7magic user. GitHub Actions reaches it through an SSH key whose
# authorized_keys entry forces this command; by hand it is
#   sudo -u 7magic bash /var/www/7magic-monorepo/deploy/release.sh
set -euo pipefail

REPO="${REPO_DIR:-/var/www/7magic-monorepo}"
# A forced-command login has no profile, so PATH is whatever sshd hands out.
# uv and the corepack pnpm shim live in /usr/local/bin.
export PATH="/usr/local/bin:/usr/bin:/bin"
# Nothing here can answer a prompt. CI=1 puts pnpm, corepack and friends in
# non-interactive mode; the purge flag covers pnpm's "modules directories will
# be removed and reinstalled" confirmation, which it asks whenever the store
# behind node_modules changes (e.g. after the tree changed owner).
export CI=1
export COREPACK_ENABLE_DOWNLOAD_PROMPT=0
export npm_config_confirm_modules_purge=false

log() { printf '==> %s\n' "$*"; }

cd "$REPO"
before="$(git rev-parse --short HEAD)"

log "pull"
git pull --ff-only -q origin main
after="$(git rev-parse --short HEAD)"

log "api: dependencies and migrations"
(cd apps/api && uv sync --frozen -q && uv run alembic upgrade head)

log "web + cms: dependencies and build"
pnpm install --frozen-lockfile --prefer-offline
pnpm --filter @7magic/web run build
pnpm --filter @7magic/cms run build

# Build first, restart last: the only downtime is the units coming back up.
log "restart 7magic.target"
sudo -n systemctl restart 7magic.target

wait_for() {
  local url="$1" code=000
  for _ in $(seq 1 30); do
    code="$(curl -s -o /dev/null -w '%{http_code}' "$url" || true)"
    case "$code" in
      200|3??) printf '    %s -> %s\n' "$url" "$code"; return 0 ;;
    esac
    sleep 2
  done
  printf '    %s -> %s after 60s\n' "$url" "$code" >&2
  return 1
}

log "health"
wait_for http://127.0.0.1:8003/api/v1/health
wait_for http://127.0.0.1:6273/
wait_for http://127.0.0.1:6173/login

log "deployed ${before} -> ${after}"
