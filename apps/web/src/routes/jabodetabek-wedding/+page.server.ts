import type { VenueCard } from '$lib/api';
import { fetchCityVenues } from '$lib/server/venues';
import { cityStats } from '$lib/venue-groups';
import { titleCase } from '$lib/utils';

// Kartu kota tanpa foto: foto sampul di katalog dipilih per venue, bukan untuk
// mewakili kota (sampul satu venue Bekasi adalah ruang gym).
//
// Urutan tampil di halaman. Kota tanpa venue aktif hilang dengan sendirinya, jadi
// Depok cukup didaftarkan di sini dan muncul begitu venue pertamanya masuk katalog.
const CITIES = ['jakarta', 'tangerang', 'bogor', 'bekasi', 'depok'];

export type JabodetabekCity = {
  slug: string;
  name: string;
  count: number;
  floor: number | null;
  guestsMax: number | null;
};

async function summarize(slug: string, fetcher: typeof fetch): Promise<JabodetabekCity | null> {
  let venues: VenueCard[];
  try {
    venues = await fetchCityVenues(slug, fetcher);
  } catch {
    // Satu kota gagal dimuat tidak boleh menjatuhkan seluruh halaman.
    return null;
  }
  if (!venues.length) return null;

  const stats = cityStats(venues);
  return {
    slug,
    name: titleCase(slug),
    count: stats.count,
    floor: stats.floor,
    guestsMax: stats.guestsMax
  };
}

export async function load({ fetch }) {
  const cities = await Promise.all(CITIES.map((slug) => summarize(slug, fetch)));
  return { cities: cities.filter((city): city is JabodetabekCity => city !== null) };
}
