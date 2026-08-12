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
    // with that venue already chosen.
    return { ...data.data, preselectedVenueId: url.searchParams.get('venue') ?? '' };
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
    const payload = (await response.json().catch(() => ({}))) as {
      error?: { code?: string };
    };
    return fail(response.status === 422 ? 422 : 409, {
      ok: false,
      code: payload.error?.code ?? 'generic'
    });
  }
};
