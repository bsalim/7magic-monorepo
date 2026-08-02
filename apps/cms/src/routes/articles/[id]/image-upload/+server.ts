import { error, json } from '@sveltejs/kit';

import { ApiRequestError, apiFetch } from '$lib/server/api';

import type { RequestHandler } from './$types';

/**
 * Proxies an inline article image to the API.
 *
 * Quill uploads from the browser, which has no admin token -- that lives in an
 * httpOnly cookie the client cannot read. Going through the app server keeps
 * the token server-side.
 */
export const POST: RequestHandler = async ({ locals, params, request }) => {
  if (!locals.token) {
    throw error(401, 'Not signed in.');
  }

  const incoming = await request.formData();
  const file = incoming.get('file');
  if (!(file instanceof File) || file.size === 0) {
    throw error(400, 'Choose an image to upload.');
  }

  const upstream = new FormData();
  upstream.set('file', file);

  try {
    const result = await apiFetch<{ url: string }>(
      `/api/v1/admin/articles/${params.id}/images`,
      { method: 'POST', body: upstream, token: locals.token }
    );
    return json(result);
  } catch (cause) {
    throw error(
      cause instanceof ApiRequestError ? cause.status : 500,
      cause instanceof ApiRequestError ? cause.message : 'Unable to upload the image.'
    );
  }
};
