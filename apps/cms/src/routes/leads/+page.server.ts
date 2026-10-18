import { redirect } from '@sveltejs/kit';

import type { AdminLeadList } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';
import { leadFilterQuery, readLeadFilters } from '$lib/server/leadFilters';

import type { PageServerLoad } from './$types';

const emptyList: AdminLeadList = {
  items: [],
  pagination: { page: 1, page_size: 50, total: 0, total_pages: 0 }
};

export const load: PageServerLoad = async ({ locals, url }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  const filters = readLeadFilters(url);
  const page = Math.max(1, Number(url.searchParams.get('page')) || 1);
  const query = leadFilterQuery(filters, page).toString();

  try {
    const leads = await apiFetch<AdminLeadList>(`/api/v1/admin/leads${query ? `?${query}` : ''}`, {
      token: locals.token
    });
    return { error: '', leads, filters };
  } catch (error) {
    return {
      // Leads need an org-wide grant, so a branch user lands here on purpose.
      error:
        error instanceof ApiRequestError && error.status === 403
          ? 'Your account cannot view leads. Leads need an organisation-wide role.'
          : error instanceof ApiRequestError
            ? error.message
            : 'Unable to load leads. Check the API server and try again.',
      leads: emptyList,
      filters
    };
  }
};
