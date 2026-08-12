import { redirect } from '@sveltejs/kit';
import { getLocale, localizeHref } from '$lib/paraglide/runtime';

/**
 * Sends every non-canonical spelling of this page to the canonical one.
 *
 * The catch-all url pattern still matches `/en/perjanjian-pranikah`, so the
 * English page is reachable at two URLs: the one with the translated slug and
 * the one that merely gained a prefix. Two URLs serving identical content split
 * its ranking, and the second is the one that was linked before the pattern
 * existed. The article routes resolve this the same way -- canonical wins, the
 * rest 301.
 */
export function load({ url }) {
  const canonical = localizeHref('/perjanjian-pranikah', { locale: getLocale() });
  if (url.pathname !== canonical) {
    throw redirect(301, `${canonical}${url.search}`);
  }
}
