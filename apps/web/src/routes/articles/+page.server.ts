import { fetchJson, type ArticleListPayload } from '$lib/api';
import { getLocale } from '$lib/paraglide/runtime';

export async function load({ fetch, url }) {
  const params = new URLSearchParams({ locale: getLocale() });
  const page = url.searchParams.get('page');
  if (page) params.set('page', page);

  return {
    articles: await fetchJson<ArticleListPayload>(
      `/api/v1/public/articles?${params.toString()}`,
      fetch
    )
  };
}
