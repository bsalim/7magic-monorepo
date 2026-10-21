/**
 * Copy for the Wedding Tools hub, in both languages. Indonesian is the source
 * of truth, as on every page of the site.
 *
 * A tool without a `path` is announced but not built yet: it renders as "Segera
 * hadir" with no link, so the hub never sends a crawler or a couple to a 404.
 * Give it a path when its page ships, and add that page to `STATIC_PATHS`.
 */

import type { Locale } from '$lib/paraglide/runtime';

export type ToolCard = {
  key: 'mahar' | 'hashtag' | 'bazi' | 'bali-cost' | 'weton' | 'tionghoa' | 'budget';
  title: string;
  copy: string;
  /** Unlocalized route; absent while the tool is still to come. */
  path?: string;
};

export type HubCopy = {
  meta: { title: string; description: string };
  hero: { eyebrow: string; title: string; lead: string };
  open: string;
  tools: ToolCard[];
};

const MAHAR_PATH = '/wedding-tools/mahar-tanggal-pernikahan';
const HASHTAG_PATH = '/wedding-tools/generator-hashtag-pernikahan';
const BAZI_PATH = '/wedding-tools/kalkulator-bazi-pasangan';
// English-only: the hub links it at its /en URL from either edition.
const BALI_COST_PATH = '/wedding-tools/bali-wedding-cost-calculator';

const id: HubCopy = {
  meta: {
    title: 'Wedding Tools: Alat Gratis untuk Persiapan Pernikahan | 7Magic',
    description:
      'Kumpulan alat gratis dari 7Magic untuk calon pengantin: hitung angka mahar dari tanggal pernikahan, buat hashtag pernikahan dari nama kalian, cek kecocokan Ba Zi berdua, dan alat lain untuk merencanakan hari besar kalian.'
  },
  hero: {
    eyebrow: 'Wedding Tools',
    title: 'Alat gratis untuk merencanakan pernikahan',
    lead: 'Hitungan kecil yang sering muncul saat persiapan nikah, dibuat jadi alat yang langsung bisa dipakai. Gratis, tanpa daftar.'
  },
  open: 'Buka alat',
  tools: [
    {
      key: 'mahar',
      title: 'Mahar dari Tanggal Pernikahan',
      copy: 'Ubah tanggal akad, hari jadian, atau tanggal Hijriah menjadi angka mahar, lengkap dengan terbilang untuk lafaz ijab kabul.',
      path: MAHAR_PATH
    },
    {
      key: 'hashtag',
      title: 'Generator Hashtag Pernikahan',
      copy: 'Ide hashtag dari nama kalian berdua: gabungan nama, plesetan, versi tanggal, dan hashtag per acara, siap disalin.',
      path: HASHTAG_PATH
    },
    {
      key: 'bazi',
      title: 'Kalkulator Ba Zi Pasangan',
      copy: 'Empat pilar kalian berdua dari tanggal dan jam lahir, kecocokan menurut tradisi, dan cek apakah tanggal pilihan kalian berbenturan.',
      path: BAZI_PATH
    },
    {
      key: 'bali-cost',
      title: 'Kalkulator Biaya Nikah di Bali (English)',
      copy: 'Perkiraan biaya pernikahan di Bali dalam dolar Australia, untuk pasangan dan tamu dari Australia. Halaman berbahasa Inggris.',
      path: BALI_COST_PATH
    },
    {
      key: 'weton',
      title: 'Weton dan Kecocokan Jodoh',
      copy: 'Hitung weton berdua menurut penanggalan Jawa.'
    },
    {
      key: 'tionghoa',
      title: 'Tanggal Baik Tionghoa',
      copy: 'Cari tanggal pernikahan menurut penanggalan Tionghoa.'
    },
    {
      key: 'budget',
      title: 'Jumlah Tamu dan Anggaran',
      copy: 'Perkirakan jumlah tamu dan susun anggaran pernikahan.'
    }
  ]
};

const en: HubCopy = {
  meta: {
    title: 'Wedding Tools: Free Tools for Planning Your Wedding | 7Magic',
    description:
      'Free tools from 7Magic for couples getting married: turn your wedding date into a mahar amount, make a wedding hashtag from your names, check your Ba Zi compatibility, with more tools for planning your big day to come.'
  },
  hero: {
    eyebrow: 'Wedding Tools',
    title: 'Free tools for planning your wedding',
    lead: 'The small calculations that keep coming up while you plan a wedding, made into tools you can use right away. Free, no sign-up.'
  },
  open: 'Open tool',
  tools: [
    {
      key: 'mahar',
      title: 'Mahar from Your Wedding Date',
      copy: 'Turn your akad date, the day you got together, or the Hijri date into a mahar amount, with the amount in words for the ijab kabul.',
      path: MAHAR_PATH
    },
    {
      key: 'hashtag',
      title: 'Wedding Hashtag Generator',
      copy: 'Hashtag ideas from both your names: name pairs, blends, wordplay, date versions and a tag per event, ready to copy.',
      path: HASHTAG_PATH
    },
    {
      key: 'bazi',
      title: 'Ba Zi Couple Calculator',
      copy: 'Both your four pillars from your birth dates and times, a traditional compatibility reading, and a check on whether your dates clash.',
      path: BAZI_PATH
    },
    {
      key: 'bali-cost',
      title: 'Bali Wedding Cost Calculator',
      copy: 'What a Bali wedding costs in Australian dollars, by guests, setting, style and extras, built from published prices.',
      path: BALI_COST_PATH
    },
    {
      key: 'weton',
      title: 'Weton and Compatibility',
      copy: 'Work out both your weton in the Javanese calendar.'
    },
    {
      key: 'tionghoa',
      title: 'Chinese Auspicious Dates',
      copy: 'Find a wedding date by the Chinese calendar.'
    },
    {
      key: 'budget',
      title: 'Guest Count and Budget',
      copy: 'Estimate your guest list and put together a wedding budget.'
    }
  ]
};

const CONTENT: Record<Locale, HubCopy> = { id, en };

export function hubCopy(locale: Locale): HubCopy {
  return CONTENT[locale] ?? CONTENT.id;
}
