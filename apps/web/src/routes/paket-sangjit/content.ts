/**
 * Copy for the sangjit landing page, in both languages.
 *
 * One locale-keyed module for the same reason as the prenup page: the copy is
 * an argument that changes as a whole, not a set of independent UI strings,
 * and the type makes a locale that misses a field fail the check rather than
 * render blank.
 *
 * Indonesian is the source of truth. The English edition is for the same
 * Jakarta service -- Chinese-Indonesian families with relatives abroad, and
 * partners from outside Indonesia marrying into one -- so the packages, the
 * tray list and the customs stay identical; only the language changes. No
 * price appears in either: quotes are per enquiry, by choice.
 *
 * Package inclusions still need confirming by 7Magic before launch (tray
 * bearer counts, documentation scope, whether 7Magic supplies the tray
 * contents). Change them in both locales together.
 */

import type { Locale } from '$lib/paraglide/runtime';

export type Package = {
  name: string;
  scale: string;
  summary: string;
  featured?: boolean;
  includes: string[];
};
export type Service = { image: string; alt: string; title: string; copy: string };
export type RunBlock = { time: string; title: string; items: string[] };
export type TrayItem = { name: string; meaning: string };
export type Titled = { title: string; copy: string };
export type Step = { title: string; copy: string; when: string };
export type Faq = { q: string; a: string };

export type SangjitCopy = {
  meta: { title: string; description: string; keywords: string };
  jsonLd: { serviceType: string };
  whatsappPrefill: string;
  hero: {
    alt: string;
    eyebrow: string;
    title: string;
    lead: string;
    cta: string;
    whatsapp: string;
    note: string;
  };
  stats: { value: string; label: string }[];
  services: { eyebrow: string; title: string; items: Service[] };
  packages: {
    eyebrow: string;
    title: string;
    lead: string;
    featuredBadge: string;
    priceSlot: string;
    cta: string;
    excludedTitle: string;
    excluded: string;
    items: Package[];
  };
  runOfShow: {
    eyebrow: string;
    title: string;
    lead: string;
    blocks: RunBlock[];
    images: { src: string; alt: string }[];
  };
  trays: { eyebrow: string; title: string; lead: string; items: TrayItem[] };
  customs: { eyebrow: string; title: string; items: Titled[] };
  steps: { eyebrow: string; title: string; items: Step[] };
  faqTitle: string;
  faqs: Faq[];
  form: {
    title: string;
    lead: string;
    chatPrompt: string;
    doneTitle: string;
    doneCopy: string;
    chatNow: string;
    date: string;
    dateHint: string;
    venue: string;
    choose: string;
    venueOptions: string[];
    guests: string;
    guestsPlaceholder: string;
    package: string;
    packageNone: string;
    packageOptions: string[];
    name: string;
    phone: string;
    email: string;
    optional: string;
    notes: string;
    notesPlaceholder: string;
    sending: string;
    submit: string;
    privacy: string;
    error: string;
  };
  /** Labels for the enquiry the team receives; kept per locale like the prenup page's. */
  lead: {
    heading: string;
    language: string;
    date: string;
    venue: string;
    guests: string;
    package: string;
    none: string;
    noNotes: string;
  };
};

const PACKAGE_NAMES = ['Sangjit Intimate', 'Sangjit Signature', 'Sangjit Grand'];

const IMAGES = {
  hero: '/img/sangjit/hero.jpg',
  decor: '/img/sangjit/decor.jpg',
  trays: '/img/sangjit/trays.jpg',
  couple: '/img/sangjit/couple.jpg',
  angpao: '/img/sangjit/angpao.jpg',
  tea: '/img/sangjit/tea.jpg',
  embrace: '/img/sangjit/embrace.jpg',
  gifts: '/img/sangjit/gifts.jpg'
};

export const HERO_IMAGE = IMAGES.hero;

const id: SangjitCopy = {
  meta: {
    title: 'Paket Sangjit Jakarta — Dekorasi, Baki Seserahan, MC & Dokumentasi | 7Magic',
    description:
      'Paket sangjit Jakarta: dekorasi, baki seserahan lengkap dengan isinya, pembawa baki, MC dwibahasa, dan dokumentasi. Susunan acara dan isi 12 baki kami jelaskan lengkap. Penawaran dalam dua hari kerja.',
    keywords:
      'paket sangjit, sangjit Jakarta, dekorasi sangjit, isi baki sangjit, isi nampan sangjit, susunan acara sangjit, seserahan sangjit, MC sangjit, harga sangjit Jakarta'
  },
  jsonLd: { serviceType: 'Sangjit (Chinese-Indonesian engagement ceremony) organizing' },
  whatsappPrefill: 'Halo 7Magic, saya mau tanya soal paket sangjit. Rencana kami:',
  hero: {
    alt: 'Keluarga menjalankan prosesi pernikahan tradisional Tionghoa dengan lampion merah',
    eyebrow: 'Paket sangjit · Jakarta',
    title: 'Sangjit yang berjalan rapi, tanpa orang tua Anda jadi panitia',
    lead: 'Dekorasi, baki seserahan lengkap dengan hitungan adatnya, pembawa baki, MC dwibahasa, dan dokumentasi. Kami samakan dulu versi adat kedua keluarga sebelum apa pun dipesan.',
    cta: 'Minta penawaran',
    whatsapp: 'Tanya lewat WhatsApp',
    note: 'Sebutkan tanggal, lokasi, dan perkiraan jumlah tamu. Penawaran kami kirim dalam dua hari kerja.'
  },
  stats: [
    { value: '18+', label: 'Tahun mengurus acara' },
    { value: '1000+', label: 'Acara terselenggara' },
    { value: '100+', label: 'Vendor dalam jaringan kami' },
    { value: 'Jabodetabek', label: 'Tim datang ke lokasi Anda' }
  ],
  services: {
    eyebrow: 'Yang kami tangani',
    title: 'Enam bagian, dan hampir semuanya menyangkut hitungan adat',
    items: [
      {
        image: IMAGES.decor,
        alt: 'Mempelai wanita berbusana merah di depan dekorasi sangjit bermotif Double Happiness',
        title: 'Dekorasi & backdrop',
        copy: 'Merah-emas klasik atau nuansa pastel modern. Kami pasang pagi hari, sebelum rombongan datang.'
      },
      {
        image: IMAGES.trays,
        alt: 'Baki merah berisi seserahan sangjit dengan aksara Double Happiness keemasan',
        title: 'Baki & penataan isi',
        copy: 'Baki, penataan, dan hitungannya. Jumlah selalu genap, dan angka empat tidak pernah kami pakai.'
      },
      {
        image: IMAGES.couple,
        alt: 'Mempelai wanita berbusana xiuhefu merah keemasan bersama orang tuanya',
        title: 'Busana & pembawa baki',
        copy: 'Cheongsam untuk pembawa baki, dan sewa busana untuk mempelai bila diperlukan.'
      },
      {
        image: IMAGES.angpao,
        alt: 'Amplop angpao merah dan sepasang cincin emas',
        title: 'Angpao & uang susu',
        copy: 'Amplop, tulisan aksaranya, dan pembagiannya. Bagian yang paling sering bikin salah paham.'
      },
      {
        image: IMAGES.tea,
        alt: 'Seorang perempuan menuangkan teh untuk anggota keluarga',
        title: 'Upacara minum teh',
        copy: 'Bila keluarga menginginkan, prosesi teh kami rangkai menyatu dengan acara sangjit.'
      },
      {
        image: IMAGES.embrace,
        alt: 'Mempelai wanita berbusana merah dipeluk ibunya',
        title: 'Koordinator & MC',
        copy: 'Satu orang yang tahu urutannya, supaya orang tua Anda tidak jadi panitia di acara sendiri.'
      }
    ]
  },
  packages: {
    eyebrow: 'Paket',
    title: 'Tiga paket, dan sebagian besar keluarga memilih yang tengah',
    lead: 'Setiap sangjit berbeda — lokasi, jumlah baki, skala dekorasi, dan apakah acaranya digabung dengan jamuan makan. Karena itu kami tidak memasang harga paket di sini, melainkan menyusun penawaran sesuai rencana Anda. Sebutkan tanggal dan perkiraan jumlah tamu, penawarannya kami kirim dalam dua hari kerja.',
    featuredBadge: 'Paling sering diambil',
    priceSlot: 'Cek harga & tanggal kosong',
    cta: 'Minta penawaran paket ini',
    excludedTitle: 'Yang tidak masuk paket',
    excluded:
      'Perhiasan emas, isi angpao, dan uang susu tetap disiapkan keluarga — bagian itu memang bukan wilayah vendor. Sewa tempat, jamuan makan, dan barongsai dihitung terpisah dan kami cantumkan di penawaran, bukan diberitahukan belakangan.',
    items: [
      {
        name: PACKAGE_NAMES[0],
        scale: 'Di rumah · sampai 30 tamu',
        summary: 'Acara keluarga di rumah, tanpa dekorasi besar, tapi tetap tertata dan terdokumentasi.',
        includes: [
          'Dekorasi meja sangjit dan backdrop 2 meter',
          '8 baki merah lengkap dengan penataan isinya',
          'Dua pembawa baki berseragam',
          'Satu koordinator yang memandu jalannya acara',
          'Dokumentasi foto, 100 foto terpilih dan tersunting'
        ]
      },
      {
        name: PACKAGE_NAMES[1],
        scale: 'Rumah atau restoran · sampai 60 tamu',
        summary: 'Paket yang paling sering diambil. Lengkap sampai MC, dan keluarga tinggal duduk.',
        featured: true,
        includes: [
          'Backdrop 3 × 2,5 meter dan dekorasi meja penuh',
          '12 baki merah lengkap dengan penataan isinya',
          'Empat pembawa baki berseragam cheongsam',
          'MC dwibahasa Indonesia–Mandarin',
          'Dokumentasi foto dan video highlight satu menit',
          'Koordinator dan satu asisten sepanjang acara',
          'Penyiapan amplop angpao dan uang susu sesuai adat'
        ]
      },
      {
        name: PACKAGE_NAMES[2],
        scale: 'Restoran atau hotel · 100 tamu ke atas',
        summary: 'Untuk keluarga besar dan acara yang digabung dengan jamuan makan siang.',
        includes: [
          'Dekorasi area penuh, meja utama, dan photo corner',
          '16 atau 18 baki, sesuai hitungan keluarga',
          'Enam pembawa baki berseragam cheongsam',
          'MC dwibahasa dan koordinator senior',
          'Dokumentasi foto dan video sinematik',
          'Sewa cheongsam atau qipao untuk kedua mempelai',
          'Opsi penyambutan barongsai (biaya terpisah)'
        ]
      }
    ]
  },
  runOfShow: {
    eyebrow: 'Susunan acara',
    title: 'Seperti apa jalannya sangjit dari pagi',
    lead: 'Ini bentuk acara yang paling sering kami jalankan. Punya Anda mungkin berbeda — tapi inilah tingkat kedetailan yang Anda dapat di penawaran kami.',
    blocks: [
      {
        time: '08.00',
        title: 'Kami pasang, Anda sarapan',
        items: [
          'Tim dekorasi datang dan memasang backdrop serta meja sangjit',
          'Baki ditata dan dihitung ulang bersama perwakilan keluarga pria',
          'Briefing singkat untuk pembawa baki dan MC'
        ]
      },
      {
        time: '10.00',
        title: 'Rombongan pria tiba',
        items: [
          'Rombongan dipimpin anggota keluarga yang dituakan, jumlahnya genap',
          'Penyambutan di depan rumah atau pintu restoran',
          'Penyerahan baki dari pembawa baki pihak pria ke pihak wanita'
        ]
      },
      {
        time: '10.30',
        title: 'Ramah tamah dan penyerahan',
        items: [
          'Perkenalan kedua keluarga, dipandu MC dalam dua bahasa',
          'Baki dibawa masuk, pihak wanita mengambil bagiannya',
          'Sisanya dikembalikan ke pihak pria — tetap dalam jumlah genap'
        ]
      },
      {
        time: '12.00',
        title: 'Foto dan jamuan',
        items: [
          'Foto keluarga besar, lalu foto kedua mempelai',
          'Makan siang bersama',
          'Rombongan pria berpamitan sebelum sore — tidak menginap, sesuai adat'
        ]
      }
    ],
    images: [
      { src: IMAGES.gifts, alt: 'Rombongan keluarga membawa seserahan bertanda Double Happiness' },
      { src: IMAGES.trays, alt: 'Baki merah berisi seserahan dengan aksara Double Happiness' },
      { src: IMAGES.embrace, alt: 'Mempelai wanita berbusana merah dipeluk ibunya' }
    ]
  },
  // Isi baki paling umum di Jakarta. Tiap keluarga punya versinya sendiri;
  // koordinator kami mengonfirmasi daftar final ke kedua keluarga sebelum hari H.
  trays: {
    eyebrow: 'Isi baki',
    title: 'Dua belas baki, dan arti masing-masing',
    lead: 'Daftar ini yang paling sering ditanyakan sebelum orang menghubungi vendor mana pun, jadi kami tulis terbuka. Tiap keluarga punya versinya sendiri — koordinator kami mengonfirmasi daftar finalnya ke kedua keluarga sebelum hari H.',
    items: [
      {
        name: 'Angpao uang susu',
        meaning: 'Tanda terima kasih untuk orang tua mempelai wanita. Diletakkan di dua amplop merah terpisah.'
      },
      { name: 'Angpao uang pesta', meaning: 'Sumbangan pihak pria untuk biaya resepsi di pihak wanita.' },
      {
        name: 'Perhiasan emas',
        meaning: 'Kalung, gelang, atau cincin untuk calon mempelai wanita. Biasanya dipakaikan hari itu juga.'
      },
      {
        name: 'Kain atau busana',
        meaning: 'Bahan kain, cheongsam, atau satu set pakaian untuk calon mempelai wanita.'
      },
      {
        name: 'Kue mangkok merah',
        meaning: 'Delapan belas potong. Melambangkan rezeki yang mengembang dan berlimpah.'
      },
      {
        name: 'Kue lapis legit atau kue keranjang',
        meaning: 'Lapisannya melambangkan rezeki yang bertingkat-tingkat dan hubungan yang lengket.'
      },
      {
        name: 'Buah-buahan',
        meaning: 'Apel, pir, jeruk, atau anggur — dalam jumlah genap. Lambang kebahagiaan dan kesejahteraan.'
      },
      { name: 'Dua botol arak atau sampanye', meaning: 'Dibuka bersama sebagai tanda restu kedua keluarga.' },
      {
        name: 'Kaki babi atau daging kalengan',
        meaning: 'Dua belas kaleng, jumlah genap. Bisa diganti bila keluarga tidak mengonsumsinya.'
      },
      { name: 'Lilin merah sepasang', meaning: 'Bergambar naga dan burung hong, lambang pasangan suami istri.' },
      {
        name: 'Lengkeng dan leci kalengan',
        meaning: 'Harapan agar keturunan segera datang dan keluarga terus bertambah.'
      },
      {
        name: 'Sepasang ayam atau bebek',
        meaning: 'Dipakai sebagian keluarga sebagai lambang kesetiaan. Sifatnya tidak wajib.'
      }
    ]
  },
  customs: {
    eyebrow: 'Yang gampang keliru',
    title: 'Empat aturan yang paling sering bikin salah paham',
    items: [
      {
        title: 'Jumlahnya harus genap',
        copy: 'Delapan, dua belas, enam belas, atau delapan belas baki. Angka empat tidak pernah dipakai karena pelafalannya dekat dengan kata "mati".'
      },
      {
        title: 'Tidak semua diambil',
        copy: 'Pihak wanita mengambil sebagian isi baki, lalu mengembalikan sisanya ke pihak pria — dan yang dikembalikan pun harus tetap genap.'
      },
      {
        title: 'Uang susu punya kode',
        copy: 'Berapa banyak yang diambil keluarga wanita membawa pesan tersendiri, dan kebiasaannya berbeda antar keluarga. Koordinator kami menanyakan ini ke kedua belah pihak jauh sebelum hari H, supaya tidak ada yang salah membaca maksud.'
      },
      {
        title: 'Pagi hari, dan pamit sebelum sore',
        copy: 'Sangjit lazimnya digelar pukul 10.00 sampai 13.00, satu minggu hingga satu bulan sebelum hari pernikahan. Rombongan pria pamit sebelum malam.'
      }
    ]
  },
  steps: {
    eyebrow: 'Cara kerja kami',
    title: 'Empat langkah, dua di antaranya kami',
    items: [
      {
        title: 'Ceritakan rencananya',
        copy: 'Tanggal, lokasi, dan kira-kira berapa orang. Lima menit di WhatsApp sudah cukup untuk mulai.',
        when: 'Hari 1'
      },
      {
        title: 'Kami kirim penawaran',
        copy: 'Lengkap dengan sketsa dekorasi, daftar isi baki, dan susunan acara per jam — bukan sekadar daftar harga.',
        when: '2 hari kerja'
      },
      {
        title: 'Kami temui kedua keluarga',
        copy: 'Ini bagian yang paling menentukan. Kami samakan versi adat kedua keluarga sebelum apa pun dipesan.',
        when: 'Setelah Anda setuju'
      },
      {
        title: 'Hari H, Anda tinggal hadir',
        copy: 'Tim datang pukul delapan pagi. Orang tua Anda datang sebagai tuan rumah, bukan sebagai panitia.',
        when: 'Hari acara'
      }
    ]
  },
  faqTitle: 'Pertanyaan yang paling sering masuk',
  faqs: [
    {
      q: 'Berapa baki yang sebaiknya kami siapkan?',
      a: 'Dua belas adalah jumlah yang paling umum di Jakarta dan yang kami sarankan kalau keluarga tidak punya patokan sendiri. Delapan untuk acara yang lebih sederhana, enam belas atau delapan belas untuk keluarga besar. Yang penting genap, dan bukan empat.'
    },
    {
      q: 'Kapan sangjit sebaiknya digelar?',
      a: 'Umumnya satu minggu sampai satu bulan sebelum hari pernikahan, pagi hari sekitar pukul 10.00 sampai 13.00. Beberapa keluarga memilih tanggal berdasarkan penanggalan Imlek — kalau keluarga Anda begitu, sebutkan sejak awal supaya kami kunci jadwal tim di tanggal itu.'
    },
    {
      q: 'Keluarga kami sudah tidak menjalankan adat ini. Masih perlu?',
      a: 'Banyak klien kami datang persis dengan kalimat itu, biasanya karena satu pihak keluarga masih ingin ada dan pihak lain sudah tidak paham urutannya. Kami sering menjalankan versi yang lebih ringkas: baki tetap ada, prosesi tetap ada, tapi durasinya dipendekkan. Yang kami jaga adalah tidak ada pihak yang merasa acaranya dikurangi diam-diam.'
    },
    {
      q: 'Apakah 7Magic juga menyediakan isi bakinya?',
      a: 'Baki, penataan, dan barang-barang yang tidak berhubungan dengan uang, kami siapkan. Perhiasan emas, angpao, dan uang susu tetap disiapkan pihak keluarga — kami hanya menyiapkan amplop, penulisan aksaranya, dan menempatkannya sesuai adat.'
    },
    {
      q: 'Bisa digelar di restoran atau hotel, bukan di rumah?',
      a: 'Bisa, dan makin banyak yang memilih begitu karena sekalian jamuan makan siang. Kami koordinasi dengan pihak restoran soal ruang, waktu pemasangan dekorasi, dan tata letak meja. Kalau Anda belum punya tempat, kami bantu carikan.'
    },
    {
      q: 'Salah satu keluarga kami bukan Tionghoa. Bagaimana?',
      a: 'Sering terjadi, dan justru di situ koordinator paling berguna. Kami buat penjelasan singkat untuk keluarga yang belum familiar — apa yang akan terjadi, apa artinya, dan apa yang perlu mereka lakukan. MC kami juga menjelaskan tiap tahap saat acara berjalan, jadi tidak ada tamu yang bingung harus berbuat apa.'
    },
    {
      q: 'Berapa lama acaranya?',
      a: 'Prosesi intinya sekitar satu setengah jam. Dengan jamuan makan siang, totalnya tiga sampai empat jam. Tim kami sudah di lokasi sejak pukul delapan pagi untuk pemasangan.'
    },
    {
      q: 'Apakah bisa digabung dengan lamaran?',
      a: 'Bisa, dan cukup banyak keluarga yang menggabungkan keduanya untuk menghemat waktu dan biaya. Susunan acaranya kami sesuaikan supaya kedua prosesi tidak terasa tumpang tindih.'
    }
  ],
  form: {
    title: 'Ceritakan rencana Anda',
    lead: 'Empat jawaban sudah cukup untuk mulai. Kami balas dalam dua hari kerja dengan sketsa dekorasi, daftar isi baki, dan susunan acara per jam.',
    chatPrompt: 'Lebih enak ngobrol langsung?',
    doneTitle: 'Sudah kami terima',
    doneCopy:
      'Penawaran kami kirim dalam dua hari kerja. Kalau tanggal Anda lebih mepet dari itu, chat kami di WhatsApp dan sebutkan tanggalnya.',
    chatNow: 'Chat sekarang',
    date: 'Tanggal sangjit',
    dateHint: '(kira-kira saja)',
    venue: 'Lokasi',
    choose: 'Pilih salah satu',
    venueOptions: ['Di rumah', 'Restoran', 'Hotel atau gedung', 'Belum ditentukan — mohon dibantu'],
    guests: 'Perkiraan jumlah tamu',
    guestsPlaceholder: 'mis. 40',
    package: 'Paket yang diminati',
    packageNone: 'Belum tahu',
    packageOptions: [...PACKAGE_NAMES, 'Belum tahu, mohon disarankan'],
    name: 'Nama Anda',
    phone: 'Nomor WhatsApp',
    email: 'Email',
    optional: '(opsional)',
    notes: 'Ada yang perlu kami tahu?',
    notesPlaceholder: 'Keluarga minta 16 baki, sekalian lamaran, ada tante yang ingin barongsai…',
    sending: 'Mengirim…',
    submit: 'Kirim & minta penawaran',
    privacy: 'Data ini kami pakai untuk menyusun penawaran sangjit Anda. Tidak untuk yang lain.',
    error: 'Pesan gagal terkirim. Coba lagi, atau langsung chat kami di WhatsApp.'
  },
  lead: {
    heading: 'LEAD: Paket Sangjit',
    language: 'Bahasa',
    date: 'Tanggal sangjit',
    venue: 'Lokasi',
    guests: 'Perkiraan tamu',
    package: 'Paket diminati',
    none: '—',
    noNotes: 'Tidak ada catatan tambahan.'
  }
};

const en: SangjitCopy = {
  meta: {
    title: 'Sangjit Package Jakarta — Decoration, Gift Trays, MC & Photography | 7Magic',
    description:
      'Sangjit packages in Jakarta: decoration, gift trays with their contents, tray bearers, a bilingual MC and photography. The full run of the day and what goes on all 12 trays, explained. A quote within two working days.',
    keywords:
      'sangjit package, sangjit Jakarta, sangjit ceremony, Chinese Indonesian engagement, sangjit trays, sangjit gift list, sangjit decoration, Chinese betrothal gifts Indonesia, guo da li Indonesia'
  },
  jsonLd: { serviceType: 'Sangjit (Chinese-Indonesian engagement ceremony) organizing' },
  whatsappPrefill: "Hi 7Magic, I'd like to ask about a sangjit package. Our plan:",
  hero: {
    alt: 'A family performing a traditional Chinese wedding ceremony under red lanterns',
    eyebrow: 'Sangjit package · Jakarta',
    title: "A sangjit that runs smoothly, without your parents having to organise it",
    lead: "Decoration, gift trays counted the way custom requires, tray bearers, a bilingual MC and photography. Before anything is booked, we agree on one version of the customs with both families.",
    cta: 'Ask for a quote',
    whatsapp: 'Ask on WhatsApp',
    note: 'Tell us the date, the place and roughly how many guests. We send a quote within two working days.'
  },
  stats: [
    { value: '18+', label: 'Years running events' },
    { value: '1000+', label: 'Events delivered' },
    { value: '100+', label: 'Vendors in our network' },
    { value: 'Jabodetabek', label: 'Our team comes to you' }
  ],
  services: {
    eyebrow: 'What we handle',
    title: 'Six parts, and nearly all of them come down to counting by custom',
    items: [
      {
        image: IMAGES.decor,
        alt: 'A bride in red in front of sangjit decoration with a Double Happiness motif',
        title: 'Decoration & backdrop',
        copy: 'Classic red and gold or soft modern pastels. We set up in the morning, before the groom’s party arrives.'
      },
      {
        image: IMAGES.trays,
        alt: 'Red trays of sangjit gifts marked with a gold Double Happiness character',
        title: 'Trays & arrangement',
        copy: 'The trays, how they are laid out and how many. Always an even number, and never four.'
      },
      {
        image: IMAGES.couple,
        alt: 'A bride in a red and gold xiuhefu with her parents',
        title: 'Outfits & tray bearers',
        copy: 'Cheongsams for the tray bearers, and outfit hire for the couple if you need it.'
      },
      {
        image: IMAGES.angpao,
        alt: 'Red angpao envelopes and a pair of gold rings',
        title: 'Angpao & milk money',
        copy: 'The envelopes, the characters written on them and how they are shared out. The part most often misunderstood.'
      },
      {
        image: IMAGES.tea,
        alt: 'A woman pouring tea for family members',
        title: 'Tea ceremony',
        copy: 'If the family wishes, we fold the tea ceremony into the sangjit itself.'
      },
      {
        image: IMAGES.embrace,
        alt: 'A bride in red embraced by her mother',
        title: 'Coordinator & MC',
        copy: 'One person who knows the order of things, so your parents are not running their own event.'
      }
    ]
  },
  packages: {
    eyebrow: 'Packages',
    title: 'Three packages, and most families choose the middle one',
    lead: 'Every sangjit is different: the venue, the number of trays, the scale of the decoration, and whether a meal follows. So we do not list package prices here; we put together a quote for your plan. Tell us the date and roughly how many guests, and the quote reaches you within two working days.',
    featuredBadge: 'Most chosen',
    priceSlot: 'Check price & availability',
    cta: 'Ask for a quote for this package',
    excludedTitle: 'What packages do not include',
    excluded:
      'Gold jewellery, the money inside the angpao and the milk money are prepared by the family; that part is never a vendor’s. Venue hire, the meal and a lion dance are priced separately and shown in the quote, not mentioned afterwards.',
    items: [
      {
        name: PACKAGE_NAMES[0],
        scale: 'At home · up to 30 guests',
        summary: 'A family occasion at home, without large decoration, but still well arranged and photographed.',
        includes: [
          'Sangjit table decoration and a 2-metre backdrop',
          '8 red trays, with their contents arranged',
          'Two tray bearers in uniform',
          'One coordinator who guides the ceremony',
          'Photography, 100 selected and edited photos'
        ]
      },
      {
        name: PACKAGE_NAMES[1],
        scale: 'Home or restaurant · up to 60 guests',
        summary: 'The package chosen most often. Everything up to the MC, so the family simply sits down.',
        featured: true,
        includes: [
          'A 3 × 2.5-metre backdrop and full table decoration',
          '12 red trays, with their contents arranged',
          'Four tray bearers in cheongsams',
          'A bilingual Indonesian–Mandarin MC',
          'Photography and a one-minute highlight video',
          'A coordinator and one assistant throughout',
          'Angpao and milk-money envelopes prepared according to custom'
        ]
      },
      {
        name: PACKAGE_NAMES[2],
        scale: 'Restaurant or hotel · 100 guests and more',
        summary: 'For large families, and for a sangjit followed by lunch.',
        includes: [
          'Full-area decoration, a head table and a photo corner',
          '16 or 18 trays, as the family counts them',
          'Six tray bearers in cheongsams',
          'A bilingual MC and a senior coordinator',
          'Photography and a cinematic video',
          'Cheongsam or qipao hire for the couple',
          'An optional lion dance welcome (priced separately)'
        ]
      }
    ]
  },
  runOfShow: {
    eyebrow: 'Run of the day',
    title: 'How a sangjit unfolds, from the morning on',
    lead: 'This is the shape we run most often. Yours may differ, but this is the level of detail you get in our quote.',
    blocks: [
      {
        time: '08:00',
        title: 'We set up, you have breakfast',
        items: [
          'The decoration team arrives and sets up the backdrop and the sangjit table',
          'Trays are arranged and counted again with someone from the groom’s family',
          'A short briefing for the tray bearers and the MC'
        ]
      },
      {
        time: '10:00',
        title: 'The groom’s party arrives',
        items: [
          'The party is led by an elder of the family, in an even number',
          'A welcome at the front of the house or the restaurant door',
          'The groom’s tray bearers hand the trays to the bride’s side'
        ]
      },
      {
        time: '10:30',
        title: 'Introductions and the exchange',
        items: [
          'The two families are introduced, guided by the MC in two languages',
          'The trays are carried in and the bride’s side takes its share',
          'The rest goes back to the groom’s side, still in an even number'
        ]
      },
      {
        time: '12:00',
        title: 'Photos and the meal',
        items: [
          'Photos of the whole family, then of the couple',
          'Lunch together',
          'The groom’s party takes its leave before evening, as custom asks: no overnight stay'
        ]
      }
    ],
    images: [
      { src: IMAGES.gifts, alt: 'A family procession carrying gifts marked Double Happiness' },
      { src: IMAGES.trays, alt: 'Red trays of gifts marked with the Double Happiness character' },
      { src: IMAGES.embrace, alt: 'A bride in red embraced by her mother' }
    ]
  },
  trays: {
    eyebrow: 'On the trays',
    title: 'Twelve trays, and what each one means',
    lead: 'This is the list people ask about before they contact any vendor, so we publish it. Every family has its own version; our coordinator confirms the final list with both families before the day.',
    items: [
      {
        name: 'Milk-money angpao (uang susu)',
        meaning: 'A thank-you to the bride’s parents for raising her. Placed in two separate red envelopes.'
      },
      {
        name: 'Banquet-money angpao (uang pesta)',
        meaning: 'The groom’s side’s contribution towards the bride’s side’s reception.'
      },
      {
        name: 'Gold jewellery',
        meaning: 'A necklace, bracelet or ring for the bride-to-be. Usually put on her that same day.'
      },
      {
        name: 'Fabric or clothing',
        meaning: 'Dress fabric, a cheongsam or a full outfit for the bride-to-be.'
      },
      {
        name: 'Red kue mangkok (steamed cups)',
        meaning: 'Eighteen pieces. They stand for fortune that rises and overflows.'
      },
      {
        name: 'Lapis legit or kue keranjang',
        meaning: 'The layers stand for fortune that keeps building, and the stickiness for a bond that holds.'
      },
      {
        name: 'Fruit',
        meaning: 'Apples, pears, oranges or grapes, always an even number. A sign of happiness and prosperity.'
      },
      {
        name: 'Two bottles of wine or champagne',
        meaning: 'Opened together as a sign that both families give their blessing.'
      },
      {
        name: 'Pork knuckle or canned meat',
        meaning: 'Twelve cans, an even number. Can be swapped if the family does not eat it.'
      },
      {
        name: 'A pair of red candles',
        meaning: 'Painted with a dragon and a phoenix, the emblem of husband and wife.'
      },
      {
        name: 'Canned longan and lychee',
        meaning: 'A wish for children to come soon and the family to keep growing.'
      },
      {
        name: 'A pair of chickens or ducks',
        meaning: 'Used by some families as a symbol of faithfulness. Not required.'
      }
    ]
  },
  customs: {
    eyebrow: 'Easy to get wrong',
    title: 'Four rules that cause the most misunderstandings',
    items: [
      {
        title: 'The count must be even',
        copy: 'Eight, twelve, sixteen or eighteen trays. Four is never used, because it sounds close to the word for "death".'
      },
      {
        title: 'Not everything is kept',
        copy: 'The bride’s side keeps part of what is on the trays and returns the rest to the groom’s side, and what goes back must still be an even number.'
      },
      {
        title: 'The milk money carries a message',
        copy: 'How much the bride’s family keeps says something of its own, and the convention differs between families. Our coordinator asks both sides well before the day, so nobody misreads the intent.'
      },
      {
        title: 'In the morning, gone before evening',
        copy: 'A sangjit usually runs from 10:00 to 13:00, one week to one month before the wedding. The groom’s party leaves before nightfall.'
      }
    ]
  },
  steps: {
    eyebrow: 'How we work',
    title: 'Four steps, and two of them are ours',
    items: [
      {
        title: 'Tell us the plan',
        copy: 'The date, the place and roughly how many people. Five minutes on WhatsApp is enough to start.',
        when: 'Day 1'
      },
      {
        title: 'We send a quote',
        copy: 'With a decoration sketch, the tray list and an hour-by-hour run of the day, not just a price list.',
        when: '2 working days'
      },
      {
        title: 'We meet both families',
        copy: 'This is the part that decides everything. We agree one version of the customs with both families before anything is booked.',
        when: 'Once you agree'
      },
      {
        title: 'On the day, you just turn up',
        copy: 'The team arrives at eight in the morning. Your parents come as hosts, not as organisers.',
        when: 'The day itself'
      }
    ]
  },
  faqTitle: 'The questions we hear most',
  faqs: [
    {
      q: 'How many trays should we prepare?',
      a: 'Twelve is the most common number in Jakarta, and what we suggest when the family has no rule of its own. Eight for a simpler occasion, sixteen or eighteen for a large family. What matters is that it is even, and not four.'
    },
    {
      q: 'When should the sangjit be held?',
      a: 'Usually one week to one month before the wedding, in the morning from about 10:00 to 13:00. Some families choose the date by the Chinese calendar; if yours does, tell us early so we can hold the team for that date.'
    },
    {
      q: 'Our family no longer keeps this custom. Do we still need it?',
      a: 'Many of our clients come to us with exactly that sentence, usually because one side of the family still wants it and the other no longer knows the order. We often run a shorter version: the trays stay, the ceremony stays, but it takes less time. What we make sure of is that no side feels the occasion was quietly cut down.'
    },
    {
      q: 'Does 7Magic supply what goes on the trays too?',
      a: 'The trays, the arrangement and everything not to do with money, yes. Gold jewellery, the angpao and the milk money are prepared by the family; we prepare the envelopes, write the characters on them and place them as custom requires.'
    },
    {
      q: 'Can it be held at a restaurant or hotel instead of at home?',
      a: 'Yes, and more and more families do, because lunch can follow straight after. We coordinate with the restaurant on the room, the set-up time for the decoration and the table plan. If you do not have a venue yet, we help you find one.'
    },
    {
      q: 'One of our families is not Chinese. How does that work?',
      a: 'It happens often, and that is where a coordinator helps most. We write a short guide for the family that is new to it: what will happen, what it means and what they need to do. Our MC also explains each step as it happens, so no guest is left wondering what to do.'
    },
    {
      q: 'How long does it take?',
      a: 'The ceremony itself takes about an hour and a half. With lunch, three to four hours in all. Our team is on site from eight in the morning to set up.'
    },
    {
      q: 'Can it be combined with the lamaran?',
      a: 'Yes, and quite a few families combine the two to save time and cost. We shape the run of the day so the two ceremonies do not feel like they overlap.'
    }
  ],
  form: {
    title: 'Tell us your plan',
    lead: 'Four answers are enough to start. We reply within two working days with a decoration sketch, the tray list and an hour-by-hour run of the day.',
    chatPrompt: 'Rather talk it through?',
    doneTitle: 'We have it',
    doneCopy:
      'Your quote arrives within two working days. If your date is sooner than that, message us on WhatsApp and tell us the date.',
    chatNow: 'Chat now',
    date: 'Sangjit date',
    dateHint: '(roughly is fine)',
    venue: 'Venue',
    choose: 'Choose one',
    venueOptions: ['At home', 'Restaurant', 'Hotel or hall', 'Not decided yet, please help'],
    guests: 'Roughly how many guests',
    guestsPlaceholder: 'e.g. 40',
    package: 'Package you are interested in',
    packageNone: 'Not sure yet',
    packageOptions: [...PACKAGE_NAMES, 'Not sure, please advise'],
    name: 'Your name',
    phone: 'WhatsApp number',
    email: 'Email',
    optional: '(optional)',
    notes: 'Anything we should know?',
    notesPlaceholder: 'The family wants 16 trays, combined with the lamaran, an aunt would love a lion dance…',
    sending: 'Sending…',
    submit: 'Send & ask for a quote',
    privacy: 'We use this only to put together your sangjit quote. Nothing else.',
    error: "Your message didn't go through. Try again, or message us on WhatsApp directly."
  },
  lead: {
    heading: 'LEAD: Sangjit Package',
    language: 'Language',
    date: 'Sangjit date',
    venue: 'Venue',
    guests: 'Estimated guests',
    package: 'Package of interest',
    none: '—',
    noNotes: 'No additional notes.'
  }
};

export function sangjitCopy(locale: Locale): SangjitCopy {
  return locale === 'en' ? en : id;
}
