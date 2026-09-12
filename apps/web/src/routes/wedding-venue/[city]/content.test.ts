import { describe, expect, it } from 'vitest';
import { BUDGET_BANDS, type CityStats } from '$lib/venue-groups';
import { hubCopy } from './content';

const jakarta: CityStats = {
  count: 61,
  floor: 45_000_000,
  ceiling: 950_000_000,
  guestsMin: 200,
  guestsMax: 1000,
  districts: 5,
  bands: [
    { band: BUDGET_BANDS[0], count: 3 },
    { band: BUDGET_BANDS[1], count: 20 },
    { band: BUDGET_BANDS[3], count: 8 }
  ]
};

const onRequest: CityStats = {
  count: 2,
  floor: null,
  ceiling: null,
  guestsMin: null,
  guestsMax: null,
  districts: 1,
  bands: []
};

describe('hubCopy', () => {
  it('quotes the live figures in Indonesian, formatted the Indonesian way', () => {
    const copy = hubCopy('id', 'Jakarta', jakarta);

    expect(copy.prose[1]).toBe(
      'Di halaman ini ada 61 venue di Jakarta, tersebar di 5 wilayah. Harga awal berkisar Rp 45 juta sampai Rp 950 juta: 3 venue di bawah Rp 50 juta, 20 di kisaran Rp 50–100 juta dan 8 dari Rp 200 juta ke atas.'
    );
    expect(copy.faq.items[2].a).toContain('dihitung untuk 200–1.000 tamu');
    expect(copy.table.guestsFor(1000)).toBe('1.000 tamu');
  });

  it('translates the same figures into English', () => {
    const copy = hubCopy('en', 'Jakarta', jakarta);

    expect(copy.prose[1]).toBe(
      'This page lists 61 venues in Jakarta, across 5 districts. Starting prices run from Rp 45 million to Rp 950 million: 3 venues under Rp 50 million, 20 between Rp 50 and 100 million and 8 at Rp 200 million and above.'
    );
    expect(copy.table.guestsFor(1000)).toBe('1,000 guests');
  });

  it('never quotes a price for a city priced entirely on request', () => {
    for (const locale of ['id', 'en'] as const) {
      const copy = hubCopy(locale, 'Bogor', onRequest);
      const text = [...copy.prose, ...copy.faq.items.map((faq) => faq.a)].join(' ');

      expect(text).not.toContain('Rp ');
      expect(text).not.toContain('null');
    }
  });

  it('gives every FAQ a question and an answer', () => {
    const copy = hubCopy('id', 'Jakarta', jakarta);

    expect(copy.faq.items).toHaveLength(6);
    for (const faq of copy.faq.items) {
      expect(faq.q.length).toBeGreaterThan(10);
      expect(faq.a.length).toBeGreaterThan(40);
    }
  });
});
