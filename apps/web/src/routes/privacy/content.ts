/**
 * The privacy policy, in both languages.
 *
 * Indonesian is the binding text (UU 24/2009 Pasal 31 requires it for anything
 * that reads as an agreement with an Indonesian party); the English is a
 * translation and must say no more and no less. The structure follows what UU
 * PDP 27/2022 asks a controller to tell the data subject (Pasal 20-21 basis and
 * purpose, Pasal 5-13 rights, Pasal 46 breach notice, Pasal 56 transfers), plus
 * the public privacy contact Singapore's PDPA s.11(5) requires for clients
 * served from the Singapore office.
 *
 * Every factual claim here is about how the site actually works: the form
 * fields, the `pref_locale` cookie, Google Analytics (rendered only when
 * PUBLIC_GA_MEASUREMENT_ID is set, which it is in production), Cloudflare R2,
 * email delivery of leads to staff, WhatsApp. Change the code and this has to
 * change with it.
 *
 * The operator is named by trade name only until the legal entity is supplied;
 * the address and contacts come from `$lib/offices` and `$lib/contact` through
 * LegalPage, not from this file. The 24-month retention period is 7Magic's
 * decision and still to be confirmed by the business. Not reviewed by counsel.
 */

import type { LegalCopy } from '$lib/components/LegalPage.svelte';
import type { Locale } from '$lib/paraglide/runtime';

export const privacyCopy: Record<Locale, LegalCopy> = {
  id: {
    meta: {
      title: 'Kebijakan Privasi | 7Magic Wedding',
      description:
        'Data apa yang dikumpulkan 7Magic Wedding, untuk apa, dengan siapa dibagikan, berapa lama disimpan, dan cara Anda menggunakan hak atas data pribadi Anda.'
    },
    eyebrow: 'Privasi',
    title: 'Kebijakan Privasi',
    updated: 'Terakhir diperbarui: 12 Oktober 2026',
    intro: [
      'Kebijakan ini menjelaskan bagaimana 7Magic Wedding mengumpulkan, memakai, membagikan, dan melindungi data pribadi Anda saat Anda membuka 7magicwedding.com, mengisi formulir di situs ini, atau menghubungi kami lewat WhatsApp dan email.',
      'Kami memproses data pribadi sesuai Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi. Untuk klien yang kami layani dari kantor Singapura, kami juga mengikuti Personal Data Protection Act 2012 Singapura.'
    ],
    contents: 'Isi kebijakan',
    operator: {
      heading: 'Pengendali data',
      name: '7Magic Wedding (nama dagang)',
      addressLabel: 'Alamat',
      otherOfficesLabel: 'Kantor lain',
      emailLabel: 'Email privasi',
      whatsappLabel: 'WhatsApp'
    },
    sections: [
      {
        id: 'data',
        heading: 'Data yang kami kumpulkan',
        blocks: [
          { p: 'Data yang Anda berikan sendiri melalui formulir konsultasi, permintaan penawaran venue, pemesanan tur venue, dan pendaftaran acara:' },
          {
            list: [
              'nama, nomor WhatsApp atau telepon, dan alamat email;',
              'rencana pernikahan Anda: tanggal, kota, venue yang diminati, perkiraan jumlah tamu, dan waktu yang nyaman untuk dihubungi;',
              'pesan yang Anda tulis, dan nama tamu yang Anda daftarkan untuk tur atau acara.'
            ]
          },
          { p: 'Data yang tercatat otomatis saat Anda memakai situs: halaman yang dibuka, perkiraan negara dari alamat IP (dipakai untuk memilih bahasa halaman utama), jenis perangkat dan peramban, serta data cookie yang dijelaskan di bagian Cookie.' },
          { p: 'Kami tidak meminta data pribadi yang bersifat spesifik, seperti data kesehatan, biometrik, atau keuangan, melalui situs ini. Mohon tidak menuliskannya di kolom pesan.' }
        ]
      },
      {
        id: 'tujuan',
        heading: 'Tujuan dan dasar pemrosesan',
        blocks: [
          {
            list: [
              'Menanggapi pertanyaan dan menyiapkan penawaran, tur venue, atau rencana pernikahan yang Anda minta. Dasarnya adalah pemenuhan kewajiban atau langkah sebelum perjanjian atas permintaan Anda (Pasal 20 ayat (2) huruf b UU PDP).',
              'Menjalankan layanan yang sudah Anda sepakati dengan kami, termasuk koordinasi dengan venue dan vendor. Dasarnya adalah perjanjian dengan Anda.',
              'Mengirim informasi promosi atau undangan acara. Ini hanya kami lakukan dengan persetujuan Anda, yang bisa Anda tarik kapan saja.',
              'Memahami cara situs dipakai agar kami bisa memperbaikinya, dan menjaga keamanan situs. Dasarnya adalah kepentingan yang sah, dengan data yang seminimal mungkin.',
              'Memenuhi kewajiban hukum, misalnya pencatatan transaksi untuk keperluan pajak.'
            ]
          }
        ]
      },
      {
        id: 'berbagi',
        heading: 'Dengan siapa data dibagikan',
        blocks: [
          { p: 'Kami tidak menjual data pribadi Anda. Data hanya dibagikan sejauh diperlukan untuk tujuan di atas:' },
          {
            list: [
              'Venue dan vendor pilihan Anda. Saat Anda meminta penawaran atau tur, kami meneruskan nama, kontak, tanggal, dan jumlah tamu Anda ke venue tersebut agar mereka bisa mengecek ketersediaan dan menyiapkan tur.',
              'ALL Access, perusahaan Singapura yang terpisah dari 7Magic, hanya jika Anda meminta layanan concierge hari-H mereka untuk pernikahan di Singapura. ALL Access memproses data itu sebagai pihak tersendiri berdasarkan kebijakan privasinya.',
              'Penyedia layanan yang bekerja atas nama kami: hosting dan server, penyimpanan gambar Cloudflare R2, layanan pengiriman email yang meneruskan formulir Anda ke tim kami, dan Google Analytics. Mereka hanya boleh memakai data sesuai instruksi kami.',
              'Instansi berwenang, jika diwajibkan oleh hukum atau putusan pengadilan.'
            ]
          },
          { p: 'Jika Anda menghubungi kami lewat WhatsApp, percakapan itu juga diproses oleh WhatsApp (Meta) sesuai kebijakan privasinya sendiri.' }
        ]
      },
      {
        id: 'transfer',
        heading: 'Transfer data ke luar Indonesia',
        blocks: [
          { p: 'Sebagian penyedia layanan kami, seperti Cloudflare, Google, dan penyedia email, dapat menyimpan atau memproses data di luar Indonesia. Untuk klien pernikahan di Singapura, data juga dibagikan ke kantor dan mitra kami di sana. Kami hanya memakai penyedia yang menerapkan pelindungan data yang setara atau lebih tinggi dari UU PDP, atau yang terikat perlindungan kontraktual, sesuai Pasal 56 UU PDP.' }
        ]
      },
      {
        id: 'cookie',
        heading: 'Cookie dan analitik',
        blocks: [
          {
            list: [
              'pref_locale: menyimpan pilihan bahasa Anda (Indonesia atau Inggris) selama satu tahun. Cookie ini diperlukan agar situs tampil dalam bahasa yang Anda pilih.',
              'Google Analytics: memakai cookie untuk menghitung kunjungan dan halaman yang dibuka secara agregat. Anda bisa menolaknya lewat pengaturan cookie peramban atau Google Analytics Opt-out Browser Add-on (tools.google.com/dlpage/gaoptout).'
            ]
          },
          { p: 'Situs publik tidak memakai cookie iklan atau pelacakan lintas situs.' }
        ]
      },
      {
        id: 'retensi',
        heading: 'Berapa lama data disimpan',
        blocks: [
          { p: 'Data dari formulir yang tidak berlanjut menjadi pemesanan kami simpan paling lama 24 bulan sejak kontak terakhir, lalu kami hapus atau anonimkan. Data klien yang memakai layanan kami disimpan selama layanan berjalan dan sesudahnya selama diwajibkan oleh peraturan, misalnya untuk keperluan pajak dan pembukuan. Anda bisa meminta penghapusan lebih awal, seperti dijelaskan di bagian Hak Anda.' }
        ]
      },
      {
        id: 'keamanan',
        heading: 'Keamanan dan kegagalan pelindungan data',
        blocks: [
          { p: 'Akses ke data formulir dibatasi untuk tim yang menanganinya, sambungan ke situs dienkripsi (HTTPS), dan akun admin dilindungi kata sandi yang di-hash. Tidak ada sistem yang sepenuhnya aman, jadi kami juga menyiapkan langkah jika terjadi kebocoran.' },
          { p: 'Jika terjadi kegagalan pelindungan data pribadi, kami akan memberi tahu Anda dan lembaga yang berwenang secara tertulis paling lambat 3 x 24 jam, sesuai Pasal 46 UU PDP. Pemberitahuan itu menjelaskan data apa yang terungkap, kapan dan bagaimana kejadiannya, serta langkah penanganan dan pemulihannya.' }
        ]
      },
      {
        id: 'hak',
        heading: 'Hak Anda',
        blocks: [
          { p: 'Sesuai Pasal 5 sampai 13 UU PDP, Anda berhak:' },
          {
            list: [
              'mendapat informasi tentang identitas kami, tujuan pemrosesan, dan dasar hukumnya;',
              'mengakses dan memperoleh salinan data pribadi Anda;',
              'memperbaiki data yang keliru atau tidak lengkap;',
              'meminta data Anda dihapus, atau pemrosesannya dihentikan atau dibatasi;',
              'menarik persetujuan yang pernah Anda berikan;',
              'menolak keputusan yang sepenuhnya otomatis (kami tidak membuat keputusan seperti itu);',
              'mendapatkan dan memindahkan data Anda dalam format yang umum dipakai;',
              'menggugat dan menerima ganti rugi atas pelanggaran pemrosesan data pribadi.'
            ]
          },
          { p: 'Kirim permintaan ke email privasi di atas, dari alamat email atau nomor WhatsApp yang sama dengan yang Anda pakai saat menghubungi kami, agar kami bisa memastikan permintaan itu berasal dari Anda. Kami menanggapi tanpa biaya dan dalam jangka waktu yang ditetapkan peraturan.' }
        ]
      },
      {
        id: 'anak',
        heading: 'Anak',
        blocks: [
          { p: 'Situs dan layanan kami ditujukan untuk orang dewasa yang merencanakan pernikahan. Kami tidak dengan sengaja mengumpulkan data anak. Jika Anda orang tua atau wali dan mengetahui data anak Anda dikirim kepada kami, hubungi kami dan kami akan menghapusnya.' }
        ]
      },
      {
        id: 'keluhan',
        heading: 'Pertanyaan dan pengaduan',
        blocks: [
          { p: 'Pertanyaan atau keluhan tentang data pribadi Anda bisa dikirim ke email privasi di atas. Jika Anda tidak puas dengan tanggapan kami, Anda dapat mengadu kepada lembaga penyelenggara pelindungan data pribadi di Indonesia, atau, untuk klien Singapura, kepada Personal Data Protection Commission (PDPC) Singapura.' }
        ]
      },
      {
        id: 'perubahan',
        heading: 'Perubahan kebijakan',
        blocks: [
          { p: 'Jika kebijakan ini berubah, kami akan memperbarui tanggal di bagian atas. Untuk perubahan yang memengaruhi data yang sudah Anda berikan, kami memberi tahu Anda sebelum perubahan itu berlaku, sesuai Pasal 21 ayat (2) UU PDP.' }
        ]
      },
      {
        id: 'bahasa',
        heading: 'Bahasa',
        blocks: [
          { p: 'Kebijakan ini tersedia dalam bahasa Indonesia dan Inggris. Jika ada perbedaan makna, versi bahasa Indonesia yang berlaku.' }
        ]
      }
    ]
  },
  en: {
    meta: {
      title: 'Privacy Policy | 7Magic Wedding',
      description:
        'What data 7Magic Wedding collects, what it is used for, who it is shared with, how long it is kept, and how to exercise your rights over your personal data.'
    },
    eyebrow: 'Privacy',
    title: 'Privacy Policy',
    updated: 'Last updated: 12 October 2026',
    intro: [
      'This policy explains how 7Magic Wedding collects, uses, shares and protects your personal data when you visit 7magicwedding.com, fill in a form on this site, or contact us by WhatsApp or email.',
      'We process personal data under Indonesian Law No. 27 of 2022 on Personal Data Protection (UU PDP). For clients we serve from our Singapore office, we also follow Singapore\'s Personal Data Protection Act 2012.'
    ],
    contents: 'Contents',
    operator: {
      heading: 'Data controller',
      name: '7Magic Wedding (trade name)',
      addressLabel: 'Address',
      otherOfficesLabel: 'Other offices',
      emailLabel: 'Privacy email',
      whatsappLabel: 'WhatsApp'
    },
    sections: [
      {
        id: 'data',
        heading: 'Data we collect',
        blocks: [
          { p: 'Data you give us yourself through the consultation form, venue quote requests, venue tour bookings and event registrations:' },
          {
            list: [
              'your name, WhatsApp or phone number, and email address;',
              'your wedding plans: date, city, venues you are interested in, approximate guest count, and a convenient time to contact you;',
              'messages you write, and the names of guests you register for a tour or event.'
            ]
          },
          { p: 'Data recorded automatically when you use the site: pages viewed, your approximate country from your IP address (used to choose the language of the home page), device and browser type, and the cookie data described under Cookies.' },
          { p: 'We do not ask for specific personal data, such as health, biometric or financial data, through this site. Please do not write it in the message field.' }
        ]
      },
      {
        id: 'purposes',
        heading: 'Purposes and legal bases',
        blocks: [
          {
            list: [
              'Answering your questions and preparing the quotes, venue tours or wedding plans you ask for. The basis is fulfilling obligations or taking pre-contract steps at your request (UU PDP Article 20(2)(b)).',
              'Delivering services you have agreed with us, including coordination with venues and vendors. The basis is our agreement with you.',
              'Sending promotional information or event invitations. We only do this with your consent, which you can withdraw at any time.',
              'Understanding how the site is used so we can improve it, and keeping the site secure. The basis is legitimate interest, using as little data as possible.',
              'Meeting legal obligations, for example keeping transaction records for tax purposes.'
            ]
          }
        ]
      },
      {
        id: 'sharing',
        heading: 'Who we share data with',
        blocks: [
          { p: 'We do not sell your personal data. It is only shared as far as the purposes above require:' },
          {
            list: [
              'Venues and vendors you choose. When you request a quote or tour, we pass your name, contact details, date and guest count to that venue so it can check availability and arrange the tour.',
              'ALL Access, a Singapore company separate from 7Magic, only if you ask for its day-of concierge service for a wedding in Singapore. ALL Access processes that data as a separate party under its own privacy policy.',
              'Service providers working on our behalf: hosting and servers, Cloudflare R2 image storage, the email delivery service that forwards your form to our team, and Google Analytics. They may only use the data as we instruct.',
              'Competent authorities, where required by law or a court order.'
            ]
          },
          { p: 'If you contact us by WhatsApp, that conversation is also processed by WhatsApp (Meta) under its own privacy policy.' }
        ]
      },
      {
        id: 'transfers',
        heading: 'Transfers outside Indonesia',
        blocks: [
          { p: 'Some of our service providers, such as Cloudflare, Google and our email provider, may store or process data outside Indonesia. For wedding clients in Singapore, data is also shared with our office and partners there. We only use providers that apply data protection equal to or higher than UU PDP, or that are bound by contractual safeguards, in line with UU PDP Article 56.' }
        ]
      },
      {
        id: 'cookies',
        heading: 'Cookies and analytics',
        blocks: [
          {
            list: [
              'pref_locale: stores your language choice (Indonesian or English) for one year. This cookie is needed for the site to appear in the language you chose.',
              'Google Analytics: uses cookies to count visits and pages viewed in aggregate. You can refuse it through your browser\'s cookie settings or the Google Analytics Opt-out Browser Add-on (tools.google.com/dlpage/gaoptout).'
            ]
          },
          { p: 'The public site does not use advertising or cross-site tracking cookies.' }
        ]
      },
      {
        id: 'retention',
        heading: 'How long we keep data',
        blocks: [
          { p: 'Data from forms that do not lead to a booking is kept for at most 24 months after the last contact, then deleted or anonymised. Data of clients who use our services is kept while the service runs and afterwards for as long as regulations require, for example for tax and bookkeeping. You can ask for earlier deletion, as described under Your rights.' }
        ]
      },
      {
        id: 'security',
        heading: 'Security and data breaches',
        blocks: [
          { p: 'Access to form data is limited to the team handling it, connections to the site are encrypted (HTTPS), and admin accounts are protected by hashed passwords. No system is completely secure, so we are also prepared for a breach.' },
          { p: 'If a personal data protection failure occurs, we will notify you and the competent authority in writing within 3 x 24 hours at the latest, as required by UU PDP Article 46. The notice will explain what data was exposed, when and how it happened, and the steps taken to handle and recover from it.' }
        ]
      },
      {
        id: 'rights',
        heading: 'Your rights',
        blocks: [
          { p: 'Under UU PDP Articles 5 to 13, you have the right to:' },
          {
            list: [
              'be informed of our identity, the purpose of processing and its legal basis;',
              'access and obtain a copy of your personal data;',
              'correct data that is wrong or incomplete;',
              'ask for your data to be deleted, or for processing to be stopped or restricted;',
              'withdraw consent you have given;',
              'object to decisions made solely by automated means (we make no such decisions);',
              'obtain and transfer your data in a commonly used format;',
              'sue and receive compensation for violations in the processing of your personal data.'
            ]
          },
          { p: 'Send your request to the privacy email above, from the same email address or WhatsApp number you used to contact us, so we can confirm the request comes from you. We respond free of charge and within the time limits set by regulation.' }
        ]
      },
      {
        id: 'children',
        heading: 'Children',
        blocks: [
          { p: 'Our site and services are intended for adults planning a wedding. We do not knowingly collect children\'s data. If you are a parent or guardian and learn that your child\'s data was sent to us, contact us and we will delete it.' }
        ]
      },
      {
        id: 'complaints',
        heading: 'Questions and complaints',
        blocks: [
          { p: 'Questions or complaints about your personal data can be sent to the privacy email above. If you are not satisfied with our response, you may complain to the personal data protection authority in Indonesia or, for Singapore clients, to Singapore\'s Personal Data Protection Commission (PDPC).' }
        ]
      },
      {
        id: 'changes',
        heading: 'Changes to this policy',
        blocks: [
          { p: 'If this policy changes, we will update the date at the top. For changes that affect data you have already given us, we will tell you before the change takes effect, as required by UU PDP Article 21(2).' }
        ]
      },
      {
        id: 'language',
        heading: 'Language',
        blocks: [
          { p: 'This policy is available in Indonesian and English. If the two differ in meaning, the Indonesian version prevails.' }
        ]
      }
    ]
  }
};
