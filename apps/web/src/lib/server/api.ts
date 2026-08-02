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
