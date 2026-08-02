import { dev } from '$app/environment';

export const sessionCookieName = 'cms_session';

// Keep in sync with the API's SESSION_TTL_SECONDS default.
export const sessionCookieMaxAgeSeconds = 60 * 60 * 24 * 14;

export const sessionCookieOptions = {
  path: '/',
  httpOnly: true,
  sameSite: 'lax' as const,
  secure: !dev
};
