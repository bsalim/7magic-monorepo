import type { VenueCard, VenueListPayload } from '$lib/api';
import { fetchVenueJson } from '$lib/server/api';

/**
 * Walks a paginated endpoint to the end. The list endpoints cap page_size well
 * below the article count, so taking the first page would silently ship a
 * partial list -- the failure mode that looks fine until traffic is missing.
 */
export async function fetchAllPages<T>(
  get: (url: string) => Promise<unknown>,
  url: (page: number) => string,
  read: (payload: never) => { items: T[]; pages: number }
): Promise<T[]> {
  const first = read((await get(url(1))) as never);
  const rest = await Promise.all(
    Array.from({ length: Math.max(0, first.pages - 1) }, (_, index) =>
      get(url(index + 2)).then((payload) => read(payload as never).items)
    )
  );
  return [...first.items, ...rest.flat()];
}

/**
 * Every venue in the catalogue, from the database-backed endpoint that the
 * search and detail pages use. /api/v1/public/venues still serves the legacy
 * in-memory fixtures, and a list built from those would advertise four venues
 * and hide the rest.
 */
export function fetchVenueCatalogue(fetcher: typeof fetch): Promise<VenueCard[]> {
  return fetchAllPages(
    (url) => fetchVenueJson(url, fetcher),
    // 24 is this endpoint's ceiling -- it rejects anything larger with a 422
    // rather than clamping, so a bigger number here loses every venue.
    (page) => `/api/v1/venues?page=${page}&page_size=24`,
    (payload: VenueListPayload) => ({
      items: payload.items,
      pages: payload.pagination.total_pages
    })
  );
}
