/**
 * Routes whose path segments differ per locale, rather than merely gaining an
 * /en prefix.
 *
 * These are the only URLs the paraglide `urlPatterns` can silently break: an
 * ordering mistake does not throw, it routes a real URL to a SvelteKit route
 * that does not exist and 404s in production. Articles have their own file
 * (`article-urls.test.ts`); this one covers the landing pages.
 */

import { describe, expect, it } from 'vitest';
import { deLocalizeUrl, localizeHref } from '$lib/paraglide/runtime';

const origin = 'https://7magicwedding.com';

describe('prenuptial agreement URLs', () => {
  it('serves an English slug under /en, not the Indonesian route name', () => {
    expect(localizeHref('/perjanjian-pranikah', { locale: 'id' })).toBe('/perjanjian-pranikah');
    expect(localizeHref('/perjanjian-pranikah', { locale: 'en' })).toBe(
      '/en/prenuptial-agreement'
    );
    // The point of the pattern: without it the catch-all produces this instead.
    expect(localizeHref('/perjanjian-pranikah', { locale: 'en' })).not.toBe(
      '/en/perjanjian-pranikah'
    );
  });

  it('de-localizes the English slug onto the Indonesian route', () => {
    // This is what `reroute` does on every request, and it is what decides
    // whether /en/prenuptial-agreement finds a route at all.
    expect(deLocalizeUrl(`${origin}/en/prenuptial-agreement`).pathname).toBe(
      '/perjanjian-pranikah'
    );
  });

  it('round-trips in both directions', () => {
    for (const locale of ['id', 'en'] as const) {
      const localized = localizeHref('/perjanjian-pranikah', { locale });
      expect(deLocalizeUrl(`${origin}${localized}`).pathname).toBe('/perjanjian-pranikah');
    }
  });

  it('does not disturb the article patterns listed after it', () => {
    expect(localizeHref('/artikel', { locale: 'en' })).toBe('/en/articles');
    expect(localizeHref('/artikel/wedding-venue/harga-catering', { locale: 'en' })).toBe(
      '/en/articles/wedding-venue/harga-catering'
    );
  });

  it('leaves a path with no pattern of its own on the catch-all', () => {
    // /paket-sangjit is Indonesian-only by choice, so it keeps its route name.
    expect(localizeHref('/paket-sangjit', { locale: 'en' })).toBe('/en/paket-sangjit');
  });
});
