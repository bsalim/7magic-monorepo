import { describe, expect, it } from 'vitest';
import { formatAud, formatAudRange, formatDateRange, monthLabel } from './bali-format';

describe('bali-format', () => {
  it('writes Australian dollars without cents', () => {
    expect(formatAud(29_240)).toBe('A$29,240');
  });

  it('writes a range with an en dash', () => {
    expect(formatAudRange({ low: 29_240, high: 42_320 })).toBe('A$29,240 – A$42,320');
    expect(formatAudRange({ low: 40, high: 40 })).toBe('A$40');
  });

  it('names a month the Australian way', () => {
    expect(monthLabel(2027, 7)).toBe('July 2027');
  });

  it('shortens a date range inside one month', () => {
    expect(formatDateRange('2027-03-08', '2027-03-08')).toBe('Mon 8 Mar 2027');
    expect(formatDateRange('2027-03-09', '2027-03-15')).toBe('9–15 Mar 2027');
    expect(formatDateRange('2027-09-27', '2027-10-08')).toBe('27 Sep – 8 Oct 2027');
    expect(formatDateRange('2027-12-21', '2028-01-28')).toBe('21 Dec 2027 – 28 Jan 2028');
  });
});
