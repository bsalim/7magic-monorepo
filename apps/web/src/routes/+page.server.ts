import { fetchJson, type HomePayload, type VenueListPayload } from '$lib/api';
import { fetchVenueJson } from '$lib/server/api';

export async function load({ fetch }) {
  const [home, venueList, baliVenues, singaporeVenues, batamVenues] = await Promise.all([
    fetchJson<HomePayload>('/api/v1/public/home', fetch),
    fetchVenueJson<VenueListPayload>('/api/v1/venues?page_size=12', fetch),
    fetchVenueJson<VenueListPayload>('/api/v1/venues?city=bali&page_size=4', fetch),
    fetchVenueJson<VenueListPayload>('/api/v1/venues?city=singapore&page_size=4', fetch),
    fetchVenueJson<VenueListPayload>('/api/v1/venues?city=batam&page_size=4', fetch)
  ]);

  const featuredVenues = venueList.items
    .filter((venue) => (venue.price_start_from ?? 0) > 0 && venue.price_for_total_pax > 0)
    .slice(0, 4);

  return {
    home: {
      ...home,
      featured_venues: featuredVenues.length === 4 ? featuredVenues : venueList.items.slice(0, 4)
    },
    baliVenues: baliVenues.items,
    singaporeVenues: singaporeVenues.items,
    batamVenues: batamVenues.items
  };
}
