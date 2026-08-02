import { fail, redirect } from '@sveltejs/kit';

import type { AdminShowcaseDetail } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';
import { readShowcaseForm } from '$lib/server/showcase-form';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }
  return {};
};

export const actions: Actions = {
  default: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const { values, payload, errors } = readShowcaseForm(await request.formData());
    if (Object.keys(errors).length) {
      return fail(400, { values, errors, message: 'Check the highlighted fields.' });
    }

    let created: AdminShowcaseDetail;
    try {
      created = await apiFetch<AdminShowcaseDetail>('/api/v1/admin/showcases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        token: locals.token
      });
    } catch (error) {
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        values,
        errors: {},
        message:
          error instanceof ApiRequestError ? error.message : 'Unable to create the showcase.'
      });
    }

    throw redirect(303, `/showcases/${created.id}`);
  }
};
