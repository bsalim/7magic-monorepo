import { fail, redirect } from '@sveltejs/kit';

import type { AdminVenue } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const venueData = await apiFetch<{ items: AdminVenue[] }>('/api/v1/admin/venues', {
      token: locals.token
    });

    return {
      error: '',
      venues: venueData.items
    };
  } catch (error) {
    return {
      error:
        error instanceof ApiRequestError
          ? error.message
          : 'Unable to load venues. Check the API server and try again.',
      venues: [] as AdminVenue[]
    };
  }
};

export const actions: Actions = {
  delete: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const formData = await request.formData();
    const id = String(formData.get('id') ?? '').trim();

    if (!id) {
      return fail(400, { ok: false, message: 'Missing venue id.' });
    }

    try {
      await apiFetch(`/api/v1/admin/venues/${id}`, {
        method: 'DELETE',
        token: locals.token
      });

      return { ok: true, message: 'Venue deleted.' };
    } catch (error) {
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        ok: false,
        message:
          error instanceof ApiRequestError
            ? error.message
            : 'Unable to delete venue. Check the API server and try again.'
      });
    }
  }
};
