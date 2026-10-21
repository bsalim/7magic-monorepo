import { describe, expect, it } from 'vitest';
import { buildLlmsTxt } from '$lib/seo/llms';
import { SITE_URL } from '$lib/seo/schema';
import { siteHref } from '$lib/seo/english-only';
import { STATIC_PATHS } from '$lib/seo/static-paths';

const cities = [
  { slug: 'jakarta', name: 'Jakarta', count: 61 },
  { slug: 'tangerang', name: 'Tangerang', count: 9 }
];

describe('buildLlmsTxt', () => {
  it('opens with the title and a blockquote summary', () => {
    expect(buildLlmsTxt(cities).startsWith('# 7Magic Wedding\n\n> ')).toBe(true);
  });

  it('lists every city hub with its venue count and both language URLs', () => {
    const text = buildLlmsTxt(cities);

    expect(text).toContain(`[Jakarta](${SITE_URL}/wedding-venue/jakarta): 61 wedding venues`);
    expect(text).toContain(`[English](${SITE_URL}/en/wedding-venue/jakarta)`);
    expect(text).toContain(`[Tangerang](${SITE_URL}/wedding-venue/tangerang): 9 wedding venues`);
  });

  it('does not pluralise a single venue', () => {
    const text = buildLlmsTxt([{ slug: 'bekasi', name: 'Bekasi', count: 1 }]);

    expect(text).toContain('1 wedding venue,');
  });

  it('still points at the venue search when the catalogue is unavailable', () => {
    const text = buildLlmsTxt([]);

    expect(text).toContain(`${SITE_URL}/wedding-venue/search`);
    expect(text).not.toContain('/wedding-venue/jakarta');
  });

  it('uses the translated English slug where the route has one', () => {
    expect(buildLlmsTxt([])).toContain(`${SITE_URL}/en/prenuptial-agreement`);
  });

  // An English-only page has no Indonesian URL to cite, and the root form is a
  // redirect a model would otherwise quote.
  it('lists an English-only page at its /en URL alone', () => {
    const text = buildLlmsTxt([]);
    expect(text).toContain(`](${SITE_URL}/en/bali-wedding-planning): `);
    expect(text).not.toContain(`](${SITE_URL}/bali-wedding-planning)`);
  });

  it('emits only absolute URLs', () => {
    expect(buildLlmsTxt(cities)).not.toMatch(/\]\(\//);
  });

  // It fell behind once already -- three landing pages, showcases and the
  // legal pages were missing -- so it is held to the sitemap the way the footer
  // is. The home page is the one exception: this file is its own summary.
  it('links every static page in the sitemap', () => {
    const text = buildLlmsTxt([]);
    const missing = STATIC_PATHS.filter((path) => path !== '/').filter(
      (path) => !text.includes(`](${SITE_URL}${siteHref(path)})`)
    );
    expect(missing).toEqual([]);
  });

  // The city pages no longer carry a price table, and the cards ask for a
  // quote, so the file must not promise prices a model would then misquote.
  it('does not promise listed prices', () => {
    expect(buildLlmsTxt(cities)).not.toMatch(/starting package prices|same venues and prices/);
  });
});
