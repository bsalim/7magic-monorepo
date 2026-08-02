import { redirect } from '@sveltejs/kit';

import { apiFetch } from '$lib/server/api';
import { sessionCookieName, sessionCookieOptions } from '$lib/server/session';

import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies, locals }) => {
  if (locals.token) {
    try {
      await apiFetch('/api/v1/auth/logout', { method: 'POST', token: locals.token });
    } catch {
      // Clear the browser session even if the upstream logout endpoint is unavailable.
    }
  }

  cookies.delete(sessionCookieName, { path: sessionCookieOptions.path });
  throw redirect(303, '/login');
};
