import { describe, expect, it } from 'vitest';

import { resolveCountry, shouldRedirectToEnglish } from './geo-redirect';

const GOOGLEBOT_UA =
  'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)';
const CHROME_UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36';

function base(overrides: Partial<Parameters<typeof shouldRedirectToEnglish>[0]> = {}) {
  return {
    method: 'GET',
    pathname: '/',
    hasLocalePreference: false,
    userAgent: CHROME_UA,
    country: 'US',
    ...overrides
  };
}

describe('shouldRedirectToEnglish', () => {
  it('redirects a first-time non-Indonesian visitor hitting the bare homepage', () => {
    expect(shouldRedirectToEnglish(base())).toBe(true);
  });

  it('does not redirect an Indonesian visitor', () => {
    expect(shouldRedirectToEnglish(base({ country: 'ID' }))).toBe(false);
  });

  it('does not redirect a bot regardless of country', () => {
    expect(shouldRedirectToEnglish(base({ userAgent: GOOGLEBOT_UA }))).toBe(false);
  });

  it('does not redirect once a locale preference cookie exists', () => {
    expect(shouldRedirectToEnglish(base({ hasLocalePreference: true }))).toBe(false);
  });

  it('fails open when the country is missing', () => {
    expect(shouldRedirectToEnglish(base({ country: null }))).toBe(false);
  });

  it.each(['XX', 'T1', '', '123', 'USA'])('fails open on malformed country code %s', (country) => {
    expect(shouldRedirectToEnglish(base({ country }))).toBe(false);
  });

  it('does not redirect a non-GET request', () => {
    expect(shouldRedirectToEnglish(base({ method: 'POST' }))).toBe(false);
  });

  it('does not redirect any path other than the bare homepage', () => {
    expect(shouldRedirectToEnglish(base({ pathname: '/wedding-venue/jakarta' }))).toBe(false);
    expect(shouldRedirectToEnglish(base({ pathname: '/en' }))).toBe(false);
  });

  it('normalizes a lowercase country code', () => {
    expect(shouldRedirectToEnglish(base({ country: 'us' }))).toBe(true);
  });
});

describe('resolveCountry', () => {
  it('reads CF-IPCountry in production', () => {
    const request = new Request('https://7magicwedding.com/?debug_country=US', {
      headers: { 'cf-ipcountry': 'ID' }
    });

    expect(resolveCountry(request, false)).toBe('ID');
  });

  it('honors the debug override in dev', () => {
    const request = new Request('http://localhost:5182/?debug_country=us', {
      headers: { 'cf-ipcountry': 'ID' }
    });

    expect(resolveCountry(request, true)).toBe('US');
  });

  it('falls back to the header in dev when no override is given', () => {
    const request = new Request('http://localhost:5182/', {
      headers: { 'cf-ipcountry': 'ID' }
    });

    expect(resolveCountry(request, true)).toBe('ID');
  });

  it('returns null when nothing is available', () => {
    const request = new Request('http://localhost:5182/');

    expect(resolveCountry(request, true)).toBeNull();
  });
});
