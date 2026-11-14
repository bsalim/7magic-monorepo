import { fail } from '@sveltejs/kit';
import { fetchJson, type ContactLeadResponse } from '$lib/api';
import * as m from '$lib/paraglide/messages';
import { clientIp, TURNSTILE_FIELD, verifyTurnstile } from '$lib/server/turnstile';

export const actions = {
  default: async ({ fetch, request, url, getClientAddress }) => {
    const form = await request.formData();
    if (!(await verifyTurnstile(form.get(TURNSTILE_FIELD), clientIp(getClientAddress), fetch))) {
      return fail(400, { error: m.captcha_error() });
    }
    const payload = {
      name: String(form.get('name') ?? ''),
      email: String(form.get('email') ?? ''),
      phone: String(form.get('phone') ?? ''),
      message: String(form.get('message') ?? ''),
      source_path: url.pathname
    };

    try {
      const lead = await fetchJson<ContactLeadResponse>('/api/v1/public/contact-leads', fetch, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload)
      });
      return { lead };
    } catch {
      return fail(400, {
        error: 'Please check your contact details and message.'
      });
    }
  }
};
