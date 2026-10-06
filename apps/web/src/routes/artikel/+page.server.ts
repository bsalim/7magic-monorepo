import { redirect } from '@sveltejs/kit';
import { fetchJson, type ArticleCategoryLink, type ArticleListPayload } from '$lib/api';
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

  // The same parameter names in both locales: they are filters, not content,
  // and one set keeps a shared link working whichever language it is opened in.
  const category = url.searchParams.get('category')?.trim() ?? '';
  // Capped to what the API accepts, so an over-long paste searches on its
  // beginning instead of failing the whole page with a 422.
  const q = (url.searchParams.get('q')?.trim() ?? '').slice(0, 80);
  // The topic chips on an article link here. The topic endpoint takes no
  // category or search, so a topic view is exclusive of both.
  const topic = (url.searchParams.get('topic')?.trim() ?? '').slice(0, 80);

  const params = new URLSearchParams({ locale });
  const page = url.searchParams.get('page');
  if (page) params.set('page', page);
  if (!topic && category) params.set('category', category);
  if (!topic && q) params.set('q', q);

  const listPath = topic
    ? `/api/v1/public/articles/topics/${encodeURIComponent(topic)}`
    : '/api/v1/public/articles';

  const [articles, categories] = await Promise.all([
    fetchJson<ArticleListPayload>(`${listPath}?${params.toString()}`, fetch),
    fetchJson<ArticleCategoryLink[]>(`/api/v1/public/articles/categories?locale=${locale}`, fetch)
  ]);

  return {
    articles,
    categories,
    category: topic ? '' : category,
    q: topic ? '' : q,
    topic,
    basePath: canonical
  };
}
