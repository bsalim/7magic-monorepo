import { json } from '@sveltejs/kit';

import { getApiBaseUrl } from '$lib/api';

import type { RequestHandler } from './$types';

/**
 * Proxies the wedding tools' lead gate to the API.
 *
 * Same reason as the contact-lead and venue-pricing proxies: the gate runs in
 * the browser on any tool page, and posting through the app server keeps the
 * API base URL server-side and avoids a CORS round trip. The body passes
 * through untouched; validation, the honeypot and notifications are the API's.
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
	const payload = await request.json().catch(() => null);
	if (!payload || typeof payload !== 'object') {
		return json({ ok: false }, { status: 400 });
	}

	let response: Response;
	try {
		response = await fetch(`${getApiBaseUrl()}/api/v1/public/tool-leads`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload)
		});
	} catch {
		// An unreachable API is a gateway failure, not a crash: the gate shows its
		// retry message and keeps what the couple typed.
		return json({ ok: false }, { status: 502 });
	}

	const body = await response.json().catch(() => ({}));
	return json(body, { status: response.status });
};
