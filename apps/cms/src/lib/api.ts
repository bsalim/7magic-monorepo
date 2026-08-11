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
  thumb_fallback?: string;
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

// snake_case, like every other type in this file: the API is snake_case on the
// wire throughout. Local TypeScript variables stay camelCase as usual -- it is
// only the field names crossing the wire that mirror the API.
export type AdminBranchSettings = {
  sender_display_name: string | null;
  reply_to_email: string | null;
  tour_notification_recipients: string[];
  tour_intro_html: string | null;
  arrival_instructions: string | null;
  parking_notes: string | null;
};

export type AdminOpeningHour = {
  id?: number;
  day_of_week: number; // ISO: Monday = 1 ... Sunday = 7
  opens_at_local: string; // "10:00:00"
  closes_at_local: string;
  active: boolean;
  sort_order: number;
};

export type AdminClosure = {
  id: number;
  starts_at_local: string;
  ends_at_local: string;
  full_day: boolean;
  reason: string | null;
  public_label: string | null;
  active: boolean;
};

export type AdminBranch = {
  id: number;
  public_id: string;
  slug: string;
  name: string;
  address_line1: string;
  address_line2: string | null;
  city: string;
  country_code: string;
  postal_code: string | null;
  timezone: string;
  public_phone: string | null;
  public_email: string | null;
  whatsapp_number: string | null;
  instagram_url: string | null;
  facebook_url: string | null;
  website_url: string | null;
  active: boolean;
  bookable: boolean;
  is_default: boolean;
  settings: AdminBranchSettings | null;
  opening_hours: AdminOpeningHour[];
  closures: AdminClosure[];
};

export type AdminEvent = {
  id: number;
  public_id: string;
  branch_id: number | null;
  branch_name: string | null;
  name: string;
  description_html: string;
  venue: string | null;
  event_start_at: string | null;
  event_end_at: string | null;
  registration_opens_at: string | null;
  registration_closes_at: string | null;
  capacity: number | null;
  cover_image_url: string | null;
  color: string | null;
  is_active: boolean;
  registration_count: number;
  head_count: number;
};

export type AdminRegistration = {
  id: number;
  public_id: string;
  event_id: number;
  event_name: string | null;
  branch_id: number | null;
  branch_name: string | null;
  guest_name: string;
  email: string;
  mobile: string | null;
  party_size: number;
  visit_date: string | null;
  visit_slot: string | null;
  status: 'registered' | 'attended' | 'no_show' | 'cancelled';
  follow_up: boolean;
  notes: string | null;
  source: string;
  attended_at: string | null;
  guests: Array<{ name: string; email: string | null; mobile: string | null }>;
  created_at: string | null;
};

export type AdminEmailTemplate = {
  kind: 'thank_you' | 'no_show' | 'cancel';
  subject: string;
  body: string;
  enabled: boolean;
};
