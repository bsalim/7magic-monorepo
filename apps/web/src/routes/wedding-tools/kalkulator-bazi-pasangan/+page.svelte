<script lang="ts">
  import { onMount } from 'svelte';
  import CalendarCheckIcon from '@lucide/svelte/icons/calendar-check';
  import CheckIcon from '@lucide/svelte/icons/check';
  import CircleAlertIcon from '@lucide/svelte/icons/circle-alert';
  import InfoIcon from '@lucide/svelte/icons/info';
  import LockIcon from '@lucide/svelte/icons/lock';
  import MailCheckIcon from '@lucide/svelte/icons/mail-check';
  import SendIcon from '@lucide/svelte/icons/send';
  import SparklesIcon from '@lucide/svelte/icons/sparkles';
  import XIcon from '@lucide/svelte/icons/x';
  import DateField from '$lib/components/DateField.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import BirthDateField from '$lib/components/tools/BirthDateField.svelte';
  import BirthTimeField from '$lib/components/tools/BirthTimeField.svelte';
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
    type Element,
    type FindingOut,
    type PartnerIn,
    type PillarOut,
    type Tone,
    type Verdict,
    type Zone
  } from '$lib/tools/bazi';
  import { isUnlocked } from '$lib/tools/lead';
  import { formatMasehi } from '$lib/tools/mahar';
  import { TOOL_PATH, baziCopy, dateReason, reading, type PillarKey } from './content';
  import { PREVIEW, PREVIEW_NAMES } from './preview';

  /**
   * The Ba Zi couple calculator: two birth moments and up to three candidate
   * wedding dates in, two charts, a traditional reading and a verdict per date
   * out.
   *
   * Unlike mahar and hashtag the calculation is not in the browser: the API
   * owns the astronomy (`app/domains/bazi`), and this page posts to it through
   * the `/api/bazi` proxy on a button press rather than on every keystroke.
   *
   * The page reads top to bottom as one flow: the form, then the result in its
   * own band. The whole result sits behind the shared soft gate. A visitor who
   * has not unlocked still gets their calculation run, but it waits in
   * `pending`, shown blurred, while the gate sits over it; passing the gate
   * reveals it and has the API email them the card and a copy. Someone who
   * unlocked on another tool is not asked again, as the gate promises, so they
   * are offered the email as a button beside the card instead.
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

  // An empty birth_time is "unknown": the hour dropdown left blank says so.
  type PartnerForm = { name: string; birth_date: string; birth_time: string; zone: Zone };
  const blankPartner = (): PartnerForm => ({ name: '', birth_date: '', birth_time: '', zone: 'WIB' });
  type Calculated = { result: BaziResponse; key: string; calculation: BaziRequest };

  let partners = $state<PartnerForm[]>([blankPartner(), blankPartner()]);
  let dates = $state<string[]>(Array.from({ length: MAX_DATES }, () => ''));

  // The result on show, with the inputs it came from: to tell the visitor when
  // it is stale, and to email exactly this result later.
  let shown = $state<Calculated | null>(null);
  // Calculated before asking, not after: a mistyped date is corrected first,
  // and the lead and the emailed copy describe a result that exists.
  let pending = $state<Calculated | null>(null);
  let loading = $state(false);
  let error = $state('');

  let unlocked = $state(false);
  // Known only in the browser: until then the page cannot say whether this
  // visitor will meet the gate, so it does not warn them of one.
  let mounted = $state(false);
  // Whether the result on show has been emailed, which only the gate does.
  let copySent = $state(false);
  let sendOpen = $state(false);

  onMount(() => {
    unlocked = isUnlocked();
    mounted = true;
  });

  const ZONES: Zone[] = ['WIB', 'WITA', 'WIT'];
  const PILLARS: PillarKey[] = ['year', 'month', 'day', 'hour'];
  const ELEMENT_ORDER: Element[] = ['wood', 'fire', 'earth', 'metal', 'water'];
  const ELEMENT_BAR: Record<Element, string> = {
    wood: 'bg-emerald-600',
    fire: 'bg-rose-600',
    earth: 'bg-amber-600',
    metal: 'bg-slate-500',
    water: 'bg-sky-600'
  };
  const TONE_STYLE: Record<Tone, string> = {
    harmony: 'text-emerald-800',
    balanced: 'text-brand-gold-hover',
    clash: 'text-rose-800'
  };
  // A different mark per kind as well as a different hue, so the two harmonies
  // and a caution are told apart without relying on colour.
  const KIND_STYLE: Record<FindingOut['kind'], { text: string; mark: string }> = {
    harmony: { text: 'text-emerald-800', mark: 'rounded-full bg-emerald-600' },
    caution: { text: 'text-amber-900', mark: 'rounded-[2px] bg-amber-600' },
    clash: { text: 'text-rose-800', mark: 'rotate-45 rounded-[2px] bg-rose-700' },
    neutral: { text: 'text-slate-700', mark: 'rounded-full bg-slate-400' }
  };
  const VERDICT_STYLE: Record<Verdict, string> = {
    safe: 'bg-emerald-50 text-emerald-900 ring-emerald-200',
    consider: 'bg-amber-50 text-amber-900 ring-amber-300',
    clash: 'bg-rose-800 text-white ring-rose-800'
  };
  // The page loads no Chinese webfont; this is the card's own stack.
  const HAN = "font-family: 'Noto Serif SC', 'Songti SC', 'STSong', 'SimSun', serif";

  function toPartner(form: PartnerForm): PartnerIn {
    return {
      name: form.name.trim() || null,
      birth_date: form.birth_date,
      birth_time: form.birth_time || null,
      zone: form.zone
    };
  }

  const request = $derived<BaziRequest>({
    partners: [toPartner(partners[0]), toPartner(partners[1])],
    dates: uniqueDates(dates),
    locale: locale === 'en' ? 'en' : 'id'
  });
  const inputKey = $derived(JSON.stringify(request));

  const bazi = $derived(shown?.result ?? null);
  const stale = $derived(shown !== null && shown.key !== inputKey);
  // A pending result is only offered while it still matches the form: edit a
  // field and the gate steps back until the new inputs are calculated.
  const awaitingGate = $derived(pending !== null && pending.key === inputKey ? pending : null);
  const locked = $derived(shown === null);

  const names = $derived(displayNames([partners[0].name, partners[1].name], copy.form.partnerFallback));
  // What the result band draws: the real result, the one waiting behind the
  // gate, or the example couple as a blurred stand-in.
  const view = $derived(
    shown
      ? { result: shown.result, names }
      : awaitingGate
        ? { result: awaitingGate.result, names }
        : { result: PREVIEW, names: PREVIEW_NAMES }
  );
  const leadNames = $derived(
    partners
      .map((p) => p.name.trim())
      .filter(Boolean)
      .join(' & ')
  );

  function scrollToResult() {
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    document.getElementById('bazi-result')?.scrollIntoView?.({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  }

  async function calculate() {
    error = '';
    if (!request.partners.every(isCompleteBirth)) {
      error = copy.form.missing;
      return;
    }
    loading = true;
    const calculated = { key: inputKey, calculation: request };
    try {
      const result = await fetchBazi(calculated.calculation);
      if (unlocked) {
        shown = { ...calculated, result };
        // Only a result that passed the gate was emailed.
        copySent = false;
      } else {
        pending = { ...calculated, result };
      }
      // The result is a band below the form, out of sight on a phone.
      scrollToResult();
    } catch (failure) {
      // Whatever was typed stays in the form; only the message changes.
      error = copy.form[failureKind(failure)];
    } finally {
      loading = false;
    }
  }

  function onUnlocked() {
    unlocked = true;
    const ready = awaitingGate;
    pending = null;
    if (!ready) return;
    shown = ready;
    copySent = true;
  }

  function fillExample() {
    partners = copy.example.partners.map((p) => ({
      name: p.name ?? '',
      birth_date: p.birth_date,
      birth_time: p.birth_time ?? '',
      zone: p.zone
    }));
    dates = Array.from({ length: MAX_DATES }, (_, index) => copy.example.dates[index] ?? '');
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

  const FIELD =
    'h-12 w-full rounded-lg border border-input bg-background px-3.5 text-base placeholder:text-muted-foreground/60 focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none disabled:opacity-50';
  const LABEL = 'text-[13px] font-medium text-foreground/75';
  const EYEBROW = 'text-xs font-semibold tracking-[0.2em] text-brand-gold-hover uppercase';
  const CAPTION = 'text-xs font-semibold tracking-wider text-foreground/60 uppercase';
</script>

<svelte:head>
  <title>{copy.meta.title}</title>
  <meta name="description" content={copy.meta.description} />
  <meta name="keywords" content={copy.meta.keywords} />
  <link rel="canonical" href={canonical} />
  {@html jsonLd}
</svelte:head>

<SocialMeta title={copy.meta.title} description={copy.meta.description} url={canonical} />

{#snippet chartPanel(chart: ChartOut, name: string)}
  {@const total = Object.values(chart.elements).reduce((a, b) => a + b, 0) || 1}
  <article class="min-w-0 rounded-2xl border border-brand-warm-deep bg-background p-4 sm:p-6">
    <div class="flex items-baseline justify-between gap-3">
      <h3 class="font-display text-xl font-semibold">{name}</h3>
      <p class="text-sm text-foreground/65">{copy.result.shio}: {chart.shio.animal_label}</p>
    </div>

    <div class="mt-4 grid grid-cols-4 gap-1.5 sm:gap-2.5">
      {#each PILLARS as key (key)}
        {@const pillar = chart[key]}
        <!-- The day pillar holds the day master and the spouse palace, the two
             things the reading turns on, so it is the one picked out. -->
        <div
          class="rounded-xl px-1 py-3 text-center {key === 'day'
            ? 'bg-brand-gold-soft ring-1 ring-brand-gold/60'
            : 'bg-brand-warm'}"
        >
          <p class="text-[11px] font-semibold tracking-wider uppercase {key === 'day' ? 'text-brand-gold-hover' : 'text-foreground/60'}">
            {copy.result.pillars[key]}
          </p>
          {#if pillar}
            <p class="mt-1.5 text-[clamp(2.1rem,2.9vw,2.6rem)] leading-tight" lang="zh" style={HAN}>{pillar.stem.char}</p>
            <p class="text-xs leading-4 text-foreground/65">{pillar.stem.pinyin}<br />{pillar.stem.element_label}</p>
            <p class="mt-1.5 text-[clamp(2.1rem,2.9vw,2.6rem)] leading-tight text-brand-gold-hover" lang="zh" style={HAN}>
              {pillar.branch.char}
            </p>
            <p class="text-xs leading-4 text-foreground/65">{pillar.branch.pinyin}<br />{pillar.branch.animal_label}</p>
          {:else}
            <p class="mt-6 px-1 text-xs leading-4 text-foreground/60">{copy.result.hourUnknown}</p>
          {/if}
        </div>
      {/each}
    </div>

    {#each PILLARS as key (key)}
      {@const pillar = chart[key]}
      {#if pillar?.depends_on_time || pillar?.near_term}
        <p class="mt-3 flex gap-2 text-[13px] leading-5 text-foreground/75">
          <InfoIcon size={15} class="mt-0.5 shrink-0 text-brand-gold-hover" aria-hidden="true" />
          <span
            ><strong class="font-semibold text-foreground">{copy.result.pillars[key]}:</strong>
            {pillar.depends_on_time ? copy.result.dependsOnTime : copy.result.nearTerm}</span
          >
        </p>
      {/if}
    {/each}

    <div class="mt-4 rounded-xl bg-brand-warm p-4">
      <p class={CAPTION}>{copy.result.dayMaster}</p>
      <p class="mt-1 text-[17px] font-semibold">
        <span lang="zh" style={HAN}>{chart.day_master.char}</span>
        {chart.day_master.pinyin} · {chart.day_master.element_label}
      </p>
      <p class="mt-1 text-[15px] leading-6 text-foreground/80">{copy.result.dayMasters[chart.day_master.index]}</p>
    </div>

    <div class="mt-4">
      <p class={CAPTION}>{copy.result.elements}</p>
      <ul class="mt-2.5 grid gap-2">
        {#each ELEMENT_ORDER as element (element)}
          <li class="flex items-center gap-2.5 text-[13px]">
            <span class="w-14 shrink-0 text-foreground/80">{copy.result.elementNames[element]}</span>
            <span class="h-2 flex-1 overflow-hidden rounded-full bg-brand-warm-deep/70">
              <span class="block h-full rounded-full {ELEMENT_BAR[element]}" style="width: {(chart.elements[element] / total) * 100}%"></span>
            </span>
            <span class="w-4 text-right text-foreground/80 tabular-nums">{chart.elements[element]}</span>
          </li>
        {/each}
      </ul>
    </div>
  </article>
{/snippet}

{#snippet resultBody(result: BaziResponse, who: [string, string], emailed: boolean)}
  <div class="flex flex-wrap items-end justify-between gap-5 border-b border-brand-warm-deep pb-7">
    <div>
      <p class="text-sm text-foreground/65">{copy.result.toneTitle} · {who.join(' & ')}</p>
      <p class="mt-1.5 font-display text-[clamp(1.9rem,4vw,2.9rem)] leading-tight font-bold {TONE_STYLE[result.tone]}">
        {result.tone_label}
      </p>
    </div>
    {#if emailed}
      <p class="flex max-w-sm gap-2.5 rounded-xl border border-brand-gold/40 bg-background px-4 py-3.5 text-sm leading-6 text-foreground/85">
        <MailCheckIcon size={18} class="mt-0.5 shrink-0 text-brand-gold-hover" aria-hidden="true" />
        {copy.result.copySent}
      </p>
    {/if}
  </div>

  <div class="mt-7 grid gap-5 lg:grid-cols-2 lg:gap-6">
    {#each result.charts as chart, index (index)}
      {@render chartPanel(chart, who[index])}
    {/each}
  </div>

  {#if hasUncertainPillar(result.charts)}
    <p class="mt-6 flex gap-2.5 rounded-xl border border-brand-gold/40 bg-background p-4 text-sm leading-6 text-foreground/85">
      <InfoIcon size={17} class="mt-0.5 shrink-0 text-brand-gold-hover" aria-hidden="true" />
      {copy.result.uncertainNote}
    </p>
  {/if}

  <h3 class="mt-10 font-display text-xl font-semibold">{copy.result.findingsTitle}</h3>
  {#if result.findings.length}
    <ul class="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {#each result.findings as finding, index (index)}
        {@const style = KIND_STYLE[finding.kind]}
        <li class="rounded-2xl border border-brand-warm-deep bg-background p-5">
          <p class="flex items-center gap-2 text-xs font-semibold tracking-wider uppercase {style.text}">
            <span class="size-2 shrink-0 {style.mark}" aria-hidden="true"></span>
            {copy.result.kinds[finding.kind]} · {copy.result.scopes[finding.pillar]}
          </p>
          <p class="mt-2.5 text-[17px] leading-snug font-semibold">
            {finding.rule_label}
            <span class="font-normal text-foreground/60" lang="zh" style={HAN}>{finding.a} · {finding.b}</span>
          </p>
          <p class="mt-2 text-[15px] leading-6 text-foreground/80">{reading(locale, finding, result.charts, who)}</p>
        </li>
      {/each}
    </ul>
  {:else}
    <p class="mt-3 text-[15px] leading-6 text-foreground/80">{copy.result.noFindings}</p>
  {/if}

  <p class="mt-7 flex gap-2.5 rounded-xl border border-brand-warm-deep bg-background p-4 text-sm leading-6 text-foreground/75">
    <InfoIcon size={17} class="mt-0.5 shrink-0 text-brand-gold-hover" aria-hidden="true" />
    {copy.result.elderNote}
  </p>
{/snippet}

<ToolShell
  stacked
  watermark="八字"
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
  {#snippet heroExtra()}
    <ol class="mt-7 flex flex-col gap-x-8 gap-y-3 sm:flex-row sm:flex-wrap">
      {#each copy.hero.steps as step, index (index)}
        <li class="flex items-center gap-3 text-[15px] font-medium">
          <span
            aria-hidden="true"
            class="flex size-8 shrink-0 items-center justify-center rounded-full bg-brand-ink font-display text-sm font-semibold text-white"
          >
            {index + 1}
          </span>
          {step}
        </li>
      {/each}
    </ol>
  {/snippet}

  {#snippet inputs()}
    <form
      id="bazi-form"
      class="grid scroll-mt-24 gap-7"
      onsubmit={(event) => {
        event.preventDefault();
        void calculate();
      }}
    >
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h2 class="font-display text-xl font-semibold md:text-[22px]">{copy.form.title}</h2>
        <button
          type="button"
          onclick={fillExample}
          class="min-h-11 rounded-full border border-brand-gold/40 bg-brand-gold-soft px-4 text-sm font-medium text-brand-gold-hover transition hover:border-brand-gold focus-visible:ring-3 focus-visible:ring-ring/40 focus-visible:outline-none"
        >
          {copy.example.tryIt}
        </button>
      </div>

      <div class="grid gap-5 lg:grid-cols-2">
        {#each partners as partner, index (index)}
          <fieldset class="min-w-0 rounded-2xl border border-border bg-brand-warm/50 p-4 sm:p-6">
            <legend class="px-2 font-display text-xs font-semibold tracking-wider text-brand-gold-hover uppercase">
              {copy.form.partnerLegend[index]}
            </legend>
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="grid content-start gap-1.5 sm:col-span-2">
                <label for="bazi-name-{index}" class={LABEL}>{copy.form.nameLabel}</label>
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
              <div class="grid content-start gap-1.5 sm:col-span-2">
                <label id="bazi-date-{index}-label" for="bazi-date-{index}" class={LABEL}>{copy.form.birthDateLabel}</label>
                <BirthDateField
                  id="bazi-date-{index}"
                  labelledby="bazi-date-{index}-label"
                  bind:value={partner.birth_date}
                  {locale}
                  labels={copy.form.birthParts}
                />
              </div>
              <div class="grid content-start gap-1.5">
                <label id="bazi-time-{index}-label" for="bazi-time-{index}" class={LABEL}>{copy.form.birthTimeLabel}</label>
                <BirthTimeField
                  id="bazi-time-{index}"
                  labelledby="bazi-time-{index}-label"
                  bind:value={partner.birth_time}
                  labels={copy.form.birthTimeParts}
                />
                <p class="text-[13px] leading-5 text-muted-foreground">{copy.form.timeBlank}</p>
              </div>
              <div class="grid content-start gap-1.5">
                <span id="bazi-zone-{index}" class={LABEL}>{copy.form.zoneLabel}</span>
                <div
                  role="group"
                  aria-labelledby="bazi-zone-{index}"
                  class="grid grid-cols-3 gap-1 rounded-xl border border-input bg-background p-1"
                >
                  {#each ZONES as zone (zone)}
                    <button
                      type="button"
                      aria-pressed={partner.zone === zone}
                      onclick={() => (partner.zone = zone)}
                      class="h-11 rounded-lg text-sm font-semibold transition focus-visible:ring-3 focus-visible:ring-ring/40 focus-visible:outline-none {partner.zone ===
                      zone
                        ? 'bg-brand-ink text-white'
                        : 'text-foreground/70 hover:bg-brand-warm'}"
                    >
                      {zone}
                    </button>
                  {/each}
                </div>
                <p class="text-[13px] leading-5 text-muted-foreground">{copy.form.zones[partner.zone]}</p>
              </div>
            </div>
          </fieldset>
        {/each}
      </div>

      <p class="-mt-3 text-[13px] leading-5 text-muted-foreground">{copy.form.timeHint}</p>

      <div class="border-t border-border pt-7">
        <div class="flex flex-wrap items-baseline gap-x-3 gap-y-1">
          <h2 class="font-display text-xl font-semibold md:text-[22px]">{copy.dates.formTitle}</h2>
          <span class="text-sm text-muted-foreground">{copy.dates.formHint}</span>
        </div>
        <p class="mt-1.5 max-w-2xl text-[15px] leading-6 text-foreground/75">{copy.dates.formLead}</p>
        <div class="mt-4 grid gap-4 sm:grid-cols-3">
          {#each dates as _, index (index)}
            <div class="grid gap-1.5">
              <label for="bazi-check-{index}" class={LABEL}>{copy.dates.label(index)}</label>
              <DateField
                id="bazi-check-{index}"
                bind:value={dates[index]}
                {locale}
                placeholder={copy.form.datePlaceholder}
                class="h-12 w-full text-base"
              />
            </div>
          {/each}
        </div>
      </div>

      <div class="flex flex-col gap-x-6 gap-y-4 sm:flex-row sm:items-center">
        <Button type="submit" variant="gold" size="lg" class="h-14 w-full shrink-0 px-10 text-base sm:w-auto" disabled={loading}>
          <SparklesIcon size={18} aria-hidden="true" />
          {loading ? copy.form.calculating : copy.form.calculate}
        </Button>
        {#if error}
          <p class="text-sm leading-6 text-destructive" role="alert">{error}</p>
        {:else if stale}
          <p class="text-sm leading-6 text-muted-foreground" role="status">{copy.form.stale}</p>
        {:else if mounted && !unlocked}
          <p class="max-w-xl text-sm leading-6 text-foreground/75">{copy.form.gateHint}</p>
        {/if}
      </div>
    </form>
  {/snippet}

  {#snippet result()}
    <section
      id="bazi-result"
      class="scroll-mt-16 bg-brand-warm px-5 py-12 md:py-16 lg:px-8"
      aria-live="polite"
      aria-busy={loading}
    >
      <div class="mx-auto max-w-7xl">
        <p class={EYEBROW}>{copy.result.eyebrow}</p>
        <h2 class="mt-2.5 font-display text-[clamp(1.6rem,3vw,2.25rem)] leading-tight font-bold">{copy.result.title}</h2>

        <div class="relative mt-8 {locked ? 'min-h-[47.5rem]' : ''}">
          <div
            class={locked
              ? 'pointer-events-none max-h-[47.5rem] overflow-hidden blur-[9px] select-none'
              : stale
                ? 'opacity-60 transition-opacity'
                : ''}
            aria-hidden={locked ? 'true' : undefined}
            inert={locked}
          >
            {@render resultBody(view.result, view.names, !locked && copySent)}
          </div>

          {#if locked}
            <div
              aria-hidden="true"
              class="pointer-events-none absolute inset-x-0 bottom-0 h-48 bg-gradient-to-b from-brand-warm/0 to-brand-warm"
            ></div>
            <div class="absolute inset-x-0 top-4 flex justify-center {awaitingGate ? '' : 'md:top-24'}">
              {#if awaitingGate}
                <LeadGate
                  inline
                  tool="bazi"
                  title={copy.gate.title}
                  description={copy.gate.description}
                  submitLabel={copy.gate.submit}
                  names={leadNames}
                  inputs={baziLeadInputs(awaitingGate.result)}
                  extra={{ calculation: awaitingGate.calculation }}
                  sourcePath={TOOL_PATH}
                  {onUnlocked}
                />
              {:else}
                <div
                  class="w-full max-w-md rounded-2xl border border-brand-warm-deep bg-background p-6 text-center shadow-[0_30px_70px_-30px_rgba(138,101,36,0.55)] sm:p-8"
                >
                  <span
                    aria-hidden="true"
                    class="mx-auto flex size-13 items-center justify-center rounded-full bg-brand-gold-soft text-brand-gold-hover"
                  >
                    <LockIcon size={22} />
                  </span>
                  <h3 class="mt-4 font-display text-xl leading-snug font-bold">{copy.result.previewTitle}</h3>
                  <p class="mt-2.5 text-[15px] leading-6 text-foreground/75">{copy.result.previewCopy}</p>
                  <a
                    href="#bazi-form"
                    class="mt-5 inline-flex min-h-12 items-center justify-center rounded-xl bg-brand-ink px-7 font-display text-[15px] font-semibold text-white transition hover:bg-brand-ink/85 focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none"
                  >
                    {copy.result.previewCta}
                  </a>
                </div>
              {/if}
            </div>
          {/if}
        </div>
      </div>
    </section>

    {#if bazi}
      <section class="px-5 py-12 md:py-16 lg:px-8">
        <div class="mx-auto grid max-w-7xl gap-10 lg:grid-cols-2 {stale ? 'opacity-60 transition-opacity' : ''}">
          <div class="min-w-0">
            <h2 class="flex items-center gap-2.5 font-display text-2xl font-bold">
              <CalendarCheckIcon size={22} class="text-brand-gold" aria-hidden="true" />
              {copy.dates.title}
            </h2>
            <p class="mt-2 text-[15px] leading-6 text-foreground/75">{copy.dates.lead}</p>

            {#if bazi.date_checks.length}
              <ul class="mt-5 grid gap-3.5">
                {#each bazi.date_checks as check, index (index)}
                  {@const day = { char: `${check.pillar.stem.char}${check.pillar.branch.char}`, animal: check.pillar.branch.animal_label }}
                  <li class="rounded-2xl border border-border p-5">
                    <div class="flex flex-wrap items-center justify-between gap-2.5">
                      <p class="text-[17px] font-semibold">{formatMasehi(check.date, locale)}</p>
                      <span class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[13px] font-semibold ring-1 {VERDICT_STYLE[check.verdict]}">
                        {#if check.verdict === 'safe'}
                          <CheckIcon size={14} strokeWidth={3} aria-hidden="true" />
                        {:else if check.verdict === 'clash'}
                          <XIcon size={14} strokeWidth={3} aria-hidden="true" />
                        {:else}
                          <CircleAlertIcon size={14} strokeWidth={2.5} aria-hidden="true" />
                        {/if}
                        {copy.dates.verdicts[check.verdict]}
                      </span>
                    </div>
                    <p class="mt-1 text-sm text-muted-foreground">
                      <span lang="zh" style={HAN}>{day.char}</span> · {day.animal}
                    </p>
                    <ul class="mt-2.5 grid gap-1 text-[15px] leading-6 text-foreground/80">
                      {#each check.reasons as reason, index (index)}
                        <li>{dateReason(locale, reason, day, bazi.charts, names)}</li>
                      {:else}
                        <li>{copy.dates.quiet}</li>
                      {/each}
                    </ul>
                  </li>
                {/each}
              </ul>
            {:else}
              <p class="mt-5 rounded-2xl border border-dashed border-border p-5 text-[15px] leading-6 text-foreground/75">
                {copy.dates.none}
              </p>
            {/if}
            <a
              href="#bazi-form"
              class="mt-3 inline-flex min-h-11 items-center rounded-sm text-[15px] font-medium text-brand-gold-hover underline-offset-4 hover:underline focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
            >
              {copy.dates.another}
            </a>
          </div>

          <div class="min-w-0">
            <h2 class="font-display text-2xl font-bold">{copy.card.title}</h2>
            <p class="mt-2 text-[15px] leading-6 text-foreground/75">{copy.card.lead}</p>

            <div class="mx-auto mt-5 max-w-sm overflow-hidden rounded-2xl bg-brand-warm ring-1 ring-brand-gold/25 lg:mx-0">
              <BaziCard
                charts={cardCharts}
                tone={bazi.tone_label}
                dates={cardDates}
                copy={copy.card}
                label={cardLabel}
                class="block h-auto w-full"
              />
            </div>

            {#if copySent}
              <p class="mt-4 flex gap-2.5 rounded-xl border border-brand-gold/40 bg-brand-gold-soft px-4 py-3.5 text-[15px] leading-6 text-foreground/85">
                <MailCheckIcon size={18} class="mt-0.5 shrink-0 text-brand-gold-hover" aria-hidden="true" />
                {copy.card.emailed}
              </p>
            {:else}
              <p class="mt-4 text-[15px] leading-6 text-foreground/75">{copy.card.sendHint}</p>
              <Button variant="gold" size="lg" class="mt-3 h-12 w-full px-7 sm:w-auto" onclick={() => (sendOpen = true)}>
                <SendIcon size={17} aria-hidden="true" />
                {copy.card.send}
              </Button>
            {/if}
          </div>
        </div>
      </section>
    {/if}
  {/snippet}

  {#snippet gate()}
    <!-- The same gate a second time, as a dialog: for a result that was shown
         without it, in a browser another tool had already unlocked. -->
    <LeadGate
      bind:open={sendOpen}
      tool="bazi"
      title={copy.gate.sendTitle}
      description={copy.gate.sendDescription}
      submitLabel={copy.gate.sendSubmit}
      names={leadNames}
      inputs={bazi ? baziLeadInputs(bazi) : {}}
      extra={{ calculation: shown?.calculation }}
      sourcePath={TOOL_PATH}
      onUnlocked={() => (copySent = true)}
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
  {/snippet}
</ToolShell>
