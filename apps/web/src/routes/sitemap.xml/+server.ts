import { fetchJson, type ArticleListPayload, type ShowcaseListPayload } from '$lib/api';
import { localizeHref } from '$lib/paraglide/runtime';
import { fetchAllPages, fetchVenueCatalogue } from '$lib/server/catalogue';
import { buildSitemap, type SitemapEntry } from '$lib/seo/sitemap';
import { venueCities } from '$lib/venue-groups';

/**
 * Every page worth indexing, in both languages.
 *
 * Built on request rather than at build time: articles and venues change
 * without a deploy, and a sitemap generated at build time would go stale while
 * claiming otherwise. The cache header below keeps that from costing a fan-out
 * of API calls per crawl.
 */

/**
 * Routes with no data behind them. Listed explicitly rather than discovered from
 * the filesystem, because "has a +page.svelte" and "should be in the sitemap"
 * are different questions -- /articles is a redirect and belongs in neither.
 */
const STATIC_PATHS = [
  '/',
  '/artikel',
  '/wedding-venue/search',
  '/wedding-showcases',
  '/our-vendors',
  '/about',
  '/contact',
  '/free-venue-tour',
  '/tour',
  '/paket-sangjit',
  '/perjanjian-pranikah',
  '/bali-wedding-planning',
  '/bali-event-organizer',
  '/privacy',
  '/terms'
];

/** Both locales of a path whose segments are the same words in both. */
function bothLocales(path: string): Record<string, string> {
  return {
    id: localizeHref(path, { locale: 'id' }),
    en: localizeHref(path, { locale: 'en' })
  };
}

async function articleEntries(fetcher: typeof fetch): Promise<SitemapEntry[]> {
  const items = await fetchAllPages(
    (url) => fetchJson(url, fetcher),
    (page) => `/api/v1/public/articles?page=${page}&page_size=50`,
    (payload: ArticleListPayload) => ({
      items: payload.items,
      pages: payload.pagination.total_pages
    })
  );

  // The API's own alternates, not a localized path: an article's category and
  // slug segments are translated, so they cannot be derived from the URL.
  return items.map((article) => ({
    alternates: article.alternates,
    lastmod: article.updated_at
  }));
}

async function venueEntries(fetcher: typeof fetch): Promise<SitemapEntry[]> {
  const items = await fetchVenueCatalogue(fetcher);

  return [
    ...venueCities(items).map((city) => ({
      alternates: bothLocales(`/wedding-venue/${city.slug}`)
    })),
    ...items.map((venue) => ({ alternates: bothLocales(venue.path_url) }))
  ];
}

async function showcaseEntries(fetcher: typeof fetch): Promise<SitemapEntry[]> {
  const payload = await fetchJson<ShowcaseListPayload>(
    '/api/v1/public/showcases?limit=60',
    fetcher
  );

  return payload.items.map((showcase) => ({
    alternates: bothLocales(`/wedding-showcases/${showcase.slug}`),
    lastmod: showcase.showcase_date
  }));
}

export async function GET({ fetch, setHeaders }) {
  // One slow or failing section must not cost the whole sitemap: a crawler that
  // gets a 500 keeps the previous one, but a sitemap missing only its venues is
  // still worth serving, and the next crawl picks the rest back up.
  //
  // Logged rather than swallowed, though. A section that quietly returns [] is
  // indistinguishable from a section that is genuinely empty, and the sitemap
  // still looks healthy while the pages it should list go unindexed.
  const section = async (name: string, entries: Promise<SitemapEntry[]>) => {
    try {
      return await entries;
    } catch (cause) {
      console.error(`[sitemap] ${name} omitted:`, cause);
      return [];
    }
  };

  const [articles, venues, showcases] = await Promise.all([
    section('articles', articleEntries(fetch)),
    section('venues', venueEntries(fetch)),
    section('showcases', showcaseEntries(fetch))
  ]);

  const xml = buildSitemap([
    ...STATIC_PATHS.map((path) => ({ alternates: bothLocales(path) })),
    ...articles,
    ...venues,
    ...showcases
  ]);

  setHeaders({
    'content-type': 'application/xml; charset=utf-8',
    'cache-control': 'public, max-age=3600'
  });

  return new Response(xml);
}
