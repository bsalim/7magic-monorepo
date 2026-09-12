/**
 * Shaping for the city hub pages.
 *
 * The hub exists to rank for "paket wedding {city}", which is a price question,
 * and to give every venue detail page an internal link from something crawlers
 * will actually reach. Both goals shape the ordering below: star rating is how
 * couples here narrow a shortlist, and price is what they came to ask.
 */

import type { VenueCard } from '$lib/api';
import { titleCase } from '$lib/utils';

export type CityEntry = { slug: string; name: string; count: number };

/**
 * The city hubs the catalogue implies, most venues first. Derived rather than
 * listed: there is no cities endpoint, and a hand-maintained list would leave a
 * city opening its first venue with a page nothing points at.
 */
export function venueCities(venues: VenueCard[]): CityEntry[] {
  const counts = new Map<string, number>();
  for (const venue of venues) {
    const slug = venue.path_url.split('/')[2];
    counts.set(slug, (counts.get(slug) ?? 0) + 1);
  }

  return [...counts]
    .map(([slug, count]) => ({ slug, name: titleCase(slug), count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name, 'id'));
}

export type StarGroup = {
  /** The rating itself. 0 is a venue with no hotel rating, not a bad hotel. */
  stars: number;
  venues: VenueCard[];
};

/**
 * Below this, a rating is treated as absent rather than as its own group.
 *
 * Five, four and three star are how couples here narrow a shortlist. One and
 * two star are not a market this site sells into, so a row carrying one is
 * almost always a standalone venue with no hotel rating -- Graha Mandiri and
 * Luxus Grand Ballroom are both stored as 1 star while priced at 162jt and
 * 195jt. Publishing "Hotel bintang 1" above those is a false claim about a
 * partner venue, and a heading no crawler or couple benefits from.
 */
const MIN_RATED_STARS = 3;

/** A price of 0 or null means "on request" -- the same rule the API's price_bands uses. */
function realPrice(venue: VenueCard): number | null {
  return venue.price_start_from && venue.price_start_from > 0 ? venue.price_start_from : null;
}

/**
 * Cheapest first, because the queries this page answers are budget-qualified
 * ("paket wedding 50 juta"). Venues priced on request sort below every real
 * price rather than as 0, which would otherwise float them all to the top.
 */
function byPriceThenName(a: VenueCard, b: VenueCard): number {
  const left = realPrice(a);
  const right = realPrice(b);
  if (left !== right) {
    if (left === null) return 1;
    if (right === null) return -1;
    return left - right;
  }
  return a.name.localeCompare(b.name, 'id');
}

/**
 * Venues grouped by star rating, highest first, unrated last.
 *
 * Ratings with no venues are omitted rather than rendered empty: a city with no
 * three-star venue should not publish a "Venue 3 Star" heading above nothing.
 */
export function groupByStars(venues: VenueCard[]): StarGroup[] {
  const groups = new Map<number, VenueCard[]>();
  for (const venue of venues) {
    const stars = venue.stars >= MIN_RATED_STARS ? venue.stars : 0;
    const bucket = groups.get(stars);
    if (bucket) bucket.push(venue);
    else groups.set(stars, [venue]);
  }

  return [...groups.entries()]
    // Descending by rating, except 0 -- which is "unrated", not "worst" -- and
    // so is pushed past every rated group instead of sorting as the lowest.
    .sort(([a], [b]) => (a === 0 ? 1 : b === 0 ? -1 : b - a))
    .map(([stars, items]) => ({ stars, venues: [...items].sort(byPriceThenName) }));
}

/** The cheapest real price in the city, for the "mulai dari" line. */
export function cityFloorPrice(venues: VenueCard[]): number | null {
  const prices = venues.map(realPrice).filter((price): price is number => price !== null);
  return prices.length ? Math.min(...prices) : null;
}
