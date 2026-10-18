import { describe, expect, it } from 'vitest';
import {
  BaziInputError,
  BaziUnavailableError,
  baziLeadInputs,
  fetchBazi,
  isCompleteBirth,
  type BaziRequest,
  type BaziResponse
} from './bazi';

const SAMPLE_BIRTH_DATES = ['1995-05-05', '1996-08-17'];

const stem = (char: string, element_label: string) => ({
  index: 0,
  char,
  pinyin: '',
  element: 'wood',
  element_label,
  yang: true
});
const branch = (animal_label: string) => ({
  index: 0,
  char: '',
  pinyin: '',
  element: 'water',
  element_label: 'Air',
  animal: 'rat',
  animal_label
});
const pillar = { stem: stem('甲', 'Kayu'), branch: branch('Tikus'), depends_on_time: false, near_term: false };
const chart = (name: string, master: [string, string], shio: string) => ({
  name,
  year: pillar,
  month: pillar,
  day: pillar,
  hour: null,
  day_master: stem(...master),
  shio: branch(shio),
  elements: { wood: 2, fire: 1, earth: 1, metal: 1, water: 1 }
});

const SAMPLE_RESPONSE: BaziResponse = {
  charts: [chart('Raka', ['乙', 'Kayu'], 'Babi'), chart('Nadia', ['庚', 'Logam'], 'Tikus')],
  tone: 'balanced',
  tone_label: 'Seimbang',
  findings: [],
  date_checks: [
    { date: '2026-09-20', pillar, verdict: 'safe', reasons: [] },
    { date: '2026-10-10', pillar, verdict: 'clash', reasons: [] }
  ]
};

const REQUEST: BaziRequest = {
  partners: [
    { name: 'Raka', birth_date: SAMPLE_BIRTH_DATES[0], birth_time: '10:00', zone: 'WIB' },
    { name: 'Nadia', birth_date: SAMPLE_BIRTH_DATES[1], birth_time: null, zone: 'WITA' }
  ],
  dates: [],
  locale: 'id'
};

const answering = (status: number, body: unknown = {}) =>
  (async () => new Response(JSON.stringify(body), { status })) as unknown as typeof fetch;

describe('baziLeadInputs', () => {
  it('builds lead inputs without any birth data', () => {
    const inputs = baziLeadInputs(SAMPLE_RESPONSE);
    expect(Object.keys(inputs).sort()).toEqual(['dates', 'day_masters', 'shio', 'tone']);
    for (const birth of SAMPLE_BIRTH_DATES) expect(JSON.stringify(inputs)).not.toContain(birth);
    expect(inputs.dates).toBe('2026-09-20:safe,2026-10-10:clash');
    expect(inputs.shio).toBe('Babi / Tikus');
    expect(inputs.day_masters).toBe('乙 Kayu / 庚 Logam');
    expect(inputs.tone).toBe('balanced');
  });

  it('leaves dates empty before any were checked', () => {
    expect(baziLeadInputs({ ...SAMPLE_RESPONSE, date_checks: [] }).dates).toBe('');
  });
});

describe('fetchBazi', () => {
  it('posts to the proxy and returns the result', async () => {
    let seen: { url: string; body: unknown } | undefined;
    const fetcher = (async (url: string, init: RequestInit) => {
      seen = { url, body: JSON.parse(String(init.body)) };
      return new Response(JSON.stringify(SAMPLE_RESPONSE), { status: 200 });
    }) as unknown as typeof fetch;

    expect(await fetchBazi(REQUEST, fetcher)).toEqual(SAMPLE_RESPONSE);
    expect(seen).toEqual({ url: '/api/bazi', body: REQUEST });
  });

  it('turns a 502 into BaziUnavailableError', async () => {
    await expect(fetchBazi(REQUEST, answering(502))).rejects.toBeInstanceOf(BaziUnavailableError);
  });

  it('turns a network failure into BaziUnavailableError', async () => {
    const failing = (async () => {
      throw new TypeError('fetch failed');
    }) as unknown as typeof fetch;
    await expect(fetchBazi(REQUEST, failing)).rejects.toBeInstanceOf(BaziUnavailableError);
  });

  it('turns a 422 into BaziInputError', async () => {
    await expect(fetchBazi(REQUEST, answering(422, { detail: [] }))).rejects.toBeInstanceOf(BaziInputError);
  });
});

describe('isCompleteBirth', () => {
  it('needs a real date between 1900 and 2100', () => {
    expect(isCompleteBirth({ birth_date: '1995-05-05', birth_time: null, zone: 'WIB' })).toBe(true);
    expect(isCompleteBirth({ birth_date: '1899-12-31', birth_time: null, zone: 'WIB' })).toBe(false);
    expect(isCompleteBirth({ birth_date: '2101-01-01', birth_time: null, zone: 'WIB' })).toBe(false);
    expect(isCompleteBirth({ birth_date: '2026-02-30', birth_time: null, zone: 'WIB' })).toBe(false);
    expect(isCompleteBirth({ birth_date: '', birth_time: null, zone: 'WIB' })).toBe(false);
  });
});
