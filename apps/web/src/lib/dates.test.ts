import { describe, expect, it } from 'vitest';
import { formatLongDate } from '$lib/dates';

describe('formatLongDate', () => {
  it('spells the month in Indonesian for the id locale', () => {
    expect(formatLongDate('2026-06-01T09:30:00+07:00', 'id')).toBe('1 Juni 2026');
  });

  it('spells the month in English for the en locale', () => {
    expect(formatLongDate('2026-06-01T09:30:00+07:00', 'en')).toBe('1 June 2026');
  });

  it('keeps the Jakarta calendar day for a timestamp that is still the previous day in UTC', () => {
    expect(formatLongDate('2026-05-31T20:00:00Z', 'id')).toBe('1 Juni 2026');
  });

  it('renders nothing for missing or unparseable input', () => {
    expect(formatLongDate(null, 'id')).toBe('');
    expect(formatLongDate(undefined, 'id')).toBe('');
    expect(formatLongDate('not a date', 'id')).toBe('');
  });
});
