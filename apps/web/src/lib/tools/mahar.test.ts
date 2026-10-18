import { describe, expect, it } from 'vitest';
import {
  HIJRI_MONTHS_ID,
  computeMahar,
  formatGrams,
  formatMasehi,
  formatRupiah,
  parseIsoDate,
  payableRemainder,
  splitGold,
  terbilang,
  toHijri
} from './mahar';

const amounts = (result: ReturnType<typeof computeMahar>) =>
  Object.fromEntries(result.variants.map((variant) => [variant.id, variant.amount]));

describe('parseIsoDate', () => {
  it('reads a real calendar date', () => {
    expect(parseIsoDate('2026-09-20')).toEqual({ year: 2026, month: 9, day: 20 });
  });

  it('rejects days that do not exist and anything that is not a date', () => {
    expect(parseIsoDate('2026-02-30')).toBeNull();
    expect(parseIsoDate('2026-13-01')).toBeNull();
    expect(parseIsoDate('')).toBeNull();
    expect(parseIsoDate('20-09-2026')).toBeNull();
  });

  it('accepts 29 February only in a leap year', () => {
    expect(parseIsoDate('2028-02-29')).toEqual({ year: 2028, month: 2, day: 29 });
    expect(parseIsoDate('2026-02-29')).toBeNull();
  });
});

describe('formatRupiah', () => {
  it('groups with periods in Indonesian and commas in English, no space after Rp', () => {
    expect(formatRupiah(20092026, 'id')).toBe('Rp20.092.026');
    expect(formatRupiah(20092026, 'en')).toBe('Rp20,092,026');
  });

  it('leaves short amounts ungrouped', () => {
    expect(formatRupiah(926, 'id')).toBe('Rp926');
    expect(formatRupiah(2026000, 'id')).toBe('Rp2.026.000');
  });
});

describe('formatGrams', () => {
  it('uses the locale decimal separator and always two decimals', () => {
    expect(formatGrams(20.09, 'id')).toBe('20,09 gram');
    expect(formatGrams(20.09, 'en')).toBe('20.09 grams');
    expect(formatGrams(5.1, 'id')).toBe('5,10 gram');
  });
});

describe('formatMasehi', () => {
  it('names the weekday and month in the visitor language', () => {
    expect(formatMasehi('2026-09-20', 'id')).toBe('Minggu, 20 September 2026');
    expect(formatMasehi('2026-08-17', 'id')).toBe('Senin, 17 Agustus 2026');
    expect(formatMasehi('2026-09-20', 'en')).toBe('Sunday, 20 September 2026');
  });

  it('renders nothing for an invalid date', () => {
    expect(formatMasehi('2026-02-30', 'id')).toBe('');
  });
});

describe('akad method', () => {
  it('turns 20-09-2026 into the four variants, in chip order', () => {
    const result = computeMahar({ method: 'akad', date: '2026-09-20' }, 'id');
    expect(result.method).toBe('akad');
    expect(result.variants.map((variant) => variant.id)).toEqual([
      'dmy',
      'dmy_unpadded',
      'ymd',
      'dmy_short'
    ]);
    expect(amounts(result)).toEqual({
      dmy: 20092026,
      dmy_unpadded: 2092026,
      ymd: 20260920,
      dmy_short: 200926
    });
  });

  // The format of Atta Halilintar's mahar on 3 April 2021.
  it('drops the leading zeros of day and month for dmy_unpadded', () => {
    const atta = computeMahar({ method: 'akad', date: '2021-04-03' }, 'id');
    const variant = atta.variants.find((item) => item.id === 'dmy_unpadded')!;
    expect(variant.amount).toBe(342021);
    expect(variant.digits).toBe('342021');
    expect(variant.reading).toBe('3 · 4 · 2021');
    expect(amounts(computeMahar({ method: 'akad', date: '2021-02-06' }, 'id')).dmy_unpadded).toBe(
      622021
    );
  });

  it('drops a leading zero from the amount but keeps it in the reading', () => {
    const result = computeMahar({ method: 'akad', date: '2026-09-05' }, 'id');
    const dmy = result.variants.find((variant) => variant.id === 'dmy')!;
    expect(dmy.amount).toBe(5092026);
    expect(dmy.digits).toBe('05092026');
    expect(dmy.reading).toBe('05 · 09 · 2026');
    expect(amounts(result).dmy_short).toBe(50926);
  });

  it('drops a variant that repeats an earlier amount', () => {
    // 20-10 has no leading zero to drop, so the unpadded reading is the same number.
    const result = computeMahar({ method: 'akad', date: '2026-10-20' }, 'id');
    expect(result.variants.map((variant) => variant.id)).toEqual(['dmy', 'ymd', 'dmy_short']);
  });

  it('reads the year first for ymd', () => {
    const result = computeMahar({ method: 'akad', date: '2026-09-20' }, 'id');
    expect(result.variants.find((variant) => variant.id === 'ymd')!.reading).toBe('2026 · 09 · 20');
  });

  it('labels the variants in each locale', () => {
    const id = computeMahar({ method: 'akad', date: '2026-09-20' }, 'id');
    const en = computeMahar({ method: 'akad', date: '2026-09-20' }, 'en');
    expect(id.variants.map((variant) => variant.label)).toEqual([
      'Tanggal · Bulan · Tahun',
      'Tanpa angka nol',
      'Tahun · Bulan · Tanggal',
      'Tanggal · Bulan · Tahun singkat'
    ]);
    expect(en.variants.map((variant) => variant.label)).toEqual([
      'Day · Month · Year',
      'Without leading zeros',
      'Year · Month · Day',
      'Day · Month · Short year'
    ]);
  });

  it('returns no variants for a missing or invalid date', () => {
    expect(computeMahar({ method: 'akad', date: '' }, 'id').variants).toEqual([]);
    expect(computeMahar({ method: 'akad', date: '2026-02-31' }, 'id').variants).toEqual([]);
  });
});

describe('special date method', () => {
  it('uses the same variants for the day a couple started dating', () => {
    const result = computeMahar({ method: 'spesial', kind: 'jadian', date: '2019-02-14' }, 'id');
    expect(result.method).toBe('spesial');
    expect(amounts(result)).toEqual({
      dmy: 14022019,
      dmy_unpadded: 1422019,
      ymd: 20190214,
      dmy_short: 140219
    });
  });

  it('and for the day they first met', () => {
    const result = computeMahar({ method: 'spesial', kind: 'bertemu', date: '2017-07-08' }, 'en');
    expect(amounts(result).dmy).toBe(8072017);
  });

  it('joins two birthdays as DDMM + DDMM', () => {
    const result = computeMahar(
      { method: 'spesial', kind: 'ulang_tahun', date: '1996-05-12', date2: '1997-11-03' },
      'id'
    );
    expect(result.variants).toHaveLength(1);
    const [variant] = result.variants;
    expect(variant.id).toBe('ddmm_ddmm');
    expect(variant.amount).toBe(12050311);
    expect(variant.reading).toBe('12 · 05 · 03 · 11');
  });

  it('keeps the order the birthdays were entered in', () => {
    const result = computeMahar(
      { method: 'spesial', kind: 'ulang_tahun', date: '1997-11-03', date2: '1996-05-12' },
      'id'
    );
    expect(result.variants[0].amount).toBe(3111205);
    expect(result.variants[0].digits).toBe('03111205');
  });

  it('needs both birthdays', () => {
    const result = computeMahar(
      { method: 'spesial', kind: 'ulang_tahun', date: '1996-05-12', date2: '' },
      'id'
    );
    expect(result.variants).toEqual([]);
  });
});

describe('toHijri', () => {
  // Umm al-Qura dates for days the calendar is well known by.
  it('converts known dates with Indonesian month names', () => {
    expect(toHijri('2025-06-26')).toEqual({ day: 1, month: 1, year: 1447, monthName: 'Muharram' });
    // 1 Syawal 1447, Idul Fitri 2026.
    expect(toHijri('2026-03-20')).toEqual({ day: 1, month: 10, year: 1447, monthName: 'Syawal' });
    // 10 Dzulhijjah 1447, Idul Adha 2026.
    expect(toHijri('2026-05-27')).toEqual({
      day: 10,
      month: 12,
      year: 1447,
      monthName: 'Dzulhijjah'
    });
  });

  it('lists the twelve months in order', () => {
    expect(HIJRI_MONTHS_ID).toEqual([
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
    ]);
  });

  it('returns null for an invalid date', () => {
    expect(toHijri('2026-02-30')).toBeNull();
  });
});

describe('hijri method', () => {
  it('applies dmy to the Hijri parts: 8 Rabiul Akhir 1448 is Rp8.041.448', () => {
    const result = computeMahar({ method: 'hijriah', date: '2026-09-19' }, 'id');
    expect(result.method).toBe('hijriah');
    expect(result.variants).toHaveLength(1);
    const [variant] = result.variants;
    expect(variant.id).toBe('dmy');
    expect(variant.amount).toBe(8041448);
    expect(variant.reading).toBe('08 · 04 · 1448');
    expect(result.hijri).toEqual({ day: 8, month: 4, year: 1448, monthName: 'Rabiul Akhir' });
  });

  it('drops the leading zero of a single-digit Hijri day', () => {
    const result = computeMahar({ method: 'hijriah', date: '2026-03-20' }, 'en');
    expect(result.variants[0].amount).toBe(1101447);
  });

  it('returns no variants for an invalid date', () => {
    expect(computeMahar({ method: 'hijriah', date: 'nope' }, 'id').variants).toEqual([]);
  });
});

describe('splitGold', () => {
  it('splits whole grams greedily into standard bar sizes', () => {
    expect(splitGold(20)).toEqual([10, 10]);
    expect(splitGold(31)).toEqual([25, 5, 1]);
    expect(splitGold(9)).toEqual([5, 3, 1]);
    expect(splitGold(4)).toEqual([3, 1]);
    expect(splitGold(150)).toEqual([100, 50]);
  });

  it('returns nothing for zero', () => {
    expect(splitGold(0)).toEqual([]);
  });
});

describe('cash and gold method', () => {
  it('pairs year x 1.000 in cash with DD,MM grams of gold', () => {
    const result = computeMahar({ method: 'emas', date: '2026-09-20' }, 'id');
    expect(result.method).toBe('emas');
    expect(result.variants).toHaveLength(1);
    const [variant] = result.variants;
    expect(variant.id).toBe('cash_gold');
    expect(variant.amount).toBe(2026000);
    expect(variant.gold).toEqual({ grams: 20.09, bars: [10, 10], jewellery: 0.09 });
  });

  it('keeps a single-digit month as hundredths of a gram', () => {
    const [variant] = computeMahar({ method: 'emas', date: '2026-01-05' }, 'id').variants;
    expect(variant.gold).toEqual({ grams: 5.01, bars: [5], jewellery: 0.01 });
  });

  it('reads December as twelve hundredths', () => {
    const [variant] = computeMahar({ method: 'emas', date: '2026-12-31' }, 'en').variants;
    expect(variant.gold).toEqual({ grams: 31.12, bars: [25, 5, 1], jewellery: 0.12 });
  });

  it('returns no variants for an invalid date', () => {
    expect(computeMahar({ method: 'emas', date: '' }, 'id').variants).toEqual([]);
  });
});

describe('terbilang', () => {
  it('spells Indonesian amounts with the se- forms', () => {
    expect(terbilang(1000, 'id')).toBe('seribu rupiah');
    expect(terbilang(1100, 'id')).toBe('seribu seratus rupiah');
    expect(terbilang(11000, 'id')).toBe('sebelas ribu rupiah');
    expect(terbilang(100000, 'id')).toBe('seratus ribu rupiah');
    expect(terbilang(10, 'id')).toBe('sepuluh rupiah');
    expect(terbilang(115, 'id')).toBe('seratus lima belas rupiah');
  });

  it('spells the date amounts the tool produces', () => {
    expect(terbilang(20092026, 'id')).toBe(
      'dua puluh juta sembilan puluh dua ribu dua puluh enam rupiah'
    );
    expect(terbilang(2026000, 'id')).toBe('dua juta dua puluh enam ribu rupiah');
    expect(terbilang(342021, 'id')).toBe('tiga ratus empat puluh dua ribu dua puluh satu rupiah');
    expect(terbilang(20260920, 'id')).toBe(
      'dua puluh juta dua ratus enam puluh ribu sembilan ratus dua puluh rupiah'
    );
  });

  it('says satu juta and satu miliar, not se-, above a thousand', () => {
    expect(terbilang(1000000, 'id')).toBe('satu juta rupiah');
    expect(terbilang(1001000000, 'id')).toBe('satu miliar satu juta rupiah');
  });

  it('handles zero', () => {
    expect(terbilang(0, 'id')).toBe('nol rupiah');
    expect(terbilang(0, 'en')).toBe('zero rupiah');
  });

  it('spells English amounts', () => {
    expect(terbilang(1000, 'en')).toBe('one thousand rupiah');
    expect(terbilang(1100, 'en')).toBe('one thousand one hundred rupiah');
    expect(terbilang(11000, 'en')).toBe('eleven thousand rupiah');
    expect(terbilang(100000, 'en')).toBe('one hundred thousand rupiah');
    expect(terbilang(20092026, 'en')).toBe('twenty million ninety-two thousand twenty-six rupiah');
    expect(terbilang(2026000, 'en')).toBe('two million twenty-six thousand rupiah');
  });
});

describe('payableRemainder', () => {
  it('is the part below the smallest coin in circulation, Rp100', () => {
    expect(payableRemainder(20092026)).toBe(26);
    expect(payableRemainder(342021)).toBe(21);
  });

  it('is zero when the amount can be paid exactly in cash', () => {
    expect(payableRemainder(2026000)).toBe(0);
    expect(payableRemainder(20260900)).toBe(0);
  });
});
