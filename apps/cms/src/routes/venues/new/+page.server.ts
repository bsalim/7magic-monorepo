import { fail, redirect } from '@sveltejs/kit';

import type { VenueDetail } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';
import {
  validateVenuePayload,
  venuePayloadFromForm,
  type VenueFormErrors,
  type VenueFormPayload
} from '$lib/server/venueForm';

import type { Actions, PageServerLoad } from './$types';

const defaultValues: VenueFormPayload = {
  name: '',
  slug: '',
  city: 'jakarta',
  district: '',
  address: '',
  stars: 5,
  description: '',
  price_start_from: null,
  price_for_total_pax: 0,
  status: 'draft'
};

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  return {
    values: defaultValues,
    // A fresh id so photos can be uploaded before the venue exists, then
    // claimed by the API when the venue is created.
    tempVenueId: crypto.randomUUID()
  };
};

export const actions: Actions = {
  default: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const formData = await request.formData();
    const values = venuePayloadFromForm(formData);
    const tempVenueId = formData.get('temp_venue_id');
    const errors = validateVenuePayload(values);
    if (Object.keys(errors).length) {
      return fail(400, {
        errors,
        message: 'Fix the highlighted venue fields.',
        values
      });
    }

    let venue: VenueDetail;
    try {
      venue = await apiFetch<VenueDetail>('/api/v1/admin/venues', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...values,
          temp_venue_id: typeof tempVenueId === 'string' && tempVenueId ? tempVenueId : undefined
        }),
        token: locals.token
      });
    } catch (error) {
      const apiErrors: VenueFormErrors = {};
      if (error instanceof ApiRequestError && error.code === 'slug_conflict') {
        apiErrors.slug = error.message;
        return fail(409, {
          errors: apiErrors,
          message: error.message,
          values
        });
      }

      return fail(500, {
        errors: apiErrors,
        message:
          error instanceof ApiRequestError
            ? error.message
            : 'Unable to create venue. Check the API server and try again.',
        values
      });
    }

    throw redirect(303, `/venues/${venue.id}`);
  }
};
