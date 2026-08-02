import type { Handle } from '@sveltejs/kit';

import type { AuthUser } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';
import {
  sessionCookieMaxAgeSeconds,
  sessionCookieName,
  sessionCookieOptions
} from '$lib/server/session';

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get(sessionCookieName);

  event.locals.token = token ?? null;
  event.locals.user = null;

  if (token) {
    try {
      event.locals.user = await apiFetch<AuthUser>('/api/v1/auth/me', { token });
      event.cookies.set(sessionCookieName, token, {
        ...sessionCookieOptions,
        maxAge: sessionCookieMaxAgeSeconds
      });
    } catch (error) {
      event.locals.token = null;
      event.cookies.delete(sessionCookieName, { path: sessionCookieOptions.path });

      if (!(error instanceof ApiRequestError)) {
        throw error;
      }
    }
  }

  return resolve(event);
};
