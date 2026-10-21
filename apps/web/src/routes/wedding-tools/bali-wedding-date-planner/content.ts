/**
 * Copy for the Bali wedding date planner. English only, for Australian couples.
 * Every date it states comes from `$lib/tools/bali-dates`, where each one
 * carries its source; the extra sources below back the weather and airport
 * lines, which are not dates in that module.
 */

import type { Source } from '$lib/tools/bali-dates';

export const TOOL_PATH = '/wedding-tools/bali-wedding-date-planner';

export const meta = {
  title: 'Bali Wedding Date Planner 2027–2028: Nyepi, Galungan & School Holidays | 7Magic',
  description:
    'Check a Bali wedding date against Nyepi (8 March 2027, airport closed), Galungan, Indonesian public holidays, Australian school holidays and the wet season. Every date sourced.',
  keywords:
    'best time for a bali wedding, bali wedding dates 2027, nyepi 2027, galungan 2027, bali wet season wedding, bali wedding school holidays'
};

export const appName = 'Bali Wedding Date Planner';

export const hero = {
  eyebrow: 'Wedding Tools · Bali',
  title: 'Pick a Bali wedding date that works',
  lead: 'Check any month or day in 2027 and 2028 against Nyepi, Balinese holy days, Indonesian holidays, Australian school holidays and the season. Every date is sourced.'
};

export const EXTRA_SOURCES: Source[] = [
  {
    title: 'Antara: Ngurah Rai airport closes for 24 hours for Nyepi (2026)',
    url: 'https://bali.antaranews.com/berita/400962/bandara-ngurah-rai-berhenti-operasi-sementara-24-jam-selama-nyepi'
  },
  {
    title: 'BMKG: rainy season outlook 2026/2027',
    url: 'https://www.bmkg.go.id/iklim/prediksi-musim/prediksi-musim-hujan-2026-2027-di-indonesia'
  },
  {
    title: 'BBMKG Region III Denpasar via Antara: Bali wet season timing (September 2026)',
    url: 'https://bali.antaranews.com/berita/414384/bmkg-minta-warga-waspadai-potensi-cuaca-ekstrem-saat-musim-hujan-di-bali'
  }
];

export const bestMonths = [
  {
    title: 'May to September: the dry season',
    body: 'The most reliable weather for an outdoor ceremony, and the busiest months. July also lines up with school holidays in every state, so families can come, but flights from Australia cost the most in July and December.'
  },
  {
    title: 'April and October: between seasons',
    body: 'Often dry and quieter, though sources disagree on exactly when the wet season ends and starts. Have a covered plan B. NSW, Victorian, Queensland and WA school holidays fall in late September or early October in both years.'
  },
  {
    title: 'November to March: the wet season',
    body: 'BMKG expects Bali’s 2026/27 wet season to start in late November or December and run to about April, peaking in February. Afternoon storms are common, prices and crowds are lower, and indoor or covered venues matter.'
  },
  {
    title: 'Dates to avoid',
    body: 'Nyepi (Monday 8 March 2027): the island goes silent for 24 hours and the airport closes. It runs straight into the Lebaran break, so 6–15 March 2027 is the busiest travel stretch of the year in Indonesia. Galungan and Kuningan are Bali’s great holy days; many local staff and vendors are with their families.'
  }
];

export const faqs = [
  {
    q: 'When is Nyepi in 2027?',
    a: 'Monday 8 March 2027, per the Indonesian government’s 2027 holiday decree. For 24 hours from 6am the island stays indoors and Ngurah Rai airport closes, as it did in 2026, so no wedding can happen and guests cannot fly in or out that day.'
  },
  {
    q: 'What is the best month for a Bali wedding?',
    a: 'For weather, May to September, the dry season. April and October are often good and quieter. If your guests have children, July and late September to early October line up with Australian school holidays.'
  },
  {
    q: 'Should we avoid Galungan?',
    a: 'You can marry around it, but plan for it. Galungan and Kuningan, ten days later, are Bali’s biggest holy days: schools and offices usually close the day before to the day after, and many Balinese staff and vendors spend them with family.'
  },
  {
    q: 'Why does Lebaran matter for a wedding in Bali?',
    a: 'Idul Fitri is Indonesia’s biggest holiday. In 2027 it falls right after Nyepi, so 6–15 March is one long national break: domestic flights, hotels and roads are at their fullest.'
  },
  {
    q: 'Are the 2028 dates final?',
    a: 'Not yet. Indonesia publishes the next year’s holidays late in the year before, so 2028 months show a notice until then. Galungan and Kuningan follow a fixed 210-day cycle, so their 2028 dates are calculated and marked as such.'
  },
  {
    q: 'Which school holidays are shown?',
    a: 'New South Wales, Victoria, Queensland and Western Australia, from each state’s education department. South Australia is not shown because we could not confirm its dates from the official source.'
  }
];
