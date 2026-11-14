/**
 * The "cek harga & tanggal kosong" request: a pricing lead, optionally followed
 * by a venue tour booking for the same venue.
 *
 * Two records rather than one combined lead, so each lands in the inbox that
 * already handles it -- the pricing lead with the planners, the tour with the
 * branch -- and neither backend had to change to accept the other's fields.
 *
 * The browser sends both in one request to /api/venue-inquiry, which files them
 * in turn. One request because a Turnstile token can be verified only once, and
 * the two records would otherwise need two tokens.
 */

import { TURNSTILE_HEADER } from '$lib/turnstile';

export type InquiryVenue = {
  id: number;
  slug: string;
  name: string;
  city: string;
};

export type VenueInquiry = {
  venue: InquiryVenue;
  name: string;
  whatsapp: string;
  email: string;
  weddingDate: string;
  bestTimeToReach: string;
  /** Null when the couple did not tick the tour box. */
  tour: { visitDate: string; partySize: number } | null;
  locale: string;
};

/**
 * `tour` is 'skipped' when none was asked for or pricing never landed, 'ok' when
 * booked, and otherwise the API's error code, so the caller can pick a message.
 */
export type InquiryResult = { pricing: 'ok' | 'failed'; tour: string };

const FAILED: InquiryResult = { pricing: 'failed', tour: 'skipped' };

/** The browser half: one POST, and any failure to reach the server is a failed pricing request. */
export async function submitVenueInquiry(
  inquiry: VenueInquiry,
  fetcher: typeof fetch,
  captchaToken = ''
): Promise<InquiryResult> {
  try {
    const response = await fetcher('/api/venue-inquiry', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        [TURNSTILE_HEADER]: captchaToken
      },
      body: JSON.stringify(inquiry)
    });
    if (!response.ok) return FAILED;
    return (await response.json()) as InquiryResult;
  } catch {
    return FAILED;
  }
}

/** The server half: files the pricing request, then the tour, straight with the API. */
export async function forwardVenueInquiry(
  inquiry: VenueInquiry,
  fetcher: typeof fetch,
  apiBase: string
): Promise<InquiryResult> {
  const { venue } = inquiry;

  const pricingLanded = await post(fetcher, `${apiBase}/api/v1/public/venue-pricing-requests`, {
    name: inquiry.name,
    whatsapp: inquiry.whatsapp,
    email: inquiry.email || null,
    wedding_date: inquiry.weddingDate || null,
    best_time_to_reach: inquiry.bestTimeToReach,
    venue_id: venue.id,
    venue_slug: venue.slug,
    venue_name: venue.name
  }).then(
    (response) => response.ok,
    () => false
  );

  // The tour waits on pricing: a retry after a failed pricing request would
  // otherwise book the same tour twice, and the API refuses the second one.
  if (!pricingLanded) return FAILED;
  if (!inquiry.tour) return { pricing: 'ok', tour: 'skipped' };

  try {
    const response = await post(fetcher, `${apiBase}/api/v1/public/tour/register`, {
      name: inquiry.name,
      email: inquiry.email,
      mobile: inquiry.whatsapp || null,
      venue_id: venue.id,
      venue_name: venue.name,
      // The venue's city is what routes the booking to a branch.
      city: venue.city,
      visit_date: inquiry.tour.visitDate,
      party_size: Math.min(Math.max(Math.trunc(inquiry.tour.partySize) || 1, 1), 20),
      locale: inquiry.locale
    });
    if (response.ok) return { pricing: 'ok', tour: 'ok' };

    const payload: { error?: { code?: string } } = await response.json().catch(() => ({}));
    return { pricing: 'ok', tour: payload.error?.code ?? 'generic' };
  } catch {
    return { pricing: 'ok', tour: 'generic' };
  }
}

function post(fetcher: typeof fetch, url: string, body: unknown): Promise<Response> {
  return fetcher(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}
