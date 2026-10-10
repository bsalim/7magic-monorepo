import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { VenueCard } from '$lib/api';

const fetchCityVenues = vi.fn();
vi.mock('$lib/server/venues', () => ({ fetchCityVenues }));

const { load } = await import('./+page.server');

function venue(overrides: Partial<VenueCard>): VenueCard {
  return {
    id: 1,
    name: 'Venue',
    slug: 'venue',
    city: 'jakarta',
    district: 'Menteng',
    address: '',
    stars: 5,
    price_start_from: 100_000_000,
    price_for_total_pax: 200,
    path_url: '/wedding-venue/jakarta/venue',
    cover_photo: { alt: 'Venue', small_url: 'https://media.example/s.jpg', large_url: null },
    ...overrides
  };
}

const run = () => load({ fetch } as Parameters<typeof load>[0]) as Promise<Awaited<ReturnType<typeof load>>>;

describe('jabodetabek-wedding load', () => {
  beforeEach(() => fetchCityVenues.mockReset());

  it('lists only the cities that have venues, in the fixed order', async () => {
    fetchCityVenues.mockImplementation(async (city: string) =>
      city === 'jakarta'
        ? [venue({ price_start_from: 95_000_000 }), venue({ id: 2, price_start_from: 150_000_000 })]
        : city === 'bogor'
          ? [venue({ id: 3, city: 'bogor' })]
          : []
    );

    const { cities } = await run();

    expect(cities.map((city) => city.slug)).toEqual(['jakarta', 'bogor']);
    expect(cities[0]).toMatchObject({ name: 'Jakarta', count: 2, floor: 95_000_000 });
  });

  // One city's API error must not take the whole page down with it.
  it('drops a city whose request fails and keeps the rest', async () => {
    fetchCityVenues.mockImplementation(async (city: string) => {
      if (city === 'tangerang') throw new Error('API request failed: 500');
      return city === 'jakarta' ? [venue({})] : [];
    });

    const { cities } = await run();

    expect(cities.map((city) => city.slug)).toEqual(['jakarta']);
  });
});
