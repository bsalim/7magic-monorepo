/**
 * Copy for the Jabodetabek wedding page, in both languages.
 *
 * Indonesian is the source of truth; the English is a translation of the same
 * page, not a different offer. Only facts already published on this site or
 * supplied by 7Magic belong here: "more than 100 venues" is 7Magic's own figure
 * (2026-10-08), covering partner venues outside the catalogue. City counts and
 * "from" prices are computed from the catalogue on each load, never typed.
 */

import type { Locale } from '$lib/paraglide/runtime';

export type Point = { title: string; copy: string };
export type Reading = { href: string; title: string };

export type JabodetabekCopy = {
  meta: { title: string; description: string };
  breadcrumb: string;
  whatsappPrefill: string;
  hero: { alt: string; eyebrow: string; title: string; lead: string; whatsapp: string };
  cities: {
    eyebrow: string;
    title: string;
    lead: string;
    cardTitle: (city: string) => string;
    venues: (count: number) => string;
    upTo: (guests: string) => string;
    from: string;
    cta: (city: string) => string;
    /** For guest counts and the "juta"/"million" unit on the price. */
    numberLocale: string;
    millions: string;
  };
  how: { title: string; points: Point[] };
  servicesTitle: string;
  readingTitle: string;
  reading: Reading[];
  closing: { title: string; office: string };
};

const id: JabodetabekCopy = {
  meta: {
    title: 'Wedding Jabodetabek: Venue di Jakarta, Tangerang, Bogor & Bekasi | 7Magic',
    description:
      'Pilih venue pernikahan di Jakarta, Tangerang, Bogor, dan Bekasi dengan harga yang terbuka, lalu kunjungi venuenya gratis bersama tim 7Magic. Kantor kami di Jalan Gajah Mada, Jakarta.'
  },
  breadcrumb: 'Wedding Jabodetabek',
  whatsappPrefill: 'Halo 7Magic, saya ingin konsultasi pernikahan di Jabodetabek.',
  hero: {
    alt: 'Bundaran HI, Jakarta, dilihat dari udara saat senja',
    eyebrow: 'Wedding · Jabodetabek',
    title: 'Menikah di Jakarta dan sekitarnya',
    lead: 'Lebih dari 100 venue di Jabodetabek. Bandingkan harga paketnya, pilih yang cocok, lalu datangi langsung bersama tim kami sebelum Anda memutuskan.',
    whatsapp: 'Tanya lewat WhatsApp'
  },
  cities: {
    eyebrow: 'Venue per kota',
    title: 'Mulai dari kota tempat tamu Anda tinggal',
    lead: 'Setiap kota punya halaman sendiri berisi semua venuenya, diurutkan menurut harga dan bintang hotel. Harga yang tertera adalah harga paket mulai dari, sesuai katalog kami hari ini.',
    cardTitle: (city) => `Wedding di ${city}`,
    venues: (count) => `${count} venue`,
    upTo: (guests) => `, hingga ${guests} tamu`,
    from: 'Mulai',
    cta: (city) => `Lihat venue di ${city}`,
    numberLocale: 'id-ID',
    millions: 'juta'
  },
  how: {
    title: 'Dari daftar venue sampai berdiri di ballroom-nya',
    points: [
      {
        title: 'Bandingkan dengan harga terbuka',
        copy: 'Harga paket setiap venue tampil di katalog, jadi Anda bisa menyaring sesuai anggaran sebelum menghubungi siapa pun.'
      },
      {
        title: 'Kunjungi venuenya, gratis',
        copy: 'Pilih venue yang ingin Anda lihat dan hari yang cocok. Kunjungannya gratis dan tidak mengikat apa pun.'
      },
      {
        title: 'Bicara dengan tim di Jakarta',
        copy: 'Minta penawaran untuk venue pilihan Anda lewat WhatsApp, atau datang ke kantor kami di Jalan Gajah Mada.'
      }
    ]
  },
  servicesTitle: 'Layanan kami di Jabodetabek',
  readingTitle: 'Bacaan sebelum memilih',
  reading: [
    {
      href: '/artikel/wedding-venue/masjid-gedung-favorit-jabodetabek-akad-nikah',
      title: 'Masjid dan Gedung Favorit di Jabodetabek untuk Akad Nikah'
    },
    {
      href: '/artikel/wedding-venue/intimate-wedding-100-tamu-jakarta-rincian-biaya',
      title: 'Intimate Wedding 100 Tamu di Jakarta: Rincian Biaya dan Cara Menekannya'
    },
    {
      href: '/artikel/wedding-preparation/syarat-dokumen-nikah-2026-kua-catatan-sipil',
      title: 'Syarat dan Dokumen Nikah 2026: Alur Lengkap di KUA dan Catatan Sipil'
    }
  ],
  closing: {
    title: 'Mulai dengan satu kunjungan',
    office: 'Kantor 7Magic: Jalan Gajah Mada No. 10, Jakarta 10130'
  }
};

const en: JabodetabekCopy = {
  meta: {
    title: 'Weddings in Jabodetabek: Venues in Jakarta, Tangerang, Bogor & Bekasi | 7Magic',
    description:
      'Choose a wedding venue in Jakarta, Tangerang, Bogor or Bekasi with prices shown up front, then visit it free with the 7Magic team. Our office is on Jalan Gajah Mada, Jakarta.'
  },
  breadcrumb: 'Weddings in Jabodetabek',
  whatsappPrefill: "Hi 7Magic, I'd like to talk about a wedding in Jabodetabek.",
  hero: {
    alt: 'An aerial view of Bundaran HI, Jakarta, at dusk',
    eyebrow: 'Weddings · Jabodetabek',
    title: 'Getting married in Jakarta and around it',
    lead: 'More than 100 venues across Jabodetabek. Compare their package prices, pick the ones that fit, then visit them with our team before you decide.',
    whatsapp: 'Ask on WhatsApp'
  },
  cities: {
    eyebrow: 'Venues by city',
    title: 'Start with the city your guests live in',
    lead: 'Each city has its own page with all its venues, sorted by price and hotel star rating. The prices shown are package starting prices from our catalogue today.',
    cardTitle: (city) => `Weddings in ${city}`,
    venues: (count) => `${count} ${count === 1 ? 'venue' : 'venues'}`,
    upTo: (guests) => `, up to ${guests} guests`,
    from: 'From',
    cta: (city) => `See venues in ${city}`,
    numberLocale: 'en-US',
    millions: 'million'
  },
  how: {
    title: 'From a list of venues to standing in the ballroom',
    points: [
      {
        title: 'Compare with prices up front',
        copy: "Every venue's package price is in the catalogue, so you can filter by budget before you contact anyone."
      },
      {
        title: 'Visit the venue, free',
        copy: "Choose the venues you want to see and a day that suits you. The visit is free and commits you to nothing."
      },
      {
        title: 'Talk to the team in Jakarta',
        copy: 'Ask for a quote on the venues you like over WhatsApp, or come to our office on Jalan Gajah Mada.'
      }
    ]
  },
  servicesTitle: 'Our services in Jabodetabek',
  readingTitle: 'Worth reading before you choose',
  reading: [
    {
      href: '/en/articles/wedding-venue/favorite-akad-venues-in-jabodetabek',
      title: 'Favorite Mosques and Halls in Jabodetabek for the Akad Nikah Ceremony'
    },
    {
      href: '/en/articles/wedding-venue/100-guest-intimate-wedding-in-jakarta',
      title: '100-Guest Intimate Wedding in Jakarta: Cost Breakdown and How to Cut It'
    },
    {
      href: '/en/articles/wedding-preparation/marriage-documents-2026',
      title: 'Marriage Requirements and Documents 2026: The Full KUA and Civil Registry Process'
    }
  ],
  closing: {
    title: 'Start with one visit',
    office: '7Magic office: Jalan Gajah Mada No. 10, Jakarta 10130'
  }
};

export function jabodetabekCopy(locale: Locale): JabodetabekCopy {
  return locale === 'en' ? en : id;
}
