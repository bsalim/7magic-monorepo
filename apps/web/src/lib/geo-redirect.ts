import { isbot } from 'isbot';

export const PREF_LOCALE_COOKIE = 'pref_locale';
export const PREF_LOCALE_MAX_AGE = 60 * 60 * 24 * 365; // 1 year, in seconds

// Cloudflare's placeholders for "no real country" -- Tor exit traffic (T1)
// fails the two-letter check on its own, XX does not and must be excluded
// explicitly. Both must fail open to Indonesian, never trigger a redirect.
const UNRESOLVED_COUNTRY_CODES = new Set(['XX', 'T1']);

/**
 * Whether a bare `/` request should be redirected to `/en`.
 *
 * Scoped to the homepage only: whether a real English translation exists for
 * arbitrary content depends on the `alternates` map each page's `load`
 * computes, which isn't available this early in the request. Deep links are
 * never redirected.
 */
export function shouldRedirectToEnglish(input: {
  method: string;
  pathname: string;
  hasLocalePreference: boolean;
  userAgent: string | null;
  country: string | null;
}): boolean {
  if (input.method !== 'GET' || input.pathname !== '/') return false;
  if (input.hasLocalePreference) return false;
  if (isbot(input.userAgent ?? '')) return false;

  const country = input.country?.toUpperCase() ?? null;
  if (!country || !/^[A-Z]{2}$/.test(country) || UNRESOLVED_COUNTRY_CODES.has(country)) {
    return false;
  }

  return country !== 'ID';
}

/**
 * Reads the visitor's country for the geo-redirect check.
 *
 * Cloudflare sets `CF-IPCountry` itself at the edge -- a client cannot forge
 * it once a request actually reaches production through Cloudflare. Local
 * dev never sits behind Cloudflare, so `debug_country` lets the redirect be
 * exercised without a VPN; it is ignored outside dev on purpose.
 */
export function resolveCountry(request: Request, isDev: boolean): string | null {
  if (isDev) {
    const debug = new URL(request.url).searchParams.get('debug_country');
    if (debug) return debug.toUpperCase();
  }

  const header = request.headers.get('cf-ipcountry');
  return header ? header.toUpperCase() : null;
}
