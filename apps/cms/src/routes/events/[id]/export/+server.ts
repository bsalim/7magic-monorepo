import { redirect } from '@sveltejs/kit';

import { getApiBaseUrl } from '$lib/server/api';

import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ locals, params }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  // apiFetch parses JSON, and this endpoint returns CSV -- so call through
  // directly and stream the body back with its filename intact.
  const response = await fetch(
    `${getApiBaseUrl()}/api/v1/admin/event-registrations/export?event_id=${params.id}`,
    { headers: { Authorization: `Bearer ${locals.token}` } }
  );

  if (!response.ok) {
    return new Response('Export failed.', { status: response.status });
  }

  return new Response(response.body, {
    headers: {
      'content-type': 'text/csv',
      'content-disposition': `attachment; filename="event-${params.id}-registrations.csv"`
    }
  });
};
