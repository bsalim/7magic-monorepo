import { fetchJson } from '$lib/api';
import { getLocale } from '$lib/paraglide/runtime';

import type { LayoutServerLoad } from './$types';

export type PromotionPopup = {
  version: string;
  title: string;
  body: string;
  banner_url: string | null;
  cta_label: string | null;
  cta_url: string | null;
  frequency: 'daily' | 'weekly' | 'once';
};

export const load: LayoutServerLoad = async ({ fetch }) => {
  const locale = getLocale();

  try {
    // The API returns null when the popup is off, so nothing ships to the
    // browser unless there is something to show.
    const promotion = await fetchJson<PromotionPopup | null>(
      `/api/v1/public/promotion-popup?locale=${locale}`,
      fetch
    );
    return { promotion };
  } catch {
    // A promo is never worth breaking every page over.
    return { promotion: null };
  }
};
