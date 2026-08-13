import { fail } from '@sveltejs/kit';

import { fetchJson, getApiBaseUrl } from '$lib/api';
import type { TourVenue } from '$lib/tour';

import type { Actions, PageServerLoad } from './$types';

type TourFormPayload = { venues: TourVenue[]; cities: string[]; open: boolean };

export const load: PageServerLoad = async ({ fetch, url }) => {
  let payload: TourFormPayload = { venues: [], cities: [], open: false };
  try {
    const data = await fetchJson<{ data: TourFormPayload }>('/api/v1/public/tour', fetch);
    payload = data.data;
  } catch {
    // An empty, closed payload rather than a 500: the page renders "not taking
    // bookings" from `open`, which is a better failure than a broken funnel.
  }

  // Resolved against the catalogue rather than trusted: an unknown ?venue= should
  // fall through to the normal form, not lock the guest to a venue we cannot name.
  const requested = url.searchParams.get('venue');
  const lockedVenue = requested
    ? (payload.venues.find((venue) => String(venue.id) === requested) ?? null)
    : null;

  return { ...payload, lockedVenue };
};

export const actions: Actions = {
  default: async ({ fetch, request }) => {
    const form = await request.formData();

    const partySize = Number(form.get('party_size') ?? 1);
    const venueId = String(form.get('venue_id') ?? '').trim();

    const response = await fetch(`${getApiBaseUrl()}/api/v1/public/tour/register`, {
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
    });

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

    // Every branch below costs a lead, and the guest only ever sees "coba lagi".
    // Without this line the server keeps no record of whether the API rejected
    // the booking or fell over, which leaves the failure undiagnosable from the
    // outside -- exactly the position this endpoint was in.
    console.error(`[tour] register failed ${response.status}: ${body.slice(0, 500)}`);

    return fail(response.status === 422 ? 422 : 409, {
      ok: false,
      code: payload.error?.code ?? 'generic'
    });
  }
};
