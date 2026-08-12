<script lang="ts">
  import CheckIcon from '@lucide/svelte/icons/check';
  import XIcon from '@lucide/svelte/icons/x';
  import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import { canonicalUrl } from '$lib/seo/schema';
  import { cn } from '$lib/utils';
  import { whatsappDisplay, whatsappHref } from '$lib/whatsapp';
  import { NOTARY, OFFER_PRICE, SEGMENT_IMAGES, prenupCopy } from './content';

  /**
   * Acquisition landing page for the prenuptial agreement service (Jakarta).
   *
   * Bilingual, and the one page on the site whose route name differs per locale:
   * /perjanjian-pranikah and /en/prenuptial-agreement, mapped in the paraglide
   * urlPatterns. The service is the same in both -- same notary, same price, same
   * legal references -- so `content.ts` holds a translation, not a second offer.
   *
   * Indonesian keywords targeted (Jakarta market research): "perjanjian
   * pranikah", "perjanjian pra nikah", "biaya perjanjian pranikah", "perjanjian
   * pisah harta", "perjanjian perkawinan", "prenup Indonesia", "perjanjian
   * pranikah WNA" / "kawin campur". English: "prenuptial agreement Indonesia",
   * "prenup Jakarta", "separation of property agreement", and the
   * foreign-national variants, which is what the /en page exists to catch.
   */

  const locale = $derived(getLocale());
  const copy = $derived(prenupCopy(locale));

  // Not hardcoded to the Indonesian URL any more: this page has two, and a
  // canonical naming the other locale's URL asks Google to drop the one being
  // read. `canonicalUrl` resolves the redirect on '/en/'.
  const canonical = $derived(canonicalUrl(localizeHref('/perjanjian-pranikah')));

  const waHref = $derived(whatsappHref(copy.whatsappPrefill));

  // Structured FAQ so it can surface as a rich result. Built from the same array
  // the page renders, so the two cannot drift apart.
  const faqJsonLd = $derived(
    JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: copy.faqs.map((faq) => ({
        '@type': 'Question',
        name: faq.q,
        acceptedAnswer: { '@type': 'Answer', text: faq.a }
      }))
    })
  );

  const serviceJsonLd = $derived(
    JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Service',
      serviceType: copy.jsonLd.serviceType,
      provider: { '@type': 'Organization', name: '7Magic' },
      areaServed: { '@type': 'City', name: 'Jakarta' },
      // The service is delivered in Indonesian either way; the page is what is
      // translated, and that is declared on the canonical/hreflang pair.
      offers: {
        '@type': 'Offer',
        price: OFFER_PRICE,
        priceCurrency: 'IDR',
        description: copy.jsonLd.offerDescription
      }
    })
  );

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

    // The API's contact-lead schema has no columns for a legal service, so the
    // qualifying answers are folded into the message body -- same approach as
    // /bali-event-organizer. A schema of its own is later work.
    //
    // The language line is not decoration: an enquiry from the English page wants
    // an English reply, and the team cannot tell from a name.
    const message = [
      labels.heading,
      `${labels.language}: ${locale === 'en' ? 'English' : 'Bahasa Indonesia'}`,
      `${labels.status}: ${field('status') || labels.none}`,
      `${labels.citizenship}: ${field('citizenship') || labels.none}`,
      `${labels.assets}: ${field('assets') || labels.none}`,
      `${labels.weddingDate}: ${field('date') || labels.none}`,
      '',
      field('notes') || labels.noNotes
    ].join('\n');

    sending = true;
    errorMessage = '';

    try {
      const response = await fetch('/api/contact-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: field('name'),
          phone: field('phone'),
          email: field('email') || undefined,
          message,
          // The Indonesian path in both locales, so the two pages report as one
          // campaign rather than splitting the lead count in the CMS.
          source_path: '/perjanjian-pranikah'
        })
      });

      if (!response.ok) {
        errorMessage = copy.form.sendError;
        return;
      }

      submitted = true;
      form.reset();
    } catch {
      errorMessage = copy.form.sendError;
    } finally {
      sending = false;
    }
  }

  const inputClass =
    'rounded-md border border-input bg-background px-3 py-2.5 text-[15px] placeholder:text-muted-foreground/60 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/30';
</script>

<svelte:head>
  <title>{copy.meta.title}</title>
  <meta name="description" content={copy.meta.description} />
  <meta name="keywords" content={copy.meta.keywords} />
  <link rel="canonical" href={canonical} />
  {@html `<script type="application/ld+json">${faqJsonLd}</script>`}
  {@html `<script type="application/ld+json">${serviceJsonLd}</script>`}
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <!-- Hero -->
  <section class="relative flex min-h-[560px] items-center overflow-hidden md:min-h-[620px]">
    <img
      src="/img/prenup/hero-couple.jpg"
      alt={copy.hero.imageAlt}
      class="absolute inset-0 h-full w-full object-cover object-[55%_35%]"
      fetchpriority="high"
    />
    <div class="absolute inset-0 bg-gradient-to-r from-black/70 via-black/35 to-transparent"></div>

    <div class="relative z-10 mx-auto w-full max-w-7xl px-5 py-20 lg:px-8">
      <div class="max-w-3xl text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-dark-accent">
          {copy.hero.eyebrow}
        </p>
        <h1 class="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl lg:text-[3.3rem]">
          {copy.hero.title}
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/90">{copy.hero.lead}</p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <a href="#konsultasi" class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'px-7')}>
            {copy.hero.ctaConsult}
          </a>
          <a
            href={waHref}
            class={cn(
              buttonVariants({ size: 'lg' }),
              'border border-white/30 bg-white/10 px-7 text-white backdrop-blur hover:bg-white hover:text-brand-ink'
            )}
          >
            <MessageCircleIcon size={18} />
            {copy.hero.ctaWhatsapp}
          </a>
        </div>

        <p class="mt-5 text-sm text-white/90">{copy.hero.note}</p>
      </div>
    </div>
  </section>

  <!-- Trust strip -->
  <section class="border-b border-border bg-brand-ink px-5 py-6 text-white lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {#each copy.stats as stat}
        <div>
          <p class="font-display text-2xl font-bold text-brand-dark-accent">{stat.value}</p>
          <p class="mt-1 text-sm text-white/72">{stat.label}</p>
        </div>
      {/each}
    </div>
  </section>

  <!-- Price -->
  <section id="harga" class="scroll-mt-20 bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {copy.price_section.eyebrow}
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
        {copy.price_section.title}
      </h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        {copy.price_section.lead}
      </p>

      <div class="mt-10 grid gap-5 lg:grid-cols-[1fr_1.2fr] lg:items-start">
        <!-- Price comparison -->
        <div class="grid gap-4">
          {#each copy.comparison as row}
            <div
              class={cn(
                'rounded-md border p-6',
                row.ours
                  ? 'border-brand-gold bg-background shadow-lg ring-1 ring-brand-gold/20'
                  : 'border-border bg-background/60'
              )}
            >
              <p class="text-sm font-medium text-muted-foreground">{row.label}</p>
              <p
                class={cn(
                  'mt-2 font-display text-2xl font-bold',
                  row.ours ? 'text-brand-gold-hover' : 'text-foreground/70'
                )}
              >
                {row.price}
              </p>
              <p class="mt-2 text-sm leading-6 text-muted-foreground">{row.note}</p>
            </div>
          {/each}
          <p class="text-xs leading-6 text-muted-foreground">{copy.price_section.marketNote}</p>
        </div>

        <!-- Breakdown -->
        <div class="rounded-md border border-border bg-background p-7">
          <div class="flex items-baseline gap-2">
            <span class="font-display text-3xl font-bold">{copy.price}</span>
            <span class="text-sm text-muted-foreground">{copy.price_section.once}</span>
          </div>
          <span
            class="mt-4 inline-block w-fit rounded-full bg-brand-gold px-3 py-1 text-xs font-semibold uppercase tracking-widest text-white"
          >
            {copy.price_section.badge}
          </span>

          <h3 class="mt-6 font-display text-base font-semibold">
            {copy.price_section.includedTitle}
          </h3>
          <ul class="mt-3 grid gap-2.5">
            {#each copy.included as item}
              <li class="flex gap-3 text-[15px] leading-7">
                <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                <span>{item}</span>
              </li>
            {/each}
          </ul>

          <h3 class="mt-7 border-t border-border pt-6 font-display text-base font-semibold">
            {copy.price_section.excludedTitle}
          </h3>
          <ul class="mt-3 grid gap-2.5">
            {#each copy.excluded as item}
              <li class="flex gap-3 text-[15px] leading-7 text-muted-foreground">
                <XIcon size={17} class="mt-1.5 shrink-0 text-muted-foreground/70" />
                <span>{item}</span>
              </li>
            {/each}
          </ul>

          <a
            href="#konsultasi"
            class={cn(buttonVariants({ variant: 'gold', size: 'lg' }), 'mt-7 w-full')}
          >
            {copy.price_section.cta}
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- Who it is for -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      {copy.segmentsIntro.eyebrow}
    </p>
    <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
      {copy.segmentsIntro.title}
    </h2>

    <div class="mt-10 grid gap-5 sm:grid-cols-2">
      {#each copy.segments as item, index}
        <!-- bg-brand-ink: see /paket-sangjit — keeps an undecoded card dark
             instead of flashing white under the gradient overlay. -->
        <article class="group relative h-[320px] overflow-hidden rounded-md bg-brand-ink">
          <img
            src={SEGMENT_IMAGES[index]}
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

  <!-- Legal basis -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {copy.law.eyebrow}
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">{copy.law.title}</h2>

      <div class="mt-10 grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
        <div class="grid gap-4">
          {#each copy.lawCards as item}
            <div class="rounded-md border border-border bg-background p-6">
              <span
                class="inline-block rounded-full bg-brand-gold-soft px-3 py-1 text-xs font-semibold uppercase tracking-widest text-brand-gold-hover"
              >
                {item.reference}
              </span>
              <h3 class="mt-4 font-display text-lg font-semibold">{item.title}</h3>
              <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{item.copy}</p>
            </div>
          {/each}

          <!-- Not a legal citation but a practical warning, so it is set apart
               with a left accent rule — this is the step most often missed and
               the one that decides anything to do with property. -->
          <div
            class="rounded-md border border-border border-l-4 border-l-brand-gold bg-background p-6"
          >
            <h3 class="font-display text-lg font-semibold">{copy.law.missedTitle}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">
              {copy.law.missedLead}<strong class="font-semibold text-foreground"
                >{copy.law.missedEmphasis}</strong
              >{copy.law.missedTail}
            </p>
          </div>

          {#if NOTARY.name}
            <div class="rounded-md border border-border bg-background p-6">
              <p class="text-sm text-muted-foreground">{copy.law.notaryLabel}</p>
              <p class="mt-1 font-display text-lg font-semibold">{NOTARY.name}</p>
              <p class="mt-1 text-sm text-muted-foreground">
                {NOTARY.decree}{NOTARY.area ? ` · ${copy.law.notaryArea} ${NOTARY.area}` : ''}
              </p>
            </div>
          {/if}
        </div>

        <img
          src="/img/prenup/deed.jpg"
          alt={copy.law.deedAlt}
          loading="lazy"
          class="h-[420px] w-full rounded-md object-cover lg:sticky lg:top-24"
        />
      </div>
    </div>
  </section>

  <!-- Process -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div class="grid gap-10 lg:grid-cols-[0.85fr_1.15fr] lg:gap-16">
      <div class="lg:sticky lg:top-24 lg:self-start">
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
          {copy.process.eyebrow}
        </p>
        <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">{copy.process.title}</h2>
        <p class="mt-4 max-w-md text-[15px] leading-7 text-muted-foreground">{copy.process.lead}</p>
      </div>

      <!-- Timeline. The rail is the <ol> left border and the markers are pulled
           out with -left so they sit on the line. An <ol> because the order is
           meaningful: step 4 cannot precede step 3. -->
      <ol class="relative border-l border-border pl-8 sm:pl-10">
        {#each copy.steps as step, index}
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
              {step.when}
            </span>
            <h3 class="mt-3 font-display text-lg font-semibold">{step.title}</h3>
            <p class="mt-2 text-[15px] leading-7 text-muted-foreground">{step.copy}</p>
          </li>
        {/each}
      </ol>
    </div>
  </section>

  <!-- What can and cannot be agreed -->
  <section class="bg-secondary px-5 py-16 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {copy.limits.eyebrow}
      </p>
      <h2 class="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">{copy.limits.title}</h2>
      <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">{copy.limits.lead}</p>

      <div class="mt-10 grid gap-5 lg:grid-cols-2">
        <div class="rounded-md border border-border bg-background p-7">
          <h3 class="font-display text-lg font-semibold">{copy.limits.canTitle}</h3>
          <ul class="mt-4 grid gap-2.5">
            {#each copy.can as item}
              <li class="flex gap-3 text-[15px] leading-7">
                <CheckIcon size={17} class="mt-1.5 shrink-0 text-brand-gold" />
                <span>{item}</span>
              </li>
            {/each}
          </ul>
        </div>

        <div class="rounded-md border border-border bg-background p-7">
          <h3 class="font-display text-lg font-semibold">{copy.limits.cannotTitle}</h3>
          <ul class="mt-4 grid gap-2.5">
            {#each copy.cannot as item}
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

  <!-- Documents -->
  <section class="mx-auto max-w-7xl px-5 py-16 lg:px-8">
    <div class="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
      <img
        src="/img/prenup/documents.jpg"
        alt={copy.docs.imageAlt}
        loading="lazy"
        class="h-[360px] w-full rounded-md object-cover"
      />
      <div>
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
          {copy.docs.eyebrow}
        </p>
        <h2 class="mt-3 font-display text-3xl font-bold md:text-4xl">{copy.docs.title}</h2>
        <p class="mt-4 text-[15px] leading-7 text-muted-foreground">{copy.docs.lead}</p>
        <ul class="mt-6 grid gap-2.5">
          {#each copy.docList as item}
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
      <h2 class="font-display text-3xl font-bold md:text-4xl">{copy.faqTitle}</h2>
      <div class="mt-8 grid gap-3">
        {#each copy.faqs as faq}
          <details class="group rounded-md border border-border bg-background p-6">
            <summary
              class="cursor-pointer list-none font-display text-lg font-semibold marker:hidden"
            >
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
        <h2 class="font-display text-3xl font-bold md:text-4xl">{copy.form.title}</h2>
        <p class="mt-4 text-[15px] leading-7 text-white/75">{copy.form.lead}</p>

        <div class="mt-8 rounded-md border border-white/15 bg-white/5 p-6">
          <p class="text-sm text-white/70">{copy.form.talkTitle}</p>
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

        <p class="mt-6 text-sm leading-7 text-white/60">{copy.form.privacy}</p>
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
            <p class="max-w-sm text-[15px] leading-7 text-muted-foreground">{copy.form.doneCopy}</p>
            <a href={waHref} class={cn(buttonVariants({ variant: 'whatsapp' }), 'mt-2')}>
              <MessageCircleIcon size={17} />
              {copy.form.doneCta}
            </a>
          </div>
        {:else}
          <form onsubmit={submit} class="grid gap-4">
            <div class="grid gap-1.5">
              <label for="pn-status" class="text-[13px] font-medium">
                {copy.form.statusLabel} <span class="text-destructive" aria-hidden="true">*</span>
              </label>
              <select id="pn-status" name="status" required class={inputClass}>
                <option value="">{copy.form.statusPlaceholder}</option>
                {#each copy.form.statusOptions as opt}
                  <option value={opt}>{opt}</option>
                {/each}
              </select>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="pn-warga" class="text-[13px] font-medium">
                  {copy.form.citizenshipLabel}
                  <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <select id="pn-warga" name="citizenship" required class={inputClass}>
                  <option value="">{copy.form.statusPlaceholder}</option>
                  {#each copy.form.citizenshipOptions as opt}
                    <option value={opt}>{opt}</option>
                  {/each}
                </select>
              </div>
              <div class="grid gap-1.5">
                <label for="pn-tanggal" class="text-[13px] font-medium">
                  {copy.form.dateLabel}
                  <span class="text-muted-foreground">{copy.form.dateHint}</span>
                </label>
                <input id="pn-tanggal" name="date" type="date" class={inputClass} />
              </div>
            </div>

            <div class="grid gap-1.5">
              <label for="pn-aset" class="text-[13px] font-medium">{copy.form.assetsLabel}</label>
              <select id="pn-aset" name="assets" class={inputClass}>
                <option value="">{copy.form.assetsPlaceholder}</option>
                {#each copy.form.assetsOptions as opt}
                  <option value={opt}>{opt}</option>
                {/each}
              </select>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid gap-1.5">
                <label for="pn-nama" class="text-[13px] font-medium">
                  {copy.form.nameLabel} <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input id="pn-nama" name="name" required autocomplete="name" class={inputClass} />
              </div>
              <div class="grid gap-1.5">
                <label for="pn-telepon" class="text-[13px] font-medium">
                  {copy.form.phoneLabel} <span class="text-destructive" aria-hidden="true">*</span>
                </label>
                <input
                  id="pn-telepon"
                  name="phone"
                  required
                  autocomplete="tel"
                  placeholder={copy.form.phonePlaceholder}
                  class={inputClass}
                />
              </div>
            </div>

            <div class="grid gap-1.5">
              <label for="pn-email" class="text-[13px] font-medium">
                {copy.form.emailLabel}
                <span class="text-muted-foreground">{copy.form.emailHint}</span>
              </label>
              <input
                id="pn-email"
                name="email"
                type="email"
                autocomplete="email"
                class={inputClass}
              />
            </div>

            <div class="grid gap-1.5">
              <label for="pn-catatan" class="text-[13px] font-medium">{copy.form.notesLabel}</label>
              <textarea
                id="pn-catatan"
                name="notes"
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
            <p class="text-center text-xs text-muted-foreground">{copy.form.dataNote}</p>
          </form>
        {/if}
      </div>
    </div>
  </section>

  <PublicFooter />
</main>
