import { fetchJson } from '$lib/api';

import type { PageServerLoad } from './$types';

export type TourBranch = {
  id: number;
  slug: string;
  name: string;
  city: string;
  addressLine1: string;
  addressLine2: string | null;
  publicPhone: string | null;
  publicEmail: string | null;
  whatsappNumber: string | null;
};

export const load: PageServerLoad = async ({ fetch }) => {
  try {
    const data = await fetchJson<{ items: TourBranch[] }>('/api/v1/public/tour/branches', fetch);
    return { branches: data.items };
  } catch {
    // A branch list that fails to load must not 500 the page; the empty state covers it.
    return { branches: [] as TourBranch[] };
  }
};
