import { redirect } from '@sveltejs/kit';

import type { AdminArticle, AdminSummary, AdminVenue } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';
import { sessionCookieName, sessionCookieOptions } from '$lib/server/session';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const [summary, venueData, articleData] = await Promise.all([
      apiFetch<AdminSummary>('/api/v1/admin/dashboard', { token: locals.token }),
      apiFetch<{ items: AdminVenue[] }>('/api/v1/admin/venues', { token: locals.token }),
      apiFetch<{ items: AdminArticle[] }>('/api/v1/admin/articles', { token: locals.token })
    ]);

    return {
      articles: articleData.items,
      error: '',
      summary,
      user: locals.user,
      venues: venueData.items
    };
  } catch (error) {
    return {
      articles: [],
      error:
        error instanceof ApiRequestError
          ? error.message
          : 'Unable to load CMS data. Check the API server and try again.',
      summary: null,
      user: locals.user,
      venues: []
    };
  }
};

export const actions: Actions = {
  logout: async ({ cookies, locals }) => {
    if (locals.token) {
      try {
        await apiFetch('/api/v1/auth/logout', { method: 'POST', token: locals.token });
      } catch {
        // A local logout should still clear the browser session if the API is unavailable.
      }
    }

    cookies.delete(sessionCookieName, { path: sessionCookieOptions.path });
    throw redirect(303, '/login');
  }
};
