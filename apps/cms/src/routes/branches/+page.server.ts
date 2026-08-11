import { fail, redirect } from '@sveltejs/kit';

import type { AdminBranch } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const data = await apiFetch<{ items: AdminBranch[] }>('/api/v1/admin/branches', {
      token: locals.token
    });
    return { error: '', branches: data.items };
  } catch (error) {
    return {
      error:
        error instanceof ApiRequestError
          ? error.message
          : 'Unable to load branches. Check the API server and try again.',
      branches: [] as AdminBranch[]
    };
  }
};

export const actions: Actions = {
  create: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const payload = {
      slug: String(form.get('slug') ?? '').trim(),
      name: String(form.get('name') ?? '').trim(),
      city: String(form.get('city') ?? 'jakarta').trim(),
      address_line1: String(form.get('address_line1') ?? '').trim(),
      timezone: String(form.get('timezone') ?? 'Asia/Jakarta').trim(),
      country_code: 'ID'
    };

    if (!payload.slug || !payload.name) {
      return fail(400, { ok: false, message: 'A branch slug and name are required.' });
    }

    try {
      await apiFetch('/api/v1/admin/branches', {
        method: 'POST',
        token: locals.token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (error) {
      return fail(400, {
        ok: false,
        message:
          error instanceof ApiRequestError && error.code === 'branch_slug_conflict'
            ? 'That branch slug is already taken.'
            : 'Could not create the branch.'
      });
    }

    return { ok: true, message: 'Branch created.' };
  },

  delete: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const id = String(form.get('id') ?? '').trim();
    if (!id) {
      return fail(400, { ok: false, message: 'Missing branch id.' });
    }

    try {
      await apiFetch(`/api/v1/admin/branches/${id}`, { method: 'DELETE', token: locals.token });
    } catch (error) {
      return fail(400, {
        ok: false,
        message: error instanceof ApiRequestError ? error.message : 'Could not delete the branch.'
      });
    }

    return { ok: true, message: 'Branch deleted.' };
  }
};
