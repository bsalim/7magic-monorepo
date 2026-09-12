import { fetchVenueCatalogue } from '$lib/server/catalogue';
import { buildLlmsTxt } from '$lib/seo/llms';
import { venueCities, type CityEntry } from '$lib/venue-groups';

/**
 * Built per request for the same reason the sitemap is: the city list comes
 * from the venue catalogue, which changes without a deploy. A catalogue outage
 * costs the city section, not the file -- logged, so an empty section is
 * distinguishable from a genuinely empty catalogue.
 */
export async function GET({ fetch, setHeaders }) {
  let cities: CityEntry[] = [];
  try {
    cities = venueCities(await fetchVenueCatalogue(fetch));
  } catch (cause) {
    console.error('[llms.txt] cities omitted:', cause);
  }

  setHeaders({
    'content-type': 'text/markdown; charset=utf-8',
    'cache-control': 'public, max-age=86400'
  });

  return new Response(buildLlmsTxt(cities));
}
