/**
 * The Ba Zi tool's side of `POST /api/v1/public/bazi`: wire types, the call
 * through the `/api/bazi` proxy, and what the lead gate sends.
 *
 * The calculation lives in the API (`app/domains/bazi`), not here: solar terms
 * need an astronomy series that has no business in the browser bundle, and
 * keeping one engine means the page and any later tool (Tanggal Baik) agree.
 * Field names are the API's snake_case.
 */

export type Zone = 'WIB' | 'WITA' | 'WIT';
export type Tone = 'harmony' | 'balanced' | 'clash';
export type Verdict = 'safe' | 'consider' | 'clash';
export type Rule =
  | 'six_combination'
  | 'half_harmony'
  | 'clash'
  | 'harm'
  | 'stem_combination'
  | 'generates'
  | 'controls'
  | 'same_element';
export type Element = 'wood' | 'fire' | 'earth' | 'metal' | 'water';

export type PartnerIn = {
  name?: string | null;
  /** ISO date; empty while the visitor has not picked one. */
  birth_date: string;
  /** "HH:MM", or null when the birth time is unknown. */
  birth_time: string | null;
  zone: Zone;
};

export type BaziRequest = {
  partners: [PartnerIn, PartnerIn];
  dates: string[];
  locale: 'id' | 'en';
};

export type StemOut = {
  index: number;
  char: string;
  pinyin: string;
  element: string;
  element_label: string;
  yang: boolean;
};

export type BranchOut = {
  index: number;
  char: string;
  pinyin: string;
  element: string;
  element_label: string;
  animal: string;
  animal_label: string;
};

export type PillarOut = {
  stem: StemOut;
  branch: BranchOut;
  depends_on_time: boolean;
  near_term: boolean;
};

export type ChartOut = {
  name: string | null;
  year: PillarOut;
  month: PillarOut;
  day: PillarOut;
  hour: PillarOut | null;
  day_master: StemOut;
  shio: BranchOut;
  elements: Record<string, number>;
};

export type FindingOut = {
  rule: Rule;
  rule_label: string;
  kind: 'harmony' | 'caution' | 'clash' | 'neutral';
  pillar: 'year' | 'day' | 'day_master';
  a: string;
  b: string;
  source: number | null;
};

export type DateReasonOut = {
  partner: number;
  against: 'shio' | 'day';
  rule: Rule;
  rule_label: string;
};

export type DateCheckOut = {
  date: string;
  pillar: PillarOut;
  verdict: Verdict;
  reasons: DateReasonOut[];
};

export type BaziResponse = {
  charts: ChartOut[];
  tone: Tone;
  tone_label: string;
  findings: FindingOut[];
  date_checks: DateCheckOut[];
};

/** The API could not be reached or failed: worth a retry, the inputs are fine. */
export class BaziUnavailableError extends Error {}
/** The API rejected the inputs (422): the visitor has something to correct. */
export class BaziInputError extends Error {}

export const FIRST_YEAR = 1900;
export const LAST_YEAR = 2100;
export const MAX_DATES = 3;

export async function fetchBazi(body: BaziRequest, fetcher: typeof fetch = fetch): Promise<BaziResponse> {
  let response: Response;
  try {
    response = await fetcher('/api/bazi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
  } catch {
    throw new BaziUnavailableError('network');
  }
  if (response.status === 422 || response.status === 400) throw new BaziInputError(String(response.status));
  if (!response.ok) throw new BaziUnavailableError(String(response.status));
  return (await response.json()) as BaziResponse;
}

/**
 * What the lead gate stores, for the team to open the conversation with.
 *
 * Deliberately no birth date or time: those are personal data the team can ask
 * for in person, and the shio, day masters and checked dates are enough to
 * start (see the design doc's privacy call).
 */
export function baziLeadInputs(result: BaziResponse): Record<string, string> {
  const [first, second] = result.charts;
  return {
    shio: `${first.shio.animal_label} / ${second.shio.animal_label}`,
    day_masters: [first, second].map((c) => `${c.day_master.char} ${c.day_master.element_label}`).join(' / '),
    tone: result.tone,
    dates: result.date_checks.map((check) => `${check.date}:${check.verdict}`).join(',')
  };
}

/** The candidate dates to send: filled fields only, each once, in the order typed. */
export function uniqueDates(dates: string[]): string[] {
  return [...new Set(dates.filter(Boolean))];
}

/** Which message a failed call deserves: the visitor's input, or a retry. */
export function failureKind(failure: unknown): 'invalid' | 'unavailable' {
  return failure instanceof BaziInputError ? 'invalid' : 'unavailable';
}

/**
 * The names the reading and card use. Blank names fall back to neutral labels,
 * not to the placeholders: those are the example couple, and a stranger's
 * reading should not be written about Raka and Nadia.
 */
export function displayNames(raw: [string, string], fallback: [string, string]): [string, string] {
  return [raw[0].trim() || fallback[0], raw[1].trim() || fallback[1]];
}

/** Whether any year or month pillar the reading leans on is uncertain. */
export function hasUncertainPillar(charts: ChartOut[]): boolean {
  return charts.some((chart) =>
    [chart.year, chart.month].some((pillar) => pillar.depends_on_time || pillar.near_term)
  );
}

export function isCompleteBirth(partner: PartnerIn): boolean {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(partner.birth_date);
  if (!match) return false;
  const [year, month, day] = match.slice(1).map(Number);
  if (year < FIRST_YEAR || year > LAST_YEAR) return false;
  const parsed = new Date(Date.UTC(year, month - 1, day));
  return parsed.getUTCMonth() === month - 1 && parsed.getUTCDate() === day;
}
