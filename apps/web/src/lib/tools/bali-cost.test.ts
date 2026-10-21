import { describe, expect, it } from 'vitest';
import { monthFlags } from './bali-dates';
import {
  ADD_ON_SOURCES,
  CALCULATOR_ADD_ONS,
  COST_SOURCES,
  METHOD_NOTES,
  SETTINGS,
  defaultInput,
  estimateCost,
  fromQuery,
  toQuery,
  type CostInput,
  type Setting
} from './bali-cost';

const today = new Date('2026-10-21T09:00:00+08:00');
const base: CostInput = {
  guests: 55,
  setting: 'villa',
  style: 'classic',
  year: 2027,
  month: 7,
  addOns: []
};
const at = (patch: Partial<CostInput>) => estimateCost({ ...base, ...patch });

describe('estimateCost', () => {
  const groupSettings = SETTINGS.map((s) => s.key).filter(
    (key) => key !== 'elopement'
  ) as Setting[];

  it('never gets cheaper as the guest list grows', () => {
    for (const setting of groupSettings) {
      const small = at({ setting, guests: 30 }).total;
      const large = at({ setting, guests: 100 }).total;
      expect(large.low, setting).toBeGreaterThanOrEqual(small.low);
      expect(large.high, setting).toBeGreaterThanOrEqual(small.high);
    }
  });

  it('orders the styles simple, classic, luxe', () => {
    const simple = at({ style: 'simple' }).total;
    const classic = at({ style: 'classic' }).total;
    const luxe = at({ style: 'luxe' }).total;
    expect(classic.low).toBeGreaterThanOrEqual(simple.low);
    expect(luxe.low).toBeGreaterThanOrEqual(classic.low);
  });

  it('adds up to its own lines', () => {
    const estimate = at({ addOns: ['car', 'massage'] });
    const priced = estimate.lines.filter((line) => line.range);
    expect(estimate.total.low).toBe(priced.reduce((sum, line) => sum + line.range!.low, 0));
    expect(estimate.total.high).toBe(priced.reduce((sum, line) => sum + line.range!.high, 0));
  });

  it('names an unpriced add-on in excludes instead of leaving it out silently', () => {
    expect(at({}).excludes).toEqual([]);
    const estimate = at({ addOns: ['legal', 'car', 'nanny', 'doctor', 'reservations'] });
    for (const line of estimate.lines.filter((l) => l.range === null)) {
      expect(estimate.excludes).toContain(line.label);
    }
  });

  it('works out the per-guest figure from the total', () => {
    const estimate = at({ guests: 40 });
    expect(estimate.perGuest.low).toBe(Math.round(estimate.total.low / 40));
    expect(estimate.perGuest.high).toBe(Math.round(estimate.total.high / 40));
  });

  // Easy Weddings 2026: the average Australian destination wedding is A$32,060
  // for about 55 guests. A classic villa wedding for 55 should sit near it.
  it('lands near the published Australian average for a classic 55-guest wedding', () => {
    const { total } = at({});
    expect(total.low).toBeLessThanOrEqual(40_000);
    expect(total.high).toBeGreaterThanOrEqual(20_000);
  });

  it('prices an 80-guest elopement link as an elopement of the maximum size', () => {
    const elopement = SETTINGS.find((s) => s.key === 'elopement')!;
    expect(at({ setting: 'elopement', guests: 80 })).toEqual(
      at({ setting: 'elopement', guests: elopement.maxGuests })
    );
  });

  it('carries the month flags for the chosen month', () => {
    expect(at({ year: 2027, month: 3 }).flags).toEqual(monthFlags(2027, 3));
  });

  it('gives a guest travel range for each city', () => {
    const travel = at({}).guestTravel;
    for (const city of ['sydney', 'melbourne', 'brisbane', 'perth'] as const) {
      expect(travel[city].high).toBeGreaterThan(travel[city].low);
    }
  });
});

describe('query state', () => {
  it('round-trips a valid input', () => {
    const input: CostInput = {
      ...base,
      setting: 'clifftop',
      style: 'luxe',
      addOns: ['car', 'hens']
    };
    expect(fromQuery(new URLSearchParams(toQuery(input)), today)).toEqual(input);
  });

  it('falls back to defaults for every invalid value but keeps the valid add-ons', () => {
    const params = new URLSearchParams(
      'guests=-5&setting=foo&style=&year=2019&month=13&addons=car,bogus'
    );
    expect(fromQuery(params, today)).toEqual({ ...defaultInput(today), addOns: ['car'] });
  });

  it('rejects a month already past and one beyond 2028', () => {
    const past = new URLSearchParams('year=2026&month=9');
    const far = new URLSearchParams('year=2029&month=1');
    const fallback = defaultInput(today);
    expect(fromQuery(past, today)).toMatchObject({ year: fallback.year, month: fallback.month });
    expect(fromQuery(far, today)).toMatchObject({ year: fallback.year, month: fallback.month });
  });

  it('clamps guests to the chosen setting', () => {
    expect(fromQuery(new URLSearchParams('setting=elopement&guests=80'), today).guests).toBe(
      SETTINGS.find((s) => s.key === 'elopement')!.maxGuests
    );
  });

  it('defaults to 55 guests, a classic villa wedding next July', () => {
    expect(defaultInput(today)).toEqual({
      guests: 55,
      setting: 'villa',
      style: 'classic',
      year: 2027,
      month: 7,
      addOns: []
    });
  });
});

describe('sources', () => {
  // Every price the calculator prints must trace to a published source the
  // page lists; an add-on without one is quoted on request instead.
  it('lists a source for every priced add-on', () => {
    const listed = new Set(COST_SOURCES.map((source) => source.url));
    for (const service of CALCULATOR_ADD_ONS) {
      const line = estimateCost({ ...base, addOns: [service.key] }).lines.find(
        (l) => l.key === `addon:${service.key}`
      )!;
      if (!line.range) continue;
      const sources = ADD_ON_SOURCES[service.key] ?? [];
      expect(sources.length, service.key).toBeGreaterThan(0);
      for (const source of sources) expect(listed.has(source.url), source.url).toBe(true);
    }
  });

  it('says beach clubs are priced from beach venue rates', () => {
    expect(METHOD_NOTES.join(' ')).toMatch(/beach club/i);
  });
});
