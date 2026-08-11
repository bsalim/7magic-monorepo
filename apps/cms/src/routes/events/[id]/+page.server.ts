import { error, fail, redirect } from '@sveltejs/kit';

import type { AdminBranch, AdminEmailTemplate, AdminEvent, AdminRegistration } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params, url }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  const statusFilter = url.searchParams.get('status') ?? '';
  const search = url.searchParams.get('q') ?? '';
  const registrationQuery = new URLSearchParams({ eventId: params.id });
  if (statusFilter) registrationQuery.set('status', statusFilter);
  if (search) registrationQuery.set('q', search);

  try {
    const [event, registrations, templates, branches] = await Promise.all([
      apiFetch<{ data: AdminEvent }>(`/api/v1/admin/events/${params.id}`, { token: locals.token }),
      apiFetch<{ items: AdminRegistration[] }>(
        `/api/v1/admin/event-registrations?${registrationQuery.toString()}`,
        { token: locals.token }
      ),
      apiFetch<{ data: { placeholders: string[]; templates: AdminEmailTemplate[] } }>(
        `/api/v1/admin/events/${params.id}/email-templates`,
        { token: locals.token }
      ),
      apiFetch<{ items: AdminBranch[] }>('/api/v1/admin/branches', { token: locals.token })
    ]);

    return {
      event: event.data,
      registrations: registrations.items,
      placeholders: templates.data.placeholders,
      templates: templates.data.templates,
      branches: branches.items,
      statusFilter,
      search
    };
  } catch (cause) {
    if (cause instanceof ApiRequestError && cause.status === 404) {
      throw error(404, 'Acara tidak ditemukan.');
    }
    throw cause;
  }
};

const requireToken = (locals: App.Locals) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }
  return locals.token;
};

export const actions: Actions = {
  details: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const branchValue = String(form.get('branchId') ?? '').trim();

    try {
      await apiFetch(`/api/v1/admin/events/${params.id}`, {
        method: 'PATCH',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          branchId: branchValue ? Number(branchValue) : null,
          name: String(form.get('name') ?? '').trim(),
          descriptionHtml: String(form.get('descriptionHtml') ?? ''),
          venue: String(form.get('venue') ?? '').trim() || null,
          capacity: form.get('capacity') ? Number(form.get('capacity')) : null,
          registrationOpensAt: String(form.get('registrationOpensAt') ?? '') || null,
          registrationClosesAt: String(form.get('registrationClosesAt') ?? '') || null,
          eventStartAt: String(form.get('eventStartAt') ?? '') || null,
          eventEndAt: String(form.get('eventEndAt') ?? '') || null,
          isActive: form.get('isActive') === 'on'
        })
      });
    } catch (cause) {
      return fail(400, {
        ok: false,
        message:
          cause instanceof ApiRequestError && cause.code === 'branch_forbidden'
            ? 'Anda tidak punya akses ke cabang tersebut.'
            : 'Acara gagal disimpan.'
      });
    }

    return { ok: true, message: 'Acara tersimpan.' };
  },

  addRegistration: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();

    try {
      await apiFetch('/api/v1/admin/event-registrations', {
        method: 'POST',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          eventId: Number(params.id),
          name: String(form.get('name') ?? '').trim(),
          email: String(form.get('email') ?? '').trim(),
          mobile: String(form.get('mobile') ?? '').trim() || null,
          visitDate: String(form.get('visitDate') ?? '') || null,
          visitSlot: String(form.get('visitSlot') ?? '').trim() || null,
          notes: String(form.get('notes') ?? '').trim() || null,
          guests: []
        })
      });
    } catch (cause) {
      const code = cause instanceof ApiRequestError ? cause.code : '';
      const messages: Record<string, string> = {
        already_registered: 'Email ini sudah terdaftar untuk acara tersebut.',
        event_full: 'Kuota acara sudah penuh.',
        branch_closed: 'Cabang tutup pada tanggal tersebut.',
        registration_closed: 'Pendaftaran sudah ditutup.'
      };
      return fail(400, { ok: false, message: messages[code] ?? 'Pendaftaran gagal disimpan.' });
    }

    return { ok: true, message: 'Pendaftaran ditambahkan.' };
  },

  updateRegistration: async ({ locals, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const id = String(form.get('registrationId') ?? '').trim();

    const body: Record<string, unknown> = {};
    if (form.has('status')) body.status = String(form.get('status'));
    if (form.has('followUp')) body.followUp = form.get('followUp') === 'true';
    if (form.has('notes')) body.notes = String(form.get('notes'));

    try {
      await apiFetch(`/api/v1/admin/event-registrations/${id}`, {
        method: 'PATCH',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(body)
      });
    } catch {
      return fail(400, { ok: false, message: 'Pendaftaran gagal diperbarui.' });
    }

    return { ok: true, message: 'Pendaftaran diperbarui.' };
  },

  saveTemplate: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const kind = String(form.get('kind') ?? '').trim();

    try {
      await apiFetch(`/api/v1/admin/events/${params.id}/email-templates/${kind}`, {
        method: 'PUT',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          subject: String(form.get('subject') ?? ''),
          body: String(form.get('body') ?? ''),
          enabled: form.get('enabled') === 'on'
        })
      });
    } catch {
      return fail(400, { ok: false, message: 'Template gagal disimpan.' });
    }

    return { ok: true, message: 'Template tersimpan.' };
  }
};
