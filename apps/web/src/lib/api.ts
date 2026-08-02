import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';

const fallbackApiBaseUrl = 'http://127.0.0.1:8003';

// The browser and the SSR process cannot share one base URL in dev. The page is
// served over https by Caddy, so the browser must call the https origin or the
// request is blocked as mixed content -- but macOS resolves only bare
// `localhost`, so Node's fetch gets ENOTFOUND on `api.7magic.localhost`
// (Chrome resolves *.localhost itself, per RFC 6761). Server-side calls
// therefore go straight to the loopback port, bypassing Caddy.
//
// Read through $env/dynamic/public rather than import.meta.env: Vite only
// exposes VITE_-prefixed vars there, so PUBLIC_API_BASE_URL always came back
// undefined and every request silently fell back to port 8003.
export function getApiBaseUrl(): string {
  if (browser) {
    return env.PUBLIC_API_BASE_URL || fallbackApiBaseUrl;
  }
  return env.PUBLIC_API_INTERNAL_URL || env.PUBLIC_API_BASE_URL || fallbackApiBaseUrl;
}

export type VenuePriceBand = {
  label: string;
  min_price: number;
  max_price: number | null;
  count: number;
};

export type VenuePriceBands = {
  floor: number | null;
  priced: number;
  on_request: number;
  bands: VenuePriceBand[];
};

export type ImageRef = {
  alt: string;
  small_url: string;
  large_url?: string | null;
  webp_srcset?: string | null;
  jpeg_srcset?: string | null;
  sizes?: string | null;
  width?: number | null;
  height?: number | null;
};

export type ShowcaseCard = {
  title: string;
  slug: string;
  showcase_date: string | null;
  image: ImageRef | null;
};

export type ShowcaseListPayload = {
  items: ShowcaseCard[];
  total: number;
};

export type ShowcaseDetail = ShowcaseCard & {
  body: string;
};

export type VenueCard = {
  id: number;
  name: string;
  slug: string;
  city: string;
  district: string;
  stars: number;
  price_start_from: number | null;
  price_for_total_pax: number;
  path_url: string;
  cover_photo: ImageRef;
};

export type Pagination = {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};

export type VenueListPayload = {
  items: VenueCard[];
  pagination: Pagination;
};

export type VenueDetail = VenueCard & {
  address: string;
  description: string;
  status: string;
  gallery: Array<{
    url?: string;
    thumbnail_url?: string;
    alt_text?: string | null;
    webp?: string;
    fallback?: string;
    thumbWebp?: string;
    thumbFallback?: string;
  }>;
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
  };
};

export type ArticleCard = {
  id: number;
  title: string;
  slug: string;
  category: string;
  summary: string;
  image_url: string;
  author: string;
  status: string;
  featured: boolean;
  updated_at: string;
};

export type ArticleListPayload = {
  items: ArticleCard[];
  pagination: Pagination;
};

export type ArticleDetail = ArticleCard & {
  content: string;
  topic: string[];
  word_count: number;
  published_at: string | null;
};

export type HomePayload = {
  hero: {
    title: string;
    subtitle: string;
    image: string;
  };
  featured_venues: VenueCard[];
  featured_articles: ArticleCard[];
  testimonials: Array<{
    couple: string;
    message: string;
    image: string;
  }>;
};

export type ContactLeadPayload = {
  name: string;
  email?: string;
  phone?: string;
  message: string;
  source_path?: string;
  venue_slug?: string;
};

export type ContactLeadResponse = {
  id: number;
  status: 'received';
  message: string;
  created_at: string;
};

export async function fetchJson<T>(
  path: string,
  fetcher: typeof fetch = fetch,
  init?: RequestInit
): Promise<T> {
  const response = await fetcher(`${getApiBaseUrl()}${path}`, init);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}
