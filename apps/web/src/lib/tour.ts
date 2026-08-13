import { fetchJson } from '$lib/api';

/** A branch currently taking visits, as `/api/v1/public/tour/branches` returns it. */
export type TourBranch = {
  id: number;
  slug: string;
  name: string;
  city: string;
  address_line1: string;
  address_line2: string | null;
  public_phone: string | null;
  public_email: string | null;
  whatsapp_number: string | null;
};

/** A venue the tour form can suggest, as `/api/v1/public/tour` returns it. */
export type TourVenue = { id: number; name: string; city: string };

/**
 * The branches a visitor can actually book, which is the API's judgement: it
 * returns only active, bookable ones.
 *
 * A failure yields an empty list rather than throwing. Both callers already
 * render an empty state, and neither the /tour picker nor the landing page should
 * return a 500 because the API blinked.
 */
export async function loadBookableBranches(fetcher: typeof fetch): Promise<TourBranch[]> {
  try {
    const data = await fetchJson<{ items: TourBranch[] }>(
      '/api/v1/public/tour/branches',
      fetcher
    );
    return data.items;
  } catch {
    return [];
  }
}

/**
 * Hero art per city. Keyed on the branch's `city`, which is a lowercase slug-ish
 * value on the row, with a fallback so a new city renders a sensible image
 * instead of a broken one the day it is added.
 */
const CITY_IMAGES: Record<string, string> = {
  jakarta: '/img/venue-city-jakarta.jpg',
  bali: '/img/venue-city-bali.jpg',
  singapore: '/img/venue-city-singapore.jpg',
  bogor: '/img/venue-city-bogor.jpg',
  tangerang: '/img/venue-city-tangerang.jpg'
};

export function cityImage(city: string): string {
  return CITY_IMAGES[city.trim().toLowerCase()] ?? '/img/hero-home.jpg';
}
