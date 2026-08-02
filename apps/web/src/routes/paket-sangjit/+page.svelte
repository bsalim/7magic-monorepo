<script lang="ts">
  import CheckIcon from '@lucide/svelte/icons/check';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { cn } from '$lib/utils';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';

  /**
   * Landing page akuisisi untuk paket sangjit (Jakarta).
   *
   * Bahasa Indonesia saja, copy di-hardcode — alasan yang sama seperti
   * /perjanjian-pranikah dan /bali-event-organizer.
   *
   * Kata kunci yang dibidik (riset pasar Jakarta): "paket sangjit", "sangjit
   * Jakarta", "dekorasi sangjit", "isi baki sangjit", "isi nampan sangjit",
   * "susunan acara sangjit", "seserahan sangjit", "MC sangjit", "harga sangjit".
   *
   * Bagian "isi baki" dan "susunan acara" sengaja ditulis lengkap: itu yang
   * dicari orang lewat Google, dan halaman yang menjawabnya yang dapat
   * peringkat — bukan halaman yang cuma memajang harga.
   */

  // ---------------------------------------------------------------------------
  // Harga sengaja tidak ditampilkan — penawaran disusun per acara dan dikirim
  // setelah calon klien menghubungi kami. Yang membedakan paket di halaman ini
  // adalah skala dan isinya, bukan angkanya.
  //
  // Isi paket masih perlu dikonfirmasi 7Magic sebelum publikasi, terutama
  // jumlah pembawa baki, cakupan dokumentasi, dan apakah isi baki benar-benar
  // kami sediakan.
  // ---------------------------------------------------------------------------
  const paket = [
    {
      name: 'Sangjit Intimate',
      skala: 'Di rumah · sampai 30 tamu',
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
      name: 'Sangjit Signature',
      skala: 'Rumah atau restoran · sampai 60 tamu',
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
      name: 'Sangjit Grand',
      skala: 'Restoran atau hotel · 100 tamu ke atas',
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
  ];

  const layanan = [
    {
      image: '/img/sangjit/decor.jpg',
      alt: 'Mempelai wanita berbusana merah di depan dekorasi sangjit bermotif Double Happiness',
      title: 'Dekorasi & backdrop',
      copy: 'Merah-emas klasik atau nuansa pastel modern. Kami pasang pagi hari, sebelum rombongan datang.'
    },
    {
      image: '/img/sangjit/trays.jpg',
      alt: 'Baki merah berisi seserahan sangjit dengan aksara Double Happiness keemasan',
      title: 'Baki & penataan isi',
      copy: 'Baki, penataan, dan hitungannya. Jumlah selalu genap, dan angka empat tidak pernah kami pakai.'
    },
    {
      image: '/img/sangjit/couple.jpg',
      alt: 'Mempelai wanita berbusana xiuhefu merah keemasan bersama orang tuanya',
      title: 'Busana & pembawa baki',
      copy: 'Cheongsam untuk pembawa baki, dan sewa busana untuk mempelai bila diperlukan.'
    },
    {
      image: '/img/sangjit/angpao.jpg',
      alt: 'Amplop angpao merah dan sepasang cincin emas',
      title: 'Angpao & uang susu',
      copy: 'Amplop, tulisan aksaranya, dan pembagiannya. Bagian yang paling sering bikin salah paham.'
    },
    {
      image: '/img/sangjit/tea.jpg',
      alt: 'Seorang perempuan menuangkan teh untuk anggota keluarga',
      title: 'Upacara minum teh',
      copy: 'Bila keluarga menginginkan, prosesi teh kami rangkai menyatu dengan acara sangjit.'
    },
    {
      image: '/img/sangjit/embrace.jpg',
      alt: 'Mempelai wanita berbusana merah dipeluk ibunya',
      title: 'Koordinator & MC',
      copy: 'Satu orang yang tahu urutannya, supaya orang tua Anda tidak jadi panitia di acara sendiri.'
    }
  ];

  const susunanAcara = [
    {
      jam: '08.00',
      title: 'Kami pasang, Anda sarapan',
      items: [
        'Tim dekorasi datang dan memasang backdrop serta meja sangjit',
        'Baki ditata dan dihitung ulang bersama perwakilan keluarga pria',
        'Briefing singkat untuk pembawa baki dan MC'
      ]
    },
    {
      jam: '10.00',
      title: 'Rombongan pria tiba',
      items: [
        'Rombongan dipimpin anggota keluarga yang dituakan, jumlahnya genap',
        'Penyambutan di depan rumah atau pintu restoran',
        'Penyerahan baki dari pembawa baki pihak pria ke pihak wanita'
      ]
    },
    {
      jam: '10.30',
      title: 'Ramah tamah dan penyerahan',
      items: [
        'Perkenalan kedua keluarga, dipandu MC dalam dua bahasa',
        'Baki dibawa masuk, pihak wanita mengambil bagiannya',
        'Sisanya dikembalikan ke pihak pria — tetap dalam jumlah genap'
      ]
    },
    {
      jam: '12.00',
      title: 'Foto dan jamuan',
      items: [
        'Foto keluarga besar, lalu foto kedua mempelai',
        'Makan siang bersama',
        'Rombongan pria berpamitan sebelum sore — tidak menginap, sesuai adat'
      ]
    }
  ];

  // Isi baki paling umum di Jakarta. Tiap keluarga punya versinya sendiri;
  // koordinator kami mengonfirmasi daftar final ke kedua keluarga sebelum hari H.
  const isiBaki = [
    {
      nama: 'Angpao uang susu',
      makna: 'Tanda terima kasih untuk orang tua mempelai wanita. Diletakkan di dua amplop merah terpisah.'
    },
    {
      nama: 'Angpao uang pesta',
      makna: 'Sumbangan pihak pria untuk biaya resepsi di pihak wanita.'
    },
    {
      nama: 'Perhiasan emas',
      makna: 'Kalung, gelang, atau cincin untuk calon mempelai wanita. Biasanya dipakaikan hari itu juga.'
    },
    {
      nama: 'Kain atau busana',
      makna: 'Bahan kain, cheongsam, atau satu set pakaian untuk calon mempelai wanita.'
    },
    {
      nama: 'Kue mangkok merah',
      makna: 'Delapan belas potong. Melambangkan rezeki yang mengembang dan berlimpah.'
    },
    {
      nama: 'Kue lapis legit atau kue keranjang',
      makna: 'Lapisannya melambangkan rezeki yang bertingkat-tingkat dan hubungan yang lengket.'
    },
    {
      nama: 'Buah-buahan',
      makna: 'Apel, pir, jeruk, atau anggur — dalam jumlah genap. Lambang kebahagiaan dan kesejahteraan.'
    },
    {
      nama: 'Dua botol arak atau sampanye',
      makna: 'Dibuka bersama sebagai tanda restu kedua keluarga.'
    },
    {
      nama: 'Kaki babi atau daging kalengan',
      makna: 'Dua belas kaleng, jumlah genap. Bisa diganti bila keluarga tidak mengonsumsinya.'
    },
    {
      nama: 'Lilin merah sepasang',
      makna: 'Bergambar naga dan burung hong, lambang pasangan suami istri.'
    },
    {
      nama: 'Lengkeng dan leci kalengan',
      makna: 'Harapan agar keturunan segera datang dan keluarga terus bertambah.'
    },
    {
      nama: 'Sepasang ayam atau bebek',
      makna: 'Dipakai sebagian keluarga sebagai lambang kesetiaan. Sifatnya tidak wajib.'
    }
  ];

  const adat = [
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
  ];

  const langkah = [
    {
      title: 'Ceritakan rencananya',
      copy: 'Tanggal, lokasi, dan kira-kira berapa orang. Lima menit di WhatsApp sudah cukup untuk mulai.',
      waktu: 'Hari 1'
    },
    {
      title: 'Kami kirim penawaran',
      copy: 'Lengkap dengan sketsa dekorasi, daftar isi baki, dan susunan acara per jam — bukan sekadar daftar harga.',
      waktu: '2 hari kerja'
    },
    {
      title: 'Kami temui kedua keluarga',
      copy: 'Ini bagian yang paling menentukan. Kami samakan versi adat kedua keluarga sebelum apa pun dipesan.',
      waktu: 'Setelah Anda setuju'
    },
    {
      title: 'Hari H, Anda tinggal hadir',
      copy: 'Tim datang pukul delapan pagi. Orang tua Anda datang sebagai tuan rumah, bukan sebagai panitia.',
      waktu: 'Hari acara'
    }
  ];

  const faqs = [
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
  ];

  const lokasiOptions = [
    'Di rumah',
    'Restoran',
    'Hotel atau gedung',
    'Belum ditentukan — mohon dibantu'
  ];

  const paketOptions = [
    'Sangjit Intimate',
    'Sangjit Signature',
    'Sangjit Grand',
    'Belum tahu, mohon disarankan'
  ];

  const waHref = whatsappHref('Halo 7Magic, saya mau tanya soal paket sangjit. Rencana kami:');

  const faqJsonLd = JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.q,
      acceptedAnswer: { '@type': 'Answer', text: faq.a }
    }))
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

    const pesan = [
      'LEAD: Paket Sangjit',
      `Tanggal sangjit: ${field('tanggal') || '—'}`,
      `Lokasi: ${field('lokasi') || '—'}`,
      `Perkiraan tamu: ${field('tamu') || '—'}`,
      `Paket diminati: ${field('paket') || '—'}`,
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
          source_path: '/paket-sangjit'
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
  <title>Paket Sangjit Jakarta — Dekorasi, Baki Seserahan, MC & Dokumentasi | 7Magic</title>
  <meta
    name="description"
    content="Paket sangjit Jakarta: dekorasi, baki seserahan lengkap dengan isinya, pembawa baki, MC dwibahasa, dan dokumentasi. Susunan acara dan isi 12 baki kami jelaskan lengkap. Penawaran dalam dua hari kerja."
  />
  <meta
    name="keywords"
    content="paket sangjit, sangjit Jakarta, dekorasi sangjit, isi baki sangjit, isi nampan sangjit, susunan acara sangjit, seserahan sangjit, MC sangjit, harga sangjit Jakarta"
  />
  <link rel="canonical" href="https://7magicwedding.com/paket-sangjit" />
  {@html `<script type="application/ld+json">${faqJsonLd}</script>`}
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <!-- Hero -->
  <section class="relative flex min-h-[560px] items-center overflow-hidden md:min-h-[640px]">
    <img
      src="/img/sangjit/hero.jpg"
      alt="Keluarga menjalankan prosesi pernikahan tradisional Tionghoa dengan lampion merah"
      class="absolute inset-0 h-full w-full object-cover object-[50%_45%]"
      fetchpriority="high"
    />
    <div class="absolute inset-0 bg-gradient-to-r from-black/70 via-black/30 to-transparent"></div>

    <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-20 lg:px-8">
      <div class="max-w-3xl text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-dark-accent">
          Paket sangjit · Jakarta
        </p>
        <h1 class="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl lg:text-[3.3rem]">
          Sangjit yang berjalan rapi, tanpa orang tua Anda jadi panitia
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/90">
          Dekorasi, baki seserahan lengkap dengan hitungan adatnya, pembawa baki, MC dwibahasa, dan
          dokumentasi. Kami samakan dulu versi adat kedua keluarga sebelum apa pun dipesan.
        </p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <a href="#penawaran" class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}>
            Minta penawaran
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
          Sebutkan tanggal, lokasi, dan perkiraan jumlah tamu. Penawaran kami kirim dalam dua hari
          kerja.
        </p>
      </div>
    </div>
  </section>

  <!-- Trust strip -->
  <section class="border-b border-border bg-brand-ink px-5 py-6 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {#each [{ value: '18+', label: 'Tahun mengurus acara' }, { value: '1000+', label: 'Acara terselenggara' }, { value: '100+', label: 'Vendor dalam jaringan kami' }, { value: 'Jabodetabek', label: 'Tim datang ke lokasi Anda' }] as stat}
        <div>
          <p class="font-display text-2xl font-bold text-brand-dark-accent">{stat.value}</p>
          <p class="mt-1 text-sm text-white/72">{stat.label}</p>
        </div>
      {/each}
    </div>
  </section>

  <!-- Layanan -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      Yang kami tangani
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      Enam bagian, dan hampir semuanya menyangkut hitungan adat
    </h2>

    <div class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {#each layanan as item}
        <!-- bg-brand-ink: the gradient overlay sits on a dark base, so a card
             whose photo has not decoded yet reads as dark rather than as a
             blank white box. -->
        <article class="group relative h-[340px] overflow-hidden rounded-md bg-brand-ink">
          <img
            src={item.image}
            alt={item.alt}
            loading="lazy"
            class="absolute inset-0 h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/45 to-black/10"></div>
          <div class="absolute inset-x-0 bottom-0 p-6 text-white">
            <h3 class="font-display text-xl font-semibold">{item.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-white/85">{item.copy}</p>
          </div>
        </article>
      {/each}
    </div>
  </section>

  <!-- Paket -->
  <section id="paket" class="scroll-mt-20 bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Paket</p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        Tiga paket, dan sebagian besar keluarga memilih yang tengah
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Setiap sangjit berbeda — lokasi, jumlah baki, skala dekorasi, dan apakah acaranya digabung
        dengan jamuan makan. Karena itu kami tidak memasang harga paket di sini, melainkan menyusun
        penawaran sesuai rencana Anda. Sebutkan tanggal dan perkiraan jumlah tamu, penawarannya
        kami kirim dalam dua hari kerja.
      </p>

      <div class="mt-10 grid gap-5 lg:grid-cols-3">
        {#each paket as p}
          <div
            class={cn(
              'flex flex-col rounded-md border bg-background p-7',
              p.featured ? 'border-brand-gold shadow-lg ring-1 ring-brand-gold/20' : 'border-border'
            )}
          >
            {#if p.featured}
              <span
                class="mb-4 w-fit rounded-full bg-brand-gold px-3 py-1 text-xs font-semibold uppercase tracking-widest text-white"
              >
                Paling sering diambil
              </span>
            {/if}
            <h3 class="font-display text-xl font-semibold">{p.name}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{p.summary}</p>

            <!-- Where the price used to sit. The slot is kept so the three
                 cards still align, and the scale line does the filtering job
                 the number used to do. -->
            <div class="mt-5">
              <p class="font-display text-lg font-semibold text-brand-gold-hover">
                Hubungi kami untuk harga
              </p>
              <p class="mt-1 text-sm text-muted-foreground">{p.skala}</p>
            </div>

            <ul class="mt-6 grid flex-1 content-start gap-2.5 border-t border-border pt-6">
              {#each p.includes as item}
                <li class="flex gap-3 text-[15px] leading-7">
                  <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                  <span>{item}</span>
                </li>
              {/each}
            </ul>

            <a
              href="#penawaran"
              class={cn(buttonVariants({ variant: p.featured ? 'gold' : 'outline' }), 'mt-7 w-full')}
            >
              Minta penawaran paket ini
            </a>
          </div>
        {/each}
      </div>

      <div class="mt-8 rounded-md border border-border bg-background p-6">
        <h3 class="font-display text-base font-semibold">Yang tidak masuk paket</h3>
        <p class="mt-2 text-[15px] leading-7 text-muted-foreground">
          Perhiasan emas, isi angpao, dan uang susu tetap disiapkan keluarga — bagian itu memang
          bukan wilayah vendor. Sewa tempat, jamuan makan, dan barongsai dihitung terpisah dan kami
          cantumkan di penawaran, bukan diberitahukan belakangan.
        </p>
      </div>
    </div>
  </section>

  <!-- Susunan acara -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div class="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
      <div>
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
          Susunan acara
        </p>
        <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">
          Seperti apa jalannya sangjit dari pagi
        </h2>
        <p class="mt-4 max-w-xl text-[15px] leading-7 text-muted-foreground">
          Ini bentuk acara yang paling sering kami jalankan. Punya Anda mungkin berbeda — tapi
          inilah tingkat kedetailan yang Anda dapat di penawaran kami.
        </p>

        <div class="mt-8 grid gap-4">
          {#each susunanAcara as blok}
            <div class="rounded-md border border-border bg-background p-6">
              <div class="flex items-baseline gap-3">
                <span
                  class="rounded-full bg-brand-gold-soft px-3 py-1 text-xs font-semibold uppercase tracking-widest text-brand-gold-hover"
                >
                  {blok.jam}
                </span>
                <h3 class="font-display text-lg font-semibold">{blok.title}</h3>
              </div>
              <ul class="mt-4 grid gap-2.5">
                {#each blok.items as item}
                  <li class="flex gap-3 text-[15px] leading-7 text-muted-foreground">
                    <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                    <span>{item}</span>
                  </li>
                {/each}
              </ul>
            </div>
          {/each}
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
        <img
          src="/img/sangjit/gifts.jpg"
          alt="Rombongan keluarga membawa seserahan bertanda Double Happiness"
          loading="lazy"
          class="h-64 w-full rounded-md object-cover"
        />
        <img
          src="/img/sangjit/trays.jpg"
          alt="Baki merah berisi seserahan dengan aksara Double Happiness"
          loading="lazy"
          class="h-64 w-full rounded-md object-cover"
        />
        <img
          src="/img/sangjit/embrace.jpg"
          alt="Mempelai wanita berbusana merah dipeluk ibunya"
          loading="lazy"
          class="h-64 w-full rounded-md object-cover object-top sm:col-span-2 lg:col-span-1"
        />
      </div>
    </div>
  </section>

  <!-- Isi baki -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Isi baki</p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        Dua belas baki, dan arti masing-masing
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Daftar ini yang paling sering ditanyakan sebelum orang menghubungi vendor mana pun, jadi
        kami tulis terbuka. Tiap keluarga punya versinya sendiri — koordinator kami mengonfirmasi
        daftar finalnya ke kedua keluarga sebelum hari H.
      </p>

      <div class="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {#each isiBaki as item, index}
          <div class="rounded-md border border-border bg-background p-6">
            <div class="flex items-baseline gap-3">
              <span class="font-display text-sm font-bold text-brand-warm-deep">
                {String(index + 1).padStart(2, '0')}
              </span>
              <h3 class="font-display text-base font-semibold">{item.nama}</h3>
            </div>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{item.makna}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Aturan adat -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      Yang gampang keliru
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      Empat aturan yang paling sering bikin salah paham
    </h2>

    <div class="mt-10 grid gap-5 md:grid-cols-2">
      {#each adat as item}
        <div class="rounded-md border border-border bg-background p-7">
          <h3 class="font-display text-lg font-semibold">{item.title}</h3>
          <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{item.copy}</p>
        </div>
      {/each}
    </div>
  </section>

  <!-- Cara kerja -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        Cara kerja kami
      </p>
      <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">Empat langkah, dua di antaranya kami</h2>

      <div class="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
        {#each langkah as step, index}
          <div class="rounded-md border border-border bg-background p-6">
            <span class="font-display text-3xl font-bold text-brand-warm-deep">
              {String(index + 1).padStart(2, '0')}
            </span>
            <h3 class="mt-3 font-display text-lg font-semibold">{step.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{step.copy}</p>
            <p class="mt-4 text-sm font-semibold text-brand-gold-hover">{step.waktu}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section class="mx-auto max-w-4xl px-5 py-16 lg:px-8">
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
  </section>

  <!-- Form -->
  <section id="penawaran" class="scroll-mt-20 bg-brand-ink px-5 py-16 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[0.85fr_1.15fr]">
      <div>
        <h2 class="font-display text-3xl font-bold md:text-4xl">Ceritakan rencana Anda</h2>
        <p class="mt-4 text-[15px] leading-7 text-white/75">
          Empat jawaban sudah cukup untuk mulai. Kami balas dalam dua hari kerja dengan sketsa
          dekorasi, daftar isi baki, dan susunan acara per jam.
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
              Penawaran kami kirim dalam dua hari kerja. Kalau tanggal Anda lebih mepet dari itu,
              chat kami di WhatsApp dan sebutkan tanggalnya.
            </p>
            <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp' }), 'mt-2')}>
              <MessageCircleIcon size={17} />
              Chat sekarang
            </a>
          </div>
        {:else}
          <form onsubmit={submit} class="grid gap-4">
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="sj-tanggal" class="text-[13px] font-medium">
                  Tanggal sangjit <span class="text-muted-foreground">(kira-kira saja)</span>
                </label>
                <input id="sj-tanggal" name="tanggal" type="date" class={inputClass} />
              </div>
              <div class="grid gap-1.5">
                <label for="sj-lokasi" class="text-[13px] font-medium">
                  Lokasi <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <select id="sj-lokasi" name="lokasi" required class={inputClass}>
                  <option value="">Pilih salah satu</option>
                  {#each lokasiOptions as opt}
                    <option value={opt}>{opt}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="sj-tamu" class="text-[13px] font-medium">
                  Perkiraan jumlah tamu <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="sj-tamu"
                  name="tamu"
                  type="number"
                  min="1"
                  required
                  placeholder="mis. 40"
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="sj-paket" class="text-[13px] font-medium">Paket yang diminati</label>
                <select id="sj-paket" name="paket" class={inputClass}>
                  <option value="">Belum tahu</option>
                  {#each paketOptions as opt}
                    <option value={opt}>{opt}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="sj-nama" class="text-[13px] font-medium">
                  Nama Anda <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input id="sj-nama" name="nama" required autocomplete="name" class={inputClass} />
              </div>
              <div class="grid gap-1.5">
                <label for="sj-telepon" class="text-[13px] font-medium">
                  Nomor WhatsApp <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="sj-telepon"
                  name="telepon"
                  required
                  autocomplete="tel"
                  placeholder="08xx xxxx xxxx"
                  class={inputClass}
                />
              </div>
            </div>

            <div class="grid gap-1.5">
              <label for="sj-email" class="text-[13px] font-medium">
                Email <span class="text-muted-foreground">(opsional)</span>
              </label>
              <input id="sj-email" name="email" type="email" autocomplete="email" class={inputClass} />
            </div>

            <div class="grid gap-1.5">
              <label for="sj-catatan" class="text-[13px] font-medium">
                Ada yang perlu kami tahu?
              </label>
              <textarea
                id="sj-catatan"
                name="catatan"
                rows="3"
                placeholder="Keluarga minta 16 baki, sekalian lamaran, ada tante yang ingin barongsai…"
                class={inputClass}
              ></textarea>
            </div>

            {#if errorMessage}
              <p class="text-sm text-destructive" role="alert">{errorMessage}</p>
            {/if}

            <Button type="submit" variant="gold" size="lg" class="w-full" disabled={sending}>
              {sending ? 'Mengirim…' : 'Kirim & minta penawaran'}
            </Button>
            <p class="text-center text-xs text-muted-foreground">
              Data ini kami pakai untuk menyusun penawaran sangjit Anda. Tidak untuk yang lain.
            </p>
          </form>
        {/if}
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
