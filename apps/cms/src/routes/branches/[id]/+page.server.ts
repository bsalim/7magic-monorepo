import { error, fail, redirect } from '@sveltejs/kit';

import type { AdminBranch } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const data = await apiFetch<{ data: AdminBranch }>(`/api/v1/admin/branches/${params.id}`, {
      token: locals.token
    });
    return { branch: data.data };
  } catch (cause) {
    if (cause instanceof ApiRequestError && cause.status === 404) {
      throw error(404, 'Branch not found.');
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

    try {
      await apiFetch(`/api/v1/admin/branches/${params.id}`, {
        method: 'PATCH',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          name: String(form.get('name') ?? '').trim(),
          slug: String(form.get('slug') ?? '').trim(),
          address_line1: String(form.get('address_line1') ?? '').trim(),
          address_line2: String(form.get('address_line2') ?? '').trim() || null,
          city: String(form.get('city') ?? '').trim(),
          postal_code: String(form.get('postal_code') ?? '').trim() || null,
          timezone: String(form.get('timezone') ?? '').trim(),
          public_phone: String(form.get('public_phone') ?? '').trim() || null,
          public_email: String(form.get('public_email') ?? '').trim() || null,
          whatsapp_number: String(form.get('whatsapp_number') ?? '').trim() || null,
          website_url: String(form.get('website_url') ?? '').trim() || null,
          active: form.get('active') === 'on',
          bookable: form.get('bookable') === 'on',
          is_default: form.get('is_default') === 'on'
        })
      });
    } catch (cause) {
      return fail(400, {
        ok: false,
        message:
          cause instanceof ApiRequestError && cause.code === 'branch_slug_conflict'
            ? 'That branch slug is already taken.'
            : 'Could not save your changes.'
      });
    }

    return { ok: true, message: 'Branch details saved.' };
  },

  settings: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();

    // One address per line in the textarea; blank lines dropped.
    const recipients = String(form.get('tour_notification_recipients') ?? '')
      .split(/[\n,]/)
      .map((value) => value.trim())
      .filter(Boolean);

    try {
      await apiFetch(`/api/v1/admin/branches/${params.id}/settings`, {
        method: 'PUT',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          sender_display_name: String(form.get('sender_display_name') ?? '').trim() || null,
          reply_to_email: String(form.get('reply_to_email') ?? '').trim() || null,
          tour_notification_recipients: recipients,
          tour_intro_html: String(form.get('tour_intro_html') ?? '').trim() || null,
          arrival_instructions: String(form.get('arrival_instructions') ?? '').trim() || null,
          parking_notes: String(form.get('parking_notes') ?? '').trim() || null
        })
      });
    } catch {
      return fail(400, { ok: false, message: 'Could not save the settings.' });
    }

    return { ok: true, message: 'Settings saved.' };
  },

  hours: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();

    // The whole week is replaced in one call: a day left unchecked is simply absent.
    const items = [1, 2, 3, 4, 5, 6, 7]
      .filter((day) => form.get(`day-${day}-active`) === 'on')
      .map((day) => ({
        day_of_week: day,
        opens_at_local: `${String(form.get(`day-${day}-opens`) ?? '10:00')}:00`,
        closes_at_local: `${String(form.get(`day-${day}-closes`) ?? '18:00')}:00`,
        active: true,
        sort_order: day
      }));

    try {
      await apiFetch(`/api/v1/admin/branches/${params.id}/opening-hours`, {
        method: 'PUT',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ items })
      });
    } catch {
      return fail(400, { ok: false, message: 'Could not save the opening hours.' });
    }

    return { ok: true, message: 'Opening hours saved.' };
  },

  addClosure: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const startDate = String(form.get('startDate') ?? '').trim();
    const endDate = String(form.get('endDate') ?? '').trim() || startDate;

    if (!startDate) {
      return fail(400, { ok: false, message: 'A start date is required.' });
    }

    try {
      await apiFetch(`/api/v1/admin/branches/${params.id}/closures`, {
        method: 'POST',
        token,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          starts_at_local: `${startDate}T00:00:00`,
          ends_at_local: `${endDate}T23:59:00`,
          full_day: true,
          reason: String(form.get('reason') ?? '').trim() || null,
          public_label: String(form.get('public_label') ?? '').trim() || null,
          active: true
        })
      });
    } catch {
      return fail(400, { ok: false, message: 'Could not add the closed date.' });
    }

    return { ok: true, message: 'Closed date added.' };
  },

  deleteClosure: async ({ locals, params, request }) => {
    const token = requireToken(locals);
    const form = await request.formData();
    const closureId = String(form.get('closureId') ?? '').trim();

    try {
      await apiFetch(`/api/v1/admin/branches/${params.id}/closures/${closureId}`, {
        method: 'DELETE',
        token
      });
    } catch {
      return fail(400, { ok: false, message: 'Could not delete the closed date.' });
    }

    return { ok: true, message: 'Closed date deleted.' };
  }
};
