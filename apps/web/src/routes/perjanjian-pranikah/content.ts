/**
 * Copy for the prenuptial agreement landing page, in both languages.
 *
 * Kept in one locale-keyed module rather than split across Paraglide message
 * keys: this page's copy is an argument that changes as a whole -- reorder the
 * FAQ, drop a comparison row, reword the legal cards -- not a set of independent
 * UI strings. A hundred `prenup_*` keys in the shared catalogue would also bury
 * the strings every other page needs. The structure is typed, so a locale that
 * misses a field fails the type check rather than rendering blank.
 *
 * Indonesian is the source of truth. The English is a translation for the same
 * Jakarta service, not a different offer: the price, the legal references and the
 * scope must stay identical in both, and the legal citations are the same
 * documents either way.
 *
 * If the price changes, it changes in `PRICE` below, in both `meta.title`s, both
 * WhatsApp prefills, the four FAQ answers that name a figure, `offerPrice`, and
 * `service_prenup_desc` in messages/{id,en}.json.
 */

import type { Locale } from '$lib/paraglide/runtime';

/**
 * The introductory all-in price: consultation, drafting, the notarial deed and
 * registration. Confirmed by 7Magic. Written per locale because Indonesian
 * groups thousands with periods and English with commas -- the same number.
 */
const PRICE = { id: 'Rp 3.500.000', en: 'Rp 3,500,000' } as const;

/** The figure as it appears mid-sentence, spoken rather than written out. */
const PRICE_SHORT = { id: 'Rp 3,5 juta', en: 'Rp 3.5 million' } as const;

export type ComparisonRow = { label: string; price: string; note: string; ours: boolean };
export type Segment = { title: string; copy: string; alt: string };
export type LawCard = { reference: string; title: string; copy: string };
export type Step = { when: string; title: string; copy: string };
export type Faq = { q: string; a: string };

export type PrenupCopy = {
  price: string;
  priceShort: string;
  meta: { title: string; description: string; keywords: string };
  hero: {
    eyebrow: string;
    title: string;
    lead: string;
    ctaConsult: string;
    ctaWhatsapp: string;
    note: string;
    imageAlt: string;
  };
  stats: { value: string; label: string }[];
  price_section: {
    eyebrow: string;
    title: string;
    lead: string;
    marketNote: string;
    once: string;
    badge: string;
    includedTitle: string;
    excludedTitle: string;
    cta: string;
  };
  comparison: ComparisonRow[];
  included: string[];
  excluded: string[];
  segmentsIntro: { eyebrow: string; title: string };
  segments: Segment[];
  law: {
    eyebrow: string;
    title: string;
    missedTitle: string;
    missedLead: string;
    missedEmphasis: string;
    missedTail: string;
    deedAlt: string;
    notaryLabel: string;
    notaryArea: string;
  };
  lawCards: LawCard[];
  process: { eyebrow: string; title: string; lead: string };
  steps: Step[];
  limits: {
    eyebrow: string;
    title: string;
    lead: string;
    canTitle: string;
    cannotTitle: string;
  };
  can: string[];
  cannot: string[];
  docs: { eyebrow: string; title: string; lead: string; imageAlt: string };
  docList: string[];
  faqTitle: string;
  faqs: Faq[];
  form: {
    title: string;
    lead: string;
    talkTitle: string;
    privacy: string;
    statusLabel: string;
    statusPlaceholder: string;
    statusOptions: string[];
    citizenshipLabel: string;
    citizenshipOptions: string[];
    dateLabel: string;
    dateHint: string;
    assetsLabel: string;
    assetsPlaceholder: string;
    assetsOptions: string[];
    nameLabel: string;
    phoneLabel: string;
    phonePlaceholder: string;
    emailLabel: string;
    emailHint: string;
    notesLabel: string;
    notesPlaceholder: string;
    submit: string;
    sending: string;
    dataNote: string;
    sendError: string;
    doneTitle: string;
    doneCopy: string;
    doneCta: string;
    optional: string;
  };
  whatsappPrefill: string;
  /** Lead body labels. English leads want an English reply. */
  lead: {
    heading: string;
    language: string;
    status: string;
    citizenship: string;
    assets: string;
    weddingDate: string;
    noNotes: string;
    none: string;
  };
  jsonLd: { serviceType: string; offerDescription: string };
};

const id: PrenupCopy = {
  price: PRICE.id,
  priceShort: PRICE_SHORT.id,
  meta: {
    title: `Perjanjian Pranikah Jakarta — ${PRICE_SHORT.id} All-in, Akta Notaris + Pencatatan | 7Magic`,
    description:
      'Jasa perjanjian pranikah dan pisah harta di Jakarta. Rp 3,5 juta sudah termasuk konsultasi, draft, akta notaris, dan pencatatan di Dukcapil. Bisa juga dibuat setelah menikah. Konsultasi awal gratis.',
    keywords:
      'perjanjian pranikah, perjanjian pra nikah, biaya perjanjian pranikah, perjanjian pisah harta, perjanjian perkawinan, prenuptial agreement Indonesia, perjanjian pranikah WNA, notaris perjanjian pranikah Jakarta'
  },
  hero: {
    eyebrow: 'Perjanjian pranikah · Jakarta',
    title: `Perjanjian pranikah, selesai sampai tercatat — ${PRICE.id}`,
    lead: 'Sudah termasuk konsultasi, penyusunan draft, akta notaris, dan pencatatan di Dukcapil. Satu angka, tanpa tagihan susulan. Bisa juga dibuat setelah Anda menikah.',
    ctaConsult: 'Konsultasi gratis',
    ctaWhatsapp: 'Tanya lewat WhatsApp',
    note: 'Konsultasi awal tidak dipungut biaya. Kalau Anda tidak jadi lanjut, tidak ada tagihan.',
    imageAlt: 'Pasangan tersenyum saat berkonsultasi dengan seorang penasihat hukum'
  },
  stats: [
    { value: PRICE.id, label: 'All-in, sampai tercatat' },
    { value: '2 – 3 minggu', label: 'Dari konsultasi sampai selesai' },
    { value: 'Notaris internal', label: 'Tanpa perantara, tanpa markup' },
    { value: 'Jakarta', label: 'Jabodetabek, bisa tatap muka' }
  ],
  price_section: {
    eyebrow: 'Harga',
    title: 'Satu angka, dan kami tulis apa saja yang ada di dalamnya',
    lead: 'Keluhan paling umum soal jasa perjanjian pranikah bukan harganya, tapi tagihan yang muncul belakangan. Jadi ini isinya, hitam di atas putih.',
    marketNote:
      'Kisaran pasar di atas adalah rentang tarif notaris di Jakarta yang dipublikasikan secara umum, bukan tarif satu kantor tertentu. Tarif tiap notaris berbeda-beda menurut kompleksitas perjanjian.',
    once: 'sekali bayar',
    badge: 'Harga perkenalan',
    includedTitle: 'Sudah termasuk',
    excludedTitle: 'Dikutip terpisah',
    cta: 'Mulai dari konsultasi gratis'
  },
  comparison: [
    {
      label: 'Notaris pada umumnya di Jakarta',
      price: 'Rp 4 – 15 juta',
      note: 'Biaya pencatatan dan konsultasi lanjutan sering dihitung terpisah.',
      ours: false
    },
    {
      label: '7Magic — paket perjanjian pranikah',
      price: `${PRICE.id} all-in`,
      note: 'Konsultasi, penyusunan draft, akta notaris, dan pencatatan. Satu angka.',
      ours: true
    }
  ],
  included: [
    'Konsultasi awal bersama tim legal kami — berdua atau sendiri dulu, terserah Anda',
    'Penyusunan draft perjanjian sesuai kondisi aset dan rencana Anda',
    'Dua kali revisi draft tanpa biaya tambahan',
    'Penandatanganan akta di hadapan notaris kami',
    'Pencatatan ke Dukcapil atau KUA sampai terbit catatan pinggirnya',
    'Salinan akta resmi untuk Anda dan pasangan'
  ],
  excluded: [
    'Struktur aset yang rumit — perusahaan tertutup, saham lintas negara, trust',
    'Penerjemah tersumpah untuk pasangan WNA yang tidak berbahasa Indonesia',
    'Legalisasi atau apostille dokumen dari luar negeri',
    'Perubahan isi perjanjian setelah akta ditandatangani'
  ],
  segmentsIntro: {
    eyebrow: 'Siapa yang biasanya butuh',
    title: 'Empat kondisi yang paling sering datang ke meja kami'
  },
  segments: [
    {
      title: 'Menikah dengan WNA',
      copy: 'Tanpa perjanjian pisah harta, WNI yang menikah dengan WNA bisa kehilangan hak untuk memegang Sertifikat Hak Milik. Ini alasan paling sering orang datang ke kami.',
      alt: 'Sepasang cincin kawin di dalam kotak'
    },
    {
      title: 'Punya usaha sendiri',
      copy: 'Kalau usaha Anda berisiko, utang usaha bisa menyeret harta bersama. Perjanjian ini memisahkan mana yang bisa dikejar kreditur dan mana yang tidak.',
      alt: 'Pasangan muda berkonsultasi dengan seorang penasihat'
    },
    {
      title: 'Sudah punya aset sebelum menikah',
      copy: 'Rumah, tanah, atau warisan yang Anda bawa masuk ke pernikahan. Perjanjian menegaskan statusnya sejak hari pertama, bukan diperdebatkan belakangan.',
      alt: 'Seorang profesional memeriksa berkas di kantor hukum'
    },
    {
      title: 'Sudah menikah, baru mau buat',
      copy: 'Bisa. Sejak Putusan MK No. 69/PUU-XIII/2015, perjanjian perkawinan boleh dibuat setelah pernikahan berlangsung. Prosesnya sama, harganya sama.',
      alt: 'Pasangan menandatangani dokumen didampingi seorang penasihat'
    }
  ],
  law: {
    eyebrow: 'Dasar hukum',
    title: 'Ini bukan tren impor. Ini diatur undang-undang.',
    missedTitle: 'Yang paling sering terlewat',
    missedLead: 'Bukan di aktanya, melainkan di ',
    missedEmphasis: 'pencatatannya',
    missedTail:
      '. Akta notaris yang tidak dicatatkan ke Dukcapil atau KUA mengikat Anda berdua, tapi tidak mengikat pihak ketiga — bank, kreditur, atau BPN. Untuk urusan properti, justru pihak ketiga inilah yang penting.',
    deedAlt: 'Tangan menandatangani dokumen perjanjian dengan pena',
    notaryLabel: 'Akta diterbitkan oleh',
    notaryArea: 'Wilayah kerja'
  },
  lawCards: [
    {
      reference: 'Pasal 29 UU No. 1 Tahun 1974',
      title: 'Perjanjian perkawinan diakui undang-undang',
      copy: 'Pada waktu atau sebelum perkawinan dilangsungkan, kedua pihak atas persetujuan bersama dapat mengajukan perjanjian tertulis yang disahkan oleh pegawai pencatat perkawinan atau notaris.'
    },
    {
      reference: 'Putusan MK No. 69/PUU-XIII/2015',
      title: 'Boleh dibuat setelah menikah',
      copy: 'Mahkamah Konstitusi memperluas aturannya: perjanjian perkawinan kini boleh dibuat juga selama masa pernikahan, bukan cuma sebelum. Inilah yang membuat pasangan yang sudah menikah bertahun-tahun tetap bisa membuatnya.'
    }
  ],
  process: {
    eyebrow: 'Prosesnya',
    title: 'Empat langkah, dua di antaranya kami yang kerjakan',
    lead: 'Anda hanya perlu hadir di langkah pertama dan ketiga. Sisanya urusan kami, dan Anda dikabari di setiap perpindahan tahap.'
  },
  steps: [
    {
      when: 'Hari 1',
      title: 'Cerita dulu, gratis',
      copy: 'Lewat WhatsApp atau tatap muka. Kami tanya soal aset, kewarganegaraan, dan rencana Anda. Belum ada biaya apa pun di tahap ini.'
    },
    {
      when: '2 – 3 hari kerja',
      title: 'Draft kami kirim',
      copy: 'Berisi pasal-pasal yang sudah disesuaikan, dengan penjelasan bahasa manusia di sampingnya supaya Anda tahu apa yang Anda tanda tangani.'
    },
    {
      when: 'Sesuai jadwal Anda',
      title: 'Tanda tangan akta',
      copy: 'Anda berdua hadir di hadapan notaris kami, bawa dokumen asli. Sekitar satu jam, selesai hari itu juga.'
    },
    {
      when: '7 – 14 hari kerja',
      title: 'Kami catatkan',
      copy: 'Akta didaftarkan ke Dukcapil atau KUA. Tanpa langkah ini perjanjian tidak mengikat pihak ketiga — dan justru langkah ini yang paling sering terlewat.'
    }
  ],
  limits: {
    eyebrow: 'Batasannya',
    title: 'Yang boleh diatur, dan yang tidak akan kami tuliskan',
    lead: 'Perjanjian yang memuat pasal terlarang bisa batal seluruhnya di pengadilan. Lebih baik Anda tahu batasnya sekarang daripada mengetahuinya saat perjanjian itu dibutuhkan.',
    canTitle: 'Bisa diatur',
    cannotTitle: 'Tidak bisa diatur'
  },
  can: [
    'Pemisahan harta bawaan dan harta yang diperoleh selama pernikahan',
    'Status kepemilikan properti, rekening, saham, dan kendaraan',
    'Tanggung jawab atas utang masing-masing pihak',
    'Pengaturan biaya rumah tangga dan pendidikan anak',
    'Pembagian penghasilan dan aset usaha',
    'Ketentuan bila salah satu pihak meninggal atau pernikahan berakhir'
  ],
  cannot: [
    'Melepaskan hak atas harta warisan yang dijamin undang-undang',
    'Menyimpangi hak dan kewajiban yang timbul dari hubungan suami istri',
    'Isi yang melanggar kesusilaan atau ketertiban umum',
    'Membebani satu pihak dengan utang melebihi bagiannya',
    'Hal-hal yang merugikan kepentingan anak'
  ],
  docs: {
    eyebrow: 'Persiapan',
    title: 'Dokumen yang perlu Anda siapkan',
    lead: 'Tidak perlu lengkap saat konsultasi pertama. Ini daftar yang dibutuhkan sampai hari penandatanganan.',
    imageAlt: 'Berkas dan dokumen tertata di atas meja kayu'
  },
  docList: [
    'KTP dan Kartu Keluarga kedua calon',
    'Akta kelahiran kedua calon',
    'Paspor dan KITAS/KITAP bila salah satu pihak WNA',
    'Daftar aset yang ingin diatur — tidak perlu sertifikat aslinya di tahap draft',
    'Buku nikah atau akta perkawinan, bila dibuat setelah menikah',
    'Pas foto berwarna, dua lembar masing-masing'
  ],
  faqTitle: 'Pertanyaan yang paling sering masuk',
  faqs: [
    {
      q: 'Kenapa Rp 3,5 juta, sementara di tempat lain bisa sampai Rp 15 juta?',
      a: 'Karena notaris kami ada di dalam grup, jadi tidak ada lapisan perantara yang mengambil margin. Angka Rp 3,5 juta berlaku untuk perjanjian dengan struktur aset standar — properti, rekening, kendaraan, dan usaha perorangan. Kalau kasus Anda melibatkan perusahaan tertutup atau aset di luar negeri, kami bilang di konsultasi awal, sebelum Anda bayar apa pun.'
    },
    {
      q: 'Apakah harga itu sudah termasuk biaya pencatatan di Dukcapil?',
      a: 'Sudah. Konsultasi, draft, akta notaris, dan pencatatan semuanya di dalam Rp 3,5 juta. Tidak ada tagihan susulan untuk langkah-langkah itu.'
    },
    {
      q: 'Saya sudah menikah. Masih bisa buat?',
      a: 'Bisa. Sebelum tahun 2016 memang harus sebelum menikah, tapi Putusan Mahkamah Konstitusi No. 69/PUU-XIII/2015 membuka pembuatan perjanjian perkawinan selama masa pernikahan. Yang perlu diingat: perjanjian itu berlaku sejak dicatatkan, bukan mundur ke tanggal pernikahan.'
    },
    {
      q: 'Pasangan saya WNA dan kami mau beli rumah atas nama saya. Cukup dengan ini?',
      a: 'Inilah fungsinya. Tanpa perjanjian pisah harta, rumah yang Anda beli dianggap harta bersama, dan karena pasangan Anda WNA, Hak Milik tidak bisa dipertahankan. Dengan perjanjian yang sudah dicatatkan, Anda bisa membeli dan memegang SHM atas nama sendiri seperti WNI lain. Bawa perjanjian ini saat ke notaris/PPAT waktu transaksi.'
    },
    {
      q: 'Berapa lama sampai selesai?',
      a: 'Draft 2–3 hari kerja. Tanda tangan akta menyesuaikan jadwal Anda. Pencatatan 7–14 hari kerja tergantung antrean Dukcapil. Jadi realistisnya 2–3 minggu dari konsultasi pertama sampai catatan pinggir terbit. Kalau tanggal nikah Anda lebih mepet dari itu, bilang di awal — kami pernah mengejar yang sepuluh hari.'
    },
    {
      q: 'Apakah ini tidak membuat pasangan saya tersinggung?',
      a: 'Kekhawatiran yang paling sering kami dengar. Pengalaman kami: yang bikin tersinggung biasanya bukan perjanjiannya, tapi cara memunculkannya — mendadak, sudah jadi, tinggal tanda tangan. Itu sebabnya konsultasi pertama kami buka untuk berdua, dan draftnya kami tulis dengan penjelasan di samping tiap pasal. Anda berdua membaca hal yang sama.'
    },
    {
      q: 'Apakah perjanjian ini bisa diubah nanti?',
      a: 'Bisa, selama kedua pihak sepakat dan perubahannya dicatatkan lagi. Yang tidak bisa adalah mengubah sepihak, atau mengubah dengan cara yang merugikan pihak ketiga yang sudah terlanjur bergantung pada perjanjian lama.'
    },
    {
      q: 'Kalau kami tidak jadi lanjut setelah konsultasi?',
      a: 'Tidak apa-apa, dan tidak ada biaya. Konsultasi awal memang kami gratiskan supaya Anda bisa memutuskan dengan informasi yang cukup.'
    }
  ],
  form: {
    title: 'Ceritakan kondisi Anda',
    lead: `Empat jawaban sudah cukup untuk kami menilai apakah kasus Anda masuk paket ${PRICE.id} atau perlu dikutip terpisah. Kami balas di hari kerja yang sama.`,
    talkTitle: 'Lebih enak ngobrol langsung?',
    privacy:
      'Apa pun yang Anda ceritakan di sini kami perlakukan sebagai rahasia klien, termasuk kalau Anda akhirnya tidak jadi menggunakan jasa kami.',
    statusLabel: 'Status Anda',
    statusPlaceholder: 'Pilih salah satu',
    statusOptions: [
      'Belum menikah, sedang merencanakan',
      'Akan menikah dalam 3 bulan ke depan',
      'Sudah menikah (perjanjian pasca-nikah)'
    ],
    citizenshipLabel: 'Kewarganegaraan',
    citizenshipOptions: ['WNI dengan WNI', 'WNI dengan WNA', 'Keduanya WNA'],
    dateLabel: 'Rencana tanggal nikah',
    dateHint: '(kira-kira saja)',
    assetsLabel: 'Aset utama yang ingin diatur',
    assetsPlaceholder: 'Belum yakin',
    assetsOptions: [
      'Properti (rumah / tanah / apartemen)',
      'Usaha atau saham perusahaan',
      'Tabungan dan investasi',
      'Aset di luar negeri',
      'Belum ada, tapi ingin mengatur ke depan'
    ],
    nameLabel: 'Nama Anda',
    phoneLabel: 'Nomor WhatsApp',
    phonePlaceholder: '08xx xxxx xxxx',
    emailLabel: 'Email',
    emailHint: '(opsional)',
    notesLabel: 'Ada yang perlu kami tahu?',
    notesPlaceholder:
      'Mau beli rumah bulan depan, pasangan WNA, sertifikat masih atas nama orang tua…',
    submit: 'Kirim & minta konsultasi gratis',
    sending: 'Mengirim…',
    dataNote:
      'Data ini kami pakai untuk menghubungi Anda soal perjanjian pranikah. Tidak untuk yang lain.',
    sendError: 'Pesan gagal terkirim. Coba lagi, atau langsung chat kami di WhatsApp.',
    doneTitle: 'Sudah kami terima',
    doneCopy:
      'Kami hubungi di hari kerja yang sama. Kalau tanggal nikah Anda mepet, chat kami di WhatsApp dan sebutkan tanggalnya.',
    doneCta: 'Chat sekarang',
    optional: 'opsional'
  },
  whatsappPrefill: `Halo 7Magic, saya mau tanya soal perjanjian pranikah yang ${PRICE_SHORT.id}. Kondisi kami:`,
  lead: {
    heading: 'LEAD: Perjanjian Pranikah',
    language: 'Bahasa',
    status: 'Status',
    citizenship: 'Kewarganegaraan',
    assets: 'Aset utama',
    weddingDate: 'Rencana tanggal nikah',
    noNotes: 'Tidak ada catatan tambahan.',
    none: '—'
  },
  jsonLd: {
    serviceType: 'Pembuatan perjanjian pranikah',
    offerDescription:
      'Konsultasi, penyusunan draft, akta notaris, dan pencatatan di Dukcapil/KUA.'
  }
};

const en: PrenupCopy = {
  price: PRICE.en,
  priceShort: PRICE_SHORT.en,
  meta: {
    title: `Prenuptial Agreement Jakarta — ${PRICE_SHORT.en} All-in, Notarial Deed + Registration | 7Magic`,
    description:
      'Prenuptial and separation-of-property agreements in Jakarta. Rp 3,500,000 covers the consultation, drafting, the notarial deed and registration with Dukcapil. Can also be made after you are married. First consultation free.',
    keywords:
      'prenuptial agreement Indonesia, prenup Jakarta, separation of property agreement, marital agreement Indonesia, prenup cost Indonesia, prenuptial agreement foreigner Indonesia, postnuptial agreement Indonesia, notary prenuptial agreement Jakarta'
  },
  hero: {
    eyebrow: 'Prenuptial agreement · Jakarta',
    title: `A prenuptial agreement, seen through to registration — ${PRICE.en}`,
    lead: 'Covers the consultation, drafting, the notarial deed and registration with Dukcapil, the civil registry. One figure, no invoices afterwards. It can also be made after you are married.',
    ctaConsult: 'Free consultation',
    ctaWhatsapp: 'Ask on WhatsApp',
    note: 'The first consultation costs nothing. If you decide not to go ahead, there is no bill.',
    imageAlt: 'A smiling couple in consultation with a legal adviser'
  },
  stats: [
    { value: PRICE.en, label: 'All-in, through to registration' },
    { value: '2 – 3 weeks', label: 'From consultation to done' },
    { value: 'In-house notary', label: 'No middleman, no markup' },
    { value: 'Jakarta', label: 'Greater Jakarta, in person if you prefer' }
  ],
  price_section: {
    eyebrow: 'Price',
    title: 'One figure, and we write down what is inside it',
    lead: 'The usual complaint about prenup services is not the price but the invoices that arrive later. So here is what is included, in black and white.',
    marketNote:
      'The market range above is the publicly published spread of notary fees in Jakarta, not the rate of any one office. Fees vary by notary and by how complex the agreement is.',
    once: 'one-off',
    badge: 'Introductory price',
    includedTitle: 'Included',
    excludedTitle: 'Quoted separately',
    cta: 'Start with a free consultation'
  },
  comparison: [
    {
      label: 'A typical notary in Jakarta',
      price: 'Rp 4 – 15 million',
      note: 'Registration fees and follow-up consultations are often billed on top.',
      ours: false
    },
    {
      label: '7Magic — prenuptial agreement package',
      price: `${PRICE.en} all-in`,
      note: 'Consultation, drafting, the notarial deed and registration. One figure.',
      ours: true
    }
  ],
  included: [
    'A first consultation with our legal team — together or on your own first, as you prefer',
    'Drafting the agreement around your actual assets and plans',
    'Two rounds of revisions at no extra cost',
    'Signing the deed before our notary',
    'Registration with Dukcapil or the KUA, through to the marginal note being issued',
    'Official copies of the deed for you and your partner'
  ],
  excluded: [
    'Complex asset structures — private companies, cross-border shareholdings, trusts',
    'A sworn translator for a foreign partner who does not read Indonesian',
    'Legalisation or apostille of documents issued abroad',
    'Changes to the agreement after the deed is signed'
  ],
  segmentsIntro: {
    eyebrow: 'Who usually needs one',
    title: 'The four situations that most often reach our desk'
  },
  segments: [
    {
      title: 'Marrying a foreign national',
      copy: 'Without a separation-of-property agreement, an Indonesian citizen married to a foreign national can lose the right to hold Hak Milik, the freehold title. This is the most common reason people come to us.',
      alt: 'A pair of wedding rings in a box'
    },
    {
      title: 'Running your own business',
      copy: 'If your business carries risk, its debts can reach into jointly owned property. The agreement draws the line between what creditors can pursue and what they cannot.',
      alt: 'A young couple in consultation with an adviser'
    },
    {
      title: 'Assets you already owned',
      copy: 'A house, land or an inheritance you bring into the marriage. The agreement fixes their status from day one instead of leaving it to be argued about later.',
      alt: 'A professional reviewing files in a law office'
    },
    {
      title: 'Already married, only now arranging it',
      copy: 'You can. Since Constitutional Court Decision No. 69/PUU-XIII/2015 a marital agreement may be made during the marriage. Same process, same price.',
      alt: 'A couple signing documents with an adviser present'
    }
  ],
  law: {
    eyebrow: 'The legal basis',
    title: 'This is not an imported trend. It is written into the law.',
    missedTitle: 'What gets missed most often',
    missedLead: 'Not the deed, but the ',
    missedEmphasis: 'registration',
    missedTail:
      '. A notarial deed that is never registered with Dukcapil or the KUA binds the two of you, but it does not bind third parties — a bank, a creditor, or the land agency. For anything to do with property, third parties are exactly who matter.',
    deedAlt: 'Hands signing an agreement with a pen',
    notaryLabel: 'Deed issued by',
    notaryArea: 'Jurisdiction'
  },
  lawCards: [
    {
      reference: 'Article 29, Law No. 1 of 1974',
      title: 'Marital agreements are recognised by statute',
      copy: 'At the time of or before the marriage is solemnised, both parties may by mutual consent submit a written agreement ratified by the marriage registrar or by a notary.'
    },
    {
      reference: 'Constitutional Court Decision No. 69/PUU-XIII/2015',
      title: 'It may be made after the wedding',
      copy: 'The Constitutional Court widened the rule: a marital agreement may now also be made during the marriage, not only before it. That is what lets couples who have been married for years still make one.'
    }
  ],
  process: {
    eyebrow: 'The process',
    title: 'Four steps, two of which are ours to do',
    lead: 'You only need to be present for the first and the third. The rest is on us, and you hear from us at every handover.'
  },
  steps: [
    {
      when: 'Day 1',
      title: 'Tell us about it, free',
      copy: 'Over WhatsApp or face to face. We ask about your assets, your citizenship and your plans. Nothing is charged at this stage.'
    },
    {
      when: '2 – 3 working days',
      title: 'We send the draft',
      copy: 'With the clauses tailored to your situation and a plain-language explanation beside each one, so you know what you are signing.'
    },
    {
      when: 'Whenever suits you',
      title: 'Signing the deed',
      copy: 'You both attend before our notary with your original documents. About an hour, finished the same day.'
    },
    {
      when: '7 – 14 working days',
      title: 'We register it',
      copy: 'The deed is registered with Dukcapil or the KUA. Without this step the agreement does not bind third parties — and this is the step most often skipped.'
    }
  ],
  limits: {
    eyebrow: 'The limits',
    title: 'What may be agreed, and what we will not write down',
    lead: 'An agreement containing a prohibited clause can be struck down in its entirety by a court. Better to know the boundaries now than at the moment the agreement is needed.',
    canTitle: 'Can be agreed',
    cannotTitle: 'Cannot be agreed'
  },
  can: [
    'Separating assets brought in from assets acquired during the marriage',
    'Ownership of property, accounts, shares and vehicles',
    'Responsibility for each party’s debts',
    'How household costs and children’s education are covered',
    'Division of income and business assets',
    'What happens if one party dies or the marriage ends'
  ],
  cannot: [
    'Waiving inheritance rights guaranteed by statute',
    'Departing from the rights and duties that arise from the marriage itself',
    'Terms that offend public morality or public order',
    'Loading one party with debts beyond their share',
    'Anything that harms the interests of a child'
  ],
  docs: {
    eyebrow: 'Getting ready',
    title: 'The documents to have ready',
    lead: 'Not all of it is needed at the first consultation. This is the full list by the day of signing.',
    imageAlt: 'Files and documents laid out on a wooden desk'
  },
  docList: [
    'KTP identity cards and the family card (Kartu Keluarga) for both parties',
    'Birth certificates for both parties',
    'Passport and KITAS/KITAP if either party is a foreign national',
    'A list of the assets to be covered — the original certificates are not needed at the drafting stage',
    'Marriage book or marriage certificate, if the agreement is made after the wedding',
    'Two colour passport photographs each'
  ],
  faqTitle: 'The questions we are asked most',
  faqs: [
    {
      q: 'Why Rp 3.5 million when elsewhere it runs to Rp 15 million?',
      a: 'Because our notary is in-house, so there is no intermediary taking a margin. The Rp 3.5 million figure applies to agreements with a standard asset structure — property, accounts, vehicles and a sole proprietorship. If your case involves a private company or assets held abroad, we say so at the first consultation, before you have paid anything.'
    },
    {
      q: 'Does the price include the Dukcapil registration fee?',
      a: 'It does. The consultation, drafting, the notarial deed and registration are all inside the Rp 3.5 million. There is no follow-up invoice for any of those steps.'
    },
    {
      q: 'I am already married. Can I still make one?',
      a: 'Yes. Before 2016 it did have to be before the wedding, but Constitutional Court Decision No. 69/PUU-XIII/2015 opened marital agreements up to couples already married. One thing to keep in mind: the agreement takes effect from the date it is registered, not retroactively from your wedding date.'
    },
    {
      q: 'My partner is a foreign national and we want to buy a house in my name. Is this enough?',
      a: 'This is exactly what it is for. Without a separation-of-property agreement, a house you buy counts as jointly owned, and because your partner is a foreign national the Hak Milik title cannot be maintained. With a registered agreement you can buy and hold Hak Milik in your own name like any other Indonesian citizen. Bring the agreement with you to the notary or land deed official at the time of the transaction.'
    },
    {
      q: 'How long does it take?',
      a: 'The draft takes 2–3 working days. Signing the deed fits your schedule. Registration takes 7–14 working days depending on the Dukcapil queue. So realistically 2–3 weeks from the first consultation to the marginal note being issued. If your wedding date is tighter than that, say so early — we have turned one around in ten days.'
    },
    {
      q: 'Will this offend my partner?',
      a: 'The worry we hear most. In our experience what causes offence is rarely the agreement itself but the way it is raised — out of nowhere, already drafted, ready to sign. That is why our first consultation is open to both of you, and why the draft is written with an explanation beside every clause. You both read the same thing.'
    },
    {
      q: 'Can the agreement be changed later?',
      a: 'Yes, as long as both parties agree and the change is registered again. What cannot be done is changing it unilaterally, or changing it in a way that harms a third party who has already relied on the old terms.'
    },
    {
      q: 'What if we decide not to proceed after the consultation?',
      a: 'That is fine, and it costs nothing. The first consultation is free precisely so that you can decide with enough information in front of you.'
    }
  ],
  form: {
    title: 'Tell us about your situation',
    lead: `Four answers are enough for us to tell whether your case fits the ${PRICE.en} package or needs a separate quote. We reply the same working day.`,
    talkTitle: 'Rather just talk?',
    privacy:
      'Whatever you tell us here we treat as client-confidential, including if you end up not using us.',
    statusLabel: 'Your status',
    statusPlaceholder: 'Choose one',
    statusOptions: [
      'Not yet married, planning ahead',
      'Marrying within the next 3 months',
      'Already married (postnuptial agreement)'
    ],
    citizenshipLabel: 'Citizenship',
    citizenshipOptions: [
      'Both Indonesian citizens',
      'Indonesian citizen with a foreign national',
      'Both foreign nationals'
    ],
    dateLabel: 'Planned wedding date',
    dateHint: '(a rough one is fine)',
    assetsLabel: 'Main assets to be covered',
    assetsPlaceholder: 'Not sure yet',
    assetsOptions: [
      'Property (house / land / apartment)',
      'A business or company shares',
      'Savings and investments',
      'Assets held abroad',
      'None yet, but we want to plan ahead'
    ],
    nameLabel: 'Your name',
    phoneLabel: 'WhatsApp number',
    phonePlaceholder: '08xx xxxx xxxx',
    emailLabel: 'Email',
    emailHint: '(optional)',
    notesLabel: 'Anything we should know?',
    notesPlaceholder:
      'Buying a house next month, partner is a foreign national, the certificate is still in my parents’ name…',
    submit: 'Send & request a free consultation',
    sending: 'Sending…',
    dataNote:
      'We use these details to contact you about the prenuptial agreement. Nothing else.',
    sendError: 'The message did not go through. Try again, or message us on WhatsApp instead.',
    doneTitle: 'We have it',
    doneCopy:
      'We will be in touch the same working day. If your wedding date is close, message us on WhatsApp and give us the date.',
    doneCta: 'Message us now',
    optional: 'optional'
  },
  whatsappPrefill: `Hi 7Magic, I would like to ask about the ${PRICE_SHORT.en} prenuptial agreement. Our situation:`,
  lead: {
    heading: 'LEAD: Prenuptial Agreement',
    language: 'Language',
    status: 'Status',
    citizenship: 'Citizenship',
    assets: 'Main assets',
    weddingDate: 'Planned wedding date',
    noNotes: 'No additional notes.',
    none: '—'
  },
  jsonLd: {
    serviceType: 'Prenuptial agreement drafting',
    offerDescription:
      'Consultation, drafting, the notarial deed, and registration with Dukcapil or the KUA.'
  }
};

const CONTENT: Record<Locale, PrenupCopy> = { id, en };

export function prenupCopy(locale: Locale): PrenupCopy {
  return CONTENT[locale] ?? CONTENT.id;
}

/**
 * Shared across locales, so the paths live here and only the alt text is
 * translated -- a duplicated path is a path that drifts.
 */
export const SEGMENT_IMAGES = [
  '/img/prenup/rings.jpg',
  '/img/prenup/advisor.jpg',
  '/img/prenup/notary.jpg',
  '/img/prenup/couple-signing.jpg'
];

/**
 * PLACEHOLDER -- deliberately empty. The notary credentials block renders only
 * when this is filled in. Putting an invented notary name and decree number on
 * the live page would be forging professional credentials, so this has to come
 * from 7Magic before launch. Not translated: a name and a decree number are the
 * same in both languages.
 */
export const NOTARY = { name: '', decree: '', area: '' };

/** The price as a bare number, for the Offer in the JSON-LD. */
export const OFFER_PRICE = '3500000';
