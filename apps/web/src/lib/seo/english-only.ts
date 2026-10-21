import { redirect } from '@sveltejs/kit';
import { localizeHref } from '$lib/paraglide/runtime';

/**
 * Pages written for an English-speaking reader, with no Indonesian edition.
 *
 * The paraglide catch-all serves every route at both `/x` and `/en/x`, which
 * for these pages meant English copy at the root under `<html lang="id">`,
 * announced by hreflang and the sitemap as the Indonesian edition of itself.
 * Each path here 301s from the root to `/en`, carries an English-only
 * alternates map, and is linked at its `/en` URL wherever the site links it,
 * so no page points at the redirect.
 *
 * Unlocalized paths. A path on this list needs a `+page.server.ts` exporting
 * `englishOnlyLoad(path)`; the test holds the two together.
 */
export const ENGLISH_ONLY_PATHS: readonly string[] = [
  '/bali-wedding-planning',
  '/wedding-planning-singapore',
  '/wedding-tools/bali-wedding-cost-calculator',
  '/wedding-tools/bali-wedding-date-planner',
  '/bali-wedding-cost',
  '/legally-married-in-bali'
];

export function isEnglishOnly(path: string): boolean {
  return ENGLISH_ONLY_PATHS.includes(path);
}

export function englishPath(path: string): string {
  return localizeHref(path, { locale: 'en' });
}

/** Where the site should link `path`: its `/en` URL if English-only, else the active locale's. */
export function siteHref(path: string): string {
  return isEnglishOnly(path) ? englishPath(path) : localizeHref(path);
}

/**
 * A static page's sitemap alternates: `en` alone for an English-only page, both
 * locales for the rest, whose segments are the same words in either.
 */
export function staticPathAlternates(path: string): Record<string, string> {
  if (isEnglishOnly(path)) return { en: englishPath(path) };
  return { id: localizeHref(path, { locale: 'id' }), en: englishPath(path) };
}

/**
 * The route load for an English-only page. The `alternates` it returns is what
 * the layout's hreflang and the language switcher read, so only `en` is
 * announced and there is no x-default pointing at a redirect.
 */
export function englishOnlyLoad(path: string) {
  const canonical = englishPath(path);
  return ({ url }: { url: URL }) => {
    if (url.pathname !== canonical) {
      throw redirect(301, `${canonical}${url.search}`);
    }
    return { alternates: { en: canonical } };
  };
}
