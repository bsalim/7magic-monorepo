<script lang="ts">
  import { onMount } from 'svelte';
  import CalendarCheckIcon from '@lucide/svelte/icons/calendar-check';
  import DownloadIcon from '@lucide/svelte/icons/download';
  import InfoIcon from '@lucide/svelte/icons/info';
  import LockIcon from '@lucide/svelte/icons/lock';
  import PrinterIcon from '@lucide/svelte/icons/printer';
  import SparklesIcon from '@lucide/svelte/icons/sparkles';
  import DateField from '$lib/components/DateField.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import BaziCard, { type BaziCardChart, type BaziCardDate } from '$lib/components/tools/BaziCard.svelte';
  import LeadGate from '$lib/components/tools/LeadGate.svelte';
  import ToolShell from '$lib/components/tools/ToolShell.svelte';
  import { Button } from '$lib/components/ui/button';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import { canonicalUrl, toolPageJsonLd } from '$lib/seo/schema';
  import {
    MAX_DATES,
    baziLeadInputs,
    displayNames,
    failureKind,
    hasUncertainPillar,
    fetchBazi,
    isCompleteBirth,
    uniqueDates,
    type BaziRequest,
    type BaziResponse,
    type ChartOut,
    type PartnerIn,
    type PillarOut,
    type Tone,
    type Verdict,
    type Zone
  } from '$lib/tools/bazi';
  import { isUnlocked } from '$lib/tools/lead';
  import { formatMasehi } from '$lib/tools/mahar';
  import { TOOL_PATH, baziCopy, dateReason, reading, type PillarKey } from './content';

  /**
   * The Ba Zi couple calculator: two birth moments in, two charts and a
   * traditional reading out, plus a clash check for candidate wedding dates.
   *
   * Unlike mahar and hashtag the calculation is not in the browser: the API
   * owns the astronomy (`app/domains/bazi`), and this page posts to it through
   * the `/api/bazi` proxy on a button press rather than on every keystroke.
   * Charts and the reading are free; the date verdicts and the card sit behind
   * the shared soft gate, and the dates are only sent once unlocked.
   */

  const locale = $derived(getLocale());
  const copy = $derived(baziCopy(locale));
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

  type PartnerForm = { name: string; birth_date: string; birth_time: string; timeUnknown: boolean; zone: Zone };
  const blankPartner = (): PartnerForm => ({ name: '', birth_date: '', birth_time: '', timeUnknown: false, zone: 'WIB' });

  let partners = $state<PartnerForm[]>([blankPartner(), blankPartner()]);
  let dates = $state<string[]>(Array.from({ length: MAX_DATES }, () => ''));

  let bazi = $state<BaziResponse | null>(null);
  // The inputs the result was computed from, to tell the visitor when it is stale.
  let resultKey = $state('');
  let loading = $state(false);
  let error = $state('');
  let dateError = $state('');

  let unlocked = $state(false);
  let gateOpen = $state(false);
  let exporting = $state(false);
  let exportError = $state('');
  let card = $state<ReturnType<typeof BaziCard>>();

  onMount(() => {
    unlocked = isUnlocked();
  });

  const ZONES: Zone[] = ['WIB', 'WITA', 'WIT'];
  const PILLARS: PillarKey[] = ['year', 'month', 'day', 'hour'];
  const ELEMENT_ORDER = ['wood', 'fire', 'earth', 'metal', 'water'] as const;
  // One hue per element, softened for the brand's cream palette.
  const ELEMENT_TONE: Record<string, { chip: string; bar: string }> = {
    wood: { chip: 'bg-emerald-50 text-emerald-800 ring-emerald-200', bar: 'bg-emerald-500' },
    fire: { chip: 'bg-rose-50 text-rose-800 ring-rose-200', bar: 'bg-rose-500' },
    earth: { chip: 'bg-amber-50 text-amber-900 ring-amber-200', bar: 'bg-amber-500' },
    metal: { chip: 'bg-slate-100 text-slate-800 ring-slate-300', bar: 'bg-slate-400' },
    water: { chip: 'bg-sky-50 text-sky-800 ring-sky-200', bar: 'bg-sky-500' }
  };
  const TONE_STYLE: Record<Tone, string> = {
    harmony: 'text-emerald-300',
    balanced: 'text-brand-dark-accent',
    clash: 'text-rose-300'
  };
  const VERDICT_STYLE: Record<Verdict, string> = {
    safe: 'bg-emerald-50 text-emerald-800 ring-emerald-200',
    consider: 'bg-amber-50 text-amber-900 ring-amber-200',
    clash: 'bg-rose-50 text-rose-800 ring-rose-200'
  };

  function toPartner(form: PartnerForm): PartnerIn {
    return {
      name: form.name.trim() || null,
      birth_date: form.birth_date,
      birth_time: form.timeUnknown || !form.birth_time ? null : form.birth_time,
      zone: form.zone
    };
  }

  const request = $derived<BaziRequest>({
    partners: [toPartner(partners[0]), toPartner(partners[1])],
    dates: [],
    locale: locale === 'en' ? 'en' : 'id'
  });
  const filledDates = $derived(uniqueDates(dates));
  const inputKey = $derived(JSON.stringify(request));
  const stale = $derived(bazi !== null && resultKey !== inputKey);

  const names = $derived(displayNames([partners[0].name, partners[1].name], copy.form.partnerFallback));
  const uncertain = $derived(bazi !== null && hasUncertainPillar(bazi.charts));

  async function calculate(withDates = unlocked && filledDates.length > 0) {
    error = '';
    dateError = '';
    if (!request.partners.every(isCompleteBirth)) {
      error = copy.form.missing;
      return;
    }
    loading = true;
    const key = inputKey;
    try {
      bazi = await fetchBazi({ ...request, dates: withDates ? filledDates : [] });
      resultKey = key;
    } catch (failure) {
      // Whatever was typed stays in the form; only the message changes, and it
      // shows beside the button that was pressed, worded for that action.
      const kind = failureKind(failure);
      if (withDates) dateError = copy.dates[kind];
      else error = copy.form[kind];
    } finally {
      loading = false;
    }
  }

  async function checkDates() {
    dateError = '';
    if (!bazi) {
      dateError = copy.dates.needResult;
      return;
    }
    if (!filledDates.length) {
      dateError = copy.dates.needDate;
      return;
    }
    await calculate(true);
  }

  function onUnlocked() {
    unlocked = true;
    if (bazi && filledDates.length) void checkDates();
  }

  const pairOf = (pillar: PillarOut): [string, string] => [pillar.stem.char, pillar.branch.char];

  const cardCharts = $derived<BaziCardChart[]>(
    (bazi?.charts ?? []).map((chart, index) => ({
      name: names[index],
      pillars: [chart.year, chart.month, chart.day, chart.hour].map((p) => (p ? pairOf(p) : null)),
      summary: `${copy.result.dayMaster} ${chart.day_master.char} ${chart.day_master.element_label} · ${copy.result.shio} ${chart.shio.animal_label}`
    }))
  );
  const cardDates = $derived<BaziCardDate[]>(
    (bazi?.date_checks ?? []).map((check) => ({
      label: formatMasehi(check.date, locale),
      verdict: check.verdict
    }))
  );
  const cardLabel = $derived(
    [copy.card.title, names.join(' & '), bazi?.tone_label, ...cardDates.map((d) => `${d.label}: ${copy.card.verdicts[d.verdict]}`)]
      .filter(Boolean)
      .join(', ')
  );

  // Before unlock the API has not seen the dates, so the lead carries them as
  // typed; after a check it carries each date with its verdict.
  const leadInputs = $derived.by(() => {
    if (!bazi) return { dates: filledDates.join(',') };
    const inputs = baziLeadInputs(bazi);
    return inputs.dates ? inputs : { ...inputs, dates: filledDates.join(',') };
  });

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

  const example = $derived(copy.example);

  function tryExample() {
    partners = example.partners.map((p) => ({
      name: p.name ?? '',
      birth_date: p.birth_date,
      birth_time: p.birth_time ?? '',
      timeUnknown: p.birth_time === null,
      zone: p.zone
    }));
    dates = Array.from({ length: MAX_DATES }, (_, index) => example.dates[index] ?? '');
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.getElementById('bazi-result')?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    void calculate();
  }

  const FIELD =
    'h-11 w-full rounded-md border border-input bg-background px-3 text-base placeholder:text-muted-foreground/60 focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none md:text-[15px] disabled:opacity-50';
  const LEGEND = 'text-[13px] font-semibold tracking-wide text-foreground';
</script>

<svelte:head>
  <title>{copy.meta.title}</title>
  <meta name="description" content={copy.meta.description} />
  <meta name="keywords" content={copy.meta.keywords} />
  <link rel="canonical" href={canonical} />
  {@html jsonLd}
</svelte:head>

<SocialMeta title={copy.meta.title} description={copy.meta.description} url={canonical} />

{#snippet chartPanel(chart: ChartOut, index: number)}
  {@const total = Object.values(chart.elements).reduce((a, b) => a + b, 0) || 1}
  <div class="rounded-xl border border-white/10 bg-white/[0.04] p-4">
    <div class="flex items-baseline justify-between gap-3">
      <p class="font-display text-lg font-semibold">{names[index]}</p>
      <p class="text-xs text-white/60">{copy.result.shio}: {chart.shio.animal_label}</p>
    </div>

    <div class="mt-3 grid grid-cols-4 gap-2">
      {#each PILLARS as key (key)}
        {@const pillar = chart[key]}
        <div class="text-center">
          <p class="text-[11px] font-semibold tracking-wider text-white/50 uppercase">{copy.result.pillars[key]}</p>
          {#if pillar}
            <div
              class="mt-1.5 rounded-lg bg-white/[0.06] px-1 py-2 {pillar.depends_on_time || pillar.near_term
                ? 'ring-1 ring-brand-dark-accent/70'
                : ''}"
            >
              <p class="text-3xl leading-tight" lang="zh">{pillar.stem.char}</p>
              <p class="text-[11px] leading-4 text-white/60">{pillar.stem.pinyin}<br />{pillar.stem.element_label}</p>
              <p class="mt-1 text-3xl leading-tight text-brand-dark-accent" lang="zh">{pillar.branch.char}</p>
              <p class="text-[11px] text-white/60">{pillar.branch.animal_label}</p>
            </div>
          {:else}
            <div class="mt-1.5 flex h-[118px] items-center justify-center rounded-lg border border-dashed border-white/15 px-1">
              <p class="text-[11px] leading-4 text-white/50">{copy.result.hourUnknown}</p>
            </div>
          {/if}
        </div>
      {/each}
    </div>

    {#each PILLARS as key (key)}
      {@const pillar = chart[key]}
      {#if pillar?.depends_on_time || pillar?.near_term}
        <p class="mt-3 flex gap-2 text-xs leading-5 text-white/70">
          <InfoIcon size={14} class="mt-0.5 shrink-0 text-brand-dark-accent" aria-hidden="true" />
          <span
            ><strong class="font-semibold text-white/85">{copy.result.pillars[key]}:</strong>
            {pillar.depends_on_time ? copy.result.dependsOnTime : copy.result.nearTerm}</span
          >
        </p>
      {/if}
    {/each}

    <div class="mt-4 rounded-lg bg-white/[0.04] p-3">
      <p class="text-xs text-white/60">{copy.result.dayMaster}</p>
      <p class="mt-0.5 font-semibold">
        <span lang="zh">{chart.day_master.char}</span>
        {chart.day_master.pinyin} · {chart.day_master.element_label}
      </p>
      <p class="mt-1 text-sm leading-6 text-white/75">{copy.result.dayMasters[chart.day_master.index]}</p>
    </div>

    <div class="mt-4">
      <p class="text-xs text-white/60">{copy.result.elements}</p>
      <ul class="mt-2 grid gap-1.5">
        {#each ELEMENT_ORDER as element (element)}
          <li class="flex items-center gap-2 text-xs">
            <span class="w-14 shrink-0 text-white/75">{copy.result.elementNames[element]}</span>
            <span class="h-2 flex-1 overflow-hidden rounded-full bg-white/10">
              <span class="block h-full rounded-full {ELEMENT_TONE[element].bar}" style="width: {(chart.elements[element] / total) * 100}%"></span>
            </span>
            <span class="w-4 text-right text-white/70 tabular-nums">{chart.elements[element]}</span>
          </li>
        {/each}
      </ul>
    </div>
  </div>
{/snippet}

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
    <form
      class="grid gap-7"
      onsubmit={(event) => {
        event.preventDefault();
        void calculate();
      }}
    >
      {#each partners as partner, index (index)}
        <fieldset class="grid gap-3">
          <legend class={LEGEND}>{copy.form.partnerLegend[index]}</legend>
          <div class="mt-3 grid gap-3 sm:grid-cols-2">
            <div class="grid gap-1.5">
              <label for="bazi-name-{index}" class="text-xs text-muted-foreground">{copy.form.nameLabel}</label>
              <input
                id="bazi-name-{index}"
                bind:value={partner.name}
                maxlength="40"
                autocomplete="off"
                autocapitalize="words"
                placeholder={copy.form.namePlaceholders[index]}
                class={FIELD}
              />
            </div>
            <div class="grid gap-1.5">
              <label for="bazi-date-{index}" class="text-xs text-muted-foreground">{copy.form.birthDateLabel}</label>
              <DateField
                id="bazi-date-{index}"
                bind:value={partner.birth_date}
                {locale}
                placeholder={copy.form.datePlaceholder}
                class="h-11 w-full text-base md:text-[15px]"
              />
            </div>
            <div class="grid gap-1.5">
              <label for="bazi-time-{index}" class="text-xs text-muted-foreground">{copy.form.birthTimeLabel}</label>
              <input
                id="bazi-time-{index}"
                type="time"
                bind:value={partner.birth_time}
                disabled={partner.timeUnknown}
                class={FIELD}
              />
              <label class="flex items-center gap-2 text-xs text-muted-foreground">
                <input type="checkbox" bind:checked={partner.timeUnknown} class="size-4 accent-brand-gold" />
                {copy.form.timeUnknown}
              </label>
            </div>
            <div class="grid content-start gap-1.5">
              <label for="bazi-zone-{index}" class="text-xs text-muted-foreground">{copy.form.zoneLabel}</label>
              <select id="bazi-zone-{index}" bind:value={partner.zone} class={FIELD}>
                {#each ZONES as zone (zone)}
                  <option value={zone}>{copy.form.zones[zone]}</option>
                {/each}
              </select>
            </div>
          </div>
        </fieldset>
      {/each}

      <p class="-mt-3 text-xs leading-5 text-muted-foreground">{copy.form.timeHint}</p>

      <div>
        <Button type="submit" variant="gold" size="lg" class="w-full sm:w-auto sm:px-10" disabled={loading}>
          <SparklesIcon size={17} aria-hidden="true" />
          {loading ? copy.form.calculating : copy.form.calculate}
        </Button>
        {#if error}
          <p class="mt-3 text-sm text-destructive" role="alert">{error}</p>
        {:else if stale}
          <p class="mt-3 text-sm text-muted-foreground" role="status">{copy.form.stale}</p>
        {/if}
      </div>
    </form>
  {/snippet}

  {#snippet result()}
    <div id="bazi-result" class="grid scroll-mt-24 gap-5">
      <div
        class="relative overflow-hidden rounded-2xl bg-brand-ink p-5 text-white shadow-[0_24px_60px_-30px_rgba(20,20,20,0.6)] md:p-7"
        aria-live="polite"
        aria-busy={loading}
      >
        <div
          aria-hidden="true"
          class="pointer-events-none absolute -top-20 -right-16 size-56 rounded-full bg-brand-gold/25 blur-3xl"
        ></div>
        <p class="relative text-xs font-semibold tracking-[0.2em] text-brand-dark-accent uppercase">
          {copy.result.title}
        </p>

        {#if bazi}
          <div class="relative mt-4 grid gap-4 md:grid-cols-2 {stale ? 'opacity-60' : ''}">
            {#each bazi.charts as chart, index (index)}
              {@render chartPanel(chart, index)}
            {/each}
          </div>

          <div class="relative mt-6 border-t border-white/15 pt-5">
            <p class="text-xs font-semibold tracking-wide text-white/60">{copy.result.toneTitle}</p>
            <p class="mt-1 font-display text-2xl font-bold {TONE_STYLE[bazi.tone]}">{bazi.tone_label}</p>

            {#if uncertain}
              <p class="mt-4 flex gap-2 rounded-lg border border-brand-dark-accent/40 p-3 text-[13px] leading-6 text-white/80">
                <InfoIcon size={15} class="mt-1 shrink-0 text-brand-dark-accent" aria-hidden="true" />
                {copy.result.uncertainNote}
              </p>
            {/if}

            <p class="mt-5 text-xs font-semibold tracking-wide text-white/60">{copy.result.findingsTitle}</p>
            {#if bazi.findings.length}
              <ul class="mt-2 grid gap-3">
                {#each bazi.findings as finding, index (index)}
                  <li class="flex gap-3 text-sm leading-6 text-white/85">
                    <span
                      class="mt-2 size-2 shrink-0 rounded-full {finding.kind === 'harmony'
                        ? 'bg-emerald-400'
                        : finding.kind === 'clash'
                          ? 'bg-rose-400'
                          : finding.kind === 'caution'
                            ? 'bg-amber-400'
                            : 'bg-white/40'}"
                      aria-hidden="true"
                    ></span>
                    <span>
                      <span class="font-semibold text-white">{finding.rule_label}</span>
                      <span class="text-white/50" lang="zh">({finding.a} · {finding.b})</span>
                      <br />{reading(locale, finding, bazi.charts, names)}
                    </span>
                  </li>
                {/each}
              </ul>
            {:else}
              <p class="mt-2 text-sm text-white/75">{copy.result.noFindings}</p>
            {/if}

            <p class="mt-5 flex gap-2 rounded-lg bg-white/[0.06] p-3 text-[13px] leading-6 text-white/75">
              <InfoIcon size={15} class="mt-1 shrink-0 text-brand-dark-accent" aria-hidden="true" />
              {copy.result.elderNote}
            </p>
          </div>
        {:else}
          <p class="relative mt-3 text-sm leading-6 text-white/70">{copy.result.empty}</p>
        {/if}
      </div>

      <div class="rounded-2xl border border-border bg-background p-5 md:p-6">
        <h2 class="flex items-center gap-2 font-display text-lg font-bold">
          <CalendarCheckIcon size={18} class="text-brand-gold" aria-hidden="true" />
          {copy.dates.title}
        </h2>
        <p class="mt-1 text-sm leading-6 text-muted-foreground">{copy.dates.lead}</p>

        <div class="mt-4 grid gap-3 sm:grid-cols-2">
          {#each dates as _, index (index)}
            <div class="grid gap-1.5">
              <label for="bazi-check-{index}" class="text-xs text-muted-foreground">{copy.dates.label(index)}</label>
              <DateField
                id="bazi-check-{index}"
                bind:value={dates[index]}
                {locale}
                placeholder={copy.form.datePlaceholder}
                class="h-11 w-full text-base md:text-[15px]"
              />
            </div>
          {/each}
        </div>

        <div class="relative mt-4">
          {#if unlocked}
            <Button variant="outline" size="lg" onclick={checkDates} disabled={loading}>
              <CalendarCheckIcon size={17} aria-hidden="true" />
              {loading ? copy.dates.checking : copy.dates.check}
            </Button>
            {#if dateError}
              <p class="mt-2 text-sm text-destructive" role="alert">{dateError}</p>
            {/if}
            {#if bazi?.date_checks.length}
              <ul class="mt-4 grid gap-3">
                {#each bazi.date_checks as check, index (index)}
                  {@const day = { char: `${check.pillar.stem.char}${check.pillar.branch.char}`, animal: check.pillar.branch.animal_label }}
                  <li class="rounded-xl border border-border p-4">
                    <div class="flex flex-wrap items-center justify-between gap-2">
                      <p class="font-semibold">{formatMasehi(check.date, locale)}</p>
                      <span class="rounded-full px-3 py-1 text-xs font-semibold ring-1 {VERDICT_STYLE[check.verdict]}">
                        {copy.dates.verdicts[check.verdict]}
                      </span>
                    </div>
                    <p class="mt-1 text-xs text-muted-foreground">
                      <span lang="zh">{day.char}</span> · {day.animal}
                    </p>
                    <ul class="mt-2 grid gap-1 text-sm leading-6 text-foreground/80">
                      {#each check.reasons as reason, index (index)}
                        <li>{dateReason(locale, reason, day, bazi.charts, names)}</li>
                      {:else}
                        <li>{copy.dates.quiet}</li>
                      {/each}
                    </ul>
                  </li>
                {/each}
              </ul>
            {/if}
          {:else}
            <div class="flex flex-col items-start gap-3 rounded-xl bg-brand-warm p-4 sm:flex-row sm:items-center sm:justify-between">
              <div class="flex gap-3">
                <span class="flex size-10 shrink-0 items-center justify-center rounded-full bg-background text-brand-gold-hover shadow-sm">
                  <LockIcon size={18} aria-hidden="true" />
                </span>
                <div>
                  <p class="font-display font-bold text-brand-ink">{copy.dates.lockedTitle}</p>
                  <p class="text-sm leading-6 text-brand-ink/75">{copy.dates.lockedCopy}</p>
                </div>
              </div>
              <Button variant="gold" size="lg" class="shrink-0 px-8" onclick={() => (gateOpen = true)}>
                {copy.dates.unlock}
              </Button>
            </div>
          {/if}
        </div>
      </div>

      <div class="rounded-2xl border border-border bg-background p-5 md:p-6">
        <div class="flex items-baseline justify-between gap-3">
          <h2 class="font-display text-lg font-bold">{copy.card.title}</h2>
          <span class="text-xs text-muted-foreground">A5 · PNG</span>
        </div>
        <p class="mt-1 text-sm leading-6 text-muted-foreground">{copy.card.lead}</p>

        <div class="relative mt-4 overflow-hidden rounded-xl bg-brand-warm ring-1 ring-brand-gold/20">
          <BaziCard
            bind:this={card}
            charts={cardCharts}
            tone={bazi?.tone_label ?? ''}
            dates={cardDates}
            copy={copy.card}
            label={cardLabel}
            class="block h-auto w-full transition duration-500 {unlocked ? '' : 'scale-105 blur-[7px] saturate-75'}"
          />
          {#if !unlocked}
            <div class="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-brand-warm/40 p-6 text-center">
              <span class="flex size-12 items-center justify-center rounded-full bg-background text-brand-gold-hover shadow-md">
                <LockIcon size={20} aria-hidden="true" />
              </span>
              <p class="font-display text-lg font-bold text-brand-ink">{copy.dates.lockedTitle}</p>
              <p class="max-w-xs text-sm leading-6 text-brand-ink/75">{copy.dates.lockedCopy}</p>
              <Button variant="gold" size="lg" class="px-8" onclick={() => (gateOpen = true)}>
                {copy.dates.unlock}
              </Button>
            </div>
          {/if}
        </div>

        {#if unlocked}
          <div class="mt-4 grid gap-2.5 sm:grid-cols-2">
            <Button variant="gold" size="lg" onclick={downloadPng} disabled={exporting || !bazi}>
              <DownloadIcon size={17} aria-hidden="true" />
              {exporting ? copy.card.exporting : copy.card.downloadPng}
            </Button>
            <Button variant="outline" size="lg" onclick={() => card?.print()} disabled={!bazi}>
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
      tool="bazi"
      title={copy.card.gateTitle}
      description={copy.card.gateDescription}
      names={partners
        .map((p) => p.name.trim())
        .filter(Boolean)
        .join(' & ')}
      inputs={leadInputs}
      sourcePath={TOOL_PATH}
      {onUnlocked}
    />
  {/snippet}

  {#snippet explainer()}
    <section class="border-y border-border bg-brand-warm/60 px-5 py-16 lg:px-8">
      <div class="mx-auto max-w-4xl">
        <h2 class="font-display text-2xl font-bold md:text-3xl">{copy.intro.title}</h2>
        {#each copy.intro.paragraphs as paragraph, index (index)}
          <p class="mt-4 text-base leading-8 text-foreground/80">{paragraph}</p>
        {/each}

        <h3 class="mt-10 text-xs font-semibold tracking-[0.2em] text-brand-gold-hover uppercase">
          {copy.intro.termsTitle}
        </h3>
        <dl class="mt-4 grid gap-4 sm:grid-cols-2">
          {#each copy.intro.terms as item (item.term)}
            <div class="rounded-xl border border-brand-gold/25 bg-background p-5">
              <dt class="flex items-baseline gap-2 font-display text-base font-semibold">
                <span lang="zh-Hans" class="text-xl text-brand-gold-hover">{item.han}</span>
                {item.term}
              </dt>
              <dd class="mt-2 text-sm leading-6 text-foreground/75">{item.text}</dd>
            </div>
          {/each}
        </dl>
      </div>
    </section>

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
          <div class="rounded-xl bg-brand-warm p-5">
            <h3 class="font-display text-base font-semibold">{copy.result.conventionsTitle}</h3>
            <ul class="mt-2 grid list-disc gap-1.5 pl-5 text-sm leading-6 text-foreground/80">
              {#each copy.result.conventions as line, index (index)}
                <li>{line}</li>
              {/each}
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-brand-ink px-5 py-16 text-white lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <span
          class="inline-block rounded-full border border-white/20 px-3 py-1 text-[11px] font-semibold tracking-wider text-white/70 uppercase"
        >
          {example.badge}
        </span>
        <h2 class="mt-4 font-display text-2xl font-bold md:text-3xl">{example.title}</h2>
        <p class="mx-auto mt-3 max-w-xl text-[15px] leading-7 text-white/70">{example.lead}</p>
        <p class="mt-4 text-sm text-white/60">{example.summary}</p>
        <button
          type="button"
          onclick={tryExample}
          class="mt-6 rounded-full border border-brand-dark-accent/50 px-5 py-2 text-sm font-medium text-brand-dark-accent transition hover:bg-brand-dark-accent hover:text-brand-ink focus-visible:ring-3 focus-visible:ring-brand-dark-accent/40 focus-visible:outline-none"
        >
          {example.tryIt}
        </button>
      </div>
    </section>
  {/snippet}
</ToolShell>
