/**
 * Copy for Tanggal Baik Tionghoa, the Chinese almanac month, in both languages.
 *
 * Laid out like the Ba Zi page's `content.ts`. Indonesian is the source of
 * truth. The short labels (animal and officer names, rule names) come from the
 * API in the requested locale; everything that reads like a sentence is here,
 * where it is edited next to its translation.
 *
 * The tool rates a day on two things only, and the copy must not claim more:
 * the day officer, where only the officers almanacs agree on get a verdict, and
 * whether the day opposes either partner's shio. Nothing is called lucky, and
 * every result carries the note that families confirm with an elder or a master.
 */

import type { Locale } from '$lib/paraglide/runtime';
import type { Animal, OfficerOut, OfficerRating, Rating, ShioReasonOut } from '$lib/tools/almanac';

export type Faq = { q: string; a: string };
export type ExplainerSection = { title: string; paragraphs: string[] };
export type Term = { term: string; han: string; text: string };
export type RelatedLink = { href: string; title: string };

export const TOOL_PATH = '/wedding-tools/tanggal-baik-tionghoa';
export const BAZI_PATH = '/wedding-tools/kalkulator-bazi-pasangan';

/** One plain sentence for how a day sits with one partner's shio. */
export type ReasonFn = (reason: ShioReasonOut, dayAnimal: string, shio: string) => string;

export type AlmanacCopy = {
  meta: { title: string; description: string; keywords: string };
  appName: string;
  /** The shio names for the pickers; the same ones the API answers with. */
  animals: Record<Animal, string>;
  hero: { eyebrow: string; title: string; lead: string; steps: string[] };
  form: {
    title: string;
    monthLabel: string;
    yearLabel: string;
    shioLabels: [string, string];
    shioPlaceholder: string;
    shioHint: string;
    submit: string;
    loading: string;
    missing: string;
    unavailable: string;
    stale: string;
    gateHint: string;
  };
  result: {
    eyebrow: string;
    /** The band's heading before any month is on show. */
    title: string;
    previewTitle: string;
    previewCopy: string;
    previewCta: string;
    summary: (good: number, avoid: number) => string;
    ratings: Record<Rating, string>;
    legendTitle: string;
    previous: string;
    next: string;
    /** Screen-reader name of a calendar cell: the date, then its rating. */
    cellLabel: (date: string, rating: string) => string;
    dayPillar: string;
    officer: string;
    clash: string;
    officerNotes: Record<OfficerRating, (officer: OfficerOut) => string>;
    clashNote: (animal: string) => string;
    partners: [string, string];
    shioTitle: string;
    shioQuiet: string;
    goodTitle: string;
    goodLead: string;
    goodNone: string;
    elderNote: string;
    baziLead: string;
    baziCta: string;
  };
  gate: { title: string; description: string; submit: string; note: string };
  intro: { title: string; paragraphs: string[]; termsTitle: string; terms: Term[] };
  explainer: { title: string; lead: string; sections: ExplainerSection[]; conventionsTitle: string; conventions: string[] };
  faqs: Faq[];
  related: RelatedLink[];
};

const idReason: ReasonFn = (reason, dayAnimal, shio) => {
  switch (reason.rule) {
    case 'clash':
      return `Hari ${dayAnimal} ciong (berbenturan) dengan shio ${shio}.`;
    case 'harm':
      return `Hari ${dayAnimal} berhubungan Celaka (Hai) dengan shio ${shio}; tradisi menyarankan berhati-hati.`;
    case 'six_combination':
      return `Hari ${dayAnimal} berkombinasi (Liu He) dengan shio ${shio}.`;
    case 'half_harmony':
      return `Hari ${dayAnimal} selaras (Tiga Harmoni) dengan shio ${shio}.`;
    default:
      return reason.rule_label;
  }
};

const enReason: ReasonFn = (reason, dayAnimal, shio) => {
  switch (reason.rule) {
    case 'clash':
      return `A ${dayAnimal} day clashes with the ${shio}.`;
    case 'harm':
      return `A ${dayAnimal} day is in a Harm (Hai) relation with the ${shio}; tradition advises care.`;
    case 'six_combination':
      return `A ${dayAnimal} day combines (Liu He) with the ${shio}.`;
    case 'half_harmony':
      return `A ${dayAnimal} day is in harmony (Three Harmony) with the ${shio}.`;
    default:
      return reason.rule_label;
  }
};

const officerName = (officer: OfficerOut) => `${officer.pinyin} (${officer.label})`;

const id: AlmanacCopy = {
  meta: {
    title: 'Tanggal Baik Tionghoa untuk Pernikahan: Kalender Bulanan Gratis | 7Magic',
    description:
      'Cari tanggal baik pernikahan menurut penanggalan Tionghoa: pilih bulan dan shio kalian berdua, lalu lihat hari mana yang umum dipilih, mana yang dihindari, dan mana yang ciong dengan shio kalian.',
    keywords:
      'tanggal baik tionghoa, hari baik menikah, tanggal baik pernikahan, kalender tionghoa, tong shu, ciong shio, hari baik menurut shio, jian chu'
  },
  appName: 'Tanggal Baik Tionghoa',
  animals: {
    rat: 'Tikus',
    ox: 'Kerbau',
    tiger: 'Macan',
    rabbit: 'Kelinci',
    dragon: 'Naga',
    snake: 'Ular',
    horse: 'Kuda',
    goat: 'Kambing',
    monkey: 'Monyet',
    rooster: 'Ayam',
    dog: 'Anjing',
    pig: 'Babi'
  },
  hero: {
    eyebrow: 'Wedding Tools',
    title: 'Cari tanggal baik menurut penanggalan Tionghoa',
    lead: 'Pilih bulan yang kalian incar dan shio kalian berdua. Kami baca setiap harinya seperti almanak Tionghoa (Tong Shu): petugas hari yang berjaga, dan apakah hari itu ciong dengan shio salah satu dari kalian.',
    steps: ['Pilih bulan dan shio berdua', 'Buka kalender dengan email', 'Lihat hari yang baik dan yang dihindari']
  },
  form: {
    title: 'Bulan dan shio kalian',
    monthLabel: 'Bulan',
    yearLabel: 'Tahun',
    shioLabels: ['Shio calon pengantin pertama', 'Shio calon pengantin kedua'],
    shioPlaceholder: 'Pilih shio',
    shioHint:
      'Lahir di bulan Januari atau Februari sebelum Imlek? Shio kalian mengikuti tahun sebelumnya. Belum yakin, cek di Kalkulator Ba Zi.',
    submit: 'Cari tanggal baik',
    loading: 'Membaca almanak...',
    missing: 'Pilih shio kalian berdua dulu.',
    unavailable: 'Almanak sedang tidak bisa dihubungi. Coba lagi sebentar lagi; pilihan kalian tetap tersimpan di halaman ini.',
    stale: 'Pilihan berubah. Tekan "Cari tanggal baik" lagi untuk memperbarui kalender.',
    gateHint: 'Gratis. Sebelum kalender tampil, kami minta email kalian sekali (nomor WhatsApp opsional).'
  },
  result: {
    eyebrow: 'Kalender',
    title: 'Tanggal baik kalian',
    previewTitle: 'Kalender kalian muncul di sini',
    previewCopy:
      'Satu bulan penuh, tiap hari ditandai: umum dipilih, biasa, atau dihindari, lengkap dengan alasannya untuk shio kalian berdua.',
    previewCta: 'Pilih bulan dan shio',
    summary: (good, avoid) =>
      good
        ? `${good} hari umum dipilih untuk pernikahan, ${avoid} hari dihindari.`
        : `Tidak ada hari yang menonjol bulan ini; ${avoid} hari dihindari.`,
    ratings: { good: 'Umum dipilih', ordinary: 'Biasa', avoid: 'Dihindari' },
    legendTitle: 'Keterangan',
    previous: 'Bulan sebelumnya',
    next: 'Bulan berikutnya',
    cellLabel: (date, rating) => `${date}: ${rating}`,
    dayPillar: 'Pilar hari',
    officer: 'Petugas hari',
    clash: 'Ciong',
    officerNotes: {
      favoured: (officer) =>
        `Hari ${officerName(officer)}: salah satu dari tiga hari yang paling umum dipilih almanak untuk pernikahan.`,
      ordinary: (officer) =>
        `Hari ${officerName(officer)}: hari biasa. Almanak berbeda pendapat tentang hari ini untuk pernikahan, jadi kami tidak memberinya nilai.`,
      avoided: (officer) =>
        `Hari ${officerName(officer)}: hari yang umum dihindari almanak untuk acara besar seperti pernikahan.`
    },
    clashNote: (animal) => `Hari ini ciong shio ${animal}: menurut tradisi dihindari oleh siapa pun yang bershio ${animal}.`,
    partners: ['Calon pengantin pertama', 'Calon pengantin kedua'],
    shioTitle: 'Untuk shio kalian',
    shioQuiet: 'Tidak ada benturan maupun kombinasi dengan shio kalian berdua.',
    goodTitle: 'Tanggal baik bulan ini',
    goodLead: 'Hari yang petugasnya umum dipilih untuk pernikahan dan tidak berbenturan dengan shio kalian. Ketuk untuk melihat alasannya.',
    goodNone:
      'Bulan ini tidak ada hari yang lolos keduanya. Coba bulan sebelum atau sesudahnya; hari "Biasa" pun tetap bisa dipertimbangkan bersama keluarga.',
    elderNote:
      'Almanak adalah tradisi, bukan kepastian. Kalender ini hanya menimbang petugas hari dan shio kalian; banyak keluarga tetap mengonfirmasi dengan orang tua atau ahli feng shui sebelum memutuskan, dan keputusan akhirnya tetap di tangan kalian berdua.',
    baziLead: 'Sudah punya calon tanggal? Cek terhadap chart lengkap kalian berdua, termasuk istana pasangan.',
    baziCta: 'Buka Kalkulator Ba Zi'
  },
  gate: {
    title: 'Kalender kalian sudah siap',
    description:
      'Isi email untuk membukanya; nomor WhatsApp boleh dikosongkan. Kami hanya menerima bulan dan shio yang kalian pilih, bukan tanggal lahir.',
    submit: 'Buka kalender',
    note: 'Cukup sekali di perangkat ini. Wedding Tools lainnya ikut terbuka.'
  },
  intro: {
    title: 'Bagaimana almanak Tionghoa menilai sebuah hari?',
    paragraphs: [
      'Keluarga Tionghoa memilih hari pernikahan dengan membuka Tong Shu, almanak yang terbit tiap tahun. Di samping setiap tanggal tercetak banyak hal, tetapi dua di antaranya selalu ada dan dihitung dengan cara yang sama di almanak mana pun: petugas hari yang sedang berjaga, dan shio yang ciong dengan hari itu.',
      'Alat ini membaca dua hal itu untuk satu bulan penuh, lalu menandai hari yang umum dipilih, hari biasa, dan hari yang dihindari. Anggap ini saringan pertama sebelum kalian membawa beberapa calon tanggal ke keluarga.'
    ],
    termsTitle: 'Istilah yang dipakai',
    terms: [
      {
        term: 'Petugas hari (Jian Chu)',
        han: '建除',
        text: 'Dua belas nama yang bergiliran satu hari sekali: Jian, Chu, Man, Ping, Ding, Zhi, Po, Wei, Cheng, Shou, Kai, Bi. Urutannya ditentukan oleh cabang bulan dan cabang hari.'
      },
      {
        term: 'Ciong',
        han: '冲',
        text: 'Setiap hari berhadapan dengan satu shio di seberangnya dalam lingkaran dua belas cabang. Hari Kuda ciong shio Tikus, hari Ular ciong shio Babi, dan seterusnya.'
      },
      {
        term: 'Bulan matahari',
        han: '节',
        text: 'Bulan dalam almanak tidak berganti di tanggal 1, tetapi di titik matahari (jie) sekitar tanggal 4 sampai 8. Karena itu urutan petugas hari bisa mengulang satu hari di tengah bulan.'
      },
      {
        term: 'Pilar hari',
        han: '日柱',
        text: 'Pasangan batang langit dan cabang bumi milik satu hari, bagian dari putaran enam puluh hari yang sama dengan yang dipakai Ba Zi.'
      }
    ]
  },
  explainer: {
    title: 'Cara kami membaca kalender ini',
    lead: 'Hanya aturan yang disepakati almanak pada umumnya. Di tempat almanak berbeda pendapat, kami tidak memberi nilai.',
    sections: [
      {
        title: 'Tiga hari yang umum dipilih',
        paragraphs: [
          'Ding (Mantap), Cheng (Berhasil), dan Kai (Buka) adalah tiga petugas hari yang paling konsisten disebut baik untuk pernikahan. Hari-hari ini kami tandai "Umum dipilih", selama tidak berbenturan dengan shio kalian.'
        ]
      },
      {
        title: 'Dua hari yang dihindari',
        paragraphs: [
          'Po (Pecah) adalah hari yang cabangnya berbenturan dengan cabang bulan, dan Bi (Tutup) adalah hari penutup putaran. Keduanya hampir selalu dihindari untuk acara besar, jadi kami tandai "Dihindari".'
        ]
      },
      {
        title: 'Tujuh hari sisanya',
        paragraphs: [
          'Untuk Jian, Chu, Man, Ping, Zhi, Wei, dan Shou, almanak yang satu dan yang lain tidak sepakat soal pernikahan. Kami tandai "Biasa" dan tidak memberinya nilai, daripada mengambil satu pendapat dan menyebutnya kepastian.'
        ]
      },
      {
        title: 'Shio kalian berdua',
        paragraphs: [
          'Hari yang ciong dengan shio salah satu dari kalian kami tandai "Dihindari", apa pun petugasnya. Hubungan Celaka (Hai) menurunkan hari yang umum dipilih menjadi "Biasa". Kombinasi dan Tiga Harmoni dengan shio kalian kami sebutkan sebagai catatan baik, tanpa mengubah nilainya.'
        ]
      }
    ],
    conventionsTitle: 'Yang tidak ditimbang alat ini',
    conventions: [
      'Bintang-bintang harian, tanggal lunar, dan pantangan lain yang juga tercetak di Tong Shu.',
      'Chart lengkap kalian berdua. Untuk itu, pakai Kalkulator Ba Zi dan cek calon tanggalnya di sana.',
      'Shio orang tua atau anggota keluarga lain, yang oleh sebagian keluarga ikut dipertimbangkan.',
      'Pergantian bulan matahari dihitung menurut waktu Tiongkok (UTC+8), seperti almanak cetak.'
    ]
  },
  faqs: [
    {
      q: 'Bagaimana cara menentukan tanggal baik menurut penanggalan Tionghoa?',
      a: 'Almanak Tionghoa (Tong Shu) menilai setiap hari dari banyak sisi. Dua yang paling dasar adalah petugas hari (Jian Chu) dan shio yang ciong dengan hari itu. Alat ini membaca keduanya untuk satu bulan: hari Ding, Cheng, dan Kai umum dipilih untuk pernikahan; hari Po dan Bi dihindari; dan hari yang ciong dengan shio kalian juga dihindari.'
    },
    {
      q: 'Apa arti hari yang ciong dengan shio?',
      a: 'Setiap hari punya cabang bumi, yang berpasangan dengan satu hewan shio. Hari itu berhadapan (ciong) dengan shio di seberangnya dalam lingkaran dua belas: Tikus dengan Kuda, Kerbau dengan Kambing, Macan dengan Monyet, Kelinci dengan Ayam, Naga dengan Anjing, Ular dengan Babi. Menurut tradisi, orang yang shionya sedang diciong sebaiknya tidak memilih hari itu untuk acara pentingnya.'
    },
    {
      q: 'Kenapa banyak hari hanya ditandai "Biasa"?',
      a: 'Karena untuk tujuh dari dua belas petugas hari, almanak berbeda pendapat soal pernikahan. Kami hanya memberi nilai pada yang disepakati luas: tiga hari yang umum dipilih dan dua hari yang dihindari. Hari "Biasa" bukan hari buruk; hari itu tetap bisa dipertimbangkan bersama keluarga atau ahli.'
    },
    {
      q: 'Apakah hasil ini sama dengan kalender Tionghoa cetak?',
      a: 'Pilar hari, petugas hari, dan shio yang ciong dihitung dengan cara yang sama dengan almanak cetak, termasuk pergantian bulan di titik matahari menurut waktu Tiongkok. Almanak cetak memuat lebih banyak hal, seperti bintang harian dan tanggal lunar, yang tidak ditimbang di sini.'
    },
    {
      q: 'Shio saya dihitung dari tahun berapa?',
      a: 'Shio mengikuti tahun Imlek, bukan tahun Masehi. Kalau kalian lahir di bulan Januari atau Februari sebelum Imlek, shio kalian adalah shio tahun sebelumnya. Kalkulator Ba Zi kami menghitungnya dari tanggal lahir lengkap.'
    },
    {
      q: 'Apakah data kami disimpan?',
      a: 'Alat ini tidak meminta tanggal lahir. Saat kalian membuka kalender, tim kami menerima email yang kalian isi, nomor WhatsApp bila kalian mengisinya, bulan yang dipilih, shio kalian berdua, dan tanggal baik yang muncul. Email itu juga diingat di browser kalian, supaya kami tidak menanyakannya lagi.'
    }
  ],
  related: [
    {
      href: '/artikel/tradisi-wedding/menentukan-tanggal-pernikahan-weton-shio',
      title: 'Menentukan Tanggal Pernikahan: Weton Jawa, Shio, dan Pertimbangan Praktis'
    },
    {
      href: '/artikel/tradisi-wedding/kecocokan-pasangan-menurut-ba-zi',
      title: 'Kecocokan Pasangan Menurut Ba Zi: Shio, Istana Pasangan, dan Day Master'
    },
    {
      href: '/artikel/tradisi-wedding/mengenal-ba-zi-empat-pilar-kelahiran',
      title: 'Mengenal Ba Zi: Cara Astrologi Tionghoa Membaca Empat Pilar Kelahiran'
    }
  ]
};

const en: AlmanacCopy = {
  meta: {
    title: 'Auspicious Chinese Wedding Dates: A Free Monthly Calendar | 7Magic',
    description:
      'Find a wedding date by the Chinese almanac: pick a month and both your zodiac signs, and see which days are commonly chosen, which are avoided, and which clash with your signs.',
    keywords:
      'auspicious wedding dates, chinese wedding date, chinese almanac, tong shu, zodiac clash, twelve day officers, jian chu, good wedding days'
  },
  appName: 'Auspicious Chinese Dates',
  animals: {
    rat: 'Rat',
    ox: 'Ox',
    tiger: 'Tiger',
    rabbit: 'Rabbit',
    dragon: 'Dragon',
    snake: 'Snake',
    horse: 'Horse',
    goat: 'Goat',
    monkey: 'Monkey',
    rooster: 'Rooster',
    dog: 'Dog',
    pig: 'Pig'
  },
  hero: {
    eyebrow: 'Wedding Tools',
    title: 'Find a good date by the Chinese almanac',
    lead: 'Pick the month you have in mind and both your zodiac signs. We read each day the way the Chinese almanac (Tong Shu) does: the day officer on duty, and whether the day clashes with either of your signs.',
    steps: ['Pick a month and both signs', 'Open the calendar with your email', 'See the days to choose and to avoid']
  },
  form: {
    title: 'Your month and signs',
    monthLabel: 'Month',
    yearLabel: 'Year',
    shioLabels: ["First partner's zodiac sign", "Second partner's zodiac sign"],
    shioPlaceholder: 'Choose a sign',
    shioHint:
      'Born in January or February before Chinese New Year? Your sign follows the year before. Not sure, check with the Ba Zi Calculator.',
    submit: 'Find good dates',
    loading: 'Reading the almanac...',
    missing: 'Choose both your zodiac signs first.',
    unavailable: "The almanac can't be reached right now. Try again in a moment; your choices stay on this page.",
    stale: 'Your choices changed. Press "Find good dates" again to update the calendar.',
    gateHint: 'Free. Before the calendar appears we ask for your email once (a WhatsApp number is optional).'
  },
  result: {
    eyebrow: 'Calendar',
    title: 'Your good dates',
    previewTitle: 'Your calendar appears here',
    previewCopy:
      'A full month with every day marked: commonly chosen, ordinary or avoided, with the reasons for both your signs.',
    previewCta: 'Pick a month and signs',
    summary: (good, avoid) =>
      good
        ? `${good} ${good === 1 ? 'day is' : 'days are'} commonly chosen for weddings, ${avoid} avoided.`
        : `No day stands out this month; ${avoid} avoided.`,
    ratings: { good: 'Commonly chosen', ordinary: 'Ordinary', avoid: 'Avoided' },
    legendTitle: 'Key',
    previous: 'Previous month',
    next: 'Next month',
    cellLabel: (date, rating) => `${date}: ${rating}`,
    dayPillar: 'Day pillar',
    officer: 'Day officer',
    clash: 'Clashes',
    officerNotes: {
      favoured: (officer) =>
        `A ${officerName(officer)} day: one of the three days almanacs most often choose for a wedding.`,
      ordinary: (officer) =>
        `A ${officerName(officer)} day: an ordinary day. Almanacs differ on it for weddings, so we give it no verdict.`,
      avoided: (officer) =>
        `A ${officerName(officer)} day: one almanacs commonly avoid for a big occasion such as a wedding.`
    },
    clashNote: (animal) => `This day clashes with the ${animal}: by tradition anyone born under the ${animal} avoids it.`,
    partners: ['First partner', 'Second partner'],
    shioTitle: 'For your signs',
    shioQuiet: 'No clash or combination with either of your signs.',
    goodTitle: 'Good dates this month',
    goodLead: "Days whose officer is commonly chosen for weddings and that don't clash with your signs. Tap one to see why.",
    goodNone:
      'No day passes both tests this month. Try the month before or after; an "Ordinary" day can still be weighed with your family.',
    elderNote:
      'The almanac is a tradition, not a certainty. This calendar weighs only the day officer and your signs; many families still check with their elders or a feng shui master before deciding, and the final decision is yours to make together.',
    baziLead: 'Have a date in mind? Check it against both your full charts, spouse palace included.',
    baziCta: 'Open the Ba Zi Calculator'
  },
  gate: {
    title: 'Your calendar is ready',
    description:
      'Enter your email to open it; a WhatsApp number is optional. We only receive the month and signs you chose, not your birth dates.',
    submit: 'Open calendar',
    note: 'Only once on this device. Our other Wedding Tools unlock too.'
  },
  intro: {
    title: 'How does the Chinese almanac judge a day?',
    paragraphs: [
      'Chinese families choose a wedding day by opening the Tong Shu, the almanac published each year. A great deal is printed beside every date, but two things are always there and are worked out the same way in any almanac: the day officer on duty, and the zodiac sign the day clashes with.',
      'This tool reads those two things for a whole month, then marks the days commonly chosen, the ordinary ones and the ones avoided. Treat it as a first pass before you take a few candidate dates to your family.'
    ],
    termsTitle: 'Terms used here',
    terms: [
      {
        term: 'Day officer (Jian Chu)',
        han: '建除',
        text: 'Twelve names that take turns, one a day: Jian, Chu, Man, Ping, Ding, Zhi, Po, Wei, Cheng, Shou, Kai, Bi. The order follows the month branch and the day branch.'
      },
      {
        term: 'Clash (Chong)',
        han: '冲',
        text: 'Each day faces the sign opposite it in the circle of twelve branches. A Horse day clashes with the Rat, a Snake day with the Pig, and so on.'
      },
      {
        term: 'Solar month',
        han: '节',
        text: 'An almanac month does not turn on the 1st but at a solar term (jie), around the 4th to the 8th. That is why the run of day officers can repeat a day mid-month.'
      },
      {
        term: 'Day pillar',
        han: '日柱',
        text: 'The pair of heavenly stem and earthly branch that belongs to one day, part of the same sixty-day cycle Ba Zi uses.'
      }
    ]
  },
  explainer: {
    title: 'How we read this calendar',
    lead: 'Only the rules almanacs broadly agree on. Where they differ, we give no verdict.',
    sections: [
      {
        title: 'Three days commonly chosen',
        paragraphs: [
          'Ding (Stable), Cheng (Success) and Kai (Open) are the three day officers most consistently named good for a wedding. We mark these "Commonly chosen", as long as they do not clash with your signs.'
        ]
      },
      {
        title: 'Two days avoided',
        paragraphs: [
          'Po (Destruction) is the day whose branch clashes with the month branch, and Bi (Close) is the day that ends the cycle. Both are almost always avoided for a big occasion, so we mark them "Avoided".'
        ]
      },
      {
        title: 'The other seven',
        paragraphs: [
          'For Jian, Chu, Man, Ping, Zhi, Wei and Shou, one almanac and the next do not agree about weddings. We mark them "Ordinary" and give no verdict, rather than take one opinion and call it certain.'
        ]
      },
      {
        title: 'Your two signs',
        paragraphs: [
          'A day that clashes with either of your signs is marked "Avoided", whatever its officer. A Harm (Hai) relation lowers a commonly chosen day to "Ordinary". A Combination or Three Harmony with your signs is noted as a good sign, without changing the mark.'
        ]
      }
    ],
    conventionsTitle: 'What this tool does not weigh',
    conventions: [
      'The daily stars, lunar dates and other taboos that a Tong Shu also prints.',
      'Both your full charts. For that, use the Ba Zi Calculator and check your candidate dates there.',
      "Your parents' or other relatives' signs, which some families also consider.",
      'Solar months turn by China time (UTC+8), as in a printed almanac.'
    ]
  },
  faqs: [
    {
      q: 'How is an auspicious wedding date chosen in the Chinese calendar?',
      a: 'The Chinese almanac (Tong Shu) judges each day from many angles. The two most basic are the day officer (Jian Chu) and the zodiac sign the day clashes with. This tool reads both for a month: Ding, Cheng and Kai days are commonly chosen for weddings; Po and Bi days are avoided; and a day that clashes with either of your signs is avoided too.'
    },
    {
      q: 'What does it mean when a day clashes with a zodiac sign?',
      a: 'Every day has an earthly branch, which pairs with one zodiac animal. The day faces (clashes with) the sign opposite it in the circle of twelve: Rat and Horse, Ox and Goat, Tiger and Monkey, Rabbit and Rooster, Dragon and Dog, Snake and Pig. By tradition, someone whose sign is being clashed does not pick that day for an important occasion.'
    },
    {
      q: 'Why are so many days only marked "Ordinary"?',
      a: 'Because for seven of the twelve day officers, almanacs disagree about weddings. We only give a verdict where there is broad agreement: three days commonly chosen and two avoided. An "Ordinary" day is not a bad day; it can still be weighed with your family or a master.'
    },
    {
      q: 'Does this match a printed Chinese calendar?',
      a: 'The day pillar, the day officer and the clashing sign are worked out the same way as in a printed almanac, including the month turning at the solar term by China time. A printed almanac holds more, such as daily stars and lunar dates, which are not weighed here.'
    },
    {
      q: 'Which year is my zodiac sign counted from?',
      a: 'Your sign follows the Chinese year, not the calendar year. If you were born in January or February before Chinese New Year, your sign is that of the year before. Our Ba Zi Calculator works it out from your full birth date.'
    },
    {
      q: 'Do you store our data?',
      a: 'This tool does not ask for birth dates. When you open the calendar, our team receives the email you enter, your WhatsApp number if you give one, the month you chose, both your signs and the good dates that came up. That email is also remembered in your browser, so we don\'t ask for it again.'
    }
  ],
  related: [
    {
      href: '/en/articles/wedding-traditions/choosing-a-wedding-date',
      title: 'Choosing a Wedding Date: Javanese Weton, Chinese Zodiac, and Practical Factors'
    },
    {
      href: '/en/articles/wedding-traditions/couple-compatibility-in-ba-zi',
      title: 'Couple Compatibility in Ba Zi: Zodiac Signs, the Spouse Palace and the Day Master'
    },
    {
      href: '/en/articles/wedding-traditions/introduction-to-ba-zi-four-pillars',
      title: 'An Introduction to Ba Zi: How Chinese Astrology Reads the Four Pillars of Birth'
    }
  ]
};

const CONTENT: Record<Locale, AlmanacCopy> = { id, en };
const REASONS: Record<Locale, ReasonFn> = { id: idReason, en: enReason };

export function almanacCopy(locale: Locale): AlmanacCopy {
  return CONTENT[locale] ?? CONTENT.id;
}

export function shioReason(locale: Locale, reason: ShioReasonOut, dayAnimal: string, shio: string): string {
  return (REASONS[locale] ?? REASONS.id)(reason, dayAnimal, shio);
}
