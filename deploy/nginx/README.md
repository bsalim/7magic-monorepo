# Nginx ingress (behind Cloudflare)

Alternative to `deploy/caddy/` — use one or the other, never both, since they
would fight over ports 80 and 443.

Cloudflare terminates TLS for the browser. Nginx is the origin: all three
services bind to `127.0.0.1` (see `deploy/systemd/`), so nothing is reachable
except through here.

| Host | Upstream | Service |
|---|---|---|
| `7magicwedding.com` | `127.0.0.1:6273` | `7magic-web` |
| `www.7magicwedding.com` | — | 301 to the apex |
| `cms.7magicwedding.com` | `127.0.0.1:6173` | `7magic-cms` |
| `api.7magicwedding.com` | `127.0.0.1:8003` | `7magic-api` |

## Certificates

There is no certbot and no ACME here — Cloudflare handles the public
certificate. The origin still needs one for the Cloudflare → nginx hop.

Use a **Cloudflare Origin Certificate**: dashboard → SSL/TLS → Origin Server →
Create Certificate, covering `7magicwedding.com` **and** `*.7magicwedding.com`.
One cert then serves all three hosts, which is why every config points at the
same pair of files:

```sh
sudo install -d -m 700 /etc/ssl/cloudflare
sudo install -m 644 origin.pem /etc/ssl/cloudflare/7magicwedding.com.pem
sudo install -m 600 origin.key /etc/ssl/cloudflare/7magicwedding.com.key
```

**Set SSL/TLS mode to Full (strict).** Flexible would leave the
Cloudflare → origin hop unencrypted, and worse, arrive as `http` — nginx would
then pass `X-Forwarded-Proto: http`, adapter-node would build `http://` URLs
and mark session cookies non-secure, and the CMS login would break.

## Install

```sh
sudo cp snippets/*.conf        /etc/nginx/snippets/
sudo cp sites-available/*.conf /etc/nginx/sites-available/

for host in 7magicwedding.com cms.7magicwedding.com api.7magicwedding.com; do
  sudo ln -sf /etc/nginx/sites-available/$host.conf /etc/nginx/sites-enabled/
done

sudo nginx -t && sudo systemctl reload nginx
```

## Locking the origin to Cloudflare

Cloudflare only protects traffic that goes through it. Anyone who learns the
server's IP can hit `:443` directly and bypass WAF and rate limits. Two ways to
stop that, best used together:

1. **Firewall** — allow 80/443 only from Cloudflare's ranges
   (`https://www.cloudflare.com/ips-v4`, `ips-v6`).
2. **Authenticated Origin Pulls** — enable it in the dashboard, install
   Cloudflare's origin-pull CA at
   `/etc/ssl/cloudflare/origin-pull-ca.pem`, then uncomment the
   `ssl_client_certificate` / `ssl_verify_client` lines in each site config.
   Nginx then refuses any connection not carrying Cloudflare's client cert.

## Client IP

`snippets/cloudflare-realip.conf` maps `CF-Connecting-IP` back onto
`$remote_addr`. Without it every request appears to come from a Cloudflare edge
address, so access logs, rate limits and the `X-Forwarded-For` passed upstream
are all wrong.

**The IP list in that file goes stale** — Cloudflare adds ranges. The file
carries a one-liner to regenerate it from `cloudflare.com/ips-v4` and `ips-v6`;
worth a monthly timer.

## Proxy headers

`snippets/7magic-proxy.conf` sets `X-Forwarded-Proto`, `X-Forwarded-Host` and
`X-Forwarded-For`. These pair with `PROTOCOL_HEADER`, `HOST_HEADER`,
`ADDRESS_HEADER` and `XFF_DEPTH` in `deploy/env/{web,cms}.env.example`. Remove
them and adapter-node sees the loopback address over http, so redirects,
cookies and logged client IPs are all wrong.

## Things that differ from the Caddyfile

- **`www` redirects rather than being served.** Caddy answered on both names
  from one block. That cannot carry over: `ORIGIN` in `apps/web/.env` is pinned
  to `https://7magicwedding.com`, and adapter-node rejects a POST whose `Origin`
  header does not match it — so on `www` every form on the site would fail its
  CSRF check. The redirect also removes the duplicate-content problem.
- **gzip only, no zstd.** `encode zstd gzip` has no stock nginx equivalent;
  zstd needs a third-party module. Cloudflare compresses to the browser anyway,
  so this only covers the origin hop.
- **`client_max_body_size` is set explicitly** on the API and CMS hosts. Caddy
  has no request-size cap by default, nginx caps at 1 MiB, and the API accepts
  uploads up to `venue_upload_max_bytes` (10 MiB). Left at the default, photo
  uploads fail with an nginx 413 that never reaches the application. Note
  Cloudflare has its own cap — 100 MB on Free/Pro — which sits below nothing
  here, but is the next limit you would hit.
