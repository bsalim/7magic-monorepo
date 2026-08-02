import { error } from '@sveltejs/kit';
import { fetchJson, type ArticleDetail } from '$lib/api';
import { getLocale } from '$lib/paraglide/runtime';

export async function load({ fetch, params }) {
  const locale = getLocale();

  try {
    return {
      article: await fetchJson<ArticleDetail>(
        `/api/v1/public/articles/${params.category}/${params.slug}?locale=${locale}`,
        fetch
      )
    };
  } catch {
    throw error(404, 'Article not found');
  }
}
