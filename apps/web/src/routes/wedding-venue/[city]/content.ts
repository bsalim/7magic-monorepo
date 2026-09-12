/**
 * Copy for the city hub's prose, price table and FAQ, in both languages.
 *
 * One locale-keyed module rather than Paraglide keys, for the reason the
 * prenup page gives: this is an argument that changes as a whole, not a set of
 * independent UI strings. Unlike that page, nothing here carries a figure of
 * its own -- every number comes from `cityStats`, computed from the catalogue
 * on each request, so the copy cannot go stale or quote a price nobody set.
 *
 * Indonesian is the source of truth; the English is a translation.
 */

import type { Locale } from '$lib/paraglide/runtime';
import type { Faq } from '$lib/seo/schema';
import { formatMillions } from '$lib/utils';
import type { BandKey, CityStats } from '$lib/venue-groups';

export type HubCopy = {
  table: {
    title: string;
    venue: string;
    district: string;
    guests: string;
    price: string;
    priceOnRequest: string;
    guestsFor: (count: number) => string;
    bands: Record<BandKey, string>;
  };
  prose: string[];
  faq: { title: string; items: Faq[]; ctaLabel: string };
};

const UNIT = { id: 'juta', en: 'million' } as const;
const NUMBER_LOCALE = { id: 'id-ID', en: 'en-US' } as const;

/** "a, b dan c" -- an Oxford comma reads as a typo in Indonesian, so none in either. */
function joinList(items: string[], and: string): string {
  if (items.length <= 1) return items.join('');
  return `${items.slice(0, -1).join(', ')} ${and} ${items[items.length - 1]}`;
}

export function hubCopy(locale: Locale, city: string, stats: CityStats): HubCopy {
  const price = (value: number) => formatMillions(value, UNIT[locale]);
  const n = (value: number) => value.toLocaleString(NUMBER_LOCALE[locale]);
  const guestRange =
    stats.guestsMin === null || stats.guestsMax === null
      ? null
      : stats.guestsMin === stats.guestsMax
        ? n(stats.guestsMin)
        : `${n(stats.guestsMin)}–${n(stats.guestsMax)}`;

  if (locale === 'en') {
    const bandPhrase: Record<BandKey, (count: number) => string> = {
      under50: (c) => `${c} ${c === 1 ? 'venue' : 'venues'} under Rp 50 million`,
      '50to100': (c) => `${c} between Rp 50 and 100 million`,
      '100to200': (c) => `${c} between Rp 100 and 200 million`,
      over200: (c) => `${c} at Rp 200 million and above`,
      onRequest: () => ''
    };
    const bands = joinList(
      stats.bands.map(({ band, count }) => bandPhrase[band.key](count)),
      'and'
    );
    const priceSentence =
      stats.floor === null || stats.ceiling === null
        ? ''
        : stats.floor === stats.ceiling
          ? ` Packages start at ${price(stats.floor)}.`
          : ` Starting prices run from ${price(stats.floor)} to ${price(stats.ceiling)}${bands ? `: ${bands}.` : '.'}`;

    return {
      table: {
        title: `Wedding package prices in ${city}`,
        venue: 'Venue',
        district: 'District',
        guests: 'Package for',
        price: 'From',
        priceOnRequest: 'On request',
        guestsFor: (count) => `${n(count)} guests`,
        bands: {
          under50: 'Under Rp 50 million',
          '50to100': 'Rp 50–100 million',
          '100to200': 'Rp 100–200 million',
          over200: 'Rp 200 million and up',
          onRequest: 'Price on request'
        }
      },
      prose: [
        `Wedding packages in ${city} are sold per package for a set number of guests, and starting prices vary widely between venues. Most hotel packages include the ballroom hire and the meal; decoration, the bridal room and the sound system differ from venue to venue, so always check the package details on each venue's page.`,
        `This page lists ${n(stats.count)} ${stats.count === 1 ? 'venue' : 'venues'} in ${city}${stats.districts > 1 ? `, across ${stats.districts} districts` : ''}.${priceSentence}`,
        `We group venues by hotel star rating because that is how most couples narrow a shortlist: five-star for a large reception with international hotel service, four- and three-star for a more measured budget with capacity that is often no smaller. Venues without a hotel rating — halls, restaurants, private spaces — are at the bottom.`,
        guestRange
          ? `The quickest way to filter: settle the guest count first, since the package prices here are calculated for ${guestRange} guests. Then compare venues by price in the table above, and open a venue's page for the package details and gallery.`
          : `The quickest way to filter: settle the guest count first, then compare venues by price in the table above, and open a venue's page for the package details and gallery.`,
        `Once you have two or three candidates, we can arrange a free venue visit — we set the date with the venue, and our team comes along.`
      ],
      faq: {
        title: `Questions about wedding packages in ${city}`,
        ctaLabel: 'Arrange a free venue visit',
        items: [
          {
            q: `How much does a wedding package in ${city} cost?`,
            a:
              stats.floor === null || stats.ceiling === null
                ? `The venues in ${city} price on request. Contact us with your date and guest count and we will send a written quote.`
                : `Across the ${n(stats.count)} venues on this page, the cheapest package starts at ${price(stats.floor)} and the highest starting price is ${price(stats.ceiling)}${bands ? `: ${bands}` : ''}. These are starting prices per package for the stated guest count, before extra guests or a menu upgrade.`
          },
          {
            q: 'What is usually included in a package?',
            a: `Almost every hotel package includes the ballroom hire and the meal for the stated number of guests. Decoration, the bridal room, the sound system and whether outside vendors are allowed differ per venue, and the details are always written on the venue's page.`
          },
          {
            q: 'How many guests can a venue take?',
            a: guestRange
              ? `Package prices in ${city} are calculated for ${guestRange} guests${stats.guestsMin === stats.guestsMax ? '' : ', depending on the venue'}. A ballroom's maximum capacity is usually higher — ask us if your guest list exceeds the package figure.`
              : `Capacity differs per venue — ask us with your approximate guest count and we will tell you which venues fit.`
          },
          {
            q: 'Are the prices here final?',
            a: `These are the venues' starting prices, which can change with the date, the day of the week and the season. We always confirm the formal quote and current price with the venue in writing before you decide.`
          },
          {
            q: 'How do I book a venue through 7Magic?',
            a: `Contact us on WhatsApp or through the contact form with the venue name, an approximate date and your guest count. We check availability, send a written quote and arrange a visit. The consultation and availability check are free.`
          },
          {
            q: 'Can I see the venue before deciding?',
            a: `Yes. Venue visits are free: pick a venue and a date on the tour page, we arrange it with the venue and come along on the visit.`
          }
        ]
      }
    };
  }

  const bandPhrase: Record<BandKey, (count: number) => string> = {
    under50: (c) => `${c} venue di bawah Rp 50 juta`,
    '50to100': (c) => `${c} di kisaran Rp 50–100 juta`,
    '100to200': (c) => `${c} di kisaran Rp 100–200 juta`,
    over200: (c) => `${c} dari Rp 200 juta ke atas`,
    onRequest: () => ''
  };
  const bands = joinList(
    stats.bands.map(({ band, count }) => bandPhrase[band.key](count)),
    'dan'
  );
  const priceSentence =
    stats.floor === null || stats.ceiling === null
      ? ''
      : stats.floor === stats.ceiling
        ? ` Harga paket mulai ${price(stats.floor)}.`
        : ` Harga awal berkisar ${price(stats.floor)} sampai ${price(stats.ceiling)}${bands ? `: ${bands}.` : '.'}`;

  return {
    table: {
      title: `Harga paket wedding ${city}`,
      venue: 'Venue',
      district: 'Wilayah',
      guests: 'Paket untuk',
      price: 'Mulai dari',
      priceOnRequest: 'Sesuai permintaan',
      guestsFor: (count) => `${n(count)} tamu`,
      bands: {
        under50: 'Di bawah Rp 50 juta',
        '50to100': 'Rp 50–100 juta',
        '100to200': 'Rp 100–200 juta',
        over200: 'Rp 200 juta ke atas',
        onRequest: 'Harga sesuai permintaan'
      }
    },
    prose: [
      `Paket wedding di ${city} umumnya dijual per paket untuk jumlah tamu tertentu, dan harga awalnya berbeda jauh antar venue. Sebagian besar paket hotel sudah mencakup sewa ballroom dan menu makan; dekorasi, kamar pengantin, dan sound system berbeda-beda per venue, jadi selalu cek rincian paket di halaman masing-masing.`,
      `Di halaman ini ada ${n(stats.count)} venue di ${city}${stats.districts > 1 ? `, tersebar di ${stats.districts} wilayah` : ''}.${priceSentence}`,
      `Kami mengelompokkan venue menurut bintang hotel karena itu cara kebanyakan pasangan menyaring: bintang lima untuk resepsi besar dengan standar layanan hotel internasional, bintang empat dan tiga untuk anggaran yang lebih terukur dengan kapasitas yang sering tidak kalah. Venue tanpa bintang hotel — gedung, restoran, ruang privat — ada di bagian paling bawah.`,
      guestRange
        ? `Cara paling cepat menyaring: tentukan dulu jumlah tamu, karena harga paket di sini dihitung untuk ${guestRange} tamu. Setelah itu bandingkan harga per venue di tabel di atas, lalu buka halaman venue untuk rincian paket dan galeri.`
        : `Cara paling cepat menyaring: tentukan dulu jumlah tamu, lalu bandingkan harga per venue di tabel di atas, dan buka halaman venue untuk rincian paket dan galeri.`,
      `Kalau sudah ada dua atau tiga kandidat, kami bisa mengatur kunjungan gratis ke venue — tanggalnya kami urus dengan pihak venue, dan tim kami ikut mendampingi.`
    ],
    faq: {
      title: `Pertanyaan seputar paket wedding di ${city}`,
      ctaLabel: 'Atur kunjungan venue gratis',
      items: [
        {
          q: `Berapa harga paket wedding di ${city}?`,
          a:
            stats.floor === null || stats.ceiling === null
              ? `Venue di ${city} memberi harga sesuai permintaan. Hubungi kami dengan tanggal dan jumlah tamu, dan kami kirim penawaran tertulis.`
              : `Dari ${n(stats.count)} venue di halaman ini, harga paket paling murah mulai ${price(stats.floor)} dan harga awal tertinggi ${price(stats.ceiling)}${bands ? `: ${bands}` : ''}. Ini harga awal per paket untuk jumlah tamu yang tertera, belum termasuk penambahan tamu atau upgrade menu.`
        },
        {
          q: 'Apa saja yang biasanya termasuk dalam paket?',
          a: `Hampir semua paket hotel sudah termasuk sewa ballroom dan menu makan untuk jumlah tamu yang tertera. Dekorasi, kamar pengantin, sound system, dan kebebasan membawa vendor luar berbeda per venue, dan rinciannya selalu tertulis di halaman venue.`
        },
        {
          q: 'Berapa kapasitas tamu yang bisa ditampung?',
          a: guestRange
            ? `Harga paket di ${city} dihitung untuk ${guestRange} tamu${stats.guestsMin === stats.guestsMax ? '' : ', tergantung venue'}. Kapasitas maksimal ballroom biasanya lebih besar dari itu — tanyakan ke kami kalau tamu Anda melebihi angka paket.`
            : `Kapasitas berbeda per venue — tanyakan ke kami dengan perkiraan jumlah tamu Anda, dan kami sebutkan venue mana yang cocok.`
        },
        {
          q: 'Apakah harga di sini sudah final?',
          a: `Ini harga awal dari venue, yang bisa berubah mengikuti tanggal, hari, dan musim. Penawaran resmi dan harga terkini selalu kami konfirmasi tertulis ke venue sebelum Anda memutuskan.`
        },
        {
          q: 'Bagaimana cara booking venue lewat 7Magic?',
          a: `Hubungi kami lewat WhatsApp atau formulir kontak dengan nama venue, perkiraan tanggal, dan jumlah tamu. Kami cek ketersediaan, kirim penawaran tertulis, dan atur jadwal kunjungan. Konsultasi dan pengecekan ketersediaan tidak dipungut biaya.`
        },
        {
          q: 'Bisa lihat venue-nya dulu sebelum memutuskan?',
          a: `Bisa. Kunjungan venue gratis: pilih venue dan tanggal di halaman tur, kami atur dengan pihak venue dan ikut mendampingi saat kunjungan.`
        }
      ]
    }
  };
}
