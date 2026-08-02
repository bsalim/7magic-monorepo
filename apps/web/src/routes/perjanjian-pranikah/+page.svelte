<script lang="ts">
  import CheckIcon from '@lucide/svelte/icons/check';
  import XIcon from '@lucide/svelte/icons/x';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { cn } from '$lib/utils';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';

  /**
   * Landing page akuisisi untuk layanan perjanjian pranikah (Jakarta).
   *
   * Bahasa Indonesia saja — ini halaman akuisisi untuk pasar Jakarta, terpisah
   * dari marketplace pernikahan yang bilingual. Copy di-hardcode dengan alasan
   * yang sama seperti /about dan /bali-event-organizer: berubah sebagai satu
   * kesatuan, bukan per-string.
   *
   * Kata kunci yang dibidik (riset pasar Jakarta): "perjanjian pranikah",
   * "perjanjian pra nikah", "biaya perjanjian pranikah", "perjanjian pisah
   * harta", "perjanjian perkawinan", "prenup Indonesia", "perjanjian pranikah
   * WNA" / "kawin campur".
   */

  // ---------------------------------------------------------------------------
  // Harga Rp 3,5 juta = harga perkenalan, all-in: konsultasi + draft + akta
  // notaris + pencatatan. Dikonfirmasi 7Magic. Kalau harga ini berubah, ubah
  // juga JSON-LD, <title>, meta description, pesan WhatsApp, kedua jawaban FAQ
  // yang menyebut angkanya, dan message "service_prenup_desc" di id.json/en.json.
  // ---------------------------------------------------------------------------
  const HARGA = 'Rp 3.500.000';

  // ---------------------------------------------------------------------------
  // PLACEHOLDER — sengaja dikosongkan. Blok kredensial notaris hanya tampil
  // kalau diisi. Mencantumkan nama notaris dan nomor SK karangan di halaman
  // live sama dengan memalsukan kredensial profesi, jadi isi ini HARUS datang
  // dari 7Magic sebelum publikasi.
  // ---------------------------------------------------------------------------
  const notaris = {
    nama: '',
    sk: '',
    wilayah: ''
  };

  // Kisaran pasar dipakai sebagai pembanding harga. Angka ini adalah kisaran
  // publik tarif notaris di Jakarta, bukan tarif kompetitor tertentu.
  const pembanding = [
    {
      label: 'Notaris pada umumnya di Jakarta',
      harga: 'Rp 4 – 15 juta',
      catatan: 'Biaya pencatatan dan konsultasi lanjutan sering dihitung terpisah.',
      ours: false
    },
    {
      label: '7Magic — paket perjanjian pranikah',
      harga: `${HARGA} all-in`,
      catatan: 'Konsultasi, penyusunan draft, akta notaris, dan pencatatan. Satu angka.',
      ours: true
    }
  ];

  const termasuk = [
    'Konsultasi awal bersama tim legal kami — berdua atau sendiri dulu, terserah Anda',
    'Penyusunan draft perjanjian sesuai kondisi aset dan rencana Anda',
    'Dua kali revisi draft tanpa biaya tambahan',
    'Penandatanganan akta di hadapan notaris kami',
    'Pencatatan ke Dukcapil atau KUA sampai terbit catatan pinggirnya',
    'Salinan akta resmi untuk Anda dan pasangan'
  ];

  const tidakTermasuk = [
    'Struktur aset yang rumit — perusahaan tertutup, saham lintas negara, trust',
    'Penerjemah tersumpah untuk pasangan WNA yang tidak berbahasa Indonesia',
    'Legalisasi atau apostille dokumen dari luar negeri',
    'Perubahan isi perjanjian setelah akta ditandatangani'
  ];

  const segmen = [
    {
      image: '/img/prenup/rings.jpg',
      alt: 'Sepasang cincin kawin di dalam kotak',
      title: 'Menikah dengan WNA',
      copy: 'Tanpa perjanjian pisah harta, WNI yang menikah dengan WNA bisa kehilangan hak untuk memegang Sertifikat Hak Milik. Ini alasan paling sering orang datang ke kami.'
    },
    {
      image: '/img/prenup/advisor.jpg',
      alt: 'Pasangan muda berkonsultasi dengan seorang penasihat',
      title: 'Punya usaha sendiri',
      copy: 'Kalau usaha Anda berisiko, utang usaha bisa menyeret harta bersama. Perjanjian ini memisahkan mana yang bisa dikejar kreditur dan mana yang tidak.'
    },
    {
      image: '/img/prenup/notary.jpg',
      alt: 'Seorang profesional memeriksa berkas di kantor hukum',
      title: 'Sudah punya aset sebelum menikah',
      copy: 'Rumah, tanah, atau warisan yang Anda bawa masuk ke pernikahan. Perjanjian menegaskan statusnya sejak hari pertama, bukan diperdebatkan belakangan.'
    },
    {
      image: '/img/prenup/couple-signing.jpg',
      alt: 'Pasangan menandatangani dokumen didampingi seorang penasihat',
      title: 'Sudah menikah, baru mau buat',
      copy: 'Bisa. Sejak Putusan MK No. 69/PUU-XIII/2015, perjanjian perkawinan boleh dibuat setelah pernikahan berlangsung. Prosesnya sama, harganya sama.'
    }
  ];

  // Dipecah jadi kartu, bukan paragraf: nomor pasal dan nomor putusan adalah
  // hal yang orang cari dan salin dari halaman ini, jadi keduanya dijadikan
  // label yang bisa dipindai sekilas alih-alih terkubur di tengah kalimat.
  const dasarHukum = [
    {
      rujukan: 'Pasal 29 UU No. 1 Tahun 1974',
      title: 'Perjanjian perkawinan diakui undang-undang',
      copy: 'Pada waktu atau sebelum perkawinan dilangsungkan, kedua pihak atas persetujuan bersama dapat mengajukan perjanjian tertulis yang disahkan oleh pegawai pencatat perkawinan atau notaris.'
    },
    {
      rujukan: 'Putusan MK No. 69/PUU-XIII/2015',
      title: 'Boleh dibuat setelah menikah',
      copy: 'Mahkamah Konstitusi memperluas aturannya: perjanjian perkawinan kini boleh dibuat juga selama masa pernikahan, bukan cuma sebelum. Inilah yang membuat pasangan yang sudah menikah bertahun-tahun tetap bisa membuatnya.'
    }
  ];

  const langkah = [
    {
      title: 'Cerita dulu, gratis',
      copy: 'Lewat WhatsApp atau tatap muka. Kami tanya soal aset, kewarganegaraan, dan rencana Anda. Belum ada biaya apa pun di tahap ini.',
      waktu: 'Hari 1'
    },
    {
      title: 'Draft kami kirim',
      copy: 'Berisi pasal-pasal yang sudah disesuaikan, dengan penjelasan bahasa manusia di sampingnya supaya Anda tahu apa yang Anda tanda tangani.',
      waktu: '2 – 3 hari kerja'
    },
    {
      title: 'Tanda tangan akta',
      copy: 'Anda berdua hadir di hadapan notaris kami, bawa dokumen asli. Sekitar satu jam, selesai hari itu juga.',
      waktu: 'Sesuai jadwal Anda'
    },
    {
      title: 'Kami catatkan',
      copy: 'Akta didaftarkan ke Dukcapil atau KUA. Tanpa langkah ini perjanjian tidak mengikat pihak ketiga — dan justru langkah ini yang paling sering terlewat.',
      waktu: '7 – 14 hari kerja'
    }
  ];

  const bisaDiatur = [
    'Pemisahan harta bawaan dan harta yang diperoleh selama pernikahan',
    'Status kepemilikan properti, rekening, saham, dan kendaraan',
    'Tanggung jawab atas utang masing-masing pihak',
    'Pengaturan biaya rumah tangga dan pendidikan anak',
    'Pembagian penghasilan dan aset usaha',
    'Ketentuan bila salah satu pihak meninggal atau pernikahan berakhir'
  ];

  const tidakBisaDiatur = [
    'Melepaskan hak atas harta warisan yang dijamin undang-undang',
    'Menyimpangi hak dan kewajiban yang timbul dari hubungan suami istri',
    'Isi yang melanggar kesusilaan atau ketertiban umum',
    'Membebani satu pihak dengan utang melebihi bagiannya',
    'Hal-hal yang merugikan kepentingan anak'
  ];

  const dokumen = [
    'KTP dan Kartu Keluarga kedua calon',
    'Akta kelahiran kedua calon',
    'Paspor dan KITAS/KITAP bila salah satu pihak WNA',
    'Daftar aset yang ingin diatur — tidak perlu sertifikat aslinya di tahap draft',
    'Buku nikah atau akta perkawinan, bila dibuat setelah menikah',
    'Pas foto berwarna, dua lembar masing-masing'
  ];

  const faqs = [
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
  ];

  const statusOptions = [
    'Belum menikah, sedang merencanakan',
    'Akan menikah dalam 3 bulan ke depan',
    'Sudah menikah (perjanjian pasca-nikah)'
  ];

  const kewarganegaraanOptions = ['WNI dengan WNI', 'WNI dengan WNA', 'Keduanya WNA'];

  const asetOptions = [
    'Properti (rumah / tanah / apartemen)',
    'Usaha atau saham perusahaan',
    'Tabungan dan investasi',
    'Aset di luar negeri',
    'Belum ada, tapi ingin mengatur ke depan'
  ];

  const waHref = whatsappHref(
    'Halo 7Magic, saya mau tanya soal perjanjian pranikah yang Rp 3,5 juta. Kondisi kami:'
  );

  // FAQ terstruktur supaya muncul sebagai rich result di Google. Sumbernya
  // array faqs di atas, jadi tidak bisa melenceng dari yang tampil di halaman.
  const faqJsonLd = JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.q,
      acceptedAnswer: { '@type': 'Answer', text: faq.a }
    }))
  });

  const serviceJsonLd = JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'Service',
    serviceType: 'Pembuatan perjanjian pranikah',
    provider: { '@type': 'Organization', name: '7Magic' },
    areaServed: { '@type': 'City', name: 'Jakarta' },
    offers: {
      '@type': 'Offer',
      price: '3500000',
      priceCurrency: 'IDR',
      description: 'Konsultasi, penyusunan draft, akta notaris, dan pencatatan di Dukcapil/KUA.'
    }
  });

  let sending = $state(false);
  let submitted = $state(false);
  let errorMessage = $state('');

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    if (sending) return;

    const form = event.currentTarget as HTMLFormElement;
    const data = new FormData(form);
    const field = (key: string) => String(data.get(key) ?? '').trim();

    // Skema contact-lead di API tidak punya kolom khusus layanan legal, jadi
    // jawaban kualifikasi digabung ke body pesan — sama seperti halaman
    // /bali-event-organizer. Skema tersendiri adalah pekerjaan lanjutan.
    const pesan = [
      'LEAD: Perjanjian Pranikah',
      `Status: ${field('status') || '—'}`,
      `Kewarganegaraan: ${field('kewarganegaraan') || '—'}`,
      `Aset utama: ${field('aset') || '—'}`,
      `Rencana tanggal nikah: ${field('tanggal') || '—'}`,
      '',
      field('catatan') || 'Tidak ada catatan tambahan.'
    ].join('\n');

    sending = true;
    errorMessage = '';

    try {
      const response = await fetch('/api/contact-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: field('nama'),
          phone: field('telepon'),
          email: field('email') || undefined,
          message: pesan,
          source_path: '/perjanjian-pranikah'
        })
      });

      if (!response.ok) {
        errorMessage = 'Pesan gagal terkirim. Coba lagi, atau langsung chat kami di WhatsApp.';
        return;
      }

      submitted = true;
      form.reset();
    } catch {
      errorMessage = 'Pesan gagal terkirim. Coba lagi, atau langsung chat kami di WhatsApp.';
    } finally {
      sending = false;
    }
  }

  const inputClass =
    'rounded-md border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30';
</script>

<svelte:head>
  <title>Perjanjian Pranikah Jakarta — Rp 3,5 Juta All-in, Akta Notaris + Pencatatan | 7Magic</title>
  <meta
    name="description"
    content="Jasa perjanjian pranikah dan pisah harta di Jakarta. Rp 3,5 juta sudah termasuk konsultasi, draft, akta notaris, dan pencatatan di Dukcapil. Bisa juga dibuat setelah menikah. Konsultasi awal gratis."
  />
  <meta
    name="keywords"
    content="perjanjian pranikah, perjanjian pra nikah, biaya perjanjian pranikah, perjanjian pisah harta, perjanjian perkawinan, prenuptial agreement Indonesia, perjanjian pranikah WNA, notaris perjanjian pranikah Jakarta"
  />
  <link rel="canonical" href="https://7magicwedding.com/perjanjian-pranikah" />
  {@html `<script type="application/ld+json">${faqJsonLd}</script>`}
  {@html `<script type="application/ld+json">${serviceJsonLd}</script>`}
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <!-- Hero -->
  <section class="relative flex min-h-[560px] items-center overflow-hidden md:min-h-[620px]">
    <img
      src="/img/prenup/hero-couple.jpg"
      alt="Pasangan tersenyum saat berkonsultasi dengan seorang penasihat hukum"
      class="absolute inset-0 h-full w-full object-cover object-[55%_35%]"
      fetchpriority="high"
    />
    <div class="absolute inset-0 bg-gradient-to-r from-black/70 via-black/35 to-transparent"></div>

    <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-20 lg:px-8">
      <div class="max-w-3xl text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-dark-accent">
          Perjanjian pranikah · Jakarta
        </p>
        <h1 class="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl lg:text-[3.3rem]">
          Perjanjian pranikah, selesai sampai tercatat — {HARGA}
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/90">
          Sudah termasuk konsultasi, penyusunan draft, akta notaris, dan pencatatan di Dukcapil.
          Satu angka, tanpa tagihan susulan. Bisa juga dibuat setelah Anda menikah.
        </p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <a href="#konsultasi" class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}>
            Konsultasi gratis
          </a>
          <a
            href={waHref}
            class={cn(
              buttonVariants({ size: 'lg' }),
              'border border-white/30 bg-white/10 px-7 text-white backdrop-blur hover:bg-white hover:text-brand-ink'
            )}
          >
            <MessageCircleIcon size={18} />
            Tanya lewat WhatsApp
          </a>
        </div>

        <p class="mt-5 text-sm text-white/90">
          Konsultasi awal tidak dipungut biaya. Kalau Anda tidak jadi lanjut, tidak ada tagihan.
        </p>
      </div>
    </div>
  </section>

  <!-- Trust strip -->
  <section class="border-b border-border bg-brand-ink px-5 py-6 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {#each [{ value: HARGA, label: 'All-in, sampai tercatat' }, { value: '2 – 3 minggu', label: 'Dari konsultasi sampai selesai' }, { value: 'Notaris internal', label: 'Tanpa perantara, tanpa markup' }, { value: 'Jakarta', label: 'Jabodetabek, bisa tatap muka' }] as stat}
        <div>
          <p class="font-display text-2xl font-bold text-brand-dark-accent">{stat.value}</p>
          <p class="mt-1 text-sm text-white/72">{stat.label}</p>
        </div>
      {/each}
    </div>
  </section>

  <!-- Harga -->
  <section id="harga" class="scroll-mt-20 bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Harga</p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        Satu angka, dan kami tulis apa saja yang ada di dalamnya
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Keluhan paling umum soal jasa perjanjian pranikah bukan harganya, tapi tagihan yang muncul
        belakangan. Jadi ini isinya, hitam di atas putih.
      </p>

      <div class="mt-10 grid gap-5 lg:grid-cols-[1fr_1.2fr] lg:items-start">
        <!-- Pembanding harga -->
        <div class="grid gap-4">
          {#each pembanding as baris}
            <div
              class={cn(
                'rounded-md border p-6',
                baris.ours
                  ? 'border-brand-gold bg-background shadow-lg ring-1 ring-brand-gold/20'
                  : 'border-border bg-background/60'
              )}
            >
              <p class="text-sm font-medium text-muted-foreground">{baris.label}</p>
              <p
                class={cn(
                  'mt-2 font-display text-2xl font-bold',
                  baris.ours ? 'text-brand-gold-hover' : 'text-foreground/70'
                )}
              >
                {baris.harga}
              </p>
              <p class="mt-2 text-sm leading-6 text-muted-foreground">{baris.catatan}</p>
            </div>
          {/each}
          <p class="text-xs leading-6 text-muted-foreground">
            Kisaran pasar di atas adalah rentang tarif notaris di Jakarta yang dipublikasikan secara
            umum, bukan tarif satu kantor tertentu. Tarif tiap notaris berbeda-beda menurut
            kompleksitas perjanjian.
          </p>
        </div>

        <!-- Rincian -->
        <div class="rounded-md border border-border bg-background p-7">
          <div class="flex items-baseline gap-2">
            <span class="font-display text-3xl font-bold">{HARGA}</span>
            <span class="text-sm text-muted-foreground">sekali bayar</span>
          </div>
          <span
            class="mt-4 inline-block w-fit rounded-full bg-brand-gold px-3 py-1 text-xs font-semibold uppercase tracking-widest text-white"
          >
            Harga perkenalan
          </span>

          <h3 class="mt-6 font-display text-base font-semibold">Sudah termasuk</h3>
          <ul class="mt-3 grid gap-2.5">
            {#each termasuk as item}
              <li class="flex gap-3 text-[15px] leading-7">
                <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                <span>{item}</span>
              </li>
            {/each}
          </ul>

          <h3 class="mt-7 border-t border-border pt-6 font-display text-base font-semibold">
            Dikutip terpisah
          </h3>
          <ul class="mt-3 grid gap-2.5">
            {#each tidakTermasuk as item}
              <li class="flex gap-3 text-[15px] leading-7 text-muted-foreground">
                <XIcon size={17} class="mt-1.5 shrink-0 text-muted-foreground/70" />
                <span>{item}</span>
              </li>
            {/each}
          </ul>

          <a href="#konsultasi" class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'mt-7 w-full')}>
            Mulai dari konsultasi gratis
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- Untuk siapa -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      Siapa yang biasanya butuh
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      Empat kondisi yang paling sering datang ke meja kami
    </h2>

    <div class="mt-10 grid gap-5 sm:grid-cols-2">
      {#each segmen as item}
        <!-- bg-brand-ink: see /paket-sangjit — keeps an undecoded card dark
             instead of flashing white under the gradient overlay. -->
        <article class="group relative h-[320px] overflow-hidden rounded-md bg-brand-ink">
          <img
            src={item.image}
            alt={item.alt}
            loading="lazy"
            class="absolute inset-0 h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
          <!-- Stop positions, not an even wash: these four photos are bright
               (a lit office, a white ring box), so an evenly spread overlay
               either left the caption unreadable or greyed out the whole
               image. The darkness is now concentrated in the bottom ~55%
               where the text sits, and clears entirely by 85% so the top of
               the photo stays clean. -->
          <div
            class="absolute inset-0 bg-gradient-to-t from-black/95 from-0% via-black/75 via-40% to-transparent to-85%"
          ></div>
          <div
            class="absolute inset-x-0 bottom-0 p-6 text-white [text-shadow:0_1px_10px_rgba(0,0,0,0.6)]"
          >
            <h3 class="font-display text-xl font-semibold">{item.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-white/90">{item.copy}</p>
          </div>
        </article>
      {/each}
    </div>
  </section>

  <!-- Dasar hukum -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        Dasar hukum
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        Ini bukan tren impor. Ini diatur undang-undang.
      </h2>

      <div class="mt-10 grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
        <div class="grid gap-4">
          {#each dasarHukum as item}
            <div class="rounded-md border border-border bg-background p-6">
              <span
                class="inline-block rounded-full bg-brand-gold-soft px-3 py-1 text-xs font-semibold uppercase tracking-widest text-brand-gold-hover"
              >
                {item.rujukan}
              </span>
              <h3 class="mt-4 font-display text-lg font-semibold">{item.title}</h3>
              <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{item.copy}</p>
            </div>
          {/each}

          <!-- Bukan kartu rujukan hukum tapi peringatan praktis, jadi dibedakan
               dengan garis aksen di kiri — ini poin yang paling sering terlewat
               dan paling menentukan untuk urusan properti. -->
          <div class="rounded-md border border-border border-l-4 border-l-brand-gold bg-background p-6">
            <h3 class="font-display text-lg font-semibold">Yang paling sering terlewat</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">
              Bukan di aktanya, melainkan di <strong class="font-semibold text-foreground"
                >pencatatannya</strong
              >. Akta notaris yang tidak dicatatkan ke Dukcapil atau KUA mengikat Anda berdua, tapi
              tidak mengikat pihak ketiga — bank, kreditur, atau BPN. Untuk urusan properti, justru
              pihak ketiga inilah yang penting.
            </p>
          </div>

          {#if notaris.nama}
            <div class="rounded-md border border-border bg-background p-6">
              <p class="text-sm text-muted-foreground">Akta diterbitkan oleh</p>
              <p class="mt-1 font-display text-lg font-semibold">{notaris.nama}</p>
              <p class="mt-1 text-sm text-muted-foreground">
                {notaris.sk}{notaris.wilayah ? ` · Wilayah kerja ${notaris.wilayah}` : ''}
              </p>
            </div>
          {/if}
        </div>

        <img
          src="/img/prenup/deed.jpg"
          alt="Tangan menandatangani dokumen perjanjian dengan pena"
          loading="lazy"
          class="h-[420px] w-full rounded-md object-cover lg:sticky lg:top-24"
        />
      </div>
    </div>
  </section>

  <!-- Proses -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div class="grid gap-10 lg:grid-cols-[0.85fr_1.15fr] lg:gap-16">
      <div class="lg:sticky lg:top-24 lg:self-start">
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
          Prosesnya
        </p>
        <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">
          Empat langkah, dua di antaranya kami yang kerjakan
        </h2>
        <p class="mt-4 max-w-md text-[15px] leading-7 text-muted-foreground">
          Anda hanya perlu hadir di langkah pertama dan ketiga. Sisanya urusan kami, dan Anda
          dikabari di setiap perpindahan tahap.
        </p>
      </div>

      <!-- Timeline. Rail digambar dari border kiri <ol>, titiknya ditarik keluar
           dengan -left agar duduk persis di atas garis. Dipakai <ol> karena
           urutannya memang bermakna: langkah 4 tidak bisa mendahului langkah 3. -->
      <ol class="relative border-l border-border pl-8 sm:pl-10">
        {#each langkah as step, index}
          <li class="relative pb-10 last:pb-0">
            <span
              class="absolute -left-[calc(2rem+1px)] flex size-8 -translate-x-1/2 items-center justify-center rounded-full bg-brand-gold font-display text-xs font-bold text-white ring-4 ring-background sm:-left-[calc(2.5rem+1px)]"
              aria-hidden="true"
            >
              {String(index + 1).padStart(2, '0')}
            </span>

            <span
              class="inline-block rounded-full bg-brand-gold-soft px-3 py-1 text-xs font-semibold uppercase tracking-widest text-brand-gold-hover"
            >
              {step.waktu}
            </span>
            <h3 class="mt-3 font-display text-lg font-semibold">{step.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{step.copy}</p>
          </li>
        {/each}
      </ol>
    </div>
  </section>

  <!-- Bisa / tidak bisa diatur -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Batasannya</p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        Yang boleh diatur, dan yang tidak akan kami tuliskan
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Perjanjian yang memuat pasal terlarang bisa batal seluruhnya di pengadilan. Lebih baik Anda
        tahu batasnya sekarang daripada mengetahuinya saat perjanjian itu dibutuhkan.
      </p>

      <div class="mt-10 grid gap-5 lg:grid-cols-2">
        <div class="rounded-md border border-border bg-background p-7">
          <h3 class="font-display text-lg font-semibold">Bisa diatur</h3>
          <ul class="mt-4 grid gap-2.5">
            {#each bisaDiatur as item}
              <li class="flex gap-3 text-[15px] leading-7">
                <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                <span>{item}</span>
              </li>
            {/each}
          </ul>
        </div>

        <div class="rounded-md border border-border bg-background p-7">
          <h3 class="font-display text-lg font-semibold">Tidak bisa diatur</h3>
          <ul class="mt-4 grid gap-2.5">
            {#each tidakBisaDiatur as item}
              <li class="flex gap-3 text-[15px] leading-7 text-muted-foreground">
                <XIcon size={17} class="mt-1.5 shrink-0 text-destructive/70" />
                <span>{item}</span>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- Dokumen -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div class="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
      <img
        src="/img/prenup/documents.jpg"
        alt="Berkas dan dokumen tertata di atas meja kayu"
        loading="lazy"
        class="h-[360px] w-full rounded-md object-cover"
      />
      <div>
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
          Persiapan
        </p>
        <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">
          Dokumen yang perlu Anda siapkan
        </h2>
        <p class="mt-4 text-[15px] leading-7 text-muted-foreground">
          Tidak perlu lengkap saat konsultasi pertama. Ini daftar yang dibutuhkan sampai hari
          penandatanganan.
        </p>
        <ul class="mt-6 grid gap-2.5">
          {#each dokumen as item}
            <li class="flex gap-3 text-[15px] leading-7">
              <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
              <span>{item}</span>
            </li>
          {/each}
        </ul>
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-4xl">
      <h2 class="font-display text-3xl font-bold md:text-4xl">Pertanyaan yang paling sering masuk</h2>
      <div class="mt-8 grid gap-3">
        {#each faqs as faq}
          <details class="group rounded-md border border-border bg-background p-6">
            <summary class="cursor-pointer list-none font-display text-lg font-semibold marker:hidden">
              {faq.q}
            </summary>
            <p class="mt-3 text-[15px] leading-7 text-muted-foreground">{faq.a}</p>
          </details>
        {/each}
      </div>
    </div>
  </section>

  <!-- Form -->
  <section id="konsultasi" class="scroll-mt-20 bg-brand-ink px-5 py-16 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[0.85fr_1.15fr]">
      <div>
        <h2 class="font-display text-3xl font-bold md:text-4xl">Ceritakan kondisi Anda</h2>
        <p class="mt-4 text-[15px] leading-7 text-white/75">
          Empat jawaban sudah cukup untuk kami menilai apakah kasus Anda masuk paket {HARGA} atau
          perlu dikutip terpisah. Kami balas di hari kerja yang sama.
        </p>

        <div class="mt-8 rounded-md border border-white/15 bg-white/5 p-6">
          <p class="text-sm text-white/70">Lebih enak ngobrol langsung?</p>
          <a
            href={waHref}
            class={cn(
              buttonVariants({ size: 'lg' }),
              'mt-3 w-full bg-brand-success text-white hover:bg-brand-success-hover'
            )}
          >
            <MessageCircleIcon size={18} />
            WhatsApp {whatsappDisplay}
          </a>
        </div>

        <p class="mt-6 text-sm leading-7 text-white/60">
          Apa pun yang Anda ceritakan di sini kami perlakukan sebagai rahasia klien, termasuk kalau
          Anda akhirnya tidak jadi menggunakan jasa kami.
        </p>
      </div>

      <div class="rounded-md bg-background p-7 text-foreground">
        {#if submitted}
          <div class="flex flex-col items-center gap-4 py-12 text-center">
            <span
              class="flex size-14 items-center justify-center rounded-full bg-brand-gold-soft text-brand-gold-hover"
            >
              <CheckIcon size={28} />
            </span>
            <h3 class="font-display text-xl font-semibold">Sudah kami terima</h3>
            <p class="max-w-sm text-[15px] leading-7 text-muted-foreground">
              Kami hubungi di hari kerja yang sama. Kalau tanggal nikah Anda mepet, chat kami di
              WhatsApp dan sebutkan tanggalnya.
            </p>
            <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp' }), 'mt-2')}>
              <MessageCircleIcon size={17} />
              Chat sekarang
            </a>
          </div>
        {:else}
          <form onsubmit={submit} class="grid gap-4">
            <div class="grid gap-1.5">
              <label for="pn-status" class="text-[13px] font-medium">
                Status Anda <span class="text-destructive" aria-hidden="true">*</span>
              </label>
              <select id="pn-status" name="status" required class={inputClass}>
                <option value="">Pilih salah satu</option>
                {#each statusOptions as opt}
                  <option value={opt}>{opt}</option>
                {/each}
              </select>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="pn-warga" class="text-[13px] font-medium">
                  Kewarganegaraan <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <select id="pn-warga" name="kewarganegaraan" required class={inputClass}>
                  <option value="">Pilih salah satu</option>
                  {#each kewarganegaraanOptions as opt}
                    <option value={opt}>{opt}</option>
                  {/each}
                </select>
              </div>
              <div class="grid gap-1.5">
                <label for="pn-tanggal" class="text-[13px] font-medium">
                  Rencana tanggal nikah <span class="text-muted-foreground">(kira-kira saja)</span>
                </label>
                <input id="pn-tanggal" name="tanggal" type="date" class={inputClass} />
              </div>
            </div>

            <div class="grid gap-1.5">
              <label for="pn-aset" class="text-[13px] font-medium">Aset utama yang ingin diatur</label>
              <select id="pn-aset" name="aset" class={inputClass}>
                <option value="">Belum yakin</option>
                {#each asetOptions as opt}
                  <option value={opt}>{opt}</option>
                {/each}
              </select>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="pn-nama" class="text-[13px] font-medium">
                  Nama Anda <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input id="pn-nama" name="nama" required autocomplete="name" class={inputClass} />
              </div>
              <div class="grid gap-1.5">
                <label for="pn-telepon" class="text-[13px] font-medium">
                  Nomor WhatsApp <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="pn-telepon"
                  name="telepon"
                  required
                  autocomplete="tel"
                  placeholder="08xx xxxx xxxx"
                  class={inputClass}
                />
              </div>
            </div>

            <div class="grid gap-1.5">
              <label for="pn-email" class="text-[13px] font-medium">
                Email <span class="text-muted-foreground">(opsional)</span>
              </label>
              <input id="pn-email" name="email" type="email" autocomplete="email" class={inputClass} />
            </div>

            <div class="grid gap-1.5">
              <label for="pn-catatan" class="text-[13px] font-medium">
                Ada yang perlu kami tahu?
              </label>
              <textarea
                id="pn-catatan"
                name="catatan"
                rows="3"
                placeholder="Mau beli rumah bulan depan, pasangan WNA, sertifikat masih atas nama orang tua…"
                class={inputClass}
              ></textarea>
            </div>

            {#if errorMessage}
              <p class="text-sm text-destructive" role="alert">{errorMessage}</p>
            {/if}

            <Button type="submit" variant="gold" size="lg" class="w-full" disabled={sending}>
              {sending ? 'Mengirim…' : 'Kirim & minta konsultasi gratis'}
            </Button>
            <p class="text-center text-xs text-muted-foreground">
              Data ini kami pakai untuk menghubungi Anda soal perjanjian pranikah. Tidak untuk yang
              lain.
            </p>
          </form>
        {/if}
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
