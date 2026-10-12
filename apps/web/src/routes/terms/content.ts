/**
 * The terms and conditions, in both languages.
 *
 * Indonesian is the binding text (UU 24/2009 Pasal 31); the English is a
 * translation and must say no more and no less. The section list was checked
 * against the terms Weddingku and Bridestory publish, which are structure
 * references only: neither text is copied, and both are thinner than this on
 * operator identity, governing law and the vendor relationship.
 *
 * Three positions here are 7Magic's choices and should be confirmed by the
 * business before counsel reviews the text: 7Magic plans and arranges, while
 * each venue or vendor contract is the couple's own; disputes go to
 * musyawarah, then Pengadilan Negeri Jakarta Pusat (the Jakarta office at
 * Gajah Mada 10130 is in Gambir), which suits consumers better than BANI
 * arbitration; and nothing limits liability that UU 8/1999 Pasal 18 forbids
 * shifting. Not reviewed by counsel.
 */

import type { LegalCopy } from '$lib/components/LegalPage.svelte';
import type { Locale } from '$lib/paraglide/runtime';

export const termsCopy: Record<Locale, LegalCopy> = {
  id: {
    meta: {
      title: 'Syarat dan Ketentuan | 7Magic Wedding',
      description:
        'Syarat dan ketentuan penggunaan 7magicwedding.com dan layanan perencanaan pernikahan 7Magic Wedding: harga dan penawaran, peran venue dan vendor, hak cipta, serta hukum yang berlaku.'
    },
    eyebrow: 'Ketentuan',
    title: 'Syarat dan Ketentuan',
    updated: 'Terakhir diperbarui: 12 Oktober 2026',
    intro: [
      'Syarat dan ketentuan ini mengatur penggunaan situs 7magicwedding.com dan permintaan layanan yang Anda ajukan kepada 7Magic Wedding melalui situs, WhatsApp, atau email. Dengan memakai situs ini, Anda menyetujui ketentuan berikut. Jika Anda tidak setuju, mohon tidak memakai situs ini.'
    ],
    contents: 'Isi ketentuan',
    operator: {
      heading: 'Pengelola situs',
      name: '7Magic Wedding (nama dagang)',
      addressLabel: 'Alamat',
      otherOfficesLabel: 'Kantor lain',
      emailLabel: 'Email',
      whatsappLabel: 'WhatsApp'
    },
    sections: [
      {
        id: 'peran',
        heading: 'Peran 7Magic',
        blocks: [
          { p: '7Magic membantu pasangan memilih venue, merencanakan pernikahan, dan berkoordinasi dengan venue serta vendor. Kami bukan pemilik venue yang ditampilkan di situs ini.' },
          { p: 'Pemesanan venue atau vendor merupakan perjanjian antara Anda dan venue atau vendor tersebut, dengan syarat, pembayaran, dan kebijakan pembatalan masing-masing. Layanan perencanaan dari 7Magic sendiri diatur oleh penawaran atau perjanjian tertulis yang kami berikan kepada Anda.' }
        ]
      },
      {
        id: 'usia',
        heading: 'Siapa yang dapat memakai layanan',
        blocks: [
          { p: 'Anda harus berusia 18 tahun atau lebih, atau sudah cakap hukum menurut peraturan yang berlaku, untuk meminta penawaran atau memesan layanan. Jika Anda mengisi formulir atas nama orang lain, misalnya calon pengantin atau keluarga, Anda menyatakan sudah mendapat izin dari orang tersebut.' }
        ]
      },
      {
        id: 'harga',
        heading: 'Informasi, harga, dan ketersediaan',
        blocks: [
          { p: 'Harga paket, kapasitas, fasilitas, dan foto di situs ini adalah panduan untuk membantu Anda merencanakan. Venue dapat mengubah harga, isi paket, dan ketersediaan tanggal kapan saja, dan informasi di situs bisa tertinggal dari perubahan itu.' },
          { p: 'Harga dan isi layanan yang mengikat adalah yang tertulis dalam penawaran resmi dari 7Magic atau dari venue untuk tanggal dan jumlah tamu Anda. Selalu konfirmasikan kepada tim kami sebelum mengambil keputusan atau melakukan pembayaran.' }
        ]
      },
      {
        id: 'pemesanan',
        heading: 'Penawaran, pemesanan, dan pembayaran',
        blocks: [
          {
            list: [
              'Mengisi formulir atau menghubungi kami tidak menciptakan pemesanan. Pemesanan baru terjadi setelah Anda menyetujui penawaran tertulis dan melakukan pembayaran yang diminta di dalamnya.',
              'Uang muka, jadwal pembayaran, dan ketentuan pembatalan atau perubahan tanggal mengikuti penawaran atau perjanjian yang berlaku untuk layanan tersebut.',
              'Lakukan pembayaran hanya ke rekening yang tercantum dalam penawaran resmi. 7Magic tidak pernah meminta pembayaran ke rekening pribadi melalui pesan yang tidak dapat Anda verifikasi.'
            ]
          }
        ]
      },
      {
        id: 'mitra',
        heading: 'Venue, vendor, dan mitra',
        blocks: [
          { p: 'Kami memilih venue dan vendor dengan hati-hati, tetapi mereka adalah usaha yang terpisah dari 7Magic dan bertanggung jawab atas layanan yang mereka berikan sendiri.' },
          { p: 'Untuk pernikahan di Singapura, layanan concierge hari-H disediakan oleh ALL Access, perusahaan Singapura yang terpisah dari 7Magic, dan ditagihkan langsung oleh ALL Access. Layanan perjanjian pranikah dikerjakan bersama notaris, yang bertanggung jawab atas akta yang ia buat.' }
        ]
      },
      {
        id: 'artikel',
        heading: 'Artikel dan informasi umum',
        blocks: [
          { p: 'Artikel, panduan, dan contoh di situs ini bersifat informasi umum. Isinya tidak menggantikan nasihat hukum, keagamaan, kesehatan, atau keuangan untuk keadaan Anda. Peraturan, tarif, dan kebijakan instansi bisa berubah setelah artikel ditulis, jadi periksa kembali ke sumber resmi yang kami cantumkan sebelum bertindak.' }
        ]
      },
      {
        id: 'hak-cipta',
        heading: 'Hak kekayaan intelektual',
        blocks: [
          { p: 'Tulisan, desain, logo, dan nama 7Magic di situs ini dilindungi oleh Undang-Undang Nomor 28 Tahun 2014 tentang Hak Cipta dan Undang-Undang Nomor 20 Tahun 2016 tentang Merek dan Indikasi Geografis. Foto dari venue, fotografer, atau penyedia foto stok tetap menjadi milik pemiliknya, sebagaimana tercantum pada kreditnya.' },
          { p: 'Anda boleh membagikan tautan ke halaman kami dan mengutip sebagian kecil isinya dengan menyebut sumber. Menyalin atau menerbitkan ulang konten secara utuh, atau memakainya untuk kepentingan komersial, memerlukan izin tertulis dari kami.' }
        ]
      },
      {
        id: 'konten-anda',
        heading: 'Konten yang Anda kirim',
        blocks: [
          { p: 'Jika Anda mengirimkan testimoni, ulasan, atau foto pernikahan Anda kepada kami, Anda menyatakan berhak atas konten tersebut. Kami hanya akan menampilkannya di situs atau media sosial 7Magic dengan izin Anda, dan Anda dapat meminta kami menghapusnya kapan saja.' }
        ]
      },
      {
        id: 'larangan',
        heading: 'Penggunaan yang tidak diperbolehkan',
        blocks: [
          {
            list: [
              'mengirim data palsu atau data orang lain tanpa izin melalui formulir kami;',
              'mengambil konten atau data situs secara otomatis dalam jumlah besar tanpa izin;',
              'mengganggu, membebani, atau mencoba membobol keamanan situs;',
              'memakai situs untuk tujuan yang melanggar hukum.'
            ]
          }
        ]
      },
      {
        id: 'tautan',
        heading: 'Tautan ke situs lain',
        blocks: [
          { p: 'Situs ini memuat tautan ke situs venue, sumber berita, dan instansi resmi. Kami tidak mengendalikan situs-situs itu dan tidak bertanggung jawab atas isi atau kebijakan privasinya.' }
        ]
      },
      {
        id: 'tanggung-jawab',
        heading: 'Batas tanggung jawab',
        blocks: [
          { p: 'Sejauh diizinkan oleh hukum, 7Magic tidak bertanggung jawab atas kerugian yang timbul dari keputusan yang diambil semata-mata berdasarkan informasi umum di situs ini tanpa konfirmasi tertulis dari kami, atau dari layanan yang diberikan venue dan vendor di bawah perjanjian mereka sendiri.' },
          { p: 'Ketentuan ini tidak mengurangi hak Anda sebagai konsumen menurut Undang-Undang Nomor 8 Tahun 1999 tentang Perlindungan Konsumen, dan tidak membatasi tanggung jawab 7Magic atas layanan yang kami berikan sendiri.' }
        ]
      },
      {
        id: 'keadaan-kahar',
        heading: 'Keadaan kahar',
        blocks: [
          { p: 'Kami tidak dianggap lalai jika tidak dapat memenuhi kewajiban karena keadaan di luar kendali yang wajar, seperti bencana alam, kebakaran, kabut asap, wabah, kerusuhan, atau kebijakan pemerintah. Dalam keadaan seperti itu, kami akan memberi tahu Anda secepatnya dan berupaya mencari jadwal atau alternatif pengganti sesuai perjanjian yang berlaku.' }
        ]
      },
      {
        id: 'privasi',
        heading: 'Privasi',
        blocks: [
          { p: 'Cara kami memproses data pribadi Anda dijelaskan dalam Kebijakan Privasi di 7magicwedding.com/privacy, yang menjadi bagian dari ketentuan ini.' }
        ]
      },
      {
        id: 'perubahan',
        heading: 'Perubahan ketentuan',
        blocks: [
          { p: 'Kami dapat memperbarui ketentuan ini dan akan mengubah tanggal di bagian atas setiap kali melakukannya. Ketentuan yang berlaku untuk pemesanan Anda adalah yang berlaku saat Anda menyetujui penawaran, kecuali kita sepakati lain secara tertulis.' }
        ]
      },
      {
        id: 'hukum',
        heading: 'Hukum yang berlaku dan penyelesaian sengketa',
        blocks: [
          { p: 'Ketentuan ini tunduk pada hukum Republik Indonesia. Setiap perselisihan akan diselesaikan lebih dahulu secara musyawarah dalam waktu 30 hari sejak salah satu pihak memberitahukannya secara tertulis. Jika tidak tercapai kesepakatan, perselisihan diselesaikan melalui Pengadilan Negeri Jakarta Pusat, tanpa mengurangi hak Anda untuk menempuh penyelesaian sengketa konsumen menurut Undang-Undang Nomor 8 Tahun 1999.' }
        ]
      },
      {
        id: 'bahasa',
        heading: 'Bahasa',
        blocks: [
          { p: 'Ketentuan ini dibuat dalam bahasa Indonesia dan Inggris. Jika ada perbedaan makna, versi bahasa Indonesia yang berlaku.' }
        ]
      }
    ]
  },
  en: {
    meta: {
      title: 'Terms and Conditions | 7Magic Wedding',
      description:
        'Terms and conditions for using 7magicwedding.com and 7Magic Wedding planning services: prices and quotes, the role of venues and vendors, copyright, and governing law.'
    },
    eyebrow: 'Terms',
    title: 'Terms and Conditions',
    updated: 'Last updated: 12 October 2026',
    intro: [
      'These terms and conditions govern your use of 7magicwedding.com and any service requests you make to 7Magic Wedding through the site, WhatsApp or email. By using this site, you agree to the following terms. If you do not agree, please do not use this site.'
    ],
    contents: 'Contents',
    operator: {
      heading: 'Site operator',
      name: '7Magic Wedding (trade name)',
      addressLabel: 'Address',
      otherOfficesLabel: 'Other offices',
      emailLabel: 'Email',
      whatsappLabel: 'WhatsApp'
    },
    sections: [
      {
        id: 'role',
        heading: 'The role of 7Magic',
        blocks: [
          { p: '7Magic helps couples choose venues, plan their wedding, and coordinate with venues and vendors. We do not own the venues shown on this site.' },
          { p: 'A venue or vendor booking is an agreement between you and that venue or vendor, under its own terms, payments and cancellation policy. 7Magic\'s own planning services are governed by the written quote or agreement we give you.' }
        ]
      },
      {
        id: 'eligibility',
        heading: 'Who may use the services',
        blocks: [
          { p: 'You must be 18 or older, or otherwise have legal capacity under applicable law, to request a quote or book a service. If you fill in a form on behalf of someone else, such as the bride or groom or a family member, you confirm that you have their permission.' }
        ]
      },
      {
        id: 'prices',
        heading: 'Information, prices and availability',
        blocks: [
          { p: 'Package prices, capacities, facilities and photos on this site are guidance to help you plan. Venues may change prices, package contents and date availability at any time, and the information on the site may lag behind those changes.' },
          { p: 'The binding prices and service contents are those written in an official quote from 7Magic or from the venue for your date and guest count. Always confirm with our team before making a decision or a payment.' }
        ]
      },
      {
        id: 'bookings',
        heading: 'Quotes, bookings and payments',
        blocks: [
          {
            list: [
              'Filling in a form or contacting us does not create a booking. A booking only exists once you accept a written quote and make the payment it asks for.',
              'Deposits, payment schedules, and cancellation or date-change terms follow the quote or agreement that applies to that service.',
              'Only pay into the account named in the official quote. 7Magic never asks for payment into a personal account through a message you cannot verify.'
            ]
          }
        ]
      },
      {
        id: 'partners',
        heading: 'Venues, vendors and partners',
        blocks: [
          { p: 'We choose venues and vendors carefully, but they are businesses separate from 7Magic and are responsible for the services they provide themselves.' },
          { p: 'For weddings in Singapore, the day-of concierge service is provided by ALL Access, a Singapore company separate from 7Magic, and billed directly by ALL Access. The prenuptial agreement service is carried out with a notary, who is responsible for the deed they draw up.' }
        ]
      },
      {
        id: 'articles',
        heading: 'Articles and general information',
        blocks: [
          { p: 'Articles, guides and examples on this site are general information. They do not replace legal, religious, medical or financial advice for your situation. Regulations, fees and official policies can change after an article is written, so check the official sources we cite before acting.' }
        ]
      },
      {
        id: 'ip',
        heading: 'Intellectual property',
        blocks: [
          { p: 'The writing, design, logo and the 7Magic name on this site are protected by Indonesian Law No. 28 of 2014 on Copyright and Law No. 20 of 2016 on Marks and Geographical Indications. Photos from venues, photographers or stock photo providers remain the property of their owners, as shown in their credits.' },
          { p: 'You may share links to our pages and quote short extracts with attribution. Copying or republishing content in full, or using it commercially, requires our written permission.' }
        ]
      },
      {
        id: 'your-content',
        heading: 'Content you send us',
        blocks: [
          { p: 'If you send us a testimonial, review or photos of your wedding, you confirm that you hold the rights to that content. We will only show it on the 7Magic site or social media with your permission, and you can ask us to remove it at any time.' }
        ]
      },
      {
        id: 'prohibited',
        heading: 'Prohibited use',
        blocks: [
          {
            list: [
              'submitting false data, or someone else\'s data without their permission, through our forms;',
              'automatically collecting the site\'s content or data in bulk without permission;',
              'disrupting, overloading or trying to breach the security of the site;',
              'using the site for any unlawful purpose.'
            ]
          }
        ]
      },
      {
        id: 'links',
        heading: 'Links to other sites',
        blocks: [
          { p: 'This site links to venue websites, news sources and official agencies. We do not control those sites and are not responsible for their content or privacy policies.' }
        ]
      },
      {
        id: 'liability',
        heading: 'Limits of liability',
        blocks: [
          { p: 'To the extent permitted by law, 7Magic is not liable for losses arising from decisions made solely on the general information on this site without our written confirmation, or from services provided by venues and vendors under their own agreements.' },
          { p: 'These terms do not reduce your rights as a consumer under Indonesian Law No. 8 of 1999 on Consumer Protection, and do not limit 7Magic\'s liability for the services we provide ourselves.' }
        ]
      },
      {
        id: 'force-majeure',
        heading: 'Force majeure',
        blocks: [
          { p: 'We are not in breach if we cannot meet an obligation because of circumstances beyond our reasonable control, such as natural disasters, fires, smoke haze, epidemics, civil unrest or government policy. In such circumstances, we will tell you as soon as possible and work to find a replacement date or alternative under the applicable agreement.' }
        ]
      },
      {
        id: 'privacy',
        heading: 'Privacy',
        blocks: [
          { p: 'How we process your personal data is explained in our Privacy Policy at 7magicwedding.com/privacy, which forms part of these terms.' }
        ]
      },
      {
        id: 'changes',
        heading: 'Changes to these terms',
        blocks: [
          { p: 'We may update these terms and will change the date at the top whenever we do. The terms that apply to your booking are those in force when you accepted the quote, unless we agree otherwise in writing.' }
        ]
      },
      {
        id: 'law',
        heading: 'Governing law and disputes',
        blocks: [
          { p: 'These terms are governed by the laws of the Republic of Indonesia. Any dispute will first be settled by deliberation (musyawarah) within 30 days of either party giving written notice of it. If no agreement is reached, the dispute will be settled through the Central Jakarta District Court (Pengadilan Negeri Jakarta Pusat), without prejudice to your right to pursue consumer dispute resolution under Law No. 8 of 1999.' }
        ]
      },
      {
        id: 'language',
        heading: 'Language',
        blocks: [
          { p: 'These terms are made in Indonesian and English. If the two differ in meaning, the Indonesian version prevails.' }
        ]
      }
    ]
  }
};
