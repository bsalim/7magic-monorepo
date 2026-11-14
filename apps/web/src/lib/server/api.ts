import { env } from '$env/dynamic/private';

import { fetchJson } from '$lib/api';

// Server-only wrapper for the protected venue endpoints. Attaches the private
// venue read key when configured; VENUE_READ_API_KEY must match the API's
// setting of the same name.
export async function fetchVenueJson<T>(
  path: string,
  fetcher: typeof fetch = fetch
): Promise<T> {
  const init = env.VENUE_READ_API_KEY
    ? { headers: { 'x-7magic-venue-key': env.VENUE_READ_API_KEY } }
    : undefined;

  return fetchJson<T>(path, fetcher, init);
}

/**
 * Headers for forwarding a lead to the API. The API refuses leads without
 * LEAD_SUBMIT_KEY when it has one set, because the captcha is only checked
 * here: a bot posting straight to the API would otherwise skip it.
 */
export function leadHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    ...(env.LEAD_SUBMIT_KEY ? { 'x-7magic-lead-key': env.LEAD_SUBMIT_KEY } : {})
  };
}
