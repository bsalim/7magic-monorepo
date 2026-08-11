import { describe, expect, it } from 'vitest';

import { isDateBookable, slotsForDate } from './tour-availability';

const HOURS = [
  { dayOfWeek: 1, opensAtLocal: '10:00:00', closesAtLocal: '13:00:00' },
  { dayOfWeek: 6, opensAtLocal: '09:00:00', closesAtLocal: '10:30:00' }
];

describe('isDateBookable', () => {
  it('accepts a day the branch has hours for', () => {
    // 2026-09-07 is a Monday.
    expect(isDateBookable('2026-09-07', HOURS, [])).toBe(true);
  });

  it('rejects a day with no hours', () => {
    // 2026-09-08 is a Tuesday, which is not in HOURS.
    expect(isDateBookable('2026-09-08', HOURS, [])).toBe(false);
  });

  it('rejects a closed date even when the weekday is open', () => {
    expect(isDateBookable('2026-09-07', HOURS, ['2026-09-07'])).toBe(false);
  });
});

describe('slotsForDate', () => {
  it('lists hourly slots from opening to closing, excluding the closing hour', () => {
    expect(slotsForDate('2026-09-07', HOURS)).toEqual(['10:00', '11:00', '12:00']);
  });

  it('rounds a part-hour window down so no slot runs past closing', () => {
    // Saturday closes at 10:30, so 10:00 is the last slot that fits.
    expect(slotsForDate('2026-09-12', HOURS)).toEqual(['09:00', '10:00']);
  });

  it('returns nothing for a day the branch is shut', () => {
    expect(slotsForDate('2026-09-08', HOURS)).toEqual([]);
  });
});
