export type PromotionFrequency = 'daily' | 'weekly' | 'once';

export const PROMOTION_COOKIE = '7magic_promo';

// How long a dismissal lasts. "once" is effectively forever; ten years is the
// longest a browser will reliably honour.
const MAX_AGE_SECONDS: Record<PromotionFrequency, number> = {
  daily: 60 * 60 * 24,
  weekly: 60 * 60 * 24 * 7,
  once: 60 * 60 * 24 * 365 * 10
};

export function readCookie(name: string, jar: string): string | null {
  for (const part of jar.split(';')) {
    const [key, ...rest] = part.trim().split('=');
    if (key === name) return decodeURIComponent(rest.join('='));
  }
  return null;
}

/**
 * Whether the popup should be shown for this version.
 *
 * The stored value is the promo's version, not a boolean, so editing the promo
 * in the CMS shows it again to people who already dismissed the old one —
 * otherwise a new campaign would stay invisible behind a stale cookie.
 */
export function shouldShow(version: string, jar: string): boolean {
  return readCookie(PROMOTION_COOKIE, jar) !== version;
}

export function dismissalCookie(version: string, frequency: PromotionFrequency): string {
  const maxAge = MAX_AGE_SECONDS[frequency] ?? MAX_AGE_SECONDS.daily;
  return `${PROMOTION_COOKIE}=${encodeURIComponent(version)}; path=/; max-age=${maxAge}; SameSite=Lax`;
}
