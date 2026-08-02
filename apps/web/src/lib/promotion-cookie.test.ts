import { describe, expect, it } from 'vitest';
import { PROMOTION_COOKIE, dismissalCookie, readCookie, shouldShow } from './promotion-cookie';

describe('readCookie', () => {
  it('finds a value among several cookies', () => {
    expect(readCookie('b', 'a=1; b=2; c=3')).toBe('2');
  });

  it('returns null when absent', () => {
    expect(readCookie('missing', 'a=1')).toBeNull();
  });

  it('does not match a cookie whose name merely ends with the key', () => {
    expect(readCookie('promo', 'other_promo=1')).toBeNull();
  });

  it('decodes encoded values', () => {
    expect(readCookie('v', 'v=a%20b')).toBe('a b');
  });
});

describe('shouldShow', () => {
  it('shows when no cookie is set', () => {
    expect(shouldShow('123', '')).toBe(true);
  });

  it('hides once dismissed at that version', () => {
    expect(shouldShow('123', `${PROMOTION_COOKIE}=123`)).toBe(false);
  });

  // The whole point of storing a version rather than a flag: a new campaign
  // must reappear for people who dismissed the previous one.
  it('shows again when the promo has been edited since dismissal', () => {
    expect(shouldShow('456', `${PROMOTION_COOKIE}=123`)).toBe(true);
  });
});

describe('dismissalCookie', () => {
  it('expires after a day for daily', () => {
    expect(dismissalCookie('1', 'daily')).toContain('max-age=86400');
  });

  it('expires after a week for weekly', () => {
    expect(dismissalCookie('1', 'weekly')).toContain('max-age=604800');
  });

  it('effectively never expires for once', () => {
    const maxAge = Number(dismissalCookie('1', 'once').match(/max-age=(\d+)/)?.[1]);
    expect(maxAge).toBeGreaterThan(60 * 60 * 24 * 365);
  });

  it('scopes the cookie to the whole site', () => {
    expect(dismissalCookie('1', 'daily')).toContain('path=/');
  });

  it('stores the version so a later edit can re-show the popup', () => {
    expect(dismissalCookie('789', 'daily')).toContain(`${PROMOTION_COOKIE}=789`);
  });
});
