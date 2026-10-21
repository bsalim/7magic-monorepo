import { describe, expect, it } from 'vitest';
import { BALI_EVENTS, galunganDates, monthFlags, seasonOf } from './bali-dates';

const DAY = 86_400_000;
const days = (from: string, to: string) => (Date.parse(to) - Date.parse(from)) / DAY;

describe('BALI_EVENTS', () => {
  // SKB 3 Menteri 2027. Several popular sites print 9 or 18 March, which would
  // send a couple's guests to a closed airport.
  it('puts Nyepi 2027 on Monday 8 March, with its source', () => {
    const nyepi = BALI_EVENTS.find(
      (event) => event.kind === 'nyepi' && event.start.startsWith('2027')
    );
    expect(nyepi?.start).toBe('2027-03-08');
    expect(nyepi?.source.url).toMatch(/^https:\/\//);
  });

  it('has Kuningan exactly ten days after each Galungan', () => {
    const galungan = BALI_EVENTS.filter((event) => event.kind === 'galungan').map((e) => e.start);
    const kuningan = BALI_EVENTS.filter((event) => event.kind === 'kuningan').map((e) => e.start);
    expect(kuningan.length).toBe(galungan.length);
    for (const date of kuningan) {
      expect(galungan.some((g) => days(g, date) === 10)).toBe(true);
    }
  });

  it('marks every 2028 Galungan and Kuningan as provisional', () => {
    const balinese2028 = BALI_EVENTS.filter(
      (event) =>
        (event.kind === 'galungan' || event.kind === 'kuningan') && event.start.startsWith('2028')
    );
    expect(balinese2028.length).toBeGreaterThan(0);
    expect(balinese2028.every((event) => event.provisional)).toBe(true);
  });

  it('gives every event an ordered range and an https source', () => {
    for (const event of BALI_EVENTS) {
      expect(event.start <= event.end, event.name).toBe(true);
      expect(event.source.url, event.name).toMatch(/^https:\/\//);
    }
  });
});

describe('galunganDates', () => {
  // The pawukon cycle is 210 days, anchored on Galungan 17 June 2026.
  it('steps the 210-day cycle', () => {
    expect(galunganDates('2026-06-17', '2028-12-31')).toEqual([
      '2026-06-17',
      '2027-01-13',
      '2027-08-11',
      '2028-03-08',
      '2028-10-04'
    ]);
  });
});

describe('monthFlags', () => {
  it('flags Nyepi and the Idul Fitri holidays in March 2027', () => {
    const flags = monthFlags(2027, 3);
    const kinds = flags.events.map((event) => event.kind);
    expect(kinds).toContain('nyepi');
    expect(kinds).toContain('id-holiday');
    expect(flags.notices).toEqual([]);
  });

  // An unpublished year must never read as a clear one.
  it('warns that 2028 holidays are not announced yet', () => {
    expect(monthFlags(2028, 6).notices.join(' ')).toMatch(/2028 holiday dates not yet announced/);
  });

  it('shows NSW school holidays in July 2027', () => {
    const states = monthFlags(2027, 7)
      .events.filter((event) => event.kind === 'au-school')
      .map((event) => event.state);
    expect(states).toContain('NSW');
  });

  it('includes an event that spans into the month', () => {
    const flags = monthFlags(2027, 10);
    expect(
      flags.events.some((event) => event.kind === 'au-school' && event.start < '2027-10-01')
    ).toBe(true);
  });
});

describe('seasonOf', () => {
  it('splits the year into wet, dry and the months between', () => {
    expect(seasonOf(1)).toBe('wet');
    expect(seasonOf(7)).toBe('dry');
    expect(seasonOf(4)).toBe('shoulder');
    expect(seasonOf(10)).toBe('shoulder');
    expect(seasonOf(12)).toBe('wet');
  });
});
