import { describe, expect, it } from 'vitest';
import {
  AlmanacUnavailableError,
  almanacLeadInputs,
  fetchAlmanac,
  monthWeeks,
  shiftMonth,
  shioYears,
  type AlmanacResponse
} from './almanac';

const days = (year: number, month: number, count: number) =>
  Array.from({ length: count }, (_, index) => ({
    date: `${year}-${String(month).padStart(2, '0')}-${String(index + 1).padStart(2, '0')}`
  }));

describe('monthWeeks', () => {
  it('starts each week on Monday and pads the ends', () => {
    // 1 June 2025 was a Sunday: it sits alone at the end of the first row.
    const weeks = monthWeeks(days(2025, 6, 30));
    expect(weeks).toHaveLength(6);
    expect(weeks[0].map((cell) => cell?.date ?? null)).toEqual([null, null, null, null, null, null, '2025-06-01']);
    expect(weeks[1][0]?.date).toBe('2025-06-02');
    expect(weeks[5].map((cell) => cell?.date ?? null)).toEqual(['2025-06-30', null, null, null, null, null, null]);
  });

  it('needs no padding for a month that fills its rows', () => {
    // February 2027 starts on a Monday and has 28 days.
    const weeks = monthWeeks(days(2027, 2, 28));
    expect(weeks).toHaveLength(4);
    expect(weeks.flat().every(Boolean)).toBe(true);
  });
});

describe('shiftMonth', () => {
  it('wraps the year in both directions', () => {
    expect(shiftMonth(2027, 12, 1)).toEqual({ year: 2028, month: 1 });
    expect(shiftMonth(2027, 1, -1)).toEqual({ year: 2026, month: 12 });
    expect(shiftMonth(2027, 6, 1)).toEqual({ year: 2027, month: 7 });
  });
});

describe('shioYears', () => {
  it('names two recent years of each animal', () => {
    expect(shioYears('rat')).toEqual([1984, 1996]);
    expect(shioYears('pig')).toEqual([1995, 2007]);
  });
});

describe('fetchAlmanac', () => {
  it('turns any failure into one retryable error', async () => {
    const down = (async () => {
      throw new TypeError('offline');
    }) as unknown as typeof fetch;
    const refused = (async () => new Response('{}', { status: 502 })) as unknown as typeof fetch;
    const body = { year: 2027, month: 3, shio: [], locale: 'id' as const };
    await expect(fetchAlmanac(body, down)).rejects.toBeInstanceOf(AlmanacUnavailableError);
    await expect(fetchAlmanac(body, refused)).rejects.toBeInstanceOf(AlmanacUnavailableError);
  });
});

describe('almanacLeadInputs', () => {
  it('tells the team the month, the shio and the good days, in Indonesian', () => {
    const result = {
      year: 2027,
      month: 3,
      shio: [{ animal_label: 'Babi' }, { animal_label: 'Tikus' }],
      days: [
        { date: '2027-03-06', rating: 'good' },
        { date: '2027-03-07', rating: 'avoid' },
        { date: '2027-03-14', rating: 'good' }
      ]
    } as unknown as AlmanacResponse;
    expect(almanacLeadInputs(result)).toEqual({ month: 'Maret 2027', shio: 'Babi & Tikus', good_days: '6, 14' });
  });
});
