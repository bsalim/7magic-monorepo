import { json } from '@sveltejs/kit';

import { getApiBaseUrl } from '$lib/api';
import { rejectUnlessHuman } from '$lib/server/turnstile';
import { forwardVenueInquiry, type VenueInquiry } from '$lib/venue-inquiry';

import type { RequestHandler } from './$types';

/**
 * The venue pricing modal: a pricing request and an optional tour booking,
 * filed in that order after one captcha check. See $lib/venue-inquiry.
 *
 * Field validation stays the API's; this only refuses a body too malformed to
 * build the two requests from.
 */
export const POST: RequestHandler = async (event) => {
	const rejected = await rejectUnlessHuman(event);
	if (rejected) return rejected;

	const inquiry = (await event.request.json().catch(() => null)) as VenueInquiry | null;
	if (
		!inquiry ||
		typeof inquiry !== 'object' ||
		!inquiry.venue ||
		typeof inquiry.venue !== 'object'
	) {
		return json({ ok: false }, { status: 400 });
	}

	const result = await forwardVenueInquiry(inquiry, event.fetch, getApiBaseUrl());
	if (result.tour !== 'ok' && result.tour !== 'skipped') {
		// The couple's pricing request already landed and they see a soft notice,
		// so this line is the only record that a tour booking was lost.
		console.error(`[tour] modal register failed: ${result.tour}`);
	}
	return json(result);
};
