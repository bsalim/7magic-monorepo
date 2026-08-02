import { type VenueListPayload } from '$lib/api';
import { fetchVenueJson } from '$lib/server/api';

export async function load({ fetch, url }) {
  const params = new URLSearchParams();
  for (const key of ['q', 'city', 'stars_min', 'page']) {
    const value = url.searchParams.get(key);
    if (value) params.set(key, value);
  }

  // `stars` is repeatable (?stars=5&stars=3) — the tick-box filter submits one
  // entry per ticked rating, so append rather than set or only the last survives.
  const stars = url.searchParams.getAll('stars').filter(Boolean);
  for (const value of stars) params.append('stars', value);

  const query = params.toString();
  return {
    // The database-backed venue endpoint, matching the home and detail pages.
    // /api/v1/public/venues still serves the legacy in-memory fixtures.
    venues: await fetchVenueJson<VenueListPayload>(
      `/api/v1/venues${query ? `?${query}` : ''}`,
      fetch
    ),
    filters: {
      q: url.searchParams.get('q') ?? '',
      city: url.searchParams.get('city') ?? '',
      starsMin: url.searchParams.get('stars_min') ?? '',
      stars
    }
  };
}
