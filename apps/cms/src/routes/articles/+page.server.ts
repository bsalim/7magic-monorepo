import { fail, redirect } from '@sveltejs/kit';

import type { AdminArticleSummary } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const data = await apiFetch<{ items: AdminArticleSummary[] }>('/api/v1/admin/articles', {
      token: locals.token
    });
    return { error: '', articles: data.items };
  } catch (error) {
    return {
      error:
        error instanceof ApiRequestError
          ? error.message
          : 'Unable to load articles. Check the API server and try again.',
      articles: [] as AdminArticleSummary[]
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
      return fail(400, { deleteMessage: 'Missing article id.' });
    }

    try {
      await apiFetch(`/api/v1/admin/articles/${id}`, { method: 'DELETE', token: locals.token });
      return { deleteMessage: 'Article moved to trash.' };
    } catch (error) {
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        deleteMessage:
          error instanceof ApiRequestError ? error.message : 'Unable to delete the article.'
      });
    }
  }
};
