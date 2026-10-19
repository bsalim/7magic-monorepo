<script lang="ts">
  import CheckIcon from '@lucide/svelte/icons/check';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import { m } from '$lib/paraglide/messages.js';
  import { canonicalUrl, landingPageJsonLd } from '$lib/seo/schema';
  import { cn } from '$lib/utils';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';
  import { HERO_IMAGE, sangjitCopy } from './content';

  /**
   * Landing page akuisisi untuk paket sangjit (Jakarta).
   *
   * Dua bahasa: /paket-sangjit dan /en/sangjit-package, dipetakan di
   * urlPatterns paraglide. Copy-nya di `content.ts`; bahasa Indonesia sumbernya.
   *
   * Kata kunci yang dibidik (riset pasar Jakarta): "paket sangjit", "sangjit
   * Jakarta", "dekorasi sangjit", "isi baki sangjit", "isi nampan sangjit",
   * "susunan acara sangjit", "seserahan sangjit", "MC sangjit", "harga sangjit".
   * English: "sangjit package", "sangjit ceremony", "Chinese Indonesian
   * engagement", for relatives abroad and partners marrying into the family.
   *
   * Bagian "isi baki" dan "susunan acara" sengaja ditulis lengkap: itu yang
   * dicari orang lewat Google, dan halaman yang menjawabnya yang dapat
   * peringkat — bukan halaman yang cuma memajang harga.
   */

  const locale = $derived(getLocale());
  const copy = $derived(sangjitCopy(locale));
  const path = $derived(localizeHref('/paket-sangjit'));
  const canonical = $derived(canonicalUrl(path));
  const waHref = $derived(whatsappHref(copy.whatsappPrefill));

  let sending = $state(false);
  let submitted = $state(false);
  let errorMessage = $state('');

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    if (sending) return;

    const form = event.currentTarget as HTMLFormElement;
    const data = new FormData(form);
    const field = (key: string) => String(data.get(key) ?? '').trim();
    const labels = copy.lead;

    // The language line tells the team which language to reply in.
    const pesan = [
      labels.heading,
      `${labels.language}: ${locale === 'en' ? 'English' : 'Bahasa Indonesia'}`,
      `${labels.date}: ${field('tanggal') || labels.none}`,
      `${labels.venue}: ${field('lokasi') || labels.none}`,
      `${labels.guests}: ${field('tamu') || labels.none}`,
      `${labels.package}: ${field('paket') || labels.none}`,
      '',
      field('catatan') || labels.noNotes
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
          // The Indonesian path in both locales, so the CMS counts one campaign.
          source_path: '/paket-sangjit'
        })
      });

      if (!response.ok) {
        errorMessage = copy.form.error;
        return;
      }

      submitted = true;
      form.reset();
    } catch {
      errorMessage = copy.form.error;
    } finally {
      sending = false;
    }
  }

  const inputClass =
    'rounded-md border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30';

  const jsonLd = $derived(
    landingPageJsonLd({
      path,
      title: copy.meta.title,
      description: copy.meta.description,
      locale,
      crumbs: [{ name: m.breadcrumb_home(), path: '/' }, { name: m.service_sangjit() }],
      service: {
        name: m.service_sangjit(),
        serviceType: copy.jsonLd.serviceType,
        description: copy.meta.description,
        areaServed: ['Jakarta']
        // No offer: the page quotes per enquiry and prints no price, by choice.
      },
      faqs: copy.faqs
    })
  );
</script>

<svelte:head>
  <title>{copy.meta.title}</title>
  <meta name="description" content={copy.meta.description} />
  <meta name="keywords" content={copy.meta.keywords} />
  <link rel="canonical" href={canonical} />
  {@html jsonLd}
</svelte:head>

<SocialMeta title={copy.meta.title} description={copy.meta.description} url={path} />

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <!-- Hero -->
  <section class="relative flex min-h-[560px] items-center overflow-hidden md:min-h-[640px]">
    <img
      src={HERO_IMAGE}
      alt={copy.hero.alt}
      class="absolute inset-0 h-full w-full object-cover object-[50%_45%]"
      fetchpriority="high"
    />
    <div class="absolute inset-0 bg-gradient-to-r from-black/70 via-black/30 to-transparent"></div>

    <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-20 lg:px-8">
      <div class="max-w-3xl text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-dark-accent">
          {copy.hero.eyebrow}
        </p>
        <h1 class="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl lg:text-[3.3rem]">
          {copy.hero.title}
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/90">
          {copy.hero.lead}
        </p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <a href="#penawaran" class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}>
            {copy.hero.cta}
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

        <p class="mt-5 text-sm text-white/90">
          {copy.hero.note}
        </p>
      </div>
    </div>
  </section>

  <!-- Trust strip -->
  <section class="border-b border-border bg-brand-ink px-5 py-6 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {#each copy.stats as stat (stat.label)}
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
      {copy.services.eyebrow}
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      {copy.services.title}
    </h2>

    <div class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {#each copy.services.items as item (item.title)}
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
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {copy.packages.eyebrow}
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        {copy.packages.title}
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        {copy.packages.lead}
      </p>

      <div class="mt-10 grid gap-5 lg:grid-cols-3">
        {#each copy.packages.items as p (p.name)}
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
                {copy.packages.featuredBadge}
              </span>
            {/if}
            <h3 class="font-display text-xl font-semibold">{p.name}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{p.summary}</p>

            <!-- Where the price used to sit. The slot is kept so the three
                 cards still align, and the scale line does the filtering job
                 the number used to do. -->
            <div class="mt-5">
              <p class="font-display text-lg font-semibold text-brand-gold-hover">
                {copy.packages.priceSlot}
              </p>
              <p class="mt-1 text-sm text-muted-foreground">{p.scale}</p>
            </div>

            <ul class="mt-6 grid flex-1 content-start gap-2.5 border-t border-border pt-6">
              {#each p.includes as item (item)}
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
              {copy.packages.cta}
            </a>
          </div>
        {/each}
      </div>

      <div class="mt-8 rounded-md border border-border bg-background p-6">
        <h3 class="font-display text-base font-semibold">{copy.packages.excludedTitle}</h3>
        <p class="mt-2 text-[15px] leading-7 text-muted-foreground">
          {copy.packages.excluded}
        </p>
      </div>
    </div>
  </section>

  <!-- Susunan acara -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div class="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
      <div>
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
          {copy.runOfShow.eyebrow}
        </p>
        <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">
          {copy.runOfShow.title}
        </h2>
        <p class="mt-4 max-w-xl text-[15px] leading-7 text-muted-foreground">
          {copy.runOfShow.lead}
        </p>

        <div class="mt-8 grid gap-4">
          {#each copy.runOfShow.blocks as blok (blok.time)}
            <div class="rounded-md border border-border bg-background p-6">
              <div class="flex items-baseline gap-3">
                <span
                  class="rounded-full bg-brand-gold-soft px-3 py-1 text-xs font-semibold uppercase tracking-widest text-brand-gold-hover"
                >
                  {blok.time}
                </span>
                <h3 class="font-display text-lg font-semibold">{blok.title}</h3>
              </div>
              <ul class="mt-4 grid gap-2.5">
                {#each blok.items as item (item)}
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
        {#each copy.runOfShow.images as image, index (image.src)}
          <img
            src={image.src}
            alt={image.alt}
            loading="lazy"
            class={cn(
              'h-64 w-full rounded-md object-cover',
              index === 2 && 'object-top sm:col-span-2 lg:col-span-1'
            )}
          />
        {/each}
      </div>
    </div>
  </section>

  <!-- Isi baki -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {copy.trays.eyebrow}
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        {copy.trays.title}
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        {copy.trays.lead}
      </p>

      <div class="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {#each copy.trays.items as item, index (item.name)}
          <div class="rounded-md border border-border bg-background p-6">
            <div class="flex items-baseline gap-3">
              <span class="font-display text-sm font-bold text-brand-warm-deep">
                {String(index + 1).padStart(2, '0')}
              </span>
              <h3 class="font-display text-base font-semibold">{item.name}</h3>
            </div>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{item.meaning}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Aturan adat -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      {copy.customs.eyebrow}
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      {copy.customs.title}
    </h2>

    <div class="mt-10 grid gap-5 md:grid-cols-2">
      {#each copy.customs.items as item (item.title)}
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
        {copy.steps.eyebrow}
      </p>
      <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">{copy.steps.title}</h2>

      <div class="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
        {#each copy.steps.items as step, index (step.title)}
          <div class="rounded-md border border-border bg-background p-6">
            <span class="font-display text-3xl font-bold text-brand-warm-deep">
              {String(index + 1).padStart(2, '0')}
            </span>
            <h3 class="mt-3 font-display text-lg font-semibold">{step.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{step.copy}</p>
            <p class="mt-4 text-sm font-semibold text-brand-gold-hover">{step.when}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section class="mx-auto max-w-4xl px-5 py-16 lg:px-8">
    <h2 class="font-display text-3xl font-bold md:text-4xl">{copy.faqTitle}</h2>
    <div class="mt-8 grid gap-3">
      {#each copy.faqs as faq (faq.q)}
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
        <h2 class="font-display text-3xl font-bold md:text-4xl">{copy.form.title}</h2>
        <p class="mt-4 text-[15px] leading-7 text-white/75">
          {copy.form.lead}
        </p>

        <div class="mt-8 rounded-md border border-white/15 bg-white/5 p-6">
          <p class="text-sm text-white/70">{copy.form.chatPrompt}</p>
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
            <h3 class="font-display text-xl font-semibold">{copy.form.doneTitle}</h3>
            <p class="max-w-sm text-[15px] leading-7 text-muted-foreground">
              {copy.form.doneCopy}
            </p>
            <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp' }), 'mt-2')}>
              <MessageCircleIcon size={17} />
              {copy.form.chatNow}
            </a>
          </div>
        {:else}
          <form onsubmit={submit} class="grid gap-4">
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="sj-tanggal" class="text-[13px] font-medium">
                  {copy.form.date} <span class="text-muted-foreground">{copy.form.dateHint}</span>
                </label>
                <input id="sj-tanggal" name="tanggal" type="date" class={inputClass} />
              </div>
              <div class="grid gap-1.5">
                <label for="sj-lokasi" class="text-[13px] font-medium">
                  {copy.form.venue} <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <select id="sj-lokasi" name="lokasi" required class={inputClass}>
                  <option value="">{copy.form.choose}</option>
                  {#each copy.form.venueOptions as opt (opt)}
                    <option value={opt}>{opt}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="sj-tamu" class="text-[13px] font-medium">
                  {copy.form.guests} <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="sj-tamu"
                  name="tamu"
                  type="number"
                  min="1"
                  required
                  placeholder={copy.form.guestsPlaceholder}
                  class={inputClass}
                />
              </div>
              <div class="grid gap-1.5">
                <label for="sj-paket" class="text-[13px] font-medium">{copy.form.package}</label>
                <select id="sj-paket" name="paket" class={inputClass}>
                  <option value="">{copy.form.packageNone}</option>
                  {#each copy.form.packageOptions as opt (opt)}
                    <option value={opt}>{opt}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="sj-nama" class="text-[13px] font-medium">
                  {copy.form.name} <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input id="sj-nama" name="nama" required autocomplete="name" class={inputClass} />
              </div>
              <div class="grid gap-1.5">
                <label for="sj-telepon" class="text-[13px] font-medium">
                  {copy.form.phone} <span class="text-destructive" aria-hidden="true">*</span>
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
                {copy.form.email} <span class="text-muted-foreground">{copy.form.optional}</span>
              </label>
              <input id="sj-email" name="email" type="email" autocomplete="email" class={inputClass} />
            </div>

            <div class="grid gap-1.5">
              <label for="sj-catatan" class="text-[13px] font-medium">
                {copy.form.notes}
              </label>
              <textarea
                id="sj-catatan"
                name="catatan"
                rows="3"
                placeholder={copy.form.notesPlaceholder}
                class={inputClass}
              ></textarea>
            </div>

            {#if errorMessage}
              <p class="text-sm text-destructive" role="alert">{errorMessage}</p>
            {/if}

            <Button type="submit" variant="gold" size="lg" class="w-full" disabled={sending}>
              {sending ? copy.form.sending : copy.form.submit}
            </Button>
            <p class="text-center text-xs text-muted-foreground">
              {copy.form.privacy}
            </p>
          </form>
        {/if}
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
