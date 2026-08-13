import { error, fail } from '@sveltejs/kit';

import { fetchJson, getApiBaseUrl } from '$lib/api';

import type { Actions, PageServerLoad } from './$types';

export type TourVenue = { id: number; name: string; city: string };

type TourBranchDetail = {
  branch: {
    id: number;
    slug: string;
    name: string;
    city: string;
    address_line1: string;
    address_line2: string | null;
    public_phone: string | null;
    public_email: string | null;
    whatsapp_number: string | null;
  };
  settings: {
    tour_intro_html: string | null;
    arrival_instructions: string | null;
    parking_notes: string | null;
  };
  event: {
    id: number;
    name: string;
    description_html: string;
    venue: string | null;
    registration_open: boolean;
    registration_closed_reason: string | null;
  } | null;
  venues: TourVenue[];
};

export const load: PageServerLoad = async ({ fetch, params, url }) => {
  try {
    const data = await fetchJson<{ data: TourBranchDetail }>(
      `/api/v1/public/tour/branches/${params.slug}`,
      fetch
    );
    // Carried from a venue's own page, so arriving from "book a tour here" lands
    // with that venue already chosen. Resolved against the catalogue rather than
    // trusted: an unknown id falls through to the normal fields.
    const requested = url.searchParams.get('venue');
    return {
      ...data.data,
      // Distinct venue cities, so this page offers the same list as the generic
      // one. The branch's own city is not it: the venue may well be elsewhere,
      // since the branch handles the booking rather than hosting it.
      cities: [...new Set(data.data.venues.map((venue) => venue.city))].sort(),
      lockedVenue: requested
        ? (data.data.venues.find((venue) => String(venue.id) === requested) ?? null)
        : null
    };
  } catch {
    throw error(404, 'Branch not found');
  }
};

export const actions: Actions = {
  default: async ({ fetch, params, request }) => {
    const form = await request.formData();

    const partySize = Number(form.get('party_size') ?? 1);
    const venueId = String(form.get('venue_id') ?? '').trim();

    const response = await fetch(
      `${getApiBaseUrl()}/api/v1/public/tour/branches/${params.slug}/register`,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          name: String(form.get('name') ?? '').trim(),
          email: String(form.get('email') ?? '').trim(),
          mobile: String(form.get('mobile') ?? '').trim() || null,
          venue_id: venueId ? Number(venueId) : null,
          venue_name: String(form.get('venue_name') ?? '').trim() || null,
          city: String(form.get('city') ?? '').trim() || null,
          visit_date: String(form.get('visit_date') ?? '') || null,
          // Clamped rather than trusted: the input has min/max, but a hand-rolled
          // POST does not have to honour them.
          party_size: Number.isFinite(partySize)
            ? Math.min(Math.max(Math.trunc(partySize), 1), 20)
            : 1
        })
      }
    );

    if (response.ok) {
      return { ok: true, code: '' };
    }

    // The API's error code drives which translated message the page shows, so the
    // copy stays in the message catalogue rather than in the server response.
    const body = await response.text();
    let payload: { error?: { code?: string } } = {};
    try {
      payload = JSON.parse(body);
    } catch {
      // Not JSON at all -- a 500, or a proxy error page. There is no code to map,
      // and the raw text is the only clue, which is what the log below carries.
    }

    // See the branch-less action: this path costs a lead and the guest only ever
    // sees "coba lagi", so the status and body are the only record there is.
    console.error(
      `[tour] register failed ${response.status} (${params.slug}): ${body.slice(0, 500)}`
    );

    return fail(response.status === 422 ? 422 : 409, {
      ok: false,
      code: payload.error?.code ?? 'generic'
    });
  }
};
