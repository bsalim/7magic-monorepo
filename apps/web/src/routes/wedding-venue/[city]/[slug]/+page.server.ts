import { error } from '@sveltejs/kit';
import { type VenueDetail } from '$lib/api';
import { getLocale } from '$lib/paraglide/runtime';
import { fetchVenueJson } from '$lib/server/api';

export async function load({ fetch, params }) {
  const locale = getLocale();

  try {
    return {
      venue: await fetchVenueJson<VenueDetail>(
        `/api/v1/venues/${params.city}/${params.slug}?locale=${locale}`,
        fetch
      )
    };
  } catch {
    throw error(404, 'Venue not found');
  }
}
