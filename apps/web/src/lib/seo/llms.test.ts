import { describe, expect, it } from 'vitest';
import { buildLlmsTxt } from '$lib/seo/llms';
import { SITE_URL } from '$lib/seo/schema';

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

    expect(text).toContain('1 wedding venue with');
  });

  it('still points at the venue search when the catalogue is unavailable', () => {
    const text = buildLlmsTxt([]);

    expect(text).toContain(`${SITE_URL}/wedding-venue/search`);
    expect(text).not.toContain('/wedding-venue/jakarta');
  });

  it('uses the translated English slug where the route has one', () => {
    expect(buildLlmsTxt([])).toContain(`${SITE_URL}/en/prenuptial-agreement`);
  });

  it('emits only absolute URLs', () => {
    expect(buildLlmsTxt(cities)).not.toMatch(/\]\(\//);
  });
});
