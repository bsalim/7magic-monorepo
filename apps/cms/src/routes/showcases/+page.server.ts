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

const STATUSES = ['draft', 'published', 'archived'] as const;

export const actions: Actions = {
  /**
   * Publish/unpublish straight from the list. PATCHes status alone -- the API
   * updates only the fields present in the body, so the row's text and images
   * are untouched by this.
   */
  setStatus: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const id = String(form.get('id') ?? '').trim();
    const status = String(form.get('status') ?? '').trim();
    if (!id || !STATUSES.includes(status as (typeof STATUSES)[number])) {
      return fail(400, { statusMessage: 'Missing showcase id or status.' });
    }

    try {
      await apiFetch(`/api/v1/admin/showcases/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
        token: locals.token
      });
      return {
        statusMessage:
          status === 'published' ? 'Showcase published.' : 'Showcase moved to draft.'
      };
    } catch (error) {
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        statusMessage:
          error instanceof ApiRequestError ? error.message : 'Unable to change the status.'
      });
    }
  },

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
