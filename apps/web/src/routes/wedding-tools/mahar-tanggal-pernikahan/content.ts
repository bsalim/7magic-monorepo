/**
 * Copy for the mahar generator, in both languages.
 *
 * One locale-keyed module, like `perjanjian-pranikah/content.ts`: the explainer,
 * examples and FAQ are an argument that is edited as a whole, not independent UI
 * strings. The UI chrome every tool shares (the lead gate, "Segera hadir") is in
 * the Paraglide catalogue instead.
 *
 * Indonesian is the source of truth. The English is a translation for the same
 * readers, and the ijab kabul wording stays Indonesian in both, since that is the
 * language it is spoken in at the KUA.
 *
 * Every fact in `explainer`, `examples` and `faqs` comes from the mahar research
 * of 2026-10-18 and has at least two independent sources; the ones the page
 * cites are in `explainer.sources`. To add a fact, add its source there too. No
 * prices, and no gold price: they change daily and the page must not go stale.
 * The amounts in the examples are what the press reported, not computed.
 */

import type { Locale } from '$lib/paraglide/runtime';
import type { MaharMethod, SpecialKind, VariantId } from '$lib/tools/mahar';

export type Faq = { q: string; a: string };
export type Source = { label: string; url: string };
export type ExplainerSection = { title: string; paragraphs: string[] };
export type RelatedLink = { href: string; title: string };

export type Example = {
  couple: string;
  /** ISO, so the weekday and month names are formatted, never typed. */
  date: string;
  mahar: string;
  reading: string;
  /** Our own write-up of the wedding, already localized. */
  href?: string;
  /** Loads this date and variant into the tool, where the tool reproduces it. */
  tryIt?: { date: string; variant: VariantId };
  sources: Source[];
};

export type MaharCopy = {
  meta: { title: string; description: string; keywords: string };
  appName: string;
  hero: { eyebrow: string; title: string; lead: string };
  form: {
    methodLegend: string;
    methods: Record<MaharMethod, { label: string; hint: string }>;
    kindLegend: string;
    kinds: Record<SpecialKind, string>;
    dateLabels: { akad: string; jadian: string; bertemu: string };
    birthdayLabels: [string, string];
    datePlaceholder: string;
    namesLegend: string;
    optional: string;
    groomLabel: string;
    brideLabel: string;
    groomPlaceholder: string;
    bridePlaceholder: string;
    variantLegend: string;
  };
  result: {
    title: string;
    empty: string;
    emptyBirthdays: string;
    readingPrefix: string;
    hijriPrefix: string;
    hijriNote: string;
    cashLabel: string;
    goldLabel: string;
    barsLabel: string;
    jewelleryNote: (grams: string) => string;
    wordsLabel: string;
    lafazLabel: string;
    /** Only shown where the page language is not the one the akad is held in. */
    lafazLanguageNote: string;
    remainderNote: (remainder: string) => string;
  };
  card: {
    title: string;
    lead: string;
    lockedTitle: string;
    lockedCopy: string;
    unlock: string;
    downloadPng: string;
    print: string;
    exporting: string;
    exportError: string;
    unlockedNote: string;
    fallbackTitle: string;
    kicker: string;
    paidCash: string;
    goldPrefix: string;
    emptyAmount: string;
    gateTitle: string;
    gateDescription: string;
  };
  explainer: {
    title: string;
    lead: string;
    sections: ExplainerSection[];
    sourcesTitle: string;
    sources: Source[];
  };
  examples: {
    title: string;
    lead: string;
    sourcesLabel: string;
    readMore: string;
    tryIt: string;
    items: Example[];
  };
  faqs: Faq[];
  related: RelatedLink[];
};

/** Shared by both locales: a source is the same document in either language. */
const SOURCES = {
  hukumonlineMahar: {
    label: 'Hukumonline Klinik, "Mahar Pernikahan dalam Islam" (diperbarui 16 Maret 2023)',
    url: 'https://www.hukumonline.com/klinik/a/mahar-pernikahan-dalam-islam-lt5d0b245a920da/'
  },
  hukumonlineUtang: {
    label: 'Hukumonline Klinik, "Hukum Mahar yang Masih Utang" (3 Juni 2022)',
    url: 'https://www.hukumonline.com/klinik/a/hukum-mahar-yang-masih-utang-cl1176/'
  },
  hukumonlineKembali: {
    label: 'Hukumonline Klinik, "Dapatkah Mahar Diminta Kembali?" (18 Agustus 2014)',
    url: 'https://www.hukumonline.com/klinik/a/dapatkah-mahar-diminta-kembali-lt53e195f4141b9/'
  },
  nuMinimal: {
    label: 'NU Online, "Berapa Batas Minimal Mahar?" (11 Juni 2015)',
    url: 'https://nu.or.id/bahtsul-masail/berapa-batas-minimal-mahar-czn8w'
  },
  tafsirAhkam: {
    label: 'tafsiralquran.id, "Tafsir Ahkam: Hukum dan Ketentuan Jumlah Mahar" (4 Agustus 2021)',
    url: 'https://tafsiralquran.id/tafsir-ahkam-hukum-dan-ketentuan-jumlah-mahar-dalam-pernikahan/'
  },
  skripsiUinsa: {
    label: 'Skripsi UIN Sunan Ampel Surabaya, penelitian di KUA Taman, Sidoarjo (2023)',
    url: 'https://digilib.uinsa.ac.id/62085'
  },
  skripsiKediri: {
    label: 'Skripsi IAIN Kediri, penelitian di KUA Puncu, Kediri (Bab 1)',
    url: 'https://etheses.iainkediri.ac.id/13354/2/931102819%20bab1.pdf'
  },
  hukumonlineBedaAgama: {
    label: 'Hukumonline Klinik, "Mahar Nikah Beda Agama" (21 Juli 2023)',
    url: 'https://www.hukumonline.com/klinik/a/mahar-nikah-beda-agama-lt5e318a99b4622/'
  },
  jawaposPanai: {
    label: 'JawaPos, fatwa MUI Sulawesi Selatan tentang uang panai (Juli 2022)',
    url: 'https://www.jawapos.com/berita-daerah/2207020120/mui-sulsel-terbitkan-fatwa-tentang-uang-panai'
  },
  uinMalangBelis: {
    label: 'Jurnal UIN Maulana Malik Ibrahim Malang tentang belis dan uang panai',
    url: 'https://urj.uin-malang.ac.id/index.php/jfs/article/view/1615'
  },
  uinSukaSinamot: {
    label: 'Skripsi UIN Sunan Kalijaga tentang sinamot',
    url: 'https://digilib.uin-suka.ac.id/id/eprint/34833/'
  }
} satisfies Record<string, Source>;

const EXAMPLE_SOURCES = {
  andre: [
    {
      label: 'detikSumut',
      url: 'https://www.detik.com/sumut/berita/d-8671104/nikahi-amanda-rigby-andre-taulany-beri-mahar-rp-20-092-026'
    },
    {
      label: 'CNN Indonesia',
      url: 'https://www.cnnindonesia.com/hiburan/20260920173152-234-1406098/bernuansa-jawa-andre-taulany-pinang-amanda-rigby-mahar-rp20092026'
    }
  ],
  atta: [
    {
      label: 'Kompas TV',
      url: 'https://www.kompas.tv/article/161031/ini-arti-maskawin-atta-halilintar-uang-rp342-021-ke-aurel-hermansyah'
    },
    {
      label: 'Popbela',
      url: 'https://www.popbela.com/relationship/married/artis-menikah-dengan-mahar-di-bawah-satu-juta-rupiah-awet-00-kc27c-qxx17f'
    }
  ],
  elRumi: [
    {
      label: 'Kompas.com',
      url: 'https://www.kompas.com/hype/read/2026/04/27/145125666/detail-mahar-el-rumi-ke-syifa-hadju-26-gram-logam-mulia-hingga-uang-2026'
    },
    {
      label: 'Medcom',
      url: 'https://www.medcom.id/hiburan/montase/nbw5lXRK-identitas-ayah-kandung-syifa-hadju-terungkap-saat-ijab-kabul-dengan-el-rumi'
    }
  ]
} satisfies Record<string, Source[]>;

const id: MaharCopy = {
  meta: {
    title: 'Mahar dari Tanggal Pernikahan: Hitung Angka Mahar Bermakna | 7Magic',
    description:
      'Ubah tanggal akad, hari jadian, ulang tahun berdua, atau tanggal Hijriah menjadi angka mahar, lengkap dengan terbilang untuk lafaz ijab kabul. Gratis, langsung jadi, plus kartu mahar siap cetak.',
    keywords:
      'mahar tanggal pernikahan, angka mahar, kalkulator mahar, hitung mahar, mahar unik, mahar tanggal nikah, terbilang mahar, mahar emas gram'
  },
  appName: 'Mahar dari Tanggal Pernikahan',
  hero: {
    eyebrow: 'Wedding Tools · Gratis',
    title: 'Mahar dari Tanggal Pernikahan',
    lead: 'Pilih tanggal yang berarti untuk kalian berdua, lalu lihat tanggal itu menjadi angka mahar, lengkap dengan cara menyebutnya saat ijab kabul. Hasilnya langsung tampil, tanpa daftar.'
  },
  form: {
    methodLegend: 'Pilih cara menghitung',
    methods: {
      akad: { label: 'Tanggal akad', hint: 'Dari tanggal ijab kabul' },
      spesial: { label: 'Tanggal spesial', hint: 'Hari jadian, pertama bertemu, atau ulang tahun' },
      hijriah: { label: 'Kalender Hijriah', hint: 'Tanggal akad versi Hijriah' },
      emas: { label: 'Uang + emas', hint: 'Tahun jadi uang, tanggal jadi gram emas' }
    },
    kindLegend: 'Tanggal apa?',
    kinds: { jadian: 'Hari jadian', bertemu: 'Pertama bertemu', ulang_tahun: 'Ulang tahun berdua' },
    dateLabels: {
      akad: 'Tanggal akad',
      jadian: 'Tanggal jadian',
      bertemu: 'Tanggal pertama bertemu'
    },
    birthdayLabels: ['Ulang tahun calon suami', 'Ulang tahun calon istri'],
    datePlaceholder: 'Pilih tanggal',
    namesLegend: 'Nama di kartu',
    optional: 'opsional',
    groomLabel: 'Calon suami',
    brideLabel: 'Calon istri',
    groomPlaceholder: 'Contoh: Raka',
    bridePlaceholder: 'Contoh: Nadia',
    variantLegend: 'Susunan angka'
  },
  result: {
    title: 'Angka mahar',
    empty: 'Pilih tanggal di samping untuk melihat angka maharnya.',
    emptyBirthdays: 'Isi kedua tanggal ulang tahun untuk melihat angka maharnya.',
    readingPrefix: 'Dibaca dari',
    hijriPrefix: 'Tanggal Hijriah',
    hijriNote:
      'Dihitung dengan kalender Umm al-Qura. Tanggal Hijriah versi Kemenag bisa berbeda satu hari, jadi cocokkan dulu dengan kalender resmi.',
    cashLabel: 'Uang tunai',
    goldLabel: 'Emas',
    barsLabel: 'Susunan emas batangan',
    jewelleryNote: (grams) => `Sisa ${grams} bisa dijadikan perhiasan.`,
    wordsLabel: 'Terbilang',
    lafazLabel: 'Latihan lafaz ijab kabul',
    lafazLanguageNote: '',
    remainderNote: (remainder) =>
      `Pecahan terkecil yang beredar saat ini Rp100, jadi sisa ${remainder} tidak bisa dibayar pas dengan uang tunai. Banyak pasangan membayar mahar seperti ini lewat transfer bank.`
  },
  card: {
    title: 'Kartu mahar',
    lead: 'Kartu dengan nama kalian, siap disimpan sebagai gambar atau dicetak ukuran A5.',
    lockedTitle: 'Kartu mahar kalian sudah siap',
    lockedCopy: 'Buka gratis dengan email dan nomor WhatsApp, lalu unduh atau cetak.',
    unlock: 'Buka gratis',
    downloadPng: 'Unduh PNG',
    print: 'Cetak / simpan PDF',
    exporting: 'Menyiapkan...',
    exportError: 'Gambar belum berhasil dibuat. Coba lagi, atau pakai Cetak / simpan PDF.',
    unlockedNote: 'Kartu ikut berubah saat tanggal, nama, atau susunan angka diganti.',
    fallbackTitle: 'Mahar Pernikahan',
    kicker: 'MAHAR PERNIKAHAN',
    paidCash: 'dibayar tunai',
    goldPrefix: 'dan emas',
    emptyAmount: 'Pilih tanggal',
    gateTitle: 'Buka kartu mahar gratis',
    gateDescription:
      'Kirim email dan nomor WhatsApp kalian, lalu kartu mahar langsung bisa diunduh sebagai PNG atau dicetak A5.'
  },
  explainer: {
    title: 'Tentang mahar dan angka tanggal',
    lead: 'Ringkasan singkat dari Kompilasi Hukum Islam (KHI) dan penelitian di KUA, supaya angka yang kalian pilih juga tepat secara aturan.',
    sections: [
      {
        title: 'Cara alat ini menghitung',
        paragraphs: [
          'Tanggal akad disusun menjadi angka: 20-09-2026 menjadi Rp20.092.026. Ada juga susunan tanpa angka nol (Rp2.092.026), tahun di depan (Rp20.260.920), dan tahun dua digit (Rp200.926). Angka nol di depan otomatis hilang dari nominal.',
          'Tanggal spesial memakai susunan yang sama untuk hari jadian atau pertama bertemu. Untuk ulang tahun, tanggal dan bulan kalian berdua digabung: 12-05 dan 03-11 menjadi Rp12.050.311.',
          'Kalender Hijriah mengubah tanggal akad ke kalender Umm al-Qura, lalu menyusunnya dengan cara yang sama. Tanggal versi Kemenag bisa berbeda satu hari.',
          'Uang + emas menjadikan tahun sebagai uang tunai (2026 menjadi Rp2.026.000) dan tanggal serta bulan sebagai gram emas (20-09 menjadi 20,09 gram). Alat ini tidak memakai atau menyarankan harga apa pun. Besaran mahar akhirnya tetap disepakati calon pengantin dan keluarga.'
        ]
      },
      {
        title: 'Apa itu mahar',
        paragraphs: [
          'Menurut KHI, mahar adalah pemberian calon mempelai pria kepada calon mempelai wanita, baik berbentuk barang, uang, atau jasa yang tidak bertentangan dengan hukum Islam (Pasal 1 huruf d). Mahar diberikan langsung kepada calon istri dan sejak itu menjadi hak pribadinya (Pasal 32).'
        ]
      },
      {
        title: 'Wajib, tetapi bukan rukun nikah',
        paragraphs: [
          'Calon mempelai pria wajib membayar mahar, dengan jumlah, bentuk, dan jenis yang disepakati kedua belah pihak (Pasal 30). Penentuannya berdasarkan kesederhanaan dan kemudahan yang dianjurkan ajaran Islam (Pasal 31).',
          'Menyerahkan mahar bukan rukun perkawinan. Lupa menyebut jenis dan jumlah mahar saat akad, atau mahar yang masih terhutang, tidak membatalkan pernikahan (Pasal 34).'
        ]
      },
      {
        title: 'Dibayar tunai atau ditangguhkan',
        paragraphs: [
          'Pada dasarnya mahar diserahkan tunai. Bila calon mempelai wanita setuju, penyerahannya boleh ditangguhkan seluruhnya atau sebagian, dan yang belum diserahkan menjadi utang calon suami (Pasal 33). Itu sebabnya lafaz akad yang lazim di Indonesia berbunyi "dengan maskawin ... dibayar tunai".'
        ]
      },
      {
        title: 'Bolehkah angka seperti Rp20.092.026?',
        paragraphs: [
          'Boleh. KHI tidak menetapkan batas minimal maupun maksimal mahar; yang menentukan adalah kesepakatan. Dalam penelitian skripsi di KUA Taman, Sidoarjo, penghulu menilai mahar angka tanggal boleh dan sah.',
          'Penghulu di sana tetap menyarankan cara bayar yang praktis, misalnya transfer, karena angka terakhirnya sering tidak ada dalam pecahan uang yang beredar. Penelitian di KUA Puncu, Kediri mencatat kesulitan yang sama. Tanyakan juga ke KUA tempat kalian mendaftar.'
        ]
      },
      {
        title: 'Di luar akad nikah Islam',
        paragraphs: [
          'Mahar adalah ketentuan dalam pernikahan Islam. Tradisi adat seperti uang panai (Bugis-Makassar), belis (NTT), dan sinamot (Batak) berbeda dari mahar, meskipun sering disebut dengan nama yang sama. Ide angka dari tanggal tetap bisa dipakai sebagai hadiah simbolis di luar akad nikah Islam.'
        ]
      }
    ],
    sourcesTitle: 'Sumber',
    sources: Object.values(SOURCES)
  },
  examples: {
    title: 'Mahar angka tanggal dari pernikahan artis',
    lead: 'Beberapa pasangan yang memakai tanggal pernikahan sebagai mahar, menurut pemberitaan media.',
    sourcesLabel: 'Sumber',
    readMore: 'Baca kisah pernikahannya',
    tryIt: 'Coba tanggal ini',
    items: [
      {
        couple: 'Andre Taulany & Amanda Rigby',
        date: '2026-09-20',
        mahar: 'Uang tunai Rp20.092.026 dan seperangkat alat salat',
        reading: '20 · 09 · 2026',
        href: '/artikel/pernikahan-selebriti/pernikahan-andre-taulany-amanda-rigby',
        tryIt: { date: '2026-09-20', variant: 'dmy' },
        sources: EXAMPLE_SOURCES.andre
      },
      {
        couple: 'Atta Halilintar & Aurel Hermansyah',
        date: '2021-04-03',
        mahar: 'Uang Rp342.021 dan seperangkat alat salat',
        reading: '3 · 4 · 2021',
        tryIt: { date: '2021-04-03', variant: 'dmy_unpadded' },
        sources: EXAMPLE_SOURCES.atta
      },
      {
        couple: 'El Rumi & Syifa Hadju',
        date: '2026-04-26',
        mahar: 'Logam mulia 26 gram dan 4 gram, ditambah £2.026',
        reading: '26 · 4 · 2026',
        sources: EXAMPLE_SOURCES.elRumi
      }
    ]
  },
  faqs: [
    {
      q: 'Bagaimana alat ini menghitung angka mahar?',
      a: 'Tanggal yang kalian pilih disusun menjadi angka. Tanggal akad 20-09-2026 menjadi Rp20.092.026, atau Rp2.092.026 tanpa angka nol. Ada juga pilihan dari hari jadian, ulang tahun berdua, kalender Hijriah, dan uang + emas dalam gram.'
    },
    {
      q: 'Apakah mahar dengan angka tanggal sah?',
      a: 'KHI tidak menetapkan batas minimal maupun maksimal mahar; jumlahnya disepakati kedua belah pihak. Penghulu yang diwawancarai dalam penelitian di KUA Taman, Sidoarjo menilai mahar angka tanggal boleh dan sah. Tetap tanyakan ke KUA tempat kalian mendaftar.'
    },
    {
      q: 'Kenapa ada catatan soal sisa puluhan rupiah?',
      a: 'Pecahan terkecil yang beredar saat ini Rp100, jadi angka seperti Rp20.092.026 tidak bisa dibayar pas dengan uang tunai. Penghulu dalam penelitian di KUA Taman, Sidoarjo menyarankan transfer bank atau cara lain untuk mahar seperti ini.'
    },
    {
      q: 'Tanggal Hijriahnya beda satu hari dengan kalender saya. Mana yang benar?',
      a: 'Alat ini memakai kalender Umm al-Qura. Kemenag menetapkan tanggal Hijriah di Indonesia dengan caranya sendiri, sehingga hasilnya bisa berbeda satu hari. Untuk akad, pakai tanggal dari kalender resmi Kemenag.'
    },
    {
      q: 'Apakah mahar harus dibayar tunai saat akad?',
      a: 'Menurut KHI Pasal 33, mahar pada dasarnya diserahkan tunai. Bila calon istri setuju, penyerahannya boleh ditangguhkan seluruhnya atau sebagian, dan yang belum diserahkan menjadi utang calon suami.'
    },
    {
      q: 'Apakah alat ini menyebut harga emas?',
      a: 'Tidak. Alat ini hanya menghitung gram dari tanggal dan tidak memakai harga apa pun.'
    },
    {
      q: 'Siapa yang menentukan besaran mahar?',
      a: 'Jumlah, bentuk, dan jenis mahar disepakati kedua belah pihak (KHI Pasal 30). Angka dari alat ini hanya ide yang bermakna; keputusan akhirnya tetap di tangan calon pengantin dan keluarga.'
    },
    {
      q: 'Apakah kartu maharnya gratis?',
      a: 'Gratis. Kami hanya meminta email dan nomor WhatsApp sekali, lalu kartu bisa diunduh sebagai PNG atau dicetak ukuran A5.'
    }
  ],
  related: [
    {
      href: '/artikel/pernikahan-islami/mahar-dalam-islam',
      title: 'Mahar dalam Islam: Ketentuan, Bentuk, dan Kisaran Wajar di 2026'
    },
    {
      href: '/artikel/pernikahan-selebriti/pernikahan-artis-indonesia-2025-2026-tren-yang-bisa-ditiru',
      title: 'Pernikahan Artis Indonesia 2025 sampai 2026: Pola yang Berulang dan Bisa Anda Tiru'
    },
    {
      href: '/artikel/pernikahan-islami/aturan-wali-nikah-dan-urutan-duduk-saat-akad',
      title: 'Wali Nikah dan Urutan Duduk saat Akad: Panduan yang Perlu Anda Pahami'
    }
  ]
};

const en: MaharCopy = {
  meta: {
    title: 'Mahar from Your Wedding Date: A Meaningful Mahar Amount | 7Magic',
    description:
      'Turn your akad date, the day you got together, both your birthdays or the Hijri date into a mahar amount, with the amount in words for the ijab kabul. Free, instant, plus a printable mahar card.',
    keywords:
      'mahar wedding date, mahar amount, mahar calculator, Indonesian mahar, mahar from date, mas kawin, mahar gold grams'
  },
  appName: 'Mahar from Your Wedding Date',
  hero: {
    eyebrow: 'Wedding Tools · Free',
    title: 'Mahar from Your Wedding Date',
    lead: 'Pick a date that means something to you both and watch it become a mahar amount, along with how to say it at the ijab kabul. The result shows instantly, no sign-up.'
  },
  form: {
    methodLegend: 'Choose a method',
    methods: {
      akad: { label: 'Akad date', hint: 'From the date of the ijab kabul' },
      spesial: { label: 'Special date', hint: 'The day you got together, first met, or birthdays' },
      hijriah: { label: 'Hijri calendar', hint: 'Your akad date in the Hijri calendar' },
      emas: { label: 'Cash + gold', hint: 'The year as cash, the day as grams of gold' }
    },
    kindLegend: 'Which date?',
    kinds: { jadian: 'Got together', bertemu: 'First met', ulang_tahun: 'Both birthdays' },
    dateLabels: {
      akad: 'Akad date',
      jadian: 'The day you got together',
      bertemu: 'The day you first met'
    },
    birthdayLabels: ["Groom's birthday", "Bride's birthday"],
    datePlaceholder: 'Pick a date',
    namesLegend: 'Names on the card',
    optional: 'optional',
    groomLabel: 'Groom',
    brideLabel: 'Bride',
    groomPlaceholder: 'e.g. Raka',
    bridePlaceholder: 'e.g. Nadia',
    variantLegend: 'Number format'
  },
  result: {
    title: 'Mahar amount',
    empty: 'Pick a date to see the mahar amount.',
    emptyBirthdays: 'Fill in both birthdays to see the mahar amount.',
    readingPrefix: 'Read from',
    hijriPrefix: 'Hijri date',
    hijriNote:
      "Calculated with the Umm al-Qura calendar. Indonesia's Ministry of Religious Affairs (Kemenag) can differ by a day, so check against the official calendar first.",
    cashLabel: 'Cash',
    goldLabel: 'Gold',
    barsLabel: 'As gold bars',
    jewelleryNote: (grams) => `The remaining ${grams} can be made into jewellery.`,
    wordsLabel: 'In words',
    lafazLabel: 'Ijab kabul practice',
    lafazLanguageNote: 'Said in Indonesian at the akad:',
    remainderNote: (remainder) =>
      `The smallest denomination in circulation today is Rp100, so the remaining ${remainder} cannot be paid exactly in cash. Many couples pay a mahar like this by bank transfer.`
  },
  card: {
    title: 'Mahar card',
    lead: 'A card with your names, ready to save as an image or print at A5.',
    lockedTitle: 'Your mahar card is ready',
    lockedCopy: 'Unlock it for free with your email and WhatsApp number, then download or print.',
    unlock: 'Unlock for free',
    downloadPng: 'Download PNG',
    print: 'Print / save PDF',
    exporting: 'Preparing...',
    exportError: 'The image could not be created. Try again, or use Print / save PDF.',
    unlockedNote: 'The card follows along when you change the date, names or number format.',
    fallbackTitle: 'Wedding Mahar',
    kicker: 'WEDDING MAHAR',
    paidCash: 'paid in cash',
    goldPrefix: 'and gold',
    emptyAmount: 'Pick a date',
    gateTitle: 'Unlock your mahar card for free',
    gateDescription:
      'Send us your email and WhatsApp number, and the mahar card is ready to download as a PNG or print at A5.'
  },
  explainer: {
    title: 'About mahar and date amounts',
    lead: "A short summary of Indonesia's Compilation of Islamic Law (Kompilasi Hukum Islam, KHI) and of research at KUA offices, so the amount you choose also fits the rules.",
    sections: [
      {
        title: 'How the tool calculates',
        paragraphs: [
          'Your akad date becomes a number: 20-09-2026 becomes Rp20,092,026. There is also a version without leading zeros (Rp2,092,026), one with the year first (Rp20,260,920) and one with a two-digit year (Rp200,926). A leading zero drops out of the amount on its own.',
          'Special date uses the same formats for the day you got together or first met. For birthdays, both your days and months are joined: 12-05 and 03-11 become Rp12,050,311.',
          'Hijri calendar converts your akad date to the Umm al-Qura calendar, then arranges it the same way. The date Kemenag sets can differ by one day.',
          'Cash + gold turns the year into cash (2026 becomes Rp2,026,000) and the day and month into grams of gold (20-09 becomes 20.09 grams). The tool uses and suggests no prices of any kind. The final mahar is still agreed by the couple and their families.'
        ]
      },
      {
        title: 'What mahar is',
        paragraphs: [
          'Under the KHI, mahar is a gift from the groom to the bride, in the form of goods, money or a service that does not conflict with Islamic law (Article 1(d)). It is given directly to the bride and from then on is her personal property (Article 32).'
        ]
      },
      {
        title: 'Obligatory, but not a pillar of the marriage',
        paragraphs: [
          'The groom must pay a mahar whose amount, form and type are agreed by both sides (Article 30). It is set on the basis of the simplicity and ease that Islam encourages (Article 31).',
          'Handing over the mahar is not a pillar (rukun) of the marriage. Forgetting to name the type and amount at the akad, or a mahar still owed, does not void the marriage (Article 34).'
        ]
      },
      {
        title: 'Paid in cash, or deferred',
        paragraphs: [
          'By default the mahar is handed over in cash. If the bride agrees, it may be deferred in whole or in part, and whatever has not been handed over becomes a debt owed by the groom (Article 33). That is why the usual akad wording in Indonesia says "dengan maskawin ... dibayar tunai" (with a mahar of ..., paid in cash).'
        ]
      },
      {
        title: 'Is an amount like Rp20,092,026 allowed?',
        paragraphs: [
          'Yes. The KHI sets no minimum and no maximum; what counts is the agreement. In an undergraduate thesis based at KUA Taman in Sidoarjo, the penghulu (marriage officiants) interviewed considered date amounts allowed and valid.',
          'They still recommend a practical way to pay, such as a transfer, because the last digits often do not exist as notes or coins in circulation. Research at KUA Puncu in Kediri records the same difficulty. Ask the KUA where you register as well.'
        ]
      },
      {
        title: 'Outside an Islamic akad',
        paragraphs: [
          'Mahar is a provision of Islamic marriage. Adat traditions such as uang panai (Bugis-Makassar), belis (East Nusa Tenggara) and sinamot (Batak) are different from mahar, even though they are often called by the same name. The idea of an amount from a date still works as a symbolic gift outside an Islamic akad.'
        ]
      }
    ],
    sourcesTitle: 'Sources (in Indonesian)',
    sources: Object.values(SOURCES)
  },
  examples: {
    title: 'Date mahars from celebrity weddings',
    lead: 'A few couples who used their wedding date as the mahar, as reported in the press.',
    sourcesLabel: 'Sources',
    readMore: 'Read about the wedding',
    tryIt: 'Try this date',
    items: [
      {
        couple: 'Andre Taulany & Amanda Rigby',
        date: '2026-09-20',
        mahar: 'Rp20,092,026 in cash and a set of prayer items',
        reading: '20 · 09 · 2026',
        href: '/en/articles/celebrity-weddings/andre-taulany-amanda-rigby-wedding',
        tryIt: { date: '2026-09-20', variant: 'dmy' },
        sources: EXAMPLE_SOURCES.andre
      },
      {
        couple: 'Atta Halilintar & Aurel Hermansyah',
        date: '2021-04-03',
        mahar: 'Rp342,021 and a set of prayer items',
        reading: '3 · 4 · 2021',
        tryIt: { date: '2021-04-03', variant: 'dmy_unpadded' },
        sources: EXAMPLE_SOURCES.atta
      },
      {
        couple: 'El Rumi & Syifa Hadju',
        date: '2026-04-26',
        mahar: '26 grams and 4 grams of gold, plus £2,026',
        reading: '26 · 4 · 2026',
        sources: EXAMPLE_SOURCES.elRumi
      }
    ]
  },
  faqs: [
    {
      q: 'How does the tool calculate the mahar amount?',
      a: 'The date you pick is arranged into a number. An akad date of 20-09-2026 becomes Rp20,092,026, or Rp2,092,026 without leading zeros. You can also start from the day you got together, both your birthdays, the Hijri calendar, or cash plus grams of gold.'
    },
    {
      q: 'Is a date-based mahar valid?',
      a: 'The KHI sets no minimum or maximum mahar; the amount is agreed by both sides. Penghulu interviewed in research at KUA Taman, Sidoarjo considered date amounts allowed and valid. Still check with the KUA where you register.'
    },
    {
      q: 'Why is there a note about a few rupiah left over?',
      a: 'The smallest denomination in circulation today is Rp100, so an amount like Rp20,092,026 cannot be paid exactly in cash. Penghulu in the research at KUA Taman, Sidoarjo suggest a bank transfer or another method for a mahar like this.'
    },
    {
      q: 'The Hijri date is a day off from my calendar. Which is right?',
      a: 'The tool uses the Umm al-Qura calendar. Kemenag sets Hijri dates in Indonesia its own way, so the result can differ by a day. For the akad, use the date in the official Kemenag calendar.'
    },
    {
      q: 'Does the mahar have to be paid in cash at the akad?',
      a: 'Under Article 33 of the KHI, the mahar is handed over in cash by default. If the bride agrees, it may be deferred in whole or in part, and whatever has not been handed over becomes a debt owed by the groom.'
    },
    {
      q: 'Does the tool give a gold price?',
      a: 'No. It only works out grams from the date and uses no prices of any kind.'
    },
    {
      q: 'Who decides the mahar amount?',
      a: 'The amount, form and type of mahar are agreed by both sides (KHI Article 30). The number from this tool is only a meaningful idea; the final decision stays with the couple and their families.'
    },
    {
      q: 'Is the mahar card free?',
      a: 'Yes. We only ask for your email and WhatsApp number once, then the card can be downloaded as a PNG or printed at A5.'
    }
  ],
  related: [
    {
      href: '/en/articles/islamic-wedding/mahar-in-islam',
      title: 'Mahar in Islam: Requirements, Forms, and Reasonable Ranges in 2026'
    },
    {
      href: '/en/articles/celebrity-weddings/indonesian-celebrity-weddings-2025-2026-trends',
      title:
        'Indonesian Celebrity Weddings 2025 to 2026: The Patterns That Keep Coming Back, and What You Can Borrow'
    },
    {
      href: '/en/articles/islamic-wedding/wali-nikah-rules-and-seating-order',
      title: 'Marriage Guardian Rules and Seating Order During the Contract'
    }
  ]
};

const CONTENT: Record<Locale, MaharCopy> = { id, en };

export function maharCopy(locale: Locale): MaharCopy {
  return CONTENT[locale] ?? CONTENT.id;
}

/** The route, unlocalized. `localizeHref` adds /en for the English page. */
export const TOOL_PATH = '/wedding-tools/mahar-tanggal-pernikahan';
