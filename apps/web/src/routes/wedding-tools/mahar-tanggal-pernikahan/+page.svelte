<script lang="ts">
  import { onMount } from 'svelte';
  import CalendarHeartIcon from '@lucide/svelte/icons/calendar-heart';
  import DownloadIcon from '@lucide/svelte/icons/download';
  import ExternalLinkIcon from '@lucide/svelte/icons/external-link';
  import GemIcon from '@lucide/svelte/icons/gem';
  import HeartIcon from '@lucide/svelte/icons/heart';
  import InfoIcon from '@lucide/svelte/icons/info';
  import LockIcon from '@lucide/svelte/icons/lock';
  import MoonStarIcon from '@lucide/svelte/icons/moon-star';
  import PrinterIcon from '@lucide/svelte/icons/printer';
  import QuoteIcon from '@lucide/svelte/icons/quote';
  import DateField from '$lib/components/DateField.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import LeadGate from '$lib/components/tools/LeadGate.svelte';
  import MaharCard from '$lib/components/tools/MaharCard.svelte';
  import ToolShell from '$lib/components/tools/ToolShell.svelte';
  import { Button } from '$lib/components/ui/button';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import { canonicalUrl, toolPageJsonLd } from '$lib/seo/schema';
  import { isUnlocked } from '$lib/tools/lead';
  import {
    computeMahar,
    formatGrams,
    formatMasehi,
    formatRupiah,
    payableRemainder,
    terbilang,
    type MaharInput,
    type MaharMethod,
    type SpecialKind,
    type VariantId
  } from '$lib/tools/mahar';
  import { TOOL_PATH, maharCopy } from './content';

  /**
   * The mahar generator: a meaningful date in, a mahar amount out.
   *
   * Everything a search engine or a couple needs to judge the page is free and
   * server-rendered: the amount, its reading, the words for the ijab kabul, the
   * explainer and FAQ. Only the designed card sits behind the soft gate, which
   * is what keeps the page linkable while still meeting couples who are
   * planning right now.
   *
   * All the arithmetic is in `$lib/tools/mahar`; this file only wires inputs to
   * it and lays the result out.
   */

  const locale = $derived(getLocale());
  const copy = $derived(maharCopy(locale));
  const canonical = $derived(canonicalUrl(localizeHref(TOOL_PATH)));

  const jsonLd = $derived(
    toolPageJsonLd({
      path: localizeHref(TOOL_PATH),
      title: copy.meta.title,
      name: copy.appName,
      description: copy.meta.description,
      locale,
      crumbs: [
        { name: m.breadcrumb_home(), path: '/' },
        { name: m.nav_wedding_tools(), path: '/wedding-tools' },
        { name: copy.appName }
      ],
      faqs: copy.faqs
    })
  );

  const METHODS: { id: MaharMethod; icon: typeof HeartIcon }[] = [
    { id: 'akad', icon: CalendarHeartIcon },
    { id: 'spesial', icon: HeartIcon },
    { id: 'hijriah', icon: MoonStarIcon },
    { id: 'emas', icon: GemIcon }
  ];
  const KINDS: SpecialKind[] = ['jadian', 'bertemu', 'ulang_tahun'];

  let method = $state<MaharMethod>('akad');
  let kind = $state<SpecialKind>('jadian');
  // One akad date for the three methods that read it, so switching between
  // them keeps what the couple already picked.
  let akadDate = $state('');
  let specialDate = $state('');
  let birthdayGroom = $state('');
  let birthdayBride = $state('');
  let groom = $state('');
  let bride = $state('');
  let variantId = $state<VariantId>('dmy');

  // False on the server and on first paint, then read from this browser: the
  // flag is a convenience in localStorage, never something to render on.
  let unlocked = $state(false);
  let gateOpen = $state(false);
  let exporting = $state(false);
  let exportError = $state('');
  let card = $state<ReturnType<typeof MaharCard>>();

  onMount(() => {
    unlocked = isUnlocked();
  });

  const birthdays = $derived(method === 'spesial' && kind === 'ulang_tahun');

  const input = $derived.by((): MaharInput => {
    if (method !== 'spesial') return { method, date: akadDate };
    if (kind === 'ulang_tahun')
      return { method, kind, date: birthdayGroom, date2: birthdayBride };
    return { method, kind, date: specialDate };
  });

  // Not called `result`: that is the name of the ToolShell snippet below, and a
  // snippet shadows a script binding of the same name inside the markup.
  const mahar = $derived(computeMahar(input, locale));
  // Falls back to the first variant rather than resetting the choice in an
  // effect: a method without the picked variant shows its own first one, and
  // switching back restores the couple's pick.
  const selected = $derived(
    mahar.variants.find((variant) => variant.id === variantId) ?? mahar.variants[0]
  );

  const amountText = $derived(selected ? formatRupiah(selected.amount, locale) : '');
  const gold = $derived(selected?.gold);
  const goldText = $derived(gold ? formatGrams(gold.grams, locale) : '');
  const words = $derived(selected ? terbilang(selected.amount, locale) : '');
  const remainder = $derived(selected ? payableRemainder(selected.amount) : 0);

  // The wording is spoken in Indonesian at the KUA, so it is Indonesian on both
  // editions of the page; only the explanation around it is translated.
  const lafaz = $derived.by(() => {
    if (!selected) return '';
    const cash = terbilang(selected.amount, 'id');
    const goldPart = gold ? ` dan emas seberat ${formatGrams(gold.grams, 'id')}` : '';
    return `"... dengan maskawin uang sebesar ${cash}${goldPart}, dibayar tunai."`;
  });

  const hijriLine = $derived(
    mahar.hijri
      ? `${mahar.hijri.day} ${mahar.hijri.monthName} ${mahar.hijri.year} ${locale === 'en' ? 'AH' : 'H'}`
      : ''
  );

  function dayMonth(iso: string): string {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
    if (!match) return '';
    return new Intl.DateTimeFormat(locale === 'en' ? 'en-GB' : 'id-ID', {
      day: 'numeric',
      month: 'long',
      timeZone: 'UTC'
    }).format(new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]), 12)));
  }

  const dateLine = $derived(
    birthdays
      ? [dayMonth(birthdayGroom), dayMonth(birthdayBride)].filter(Boolean).join(' & ')
      : formatMasehi(input.date, locale)
  );

  const names = $derived([groom.trim(), bride.trim()].filter(Boolean).join(' & '));

  const cardLabel = $derived(
    [copy.card.title, names || copy.card.fallbackTitle, dateLine, amountText, goldText]
      .filter(Boolean)
      .join(', ')
  );

  // What the team sees in the lead: enough to know which mahar the couple made.
  const leadInputs = $derived.by(() => {
    const fields: Record<string, string | number> = { method, date: input.date };
    if (selected) {
      fields.variant = selected.id;
      fields.amount = selected.amount;
    }
    if (method === 'spesial') fields.kind = kind;
    if (input.date2) fields.date2 = input.date2;
    if (gold) fields.gold_grams = gold.grams;
    return fields;
  });

  const emptyHint = $derived(birthdays ? copy.result.emptyBirthdays : copy.result.empty);

  async function downloadPng() {
    exporting = true;
    exportError = '';
    try {
      await card?.downloadPng();
    } catch {
      exportError = copy.card.exportError;
    } finally {
      exporting = false;
    }
  }

  /** "Coba tanggal ini" on an example: load it and bring the tool into view. */
  function tryExample(date: string, variant: VariantId) {
    method = 'akad';
    akadDate = date;
    variantId = variant;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    document
      .getElementById('mahar-result')
      ?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  }

  const FIELD =
    'h-11 w-full rounded-md border border-input bg-background px-3 text-base placeholder:text-muted-foreground/60 focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none md:text-[15px]';
  const LEGEND = 'text-[13px] font-semibold tracking-wide text-foreground';
  // Native radios under styled labels: arrow keys, focus order and screen
  // reader grouping come for free, which a row of buttons would have to fake.
  const CHOICE =
    'relative flex cursor-pointer rounded-xl border border-border bg-background transition hover:border-brand-gold/60 has-checked:border-brand-gold has-checked:bg-brand-gold-soft has-checked:shadow-[0_0_0_1px_var(--brand-gold)] has-focus-visible:ring-3 has-focus-visible:ring-ring/40';
</script>

<svelte:head>
  <title>{copy.meta.title}</title>
  <meta name="description" content={copy.meta.description} />
  <meta name="keywords" content={copy.meta.keywords} />
  <link rel="canonical" href={canonical} />
  {@html jsonLd}
</svelte:head>

<SocialMeta title={copy.meta.title} description={copy.meta.description} url={canonical} />

<ToolShell
  eyebrow={copy.hero.eyebrow}
  title={copy.hero.title}
  lead={copy.hero.lead}
  crumbs={[
    { name: m.breadcrumb_home(), path: '/' },
    { name: m.nav_wedding_tools(), path: '/wedding-tools' },
    { name: copy.appName }
  ]}
  faqs={copy.faqs}
  related={copy.related}
>
  {#snippet inputs()}
    <div class="grid gap-7">
      <fieldset>
        <legend class={LEGEND}>{copy.form.methodLegend}</legend>
        <div class="mt-3 grid grid-cols-2 gap-2.5">
          {#each METHODS as option (option.id)}
            {@const Icon = option.icon}
            <label class="{CHOICE} flex-col gap-1.5 p-3.5">
              <input
                type="radio"
                name="mahar-method"
                value={option.id}
                bind:group={method}
                class="sr-only"
              />
              <Icon size={20} class="text-brand-gold" aria-hidden="true" />
              <span class="font-display text-sm leading-5 font-semibold">
                {copy.form.methods[option.id].label}
              </span>
              <span class="text-xs leading-5 text-muted-foreground">
                {copy.form.methods[option.id].hint}
              </span>
            </label>
          {/each}
        </div>
      </fieldset>

      {#if method === 'spesial'}
        <fieldset>
          <legend class={LEGEND}>{copy.form.kindLegend}</legend>
          <div class="mt-3 flex flex-wrap gap-2">
            {#each KINDS as option (option)}
              <label class="{CHOICE} rounded-full px-4 py-2 text-sm font-medium">
                <input
                  type="radio"
                  name="mahar-kind"
                  value={option}
                  bind:group={kind}
                  class="sr-only"
                />
                {copy.form.kinds[option]}
              </label>
            {/each}
          </div>
        </fieldset>
      {/if}

      <div class="grid gap-4 {birthdays ? 'sm:grid-cols-2' : ''}">
        {#if birthdays}
          <div class="grid gap-1.5">
            <label for="mahar-birthday-groom" class="{LEGEND}">{copy.form.birthdayLabels[0]}</label>
            <DateField
              id="mahar-birthday-groom"
              bind:value={birthdayGroom}
              {locale}
              placeholder={copy.form.datePlaceholder}
              class="h-11 w-full text-base md:text-[15px]"
            />
          </div>
          <div class="grid gap-1.5">
            <label for="mahar-birthday-bride" class="{LEGEND}">{copy.form.birthdayLabels[1]}</label>
            <DateField
              id="mahar-birthday-bride"
              bind:value={birthdayBride}
              {locale}
              placeholder={copy.form.datePlaceholder}
              class="h-11 w-full text-base md:text-[15px]"
            />
          </div>
        {:else if method === 'spesial'}
          <div class="grid gap-1.5">
            <label for="mahar-special-date" class="{LEGEND}">
              {kind === 'bertemu' ? copy.form.dateLabels.bertemu : copy.form.dateLabels.jadian}
            </label>
            <DateField
              id="mahar-special-date"
              bind:value={specialDate}
              {locale}
              placeholder={copy.form.datePlaceholder}
              class="h-11 w-full text-base md:text-[15px]"
            />
          </div>
        {:else}
          <div class="grid gap-1.5">
            <label for="mahar-akad-date" class="{LEGEND}">{copy.form.dateLabels.akad}</label>
            <DateField
              id="mahar-akad-date"
              bind:value={akadDate}
              {locale}
              placeholder={copy.form.datePlaceholder}
              class="h-11 w-full text-base md:text-[15px]"
            />
          </div>
        {/if}
      </div>

      <fieldset>
        <legend class={LEGEND}>
          {copy.form.namesLegend}
          <span class="font-normal text-muted-foreground">({copy.form.optional})</span>
        </legend>
        <div class="mt-3 grid gap-3 sm:grid-cols-2">
          <div class="grid gap-1.5">
            <label for="mahar-groom" class="text-xs text-muted-foreground">{copy.form.groomLabel}</label>
            <input
              id="mahar-groom"
              bind:value={groom}
              maxlength="40"
              autocomplete="off"
              placeholder={copy.form.groomPlaceholder}
              class={FIELD}
            />
          </div>
          <div class="grid gap-1.5">
            <label for="mahar-bride" class="text-xs text-muted-foreground">{copy.form.brideLabel}</label>
            <input
              id="mahar-bride"
              bind:value={bride}
              maxlength="40"
              autocomplete="off"
              placeholder={copy.form.bridePlaceholder}
              class={FIELD}
            />
          </div>
        </div>
      </fieldset>

      {#if mahar.variants.length > 1}
        <fieldset>
          <legend class={LEGEND}>{copy.form.variantLegend}</legend>
          <div class="mt-3 grid grid-cols-2 gap-2.5">
            {#each mahar.variants as variant (variant.id)}
              <label class="{CHOICE} flex-col px-3.5 py-3">
                <input
                  type="radio"
                  name="mahar-variant"
                  value={variant.id}
                  checked={selected?.id === variant.id}
                  onchange={() => (variantId = variant.id)}
                  class="sr-only"
                />
                <span class="font-display text-[15px] font-semibold tabular-nums">
                  {formatRupiah(variant.amount, locale)}
                </span>
                <span class="mt-0.5 text-xs text-muted-foreground">{variant.label}</span>
              </label>
            {/each}
          </div>
        </fieldset>
      {/if}
    </div>
  {/snippet}

  {#snippet result()}
    <div id="mahar-result" class="grid scroll-mt-24 gap-5">
      <div
        class="relative overflow-hidden rounded-2xl bg-brand-ink p-6 text-white shadow-[0_24px_60px_-30px_rgba(20,20,20,0.6)] md:p-7"
      >
        <div
          aria-hidden="true"
          class="pointer-events-none absolute -top-20 -right-16 size-56 rounded-full bg-brand-gold/25 blur-3xl"
        ></div>
        <p class="relative text-xs font-semibold tracking-[0.2em] text-brand-dark-accent uppercase">
          {copy.result.title}
        </p>

        <div class="relative" aria-live="polite" aria-atomic="true">
          {#if selected}
            <p
              class="mt-3 font-display text-4xl leading-none font-bold tracking-tight tabular-nums sm:text-5xl"
            >
              {amountText}
            </p>
            {#if goldText}
              <p class="mt-2 font-display text-2xl font-semibold text-brand-dark-accent">
                + {goldText}
              </p>
            {/if}
            <p class="mt-3 text-sm text-white/70">
              {copy.result.readingPrefix}
              <span class="font-medium tracking-wide text-white">{selected.reading}</span>
            </p>
          {:else}
            <p class="mt-3 font-display text-2xl font-semibold text-white/40">Rp··.···.···</p>
            <p class="mt-3 text-sm text-white/70">{emptyHint}</p>
          {/if}
        </div>

        {#if hijriLine}
          <p class="relative mt-4 text-sm text-white/80">
            {copy.result.hijriPrefix}: <span class="font-medium text-white">{hijriLine}</span>
          </p>
          <p class="relative mt-1.5 text-xs leading-5 text-white/60">{copy.result.hijriNote}</p>
        {/if}

        {#if gold}
          <dl class="relative mt-5 grid gap-2 border-t border-white/15 pt-4 text-sm">
            <div class="flex justify-between gap-4">
              <dt class="text-white/60">{copy.result.cashLabel}</dt>
              <dd class="font-medium tabular-nums">{amountText}</dd>
            </div>
            <div class="flex justify-between gap-4">
              <dt class="text-white/60">{copy.result.goldLabel}</dt>
              <dd class="font-medium tabular-nums">{goldText}</dd>
            </div>
            {#if gold.bars.length}
              <div class="flex justify-between gap-4">
                <dt class="text-white/60">{copy.result.barsLabel}</dt>
                <dd class="text-right font-medium tabular-nums">
                  {gold.bars.map((bar) => `${bar} g`).join(' + ')}
                </dd>
              </div>
            {/if}
          </dl>
          {#if gold.jewellery > 0}
            <p class="relative mt-2 text-xs leading-5 text-white/60">
              {copy.result.jewelleryNote(formatGrams(gold.jewellery, locale))}
            </p>
          {/if}
        {/if}

        {#if selected}
          <div class="relative mt-5 grid gap-3 border-t border-white/15 pt-4">
            <div>
              <p class="text-xs font-semibold tracking-wide text-brand-dark-accent">
                {copy.result.wordsLabel}
              </p>
              <p class="mt-1 text-[15px] leading-6 text-white/90 first-letter:uppercase">{words}</p>
            </div>
            <div class="rounded-xl bg-white/[0.06] p-4">
              <p class="flex items-center gap-2 text-xs font-semibold tracking-wide text-brand-dark-accent">
                <QuoteIcon size={14} aria-hidden="true" />
                {copy.result.lafazLabel}
              </p>
              {#if copy.result.lafazLanguageNote}
                <p class="mt-1 text-xs text-white/60">{copy.result.lafazLanguageNote}</p>
              {/if}
              <p class="mt-2 text-[15px] leading-7 text-white italic">{lafaz}</p>
            </div>
          </div>
        {/if}

        {#if remainder > 0}
          <p
            class="relative mt-4 flex gap-2.5 rounded-xl border border-brand-dark-accent/30 bg-brand-dark-accent/10 p-3.5 text-[13px] leading-6 text-white/85"
          >
            <InfoIcon size={16} class="mt-1 shrink-0 text-brand-dark-accent" aria-hidden="true" />
            <span>{copy.result.remainderNote(formatRupiah(remainder, locale))}</span>
          </p>
        {/if}
      </div>

      <div class="rounded-2xl border border-border bg-background p-5 md:p-6">
        <div class="flex items-baseline justify-between gap-3">
          <h2 class="font-display text-lg font-bold">{copy.card.title}</h2>
          <span class="text-xs text-muted-foreground">A5 · PNG</span>
        </div>
        <p class="mt-1 text-sm leading-6 text-muted-foreground">{copy.card.lead}</p>

        <div class="relative mt-4 overflow-hidden rounded-xl bg-brand-warm ring-1 ring-brand-gold/20">
          <MaharCard
            bind:this={card}
            {names}
            {dateLine}
            {hijriLine}
            amount={amountText}
            gold={goldText}
            {words}
            copy={copy.card}
            label={cardLabel}
            class="block h-auto w-full transition duration-500 {unlocked
              ? ''
              : 'scale-105 blur-[7px] saturate-75'}"
          />

          {#if !unlocked}
            <div
              class="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-brand-warm/40 p-6 text-center"
            >
              <span
                class="flex size-12 items-center justify-center rounded-full bg-background text-brand-gold-hover shadow-md"
              >
                <LockIcon size={20} aria-hidden="true" />
              </span>
              <p class="font-display text-lg font-bold text-brand-ink">{copy.card.lockedTitle}</p>
              <p class="max-w-xs text-sm leading-6 text-brand-ink/75">{copy.card.lockedCopy}</p>
              <Button variant="gold" size="lg" class="px-8" onclick={() => (gateOpen = true)}>
                {copy.card.unlock}
              </Button>
            </div>
          {/if}
        </div>

        {#if unlocked}
          <div class="mt-4 grid gap-2.5 sm:grid-cols-2">
            <Button variant="gold" size="lg" onclick={downloadPng} disabled={exporting}>
              <DownloadIcon size={17} aria-hidden="true" />
              {exporting ? copy.card.exporting : copy.card.downloadPng}
            </Button>
            <Button variant="outline" size="lg" onclick={() => card?.print()}>
              <PrinterIcon size={17} aria-hidden="true" />
              {copy.card.print}
            </Button>
          </div>
          {#if exportError}
            <p class="mt-2 text-sm text-destructive" role="alert">{exportError}</p>
          {:else}
            <p class="mt-2 text-xs leading-5 text-muted-foreground">{copy.card.unlockedNote}</p>
          {/if}
        {/if}
      </div>
    </div>
  {/snippet}

  {#snippet gate()}
    <LeadGate
      bind:open={gateOpen}
      tool="mahar"
      title={copy.card.gateTitle}
      description={copy.card.gateDescription}
      {names}
      inputs={leadInputs}
      sourcePath={TOOL_PATH}
      onUnlocked={() => (unlocked = true)}
    />
  {/snippet}

  {#snippet explainer()}
    <section class="px-5 py-16 lg:px-8">
      <div class="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.4fr)]">
        <div class="lg:sticky lg:top-24 lg:self-start">
          <p class="text-xs font-semibold tracking-[0.2em] text-brand-gold-hover uppercase">
            {m.nav_wedding_tools()}
          </p>
          <h2 class="mt-3 font-display text-2xl font-bold md:text-3xl">{copy.explainer.title}</h2>
          <p class="mt-3 text-[15px] leading-7 text-muted-foreground">{copy.explainer.lead}</p>
        </div>

        <div class="grid gap-8">
          {#each copy.explainer.sections as section (section.title)}
            <div class="border-l-2 border-brand-gold/40 pl-5">
              <h3 class="font-display text-lg font-semibold">{section.title}</h3>
              {#each section.paragraphs as paragraph, index (index)}
                <p class="mt-2.5 text-[15px] leading-7 text-foreground/80">{paragraph}</p>
              {/each}
            </div>
          {/each}

          <details class="group rounded-xl border border-border p-5">
            <summary
              class="flex cursor-pointer list-none items-center justify-between rounded-sm text-sm font-semibold focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none [&::-webkit-details-marker]:hidden"
            >
              {copy.explainer.sourcesTitle}
              <span class="text-xs font-normal text-muted-foreground">
                {copy.explainer.sources.length}
              </span>
            </summary>
            <ol class="mt-3 grid list-decimal gap-2 pl-5 text-sm leading-6 text-muted-foreground">
              {#each copy.explainer.sources as source (source.url)}
                <li>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="underline decoration-border underline-offset-2 transition hover:text-foreground hover:decoration-brand-gold"
                  >
                    {source.label}
                  </a>
                </li>
              {/each}
            </ol>
          </details>
        </div>
      </div>
    </section>

    <section class="bg-brand-ink px-5 py-16 text-white lg:px-8">
      <div class="mx-auto max-w-7xl">
        <h2 class="font-display text-2xl font-bold md:text-3xl">{copy.examples.title}</h2>
        <p class="mt-3 max-w-2xl text-[15px] leading-7 text-white/70">{copy.examples.lead}</p>

        <ul class="mt-8 grid gap-5 md:grid-cols-3">
          {#each copy.examples.items as example (example.couple)}
            <li class="flex flex-col rounded-2xl border border-white/10 bg-white/[0.04] p-6">
              <p class="text-xs text-white/60">{formatMasehi(example.date, locale)}</p>
              <h3 class="mt-1 font-display text-lg font-semibold">{example.couple}</h3>
              <p class="mt-4 font-display text-xl leading-snug font-semibold text-brand-dark-accent">
                {example.mahar}
              </p>
              <p class="mt-2 text-sm tracking-wide text-white/70">{example.reading}</p>

              <div class="mt-auto pt-5">
                <div class="flex flex-wrap items-center gap-x-4 gap-y-2">
                  {#if example.tryIt}
                    {@const tryIt = example.tryIt}
                    <button
                      type="button"
                      onclick={() => tryExample(tryIt.date, tryIt.variant)}
                      class="rounded-full border border-brand-dark-accent/50 px-4 py-1.5 text-sm font-medium text-brand-dark-accent transition hover:bg-brand-dark-accent hover:text-brand-ink focus-visible:ring-3 focus-visible:ring-brand-dark-accent/40 focus-visible:outline-none"
                    >
                      {copy.examples.tryIt}
                    </button>
                  {/if}
                  {#if example.href}
                    <a
                      href={example.href}
                      class="text-sm text-white/80 underline decoration-white/30 underline-offset-2 transition hover:text-white"
                    >
                      {copy.examples.readMore}
                    </a>
                  {/if}
                </div>
                <p class="mt-4 text-xs text-white/50">
                  {copy.examples.sourcesLabel}:
                  {#each example.sources as source, index (source.url)}
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      class="inline-flex items-center gap-0.5 underline decoration-white/20 underline-offset-2 hover:text-white"
                    >
                      {source.label}<ExternalLinkIcon size={11} aria-hidden="true" />
                    </a>{index < example.sources.length - 1 ? ', ' : ''}
                  {/each}
                </p>
              </div>
            </li>
          {/each}
        </ul>
      </div>
    </section>
  {/snippet}
</ToolShell>
