import { env } from '$env/dynamic/public';

/**
 * The header a browser-side form sends its Turnstile token in. A header rather
 * than a body field: the /api proxies pass the body to the API untouched, and
 * the API's schemas have no field for it.
 */
export const TURNSTILE_HEADER = 'x-turnstile-token';

/**
 * True while the form should hold its submit button: the widget is configured
 * but has not produced a token yet. Always false without a site key, so forms
 * work unchanged where Turnstile is not set up.
 */
export function captchaPending(token: string): boolean {
  return Boolean(env.PUBLIC_TURNSTILE_SITE_KEY) && !token;
}
