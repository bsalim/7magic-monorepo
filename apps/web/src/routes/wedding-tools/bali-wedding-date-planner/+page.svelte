<script lang="ts">
  import CalendarIcon from '@lucide/svelte/icons/calendar';
  import InfoIcon from '@lucide/svelte/icons/info';
  import BaliEnquiry from '$lib/components/bali/BaliEnquiry.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import ToolShell from '$lib/components/tools/ToolShell.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import { englishPath, siteHref } from '$lib/seo/english-only';
  import { canonicalUrl, toolPageJsonLd } from '$lib/seo/schema';
  import { defaultInput, monthOptions } from '$lib/tools/bali-cost';
  import {
    ANNOUNCED,
    BALI_EVENTS,
    DATES_CHECKED,
    LAST_MONTH,
    eventsOn,
    monthFlags,
    type BaliEvent,
    type Source
  } from '$lib/tools/bali-dates';
  import { formatDateRange, monthLabel } from '$lib/tools/bali-format';
  import { EXTRA_SOURCES, TOOL_PATH, appName, bestMonths, faqs, hero, meta } from './content';

  /**
   * The Bali wedding date planner: a month (and optionally a day) in, what
   * falls on it out. All the dates and their sources live in
   * `$lib/tools/bali-dates`; this page lays them out, and server-renders the
   * full 2027 table below the tool, which is the part worth citing.
   */

  const path = englishPath(TOOL_PATH);
  const canonical = canonicalUrl(path);
  const crumbs = [
    { name: m.breadcrumb_home(), path: '/' },
    { name: m.nav_wedding_tools(), path: '/wedding-tools' },
    { name: appName }
  ];
  const jsonLd = toolPageJsonLd({
    path,
    title: meta.title,
    name: appName,
    description: meta.description,
    locale: 'en',
    crumbs,
    faqs
  });

  const today = new Date();
  const months = monthOptions(today);
  const start = defaultInput(today);

  let monthKey = $state(`${start.year}-${start.month}`);
  let day = $state('');

  const pad = (n: number) => String(n).padStart(2, '0');
  const selected = $derived(monthKey.split('-').map(Number) as [number, number]);
  const flags = $derived(monthFlags(selected[0], selected[1]));
  const minDay = `${months[0].year}-${pad(months[0].month)}-01`;
  const maxDay = `${LAST_MONTH.year}-${pad(LAST_MONTH.month)}-31`;

  // Picking a day moves the month view to it, so the two never disagree.
  function pickDay(value: string) {
    day = value;
    if (!value) return;
    const [year, month] = value.split('-').map(Number);
    monthKey = `${year}-${month}`;
  }

  const dayEvents = $derived(day ? eventsOn(day) : []);
  const dayYear = $derived(day ? Number(day.slice(0, 4)) : 0);

  function verdict(event: BaliEvent): string {
    switch (event.kind) {
      case 'nyepi':
        return 'Nyepi: no wedding can take place, and the airport is closed.';
      case 'galungan':
      case 'kuningan':
        return `${event.name}: a Balinese holy day. Possible, but local staff and vendors are stretched.`;
      case 'id-holiday':
        return `${event.name}: an Indonesian public holiday. Expect busier flights and roads.`;
      case 'au-school':
        return `${event.name}: easier for guests with children, but flights cost more.`;
    }
  }

  const SEASON_TEXT = {
    wet: 'Wet season. Afternoon storms are likely, so plan a covered option.',
    dry: 'Dry season. The most reliable weather, and the busiest months.',
    shoulder: 'Between seasons. Often dry, but sources disagree on where the wet season starts or ends.'
  };

  const KIND_LABEL: Record<BaliEvent['kind'], string> = {
    nyepi: 'Balinese',
    galungan: 'Balinese',
    kuningan: 'Balinese',
    'id-holiday': 'Indonesia',
    'au-school': 'School holidays'
  };

  const table2027 = BALI_EVENTS.filter(
    (event) => event.kind !== 'au-school' && event.start.startsWith('2027')
  );
  const schoolTable = BALI_EVENTS.filter(
    (event) => event.kind === 'au-school' && event.end >= '2027-01-01' && event.start <= '2027-12-31'
  );

  const sources = $derived.by(() => {
    const all = new Map<string, Source>();
    for (const event of BALI_EVENTS) all.set(event.source.url, event.source);
    for (const source of EXTRA_SOURCES) all.set(source.url, source);
    return [...all.values()];
  });

  const context = $derived([
    `Date planner: ${day ? formatDateRange(day, day) : monthLabel(selected[0], selected[1])}`
  ]);
  const whatsappText = $derived(
    `Hi 7Magic, we're thinking of a Bali wedding on ${day ? formatDateRange(day, day) : `a date in ${monthLabel(selected[0], selected[1])}`}. Could you check it for us?`
  );

  const related = [
    { href: siteHref('/wedding-tools/bali-wedding-cost-calculator'), title: 'Bali wedding cost calculator (AUD)' },
    { href: siteHref('/legally-married-in-bali'), title: 'Is a Bali wedding legal in Australia?' },
    { href: siteHref('/bali-wedding-concierge'), title: 'Bali wedding concierge: guests, transport and more' }
  ];

  const FIELD =
    'h-11 w-full rounded-md border border-input bg-background px-3 text-base focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none md:text-[15px]';
  const LEGEND = 'text-[13px] font-semibold tracking-wide text-foreground';
</script>

<svelte:head>
  <title>{meta.title}</title>
  <meta name="description" content={meta.description} />
  <meta name="keywords" content={meta.keywords} />
  <link rel="canonical" href={canonical} />
  {@html jsonLd}
</svelte:head>

<SocialMeta title={meta.title} description={meta.description} url={path} />

<ToolShell eyebrow={hero.eyebrow} title={hero.title} lead={hero.lead} {crumbs} {faqs} {related}>
  {#snippet inputs()}
    <div class="grid gap-6">
      <div class="grid gap-2">
        <label for="dp-month" class={LEGEND}>Month</label>
        <select id="dp-month" bind:value={monthKey} onchange={() => (day = '')} class={FIELD}>
          {#each months as option (`${option.year}-${option.month}`)}
            <option value={`${option.year}-${option.month}`}>{monthLabel(option.year, option.month)}</option>
          {/each}
        </select>
      </div>
      <div class="grid gap-2">
        <label for="dp-day" class={LEGEND}>
          A date you have in mind <span class="font-normal text-muted-foreground">(optional)</span>
        </label>
        <input
          id="dp-day"
          type="date"
          min={minDay}
          max={maxDay}
          value={day}
          oninput={(event) => pickDay(event.currentTarget.value)}
          class={FIELD}
        />
      </div>
      <p class="text-sm leading-6 text-muted-foreground">
        Dates checked {DATES_CHECKED}. Indonesian holidays are published to {ANNOUNCED.idHolidays};
        Galungan and Kuningan marked "calculated" follow the 210-day Balinese cycle.
      </p>
    </div>
  {/snippet}

  {#snippet result()}
    <div class="grid gap-4">
      {#if day}
        <div class="rounded-2xl bg-brand-ink p-6 text-white" aria-live="polite">
          <p class="text-xs font-semibold tracking-[0.2em] text-brand-dark-accent uppercase">
            {formatDateRange(day, day)}
          </p>
          {#if dayEvents.length}
            <ul class="mt-3 grid gap-2 text-[15px] leading-6">
              {#each dayEvents as event (`${event.kind}-${event.name}-${event.start}`)}
                <li>{verdict(event)}</li>
              {/each}
            </ul>
          {:else if dayYear > ANNOUNCED.idHolidays}
            <p class="mt-3 text-[15px] leading-6">
              {dayYear} Indonesian holidays are not announced yet, so we can't call this date clear.
              Nothing in our data falls on it so far.
            </p>
          {:else}
            <p class="mt-3 text-[15px] leading-6">
              No Balinese holy day, Indonesian public holiday or Australian school holiday in our data
              on this date.
            </p>
          {/if}
          {#if dayYear > ANNOUNCED.idHolidays}
            <p class="mt-3 text-sm text-white/75">
              {dayYear} Indonesian holidays are not announced yet, so check this date with us.
            </p>
          {/if}
        </div>
      {/if}

      <div class="rounded-2xl border border-border bg-background p-5" aria-live="polite">
        <p class="font-display text-lg font-semibold">{monthLabel(selected[0], selected[1])}</p>
        <p class="mt-2 flex gap-2 text-sm leading-6">
          <CalendarIcon size={16} class="mt-1 shrink-0 text-brand-gold-hover" />{SEASON_TEXT[flags.season]}
        </p>
        {#each flags.notices as notice (notice)}
          <p class="mt-2 flex gap-2 text-sm font-medium leading-6">
            <InfoIcon size={16} class="mt-1 shrink-0" />{notice}
          </p>
        {/each}
        {#if flags.events.length}
          <ul class="mt-4 grid gap-3">
            {#each flags.events as event (`${event.kind}-${event.name}-${event.start}`)}
              <li class="border-l-2 border-brand-gold/40 pl-3 text-sm leading-6">
                <p>
                  <span class="text-xs font-semibold tracking-wide text-muted-foreground uppercase">{KIND_LABEL[event.kind]}</span>
                  <span class="font-semibold"> {event.name}</span>
                  {#if event.provisional}<span class="text-muted-foreground"> (calculated)</span>{/if}
                </p>
                <p class="text-muted-foreground">{formatDateRange(event.start, event.end)}</p>
                {#if event.note}<p class="mt-1">{event.note}</p>{/if}
              </li>
            {/each}
          </ul>
        {:else}
          <p class="mt-3 text-sm text-muted-foreground">Nothing in our data falls in this month.</p>
        {/if}
      </div>
    </div>
  {/snippet}

  {#snippet explainer()}
    <section class="px-5 py-16 lg:px-8">
      <div class="mx-auto max-w-5xl">
        <h2 class="font-display text-2xl font-bold md:text-3xl">The best months for a Bali wedding</h2>
        <div class="mt-8 grid gap-6 md:grid-cols-2">
          {#each bestMonths as block (block.title)}
            <div class="border-l-2 border-brand-gold/40 pl-5">
              <h3 class="font-display text-lg font-semibold">{block.title}</h3>
              <p class="mt-2 text-[15px] leading-7 text-foreground/80">{block.body}</p>
            </div>
          {/each}
        </div>

        <h2 class="mt-14 font-display text-2xl font-bold">Bali and Indonesian dates in 2027</h2>
        <div class="mt-4 overflow-x-auto">
          <table class="w-full min-w-[480px] text-sm">
            <thead>
              <tr class="text-left text-muted-foreground">
                <th class="py-2 pr-4 font-medium">Date</th>
                <th class="py-2 pr-4 font-medium">What</th>
                <th class="py-2 font-medium">Source</th>
              </tr>
            </thead>
            <tbody>
              {#each table2027 as event (`${event.kind}-${event.name}-${event.start}`)}
                <tr class="border-t border-border align-top">
                  <td class="py-2 pr-4 whitespace-nowrap">{formatDateRange(event.start, event.end)}</td>
                  <td class="py-2 pr-4">
                    {event.name}{#if event.provisional}<span class="text-muted-foreground"> (calculated)</span>{/if}
                  </td>
                  <td class="py-2">
                    <a href={event.source.url} target="_blank" rel="noopener noreferrer" class="underline underline-offset-2">Source</a>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        <h2 class="mt-14 font-display text-2xl font-bold">Australian school holidays in 2027</h2>
        <div class="mt-4 overflow-x-auto">
          <table class="w-full min-w-[420px] text-sm">
            <tbody>
              {#each schoolTable as event (`${event.state}-${event.start}`)}
                <tr class="border-t border-border">
                  <td class="py-2 pr-4 font-medium">{event.state}</td>
                  <td class="py-2 pr-4">{event.name.replace(`${event.state} `, '')}</td>
                  <td class="py-2 whitespace-nowrap">{formatDateRange(event.start, event.end)}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        <details class="mt-10 rounded-xl border border-border p-5">
          <summary class="cursor-pointer text-sm font-semibold">Sources ({sources.length})</summary>
          <ol class="mt-3 grid list-decimal gap-2 pl-5 text-sm leading-6 text-muted-foreground">
            {#each sources as source (source.url)}
              <li>
                <a href={source.url} target="_blank" rel="noopener noreferrer" class="underline underline-offset-2 hover:text-foreground">{source.title}</a>
              </li>
            {/each}
          </ol>
        </details>
      </div>
    </section>

    <section class="bg-secondary px-5 py-16 lg:px-8">
      <div class="mx-auto max-w-5xl">
        <BaliEnquiry
          sourcePath={TOOL_PATH}
          heading="Want us to check your date?"
          lead="Venue availability, local ceremonies and permits change date by date. Send us yours and our Bali team will check it."
          {context}
          {whatsappText}
          event="Bali Date Check Requested"
        />
      </div>
    </section>
  {/snippet}
</ToolShell>
