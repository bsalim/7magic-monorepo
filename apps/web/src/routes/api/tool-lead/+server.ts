import { json } from '@sveltejs/kit';

import { getApiBaseUrl } from '$lib/api';
import { leadHeaders } from '$lib/server/api';
import { rejectUnlessHuman } from '$lib/server/turnstile';

import type { RequestHandler } from './$types';

/**
 * Proxies the wedding tools' lead gate to the API.
 *
 * Same reason as the contact-lead proxy and the venue-inquiry endpoint: the gate runs in
 * the browser on any tool page, and posting through the app server keeps the
 * API base URL server-side and avoids a CORS round trip. The body passes
 * through untouched; validation, the honeypot and notifications are the API's.
 *
 * Ba Zi's gate sits in front of the result itself, so its lead carries the
 * calculation and goes to the calculator's own endpoint, which also emails the
 * couple their copy.
 */
const TOOL_LEADS = '/api/v1/public/tool-leads';
const BAZI_LEADS = '/api/v1/public/bazi/leads';

export const POST: RequestHandler = async (event) => {
	const { request, fetch } = event;
	const rejected = await rejectUnlessHuman(event);
	if (rejected) return rejected;

	const payload = await request.json().catch(() => null);
	if (!payload || typeof payload !== 'object') {
		return json({ ok: false }, { status: 400 });
	}

	let response: Response;
	try {
		const path = (payload as { tool?: unknown }).tool === 'bazi' ? BAZI_LEADS : TOOL_LEADS;
		response = await fetch(`${getApiBaseUrl()}${path}`, {
			method: 'POST',
			headers: leadHeaders(),
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
