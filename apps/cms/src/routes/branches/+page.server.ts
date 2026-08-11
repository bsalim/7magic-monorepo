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
          : 'Tidak bisa memuat cabang. Periksa server API lalu coba lagi.',
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
      addressLine1: String(form.get('addressLine1') ?? '').trim(),
      timezone: String(form.get('timezone') ?? 'Asia/Jakarta').trim(),
      countryCode: 'ID'
    };

    if (!payload.slug || !payload.name) {
      return fail(400, { ok: false, message: 'Slug dan nama cabang wajib diisi.' });
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
            ? 'Slug cabang sudah dipakai.'
            : 'Cabang gagal dibuat.'
      });
    }

    return { ok: true, message: 'Cabang dibuat.' };
  },

  delete: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const id = String(form.get('id') ?? '').trim();
    if (!id) {
      return fail(400, { ok: false, message: 'Id cabang tidak ada.' });
    }

    try {
      await apiFetch(`/api/v1/admin/branches/${id}`, { method: 'DELETE', token: locals.token });
    } catch (error) {
      return fail(400, {
        ok: false,
        message: error instanceof ApiRequestError ? error.message : 'Cabang gagal dihapus.'
      });
    }

    return { ok: true, message: 'Cabang dihapus.' };
  }
};
