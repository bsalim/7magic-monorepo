import { fail, redirect } from '@sveltejs/kit';

import type { AdminBranch, AdminEvent } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, url }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  const branchId = url.searchParams.get('branchId') ?? '';
  const query = branchId ? `?branchId=${encodeURIComponent(branchId)}` : '';

  try {
    const [events, branches] = await Promise.all([
      apiFetch<{ items: AdminEvent[] }>(`/api/v1/admin/events${query}`, { token: locals.token }),
      apiFetch<{ items: AdminBranch[] }>('/api/v1/admin/branches', { token: locals.token })
    ]);

    return { error: '', events: events.items, branches: branches.items, branchId };
  } catch (error) {
    return {
      error: error instanceof ApiRequestError ? error.message : 'Tidak bisa memuat acara.',
      events: [] as AdminEvent[],
      branches: [] as AdminBranch[],
      branchId
    };
  }
};

export const actions: Actions = {
  create: async ({ locals, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const form = await request.formData();
    const branchValue = String(form.get('branchId') ?? '').trim();

    // The redirect is thrown OUTSIDE the try: SvelteKit signals redirects by
    // throwing, so a `throw redirect(...)` inside a try lands in the catch and
    // gets swallowed as a failure.
    let createdId: number;
    try {
      const created = await apiFetch<{ data: AdminEvent }>('/api/v1/admin/events', {
        method: 'POST',
        token: locals.token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          // "" means every branch; only an org-wide user may do that and the API enforces it.
          branchId: branchValue ? Number(branchValue) : null,
          name: String(form.get('name') ?? '').trim(),
          venue: String(form.get('venue') ?? '').trim() || null,
          capacity: form.get('capacity') ? Number(form.get('capacity')) : null,
          registrationOpensAt: String(form.get('registrationOpensAt') ?? '') || null,
          registrationClosesAt: String(form.get('registrationClosesAt') ?? '') || null
        })
      });
      createdId = created.data.id;
    } catch (error) {
      return fail(400, {
        ok: false,
        message:
          error instanceof ApiRequestError && error.code === 'branch_forbidden'
            ? 'Anda tidak punya akses ke cabang tersebut.'
            : 'Acara gagal dibuat.'
      });
    }

    throw redirect(303, `/events/${createdId}`);
  }
};
