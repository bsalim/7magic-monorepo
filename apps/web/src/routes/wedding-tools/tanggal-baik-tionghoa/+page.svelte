<script lang="ts">
  import { onMount } from 'svelte';
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import CalendarSearchIcon from '@lucide/svelte/icons/calendar-search';
  import CheckIcon from '@lucide/svelte/icons/check';
  import ChevronLeftIcon from '@lucide/svelte/icons/chevron-left';
  import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
  import InfoIcon from '@lucide/svelte/icons/info';
  import LockIcon from '@lucide/svelte/icons/lock';
  import XIcon from '@lucide/svelte/icons/x';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import LeadGate from '$lib/components/tools/LeadGate.svelte';
  import ToolShell from '$lib/components/tools/ToolShell.svelte';
  import { Button } from '$lib/components/ui/button';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import { canonicalUrl, toolPageJsonLd } from '$lib/seo/schema';
  import {
    ANIMALS,
    almanacLeadInputs,
    fetchAlmanac,
    monthWeeks,
    shiftMonth,
    shioYears,
    type AlmanacDayOut,
    type AlmanacRequest,
    type AlmanacResponse,
    type Animal,
    type Rating
  } from '$lib/tools/almanac';
  import { storedEmail } from '$lib/tools/lead';
  import { formatMasehi } from '$lib/tools/mahar';
  import { BAZI_PATH, TOOL_PATH, almanacCopy, shioReason } from './content';

  /**
   * Tanggal Baik Tionghoa: a month and the couple's two shio in, the month as
   * the Chinese almanac reads it out, each day marked commonly chosen, ordinary
   * or avoided.
   *
   * Built like the Ba Zi page it sits beside: the API owns the reading
   * (`app/domains/almanac`, on Ba Zi's pillars and solar terms), the page posts
   * to it through the `/api/almanac` proxy on a button press, and the result
   * sits behind the lead gate until this browser has given an email. The
   * calculation is run first and waits blurred in `pending` while the gate sits
   * over it. With an email on file the month shows at once.
   */

  const locale = $derived(getLocale());
  const copy = $derived(almanacCopy(locale));
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

  type Calculated = { result: AlmanacResponse; key: string };

  const today = new Date();
  const THIS_YEAR = today.getFullYear();
  // Far enough ahead for any engagement; the API itself reads up to 2100.
  const YEARS = Array.from({ length: 6 }, (_, index) => THIS_YEAR + index);

  let year = $state(THIS_YEAR);
  let month = $state(today.getMonth() + 1);
  let shio = $state<[Animal | '', Animal | '']>(['', '']);

  let shown = $state<Calculated | null>(null);
  let pending = $state<Calculated | null>(null);
  let loading = $state(false);
  let error = $state('');
  // The day whose reading is open; null leaves it to the first good day.
  let picked = $state<string | null>(null);

  let unlocked = $state(false);
  // Known only in the browser: until then the page cannot say whether this
  // visitor will meet the gate, so it does not warn them of one.
  let mounted = $state(false);

  onMount(() => {
    unlocked = storedEmail() !== null;
    mounted = true;
  });

  const dateLocale = $derived(locale === 'en' ? 'en-GB' : 'id-ID');
  const monthNames = $derived(
    Array.from({ length: 12 }, (_, index) =>
      new Intl.DateTimeFormat(dateLocale, { month: 'long', timeZone: 'UTC' }).format(new Date(Date.UTC(2024, index, 1)))
    )
  );
  // 1 January 2024 was a Monday, so these run Monday to Sunday.
  const weekdays = $derived(
    Array.from({ length: 7 }, (_, index) =>
      new Intl.DateTimeFormat(dateLocale, { weekday: 'short', timeZone: 'UTC' }).format(new Date(Date.UTC(2024, 0, index + 1)))
    )
  );

  const request = $derived<AlmanacRequest>({
    year,
    month,
    shio: shio.filter((animal): animal is Animal => animal !== ''),
    locale: locale === 'en' ? 'en' : 'id'
  });
  const inputKey = $derived(JSON.stringify(request));

  const stale = $derived(shown !== null && shown.key !== inputKey);
  // A pending month is only offered while it still matches the form.
  const awaitingGate = $derived(pending !== null && pending.key === inputKey ? pending : null);
  const locked = $derived(shown === null);
  const view = $derived(shown?.result ?? awaitingGate?.result ?? null);

  const weeks = $derived(view ? monthWeeks(view.days) : []);
  const goodDays = $derived(view ? view.days.filter((day) => day.rating === 'good') : []);
  const avoidCount = $derived(view ? view.days.filter((day) => day.rating === 'avoid').length : 0);
  const selected = $derived(
    view ? (view.days.find((day) => day.date === picked) ?? goodDays[0] ?? view.days[0] ?? null) : null
  );
  const viewTitle = $derived(view ? `${monthNames[view.month - 1]} ${view.year}` : copy.result.title);

  const RATING_CELL: Record<Rating, string> = {
    good: 'bg-emerald-50 text-emerald-950 ring-emerald-300 hover:ring-emerald-500',
    ordinary: 'bg-background text-foreground ring-border hover:ring-foreground/40',
    avoid: 'bg-rose-50 text-rose-950 ring-rose-200 hover:ring-rose-400'
  };
  const RATING_SWATCH: Record<Rating, string> = {
    good: 'bg-emerald-50 text-emerald-950 ring-emerald-300',
    ordinary: 'bg-background text-foreground ring-border',
    avoid: 'bg-rose-50 text-rose-950 ring-rose-200'
  };
  const RATING_BADGE: Record<Rating, string> = {
    good: 'bg-emerald-50 text-emerald-900 ring-emerald-300',
    ordinary: 'bg-secondary text-foreground/80 ring-border',
    avoid: 'bg-rose-800 text-white ring-rose-800'
  };
  // The page loads no Chinese webfont; this is the same stack the Ba Zi page uses.
  const HAN = "font-family: 'Noto Serif SC', 'Songti SC', 'STSong', 'SimSun', serif";

  function scrollTo(id: string) {
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    document.getElementById(id)?.scrollIntoView?.({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  }

  async function calculate({ scroll = true } = {}) {
    error = '';
    if (request.shio.length < 2) {
      error = copy.form.missing;
      return;
    }
    loading = true;
    const key = inputKey;
    try {
      const result = await fetchAlmanac(request);
      picked = null;
      if (unlocked) shown = { result, key };
      else pending = { result, key };
      // The calendar is a band below the form, out of sight on a phone.
      if (scroll) scrollTo('tionghoa-result');
    } catch {
      // Whatever was picked stays in the form; only the message changes.
      error = copy.form.unavailable;
    } finally {
      loading = false;
    }
  }

  function onUnlocked() {
    unlocked = true;
    const ready = awaitingGate;
    pending = null;
    if (ready) shown = ready;
  }

  /** Step the calendar a month, from the arrows over the grid. */
  function step(by: number) {
    // From the month on show, which the form may have moved away from.
    const next = shiftMonth(view?.year ?? year, view?.month ?? month, by);
    if (!YEARS.includes(next.year)) return;
    year = next.year;
    month = next.month;
    void calculate({ scroll: false });
  }

  function pick(day: AlmanacDayOut, scroll = false) {
    picked = day.date;
    if (scroll) scrollTo('tionghoa-day');
  }

  const FIELD =
    'h-12 w-full rounded-lg border border-input bg-background px-3.5 text-base focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none disabled:opacity-50';
  const LABEL = 'text-[13px] font-medium text-foreground/75';
  const EYEBROW = 'text-xs font-semibold tracking-[0.2em] text-brand-gold-hover uppercase';
</script>

<svelte:head>
  <title>{copy.meta.title}</title>
  <meta name="description" content={copy.meta.description} />
  <meta name="keywords" content={copy.meta.keywords} />
  <link rel="canonical" href={canonical} />
  {@html jsonLd}
</svelte:head>

<SocialMeta title={copy.meta.title} description={copy.meta.description} url={canonical} />

{#snippet ratingMark(rating: Rating, size: number)}
  <!-- A different mark per rating as well as a different colour. -->
  {#if rating === 'good'}
    <CheckIcon {size} strokeWidth={3} aria-hidden="true" />
  {:else if rating === 'avoid'}
    <XIcon {size} strokeWidth={3} aria-hidden="true" />
  {:else}
    <span aria-hidden="true" class="block rounded-full bg-foreground/30" style="width: {size / 2}px; height: {size / 2}px"></span>
  {/if}
{/snippet}

{#snippet calendar(result: AlmanacResponse, interactive: boolean)}
  <div class="rounded-2xl border border-brand-warm-deep bg-background p-3 sm:p-5">
    <div class="flex items-center justify-between gap-2">
      <Button
        variant="outline"
        size="icon"
        class="size-11 shrink-0"
        aria-label={copy.result.previous}
        disabled={!interactive || loading || !YEARS.includes(shiftMonth(result.year, result.month, -1).year)}
        onclick={() => step(-1)}
      >
        <ChevronLeftIcon size={18} aria-hidden="true" />
      </Button>
      <p class="font-display text-lg font-semibold sm:text-xl" aria-live="polite">
        {monthNames[result.month - 1]}
        {result.year}
      </p>
      <Button
        variant="outline"
        size="icon"
        class="size-11 shrink-0"
        aria-label={copy.result.next}
        disabled={!interactive || loading || !YEARS.includes(shiftMonth(result.year, result.month, 1).year)}
        onclick={() => step(1)}
      >
        <ChevronRightIcon size={18} aria-hidden="true" />
      </Button>
    </div>

    <div class="mt-4 grid grid-cols-7 gap-1 sm:gap-2" aria-hidden="true">
      {#each weekdays as weekday (weekday)}
        <p class="text-center text-[11px] font-semibold tracking-wide text-muted-foreground uppercase sm:text-xs">
          {weekday}
        </p>
      {/each}
    </div>
    <div class="mt-1.5 grid gap-1 sm:gap-2">
      {#each weeks as week, index (index)}
        <div class="grid grid-cols-7 gap-1 sm:gap-2">
          {#each week as day, slot (slot)}
            {#if day}
              <button
                type="button"
                onclick={() => pick(day)}
                aria-pressed={selected?.date === day.date}
                aria-label={copy.result.cellLabel(formatMasehi(day.date, locale), copy.result.ratings[day.rating])}
                class="flex min-h-14 flex-col items-center justify-between rounded-lg px-0.5 py-1.5 ring-1 transition focus-visible:ring-3 focus-visible:ring-ring/60 focus-visible:outline-none aria-pressed:ring-2 aria-pressed:ring-brand-ink sm:min-h-[4.75rem] sm:rounded-xl sm:py-2 {RATING_CELL[
                  day.rating
                ]}"
              >
                <span class="font-display text-[15px] leading-none font-semibold sm:text-lg">{Number(day.date.slice(8))}</span>
                <span lang="zh" style={HAN} class="text-xs leading-none opacity-70 sm:text-sm">{day.officer.char}</span>
                <span class="flex h-3.5 items-center">{@render ratingMark(day.rating, 13)}</span>
              </button>
            {:else}
              <span aria-hidden="true"></span>
            {/if}
          {/each}
        </div>
      {/each}
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-border pt-3.5 text-[13px] text-foreground/80">
      <span class="sr-only">{copy.result.legendTitle}</span>
      {#each ['good', 'ordinary', 'avoid'] as const as rating (rating)}
        <span class="inline-flex items-center gap-1.5">
          <span class="flex size-5 items-center justify-center rounded-md ring-1 {RATING_SWATCH[rating]}">
            {@render ratingMark(rating, 11)}
          </span>
          {copy.result.ratings[rating]}
        </span>
      {/each}
    </div>
  </div>
{/snippet}

{#snippet dayDetail(result: AlmanacResponse, day: AlmanacDayOut)}
  <article
    id="tionghoa-day"
    class="scroll-mt-20 rounded-2xl border border-brand-warm-deep bg-background p-5 sm:p-6"
    aria-live="polite"
  >
    <div class="flex flex-wrap items-start justify-between gap-3">
      <h3 class="font-display text-xl leading-snug font-semibold">{formatMasehi(day.date, locale)}</h3>
      <span
        class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[13px] font-semibold ring-1 {RATING_BADGE[
          day.rating
        ]}"
      >
        {@render ratingMark(day.rating, 14)}
        {copy.result.ratings[day.rating]}
      </span>
    </div>

    <dl class="mt-4 grid grid-cols-3 gap-2 text-center">
      <div class="rounded-xl bg-brand-warm px-2 py-3">
        <dt class="text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">{copy.result.dayPillar}</dt>
        <dd class="mt-1.5">
          <span lang="zh" style={HAN} class="block text-2xl leading-none">{day.pillar.stem.char}{day.pillar.branch.char}</span>
          <span class="mt-1.5 block text-[13px] text-foreground/75">{day.pillar.branch.animal_label}</span>
        </dd>
      </div>
      <div class="rounded-xl bg-brand-warm px-2 py-3">
        <dt class="text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">{copy.result.officer}</dt>
        <dd class="mt-1.5">
          <span lang="zh" style={HAN} class="block text-2xl leading-none">{day.officer.char}</span>
          <span class="mt-1.5 block text-[13px] text-foreground/75">{day.officer.pinyin} · {day.officer.label}</span>
        </dd>
      </div>
      <div class="rounded-xl bg-brand-warm px-2 py-3">
        <dt class="text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">{copy.result.clash}</dt>
        <dd class="mt-1.5">
          <span lang="zh" style={HAN} class="block text-2xl leading-none">{day.clashes.char}</span>
          <span class="mt-1.5 block text-[13px] text-foreground/75">{day.clashes.animal_label}</span>
        </dd>
      </div>
    </dl>

    <p class="mt-4 text-[15px] leading-6 text-foreground/85">{copy.result.officerNotes[day.officer.rating](day.officer)}</p>
    <p class="mt-2 text-[15px] leading-6 text-foreground/85">{copy.result.clashNote(day.clashes.animal_label)}</p>

    <h4 class="mt-5 text-xs font-semibold tracking-[0.16em] text-brand-gold-hover uppercase">{copy.result.shioTitle}</h4>
    <ul class="mt-2 grid gap-1.5 text-[15px] leading-6 text-foreground/85">
      {#each day.reasons as reason, index (index)}
        <li>
          <span class="font-medium text-foreground">{copy.result.partners[reason.partner]}:</span>
          {shioReason(locale, reason, day.pillar.branch.animal_label, result.shio[reason.partner].animal_label)}
        </li>
      {:else}
        <li>{copy.result.shioQuiet}</li>
      {/each}
    </ul>
  </article>
{/snippet}

<ToolShell
  stacked
  watermark="吉日"
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
      id="tionghoa-form"
      class="grid scroll-mt-24 gap-6"
      onsubmit={(event) => {
        event.preventDefault();
        void calculate();
      }}
    >
      <h2 class="font-display text-xl font-semibold md:text-[22px]">{copy.form.title}</h2>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div class="grid content-start gap-1.5">
          <label for="tionghoa-month" class={LABEL}>{copy.form.monthLabel}</label>
          <select id="tionghoa-month" bind:value={month} class={FIELD}>
            {#each monthNames as name, index (index)}
              <option value={index + 1}>{name}</option>
            {/each}
          </select>
        </div>
        <div class="grid content-start gap-1.5">
          <label for="tionghoa-year" class={LABEL}>{copy.form.yearLabel}</label>
          <select id="tionghoa-year" bind:value={year} class={FIELD}>
            {#each YEARS as option (option)}
              <option value={option}>{option}</option>
            {/each}
          </select>
        </div>
        {#each copy.form.shioLabels as label, index (index)}
          <div class="grid content-start gap-1.5">
            <label for="tionghoa-shio-{index}" class={LABEL}>{label}</label>
            <select id="tionghoa-shio-{index}" bind:value={shio[index]} class={FIELD}>
              <option value="">{copy.form.shioPlaceholder}</option>
              {#each ANIMALS as animal (animal)}
                <option value={animal}>{copy.animals[animal]} ({shioYears(animal).join(', ')})</option>
              {/each}
            </select>
          </div>
        {/each}
      </div>
      <p class="-mt-2 text-sm leading-6 text-muted-foreground">{copy.form.shioHint}</p>

      <div class="flex flex-col gap-x-6 gap-y-4 sm:flex-row sm:items-center">
        <Button type="submit" variant="gold" size="lg" class="h-14 w-full shrink-0 px-10 text-base sm:w-auto" disabled={loading}>
          <CalendarSearchIcon size={18} aria-hidden="true" />
          {loading ? copy.form.loading : copy.form.submit}
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
    <section id="tionghoa-result" class="scroll-mt-16 bg-brand-warm px-5 py-12 md:py-16 lg:px-8" aria-busy={loading}>
      <div class="mx-auto max-w-7xl">
        <p class={EYEBROW}>{copy.result.eyebrow}</p>
        <h2 class="mt-2.5 font-display text-[clamp(1.6rem,3vw,2.25rem)] leading-tight font-bold">
          {locked ? copy.result.title : viewTitle}
        </h2>
        {#if !locked}
          <p class="mt-2 text-[15px] leading-6 text-foreground/80" role="status">
            {copy.result.summary(goodDays.length, avoidCount)}
          </p>
        {/if}

        {#if view}
          <div class="relative mt-8 {locked ? 'min-h-[40rem]' : ''}">
            <div
              class={locked
                ? 'pointer-events-none max-h-[40rem] overflow-hidden blur-[9px] select-none'
                : stale
                  ? 'opacity-60 transition-opacity'
                  : ''}
              aria-hidden={locked ? 'true' : undefined}
              inert={locked}
            >
              <div class="grid gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)] lg:items-start">
                {@render calendar(view, !locked)}
                {#if selected}
                  {@render dayDetail(view, selected)}
                {/if}
              </div>

              <h3 class="mt-10 font-display text-xl font-semibold">{copy.result.goodTitle}</h3>
              {#if goodDays.length}
                <p class="mt-2 max-w-2xl text-[15px] leading-6 text-foreground/75">{copy.result.goodLead}</p>
                <ul class="mt-4 flex flex-wrap gap-2.5">
                  {#each goodDays as day (day.date)}
                    <li>
                      <button
                        type="button"
                        onclick={() => pick(day, true)}
                        aria-pressed={selected?.date === day.date}
                        class="inline-flex min-h-11 items-center gap-2 rounded-full bg-background px-4 text-[15px] font-medium text-emerald-950 ring-1 ring-emerald-300 transition hover:ring-emerald-500 focus-visible:ring-3 focus-visible:ring-ring/60 focus-visible:outline-none aria-pressed:ring-2 aria-pressed:ring-brand-ink"
                      >
                        <CheckIcon size={15} strokeWidth={3} class="text-emerald-700" aria-hidden="true" />
                        {formatMasehi(day.date, locale)}
                      </button>
                    </li>
                  {/each}
                </ul>
              {:else}
                <p class="mt-3 max-w-2xl rounded-2xl border border-dashed border-brand-gold/40 bg-background p-5 text-[15px] leading-6 text-foreground/80">
                  {copy.result.goodNone}
                </p>
              {/if}

              <p
                class="mt-8 flex gap-3.5 rounded-2xl border border-brand-gold/40 border-l-4 border-l-brand-gold bg-background p-5 font-display text-[17px] leading-7 font-semibold text-foreground sm:p-6 md:text-xl md:leading-8"
              >
                <InfoIcon size={24} class="mt-0.5 shrink-0 text-brand-gold-hover md:mt-1" aria-hidden="true" />
                {copy.result.elderNote}
              </p>

              <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <p class="text-[15px] leading-6 text-foreground/80">{copy.result.baziLead}</p>
                <a
                  href={localizeHref(BAZI_PATH)}
                  class="inline-flex min-h-11 shrink-0 items-center gap-2 rounded-sm text-[15px] font-semibold text-brand-gold-hover underline-offset-4 hover:underline focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
                >
                  {copy.result.baziCta}
                  <ArrowRightIcon size={16} aria-hidden="true" />
                </a>
              </div>
            </div>

            {#if awaitingGate && locked}
              <div
                aria-hidden="true"
                class="pointer-events-none absolute inset-x-0 bottom-0 h-48 bg-gradient-to-b from-brand-warm/0 to-brand-warm"
              ></div>
              <div class="absolute inset-x-0 top-4 flex justify-center">
                <LeadGate
                  inline
                  tool="tionghoa"
                  title={copy.gate.title}
                  description={copy.gate.description}
                  submitLabel={copy.gate.submit}
                  inputs={almanacLeadInputs(awaitingGate.result)}
                  note={copy.gate.note}
                  phoneOptional
                  sourcePath={TOOL_PATH}
                  {onUnlocked}
                />
              </div>
            {/if}
          </div>
        {:else}
          <div class="mt-8 flex justify-center rounded-2xl border border-dashed border-brand-gold/40 px-5 py-12">
            <div class="w-full max-w-md text-center">
              <span
                aria-hidden="true"
                class="mx-auto flex size-13 items-center justify-center rounded-full bg-background text-brand-gold-hover ring-1 ring-brand-gold/30"
              >
                <LockIcon size={22} />
              </span>
              <h3 class="mt-4 font-display text-xl leading-snug font-bold">{copy.result.previewTitle}</h3>
              <p class="mt-2.5 text-[15px] leading-6 text-foreground/75">{copy.result.previewCopy}</p>
              <a
                href="#tionghoa-form"
                class="mt-5 inline-flex min-h-12 items-center justify-center rounded-xl bg-brand-ink px-7 font-display text-[15px] font-semibold text-white transition hover:bg-brand-ink/85 focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none"
              >
                {copy.result.previewCta}
              </a>
            </div>
          </div>
        {/if}
      </div>
    </section>
  {/snippet}

  {#snippet explainer()}
    <section class="border-b border-border bg-brand-warm/60 px-5 py-16 lg:px-8">
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
            <h3 class="font-display text-base font-semibold">{copy.explainer.conventionsTitle}</h3>
            <ul class="mt-2 grid list-disc gap-1.5 pl-5 text-sm leading-6 text-foreground/80">
              {#each copy.explainer.conventions as line, index (index)}
                <li>{line}</li>
              {/each}
            </ul>
          </div>
        </div>
      </div>
    </section>
  {/snippet}
</ToolShell>
