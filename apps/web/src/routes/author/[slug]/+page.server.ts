import { error } from '@sveltejs/kit';
import { fetchJson, type ArticleListPayload } from '$lib/api';
import { authorNameForSlug } from '$lib/authors';
import { getLocale, localizeHref } from '$lib/paraglide/runtime';

// Enough that the whole back catalogue is reachable in a few paginated crawls.
const PAGE_SIZE = 24;

export async function load({ fetch, params, url }) {
  const name = authorNameForSlug(params.slug);
  if (!name) throw error(404);

  const locale = getLocale();

  const page = Number(url.searchParams.get('page'));
  const query = new URLSearchParams({ locale, page_size: String(PAGE_SIZE) });
  if (Number.isInteger(page) && page > 1) query.set('page', String(page));

  const articles = await fetchJson<ArticleListPayload>(
    `/api/v1/public/articles/authors/${encodeURIComponent(params.slug)}?${query.toString()}`,
    fetch
  );
  // Past the last page is an empty shell, which must not answer 200.
  if (!articles.items.length && page > 1) throw error(404);

  return { name, articles, basePath: localizeHref(`/author/${params.slug}`, { locale }) };
}
