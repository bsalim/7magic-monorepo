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
  const registrationQuery = new URLSearchParams({ event_id: params.id });
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
      throw error(404, 'Event not found.');
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
    const branchValue = String(form.get('branch_id') ?? '').trim();

    try {
      await apiFetch(`/api/v1/admin/events/${params.id}`, {
        method: 'PATCH',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          branch_id: branchValue ? Number(branchValue) : null,
          name: String(form.get('name') ?? '').trim(),
          description_html: String(form.get('description_html') ?? ''),
          venue: String(form.get('venue') ?? '').trim() || null,
          capacity: form.get('capacity') ? Number(form.get('capacity')) : null,
          registration_opens_at: String(form.get('registration_opens_at') ?? '') || null,
          registration_closes_at: String(form.get('registration_closes_at') ?? '') || null,
          event_start_at: String(form.get('event_start_at') ?? '') || null,
          event_end_at: String(form.get('event_end_at') ?? '') || null,
          is_active: form.get('is_active') === 'on'
        })
      });
    } catch (cause) {
      return fail(400, {
        ok: false,
        message:
          cause instanceof ApiRequestError && cause.code === 'branch_forbidden'
            ? 'You do not have access to that branch.'
            : 'Could not save the event.'
      });
    }

    return { ok: true, message: 'Event saved.' };
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
          event_id: Number(params.id),
          name: String(form.get('name') ?? '').trim(),
          email: String(form.get('email') ?? '').trim(),
          mobile: String(form.get('mobile') ?? '').trim() || null,
          visit_date: String(form.get('visit_date') ?? '') || null,
          visit_slot: String(form.get('visit_slot') ?? '').trim() || null,
          notes: String(form.get('notes') ?? '').trim() || null,
          guests: []
        })
      });
    } catch (cause) {
      const code = cause instanceof ApiRequestError ? cause.code : '';
      const messages: Record<string, string> = {
        already_registered: 'That email is already registered for this event.',
        event_full: 'This event is fully booked.',
        branch_closed: 'The branch is closed on that date.',
        registration_closed: 'Registration has closed.'
      };
      return fail(400, { ok: false, message: messages[code] ?? 'Could not save the registration.' });
    }

    return { ok: true, message: 'Registration added.' };
  },

  updateRegistration: async ({ locals, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const id = String(form.get('registration_id') ?? '').trim();

    const body: Record<string, unknown> = {};
    if (form.has('status')) body.status = String(form.get('status'));
    if (form.has('follow_up')) body.follow_up = form.get('follow_up') === 'true';
    if (form.has('notes')) body.notes = String(form.get('notes'));

    try {
      await apiFetch(`/api/v1/admin/event-registrations/${id}`, {
        method: 'PATCH',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(body)
      });
    } catch {
      return fail(400, { ok: false, message: 'Could not update the registration.' });
    }

    return { ok: true, message: 'Registration updated.' };
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
      return fail(400, { ok: false, message: 'Could not save the template.' });
    }

    return { ok: true, message: 'Template saved.' };
  }
};
