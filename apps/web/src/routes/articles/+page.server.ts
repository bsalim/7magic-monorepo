import { redirect } from '@sveltejs/kit';
import { getLocale, localizeHref } from '$lib/paraglide/runtime';

/**
 * The article index used to live at /articles in both languages. It is now
 * /artikel in Indonesian and /en/articles in English, so this path is left
 * behind purely to redirect: it has been linked and indexed, and dropping it
 * would 404 that traffic instead of passing it on.
 *
 * 301 rather than 302 -- the move is permanent, and the old URL should stop
 * being the one search engines hold on to.
 */
export function load({ url }) {
  const target = localizeHref('/artikel', { locale: getLocale() });
  throw redirect(301, `${target}${url.search}`);
}
