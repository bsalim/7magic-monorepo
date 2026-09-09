import { describe, expect, it } from 'vitest';
import type { VenueCard } from '$lib/api';
import { cityFloorPrice, groupByStars } from './venue-groups';

const venue = (overrides: Partial<VenueCard>): VenueCard => ({
  id: 1,
  name: 'A Venue',
  slug: 'a-venue',
  city: 'Jakarta',
  district: 'Kuningan',
  stars: 5,
  price_start_from: 100_000_000,
  price_for_total_pax: 300,
  path_url: '/wedding-venue/jakarta/a-venue',
  cover_photo: { alt: 'A Venue', small_url: '/img/venue.webp' },
  ...overrides
});

describe('groupByStars', () => {
  it('orders the groups five stars first, down to three', () => {
    const groups = groupByStars([
      venue({ id: 1, stars: 3 }),
      venue({ id: 2, stars: 5 }),
      venue({ id: 3, stars: 4 })
    ]);

    expect(groups.map((group) => group.stars)).toEqual([5, 4, 3]);
  });

  it('omits a rating no venue in the city has', () => {
    const groups = groupByStars([venue({ id: 1, stars: 5 }), venue({ id: 2, stars: 3 })]);

    expect(groups.map((group) => group.stars)).toEqual([5, 3]);
  });

  // Non-hotel venues carry stars = 0. They still belong on the page -- the point
  // of the hub is that every venue detail page gets an internal link -- but they
  // are not a star rating, so they sort below every rated group.
  it('keeps unrated venues, last', () => {
    const groups = groupByStars([venue({ id: 1, stars: 0 }), venue({ id: 2, stars: 4 })]);

    expect(groups.map((group) => group.stars)).toEqual([4, 0]);
    expect(groups[1].venues).toHaveLength(1);
  });

  // Graha Mandiri and Luxus Grand Ballroom are stored as 1 star while priced at
  // 162jt and 195jt -- they are standalone ballrooms with no hotel rating, not
  // one-star hotels. Rendering "Hotel bintang 1" over them publishes a claim
  // that is both wrong and insulting to the venue.
  it('treats a rating below three as unrated rather than its own group', () => {
    const groups = groupByStars([
      venue({ id: 1, stars: 5 }),
      venue({ id: 2, stars: 1 }),
      venue({ id: 3, stars: 2 })
    ]);

    expect(groups.map((group) => group.stars)).toEqual([5, 0]);
    expect(groups[1].venues.map((item) => item.id)).toEqual([2, 3]);
  });

  it('sorts each group cheapest first, because the query is a price question', () => {
    const groups = groupByStars([
      venue({ id: 1, stars: 5, price_start_from: 250_000_000 }),
      venue({ id: 2, stars: 5, price_start_from: 90_000_000 })
    ]);

    expect(groups[0].venues.map((item) => item.id)).toEqual([2, 1]);
  });

  // A price of 0 or null means "on request", not "free". Sorting it as a number
  // would put every unpriced venue at the top of the cheapest-first list.
  it('sorts venues priced on request below every real price', () => {
    const groups = groupByStars([
      venue({ id: 1, stars: 4, price_start_from: 0 }),
      venue({ id: 2, stars: 4, price_start_from: null }),
      venue({ id: 3, stars: 4, price_start_from: 300_000_000 })
    ]);

    expect(groups[0].venues[0].id).toBe(3);
    expect(groups[0].venues.slice(1).map((item) => item.id)).toEqual([1, 2]);
  });

  it('breaks a price tie on name, so the order is stable between requests', () => {
    const groups = groupByStars([
      venue({ id: 1, stars: 5, name: 'Zenith Ballroom', price_start_from: 80_000_000 }),
      venue({ id: 2, stars: 5, name: 'Amaranta Hall', price_start_from: 80_000_000 })
    ]);

    expect(groups[0].venues.map((item) => item.name)).toEqual([
      'Amaranta Hall',
      'Zenith Ballroom'
    ]);
  });

  it('counts the venues it was given', () => {
    const groups = groupByStars([venue({ id: 1, stars: 5 }), venue({ id: 2, stars: 5 })]);

    expect(groups[0].venues).toHaveLength(2);
  });
});

describe('cityFloorPrice', () => {
  it('returns the cheapest real price', () => {
    const floor = cityFloorPrice([
      venue({ id: 1, price_start_from: 250_000_000 }),
      venue({ id: 2, price_start_from: 88_000_000 })
    ]);

    expect(floor).toBe(88_000_000);
  });

  // Mirrors the API's own price_bands rule: a venue stored as 0 is priced on
  // request, and counting it would advertise a floor of Rp 0.
  it('ignores venues priced on request', () => {
    const floor = cityFloorPrice([
      venue({ id: 1, price_start_from: 0 }),
      venue({ id: 2, price_start_from: null }),
      venue({ id: 3, price_start_from: 120_000_000 })
    ]);

    expect(floor).toBe(120_000_000);
  });

  it('returns null when no venue in the city has a price', () => {
    expect(cityFloorPrice([venue({ id: 1, price_start_from: 0 })])).toBeNull();
  });
});
