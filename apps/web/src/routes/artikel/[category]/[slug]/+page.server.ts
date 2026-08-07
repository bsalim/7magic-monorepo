import { error, redirect } from '@sveltejs/kit';
import { fetchJson, type ArticleDetail } from '$lib/api';
import { getLocale } from '$lib/paraglide/runtime';

export async function load({ fetch, params, url }) {
  const locale = getLocale();

  let article: ArticleDetail;
  try {
    article = await fetchJson<ArticleDetail>(
      `/api/v1/public/articles/${params.category}/${params.slug}?locale=${locale}`,
      fetch
    );
  } catch {
    throw error(404, 'Article not found');
  }

  // The API resolves an article by either language's slug, so an English reader
  // can arrive on the Indonesian URL -- from a link minted before the English
  // slugs existed, or from the Indonesian article itself. Serving the same
  // article at two URLs splits its ranking, so the non-canonical one redirects
  // instead. `path` is what the API considers canonical for this locale.
  if (article.path && article.path !== url.pathname) {
    throw redirect(301, `${article.path}${url.search}`);
  }

  return { article, alternates: article.alternates };
}
