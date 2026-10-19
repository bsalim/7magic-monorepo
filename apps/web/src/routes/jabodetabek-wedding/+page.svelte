<script lang="ts">
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import MapPinIcon from '@lucide/svelte/icons/map-pin';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import { buttonVariants } from '$lib/components/ui/button';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import {
    breadcrumbList,
    canonicalUrl,
    graph,
    jsonLdScript,
    organization,
    webPageNode,
    website
  } from '$lib/seo/schema';
  import { cn, formatMillions } from '$lib/utils';
  import { whatsappHref } from '$lib/whatsapp';
  import { jabodetabekCopy } from './content';

  /**
   * Halaman Wedding Jabodetabek, pasangan dari Bali Wedding dan Singapore
   * Wedding di menu utama.
   *
   * Dua bahasa, copy di `content.ts`; bahasa Indonesia sumbernya. Rute yang
   * sama di kedua bahasa: "jabodetabek-wedding" sudah terbaca dalam bahasa Inggris.
   *
   * Sengaja hanya memuat fakta yang sudah terbit di situs ini atau yang
   * diberikan 7Magic. "Lebih dari 100 venue" di hero adalah angka dari 7Magic
   * (2026-10-08), mencakup venue rekanan di luar katalog; kartu kota memakai
   * jumlah dan harga "mulai dari" dari katalog, dihitung setiap kali halaman
   * dimuat, tidak diketik. Paket layanan perencanaan, harga paket, dan foto pernikahan sendiri
   * menunggu data dari 7Magic; jangan tambahkan angka atau janji layanan sebelum
   * itu ada.
   */

  let { data } = $props();

  const locale = $derived(getLocale());
  const copy = $derived(jabodetabekCopy(locale));
  const path = $derived(localizeHref('/jabodetabek-wedding'));
  const waHref = $derived(whatsappHref(copy.whatsappPrefill));

  const services = [
    { href: '/paket-sangjit', label: m.service_sangjit(), desc: m.service_sangjit_desc() },
    { href: '/perjanjian-pranikah', label: m.service_prenup(), desc: m.service_prenup_desc() }
  ];

  const jsonLd = $derived(
    jsonLdScript(
      graph(
        organization(),
        website(),
        webPageNode({
          url: path,
          name: copy.meta.title,
          description: copy.meta.description,
          locale,
          type: 'CollectionPage'
        }),
        breadcrumbList([{ name: m.breadcrumb_home(), path: '/' }, { name: copy.breadcrumb }])
      )
    )
  );
</script>

<svelte:head>
  <title>{copy.meta.title}</title>
  <meta name="description" content={copy.meta.description} />
  <link rel="canonical" href={canonicalUrl(path)} />
  {@html jsonLd}
</svelte:head>

<SocialMeta
  title={copy.meta.title}
  description={copy.meta.description}
  url={path}
  image="/img/jabodetabek/bundaran-hi-1280.jpg"
/>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <section class="relative flex min-h-[520px] items-center overflow-hidden md:min-h-[600px]">
    <!-- Dua ukuran: 2560px agar tetap tajam di layar lebar beresolusi tinggi,
         1280px untuk ponsel. Foto 1280px yang dulu dipakai tampak buram begitu
         direntangkan selebar layar. -->
    <img
      src="/img/jabodetabek/bundaran-hi-1280.jpg"
      srcset="/img/jabodetabek/bundaran-hi-1280.jpg 1280w, /img/jabodetabek/bundaran-hi-2560.jpg 2560w"
      sizes="100vw"
      alt={copy.hero.alt}
      class="absolute inset-0 h-full w-full object-cover"
      fetchpriority="high"
    />
    <div class="absolute inset-0 bg-gradient-to-r from-black/75 via-black/45 to-black/10"></div>

    <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-20 lg:px-8">
      <div class="max-w-3xl text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-dark-accent">
          {copy.hero.eyebrow}
        </p>
        <h1 class="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl lg:text-[3.4rem]">
          {copy.hero.title}
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/90">
          {copy.hero.lead}
        </p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <a
            href={localizeHref('/tour')}
            class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}
          >
            {m.nav_free_venue_tour()}
          </a>
          <a
            href={waHref}
            class={cn(
              buttonVariants({ size: 'lg' }),
              'border border-white/30 bg-white/10 px-7 text-white backdrop-blur hover:bg-white hover:text-brand-ink'
            )}
          >
            <MessageCircleIcon size={18} />
            {copy.hero.whatsapp}
          </a>
        </div>
      </div>
    </div>
  </section>

  {#if data.cities.length}
    <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {copy.cities.eyebrow}
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        {copy.cities.title}
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        {copy.cities.lead}
      </p>

      <div class="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {#each data.cities as city (city.slug)}
          <a
            href={localizeHref(`/wedding-venue/${city.slug}`)}
            class="group rounded-card border border-border bg-card transition hover:border-accent-foreground/40 hover:shadow-lg"
          >
            <div class="p-5">
              <p class="font-display text-xl font-bold">{copy.cities.cardTitle(city.name)}</p>
              <p class="mt-1 text-sm text-muted-foreground">
                {copy.cities.venues(city.count)}{#if city.guestsMax}{copy.cities.upTo(
                    city.guestsMax.toLocaleString(copy.cities.numberLocale)
                  )}{/if}
              </p>
              {#if city.floor}
                <p class="mt-3 text-[15px]">
                  {copy.cities.from}
                  <span class="font-semibold">{formatMillions(city.floor, copy.cities.millions)}</span>
                </p>
              {/if}
              <p class="mt-4 flex items-center gap-1.5 text-sm font-semibold text-accent-foreground">
                {copy.cities.cta(city.name)}
                <ArrowRightIcon size={15} class="transition group-hover:translate-x-0.5" />
              </p>
            </div>
          </a>
        {/each}
      </div>
    </section>
  {/if}

  <section class="border-y border-border bg-muted/40 px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <h2 class="max-w-2xl font-display text-3xl font-bold md:text-4xl">
        {copy.how.title}
      </h2>
      <div class="mt-10 grid gap-8 md:grid-cols-3">
        {#each copy.how.points as point (point.title)}
          <div>
            <p class="font-display text-lg font-bold">{point.title}</p>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{point.copy}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div class="grid gap-12 lg:grid-cols-2">
      <div>
        <h2 class="font-display text-2xl font-bold md:text-3xl">{copy.servicesTitle}</h2>
        <div class="mt-6 grid gap-4">
          {#each services as service (service.href)}
            <a
              href={localizeHref(service.href)}
              class="rounded-card border border-border p-5 transition hover:border-accent-foreground/40 hover:bg-muted/40"
            >
              <p class="font-semibold">{service.label}</p>
              <p class="mt-1 text-sm text-muted-foreground">{service.desc}</p>
            </a>
          {/each}
        </div>
      </div>
      <div>
        <h2 class="font-display text-2xl font-bold md:text-3xl">{copy.readingTitle}</h2>
        <ul class="mt-6 grid gap-4">
          {#each copy.reading as article (article.href)}
            <li>
              <a
                href={article.href}
                class="flex items-start gap-2 text-[15px] leading-7 hover:text-accent-foreground"
              >
                <ArrowRightIcon size={16} class="mt-1.5 shrink-0" />
                {article.title}
              </a>
            </li>
          {/each}
        </ul>
      </div>
    </div>
  </section>

  <section class="bg-brand-ink px-5 py-16 text-white lg:px-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-8 md:flex-row md:items-center md:justify-between">
      <div>
        <h2 class="font-display text-3xl font-bold">{copy.closing.title}</h2>
        <p class="mt-3 flex items-start gap-2 text-white/80">
          <MapPinIcon size={18} class="mt-0.5 shrink-0" />
          {copy.closing.office}
        </p>
      </div>
      <div class="flex flex-col gap-3 sm:flex-row">
        <a
          href={localizeHref('/tour')}
          class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}
        >
          {m.nav_free_venue_tour()}
        </a>
        <a
          href={waHref}
          class={cn(
            buttonVariants({ size: 'lg' }),
            'border border-white/30 bg-white/10 px-7 text-white hover:bg-white hover:text-brand-ink'
          )}
        >
          <MessageCircleIcon size={18} />
          WhatsApp
        </a>
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
