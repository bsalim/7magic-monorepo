import type { Handle } from '@sveltejs/kit';

import { dev } from '$app/environment';
import {
  PREF_LOCALE_COOKIE,
  PREF_LOCALE_MAX_AGE,
  resolveCountry,
  shouldRedirectToEnglish
} from '$lib/geo-redirect';
import { paraglideMiddleware } from '$lib/paraglide/server';

export const handle: Handle = ({ event, resolve }) =>
  paraglideMiddleware(event.request, ({ request, locale }) => {
    event.request = request;

    // A visitor outside Indonesia landing on the bare homepage for the first
    // time is sent to /en. Scoped to '/' only -- see geo-redirect.ts and
    // docs/superpowers/specs/2026-09-12-geo-ip-locale-redirect-design.md for
    // why every other route is left alone.
    const wantsEnglish = shouldRedirectToEnglish({
      method: event.request.method,
      pathname: event.url.pathname,
      hasLocalePreference: event.cookies.get(PREF_LOCALE_COOKIE) !== undefined,
      userAgent: event.request.headers.get('user-agent'),
      country: resolveCountry(event.request, dev)
    });

    if (wantsEnglish) {
      const headers = new Headers({ Location: '/en', 'Cache-Control': 'private, no-store' });
      headers.append(
        'Set-Cookie',
        `${PREF_LOCALE_COOKIE}=en; Path=/; Max-Age=${PREF_LOCALE_MAX_AGE}; SameSite=Lax; HttpOnly${
          dev ? '' : '; Secure'
        }`
      );
      return new Response(null, { status: 302, headers });
    }

    // Refreshed on every response, every path -- this is what makes a manual
    // language switch win permanently: it overwrites whatever the geo-redirect
    // set, and once present it short-circuits the check above.
    event.cookies.set(PREF_LOCALE_COOKIE, locale, {
      path: '/',
      maxAge: PREF_LOCALE_MAX_AGE,
      httpOnly: true,
      sameSite: 'lax'
    });

    return resolve(event, {
      transformPageChunk: ({ html }) => html.replace('%paraglide.lang%', locale)
    });
  });
