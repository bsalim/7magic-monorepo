/**
 * Copy for the Bali prenuptial agreement landing page, in both languages.
 *
 * A second offer, not a translation of the Jakarta page: the deed is signed
 * before a partner notary based in Bali, because a notary may only act inside
 * the province where they are based (UU Jabatan Notaris, Pasal 17-18). The
 * price differs from Jakarta's, and the audience leans foreign -- couples who
 * marry in Bali from abroad, and expatriates married to an Indonesian who are
 * about to buy property -- so the English page matters more here than it does
 * for Jakarta.
 *
 * What does not depend on the city -- what may and may not be agreed, the
 * documents, the form's questions -- is taken from the Jakarta copy rather than
 * repeated, so a correction there reaches both pages.
 *
 * Indonesian is the source of truth; the English is a translation of the same
 * offer.
 */

import type { Locale } from '$lib/paraglide/runtime';
import type { PrenupCopy } from '$lib/components/prenup/types';
import { prenupCopy } from '../perjanjian-pranikah/content';

/**
 * PENDING -- the Bali all-in price has not been confirmed by 7Magic yet, so the
 * page is priced on request and the JSON-LD carries no Offer. When the figure
 * is confirmed, set it here (written per locale: Indonesian groups thousands
 * with periods, English with commas) and every priced string below switches
 * over. Never fill this with an estimate.
 */
type Price = { id: string; en: string; offer: string };
// `as`, not an annotation: an annotated `const` holding null narrows to `never`
// and every priced branch below stops type-checking.
const PRICE = null as Price | null;

/** The price as a bare number for the JSON-LD Offer, or null while on request. */
export const OFFER_PRICE: string | null = PRICE?.offer ?? null;

/**
 * Same photographs as the Jakarta page, in the same order, so each segment's
 * alt text below must still describe the picture at that index.
 */
export { SEGMENT_IMAGES } from '../perjanjian-pranikah/content';

/**
 * PLACEHOLDER -- deliberately empty, as on the Jakarta page. The Bali partner
 * notary's name and decree come from 7Magic, never from us.
 */
export const NOTARY = { name: '', decree: '', area: '' };

const baseId = prenupCopy('id');
const baseEn = prenupCopy('en');

const id: PrenupCopy = {
  ...baseId,
  price: PRICE?.id ?? 'Dikonfirmasi saat konsultasi',
  priceShort: PRICE?.id ?? '',
  meta: {
    title: PRICE
      ? `Perjanjian Pranikah Bali — ${PRICE.id} All-in, Notaris di Bali | 7Magic`
      : 'Perjanjian Pranikah di Bali — Notaris di Bali, Akta + Pencatatan | 7Magic',
    description:
      'Perjanjian pranikah dan pisah harta di Bali, ditandatangani di hadapan notaris yang berkedudukan di Bali. Termasuk konsultasi, draft, akta notaris, dan pencatatan di Dukcapil atau KUA. Untuk pasangan WNI–WNA dan yang sudah menikah. Konsultasi awal gratis.',
    keywords:
      'perjanjian pranikah bali, notaris perjanjian pranikah bali, perjanjian pisah harta bali, perjanjian perkawinan bali, perjanjian pranikah WNA bali, perjanjian kawin campur bali, notaris denpasar perjanjian kawin, prenup bali'
  },
  hero: {
    ...baseId.hero,
    eyebrow: 'Perjanjian pranikah · Bali',
    title: PRICE
      ? `Perjanjian pranikah di Bali, selesai sampai tercatat — ${PRICE.id}`
      : 'Perjanjian pranikah di Bali, dari konsultasi sampai tercatat',
    lead: 'Konsultasi dan draft bisa dikerjakan dari mana saja. Akta ditandatangani di hadapan notaris mitra kami di Bali, lalu kami catatkan di Dukcapil atau KUA. Bisa juga dibuat setelah Anda menikah.'
  },
  stats: [
    { value: 'Gratis', label: 'Konsultasi awal, lewat WhatsApp' },
    { value: '2 – 3 minggu', label: 'Dari konsultasi sampai tercatat' },
    { value: 'Notaris di Bali', label: 'Akta ditandatangani di Bali' },
    { value: 'Sekali datang', label: 'Hanya saat tanda tangan akta' }
  ],
  price_section: {
    ...baseId.price_section,
    title: 'Apa saja yang termasuk, kami tulis di sini',
    lead: PRICE
      ? 'Satu angka, tanpa tagihan susulan untuk langkah-langkah di bawah. Ini isinya, hitam di atas putih.'
      : 'Harga paket Bali kami sebutkan di konsultasi pertama, sebelum Anda membayar apa pun. Yang sudah pasti adalah isinya, hitam di atas putih.',
    marketNote: '',
    once: PRICE ? 'sekali bayar' : '',
    badge: 'Konsultasi awal gratis'
  },
  // No market comparison: there is no published range of Bali notary fees to
  // cite, and the Jakarta range says nothing about Bali.
  comparison: [],
  included: [
    'Konsultasi awal bersama tim legal kami lewat WhatsApp — bisa sebelum Anda tiba di Bali',
    'Penyusunan draft perjanjian sesuai kondisi aset dan rencana Anda',
    'Dua kali revisi draft tanpa biaya tambahan',
    'Penandatanganan akta di hadapan notaris mitra kami di Bali',
    'Pencatatan ke Dukcapil atau KUA sampai terbit catatan pinggirnya',
    'Salinan akta resmi untuk Anda dan pasangan'
  ],
  excluded: [
    ...baseId.excluded,
    'Perjalanan dan akomodasi Anda ke Bali untuk hari penandatanganan'
  ],
  segmentsIntro: {
    eyebrow: 'Siapa yang biasanya butuh',
    title: 'Empat kondisi yang membuat perjanjian ini penting di Bali'
  },
  segments: [
    {
      title: 'Menikah dengan WNA',
      copy: 'Tanpa pisah harta, tanah yang dibeli selama pernikahan menjadi harta bersama, dan bagian pasangan WNA atas Hak Milik harus dilepas dalam satu tahun. Perjanjian yang tercatat menjaga hak WNI memegang SHM atas nama sendiri.',
      alt: 'Sepasang cincin kawin di dalam kotak'
    },
    {
      title: 'Berencana membeli vila atau tanah',
      copy: 'Banyak pasangan campuran baru memikirkan perjanjian ini setelah menemukan properti incaran. Bank dan notaris/PPAT dapat meminta bukti pisah harta, jadi buat perjanjiannya sebelum transaksi, bukan sesudahnya.',
      alt: 'Pasangan muda berkonsultasi dengan seorang penasihat'
    },
    {
      title: 'Punya usaha pariwisata',
      copy: 'Vila sewaan, restoran, atau jasa wisata membawa risiko utang usaha. Perjanjian ini memisahkan mana yang bisa dikejar kreditur dan mana yang tidak.',
      alt: 'Seorang profesional memeriksa berkas di kantor hukum'
    },
    {
      title: 'Sudah menikah, baru mau buat',
      copy: 'Bisa. Sejak Putusan MK No. 69/PUU-XIII/2015, perjanjian perkawinan boleh dibuat selama pernikahan — yang biasanya dibutuhkan pasangan campuran yang sudah lama tinggal di Bali dan baru akan membeli properti.',
      alt: 'Pasangan menandatangani dokumen didampingi seorang penasihat'
    }
  ],
  law: {
    ...baseId.law,
    title: 'Dasar hukumnya, dan kenapa notarisnya harus di Bali'
  },
  lawCards: [
    ...baseId.lawCards,
    {
      reference: 'Pasal 21 ayat (3) UU No. 5 Tahun 1960 (UUPA)',
      title: 'Hak Milik tidak bisa ikut dimiliki pasangan WNA',
      copy: 'Orang asing yang memperoleh Hak Milik karena percampuran harta perkawinan wajib melepaskannya dalam satu tahun. Bila tidak, hak itu hapus dan tanahnya jatuh kepada negara. Perjanjian pisah harta yang tercatat mencegah tanah Anda tercampur ke dalam harta bersama.'
    },
    {
      reference: 'Pasal 17–18 UU No. 30 Tahun 2004 jo. UU No. 2 Tahun 2014',
      title: 'Kenapa notarisnya harus di Bali',
      copy: 'Wilayah jabatan notaris meliputi provinsi tempat kedudukannya, dan notaris dilarang menjalankan jabatan di luar wilayah itu. Akta yang ditandatangani di Bali dibuat oleh notaris yang berkedudukan di Bali, karena itu kami bekerja dengan notaris mitra di sana.'
    }
  ],
  process: {
    eyebrow: 'Prosesnya',
    title: 'Empat langkah, hanya satu yang perlu Anda hadiri di Bali',
    lead: 'Konsultasi dan draft lewat WhatsApp dan email. Anda berdua cukup datang sekali, saat tanda tangan akta. Pencatatannya kami yang urus.'
  },
  steps: [
    {
      when: 'Hari 1',
      title: 'Cerita dulu, gratis',
      copy: 'Lewat WhatsApp, dari mana pun Anda berada. Kami tanya soal aset, kewarganegaraan, tanggal nikah, dan kapan Anda berdua ada di Bali.'
    },
    {
      when: '2 – 3 hari kerja',
      title: 'Draft kami kirim',
      copy: 'Berisi pasal-pasal yang sudah disesuaikan, dengan penjelasan bahasa manusia di sampingnya supaya Anda tahu apa yang Anda tanda tangani.'
    },
    {
      when: 'Saat Anda di Bali',
      title: 'Tanda tangan akta',
      copy: 'Anda berdua hadir di hadapan notaris mitra kami di Bali dengan dokumen asli. Kalau Anda menikah di Bali, jadwalkan sebelum hari pernikahan.'
    },
    {
      when: '7 – 14 hari kerja',
      title: 'Kami catatkan',
      copy: 'Akta didaftarkan ke Dukcapil atau KUA. Anda tidak perlu menunggu di Bali untuk langkah ini — tanpa langkah ini pula perjanjian tidak mengikat pihak ketiga.'
    }
  ],
  faqTitle: 'Pertanyaan yang paling sering masuk',
  faqs: [
    {
      q: 'Berapa biayanya?',
      a: PRICE
        ? `${PRICE.id}, sudah termasuk konsultasi, draft, akta notaris di Bali, dan pencatatan. Penerjemah tersumpah dan apostille untuk pasangan WNA dikutip terpisah, setelah kami tahu dokumen apa yang dibutuhkan.`
        : 'Kami sebutkan di konsultasi pertama, sebelum Anda membayar apa pun. Angkanya sudah termasuk konsultasi, draft, akta notaris di Bali, dan pencatatan. Penerjemah tersumpah dan apostille untuk pasangan WNA dikutip terpisah, setelah kami tahu dokumen apa yang dibutuhkan.'
    },
    {
      q: 'Kami tinggal di luar negeri dan akan menikah di Bali. Bagaimana caranya?',
      a: 'Konsultasi dan draft kami kerjakan jarak jauh sebelum Anda berangkat. Tanda tangan akta dijadwalkan saat Anda berdua sudah di Bali dan sebelum hari pernikahan, karena perjanjian pranikah harus sudah ada saat perkawinan dicatatkan. Hubungi kami paling lambat tiga minggu sebelum tanggal nikah.'
    },
    {
      q: 'Pasangan saya WNA. Bisakah ia ikut memiliki vila yang kami beli?',
      a: 'Tidak dengan Hak Milik — orang asing tidak bisa memegang Hak Milik atas tanah. Perjanjian pisah harta membuat tanah yang Anda beli tetap milik Anda sebagai WNI dan tidak menjadi harta bersama. Kalau pasangan WNA ingin punya hak atas hunian sendiri, jalurnya Hak Pakai, dan itu dibahas dengan notaris/PPAT saat transaksi, di luar perjanjian ini.'
    },
    {
      q: 'Bisakah tanah dibeli dengan uang pasangan WNA tapi atas nama saya?',
      a: 'Itu yang disebut pinjam nama (nominee), dan perjanjian ini tidak bisa dipakai untuk itu. Pasal 26 ayat (2) UUPA menyatakan batal demi hukum setiap perbuatan yang dimaksudkan untuk, langsung maupun tidak langsung, memindahkan Hak Milik kepada orang asing. Perjanjian pisah harta melindungi kepemilikan WNI yang sah, bukan kepemilikan terselubung.'
    },
    {
      q: 'Saya sudah menikah. Masih bisa buat?',
      a: 'Bisa. Putusan Mahkamah Konstitusi No. 69/PUU-XIII/2015 membuka pembuatan perjanjian perkawinan selama masa pernikahan. Yang perlu diingat: perjanjian itu berlaku sejak dicatatkan, bukan mundur ke tanggal pernikahan.'
    },
    {
      q: 'Apakah akta dari notaris di Bali berlaku di luar Bali?',
      a: 'Berlaku. Wilayah jabatan membatasi di mana notaris boleh membuat akta, bukan di mana akta itu berlaku. Setelah dicatatkan, perjanjian Anda mengikat pihak ketiga di mana pun di Indonesia, termasuk bank dan kantor pertanahan di luar Bali.'
    },
    {
      q: 'Apakah perjanjian ini diakui di negara asal pasangan saya?',
      a: 'Itu ditentukan oleh hukum negara tersebut, bukan hukum Indonesia. Perjanjian ini mengatur harta perkawinan Anda di Indonesia. Kalau Anda punya aset atau akan tinggal di luar negeri, bicarakan juga dengan pengacara di sana; terjemahan tersumpah aktanya bisa kami siapkan.'
    },
    {
      q: 'Berapa lama sampai selesai?',
      a: 'Draft 2–3 hari kerja. Tanda tangan akta menyesuaikan jadwal Anda di Bali. Pencatatan 7–14 hari kerja tergantung antrean Dukcapil. Jadi realistisnya 2–3 minggu dari konsultasi pertama sampai catatan pinggir terbit.'
    },
    {
      q: 'Kalau kami tidak jadi lanjut setelah konsultasi?',
      a: 'Tidak apa-apa, dan tidak ada biaya. Konsultasi awal memang kami gratiskan supaya Anda bisa memutuskan dengan informasi yang cukup.'
    }
  ],
  form: {
    ...baseId.form,
    lead: 'Empat jawaban sudah cukup untuk kami menilai kasus Anda dan menyebutkan harganya. Kami balas di hari kerja yang sama.',
    notesPlaceholder:
      'Menikah di Ubud bulan Maret, pasangan WN Australia, sedang menawar vila di Canggu…',
    dataNote:
      'Data ini kami pakai untuk menghubungi Anda soal perjanjian pranikah di Bali. Tidak untuk yang lain.'
  },
  whatsappPrefill: 'Halo 7Magic, saya mau tanya soal perjanjian pranikah di Bali. Kondisi kami:',
  lead: { ...baseId.lead, heading: 'LEAD: Perjanjian Pranikah Bali' },
  jsonLd: {
    serviceType: 'Pembuatan perjanjian pranikah di Bali',
    offerDescription:
      'Konsultasi, penyusunan draft, akta notaris di Bali, dan pencatatan di Dukcapil/KUA.'
  }
};

const en: PrenupCopy = {
  ...baseEn,
  price: PRICE?.en ?? 'Confirmed at your consultation',
  priceShort: PRICE?.en ?? '',
  meta: {
    title: PRICE
      ? `Prenuptial Agreement in Bali — ${PRICE.en} All-in, Bali Notary | 7Magic`
      : 'Prenuptial Agreement in Bali — Bali Notary, Deed + Registration | 7Magic',
    description:
      'Prenuptial and separation-of-property agreements in Bali, signed before a notary based in Bali. Covers the consultation, drafting, the notarial deed and registration with Dukcapil or the KUA. For mixed-nationality couples and couples already married. First consultation free.',
    keywords:
      'prenuptial agreement Bali, prenup Bali, Bali notary prenuptial agreement, postnuptial agreement Indonesia, marrying an Indonesian property, foreigner own land Bali spouse, separation of property agreement Bali, mixed marriage prenup Indonesia'
  },
  hero: {
    ...baseEn.hero,
    eyebrow: 'Prenuptial agreement · Bali',
    title: PRICE
      ? `A prenuptial agreement in Bali, seen through to registration — ${PRICE.en}`
      : 'A prenuptial agreement in Bali, from first call to registration',
    lead: 'The consultation and the draft can be done from anywhere. The deed is signed before our partner notary in Bali, and we register it with Dukcapil or the KUA. It can also be made after you are married.'
  },
  stats: [
    { value: 'Free', label: 'First consultation, on WhatsApp' },
    { value: '2 – 3 weeks', label: 'From consultation to registration' },
    { value: 'Bali notary', label: 'The deed is signed in Bali' },
    { value: 'One visit', label: 'Only for signing the deed' }
  ],
  price_section: {
    ...baseEn.price_section,
    title: 'What is included, written down',
    lead: PRICE
      ? 'One figure, and no follow-up invoices for the steps below. Here is what is included, in black and white.'
      : 'We quote the Bali package at your first consultation, before you pay anything. What is already fixed is what it covers, in black and white.',
    marketNote: '',
    once: PRICE ? 'one-off' : '',
    badge: 'First consultation free'
  },
  comparison: [],
  included: [
    'A first consultation with our legal team on WhatsApp — before you arrive in Bali, if you like',
    'Drafting the agreement around your actual assets and plans',
    'Two rounds of revisions at no extra cost',
    'Signing the deed before our partner notary in Bali',
    'Registration with Dukcapil or the KUA, through to the marginal note being issued',
    'Official copies of the deed for you and your partner'
  ],
  excluded: [...baseEn.excluded, 'Your travel and accommodation in Bali for the signing'],
  segmentsIntro: {
    eyebrow: 'Who usually needs one',
    title: 'Four situations that make this agreement matter in Bali'
  },
  segments: [
    {
      title: 'Marrying a foreign national',
      copy: 'Without separate property, land bought during the marriage becomes jointly owned, and the foreign spouse’s share of a Hak Milik freehold must be given up within a year. A registered agreement keeps the Indonesian spouse’s right to hold freehold title in their own name.',
      alt: 'A pair of wedding rings in a box'
    },
    {
      title: 'Planning to buy a villa or land',
      copy: 'Many mixed couples only think about this once they have found the property. Banks and the notary handling the sale can ask for proof of separate property, so make the agreement before the transaction, not after.',
      alt: 'A young couple in consultation with an adviser'
    },
    {
      title: 'Running a tourism business',
      copy: 'A rental villa, a restaurant or a tour business carries business debt. The agreement draws the line between what creditors can pursue and what they cannot.',
      alt: 'A professional reviewing files in a law office'
    },
    {
      title: 'Already married, only now arranging it',
      copy: 'You can. Since Constitutional Court Decision No. 69/PUU-XIII/2015 a marital agreement may be made during the marriage — usually what a mixed couple long settled in Bali needs before buying property.',
      alt: 'A couple signing documents with an adviser present'
    }
  ],
  law: {
    ...baseEn.law,
    title: 'The legal basis, and why the notary has to be in Bali'
  },
  lawCards: [
    ...baseEn.lawCards,
    {
      reference: 'Article 21(3), Law No. 5 of 1960 (Basic Agrarian Law)',
      title: 'A foreign spouse cannot share in freehold title',
      copy: 'A foreign national who acquires Hak Milik through the mixing of marital property must give it up within one year. If not, the right lapses and the land passes to the state. A registered separation-of-property agreement keeps your land out of joint property.'
    },
    {
      reference: 'Articles 17–18, Law No. 30 of 2004 as amended by Law No. 2 of 2014',
      title: 'Why the notary has to be in Bali',
      copy: 'A notary’s jurisdiction is the province where they are based, and a notary may not act outside it. A deed signed in Bali is made by a notary based in Bali, which is why we work with a partner notary there.'
    }
  ],
  process: {
    eyebrow: 'The process',
    title: 'Four steps, and only one needs you in Bali',
    lead: 'The consultation and the draft happen over WhatsApp and email. You both come once, to sign the deed. Registration is on us.'
  },
  steps: [
    {
      when: 'Day 1',
      title: 'Tell us about it, free',
      copy: 'On WhatsApp, wherever you are. We ask about your assets, your citizenship, your wedding date and when you will both be in Bali.'
    },
    {
      when: '2 – 3 working days',
      title: 'We send the draft',
      copy: 'With the clauses tailored to your situation and a plain-language explanation beside each one, so you know what you are signing.'
    },
    {
      when: 'While you are in Bali',
      title: 'Signing the deed',
      copy: 'You both attend before our partner notary in Bali with your original documents. If you are marrying in Bali, schedule it before the wedding day.'
    },
    {
      when: '7 – 14 working days',
      title: 'We register it',
      copy: 'The deed is registered with Dukcapil or the KUA. You do not need to stay in Bali for this — and without it the agreement does not bind third parties.'
    }
  ],
  faqTitle: 'The questions we are asked most',
  faqs: [
    {
      q: 'How much does it cost?',
      a: PRICE
        ? `${PRICE.en}, covering the consultation, drafting, the notarial deed in Bali and registration. A sworn translator and apostille for a foreign partner are quoted separately, once we know which documents are involved.`
        : 'We quote it at your first consultation, before you pay anything. The figure covers the consultation, drafting, the notarial deed in Bali and registration. A sworn translator and apostille for a foreign partner are quoted separately, once we know which documents are involved.'
    },
    {
      q: 'We live abroad and are getting married in Bali. How does this work?',
      a: 'We do the consultation and the draft remotely before you travel. The signing is scheduled once you are both in Bali and before the wedding day, because a prenuptial agreement has to exist when the marriage is registered. Contact us at least three weeks before your wedding date.'
    },
    {
      q: 'My partner is a foreign national. Can they co-own the villa we buy?',
      a: 'Not as Hak Milik — foreign nationals cannot hold freehold title to land. A separation-of-property agreement keeps land you buy yours as an Indonesian citizen, outside joint property. If your foreign partner wants a right to a home of their own, the route is Hak Pakai, the right of use, which is handled with the notary at the time of purchase, not in this agreement.'
    },
    {
      q: 'Can land be bought with my foreign partner’s money but in my name?',
      a: 'That is a nominee arrangement, and this agreement cannot be used for one. Article 26(2) of the Basic Agrarian Law voids any act intended to transfer freehold title to a foreign national, directly or indirectly. A separation-of-property agreement protects genuine ownership by the Indonesian spouse, not disguised ownership.'
    },
    {
      q: 'We are already married. Can we still make one?',
      a: 'Yes. Constitutional Court Decision No. 69/PUU-XIII/2015 opened marital agreements up to couples already married. One thing to keep in mind: the agreement takes effect from the date it is registered, not retroactively from your wedding date.'
    },
    {
      q: 'Is a deed from a Bali notary valid outside Bali?',
      a: 'Yes. Jurisdiction limits where a notary may make a deed, not where the deed has effect. Once registered, your agreement binds third parties anywhere in Indonesia, including banks and land offices outside Bali.'
    },
    {
      q: 'Will it be recognised in my partner’s home country?',
      a: 'That is decided by that country’s law, not Indonesia’s. This agreement governs your marital property in Indonesia. If you hold assets or will live abroad, speak to a lawyer there as well; we can arrange a sworn translation of the deed.'
    },
    {
      q: 'How long does it take?',
      a: 'The draft takes 2–3 working days. Signing fits your time in Bali. Registration takes 7–14 working days depending on the Dukcapil queue. So realistically 2–3 weeks from the first consultation to the marginal note being issued.'
    },
    {
      q: 'What if we decide not to proceed after the consultation?',
      a: 'That is fine, and it costs nothing. The first consultation is free precisely so that you can decide with enough information in front of you.'
    }
  ],
  form: {
    ...baseEn.form,
    lead: 'Four answers are enough for us to assess your case and quote it. We reply the same working day.',
    notesPlaceholder:
      'Marrying in Ubud in March, partner is Australian, negotiating on a villa in Canggu…',
    dataNote:
      'We use these details to contact you about a prenuptial agreement in Bali. Nothing else.'
  },
  whatsappPrefill: 'Hi 7Magic, I would like to ask about a prenuptial agreement in Bali. Our situation:',
  lead: { ...baseEn.lead, heading: 'LEAD: Perjanjian Pranikah Bali' },
  jsonLd: {
    serviceType: 'Prenuptial agreement drafting in Bali',
    offerDescription:
      'Consultation, drafting, the notarial deed in Bali, and registration with Dukcapil or the KUA.'
  }
};

const CONTENT: Record<Locale, PrenupCopy> = { id, en };

export function baliPrenupCopy(locale: Locale): PrenupCopy {
  return CONTENT[locale] ?? CONTENT.id;
}
