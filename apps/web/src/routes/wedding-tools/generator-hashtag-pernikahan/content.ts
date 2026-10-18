/**
 * Copy for the wedding hashtag generator, in both languages.
 *
 * Laid out like the mahar page's `content.ts`: the explainer, example and FAQ
 * are one argument edited as a whole; the chrome every tool shares (the gate,
 * "Gratis") is in the Paraglide catalogue.
 *
 * Indonesian is the source of truth. The tags themselves are not translated:
 * couples here mix Indonesian and English hashtags, so both editions show
 * both, and only the labels around them change.
 *
 * No statistics and no Instagram limits on purpose: hashtag rules and counts
 * change, and this page should not go stale. The advice is practical, and the
 * example couple is fictional, so there is nothing here that needs a source.
 */

import type { Locale } from '$lib/paraglide/runtime';
import type { HashtagEvent, HashtagGroupId } from '$lib/tools/hashtag';
import type { HashtagCardCopy } from '$lib/components/tools/HashtagCard.svelte';

export type Faq = { q: string; a: string };
export type ExplainerSection = { title: string; paragraphs: string[] };
export type RelatedLink = { href: string; title: string };

export type HashtagCopy = {
  meta: { title: string; description: string; keywords: string };
  appName: string;
  hero: { eyebrow: string; title: string; lead: string };
  form: {
    namesLegend: string;
    groomLabel: string;
    brideLabel: string;
    groomPlaceholder: string;
    bridePlaceholder: string;
    namesHint: string;
    orderLegend: string;
    extrasLegend: string;
    optional: string;
    familyLabel: string;
    familyPlaceholder: string;
    familyHint: string;
    dateLabel: string;
    datePlaceholder: string;
    cityLabel: string;
    cityPlaceholder: string;
    eventsLegend: string;
    events: Record<HashtagEvent, string>;
  };
  result: {
    title: string;
    empty: string;
    emptyTag: string;
    copy: string;
    copied: string;
    copyAll: string;
    copiedAll: string;
    count: (count: number) => string;
    check: string;
    longNote: string;
    pickHint: string;
    groups: Record<HashtagGroupId, { title: string; hint: string }>;
    copyFailed: string;
  };
  card: HashtagCardCopy & {
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
    gateTitle: string;
    gateDescription: string;
  };
  explainer: { title: string; lead: string; sections: ExplainerSection[] };
  example: {
    title: string;
    lead: string;
    badge: string;
    couple: string;
    groom: string;
    bride: string;
    date: string;
    city: string;
    events: HashtagEvent[];
    tryIt: string;
  };
  faqs: Faq[];
  related: RelatedLink[];
};

/** Shared by both locales: a fictional couple, so the example needs no source. */
const EXAMPLE = {
  groom: 'Raka',
  bride: 'Nadia',
  date: '2026-09-20',
  city: 'Bandung',
  events: ['lamaran', 'akad', 'resepsi'] as HashtagEvent[]
};

const id: HashtagCopy = {
  meta: {
    title: 'Generator Hashtag Pernikahan: Ide Hashtag dari Nama Kalian | 7Magic',
    description:
      'Buat hashtag pernikahan dari nama kalian berdua secara gratis: gabungan nama, plesetan bahasa Indonesia dan Inggris, versi tanggal, dan hashtag per acara dari lamaran sampai resepsi.',
    keywords:
      'hashtag pernikahan, generator hashtag pernikahan, hashtag nikah, ide hashtag wedding, wedding hashtag generator, hashtag lamaran, hashtag prewedding'
  },
  appName: 'Generator Hashtag Pernikahan',
  hero: {
    eyebrow: 'Wedding Tools',
    title: 'Generator hashtag pernikahan dari nama kalian',
    lead: 'Tulis nama panggilan berdua, lalu pilih hashtag yang paling terasa kalian: gabungan nama, plesetan, versi tanggal, sampai hashtag untuk tiap acara. Salin dengan satu klik.'
  },
  form: {
    namesLegend: 'Nama panggilan',
    groomLabel: 'Pengantin pria',
    brideLabel: 'Pengantin wanita',
    groomPlaceholder: 'Raka',
    bridePlaceholder: 'Nadia',
    namesHint: 'Pakai nama yang dipanggil teman-teman, bukan nama lengkap di KTP.',
    orderLegend: 'Nama siapa duluan',
    extrasLegend: 'Biar lebih personal',
    optional: 'opsional',
    familyLabel: 'Nama keluarga',
    familyPlaceholder: 'Wijaya',
    familyHint: 'Untuk #HappilyEver… dan #MrAndMrs….',
    dateLabel: 'Tanggal pernikahan',
    datePlaceholder: 'Pilih tanggal',
    cityLabel: 'Kota atau lokasi',
    cityPlaceholder: 'Bali',
    eventsLegend: 'Acara yang butuh hashtag sendiri',
    events: {
      lamaran: 'Lamaran',
      prewedding: 'Prewedding',
      sangjit: 'Sangjit',
      akad: 'Akad',
      pemberkatan: 'Pemberkatan',
      resepsi: 'Resepsi'
    }
  },
  result: {
    title: 'Hashtag pilihan kalian',
    empty: 'Isi nama panggilan berdua untuk melihat ide hashtag.',
    emptyTag: '#NamaKalian',
    copy: 'Salin',
    copied: 'Tersalin',
    copyAll: 'Salin semua',
    copiedAll: 'Semua tersalin',
    count: (count) => `${count} ide hashtag`,
    check: 'Cek di Instagram',
    longNote: 'Agak panjang: tamu lebih mudah salah ketik. Pertimbangkan versi yang lebih pendek.',
    pickHint: 'Ketuk hashtag mana pun untuk menjadikannya pilihan utama dan memasangnya di kartu.',
    groups: {
      classic: { title: 'Nama berdua', hint: 'Paling mudah diingat tamu.' },
      blend: { title: 'Gabungan nama', hint: 'Potongan nama kalian, dijadikan satu.' },
      indonesian: { title: 'Plesetan Indonesia', hint: 'Akrab dan sedikit jenaka.' },
      english: { title: 'Gaya Inggris', hint: 'Untuk feed yang campur bahasa.' },
      date: { title: 'Dengan tanggal', hint: 'Membuat hashtag lebih unik.' },
      events: { title: 'Per acara dan lokasi', hint: 'Supaya foto tiap acara mudah dicari.' }
    },
    copyFailed: 'Browser menolak menyalin. Tekan lama hashtag-nya untuk menyalin manual.'
  },
  card: {
    title: 'Kartu hashtag',
    lead: 'Untuk diunggah sebagai pengumuman, atau dicetak A5 dan dipajang di meja tamu.',
    lockedTitle: 'Kartu siap dibuka',
    lockedCopy: 'Gratis. Isi email dan WhatsApp sekali, lalu unduh PNG atau cetak A5.',
    unlock: 'Buka gratis',
    downloadPng: 'Unduh PNG',
    print: 'Cetak A5',
    exporting: 'Menyiapkan...',
    exportError: 'Kartu belum berhasil dibuat. Coba lagi, atau pakai tombol cetak.',
    unlockedNote: 'Ganti hashtag di atas kapan saja; kartunya ikut berubah.',
    gateTitle: 'Buka kartu hashtag',
    gateDescription:
      'Isi email dan WhatsApp sekali untuk mengunduh kartu ini. Tim 7Magic bisa membantu jika kalian butuh venue atau vendor.',
    fallbackTitle: 'Hari Bahagia Kami',
    kicker: 'BAGIKAN MOMEN KAMI',
    invite: 'Unggah foto dan video hari ini dengan',
    emptyTag: '#NamaKalian'
  },
  explainer: {
    title: 'Memilih hashtag pernikahan yang dipakai tamu',
    lead: 'Hashtag yang baik bukan yang paling lucu, tetapi yang benar-benar diketik tamu. Beberapa hal yang membantu.',
    sections: [
      {
        title: 'Kenapa perlu hashtag sendiri',
        paragraphs: [
          'Di hari pernikahan, foto terbaik sering ada di ponsel tamu, bukan di kamera fotografer. Hashtag yang sama untuk semua orang membuat foto dan video itu terkumpul di satu tempat, dan kalian bisa membukanya lagi bertahun-tahun kemudian.',
          'Banyak pasangan mulai memakainya sejak lamaran atau sesi prewedding, sehingga seluruh cerita menuju hari H ikut terkumpul.'
        ]
      },
      {
        title: 'Pendek, mudah dieja, mudah diucapkan',
        paragraphs: [
          'Tamu biasanya mengetik hashtag dari papan di meja tamu atau dari ucapan MC. Semakin pendek dan semakin jelas ejaannya, semakin sedikit yang salah ketik. Alat ini menandai hashtag yang lebih dari 24 huruf.',
          'Huruf besar hanya membantu membaca; Instagram memperlakukan #RakaNadia dan #rakanadia sebagai hashtag yang sama. Coba tulis pilihan kalian dengan huruf kecil semua, lalu minta teman membacanya. Kalau terbaca janggal, pilih yang lain.'
        ]
      },
      {
        title: 'Cek dulu sebelum dicetak',
        paragraphs: [
          'Nama yang umum bisa saja sudah dipakai pasangan lain. Klik "Cek di Instagram" untuk membuka halaman hashtag tersebut. Kalau sudah ramai, tambahkan tahun atau tanggal, atau pakai versi gabungan nama.'
        ]
      },
      {
        title: 'Di mana memasangnya',
        paragraphs: [
          'Tulis di undangan cetak maupun undangan digital, di bio Instagram kalian selama masa persiapan, di papan sambutan, di meja tamu, dan di layar saat resepsi. Titipkan juga ke MC supaya diumumkan sekali atau dua kali.',
          'Kalau ada beberapa acara, satu hashtag utama untuk semuanya sudah cukup. Versi per acara (#…Lamaran, #…Resepsi) membantu jika kalian ingin foto tiap acara terpisah.'
        ]
      }
    ]
  },
  example: {
    title: 'Contoh: Raka dan Nadia',
    lead: 'Pasangan fiktif yang menikah di Bandung, dengan lamaran, akad, dan resepsi. Beberapa hashtag yang dihasilkan alat ini untuk mereka:',
    badge: 'Contoh fiktif',
    couple: 'Raka & Nadia',
    ...EXAMPLE,
    tryIt: 'Coba contoh ini'
  },
  faqs: [
    {
      q: 'Kapan hashtag pernikahan sebaiknya mulai dipakai?',
      a: 'Sejak lamaran atau sesi prewedding. Dengan begitu unggahan selama persiapan sudah terkumpul di hashtag yang sama, dan tamu sudah akrab dengannya saat hari H.'
    },
    {
      q: 'Perlu satu hashtag atau beberapa?',
      a: 'Satu hashtag utama untuk semua acara sudah cukup dan paling mudah diingat. Jika ingin, tambahkan versi per acara seperti #RakaNadiaLamaran atau #RakaNadiaResepsi agar foto tiap acara mudah dicari.'
    },
    {
      q: 'Bagaimana tahu hashtag kami sudah dipakai orang lain?',
      a: 'Alat ini tidak bisa memeriksanya otomatis. Klik "Cek di Instagram" pada hashtag pilihan kalian untuk membuka halamannya. Jika sudah ada unggahan pasangan lain, tambahkan tahun, tanggal, atau pilih versi gabungan nama.'
    },
    {
      q: 'Apakah huruf besar dan kecil berpengaruh?',
      a: 'Tidak untuk pencarian. Huruf besar di awal tiap kata hanya membuat hashtag lebih mudah dibaca, terutama di papan dan undangan.'
    },
    {
      q: 'Boleh memakai spasi, tanda hubung, atau huruf beraksen?',
      a: 'Sebaiknya tidak, karena hashtag akan terpotong di karakter tersebut. Alat ini sudah membuang spasi, tanda baca, dan aksen, sehingga setiap hashtag hanya berisi huruf dan angka.'
    },
    {
      q: 'Pakai bahasa Indonesia atau Inggris?',
      a: 'Bebas. Pilih yang terdengar seperti kalian berdua. Yang terpenting, hashtag itu mudah diucapkan MC dan mudah diketik tamu.'
    },
    {
      q: 'Apakah kartu hashtagnya gratis?',
      a: 'Gratis. Kami hanya meminta email dan nomor WhatsApp sekali, lalu kartu bisa diunduh sebagai PNG atau dicetak ukuran A5.'
    }
  ],
  related: [
    {
      href: '/artikel/wedding-preparation/undangan-pernikahan-digital-4-alasan-kenapa-lebih-hemat-stylish-dan-ramah-lingkungan',
      title: 'Undangan Pernikahan Digital: 4 Alasan Kenapa Lebih Hemat, Stylish, dan Ramah Lingkungan'
    },
    {
      href: '/artikel/wedding-preparation/wedding-content-creator-tren-pernikahan-kekinian-biar-momenmu-terekam-dengan-aesthetic',
      title: 'Wedding Content Creator: Tren Pernikahan Kekinian Biar Momenmu Terekam dengan Aesthetic'
    },
    {
      href: '/artikel/photography/sepuluh-gaya-fotografi-pernikahan',
      title: 'Sepuluh Gaya Fotografi Pernikahan dan Cara Memilih yang Cocok untuk Anda'
    }
  ]
};

const en: HashtagCopy = {
  meta: {
    title: 'Wedding Hashtag Generator: Hashtag Ideas from Your Names | 7Magic',
    description:
      'Make a wedding hashtag from both your names, free: name pairs, Indonesian and English wordplay, date versions, and a hashtag for every event from the lamaran to the reception.',
    keywords:
      'wedding hashtag generator, wedding hashtag ideas, hashtag pernikahan, couple hashtag, engagement hashtag, prewedding hashtag'
  },
  appName: 'Wedding Hashtag Generator',
  hero: {
    eyebrow: 'Wedding Tools',
    title: 'A wedding hashtag generator for your names',
    lead: 'Type the names you both go by, then pick the hashtag that feels most like you: name pairs, blends, wordplay, date versions and a tag for each event. Copy it in one tap.'
  },
  form: {
    namesLegend: 'The names you go by',
    groomLabel: 'Groom',
    brideLabel: 'Bride',
    groomPlaceholder: 'Raka',
    bridePlaceholder: 'Nadia',
    namesHint: 'Use the names your friends call you, not the full names on your ID.',
    orderLegend: 'Whose name comes first',
    extrasLegend: 'Make it more personal',
    optional: 'optional',
    familyLabel: 'Family name',
    familyPlaceholder: 'Wijaya',
    familyHint: 'For #HappilyEver… and #MrAndMrs….',
    dateLabel: 'Wedding date',
    datePlaceholder: 'Pick a date',
    cityLabel: 'City or venue area',
    cityPlaceholder: 'Bali',
    eventsLegend: 'Events that need their own hashtag',
    events: {
      lamaran: 'Lamaran (proposal)',
      prewedding: 'Prewedding',
      sangjit: 'Sangjit',
      akad: 'Akad',
      pemberkatan: 'Church blessing',
      resepsi: 'Reception'
    }
  },
  result: {
    title: 'Your hashtag',
    empty: 'Fill in both your names to see hashtag ideas.',
    emptyTag: '#YourNames',
    copy: 'Copy',
    copied: 'Copied',
    copyAll: 'Copy all',
    copiedAll: 'All copied',
    count: (count) => `${count} hashtag ideas`,
    check: 'Check on Instagram',
    longNote: 'On the long side: guests are more likely to mistype it. Consider a shorter one.',
    pickHint: 'Tap any hashtag to make it your pick and put it on the card.',
    groups: {
      classic: { title: 'Both names', hint: 'The easiest for guests to remember.' },
      blend: { title: 'Name blends', hint: 'Pieces of your names, made into one.' },
      indonesian: { title: 'Indonesian wordplay', hint: 'Familiar and a little playful.' },
      english: { title: 'English style', hint: 'For a feed that mixes languages.' },
      date: { title: 'With the date', hint: 'Makes a hashtag more unique.' },
      events: { title: 'Per event and place', hint: 'So each event’s photos are easy to find.' }
    },
    copyFailed: 'Your browser blocked copying. Long-press the hashtag to copy it by hand.'
  },
  card: {
    title: 'Hashtag card',
    lead: 'Post it as an announcement, or print it at A5 for the guest-book table.',
    lockedTitle: 'Your card is ready',
    lockedCopy: 'Free. Enter your email and WhatsApp once, then download the PNG or print at A5.',
    unlock: 'Unlock for free',
    downloadPng: 'Download PNG',
    print: 'Print A5',
    exporting: 'Preparing...',
    exportError: 'The card could not be made. Try again, or use the print button.',
    unlockedNote: 'Change the hashtag above any time; the card follows.',
    gateTitle: 'Unlock the hashtag card',
    gateDescription:
      'Enter your email and WhatsApp once to download this card. The 7Magic team can help if you need a venue or vendors.',
    fallbackTitle: 'Our Wedding Day',
    kicker: 'SHARE THE MOMENT',
    invite: 'Post your photos and videos with',
    emptyTag: '#YourNames'
  },
  explainer: {
    title: 'Choosing a wedding hashtag guests will actually use',
    lead: 'A good hashtag is not the cleverest one, it is the one guests really type. A few things that help.',
    sections: [
      {
        title: 'Why have a hashtag of your own',
        paragraphs: [
          'On the day, many of the best photos are on guests’ phones, not in the photographer’s camera. One hashtag for everyone gathers those photos and videos in one place, and you can open it again years later.',
          'Many couples start using it from the lamaran or the prewedding shoot, so the whole story leading up to the day is collected too.'
        ]
      },
      {
        title: 'Short, easy to spell, easy to say',
        paragraphs: [
          'Guests usually type a hashtag from the sign on the guest-book table or from what the MC says. The shorter it is and the clearer the spelling, the fewer typos. This tool flags any hashtag longer than 24 letters.',
          'Capitals only help reading; Instagram treats #RakaNadia and #rakanadia as the same hashtag. Write your pick all in lower case and ask a friend to read it. If it reads oddly, choose another.'
        ]
      },
      {
        title: 'Check before you print',
        paragraphs: [
          'A common name may already be in use by another couple. Click "Check on Instagram" to open that hashtag’s page. If it is busy, add the year or the date, or use a name blend.'
        ]
      },
      {
        title: 'Where to put it',
        paragraphs: [
          'Put it on the printed and the digital invitation, in your Instagram bio while you plan, on the welcome sign, on the guest-book table and on the screen at the reception. Ask the MC to mention it once or twice.',
          'With several events, one main hashtag for all of them is enough. Per-event versions (#…Lamaran, #…Resepsi) help if you want each event’s photos kept apart.'
        ]
      }
    ]
  },
  example: {
    title: 'Example: Raka and Nadia',
    lead: 'A fictional couple marrying in Bandung, with a lamaran, an akad and a reception. Some of the hashtags this tool makes for them:',
    badge: 'Fictional example',
    couple: 'Raka & Nadia',
    ...EXAMPLE,
    tryIt: 'Try this example'
  },
  faqs: [
    {
      q: 'When should we start using our wedding hashtag?',
      a: 'From the lamaran or the prewedding shoot. That way posts made while you plan are already gathered under it, and guests know it by the day itself.'
    },
    {
      q: 'Do we need one hashtag or several?',
      a: 'One main hashtag for every event is enough and the easiest to remember. If you like, add per-event versions such as #RakaNadiaLamaran or #RakaNadiaResepsi so each event’s photos are easy to find.'
    },
    {
      q: 'How do we know whether our hashtag is already taken?',
      a: 'This tool cannot check that automatically. Click "Check on Instagram" on your pick to open its page. If another couple has posts there, add the year or the date, or pick a name blend.'
    },
    {
      q: 'Do capital letters matter?',
      a: 'Not for search. A capital at the start of each word only makes the hashtag easier to read, especially on signs and invitations.'
    },
    {
      q: 'Can we use spaces, hyphens or accented letters?',
      a: 'Better not, since the hashtag stops at those characters. This tool already removes spaces, punctuation and accents, so every hashtag holds only letters and digits.'
    },
    {
      q: 'Indonesian or English?',
      a: 'Either. Pick what sounds like the two of you. What matters most is that the MC can say it and guests can type it.'
    },
    {
      q: 'Is the hashtag card free?',
      a: 'Yes. We only ask for your email and WhatsApp number once, then you can download the card as a PNG or print it at A5.'
    }
  ],
  related: [
    {
      href: '/en/articles/wedding-preparation/digital-wedding-invitations-4-reasons-they-re-cheaper-more-stylish-and-kinder-to-the-planet',
      title: "Digital Wedding Invitations: 4 Reasons They're Cheaper, More Stylish and Kinder to the Planet"
    },
    {
      href: '/en/articles/wedding-preparation/wedding-content-creators-the-trend-that-gets-your-big-day-onto-your-feed-looking-good',
      title: 'Wedding Content Creators: The Trend That Gets Your Big Day Onto Your Feed, Looking Good'
    },
    {
      href: '/en/articles/photography/ten-wedding-photography-styles',
      title: 'Ten Wedding Photography Styles and How to Choose the Right One for You'
    }
  ]
};

const CONTENT: Record<Locale, HashtagCopy> = { id, en };

export function hashtagCopy(locale: Locale): HashtagCopy {
  return CONTENT[locale] ?? CONTENT.id;
}

export const TOOL_PATH = '/wedding-tools/generator-hashtag-pernikahan';
