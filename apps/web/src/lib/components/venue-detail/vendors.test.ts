import { describe, expect, it } from 'vitest';
import { VENDORS, VENDOR_CATS, vendorCount } from './vendors';

describe('vendors', () => {
  it('exposes the full partner list', () => {
    expect(VENDORS.length).toBeGreaterThan(30);
  });

  it('reports a count that matches the list', () => {
    expect(vendorCount).toBe(VENDORS.length);
  });

  it('starts its category list with All', () => {
    expect(VENDOR_CATS[0]).toBe('All');
  });

  it('only uses categories declared in VENDOR_CATS', () => {
    const known = new Set<string>(VENDOR_CATS);
    for (const vendor of VENDORS) {
      expect(known.has(vendor.cat)).toBe(true);
    }
  });

  it('gives every vendor a logo path', () => {
    for (const vendor of VENDORS) {
      expect(vendor.logo).toMatch(/^\/img\//);
    }
  });
});
