import { describe, expect, it } from 'vitest';
import { m } from '$lib/paraglide/messages.js';

// A city with a single venue (Bekasi, today) printed "1 Venues" in the English
// title Google shows. English counts need a singular; Indonesian has none.
describe('city hub counts in English', () => {
  const en = { locale: 'en' } as const;

  it('uses the singular for one venue', () => {
    expect(m.city_hub_meta_title({ city: 'Bekasi', count: 1 }, en)).toBe(
      'Wedding Packages in Bekasi: 1 Venue & Price | 7Magic Wedding'
    );
    expect(m.city_hub_meta_description({ city: 'Bekasi', count: 1 }, en)).toMatch(/^1 wedding venue in Bekasi/);
    expect(m.city_hub_intro_no_price({ city: 'Bekasi', count: 1 }, en)).toMatch(/^1 wedding venue in Bekasi/);
    expect(m.city_hub_intro({ city: 'Bekasi', count: 1, price: 'Rp 1' }, en)).toMatch(/^1 wedding venue in Bekasi/);
    expect(m.city_hub_group_count({ count: 1 }, en)).toBe('1 venue');
  });

  it('keeps the plural for several', () => {
    expect(m.city_hub_meta_title({ city: 'Jakarta', count: 60 }, en)).toBe(
      'Wedding Packages in Jakarta: 60 Venues & Prices | 7Magic Wedding'
    );
    expect(m.city_hub_group_count({ count: 3 }, en)).toBe('3 venues');
  });

  it('leaves Indonesian alone', () => {
    expect(m.city_hub_group_count({ count: 1 }, { locale: 'id' })).toBe(
      m.city_hub_group_count({ count: 2 }, { locale: 'id' }).replace('2', '1')
    );
  });
});
