/**
 * The article route is the only one whose path segment is localized, so it is
 * the only one where the paraglide URL patterns can silently regress: an order
 * mistake in `urlPatterns` does not throw, it just routes `/en/articles/...` to
 * a SvelteKit route that does not exist and 404s in production.
 */

import { describe, expect, it } from 'vitest';
import { deLocalizeUrl, localizeHref } from '$lib/paraglide/runtime';

const origin = 'https://7magicwedding.com';

describe('article URL localization', () => {
  it('serves the Indonesian list at the root and the English one under /en', () => {
    expect(localizeHref('/artikel', { locale: 'id' })).toBe('/artikel');
    expect(localizeHref('/artikel', { locale: 'en' })).toBe('/en/articles');
  });

  it('localizes the detail path, keeping the segments it was given', () => {
    expect(localizeHref('/artikel/wedding-venue/harga-catering', { locale: 'en' })).toBe(
      '/en/articles/wedding-venue/harga-catering'
    );
  });

  it('de-localizes English article URLs onto the /artikel route', () => {
    expect(deLocalizeUrl(`${origin}/en/articles`).pathname).toBe('/artikel');
    expect(deLocalizeUrl(`${origin}/en/articles/wedding-venues/a-guide`).pathname).toBe(
      '/artikel/wedding-venues/a-guide'
    );
  });

  it('leaves every other route structurally alone', () => {
    expect(deLocalizeUrl(`${origin}/en/wedding-venue/jakarta`).pathname).toBe(
      '/wedding-venue/jakarta'
    );
    expect(localizeHref('/about', { locale: 'en' })).toBe('/en/about');
  });
});
