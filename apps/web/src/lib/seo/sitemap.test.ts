import { describe, expect, it } from 'vitest';
import { buildSitemap, lastmodDate } from '$lib/seo/sitemap';
import { SITE_URL } from '$lib/seo/schema';

const entry = {
  alternates: {
    id: '/artikel/dekorasi/harga-dekorasi',
    en: '/en/articles/decoration/decoration-prices'
  },
  lastmod: '2026-06-01T09:30:00+07:00'
};

describe('buildSitemap', () => {
  it('emits one <url> per language, not one per page', () => {
    const xml = buildSitemap([entry]);

    expect(xml).toContain(`<loc>${SITE_URL}/artikel/dekorasi/harga-dekorasi</loc>`);
    expect(xml).toContain(`<loc>${SITE_URL}/en/articles/decoration/decoration-prices</loc>`);
    expect(xml.match(/<url>/g)).toHaveLength(2);
  });

  it('gives every entry a self-referencing alternate', () => {
    const xml = buildSitemap([entry]);
    const blocks = xml.split('<url>').slice(1);

    for (const block of blocks) {
      expect(block).toContain(`hreflang="id" href="${SITE_URL}/artikel/dekorasi/harga-dekorasi"`);
      expect(block).toContain(
        `hreflang="en" href="${SITE_URL}/en/articles/decoration/decoration-prices"`
      );
    }
  });

  it('points x-default at the Indonesian URL', () => {
    const xml = buildSitemap([entry]);

    expect(xml).toContain(
      `hreflang="x-default" href="${SITE_URL}/artikel/dekorasi/harga-dekorasi"`
    );
  });

  it('makes every URL absolute', () => {
    const xml = buildSitemap([entry]);
    const locs = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]);

    expect(locs.length).toBeGreaterThan(0);
    expect(locs.every((loc) => loc.startsWith('https://'))).toBe(true);
  });

  it('escapes XML metacharacters in URLs', () => {
    const xml = buildSitemap([{ alternates: { id: '/cari?q=a&b=c' } }]);

    expect(xml).toContain('q=a&amp;b=c');
    expect(xml).not.toMatch(/q=a&b=c/);
  });

  it('lists only the locales an entry actually has', () => {
    const xml = buildSitemap([{ alternates: { id: '/artikel/dekorasi/belum-diterjemahkan' } }]);

    expect(xml.match(/<url>/g)).toHaveLength(1);
    expect(xml).not.toContain('hreflang="en"');
    expect(xml).toContain('hreflang="x-default"');
  });

  it('names the URL that is served, not one that redirects to it', () => {
    const xml = buildSitemap([{ alternates: { id: '/', en: '/en/' } }]);

    expect(xml).toContain(`<loc>${SITE_URL}/en</loc>`);
    expect(xml).not.toContain(`<loc>${SITE_URL}/en/</loc>`);
    // The root itself keeps its slash -- a bare origin is not a valid <loc>.
    expect(xml).toContain(`<loc>${SITE_URL}/</loc>`);
  });

  it('omits lastmod rather than inventing one', () => {
    const xml = buildSitemap([{ alternates: { id: '/about' }, lastmod: '' }]);

    expect(xml).not.toContain('<lastmod>');
  });

  it('is well-formed XML', () => {
    const xml = buildSitemap([entry, { alternates: { id: '/about', en: '/en/about' } }]);
    const parsed = new DOMParser().parseFromString(xml, 'application/xml');

    expect(parsed.querySelector('parsererror')).toBeNull();
    expect(parsed.documentElement.tagName).toBe('urlset');
    expect(parsed.querySelectorAll('url')).toHaveLength(4);
  });
});

describe('lastmodDate', () => {
  it('reduces a timestamp to a date', () => {
    expect(lastmodDate('2026-06-01T09:30:00Z')).toBe('2026-06-01');
  });

  it('returns null for missing or unparseable input', () => {
    expect(lastmodDate('')).toBeNull();
    expect(lastmodDate(null)).toBeNull();
    expect(lastmodDate('not a date')).toBeNull();
  });
});
