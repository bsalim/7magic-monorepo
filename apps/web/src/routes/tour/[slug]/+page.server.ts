import { error, fail } from '@sveltejs/kit';

import { fetchJson, getApiBaseUrl } from '$lib/api';
import type { OpeningHour } from '$lib/tour-availability';

import type { Actions, PageServerLoad } from './$types';

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
  opening_hours: OpeningHour[];
  closed_dates: string[];
};

export const load: PageServerLoad = async ({ fetch, params }) => {
  try {
    const data = await fetchJson<{ data: TourBranchDetail }>(
      `/api/v1/public/tour/branches/${params.slug}`,
      fetch
    );
    return data.data;
  } catch {
    throw error(404, 'Branch not found');
  }
};

export const actions: Actions = {
  default: async ({ fetch, params, request }) => {
    const form = await request.formData();

    const guestCount = Number(form.get('guests') ?? 0);
    const guests = Array.from({ length: Math.max(0, Math.min(guestCount, 10)) }, (_, index) => ({
      name: String(form.get(`guest-${index}`) ?? `Tamu ${index + 1}`).trim() || `Tamu ${index + 1}`
    }));

    const response = await fetch(
      `${getApiBaseUrl()}/api/v1/public/tour/branches/${params.slug}/register`,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          name: String(form.get('name') ?? '').trim(),
          email: String(form.get('email') ?? '').trim(),
          mobile: String(form.get('mobile') ?? '').trim() || null,
          visit_date: String(form.get('visit_date') ?? '') || null,
          visit_slot: String(form.get('visit_slot') ?? '') || null,
          guests
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
