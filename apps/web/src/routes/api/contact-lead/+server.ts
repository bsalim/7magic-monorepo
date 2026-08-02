import { json } from '@sveltejs/kit';

import { getApiBaseUrl } from '$lib/api';

import type { RequestHandler } from './$types';

/**
 * Proxies the header consultation modal to the API.
 *
 * The /contact page posts through a form action, but the modal opens on every
 * route, so it needs an endpoint of its own. Posting through the app server
 * keeps the API base URL server-side and avoids a CORS round trip, matching
 * the venue-pricing-request proxy.
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
	const payload = await request.json();

	const response = await fetch(`${getApiBaseUrl()}/api/v1/public/contact-leads`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});

	const body = await response.json().catch(() => ({}));
	return json(body, { status: response.status });
};
