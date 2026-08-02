import { fail, redirect } from '@sveltejs/kit';

import type { AdminShowcaseSummary } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const data = await apiFetch<{ items: AdminShowcaseSummary[] }>('/api/v1/admin/showcases', {
      token: locals.token
    });
    return { error: '', showcases: data.items };
  } catch (error) {
    return {
      error:
        error instanceof ApiRequestError
          ? error.message
          : 'Unable to load showcases. Check the API server and try again.',
      showcases: [] as AdminShowcaseSummary[]
    };
  }
};

export const actions: Actions = {
  delete: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const id = String((await request.formData()).get('id') ?? '').trim();
    if (!id) {
      return fail(400, { deleteMessage: 'Missing showcase id.' });
    }

    try {
      await apiFetch(`/api/v1/admin/showcases/${id}`, { method: 'DELETE', token: locals.token });
      return { deleteMessage: 'Showcase deleted.' };
    } catch (error) {
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        deleteMessage:
          error instanceof ApiRequestError ? error.message : 'Unable to delete the showcase.'
      });
    }
  }
};
