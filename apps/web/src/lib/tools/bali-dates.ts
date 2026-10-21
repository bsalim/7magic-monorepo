/**
 * The dates a couple planning a Bali wedding from Australia needs to plan
 * around: Balinese holy days, Indonesian public holidays, Australian school
 * holidays and the season.
 *
 * Every date carries the source it was checked against (2026-10-21). These pages
 * win on being right where the popular results are not -- several print Nyepi
 * 2027 as 9 or 18 March -- so a date that could not be confirmed is either
 * labelled as calculated or left out:
 *
 * - Galungan falls every 210 days (the pawukon cycle) and Kuningan ten days
 *   after it. Only Galungan on 13 January 2027 is in a published Bali calendar
 *   so far; the rest are calculated from that cycle and marked `provisional`.
 * - South Australia's education department page could not be loaded, so SA is
 *   not listed rather than listed from a secondary site.
 * - Victoria and Western Australia publish term dates; their holidays are the
 *   gaps between terms.
 * - Indonesia's 2028 holidays come out in the SKB late in 2027. Until then a
 *   2028 month carries a notice instead of looking clear.
 */

export type Source = { title: string; url: string };
export type AuState = 'NSW' | 'VIC' | 'QLD' | 'WA';
export type BaliEventKind = 'nyepi' | 'galungan' | 'kuningan' | 'id-holiday' | 'au-school';

export type BaliEvent = {
  kind: BaliEventKind;
  name: string;
  /** ISO dates, inclusive. */
  start: string;
  end: string;
  state?: AuState;
  /** Calculated from the 210-day cycle, not yet in a published calendar. */
  provisional?: boolean;
  note?: string;
  source: Source;
};

export type Season = 'wet' | 'dry' | 'shoulder';
export type MonthFlags = { season: Season; events: BaliEvent[]; notices: string[] };

export const DATES_CHECKED = '2026-10-21';

/** The first and last month the planner and calculator cover. */
export const FIRST_MONTH = { year: 2027, month: 1 };
export const LAST_MONTH = { year: 2028, month: 12 };

/** The last year each calendar has been published for. */
export const ANNOUNCED: { idHolidays: number; auSchool: Record<AuState, number> } = {
  idHolidays: 2027,
  auSchool: { NSW: 2028, VIC: 2028, QLD: 2028, WA: 2028 }
};

const SKB_2027: Source = {
  title: 'SKB 3 Menteri: national holidays and collective leave 2027 (Kemensetneg)',
  url: 'https://setneg.go.id/baca/index/inilah_skb_3_menteri_libur_nasional_dan_cuti_bersama_2027'
};
const ISI_BALI: Source = {
  title: 'ISI Bali academic calendar 2026/2027 (Galungan 12–14 January 2027)',
  url: 'https://isibali.ac.id/wp-content/uploads/2026/08/Kalender-Akademik-ISI-BALI-Ganjil-Genap-2026-2027-Revisi-31-agustus-1.pdf'
};
const KEMENAG_2026: Source = {
  title: 'Kemenag Bimas Hindu circular on Galungan 17 June 2026 (reported by Katadata)',
  url: 'https://katadata.co.id/lifestyle/varia/6a3244b6b5cf1/kapan-hari-raya-galungan-dan-kuningan-2026-simak-jadwal-dan-perayaannya'
};
const NSW: Source = {
  title: 'NSW Department of Education: term and vacation dates',
  url: 'https://education.nsw.gov.au/schooling/calendars/future-and-past-nsw-term-and-vacation-dates'
};
const VIC: Source = {
  title: 'Victoria: school term dates and holidays',
  url: 'https://www.vic.gov.au/school-term-dates-and-holidays-victoria'
};
const QLD: Source = {
  title: 'Queensland Department of Education: future term dates',
  url: 'https://education.qld.gov.au/about-us/calendar/future-dates'
};
const WA: Source = {
  title: 'WA Department of Education: future term dates',
  url: 'https://www.education.wa.edu.au/future-term-dates'
};

const DAY = 86_400_000;
const GALUNGAN_ANCHOR = '2026-06-17';
const CYCLE_DAYS = 210;
const KUNINGAN_OFFSET = 10;

const iso = (time: number) => new Date(time).toISOString().slice(0, 10);
const addDays = (date: string, days: number) => iso(Date.parse(date) + days * DAY);

/** Every Galungan from `fromIso` to `toIso`, inclusive, stepping the 210-day cycle. */
export function galunganDates(fromIso: string, toIso: string): string[] {
  const anchor = Date.parse(GALUNGAN_ANCHOR);
  const from = Date.parse(fromIso);
  const to = Date.parse(toIso);
  const step = CYCLE_DAYS * DAY;
  const dates: string[] = [];
  for (let time = anchor + Math.ceil((from - anchor) / step) * step; time <= to; time += step) {
    dates.push(iso(time));
  }
  return dates;
}

// The one Galungan a published calendar confirms; the rest of the cycle is maths.
const PUBLISHED_GALUNGAN = new Set(['2027-01-13']);

function balineseHolyDays(): BaliEvent[] {
  return galunganDates('2027-01-01', '2028-12-31').flatMap((galungan) => {
    const published = PUBLISHED_GALUNGAN.has(galungan);
    const calculated: Source = published ? ISI_BALI : KEMENAG_2026;
    const kuningan = addDays(galungan, KUNINGAN_OFFSET);
    return [
      {
        kind: 'galungan' as const,
        name: 'Galungan',
        start: galungan,
        end: galungan,
        provisional: published ? undefined : true,
        note: 'Bali’s biggest holy days. Schools and offices usually close the day before to the day after, and many local vendors and staff are with family.',
        source: calculated
      },
      {
        kind: 'kuningan' as const,
        name: 'Kuningan',
        start: kuningan,
        end: kuningan,
        provisional: true,
        note: 'Closes the Galungan period, ten days later. Temples are busy and ceremonies are held island-wide.',
        source: calculated
      }
    ];
  });
}

const idHoliday = (name: string, start: string, end = start, note?: string): BaliEvent => ({
  kind: 'id-holiday',
  name,
  start,
  end,
  note,
  source: SKB_2027
});

const school = (state: AuState, name: string, start: string, end: string): BaliEvent => ({
  kind: 'au-school',
  name: `${state} ${name} school holidays`,
  start,
  end,
  state,
  source: { NSW, VIC, QLD, WA }[state]
});

export const BALI_EVENTS: BaliEvent[] = [
  {
    kind: 'nyepi',
    name: 'Nyepi (Balinese Day of Silence)',
    start: '2027-03-08',
    end: '2027-03-08',
    note: 'The whole island stays indoors for 24 hours from 6am, and Ngurah Rai airport closes. No wedding can be held, and guests cannot fly in or out.',
    source: SKB_2027
  },
  ...balineseHolyDays(),

  idHoliday('New Year’s Day', '2027-01-01'),
  idHoliday('Isra Mi’raj', '2027-01-05'),
  idHoliday('Chinese New Year and collective leave', '2027-02-05', '2027-02-06'),
  idHoliday(
    'Idul Fitri (Lebaran) and collective leave',
    '2027-03-09',
    '2027-03-15',
    'Right after Nyepi, so 6–15 March is one long break across Indonesia: flights and hotels are at their fullest.'
  ),
  idHoliday('Good Friday and Easter', '2027-03-25', '2027-03-28'),
  idHoliday('Labour Day', '2027-05-01'),
  idHoliday('Ascension Day', '2027-05-06'),
  idHoliday('Idul Adha, Vesak and collective leave', '2027-05-17', '2027-05-20'),
  idHoliday('Pancasila Day', '2027-06-01'),
  idHoliday('Islamic New Year', '2027-06-06'),
  idHoliday('Prophet’s Birthday (Maulid)', '2027-08-15'),
  idHoliday('Independence Day', '2027-08-17'),
  idHoliday('Christmas and Isra Mi’raj', '2027-12-24', '2027-12-26'),

  school('NSW', 'summer', '2026-12-18', '2027-01-27'),
  school('NSW', 'autumn', '2027-04-12', '2027-04-23'),
  school('NSW', 'winter', '2027-07-05', '2027-07-16'),
  school('NSW', 'spring', '2027-09-27', '2027-10-08'),
  school('NSW', 'summer', '2027-12-21', '2028-01-28'),
  school('NSW', 'autumn', '2028-04-10', '2028-04-21'),
  school('NSW', 'winter', '2028-07-10', '2028-07-21'),
  school('NSW', 'spring', '2028-10-03', '2028-10-13'),
  school('NSW', 'summer', '2028-12-22', '2029-01-25'),

  school('VIC', 'summer', '2026-12-21', '2027-01-27'),
  school('VIC', 'autumn', '2027-03-26', '2027-04-11'),
  school('VIC', 'winter', '2027-06-26', '2027-07-11'),
  school('VIC', 'spring', '2027-09-18', '2027-10-03'),
  school('VIC', 'summer', '2027-12-18', '2028-01-26'),
  school('VIC', 'autumn', '2028-04-01', '2028-04-17'),
  school('VIC', 'winter', '2028-07-01', '2028-07-16'),
  school('VIC', 'spring', '2028-09-23', '2028-10-08'),
  school('VIC', 'summer', '2028-12-22', '2028-12-31'),

  school('QLD', 'summer', '2026-12-12', '2027-01-26'),
  school('QLD', 'autumn', '2027-03-26', '2027-04-11'),
  school('QLD', 'winter', '2027-06-26', '2027-07-11'),
  school('QLD', 'spring', '2027-09-18', '2027-10-04'),
  school('QLD', 'summer', '2027-12-11', '2028-01-23'),
  school('QLD', 'autumn', '2028-04-01', '2028-04-17'),
  school('QLD', 'winter', '2028-06-24', '2028-07-09'),
  school('QLD', 'spring', '2028-09-16', '2028-10-02'),
  school('QLD', 'summer', '2028-12-09', '2029-01-21'),

  school('WA', 'summer', '2026-12-18', '2027-01-31'),
  school('WA', 'autumn', '2027-04-10', '2027-04-25'),
  school('WA', 'winter', '2027-07-03', '2027-07-18'),
  school('WA', 'spring', '2027-09-25', '2027-10-10'),
  school('WA', 'summer', '2027-12-17', '2028-02-01'),
  school('WA', 'autumn', '2028-04-08', '2028-04-23'),
  school('WA', 'winter', '2028-07-01', '2028-07-16'),
  school('WA', 'spring', '2028-09-23', '2028-10-08'),
  school('WA', 'summer', '2028-12-15', '2028-12-31')
].sort((a, b) => a.start.localeCompare(b.start));

/**
 * Bali's seasons by month. BMKG puts the wet season at roughly November or
 * December to April and the dry season at April or May to October; the months
 * where sources disagree are called `shoulder` rather than picked.
 */
export function seasonOf(month: number): Season {
  if (month >= 5 && month <= 9) return 'dry';
  if (month === 4 || month === 10) return 'shoulder';
  return 'wet';
}

const pad = (n: number) => String(n).padStart(2, '0');

export function monthFlags(year: number, month: number): MonthFlags {
  const first = `${year}-${pad(month)}-01`;
  const last = iso(Date.UTC(year, month, 0));
  const events = BALI_EVENTS.filter((event) => event.start <= last && event.end >= first);

  const notices: string[] = [];
  if (year > ANNOUNCED.idHolidays) {
    notices.push(`${year} holiday dates not yet announced. Check your date with us.`);
  }
  const unpublished = (Object.keys(ANNOUNCED.auSchool) as AuState[]).filter(
    (state) => ANNOUNCED.auSchool[state] < year
  );
  if (unpublished.length) {
    notices.push(`${unpublished.join(', ')} school holidays for ${year} are not published yet.`);
  }

  return { season: seasonOf(month), events, notices };
}
