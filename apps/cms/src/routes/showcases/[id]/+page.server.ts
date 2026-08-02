import { error, fail, redirect } from '@sveltejs/kit';

import type { AdminShowcaseDetail } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';
import { readShowcaseForm } from '$lib/server/showcase-form';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const showcase = await apiFetch<AdminShowcaseDetail>(
      `/api/v1/admin/showcases/${params.id}`,
      { token: locals.token }
    );
    return { showcase };
  } catch (cause) {
    throw error(
      cause instanceof ApiRequestError ? cause.status : 500,
      cause instanceof ApiRequestError ? cause.message : 'Unable to load the showcase.'
    );
  }
};

export const actions: Actions = {
  save: async ({ locals, params, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const { values, payload, errors } = readShowcaseForm(await request.formData());
    if (Object.keys(errors).length) {
      return fail(400, { values, errors, message: 'Check the highlighted fields.' });
    }

    try {
      await apiFetch(`/api/v1/admin/showcases/${params.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        token: locals.token
      });
    } catch (cause) {
      return fail(cause instanceof ApiRequestError ? cause.status : 500, {
        values,
        errors: {},
        message:
          cause instanceof ApiRequestError ? cause.message : 'Unable to save the showcase.'
      });
    }

    return { saved: true, values, errors: {}, message: '' };
  }
};
