import { redirect } from '@sveltejs/kit';
import { fetchJson, type ArticleListPayload } from '$lib/api';
import { getLocale, localizeHref } from '$lib/paraglide/runtime';

export async function load({ fetch, url }) {
  const locale = getLocale();

  // /en/artikel resolves here too -- the catch-all URL pattern strips the /en
  // prefix and lands on this same route -- which would serve the English index
  // at two addresses. Only the localized one is canonical; the other redirects
  // rather than becoming a duplicate for a crawler to find.
  const canonical = localizeHref('/artikel', { locale });
  if (url.pathname !== canonical) {
    throw redirect(301, `${canonical}${url.search}`);
  }

  const params = new URLSearchParams({ locale });
  const page = url.searchParams.get('page');
  if (page) params.set('page', page);

  return {
    articles: await fetchJson<ArticleListPayload>(
      `/api/v1/public/articles?${params.toString()}`,
      fetch
    )
  };
}
