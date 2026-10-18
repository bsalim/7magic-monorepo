/**
 * Mahar from a meaningful date: the arithmetic behind the mahar generator.
 *
 * Pure functions with no DOM, so the page, the card and the tests all read the
 * same numbers. Every amount is whole Rupiah and every input is an ISO
 * "YYYY-MM-DD" string, the shape `DateField` binds.
 *
 * Dates are read off their parts rather than through `new Date(iso)`, which
 * parses as UTC midnight and lands a day early west of Greenwich. Where a Date
 * object is unavoidable (weekday names, the Hijri conversion) it is built at
 * UTC noon and formatted in UTC, so no time zone can move it across midnight.
 */

export type Locale = 'id' | 'en';

export type MaharMethod = 'akad' | 'spesial' | 'hijriah' | 'emas';
export type SpecialKind = 'jadian' | 'bertemu' | 'ulang_tahun';
export type VariantId = 'dmy' | 'dmy_unpadded' | 'ymd' | 'dmy_short' | 'ddmm_ddmm' | 'cash_gold';

export type MaharInput = {
  method: MaharMethod;
  /** Only read by the special-date method. */
  kind?: SpecialKind;
  date: string;
  /** The second birthday, for `kind: 'ulang_tahun'`. */
  date2?: string;
};

export type GoldPart = {
  grams: number;
  /** Whole grams as standard bar sizes, largest first. */
  bars: number[];
  /** The fraction of a gram that no bar comes in, offered as jewellery. */
  jewellery: number;
};

export type MaharVariant = {
  id: VariantId;
  amount: number;
  /** The digit string before it became a number, leading zero included. */
  digits: string;
  /** The digits as the couple would read them aloud: "05 · 09 · 2026". */
  reading: string;
  label: string;
  /** Cash and gold only. */
  gold?: GoldPart;
};

export type HijriDate = { day: number; month: number; year: number; monthName: string };

export type MaharResult = {
  method: MaharMethod;
  variants: MaharVariant[];
  /** The converted date, for the Hijri method's card line. */
  hijri?: HijriDate;
};

type DateParts = { year: number; month: number; day: number };

/**
 * The spellings Kemenag and most Indonesian calendars print, not the
 * transliterations Intl would give ("Rabiʻ II"), which nobody here writes.
 */
export const HIJRI_MONTHS_ID = [
  'Muharram',
  'Safar',
  'Rabiul Awal',
  'Rabiul Akhir',
  'Jumadil Awal',
  'Jumadil Akhir',
  'Rajab',
  "Sya'ban",
  'Ramadhan',
  'Syawal',
  "Dzulqa'dah",
  'Dzulhijjah'
] as const;

/** Bar sizes Indonesian gold dealers stock, largest first, for the greedy split. */
const GOLD_BARS = [100, 50, 25, 10, 5, 3, 2, 1];

const LABELS: Record<Locale, Record<VariantId, string>> = {
  id: {
    dmy: 'Tanggal · Bulan · Tahun',
    dmy_unpadded: 'Tanpa angka nol',
    ymd: 'Tahun · Bulan · Tanggal',
    dmy_short: 'Tanggal · Bulan · Tahun singkat',
    ddmm_ddmm: 'Ulang tahun berdua',
    cash_gold: 'Uang tunai + emas'
  },
  en: {
    dmy: 'Day · Month · Year',
    dmy_unpadded: 'Without leading zeros',
    ymd: 'Year · Month · Day',
    dmy_short: 'Day · Month · Short year',
    ddmm_ddmm: 'Both birthdays',
    cash_gold: 'Cash + gold'
  }
};

const pad = (part: number) => String(part).padStart(2, '0');

/** Null for anything that is not a real calendar day, 30 February included. */
export function parseIsoDate(iso: string | null | undefined): DateParts | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso ?? '');
  if (!match) return null;
  const [year, month, day] = [Number(match[1]), Number(match[2]), Number(match[3])];
  const check = new Date(Date.UTC(year, month - 1, day));
  if (
    check.getUTCFullYear() !== year ||
    check.getUTCMonth() !== month - 1 ||
    check.getUTCDate() !== day
  ) {
    return null;
  }
  return { year, month, day };
}

const utcNoon = ({ year, month, day }: DateParts) => new Date(Date.UTC(year, month - 1, day, 12));

/**
 * Grouped by hand rather than through Intl's currency style, which puts a
 * (non-breaking) space after "Rp" in Indonesian. The mahar is quoted the way it
 * is written on an invitation, "Rp20.092.026", and that space would also make
 * the figure wrap on a narrow card.
 */
export function formatRupiah(amount: number, locale: Locale): string {
  const separator = locale === 'en' ? ',' : '.';
  const grouped = String(Math.trunc(amount)).replace(/\B(?=(\d{3})+(?!\d))/g, separator);
  return `Rp${grouped}`;
}

export function formatGrams(grams: number, locale: Locale): string {
  const fixed = grams.toFixed(2);
  return locale === 'en' ? `${fixed} grams` : `${fixed.replace('.', ',')} gram`;
}

/** "Minggu, 20 September 2026". Empty for an invalid date. */
export function formatMasehi(iso: string, locale: Locale): string {
  const parts = parseIsoDate(iso);
  if (!parts) return '';
  return new Intl.DateTimeFormat(locale === 'en' ? 'en-GB' : 'id-ID', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC'
  })
    .format(utcNoon(parts))
    .replace(/^(\w+) /, '$1, ');
}

/**
 * The date in the Umm al-Qura calendar. Kemenag sets Indonesia's dates by its
 * own sighting, so a day near a month boundary can differ by one -- the page
 * says so. Umm al-Qura is used because it is the one Hijri calendar every
 * browser ships, which keeps the tool free of a lookup table.
 */
export function toHijri(iso: string): HijriDate | null {
  const parts = parseIsoDate(iso);
  if (!parts) return null;
  const formatted = new Intl.DateTimeFormat('en-u-ca-islamic-umalqura', {
    day: 'numeric',
    month: 'numeric',
    year: 'numeric',
    timeZone: 'UTC'
  }).formatToParts(utcNoon(parts));
  const read = (type: string) =>
    Number(formatted.find((part) => part.type === type)?.value.replace(/\D/g, ''));
  const [day, month, year] = [read('day'), read('month'), read('year')];
  if (!day || !month || !year) return null;
  return { day, month, year, monthName: HIJRI_MONTHS_ID[month - 1] };
}

/** Whole grams as standard bars, largest first: 20 is 10 + 10, not one 20 g bar. */
export function splitGold(wholeGrams: number): number[] {
  const bars: number[] = [];
  let left = Math.max(0, Math.trunc(wholeGrams));
  for (const size of GOLD_BARS) {
    while (left >= size) {
      bars.push(size);
      left -= size;
    }
  }
  return bars;
}

/**
 * The smallest coin Bank Indonesia still issues. A mahar ending below it cannot
 * be handed over exactly in cash; penghulu in the field studies cited on the
 * page suggest a transfer instead.
 */
export const SMALLEST_DENOMINATION = 100;

/** The part of an amount that no coin in circulation can pay. */
export function payableRemainder(amount: number): number {
  return Math.trunc(amount) % SMALLEST_DENOMINATION;
}

const ID_DIGITS = [
  '',
  'satu',
  'dua',
  'tiga',
  'empat',
  'lima',
  'enam',
  'tujuh',
  'delapan',
  'sembilan'
];

function idBelowThousand(n: number): string {
  const words: string[] = [];
  const hundreds = Math.floor(n / 100);
  const rest = n % 100;
  if (hundreds === 1) words.push('seratus');
  else if (hundreds > 1) words.push(`${ID_DIGITS[hundreds]} ratus`);
  if (rest === 10) words.push('sepuluh');
  else if (rest === 11) words.push('sebelas');
  else if (rest > 11 && rest < 20) words.push(`${ID_DIGITS[rest - 10]} belas`);
  else if (rest >= 20) {
    words.push(`${ID_DIGITS[Math.floor(rest / 10)]} puluh`);
    if (rest % 10) words.push(ID_DIGITS[rest % 10]);
  } else if (rest > 0) words.push(ID_DIGITS[rest]);
  return words.join(' ');
}

const EN_ONES = [
  '',
  'one',
  'two',
  'three',
  'four',
  'five',
  'six',
  'seven',
  'eight',
  'nine',
  'ten',
  'eleven',
  'twelve',
  'thirteen',
  'fourteen',
  'fifteen',
  'sixteen',
  'seventeen',
  'eighteen',
  'nineteen'
];
const EN_TENS = [
  '',
  '',
  'twenty',
  'thirty',
  'forty',
  'fifty',
  'sixty',
  'seventy',
  'eighty',
  'ninety'
];

function enBelowThousand(n: number): string {
  const words: string[] = [];
  const hundreds = Math.floor(n / 100);
  const rest = n % 100;
  if (hundreds) words.push(`${EN_ONES[hundreds]} hundred`);
  if (rest >= 20)
    words.push(EN_TENS[Math.floor(rest / 10)] + (rest % 10 ? `-${EN_ONES[rest % 10]}` : ''));
  else if (rest > 0) words.push(EN_ONES[rest]);
  return words.join(' ');
}

const SCALES: Record<Locale, string[]> = {
  id: ['', 'ribu', 'juta', 'miliar', 'triliun'],
  en: ['', 'thousand', 'million', 'billion', 'trillion']
};

/**
 * The amount in words, as the groom says it in the kabul: "dua puluh juta
 * sembilan puluh dua ribu dua puluh enam rupiah". Worth getting exactly right,
 * because the field studies on the page record penghulu stumbling over these
 * figures, and a couple practising the wording needs the same words the KUA will
 * read. Indonesian contracts one thousand to "seribu" but keeps "satu juta".
 */
export function terbilang(amount: number, locale: Locale): string {
  let n = Math.max(0, Math.trunc(amount));
  if (n === 0) return locale === 'en' ? 'zero rupiah' : 'nol rupiah';

  const groups: string[] = [];
  for (let scale = 0; n > 0; scale++, n = Math.floor(n / 1000)) {
    const chunk = n % 1000;
    if (!chunk) continue;
    const name = SCALES[locale][scale];
    if (locale === 'id' && scale === 1 && chunk === 1) groups.unshift('seribu');
    else {
      const words = locale === 'en' ? enBelowThousand(chunk) : idBelowThousand(chunk);
      groups.unshift(name ? `${words} ${name}` : words);
    }
  }
  return `${groups.join(' ')} rupiah`;
}

function variant(id: VariantId, groups: string[], locale: Locale): MaharVariant {
  const digits = groups.join('');
  return {
    id,
    amount: Number(digits),
    digits,
    reading: groups.join(' · '),
    label: LABELS[locale][id]
  };
}

/**
 * The readings of one date, in the order the chips show them. A leading zero
 * falls out of the `dmy` number on its own; `dmy_unpadded` drops the month's
 * too, which is how Atta Halilintar's 3-4-2021 became Rp342.021.
 */
function dateVariants({ year, month, day }: DateParts, locale: Locale): MaharVariant[] {
  const [dd, mm, yyyy] = [pad(day), pad(month), String(year)];
  const all = [
    variant('dmy', [dd, mm, yyyy], locale),
    variant('dmy_unpadded', [String(day), String(month), yyyy], locale),
    variant('ymd', [yyyy, mm, dd], locale),
    variant('dmy_short', [dd, mm, yyyy.slice(-2)], locale)
  ];
  // A date like 20-10 has no zero to drop, so two readings land on one number;
  // two chips with the same amount would look like a bug, so the later goes.
  return all.filter(
    (item, index) => all.findIndex((other) => other.amount === item.amount) === index
  );
}

export function computeMahar(input: MaharInput, locale: Locale): MaharResult {
  const { method } = input;
  const empty: MaharResult = { method, variants: [] };
  const date = parseIsoDate(input.date);
  if (!date) return empty;

  switch (method) {
    case 'akad':
      return { method, variants: dateVariants(date, locale) };

    case 'spesial': {
      if (input.kind !== 'ulang_tahun') return { method, variants: dateVariants(date, locale) };
      const second = parseIsoDate(input.date2);
      if (!second) return empty;
      // Birth years are left out: they would make a ten-figure mahar, and DDMM
      // is how a birthday is remembered anyway.
      return {
        method,
        variants: [
          variant(
            'ddmm_ddmm',
            [pad(date.day), pad(date.month), pad(second.day), pad(second.month)],
            locale
          )
        ]
      };
    }

    case 'hijriah': {
      const hijri = toHijri(input.date);
      if (!hijri) return empty;
      return {
        method,
        hijri,
        variants: [variant('dmy', [pad(hijri.day), pad(hijri.month), String(hijri.year)], locale)]
      };
    }

    case 'emas': {
      // DD,MM grams: the month is the two decimal places, so September is ,09
      // and December ,12. Kept in hundredths to dodge float drift in the split.
      const hundredths = date.day * 100 + date.month;
      const bars = splitGold(date.day);
      const cash = variant('cash_gold', [String(date.year), '000'], locale);
      return {
        method,
        variants: [
          {
            ...cash,
            reading: `${date.year} × 1.000 · ${pad(date.day)},${pad(date.month)}`,
            gold: { grams: hundredths / 100, bars, jewellery: date.month / 100 }
          }
        ]
      };
    }
  }
}
