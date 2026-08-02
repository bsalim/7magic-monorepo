import { error } from '@sveltejs/kit';

import { fetchJson, type ShowcaseDetail } from '$lib/api';
import { getLocale } from '$lib/paraglide/runtime';

export async function load({ fetch, params }) {
  try {
    return {
      showcase: await fetchJson<ShowcaseDetail>(
        `/api/v1/public/showcases/${params.slug}?locale=${getLocale()}`,
        fetch
      )
    };
  } catch {
    throw error(404, 'Showcase not found');
  }
}
