import { error, redirect } from '@sveltejs/kit';
import { type VenueCard, type VenueListPayload } from '$lib/api';
import { localizeHref } from '$lib/paraglide/runtime';
import { fetchVenueJson } from '$lib/server/api';
import { titleCase } from '$lib/utils';

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
async function fetchCityVenues(city: string, fetcher: typeof fetch): Promise<VenueCard[]> {
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

export async function load({ fetch, params, url }) {
  // Venue paths are always lowercase (`Venue.path_for` normalizes them), so any
  // other spelling of the same city is a second address for one page. Sent to
  // the canonical one rather than served, the way the landing pages do it.
  const city = params.city.toLowerCase();
  if (params.city !== city) {
    throw redirect(301, `${localizeHref(`/wedding-venue/${city}`)}${url.search}`);
  }

  let venues: VenueCard[];
  try {
    venues = await fetchCityVenues(city, fetch);
  } catch {
    throw error(500, 'Could not load venues');
  }

  // A city with no active venues has no page. This is also what keeps the route
  // from answering for every arbitrary string in the URL -- there is no city
  // list to validate against, so the catalogue itself is the validation.
  if (!venues.length) throw error(404, 'No venues in this city');

  return {
    // Title-cased rather than taken as stored: `city` is not consistently
    // capitalized in the catalogue -- Jakarta's rows carry "jakarta" -- and this
    // name goes in the H1 and the <title>. Same treatment `schema.ts` gives it.
    cityName: titleCase(venues[0].city),
    citySlug: city,
    venues
  };
}
