import { error, json } from '@sveltejs/kit';

import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { RequestHandler } from './$types';

/**
 * Proxies a Dropzone multipart upload to the admin temp-photo endpoint,
 * attaching the server-side session token. The browser uploads here with a
 * generated `temp_venue_id`; the photos are claimed when the venue is created.
 */
export const POST: RequestHandler = async ({ request, locals }) => {
  if (!locals.token) {
    throw error(401, 'Your session has expired. Sign in again.');
  }

  const incoming = await request.formData();
  const file = incoming.get('file');
  if (!(file instanceof File) || file.size === 0) {
    throw error(400, 'No image file was provided.');
  }

  const upstream = new FormData();
  upstream.set('file', file);
  const tempVenueId = incoming.get('temp_venue_id');
  if (typeof tempVenueId === 'string' && tempVenueId) {
    upstream.set('temp_venue_id', tempVenueId);
  }
  const altText = incoming.get('alt_text');
  if (typeof altText === 'string' && altText) {
    upstream.set('alt_text', altText);
  }
  const sortOrder = incoming.get('sort_order');
  upstream.set('sort_order', typeof sortOrder === 'string' && sortOrder ? sortOrder : '0');

  try {
    const photo = await apiFetch('/api/v1/admin/uploads/venue-photo', {
      method: 'POST',
      body: upstream,
      token: locals.token
    });
    return json(photo, { status: 201 });
  } catch (err) {
    if (err instanceof ApiRequestError) {
      throw error(err.status, err.message);
    }
    throw error(502, 'Unable to reach the upload service.');
  }
};
