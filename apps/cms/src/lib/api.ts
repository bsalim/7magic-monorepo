import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';

// Same reason as $lib/server/api.ts: import.meta.env does not carry
// PUBLIC_-prefixed vars, so reading it there always fell back to port 8003.
//
// See apps/web/src/lib/api.ts for why the browser and SSR need different hosts:
// the browser must use the https origin Caddy serves, while Node cannot resolve
// a *.localhost subdomain and has to hit the loopback port directly.
export function getApiBaseUrl(): string {
  if (browser) {
    return env.PUBLIC_API_BASE_URL || 'http://127.0.0.1:8003';
  }
  return env.PUBLIC_API_INTERNAL_URL || env.PUBLIC_API_BASE_URL || 'http://127.0.0.1:8003';
}

export type AdminShowcaseSummary = {
  id: number;
  title: string;
  slug: string;
  status: string;
  showcase_date: string | null;
  image_url: string | null;
  /** False when the English fields are blank and the showcase falls back. */
  has_english: boolean;
  updated_at: string | null;
};

export type AdminShowcaseDetail = {
  id: number;
  title_id: string;
  title_en: string;
  slug: string;
  body_id: string;
  body_en: string;
  showcase_date: string | null;
  status: string;
  image_url: string | null;
  image_storage_key: string | null;
  has_english: boolean;
  source_ref: string | null;
  updated_at: string | null;
};

export type AdminArticleSummary = {
  id: number;
  title: string;
  slug: string;
  category: string;
  category_slug: string;
  status: string;
  featured: boolean;
  word_count: number;
  /** False when the English fields are blank and the article falls back. */
  has_english: boolean;
  published_at: string | null;
  updated_at: string | null;
};

export type AdminArticleDetail = {
  id: number;
  title_id: string;
  title_en: string;
  slug: string;
  summary_id: string;
  summary_en: string;
  body_id: string;
  body_en: string;
  category: string;
  category_slug: string;
  topic: string[];
  status: string;
  featured: boolean;
  word_count: number;
  has_english: boolean;
  image_url: string | null;
  author: string;
  published_at: string | null;
  updated_at: string | null;
};

export type AdminSummary = {
  totals: {
    venues: number;
    articles: number;
    drafts: number;
    leads: number;
  };
  venues: {
    total: number;
    active: number;
    draft: number;
    archived: number;
  };
  recent_activity: Array<{
    id: number;
    action: string;
    entity: string;
    actor: string;
    created_at: string;
  }>;
};

export type AdminVenue = {
  id: number;
  name: string;
  slug: string;
  city: string;
  district: string;
  stars: number;
  price_start_from: number | null;
  price_for_total_pax: number;
  status: string;
  cover_photo: {
    alt: string;
    small_url: string;
    large_url?: string | null;
  };
};

export type VenuePhoto = {
  id?: number;
  venue_id?: number | null;
  temp_venue_id?: string | null;
  url?: string;
  thumbnail_url?: string;
  fallback?: string;
  thumbFallback?: string;
  alt_text?: string | null;
  sort_order?: number;
  filename?: string;
  original_filename?: string | null;
  content_type?: string | null;
  file_size?: number | null;
  storage_key?: string;
  variants?: Record<string, unknown>;
};

export type VenueDetail = AdminVenue & {
  address: string;
  description: string;
  gallery: VenuePhoto[];
  packages: Array<{
    name: string;
    price: number;
    pax: number;
    note: string;
  }>;
  seo?: {
    title: string;
    meta_description: string;
    canonical_url: string;
  } | null;
};

export type AdminArticle = {
  id: number;
  title: string;
  author: string;
  category: string;
  status: string;
  featured: boolean;
  updated_at: string;
};

export type AuthUser = {
  id: number;
  email: string;
  username: string | null;
  first_name: string;
  last_name: string;
  roles: string[];
};

export type LoginResponse = {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
  user: AuthUser;
};

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}
