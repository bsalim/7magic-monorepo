import { json } from '@sveltejs/kit';

import { getApiBaseUrl } from '$lib/api';

import type { RequestHandler } from './$types';

/**
 * Proxies the venue pricing modal to the API.
 *
 * The modal runs in the browser, so it cannot reach the API host directly in
 * every environment. Posting through the app server keeps the API base URL
 * server-side and avoids a CORS round trip.
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
	const payload = await request.json();

	const response = await fetch(`${getApiBaseUrl()}/api/v1/public/venue-pricing-requests`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});

	const body = await response.json().catch(() => ({}));
	return json(body, { status: response.status });
};
