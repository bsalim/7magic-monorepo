/**
 * A market estimate of what a Bali wedding costs, in Australian dollars.
 *
 * Not a 7Magic quote and not read from the venue catalogue: the user decided the
 * calculator and the cost guide show typical market ranges, because what
 * 7Magic charges a foreign couple differs from its venue list prices. Every
 * anchor below is a figure published by someone else, with its source and the
 * date it was checked; every step that turns anchors into a total is written
 * down in METHOD_NOTES, which the pages print under "How we estimate".
 *
 * No source fills a grid of six settings, three styles and 2-150 guests, so this
 * is a model, not a lookup table: venue and supplier lines come from published
 * ranges, a style takes a fixed slice of each range, food and drink scale per
 * guest, and an add-on with no published price is listed as excluded rather
 * than guessed.
 */

import type { ConciergeKey } from '$lib/bali-concierge';
import { CONCIERGE_SERVICES } from '$lib/bali-concierge';
import {
  FIRST_MONTH,
  LAST_MONTH,
  monthFlags,
  type MonthFlags,
  type Source
} from '$lib/tools/bali-dates';

export type Setting = 'villa' | 'resort' | 'clifftop' | 'beach-club' | 'ubud' | 'elopement';
export type Style = 'simple' | 'classic' | 'luxe';
export type City = 'sydney' | 'melbourne' | 'brisbane' | 'perth';
/** Whole Australian dollars. */
export type Range = { low: number; high: number };

export type CostInput = {
  guests: number;
  setting: Setting;
  style: Style;
  year: number;
  month: number;
  addOns: ConciergeKey[];
};

/** A null range is a line nobody publishes a price for: "quoted on request". */
export type CostLine = { key: string; label: string; range: Range | null };

export type CostEstimate = {
  total: Range;
  perGuest: Range;
  lines: CostLine[];
  /** Labels of the lines the total leaves out because they have no published price. */
  excludes: string[];
  guestTravel: Record<City, Range>;
  flags: MonthFlags;
};

export const ESTIMATES_AS_OF = '2026-10-21';

// Exchange rates on 2026-10-21 (open.er-api.com, within 0.3% of the ECB rate).
const AUD_PER_USD = 1 / 0.7;
const IDR_PER_AUD = 12_603;
const usd = (amount: number) => amount * AUD_PER_USD;
const idr = (amount: number) => amount / IDR_PER_AUD;

export const SETTINGS: { key: Setting; label: string; maxGuests: number }[] = [
  { key: 'villa', label: 'Private villa', maxGuests: 150 },
  { key: 'resort', label: 'Resort or hotel', maxGuests: 150 },
  { key: 'clifftop', label: 'Clifftop (Uluwatu, Jimbaran)', maxGuests: 150 },
  { key: 'beach-club', label: 'Beach or beach club', maxGuests: 150 },
  { key: 'ubud', label: 'Ubud jungle or rice fields', maxGuests: 150 },
  { key: 'elopement', label: 'Elopement (just you, up to 10 guests)', maxGuests: 10 }
];

export const STYLES: { key: Style; label: string }[] = [
  { key: 'simple', label: 'Simple' },
  { key: 'classic', label: 'Classic' },
  { key: 'luxe', label: 'Luxe' }
];

const MIN_GUESTS = 2;

/** Where each priced add-on's range was published, checked 2026-10-21. */
const SRC = {
  transfers: {
    title: 'Kura-Kura Bus: Bali airport transfer prices 2026',
    url: 'https://kura2bus.com/blog/bali-airport-transfer-price-guide-2026/'
  },
  nusaPenida: {
    title: 'NusaPenida.org: west Nusa Penida day tour prices',
    url: 'https://nusapenida.org/nusa-penida-west-tour/'
  },
  jimbaran: {
    title: 'GoBaliGo: Jimbaran seafood restaurants and prices',
    url: 'https://gobaligo.id/en/blog/jimbaran-seafood-restaurants-list/'
  },
  villaGrill: {
    title: 'Maya Ubud: in-villa grill dinner',
    url: 'https://mayaresorts.com/ubud/experience/in-villa-grill'
  },
  boat: {
    title: 'Boat Charter Bali: party boat packages',
    url: 'https://boatcharterbali.com/packages.html'
  },
  driver: {
    title: 'Bali Untold: private driver rates',
    url: 'https://baliuntold.com/getting-around/private-drivers/'
  },
  massage: { title: 'Asih Spa: in-villa massage prices', url: 'https://asihspa.com' },
  chef: {
    title: 'Inivie: private chef prices in Bali',
    url: 'https://inivie.com/discover-bali/private-chef-bali'
  },
  nanny: {
    title: 'My Bali Nanny: nanny prices and rates 2026',
    url: 'https://mybalinanny.com/post/bali-nanny-prices-rates-2026'
  },
  surf: {
    title: 'Cabo Bali: Canggu surf school prices',
    url: 'https://cabobali.com/blog/best-surf-schools-canggu'
  },
  doctor: {
    title: 'Finns Beach Club guide: villa doctor visits',
    url: 'https://finnsbeachclub.com/guides/best-medical-home-care-services-bali/'
  },
  holidayPhotographer: {
    title: 'Localgrapher: what a Bali photographer costs',
    url: 'https://localgrapher.com/bali-photographer-cost/'
  }
} satisfies Record<string, Source>;

export const COST_SOURCES: Source[] = [
  {
    title: 'Easy Weddings Annual Survey 2026 (destination weddings average A$32,060, ~55 guests)',
    url: 'https://assets.easyweddings.com/files/2026/02/12092848/EW-Annual-Survey-2026-LowRes.pdf'
  },
  {
    title:
      'Ohana Agency: Bali wedding venue day rates, catering, decor, photo and celebrant (prices verified July 2026)',
    url: 'https://ohana-agency.com/blog/bali-wedding'
  },
  {
    title: 'Happy Bali Wedding: villa rates, banjar fees, decor and bar costs',
    url: 'https://happybaliwedding.com/how-much-does-a-bali-wedding-cost/'
  },
  {
    title: 'Belmond Jimbaran Puri wedding packages (USD)',
    url: 'https://pdfs.belmond.com/jpb/JPB-Wedding-Packages-USD.pdf'
  },
  {
    title: 'The Ritz-Carlton Bali wedding packages',
    url: 'https://www.ritzcarlton.com/en/hotels/dpssw-the-ritz-carlton-bali/weddings/'
  },
  {
    title: 'Bali Weddings: elopement costs (July 2026)',
    url: 'https://baliweddings.com/blog/how-much-does-a-bali-wedding-cost'
  },
  {
    title: 'Bali Done Right: wedding catering per person (October 2026)',
    url: 'https://balidoneright.com/best-catering-bali/'
  },
  {
    title: 'Beach Bride: Bali wedding catering and drinks (April 2026)',
    url: 'https://beachbride.com/bali-wedding-catering/'
  },
  {
    title: 'Bali for Two: wedding planner fees by guest count',
    url: 'https://balifortwo.com/wedding-planner'
  },
  {
    title: 'Love Lab Bali: planner, photographer and videographer fees',
    url: 'https://lovelabbali.com'
  },
  {
    title: 'Australian Consulate-General Bali: notarial fees (CNI A$181)',
    url: 'https://bali.consulate.gov.au/blli/Fees.html'
  },
  {
    title: 'KAYAK: Sydney, Melbourne, Brisbane and Perth to Denpasar return fares',
    url: 'https://www.kayak.com.au/flight-routes/Sydney-Kingsford-Smith-SYD/Bali-Denpasar-DPS'
  },
  {
    title: 'Exchange rates on 21 October 2026 (A$1 = US$0.70 = Rp12,603)',
    url: 'https://open.er-api.com/v6/latest/AUD'
  },
  ...Object.values(SRC)
];

export const METHOD_NOTES: string[] = [
  'Venue hire uses published day rates for each setting (villa, clifftop, beach, Ubud) and published resort package prices. A villa adds the banjar (village) fee. No beach club publishes wedding prices, so the beach club setting uses beach venue day rates.',
  'Each style takes a slice of every published range: Simple the bottom quarter, Classic the second quarter, Luxe the top half, because the top of each range is the "lavish" end.',
  'Food and drink is per guest: a buffet with soft drinks for Simple, a plated dinner with a basic open bar for Classic, fine dining with a premium bar for Luxe. Resorts and clifftop hotels add 21% tax and service on top.',
  'An elopement is priced as a published elopement package (venue, celebrant, styling and photographer), plus food for any guests.',
  'US dollar and rupiah prices are converted at the 21 October 2026 rate. Lines are rounded to the nearest A$10.',
  'Guest flights are typical return economy fares from KAYAK; December and July cost more. They are your guests’ cost, not part of your total.',
  'Add-ons are priced for a stated amount (for example one car for three days). An add-on nobody publishes a price for is listed as not included.',
  'We found no published figure that changes with the season, so the month does not change the estimate; it only shows the dates to plan around.'
];

/** Published lows and highs, already in AUD. */
const VENUE: Record<Exclude<Setting, 'elopement'>, Range> = {
  // Ohana day rates (USD 3,000-10,000) plus a banjar fee (USD 200-500).
  villa: { low: usd(3_200), high: usd(10_500) },
  // Belmond Jimbaran Puri from US$3,509++, Ritz-Carlton Majestic US$8,088++.
  resort: { low: usd(3_509 * 1.21), high: usd(8_088 * 1.21) },
  clifftop: { low: usd(4_000), high: usd(15_000) },
  // No beach club publishes wedding pricing; beach venue day rates stand in.
  'beach-club': { low: usd(2_500), high: usd(8_000) },
  ubud: { low: usd(2_000), high: usd(6_000) }
};

// Bali Weddings: an elopement for 2-10 guests, US$1,500-5,000.
const ELOPEMENT_PACKAGE: Range = { low: usd(1_500), high: usd(5_000) };

/** Food and drink per guest, by style (catering + bar). */
const FOOD_PER_GUEST: Record<Style, Range> = {
  // Buffet or BBQ Rp450k-950k, free-flow soft drinks about US$10.
  simple: { low: idr(450_000) + usd(10), high: idr(950_000) + usd(10) },
  // Plated 3-5 courses Rp800k-1.3m, basic open bar about US$40.
  classic: { low: idr(800_000) + usd(40), high: idr(1_300_000) + usd(40) },
  // Fine dining Rp1.5m-3m, premium open bar about US$80.
  luxe: { low: idr(1_500_000) + usd(80), high: idr(3_000_000) + usd(80) }
};

const HOTEL_SERVICE = 1.21;

// Happy Bali Wedding US$1,500 simple to Ohana US$12,000 for 100+ guests.
const STYLING: Range = { low: usd(1_500), high: usd(12_000) };
// Ohana, photo and video combined.
const PHOTO: Range = { low: usd(1_200), high: usd(7_000) };
// Ohana, celebrant or ceremony.
const CEREMONY: Range = { low: usd(300), high: usd(1_200) };
// Bali for Two from US$2,000; Love Lab full service to US$8,000.
const PLANNER: Range = { low: usd(2_000), high: usd(8_000) };

const STYLE_SLICE: Record<Style, [number, number]> = {
  simple: [0, 0.25],
  classic: [0.25, 0.5],
  luxe: [0.5, 1]
};

function slice(range: Range, style: Style): Range {
  const [from, to] = STYLE_SLICE[style];
  const span = range.high - range.low;
  return { low: range.low + span * from, high: range.low + span * to };
}

const scale = (range: Range, by: number): Range => ({ low: range.low * by, high: range.high * by });
const roundTen = (value: number) => Math.round(value / 10) * 10;
const rounded = (range: Range): Range => ({ low: roundTen(range.low), high: roundTen(range.high) });

/**
 * What each concierge add-on costs the couple, for a stated amount. Null where
 * no price is published, or where the guests pay for it themselves.
 */
const ADD_ON_PRICES: Partial<Record<ConciergeKey, (guests: number) => Range | null>> = {
  // Consulate CNI A$181 plus civil and religious fees US$700-1,200.
  legal: () => ({ low: 181 + usd(700), high: 181 + usd(1_200) }),
  // Rp480k-560k a car, three guests to a car, there and back.
  transfers: (guests) =>
    scale({ low: idr(480_000), high: idr(560_000) }, Math.ceil(guests / 3) * 2),
  accommodation: () => null,
  arrival: () => null,
  // A Nusa Penida day trip, Rp858k-1.525m a guest.
  activities: (guests) => scale({ low: idr(858_000), high: idr(1_525_000) }, guests),
  // Welcome dinner only: Jimbaran seafood Rp150k to an in-villa grill Rp800k++.
  welcome: (guests) => scale({ low: idr(150_000), high: idr(800_000 * HOTEL_SERVICE) }, guests),
  // A blessing led by a pemangku, US$200-400.
  blessing: () => ({ low: usd(200), high: usd(400) }),
  // One party boat for up to 12, US$670-850.
  hens: () => ({ low: usd(670), high: usd(850) }),
  // Published packages run Rp5m-22.8m, but the top of that range could not
  // be tied to one source, so the shoot is quoted on request.
  prewedding: () => null,
  // Rp600k-1m a day; one car for three days.
  car: () => scale({ low: idr(600_000), high: idr(1_000_000) }, 3),
  // Rp300k-450k for 60 minutes in the villa; four massages.
  massage: () => scale({ low: idr(300_000), high: idr(450_000) }, 4),
  // Rp230k-375k a person a meal; one family dinner for ten.
  chef: () => scale({ low: idr(230_000), high: idr(375_000) }, 10),
  reservations: () => null,
  // Rp97.5k-130k an hour; one wedding night of six hours.
  nanny: () => scale({ low: idr(97_500), high: idr(130_000) }, 6),
  // A private surf lesson in Canggu, Rp400k-700k each, for two.
  wellness: () => scale({ low: idr(400_000), high: idr(700_000) }, 2),
  // One villa visit, Rp550k, medicines extra.
  doctor: () => ({ low: idr(550_000), high: idr(550_000) }),
  // A holiday photo session, US$280-630.
  'holiday-photographer': () => ({ low: usd(280), high: usd(630) })
};

const byUrl = (url: string) => COST_SOURCES.find((source) => source.url === url)!;

/** The published sources behind each priced add-on, all listed in COST_SOURCES. */
export const ADD_ON_SOURCES: Partial<Record<ConciergeKey, Source[]>> = {
  legal: [
    byUrl('https://bali.consulate.gov.au/blli/Fees.html'),
    byUrl('https://happybaliwedding.com/how-much-does-a-bali-wedding-cost/')
  ],
  transfers: [SRC.transfers],
  activities: [SRC.nusaPenida],
  welcome: [SRC.jimbaran, SRC.villaGrill],
  blessing: [byUrl('https://ohana-agency.com/blog/bali-wedding')],
  hens: [SRC.boat],
  car: [SRC.driver],
  massage: [SRC.massage],
  chef: [SRC.chef],
  nanny: [SRC.nanny],
  wellness: [SRC.surf],
  doctor: [SRC.doctor],
  'holiday-photographer': [SRC.holidayPhotographer]
};

/** The add-ons the calculator offers: a vow renewal is an event of its own, not a wedding extra. */
export const CALCULATOR_ADD_ONS = CONCIERGE_SERVICES.filter((service) => service.key !== 'renewal');
const ADD_ON_KEYS = new Set<string>(CALCULATOR_ADD_ONS.map((service) => service.key));

/** KAYAK typical return economy fares, AUD. */
const GUEST_TRAVEL: Record<City, Range> = {
  sydney: { low: 556, high: 937 },
  melbourne: { low: 457, high: 837 },
  brisbane: { low: 538, high: 850 },
  perth: { low: 320, high: 590 }
};

function clampGuests(guests: number, setting: Setting): number {
  const max = SETTINGS.find((s) => s.key === setting)!.maxGuests;
  return Math.min(Math.max(Math.round(guests), MIN_GUESTS), max);
}

export function estimateCost(input: CostInput): CostEstimate {
  const guests = clampGuests(input.guests, input.setting);
  const { setting, style } = input;
  const hotel = setting === 'resort' || setting === 'clifftop';
  const food = scale(FOOD_PER_GUEST[style], guests * (hotel ? HOTEL_SERVICE : 1));

  const base: CostLine[] =
    setting === 'elopement'
      ? [
          { key: 'package', label: 'Elopement package', range: slice(ELOPEMENT_PACKAGE, style) },
          { key: 'food', label: 'Food & drinks', range: food }
        ]
      : [
          {
            key: 'venue',
            label: 'Venue hire / minimum spend',
            range: slice(VENUE[setting], style)
          },
          { key: 'food', label: 'Food & drinks', range: food },
          { key: 'styling', label: 'Styling & flowers', range: slice(STYLING, style) },
          { key: 'photo', label: 'Photo & video', range: slice(PHOTO, style) },
          { key: 'ceremony', label: 'Ceremony & celebrant', range: slice(CEREMONY, style) },
          { key: 'planner', label: 'Planner & coordination', range: slice(PLANNER, style) }
        ];

  const addOns: CostLine[] = CALCULATOR_ADD_ONS.filter((service) =>
    input.addOns.includes(service.key)
  ).map((service) => ({
    key: `addon:${service.key}`,
    label: service.name,
    range: ADD_ON_PRICES[service.key]?.(guests) ?? null
  }));

  const lines = [...base, ...addOns].map((line) => ({
    ...line,
    range: line.range && rounded(line.range)
  }));
  const priced = lines.filter((line) => line.range);
  const total = {
    low: priced.reduce((sum, line) => sum + line.range!.low, 0),
    high: priced.reduce((sum, line) => sum + line.range!.high, 0)
  };

  return {
    total,
    perGuest: { low: Math.round(total.low / guests), high: Math.round(total.high / guests) },
    lines,
    excludes: lines.filter((line) => !line.range).map((line) => line.label),
    guestTravel: GUEST_TRAVEL,
    flags: monthFlags(input.year, input.month)
  };
}

const monthIndex = (year: number, month: number) => year * 12 + (month - 1);

function firstAllowedMonth(today: Date): number {
  return Math.max(
    monthIndex(FIRST_MONTH.year, FIRST_MONTH.month),
    monthIndex(today.getFullYear(), today.getMonth() + 1)
  );
}

/** The months the calculator offers, oldest first. */
export function monthOptions(today: Date): { year: number; month: number }[] {
  const options = [];
  for (let i = firstAllowedMonth(today); i <= monthIndex(LAST_MONTH.year, LAST_MONTH.month); i++) {
    options.push({ year: Math.floor(i / 12), month: (i % 12) + 1 });
  }
  return options;
}

export function defaultInput(today: Date): CostInput {
  const last = monthIndex(LAST_MONTH.year, LAST_MONTH.month);
  const july = Math.min(monthIndex(today.getFullYear() + 1, 7), last);
  return {
    guests: 55,
    setting: 'villa',
    style: 'classic',
    year: Math.floor(july / 12),
    month: (july % 12) + 1,
    addOns: []
  };
}

const SETTING_KEYS = new Set<string>(SETTINGS.map((s) => s.key));
const STYLE_KEYS = new Set<string>(STYLES.map((s) => s.key));

/** A shared link's inputs. Anything invalid falls back to the default, never to NaN. */
export function fromQuery(params: URLSearchParams, today: Date): CostInput {
  const fallback = defaultInput(today);
  const setting = SETTING_KEYS.has(params.get('setting') ?? '')
    ? (params.get('setting') as Setting)
    : fallback.setting;
  const style = STYLE_KEYS.has(params.get('style') ?? '')
    ? (params.get('style') as Style)
    : fallback.style;

  const guestsParam = Number(params.get('guests'));
  const guests = clampGuests(
    Number.isFinite(guestsParam) && guestsParam >= MIN_GUESTS ? guestsParam : fallback.guests,
    setting
  );

  const year = Number(params.get('year'));
  const month = Number(params.get('month'));
  const index = monthIndex(year, month);
  const validMonth =
    Number.isInteger(year) &&
    Number.isInteger(month) &&
    month >= 1 &&
    month <= 12 &&
    index >= firstAllowedMonth(today) &&
    index <= monthIndex(LAST_MONTH.year, LAST_MONTH.month);

  const addOns = (params.get('addons') ?? '')
    .split(',')
    .filter((key): key is ConciergeKey => ADD_ON_KEYS.has(key));

  return {
    guests,
    setting,
    style,
    year: validMonth ? year : fallback.year,
    month: validMonth ? month : fallback.month,
    addOns: [...new Set(addOns)]
  };
}

export function toQuery(input: CostInput): string {
  const params = new URLSearchParams({
    guests: String(input.guests),
    setting: input.setting,
    style: input.style,
    year: String(input.year),
    month: String(input.month)
  });
  if (input.addOns.length) params.set('addons', input.addOns.join(','));
  return params.toString();
}
