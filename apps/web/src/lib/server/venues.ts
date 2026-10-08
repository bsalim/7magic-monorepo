import type { VenueCard, VenueListPayload } from '$lib/api';
import { fetchVenueJson } from '$lib/server/api';

/**
 * The endpoint's ceiling. It rejects anything larger with a 422 rather than
 * clamping, so a bigger number here loses every venue -- the same trap the
 * sitemap documents.
 */
const PAGE_SIZE = 24;

/**
 * Every active venue in one city.
 *
 * The hub lists them all on one page rather than paginating: 61 is the largest
 * city and the whole point of the page is that each venue detail page gets an
 * internal link a crawler reaches without following a pager.
 */
export async function fetchCityVenues(city: string, fetcher: typeof fetch): Promise<VenueCard[]> {
  const url = (page: number) =>
    `/api/v1/venues?city=${encodeURIComponent(city)}&page=${page}&page_size=${PAGE_SIZE}`;

  const first = await fetchVenueJson<VenueListPayload>(url(1), fetcher);
  const rest = await Promise.all(
    Array.from({ length: Math.max(0, first.pagination.total_pages - 1) }, (_, index) =>
      fetchVenueJson<VenueListPayload>(url(index + 2), fetcher).then((payload) => payload.items)
    )
  );

  return [...first.items, ...rest.flat()];
}
