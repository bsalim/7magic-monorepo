import { env } from '$env/dynamic/private';

const SITEVERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify';

/** The field name the Turnstile widget writes its token into. */
export const TURNSTILE_FIELD = 'cf-turnstile-response';

/**
 * Checks a Cloudflare Turnstile token with Cloudflare.
 *
 * The secret is the on/off switch, like PUBLIC_GA_MEASUREMENT_ID is for
 * analytics: with TURNSTILE_SECRET_KEY unset every token passes, so local dev
 * and tests need no Cloudflare account. Production must set it, or the form is
 * unprotected.
 *
 * A Cloudflare outage fails closed. The guest sees "try again", which is better
 * than letting the form open to bots for as long as the outage lasts.
 */
export async function verifyTurnstile(
  token: FormDataEntryValue | null,
  remoteIp: string | null,
  fetcher: typeof fetch = fetch
): Promise<boolean> {
  const secret = env.TURNSTILE_SECRET_KEY;
  if (!secret) return true;
  if (typeof token !== 'string' || !token) return false;

  const body = new URLSearchParams({ secret, response: token });
  if (remoteIp) body.set('remoteip', remoteIp);

  try {
    const response = await fetcher(SITEVERIFY_URL, { method: 'POST', body });
    const result: { success?: boolean; 'error-codes'?: string[] } = await response.json();
    if (!result.success) {
      console.warn(`[turnstile] rejected: ${(result['error-codes'] ?? []).join(',')}`);
    }
    return result.success === true;
  } catch (err) {
    console.error('[turnstile] siteverify unreachable', err);
    return false;
  }
}

/** The client address, or null where adapter-node cannot tell (dev, tests). */
export function clientIp(getClientAddress: () => string): string | null {
  try {
    return getClientAddress();
  } catch {
    return null;
  }
}
