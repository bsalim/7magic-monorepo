/**
 * The Tanggal Baik Tionghoa tool's side of `POST /api/v1/public/almanac`: wire
 * types, the call through the `/api/almanac` proxy, the month grid, and what
 * the lead gate sends.
 *
 * The reading lives in the API (`app/domains/almanac`), on the same pillars and
 * solar terms as Ba Zi, so a date read here and there has the same day pillar.
 * Field names are the API's snake_case.
 */

import type { BranchOut, PillarOut, Rule } from './bazi';

export const ANIMALS = [
  'rat',
  'ox',
  'tiger',
  'rabbit',
  'dragon',
  'snake',
  'horse',
  'goat',
  'monkey',
  'rooster',
  'dog',
  'pig'
] as const;
export type Animal = (typeof ANIMALS)[number];

export type Rating = 'good' | 'ordinary' | 'avoid';
export type OfficerRating = 'favoured' | 'ordinary' | 'avoided';

export type AlmanacRequest = {
  year: number;
  /** 1-12. */
  month: number;
  shio: Animal[];
  locale: 'id' | 'en';
};

export type OfficerOut = {
  index: number;
  char: string;
  pinyin: string;
  label: string;
  rating: OfficerRating;
};

export type ShioReasonOut = {
  partner: number;
  rule: Rule;
  rule_label: string;
};

export type AlmanacDayOut = {
  /** ISO date. */
  date: string;
  pillar: PillarOut;
  officer: OfficerOut;
  /** The animal the day opposes, whoever is asking. */
  clashes: BranchOut;
  reasons: ShioReasonOut[];
  rating: Rating;
};

export type AlmanacResponse = {
  year: number;
  month: number;
  shio: BranchOut[];
  days: AlmanacDayOut[];
};

/** The API could not be reached or failed: worth a retry, the inputs are fine. */
export class AlmanacUnavailableError extends Error {}

export async function fetchAlmanac(body: AlmanacRequest, fetcher: typeof fetch = fetch): Promise<AlmanacResponse> {
  let response: Response;
  try {
    response = await fetcher('/api/almanac', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
  } catch {
    throw new AlmanacUnavailableError('network');
  }
  if (!response.ok) throw new AlmanacUnavailableError(String(response.status));
  return (await response.json()) as AlmanacResponse;
}

/** Two recent birth years per animal, to help someone find theirs in the list. */
export function shioYears(animal: Animal): [number, number] {
  // 1984 was a Rat year; the cycle is twelve long.
  const first = 1984 + ANIMALS.indexOf(animal);
  return [first, first + 12];
}

/**
 * The days laid out as calendar weeks, Monday first, padded with nulls: a
 * wedding is usually on a weekend, and Monday-first keeps Saturday and Sunday
 * side by side at the end of each row.
 */
export function monthWeeks<T extends { date: string }>(days: T[]): (T | null)[][] {
  if (!days.length) return [];
  const [year, month, day] = days[0].date.split('-').map(Number);
  // getUTCDay: 0 is Sunday; shift so Monday is 0.
  const lead = (new Date(Date.UTC(year, month - 1, day)).getUTCDay() + 6) % 7;
  const cells: (T | null)[] = [...Array.from({ length: lead }, () => null), ...days];
  while (cells.length % 7) cells.push(null);
  return Array.from({ length: cells.length / 7 }, (_, week) => cells.slice(week * 7, week * 7 + 7));
}

/** The month before or after, wrapping the year. */
export function shiftMonth(year: number, month: number, by: number): { year: number; month: number } {
  const index = year * 12 + (month - 1) + by;
  return { year: Math.floor(index / 12), month: (index % 12) + 1 };
}

const TEAM_MONTHS = [
  'Januari',
  'Februari',
  'Maret',
  'April',
  'Mei',
  'Juni',
  'Juli',
  'Agustus',
  'September',
  'Oktober',
  'November',
  'Desember'
];

/**
 * What the lead gate stores, for the team to open the conversation with. In
 * Indonesian whichever edition the couple used, since the same text is what the
 * team's email and WhatsApp alert show.
 */
export function almanacLeadInputs(result: AlmanacResponse): Record<string, string> {
  return {
    month: `${TEAM_MONTHS[result.month - 1]} ${result.year}`,
    shio: result.shio.map((shio) => shio.animal_label).join(' & '),
    good_days: result.days
      .filter((day) => day.rating === 'good')
      .map((day) => Number(day.date.slice(8)))
      .join(', ')
  };
}
