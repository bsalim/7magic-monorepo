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

export type BandKey = 'under50' | '50to100' | '100to200' | 'over200' | 'onRequest';

export type BudgetBand = { key: BandKey; min: number; max: number | null };

/**
 * The budget bands couples search in ("paket wedding 50 juta"), so each
 * heading matches a query. The upper bound is exclusive: a venue starting at
 * exactly Rp 100 juta reads as "Rp 100–200 juta", the band its own price names.
 */
export const BUDGET_BANDS: BudgetBand[] = [
  { key: 'under50', min: 0, max: 50_000_000 },
  { key: '50to100', min: 50_000_000, max: 100_000_000 },
  { key: '100to200', min: 100_000_000, max: 200_000_000 },
  { key: 'over200', min: 200_000_000, max: null }
];

const ON_REQUEST: BudgetBand = { key: 'onRequest', min: 0, max: null };

export type BudgetGroup = { band: BudgetBand; venues: VenueCard[] };

function bandFor(price: number | null): BudgetBand {
  if (price === null) return ON_REQUEST;
  return (
    BUDGET_BANDS.find((band) => price >= band.min && (band.max === null || price < band.max)) ??
    ON_REQUEST
  );
}

/** Venues by budget band, cheapest band first and priced-on-request last; empty bands omitted. */
export function groupByBudget(venues: VenueCard[]): BudgetGroup[] {
  return [...BUDGET_BANDS, ON_REQUEST]
    .map((band) => ({
      band,
      venues: venues.filter((venue) => bandFor(realPrice(venue)) === band).sort(byPriceThenName)
    }))
    .filter((group) => group.venues.length > 0);
}

export type CityStats = {
  count: number;
  floor: number | null;
  /** The highest starting price -- not the dearest package, which the cards do not carry. */
  ceiling: number | null;
  guestsMin: number | null;
  guestsMax: number | null;
  districts: number;
  /** Priced bands with at least one venue, cheapest first. */
  bands: { band: BudgetBand; count: number }[];
};

/** Every figure the hub copy quotes, so that none of them is typed into the prose. */
export function cityStats(venues: VenueCard[]): CityStats {
  const prices = venues.map(realPrice).filter((price): price is number => price !== null);
  const guests = venues.map((venue) => venue.price_for_total_pax).filter((count) => count > 0);

  return {
    count: venues.length,
    floor: prices.length ? Math.min(...prices) : null,
    ceiling: prices.length ? Math.max(...prices) : null,
    guestsMin: guests.length ? Math.min(...guests) : null,
    guestsMax: guests.length ? Math.max(...guests) : null,
    // Case-folded: the catalogue is not consistent about it, and "Kuningan" and
    // "kuningan" are one district, not two.
    districts: new Set(venues.map((venue) => venue.district.trim().toLowerCase()).filter(Boolean))
      .size,
    bands: groupByBudget(venues)
      .filter((group) => group.band.key !== 'onRequest')
      .map((group) => ({ band: group.band, count: group.venues.length }))
  };
}
