#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_PORT="${API_PORT:-8003}"
WEB_PORT="${WEB_PORT:-${PORT:-5182}}"
CMS_PORT="${CMS_PORT:-5181}"

# Caddy (~/Caddyfile) terminates TLS on these names and proxies to the ports
# above. The browser must call the https origin -- an http API call from an
# https page is blocked as mixed content -- but Node cannot resolve a
# *.localhost subdomain (macOS resolves only bare `localhost`; Chrome resolves
# these itself per RFC 6761), so SSR talks to the loopback port directly.
API_URL="${PUBLIC_API_BASE_URL:-https://api.7magic.localhost}"
API_INTERNAL_URL="${PUBLIC_API_INTERNAL_URL:-http://127.0.0.1:${API_PORT}}"
WEB_URL="${WEB_URL:-https://7magic.localhost}"
CMS_URL="${CMS_URL:-https://cms.7magic.localhost}"

cleanup() {
  if [[ -n "${API_PID:-}" ]]; then
    kill "${API_PID}" 2>/dev/null || true
  fi
  if [[ -n "${WEB_PID:-}" ]]; then
    kill "${WEB_PID}" 2>/dev/null || true
  fi
  if [[ -n "${CMS_PID:-}" ]]; then
    kill "${CMS_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

(
  cd "${ROOT_DIR}/apps/api"
  API_PORT="${API_PORT}" uv run uvicorn app.main:app --reload --host 127.0.0.1 --port "${API_PORT}"
) &
API_PID=$!

(
  cd "${ROOT_DIR}/apps/web"
  PUBLIC_API_BASE_URL="${API_URL}" PUBLIC_API_INTERNAL_URL="${API_INTERNAL_URL}" \
    pnpm exec vite dev --host 0.0.0.0 --port "${WEB_PORT}" --strictPort
) &
WEB_PID=$!

(
  cd "${ROOT_DIR}/apps/cms"
  PUBLIC_API_BASE_URL="${API_URL}" PUBLIC_API_INTERNAL_URL="${API_INTERNAL_URL}" \
    pnpm exec vite dev --host 0.0.0.0 --port "${CMS_PORT}" --strictPort
) &
CMS_PID=$!

echo "API: ${API_URL}          (direct: http://127.0.0.1:${API_PORT})"
echo "Web: ${WEB_URL}              (direct: http://localhost:${WEB_PORT})"
echo "CMS: ${CMS_URL}          (direct: http://localhost:${CMS_PORT})"

wait -n "${API_PID}" "${WEB_PID}" "${CMS_PID}"
exit_code=$?
cleanup
wait "${API_PID}" 2>/dev/null || true
wait "${WEB_PID}" 2>/dev/null || true
wait "${CMS_PID}" 2>/dev/null || true
exit "${exit_code}"
