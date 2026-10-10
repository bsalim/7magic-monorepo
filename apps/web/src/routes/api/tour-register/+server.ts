import { json } from '@sveltejs/kit';

import { getApiBaseUrl } from '$lib/api';

import type { RequestHandler } from './$types';

/**
 * Proxies the tour opt-in on the venue pricing modal to the API, for the same
 * reason as the venue-pricing-request proxy: the modal runs in the browser and
 * the API base URL stays server-side.
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
	const payload = await request.json();

	const response = await fetch(`${getApiBaseUrl()}/api/v1/public/tour/register`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});

	const body = await response.json().catch(() => ({}));
	if (!response.ok) {
		// The couple's pricing request already landed and they see a soft notice,
		// so this line is the only record that a tour booking was lost.
		console.error(`[tour] modal register failed ${response.status}: ${JSON.stringify(body).slice(0, 500)}`);
	}
	return json(body, { status: response.status });
};
