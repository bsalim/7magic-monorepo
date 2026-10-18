import { redirect } from '@sveltejs/kit';

import { getApiBaseUrl } from '$lib/server/api';
import { leadFilterQuery, readLeadFilters } from '$lib/server/leadFilters';

import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ locals, url }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  const query = leadFilterQuery(readLeadFilters(url)).toString();

  // apiFetch parses JSON, and this endpoint returns CSV -- so call through
  // directly and stream the body back.
  const response = await fetch(`${getApiBaseUrl()}/api/v1/admin/leads.csv${query ? `?${query}` : ''}`, {
    headers: { Authorization: `Bearer ${locals.token}` }
  });

  if (!response.ok) {
    return new Response('Export failed.', { status: response.status });
  }

  return new Response(response.body, {
    headers: {
      'content-type': 'text/csv',
      'content-disposition': 'attachment; filename="leads.csv"'
    }
  });
};
