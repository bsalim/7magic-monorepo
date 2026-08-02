import { fetchJson, type ShowcaseListPayload } from '$lib/api';
import { getLocale } from '$lib/paraglide/runtime';

export async function load({ fetch, url }) {
  const params = new URLSearchParams({ locale: getLocale(), limit: '24' });
  const page = Number(url.searchParams.get('page') ?? '1');
  const current = Number.isFinite(page) && page > 0 ? Math.floor(page) : 1;
  params.set('offset', String((current - 1) * 24));

  return {
    page: current,
    showcases: await fetchJson<ShowcaseListPayload>(
      `/api/v1/public/showcases?${params.toString()}`,
      fetch
    )
  };
}
