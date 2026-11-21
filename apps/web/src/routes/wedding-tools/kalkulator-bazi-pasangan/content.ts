/**
 * Copy for the Ba Zi compatibility calculator, in both languages.
 *
 * Laid out like the hashtag page's `content.ts`. Indonesian is the source of
 * truth. The short labels (element and animal names, rule names, the tone) come
 * from the API in the requested locale; everything that reads like a sentence
 * is here, where it is edited next to its translation.
 *
 * Every reading is framed as tradition ("menurut tradisi…") and none promises
 * anything: no scores, nothing called lucky, and a standing note that families
 * confirm with an elder or a feng shui master. The example couple is fictional.
 *
 * The readings, date reasons, day-master lines and the two notes are repeated
 * in the API (`app/domains/bazi/emails.py`), which writes the copy of the
 * result the couple is emailed. Edit a sentence here and there together.
 */

import type { Locale } from '$lib/paraglide/runtime';
import type { ChartOut, DateReasonOut, Element, FindingOut, PartnerIn, Verdict, Zone } from '$lib/tools/bazi';

export type Faq = { q: string; a: string };
export type ExplainerSection = { title: string; paragraphs: string[] };
export type Term = { term: string; han: string; text: string };
export type RelatedLink = { href: string; title: string };
export type PillarKey = 'year' | 'month' | 'day' | 'hour';

export type BaziCopy = {
  meta: { title: string; description: string; keywords: string };
  appName: string;
  hero: { eyebrow: string; title: string; lead: string; steps: [string, string, string] };
  form: {
    title: string;
    partnerLegend: [string, string];
    partnerFallback: [string, string];
    nameLabel: string;
    namePlaceholders: [string, string];
    birthDateLabel: string;
    /** The three fields a birth date is typed into, and the day's short placeholder. */
    birthParts: { day: string; dayPlaceholder: string; month: string; year: string };
    datePlaceholder: string;
    birthTimeLabel: string;
    /** The two dropdowns a birth time is picked in. */
    birthTimeParts: { hour: string; minute: string };
    /** Under the time field: blank means unknown, a rough guess is welcome. */
    timeBlank: string;
    timeHint: string;
    zoneLabel: string;
    zones: Record<Zone, string>;
    calculate: string;
    calculating: string;
    missing: string;
    unavailable: string;
    invalid: string;
    stale: string;
    gateHint: string;
  };
  result: {
    eyebrow: string;
    title: string;
    /** The card over the blurred stand-in, before anything is calculated. */
    previewTitle: string;
    previewCopy: string;
    previewCta: string;
    pillars: Record<PillarKey, string>;
    hourUnknown: string;
    dayMaster: string;
    shio: string;
    elements: string;
    elementNames: Record<Element, string>;
    dependsOnTime: string;
    nearTerm: string;
    toneTitle: string;
    findingsTitle: string;
    noFindings: string;
    kinds: Record<FindingOut['kind'], string>;
    scopes: Record<FindingOut['pillar'], string>;
    dayMasters: string[];
    elderNote: string;
    uncertainNote: string;
    copySent: string;
    conventionsTitle: string;
    conventions: string[];
  };
  dates: {
    /** In the form, where the dates are typed. */
    formTitle: string;
    formHint: string;
    formLead: string;
    label: (index: number) => string;
    /** Under the result, where each date gets its verdict. */
    title: string;
    lead: string;
    verdicts: Record<Verdict, string>;
    quiet: string;
    none: string;
    another: string;
  };
  /** The card is not on the page at all: it arrives in the emailed copy. */
  card: {
    title: string;
    lead: string;
    emailed: string;
    sendHint: string;
    send: string;
  };
  /**
   * The gate in front of a first result, and its second use: emailing a result
   * to someone whose browser already had their email, so was not asked.
   */
  gate: {
    title: string;
    description: string;
    submit: string;
    note: string;
    sendTitle: string;
    sendDescription: string;
    sendSubmit: string;
  };
  /** The "what is Ba Zi" block: searchers land here before they trust the tool. */
  intro: { title: string; paragraphs: string[]; termsTitle: string; terms: Term[] };
  explainer: { title: string; lead: string; sections: ExplainerSection[] };
  example: { partners: [PartnerIn, PartnerIn]; dates: string[]; tryIt: string };
  faqs: Faq[];
  related: RelatedLink[];
};

/** A finding as one plain sentence, given the two charts and display names. */
export type ReadingFn = (finding: FindingOut, charts: ChartOut[], names: [string, string]) => string;
/** A date-check reason as one plain sentence. */
export type ReasonFn = (
  reason: DateReasonOut,
  day: { char: string; animal: string },
  charts: ChartOut[],
  names: [string, string]
) => string;

/** Shared by both locales: a fictional couple, so the example needs no source. */
const EXAMPLE_PARTNERS: [PartnerIn, PartnerIn] = [
  { name: 'Raka', birth_date: '1995-05-05', birth_time: '10:00', zone: 'WIB' },
  { name: 'Nadia', birth_date: '1996-04-14', birth_time: '07:30', zone: 'WITA' }
];
const EXAMPLE_DATES = ['2026-09-26', '2026-10-10'];

const ID_READINGS: Record<string, ReadingFn> = {
  'year:six_combination': (f, c, [a, b]) =>
    `Shio ${a} (${c[0].shio.animal_label}) dan ${b} (${c[1].shio.animal_label}) membentuk Kombinasi Enam. Menurut tradisi, keluarga kedua pihak cenderung mudah akrab.`,
  'year:half_harmony': (f, c, [a, b]) =>
    `Shio ${a} dan ${b} berada dalam satu kelompok Tiga Harmoni. Tradisi membacanya sebagai tanda mudah bekerja sama.`,
  'year:clash': (f, c, [a, b]) =>
    `Shio ${a} (${c[0].shio.animal_label}) dan ${b} (${c[1].shio.animal_label}) berbenturan. Banyak keluarga menganggapnya hal untuk dibicarakan bersama, bukan larangan.`,
  'year:harm': (f, c, [a, b]) =>
    `Shio ${a} dan ${b} membentuk pasangan Celaka. Tradisi menyarankan lebih sabar dalam urusan keluarga besar.`,
  'day:six_combination': () =>
    'Cabang hari kalian, yang di Ba Zi disebut istana pasangan, saling berkombinasi. Menurut tradisi ini tanda ikatan yang hangat di rumah tangga.',
  'day:half_harmony': () =>
    'Cabang hari kalian (istana pasangan) berada dalam satu kelompok Tiga Harmoni: tradisi membacanya sebagai saling mendukung.',
  'day:clash': () =>
    'Cabang hari kalian (istana pasangan) berbenturan. Untuk pasangan, inilah yang paling diperhatikan dalam Ba Zi; ahli biasanya melihat seluruh chart sebelum menyimpulkan apa pun.',
  'day:harm': () =>
    'Cabang hari kalian (istana pasangan) membentuk pasangan Celaka. Tradisi membacanya sebagai gesekan kecil sehari-hari yang perlu dikomunikasikan.',
  'day_master:stem_combination': (f) =>
    `Day master kalian (${f.a} dan ${f.b}) saling berpasangan. Dalam Ba Zi ini salah satu tanda jodoh yang klasik.`,
  'day_master:generates': (f, c, names) => {
    const giver = f.source ?? 0;
    const other = 1 - giver;
    return `Unsur ${names[giver]} (${c[giver].day_master.element_label}) menghidupi unsur ${names[other]} (${c[other].day_master.element_label}). Tradisi membacanya sebagai pasangan yang saling menopang.`;
  },
  'day_master:controls': (f, c, names) => {
    const ruler = f.source ?? 0;
    const other = 1 - ruler;
    return `Unsur ${names[ruler]} (${c[ruler].day_master.element_label}) mengendalikan unsur ${names[other]} (${c[other].day_master.element_label}). Bukan hal buruk; tradisi menyarankan pembagian peran yang seimbang.`;
  },
  'day_master:same_element': (f, c) =>
    `Day master kalian berunsur sama (${c[0].day_master.element_label}). Mudah saling memahami, kadang sama-sama keras kepala.`
};

const EN_READINGS: Record<string, ReadingFn> = {
  'year:six_combination': (f, c, [a, b]) =>
    `${a}'s sign (${c[0].shio.animal_label}) and ${b}'s (${c[1].shio.animal_label}) form a Six Combination. By tradition, the two families tend to get on easily.`,
  'year:half_harmony': (f, c, [a, b]) =>
    `${a}'s and ${b}'s signs sit in the same Three Harmony group, which tradition reads as an easy partnership.`,
  'year:clash': (f, c, [a, b]) =>
    `${a}'s sign (${c[0].shio.animal_label}) and ${b}'s (${c[1].shio.animal_label}) clash. Many families treat this as something to talk through together, not a prohibition.`,
  'year:harm': (f, c, [a, b]) =>
    `${a}'s and ${b}'s signs form a Harm pair. Tradition advises extra patience in matters of the wider family.`,
  'day:six_combination': () =>
    'Your day branches, called the spouse palace in Ba Zi, combine. By tradition this is a sign of a warm bond at home.',
  'day:half_harmony': () =>
    'Your day branches (the spouse palace) sit in the same Three Harmony group, which tradition reads as mutual support.',
  'day:clash': () =>
    'Your day branches (the spouse palace) clash. For a couple this is what Ba Zi watches most closely; a practitioner usually reads the whole chart before concluding anything.',
  'day:harm': () =>
    'Your day branches (the spouse palace) form a Harm pair. Tradition reads it as small everyday friction worth talking about.',
  'day_master:stem_combination': (f) =>
    `Your day masters (${f.a} and ${f.b}) pair with each other, one of the classic signs of a match in Ba Zi.`,
  'day_master:generates': (f, c, names) => {
    const giver = f.source ?? 0;
    const other = 1 - giver;
    return `${names[giver]}'s element (${c[giver].day_master.element_label}) feeds ${names[other]}'s (${c[other].day_master.element_label}). Tradition reads this as partners who hold each other up.`;
  },
  'day_master:controls': (f, c, names) => {
    const ruler = f.source ?? 0;
    const other = 1 - ruler;
    return `${names[ruler]}'s element (${c[ruler].day_master.element_label}) controls ${names[other]}'s (${c[other].day_master.element_label}). Not a bad sign; tradition advises sharing roles evenly.`;
  },
  'day_master:same_element': (f, c) =>
    `Your day masters share an element (${c[0].day_master.element_label}): quick to understand each other, and sometimes equally stubborn.`
};

const ID_VERBS: Record<string, string> = {
  clash: 'berbenturan dengan',
  harm: 'membentuk pasangan Celaka dengan',
  six_combination: 'berkombinasi dengan',
  half_harmony: 'selaras (Tiga Harmoni) dengan'
};
const EN_VERBS: Record<string, string> = {
  clash: 'clashes with',
  harm: 'forms a Harm pair with',
  six_combination: 'combines with',
  half_harmony: 'is in Three Harmony with'
};

const idReason: ReasonFn = (r, day, charts, names) => {
  const target =
    r.against === 'shio'
      ? `shio ${charts[r.partner].shio.animal_label} ${names[r.partner]}`
      : `cabang hari (istana pasangan) ${names[r.partner]}`;
  return `Hari ${day.char} ${day.animal} ${ID_VERBS[r.rule] ?? r.rule_label} ${target}.`;
};
const enReason: ReasonFn = (r, day, charts, names) => {
  const target =
    r.against === 'shio'
      ? `${names[r.partner]}'s sign, the ${charts[r.partner].shio.animal_label}`
      : `${names[r.partner]}'s day branch (spouse palace)`;
  return `The ${day.char} ${day.animal} day ${EN_VERBS[r.rule] ?? r.rule_label} ${target}.`;
};

const id: BaziCopy = {
  meta: {
    title: 'Kalkulator Ba Zi Pasangan: Cek Kecocokan dan Tanggal Pernikahan | 7Magic',
    description:
      'Hitung Ba Zi (empat pilar) kalian berdua secara gratis: shio, day master, keseimbangan unsur, kecocokan menurut tradisi, dan cek apakah tanggal pernikahan pilihan kalian berbenturan.',
    keywords:
      'ba zi, bazi, kalkulator bazi, kecocokan shio, shio jodoh, empat pilar, day master, tanggal pernikahan tionghoa, cek kecocokan pasangan'
  },
  appName: 'Kalkulator Ba Zi Pasangan',
  hero: {
    eyebrow: 'Wedding Tools',
    title: 'Kalkulator Ba Zi untuk calon pengantin',
    lead: 'Masukkan tanggal dan jam lahir kalian berdua. Kami hitung empat pilar masing-masing dari posisi matahari, lalu membaca kecocokannya menurut tradisi Ba Zi, termasuk apakah tanggal pernikahan pilihan kalian berbenturan.',
    steps: ['Isi data kelahiran berdua', 'Buka hasil dengan email', 'Baca hasilnya; salinan dan kartu masuk ke email']
  },
  form: {
    title: 'Data kelahiran kalian',
    partnerLegend: ['Calon pengantin pertama', 'Calon pengantin kedua'],
    partnerFallback: ['Pengantin 1', 'Pengantin 2'],
    nameLabel: 'Nama panggilan',
    namePlaceholders: ['Raka', 'Nadia'],
    birthDateLabel: 'Tanggal lahir',
    birthParts: { day: 'Tanggal', dayPlaceholder: 'Tgl', month: 'Bulan', year: 'Tahun' },
    datePlaceholder: 'Pilih tanggal',
    birthTimeLabel: 'Jam lahir',
    birthTimeParts: { hour: 'Jam', minute: 'Menit' },
    timeBlank: 'Kosongkan kalau tidak tahu jam lahir. Ingat kira-kira saja? Isi perkiraannya.',
    timeHint: 'Lahir pukul 23.00 ke atas? Isi jamnya: dalam Ba Zi jam itu sudah masuk hari berikutnya.',
    zoneLabel: 'Zona waktu di akta lahir',
    zones: {
      WIB: 'WIB (Jawa, Sumatra, Kalbar, Kalteng)',
      WITA: 'WITA (Bali, Nusa Tenggara, Sulawesi, Kalsel, Kaltim)',
      WIT: 'WIT (Maluku, Papua)'
    },
    calculate: 'Hitung Ba Zi',
    calculating: 'Menghitung…',
    missing: 'Isi tanggal lahir kalian berdua (tahun 1900 sampai 2100).',
    unavailable:
      'Kalkulator sedang tidak bisa dihubungi. Coba lagi sebentar lagi; isian kalian tetap tersimpan di halaman ini.',
    invalid: 'Ada tanggal yang tidak valid. Periksa lagi tanggal lahir dan tanggal pernikahannya (tahun 1900 sampai 2100).',
    stale: 'Isian berubah. Tekan "Hitung Ba Zi" lagi untuk memperbarui hasil.',
    gateHint:
      'Gratis. Sebelum hasil tampil, kami minta email kalian sekali (nomor WhatsApp opsional); salinan hasil dan kartu Ba Zi kami kirim ke email itu.'
  },
  result: {
    eyebrow: 'Hasil',
    title: 'Ba Zi kalian berdua',
    previewTitle: 'Hasil kalian muncul di sini',
    previewCopy:
      'Empat pilar berdua, kecocokan menurut tradisi, cek tanggal pernikahan, dan kartu Ba Zi yang kami kirim ke email kalian.',
    previewCta: 'Isi data kelahiran',
    pillars: { year: 'Tahun', month: 'Bulan', day: 'Hari', hour: 'Jam' },
    hourUnknown: 'Jam tidak diketahui',
    dayMaster: 'Day master',
    shio: 'Shio',
    elements: 'Keseimbangan lima unsur',
    elementNames: { wood: 'Kayu', fire: 'Api', earth: 'Tanah', metal: 'Logam', water: 'Air' },
    dependsOnTime:
      'Pada tanggal ini matahari masuk titik baru, jadi pilar ini bergantung pada jam lahir. Isi jamnya agar pasti.',
    nearTerm:
      'Lahir dekat pergantian titik matahari: kalau jam di akta dibulatkan, pilar ini bisa berbeda.',
    toneTitle: 'Kecocokan menurut tradisi',
    findingsTitle: 'Yang terbaca dari chart kalian',
    noFindings: 'Tidak ada kombinasi atau benturan yang menonjol di antara shio, istana pasangan, dan day master kalian.',
    kinds: { harmony: 'Selaras', caution: 'Perlu diperhatikan', clash: 'Benturan', neutral: 'Catatan' },
    scopes: { year: 'Shio', day: 'Istana pasangan', day_master: 'Day master' },
    dayMasters: [
      'Seperti pohon besar: lurus, teguh, senang tumbuh dan melindungi.',
      'Seperti tanaman merambat: luwes, ramah, pandai menyesuaikan diri.',
      'Seperti matahari: hangat, terbuka, sumber semangat orang di sekitarnya.',
      'Seperti nyala lilin: lembut, teliti, menerangi orang-orang terdekat.',
      'Seperti gunung: stabil, bisa diandalkan, tidak mudah goyah.',
      'Seperti tanah kebun: merawat, sabar, membuat yang lain tumbuh.',
      'Seperti baja: tegas, adil, berani mengambil keputusan.',
      'Seperti perhiasan: halus, rapi, peka pada detail dan keindahan.',
      'Seperti sungai besar: bebas, cerdas, penuh gagasan.',
      'Seperti embun dan hujan: intuitif, tenang, menyejukkan.'
    ],
    elderNote:
      'Ba Zi adalah tradisi, bukan kepastian. Banyak keluarga tetap mengonfirmasi dengan orang tua atau ahli feng shui sebelum memutuskan, dan keputusan akhirnya tetap di tangan kalian berdua.',
    uncertainNote:
      'Salah satu pilar tahun atau bulan di atas bergantung pada jam lahir, jadi bacaan dan cek tanggal di bawah ini dihitung dari perkiraan. Isi jam lahir yang tepat agar hasilnya sesuai.',
    copySent: 'Salinan hasil dan kartu Ba Zi kami kirim ke email kalian. Belum masuk? Cek folder spam.',
    conventionsTitle: 'Cara kalkulator ini menghitung',
    conventions: [
      'Jam lahir dibaca sesuai jam di akta dan zona waktunya (WIB, WITA, atau WIT), tanpa koreksi waktu matahari lokal.',
      'Pukul 23.00 sudah dihitung sebagai hari berikutnya, sesuai aturan jam Zi yang umum dipakai.',
      'Tahun dan bulan berganti pada titik matahari (Lichun sekitar 4 Februari), dihitung dengan rumus astronomi sampai hitungan menit.',
      'Untuk kelahiran sebelum 1964, zona waktu di Indonesia berbeda dari sekarang, jadi pilar di dekat pergantian jam bisa meleset.'
    ]
  },
  dates: {
    formTitle: 'Tanggal pernikahan yang dipertimbangkan',
    formHint: 'Opsional, sampai tiga tanggal',
    formLead: 'Kami bandingkan pilar hari itu dengan shio dan istana pasangan kalian berdua.',
    label: (index) => `Tanggal ${index + 1}`,
    title: 'Cek tanggal pernikahan',
    lead: 'Pilar hari tiap tanggal, dibandingkan dengan shio dan istana pasangan kalian berdua.',
    verdicts: { safe: 'Aman', consider: 'Perlu dipertimbangkan', clash: 'Bentrok' },
    quiet: 'Tidak berbenturan dengan shio maupun istana pasangan kalian.',
    none: 'Belum ada tanggal yang dicek. Isi tanggal di formulir, lalu hitung lagi.',
    another: 'Cek tanggal lain'
  },
  card: {
    title: 'Kartu Ba Zi pasangan',
    lead: 'Empat pilar kalian berdua dalam satu kartu, siap dibagikan ke keluarga atau dibawa saat konsultasi.',
    emailed: 'Kartu ini kami kirim ke email kalian, bersama salinan hasilnya.',
    sendHint: 'Kartu untuk hasil ini belum dikirim. Minta kami mengirimnya ke email kalian, bersama salinan hasilnya.',
    send: 'Kirim hasil & kartu ke email'
  },
  gate: {
    title: 'Hasil Ba Zi kalian sudah siap',
    description:
      'Isi email untuk membukanya; nomor WhatsApp boleh dikosongkan. Salinan hasil dan kartu Ba Zi kami kirim ke email kalian. Kami tidak menyimpan tanggal lahir kalian.',
    submit: 'Buka hasil & kirim ke email',
    note: 'Cukup sekali di perangkat ini. Wedding Tools lainnya ikut terbuka.',
    sendTitle: 'Kirim hasil & kartu ke email',
    sendDescription:
      'Periksa email kalian; nomor WhatsApp boleh dikosongkan. Kartu Ba Zi dan salinan hasil ini kami kirim ke email itu. Kami tidak menyimpan tanggal lahir kalian.',
    sendSubmit: 'Kirim ke email'
  },
  intro: {
    title: 'Apa itu Ba Zi?',
    paragraphs: [
      'Ba Zi (八字) berarti "delapan karakter". Ini cara astrologi Tionghoa membaca saat kelahiran seseorang sebagai empat pilar: tahun, bulan, hari, dan jam. Karena itu Ba Zi juga dikenal sebagai Empat Pilar (四柱, Si Zhu). Tiap pilar berisi satu batang langit dan satu cabang bumi, dan kedelapan karakter itulah yang menjadi peta kelahiran seseorang.',
      'Ba Zi berkembang sejak zaman Dinasti Tang dan Song di Tiongkok, dan sampai sekarang masih dipegang banyak keluarga Tionghoa, termasuk di Indonesia. Dua kegunaannya paling dekat dengan pernikahan: mencocokkan calon pasangan (合婚, he hun) dan memilih tanggal pernikahan yang tidak berbenturan dengan kelahiran kedua mempelai.',
      'Shio yang sudah akrab di telinga hanyalah satu dari delapan karakter itu. Ba Zi melihat lebih jauh: unsur apa yang dominan, siapa day master masing-masing, dan bagaimana cabang hari, yang disebut istana pasangan, saling bertemu. Kalkulator di atas menghitung semuanya untuk kalian berdua, gratis.'
    ],
    termsTitle: 'Istilah yang akan kalian temui',
    terms: [
      {
        term: 'Batang langit',
        han: '天干',
        text: 'Sepuluh tanda, yaitu lima unsur dalam versi Yang dan Yin, misalnya 甲 Kayu Yang. Ada satu di setiap pilar.'
      },
      {
        term: 'Cabang bumi',
        han: '地支',
        text: 'Dua belas tanda yang dikenal lewat dua belas shio, dari Tikus sampai Babi. Cabang pilar tahun adalah shio kalian.'
      },
      {
        term: 'Lima unsur',
        han: '五行',
        text: 'Kayu, Api, Tanah, Logam, dan Air. Unsur saling menumbuhkan dan saling mengendalikan, dan keseimbangannya dibaca di tiap chart.'
      },
      {
        term: 'Day master',
        han: '日主',
        text: 'Batang langit pada pilar hari. Dalam Ba Zi, inilah yang paling mewakili diri seseorang dan sifatnya.'
      }
    ]
  },
  explainer: {
    title: 'Cara kalkulator ini membaca Ba Zi',
    lead: 'Kenapa tahunnya tidak ikut Imlek, apa saja yang dibandingkan, dan sejauh mana hasilnya bisa dipegang.',
    sections: [
      {
        title: 'Kenapa tahunnya mulai sekitar 4 Februari',
        paragraphs: [
          'Ba Zi memakai kalender matahari, bukan kalender Imlek. Tahun berganti saat Lichun (立春, awal musim semi), sekitar 4 Februari, dan bulan berganti di dua belas titik matahari.',
          'Karena itu, yang lahir sebelum Lichun ikut shio tahun sebelumnya, apa pun tanggal Imleknya tahun itu. Kalkulator ini menghitung posisi matahari dengan rumus astronomi, jadi kelahiran di dekat pergantian pun terbaca dengan benar.'
        ]
      },
      {
        title: 'Cara kecocokan dibaca',
        paragraphs: [
          'Kami membandingkan tiga hal yang paling diperhatikan tradisi: shio kalian (sisi keluarga), cabang hari atau istana pasangan (sisi rumah tangga), dan day master (sifat masing-masing).',
          'Hasilnya berupa daftar kombinasi, keselarasan, dan benturan klasik, ditambah satu kesimpulan umum. Sengaja tanpa angka atau persentase: tradisi Ba Zi tidak pernah membaca jodoh sebagai skor.'
        ]
      },
      {
        title: 'Batas kalkulator ini',
        paragraphs: [
          'Kalkulator ini tidak membaca pilar keberuntungan (da yun), tahun-tahun mendatang, atau batang tersembunyi. Ahli Ba Zi melihat semua itu sebelum memberi nasihat.',
          'Anggap hasilnya sebagai bahan obrolan dengan keluarga. Untuk keputusan besar seperti tanggal pernikahan, banyak keluarga Tionghoa tetap berkonsultasi dengan orang tua atau ahli feng shui.'
        ]
      }
    ]
  },
  example: { partners: EXAMPLE_PARTNERS, dates: EXAMPLE_DATES, tryIt: 'Coba contoh: Raka & Nadia' },
  faqs: [
    {
      q: 'Apa bedanya Ba Zi dengan shio?',
      a: 'Shio hanya satu dari delapan karakter Ba Zi, yaitu cabang pada pilar tahun. Ba Zi juga membaca bulan, hari, dan jam lahir, sehingga dua orang dengan shio yang sama bisa punya chart yang sangat berbeda.'
    },
    {
      q: 'Kalau tidak tahu jam lahir, apakah tetap bisa?',
      a: 'Bisa. Tanpa jam lahir, chart berisi tiga pilar (tahun, bulan, hari) dan pilar jam ditandai tidak diketahui. Kalau pada tanggal itu matahari masuk titik baru, kami beri tanda bahwa pilar bulan atau tahun bergantung pada jam lahir.'
    },
    {
      q: 'Kenapa shio saya di sini berbeda dari yang saya tahu?',
      a: 'Biasanya karena lahir di bulan Januari atau awal Februari. Ba Zi mengganti tahun saat Lichun (sekitar 4 Februari), bukan saat Imlek, jadi yang lahir sebelum Lichun ikut shio tahun sebelumnya.'
    },
    {
      q: 'Kalau shio atau istana pasangan kami berbenturan, apakah tidak boleh menikah?',
      a: 'Tidak. Dalam tradisi, benturan dibaca sebagai hal yang perlu diperhatikan dan dibicarakan, bukan larangan. Ahli Ba Zi melihat seluruh chart, dan banyak pasangan dengan benturan hidup rukun. Keputusan tetap di tangan kalian dan keluarga.'
    },
    {
      q: 'Bagaimana cara memilih tanggal pernikahan dengan alat ini?',
      a: 'Masukkan tanggal yang sedang kalian pertimbangkan. Kami cek apakah pilar hari itu berbenturan dengan shio atau istana pasangan kalian berdua. Pemilihan tanggal secara lengkap dalam almanak Tionghoa menimbang lebih banyak hal; untuk itu kami sedang menyiapkan alat Tanggal Baik Tionghoa.'
    },
    {
      q: 'Zona waktu mana yang harus saya pilih?',
      a: 'Zona yang dipakai jam di tempat lahir saat itu, seperti tertulis di akta. Perhatikan bahwa Bali dan sebagian Kalimantan berganti zona pada 1988, jadi untuk kelahiran sebelum 1988 pilih zona yang berlaku waktu itu.'
    },
    {
      q: 'Apakah tanggal lahir kami disimpan?',
      a: 'Tidak. Perhitungan dilakukan lalu dilupakan. Saat kalian membuka hasil, tim kami menerima email dan nama panggilan yang kalian isi, nomor WhatsApp bila kalian mengisinya, ditambah shio, day master, kesimpulan, dan tanggal yang dicek, tanpa tanggal maupun jam lahir. Salinan dan kartu yang kami kirim ke email kalian berisi chart dan bacaannya, juga tanpa tanggal lahir. Email itu juga diingat di browser kalian, supaya kami tidak menanyakannya lagi.'
    }
  ],
  related: [
    {
      href: '/artikel/tradisi-wedding/mengenal-ba-zi-empat-pilar-kelahiran',
      title: 'Mengenal Ba Zi: Cara Astrologi Tionghoa Membaca Empat Pilar Kelahiran'
    },
    {
      href: '/artikel/tradisi-wedding/kecocokan-pasangan-menurut-ba-zi',
      title: 'Kecocokan Pasangan Menurut Ba Zi: Shio, Istana Pasangan, dan Day Master'
    },
    {
      href: '/artikel/tradisi-wedding/menentukan-tanggal-pernikahan-weton-shio',
      title: 'Menentukan Tanggal Pernikahan: Weton Jawa, Shio, dan Pertimbangan Praktis'
    }
  ]
};

const en: BaziCopy = {
  meta: {
    title: 'Ba Zi Couple Calculator: Check Compatibility and Wedding Dates | 7Magic',
    description:
      'Work out both your Ba Zi (Four Pillars) for free: Chinese zodiac sign, day master, element balance, a traditional compatibility reading, and whether the wedding dates you have in mind clash.',
    keywords:
      'ba zi, bazi, bazi calculator, four pillars, chinese zodiac compatibility, day master, chinese wedding date, couple compatibility'
  },
  appName: 'Ba Zi Couple Calculator',
  hero: {
    eyebrow: 'Wedding Tools',
    title: 'A Ba Zi calculator for couples',
    lead: "Enter both your birth dates and times. We work out each person's four pillars from the Sun's position, then read your compatibility the way Ba Zi tradition does, including whether the wedding dates you have in mind clash.",
    steps: ['Enter both birth details', 'Open your result with your email', 'Read it; a copy and the card land in your inbox']
  },
  form: {
    title: 'Your birth details',
    partnerLegend: ['First partner', 'Second partner'],
    partnerFallback: ['Partner 1', 'Partner 2'],
    nameLabel: 'Nickname',
    namePlaceholders: ['Raka', 'Nadia'],
    birthDateLabel: 'Date of birth',
    birthParts: { day: 'Day', dayPlaceholder: 'Day', month: 'Month', year: 'Year' },
    datePlaceholder: 'Pick a date',
    birthTimeLabel: 'Time of birth',
    birthTimeParts: { hour: 'Hour', minute: 'Minute' },
    timeBlank: "Leave it blank if you don't know the time. Only roughly sure? Enter your best guess.",
    timeHint: 'Born at 23:00 or later? Enter the time: in Ba Zi that hour already belongs to the next day.',
    zoneLabel: 'Time zone on the birth certificate',
    zones: {
      WIB: 'WIB (Java, Sumatra, West & Central Kalimantan)',
      WITA: 'WITA (Bali, Nusa Tenggara, Sulawesi, South & East Kalimantan)',
      WIT: 'WIT (Maluku, Papua)'
    },
    calculate: 'Work out Ba Zi',
    calculating: 'Working it out…',
    missing: 'Enter both your birth dates (years 1900 to 2100).',
    unavailable: "The calculator can't be reached right now. Try again in a moment; what you typed stays on this page.",
    invalid: "One of the dates isn't valid. Check the birth dates and wedding dates again (years 1900 to 2100).",
    stale: 'Your inputs changed. Press "Work out Ba Zi" again to update the result.',
    gateHint:
      'Free. Before the result appears we ask for your email once (a WhatsApp number is optional), and send a copy of the result and your Ba Zi card to that email.'
  },
  result: {
    eyebrow: 'Result',
    title: 'Your Ba Zi',
    previewTitle: 'Your result appears here',
    previewCopy:
      'Both four-pillar charts, compatibility by tradition, the wedding date check, and a Ba Zi card sent to your email.',
    previewCta: 'Enter birth details',
    pillars: { year: 'Year', month: 'Month', day: 'Day', hour: 'Hour' },
    hourUnknown: 'Hour unknown',
    dayMaster: 'Day master',
    shio: 'Zodiac sign',
    elements: 'Five-element balance',
    elementNames: { wood: 'Wood', fire: 'Fire', earth: 'Earth', metal: 'Metal', water: 'Water' },
    dependsOnTime:
      'The Sun enters a new term on this date, so this pillar depends on the time of birth. Add the time to be sure.',
    nearTerm: 'Born close to a solar-term change: if the certificate rounds the time, this pillar could differ.',
    toneTitle: 'Compatibility by tradition',
    findingsTitle: 'What your charts show',
    noFindings: 'No notable combination or clash between your signs, spouse palaces and day masters.',
    kinds: { harmony: 'In harmony', caution: 'Worth noting', clash: 'Clash', neutral: 'Note' },
    scopes: { year: 'Zodiac sign', day: 'Spouse palace', day_master: 'Day master' },
    dayMasters: [
      'Like a tall tree: upright, steady, keen to grow and to shelter others.',
      'Like a climbing vine: flexible, friendly, good at adapting.',
      'Like the sun: warm, open, a source of energy for everyone around.',
      'Like a candle flame: gentle, careful, lighting up the people closest.',
      'Like a mountain: stable, dependable, hard to shake.',
      'Like garden soil: nurturing, patient, helping others grow.',
      'Like steel: decisive, fair, unafraid to make the call.',
      'Like fine jewellery: refined, neat, alert to detail and beauty.',
      'Like a great river: free, clever, full of ideas.',
      'Like dew and rain: intuitive, calm, soothing.'
    ],
    elderNote:
      'Ba Zi is a tradition, not a certainty. Many families still check with their elders or a feng shui master before deciding, and the final decision is yours to make together.',
    uncertainNote:
      'One of the year or month pillars above depends on the time of birth, so the reading and the date check below are based on an estimate. Add the exact time of birth for a result that matches.',
    copySent: "We've sent a copy of this result and your Ba Zi card to your email. Not there yet? Check your spam folder.",
    conventionsTitle: 'How this calculator works',
    conventions: [
      'The birth time is read as the clock time on the certificate in its zone (WIB, WITA or WIT), with no local solar-time correction.',
      '23:00 counts as the next day, following the common rule for the Zi hour.',
      'Years and months change at the solar terms (Lichun is around 4 February), worked out with astronomical formulas to the minute.',
      "For births before 1964, Indonesia's time zones differed from today's, so a pillar near an hour boundary may be off."
    ]
  },
  dates: {
    formTitle: "Wedding dates you're considering",
    formHint: 'Optional, up to three dates',
    formLead: "We compare that day's pillar with both your signs and spouse palaces.",
    label: (index) => `Date ${index + 1}`,
    title: 'Check wedding dates',
    lead: "Each date's day pillar, compared with both your signs and spouse palaces.",
    verdicts: { safe: 'Clear', consider: 'Worth weighing', clash: 'Clash' },
    quiet: "It doesn't clash with either of your signs or spouse palaces.",
    none: 'No dates checked yet. Add dates in the form, then work it out again.',
    another: 'Check other dates'
  },
  card: {
    title: 'Couple Ba Zi card',
    lead: 'Both your four pillars on one card, ready to share with family or bring to a consultation.',
    emailed: 'We email you this card, along with a copy of the result.',
    sendHint: "The card for this result hasn't been sent yet. Ask us to email it to you, along with a copy of the result.",
    send: 'Email me the result & card'
  },
  gate: {
    title: 'Your Ba Zi result is ready',
    description:
      "Enter your email to open it; a WhatsApp number is optional. We'll email you a copy of the result and your Ba Zi card. We don't store your birth dates.",
    submit: 'Open result & email it',
    note: 'Only once on this device. Our other Wedding Tools unlock too.',
    sendTitle: 'Email the result & card',
    sendDescription:
      "Check your email; a WhatsApp number is optional. We'll send your Ba Zi card and a copy of this result to that email. We don't store your birth dates.",
    sendSubmit: 'Send to my email'
  },
  intro: {
    title: 'What is Ba Zi?',
    paragraphs: [
      'Ba Zi (八字) means "eight characters". It is the Chinese astrological way of reading a moment of birth as four pillars: year, month, day and hour, which is why it is also called the Four Pillars (四柱, Si Zhu). Each pillar holds one heavenly stem and one earthly branch, and those eight characters are the map of a person\'s birth.',
      'Ba Zi took shape during the Tang and Song dynasties in China and is still followed by many Chinese families today, Chinese Indonesian families among them. Two of its uses sit closest to a wedding: matching a couple (合婚, he hun) and choosing a wedding date that does not clash with either partner\'s birth.',
      'The zodiac sign everyone knows is only one of those eight characters. Ba Zi looks further: which element dominates, what each person\'s day master is, and how the day branches, known as the spouse palaces, meet. The calculator above works all of it out for the two of you, free.'
    ],
    termsTitle: "Terms you'll come across",
    terms: [
      {
        term: 'Heavenly stems',
        han: '天干',
        text: 'Ten signs: the five elements in a Yang and a Yin form, such as 甲 Yang Wood. Each pillar has one.'
      },
      {
        term: 'Earthly branches',
        han: '地支',
        text: 'Twelve signs, known through the twelve zodiac animals from Rat to Pig. The branch of the year pillar is your sign.'
      },
      {
        term: 'Five elements',
        han: '五行',
        text: 'Wood, Fire, Earth, Metal and Water. They feed and restrain each other, and each chart is read for its balance of them.'
      },
      {
        term: 'Day master',
        han: '日主',
        text: 'The heavenly stem of the day pillar. Ba Zi treats it as the closest picture of the person and their nature.'
      }
    ]
  },
  explainer: {
    title: 'How this calculator reads Ba Zi',
    lead: "Why the year doesn't follow Chinese New Year, what gets compared, and how far the result can be taken.",
    sections: [
      {
        title: 'Why the year starts around 4 February',
        paragraphs: [
          'Ba Zi follows the solar calendar, not the lunar one. The year turns at Lichun (立春, the start of spring), around 4 February, and the months turn at twelve solar terms.',
          "So anyone born before Lichun takes the previous year's sign, whenever Chinese New Year fell that year. This calculator works out the Sun's position with astronomical formulas, so births close to a change are read correctly too."
        ]
      },
      {
        title: 'How compatibility is read',
        paragraphs: [
          'We compare the three things tradition watches most: your signs (the family side), your day branches or spouse palaces (the home side) and your day masters (each of you).',
          'The result is a list of classic combinations, harmonies and clashes, plus one overall line. There is deliberately no number or percentage: Ba Zi tradition has never read a match as a score.'
        ]
      },
      {
        title: "This calculator's limits",
        paragraphs: [
          "It doesn't read luck pillars (da yun), the years ahead or hidden stems. A Ba Zi practitioner looks at all of those before giving advice.",
          'Treat the result as something to talk over with your family. For big decisions like the wedding date, many Chinese Indonesian families still consult their elders or a feng shui master.'
        ]
      }
    ]
  },
  example: { partners: EXAMPLE_PARTNERS, dates: EXAMPLE_DATES, tryIt: 'Try the example: Raka & Nadia' },
  faqs: [
    {
      q: 'How is Ba Zi different from my zodiac sign?',
      a: 'Your sign is only one of the eight characters in Ba Zi, the branch of the year pillar. Ba Zi also reads the month, day and hour of birth, so two people with the same sign can have very different charts.'
    },
    {
      q: "Can I use it if I don't know my time of birth?",
      a: "Yes. Without a time the chart has three pillars (year, month, day) and the hour is marked unknown. If the Sun entered a new term on that date, we flag that the month or year pillar depends on the time of birth."
    },
    {
      q: 'Why is my sign here different from the one I know?',
      a: "Usually because you were born in January or early February. Ba Zi changes the year at Lichun (around 4 February), not at Chinese New Year, so anyone born before Lichun takes the previous year's sign."
    },
    {
      q: 'If our signs or spouse palaces clash, does that mean we should not marry?',
      a: 'No. By tradition a clash is something to be aware of and talk through, not a prohibition. A practitioner reads the whole chart, and plenty of couples with a clash live happily together. The decision stays with you and your families.'
    },
    {
      q: 'How do I choose a wedding date with this tool?',
      a: "Enter the dates you're considering. We check whether that day's pillar clashes with either of your signs or spouse palaces. Full date selection in the Chinese almanac weighs more than this; we're preparing a separate Chinese auspicious-date tool for that."
    },
    {
      q: 'Which time zone should I pick?',
      a: 'The zone the clocks used where and when you were born, as on the birth certificate. Bali and parts of Kalimantan changed zones in 1988, so for births before 1988 pick the zone in force then.'
    },
    {
      q: 'Do you store our birth dates?',
      a: "No. The calculation is done and forgotten. When you open your result, our team receives the email and names you enter, your WhatsApp number if you give one, plus your signs, day masters, the overall reading and the dates you checked, but not your dates or times of birth. The copy and card we email you hold your charts and the reading, and no birth dates either. That email is also remembered in your browser, so we don't ask for it again."
    }
  ],
  related: [
    {
      href: '/en/articles/wedding-traditions/introduction-to-ba-zi-four-pillars',
      title: 'An Introduction to Ba Zi: How Chinese Astrology Reads the Four Pillars of Birth'
    },
    {
      href: '/en/articles/wedding-traditions/couple-compatibility-in-ba-zi',
      title: 'Couple Compatibility in Ba Zi: Zodiac Signs, the Spouse Palace and the Day Master'
    },
    {
      href: '/en/articles/wedding-traditions/choosing-a-wedding-date',
      title: 'Choosing a Wedding Date: Javanese Weton, Chinese Zodiac, and Practical Factors'
    }
  ]
};

const CONTENT: Record<Locale, BaziCopy> = { id, en };
const READINGS: Record<Locale, Record<string, ReadingFn>> = { id: ID_READINGS, en: EN_READINGS };
const REASONS: Record<Locale, ReasonFn> = { id: idReason, en: enReason };

export function baziCopy(locale: Locale): BaziCopy {
  return CONTENT[locale] ?? CONTENT.id;
}

/** One plain sentence for a finding, or its rule label if a pairing has no copy. */
export function reading(locale: Locale, finding: FindingOut, charts: ChartOut[], names: [string, string]): string {
  const fn = (READINGS[locale] ?? READINGS.id)[`${finding.pillar}:${finding.rule}`];
  return fn ? fn(finding, charts, names) : finding.rule_label;
}

export function dateReason(
  locale: Locale,
  reason: DateReasonOut,
  day: { char: string; animal: string },
  charts: ChartOut[],
  names: [string, string]
): string {
  return (REASONS[locale] ?? REASONS.id)(reason, day, charts, names);
}

export const TOOL_PATH = '/wedding-tools/kalkulator-bazi-pasangan';
