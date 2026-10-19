import { describe, expect, it } from 'vitest';
import { jabodetabekCopy } from './content';

describe('Jabodetabek copy', () => {
  // /en/jabodetabek-wedding served the Indonesian title and body until it had
  // an English edition.
  it('has an English edition', () => {
    const en = jabodetabekCopy('en');
    expect(en.meta.title).toBe('Weddings in Jabodetabek: Venues in Jakarta, Tangerang, Bogor & Bekasi | 7Magic');
    expect(en.hero.title).not.toBe(jabodetabekCopy('id').hero.title);
  });

  // An article's slug is translated content, not routing, so the English links
  // are written out rather than produced by localizeHref (which would 301).
  it('links each article at its own URL in each language', () => {
    expect(jabodetabekCopy('id').reading.map((a) => a.href)).toEqual([
      '/artikel/wedding-venue/masjid-gedung-favorit-jabodetabek-akad-nikah',
      '/artikel/wedding-venue/intimate-wedding-100-tamu-jakarta-rincian-biaya',
      '/artikel/wedding-preparation/syarat-dokumen-nikah-2026-kua-catatan-sipil'
    ]);
    expect(jabodetabekCopy('en').reading.map((a) => a.href)).toEqual([
      '/en/articles/wedding-venue/favorite-akad-venues-in-jabodetabek',
      '/en/articles/wedding-venue/100-guest-intimate-wedding-in-jakarta',
      '/en/articles/wedding-preparation/marriage-documents-2026'
    ]);
  });
});
