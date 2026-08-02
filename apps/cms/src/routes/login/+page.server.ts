import { fail, redirect } from '@sveltejs/kit';

import type { LoginResponse } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';
import { sessionCookieName, sessionCookieOptions } from '$lib/server/session';

import type { Actions } from './$types';

export const actions: Actions = {
  default: async ({ cookies, request, url }) => {
    const formData = await request.formData();
    const email = String(formData.get('email') ?? '').trim().toLowerCase();
    const password = String(formData.get('password') ?? '');

    if (!email || !password) {
      return fail(400, {
        email,
        message: 'Email and password are required.'
      });
    }

    try {
      const session = await apiFetch<LoginResponse>('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: {
          'Content-Type': 'application/json'
        }
      });

      cookies.set(sessionCookieName, session.access_token, {
        ...sessionCookieOptions,
        maxAge: session.expires_in
      });
    } catch (error) {
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        email,
        message:
          error instanceof ApiRequestError
            ? error.message
            : 'Unable to reach the login API. Check the API server and try again.'
      });
    }

    const redirectTo = url.searchParams.get('redirectTo');
    if (redirectTo?.startsWith('/') && !redirectTo.startsWith('//')) {
      throw redirect(303, redirectTo);
    }

    throw redirect(303, '/');
  }
};
