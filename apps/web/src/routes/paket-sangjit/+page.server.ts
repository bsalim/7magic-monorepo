import { redirect } from '@sveltejs/kit';
import { getLocale, localizeHref } from '$lib/paraglide/runtime';

/**
 * Sends every non-canonical spelling of this page to the canonical one, as the
 * prenup page does. The catch-all url pattern still matches /en/paket-sangjit,
 * which is the English URL the sitemap listed before the page had an English
 * slug, so it must 301 rather than serve a duplicate.
 */
export function load({ url }) {
  const canonical = localizeHref('/paket-sangjit', { locale: getLocale() });
  if (url.pathname !== canonical) {
    throw redirect(301, `${canonical}${url.search}`);
  }
}
