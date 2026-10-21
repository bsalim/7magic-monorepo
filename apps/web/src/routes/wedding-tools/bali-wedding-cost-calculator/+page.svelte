<script lang="ts">
  import { onMount } from 'svelte';
  import CalendarIcon from '@lucide/svelte/icons/calendar';
  import InfoIcon from '@lucide/svelte/icons/info';
  import PlaneIcon from '@lucide/svelte/icons/plane';
  import { replaceState } from '$app/navigation';
  import { page } from '$app/state';
  import { trackEvent } from '$lib/analytics';
  import { CONCIERGE_GROUPS } from '$lib/bali-concierge';
  import BaliEnquiry from '$lib/components/bali/BaliEnquiry.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import ToolShell from '$lib/components/tools/ToolShell.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import { englishPath, siteHref } from '$lib/seo/english-only';
  import { canonicalUrl, toolPageJsonLd } from '$lib/seo/schema';
  import {
    CALCULATOR_ADD_ONS,
    COST_SOURCES,
    ESTIMATES_AS_OF,
    METHOD_NOTES,
    SETTINGS,
    STYLES,
    estimateCost,
    fromQuery,
    monthOptions,
    toQuery,
    type City,
    type CostInput
  } from '$lib/tools/bali-cost';
  import { formatAud, formatAudRange, formatDateRange, monthLabel } from '$lib/tools/bali-format';
  import { TOOL_PATH, appName, faqs, hero, meta } from './content';

  /**
   * The Bali wedding cost calculator: guests, setting, month, style and extras
   * in, a market range in Australian dollars out.
   *
   * Everything is free and server-rendered from the URL's inputs, so a shared
   * link opens on the same result. All the arithmetic is in
   * `$lib/tools/bali-cost`; this file wires inputs to it and lays it out.
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
  const initial = fromQuery(page.url.searchParams, today);

  let guests = $state(initial.guests);
  let setting = $state(initial.setting);
  let style = $state(initial.style);
  let monthKey = $state(`${initial.year}-${initial.month}`);
  let addOns = $state([...initial.addOns]);

  const maxGuests = $derived(SETTINGS.find((s) => s.key === setting)!.maxGuests);
  const input = $derived.by((): CostInput => {
    const [year, month] = monthKey.split('-').map(Number);
    return { guests: Math.min(Math.max(guests || 2, 2), maxGuests), setting, style, year, month, addOns };
  });
  const estimate = $derived(estimateCost(input));
  const settingLabel = $derived(SETTINGS.find((s) => s.key === setting)!.label);
  const styleLabel = $derived(STYLES.find((s) => s.key === style)!.label);
  const addOnNames = $derived(
    CALCULATOR_ADD_ONS.filter((service) => addOns.includes(service.key)).map((s) => s.name)
  );

  const summary = $derived(
    [
      `${input.guests} guests`,
      settingLabel,
      monthLabel(input.year, input.month),
      styleLabel,
      ...(addOnNames.length ? [`Add-ons: ${addOnNames.join(', ')}`] : [])
    ].join(' · ')
  );
  const context = $derived([
    `Calculator: ${summary}`,
    `Estimate shown: ${formatAudRange(estimate.total)}`
  ]);
  const whatsappText = $derived(
    `Hi 7Magic, I used your Bali wedding cost calculator: ${summary}. It estimated ${formatAudRange(estimate.total)}. Could you send us a real quote?`
  );

  const SEASON_LABEL = {
    wet: 'Wet season: afternoon storms are likely, so plan cover for an outdoor ceremony.',
    dry: 'Dry season: the most reliable weather and the busiest months.',
    shoulder: 'Between seasons: sources disagree on where the wet season starts or ends.'
  };

  const CITIES: { key: City; label: string }[] = [
    { key: 'sydney', label: 'Sydney' },
    { key: 'melbourne', label: 'Melbourne' },
    { key: 'brisbane', label: 'Brisbane' },
    { key: 'perth', label: 'Perth' }
  ];

  // The URL follows the inputs so the result can be shared, without adding a
  // history entry per slider step. Only after mount: the router is not ready
  // during hydration.
  let mounted = $state(false);
  let used = false;
  onMount(() => {
    mounted = true;
  });
  $effect(() => {
    const query = toQuery(input);
    if (!mounted) return;
    if (query === toQuery(initial)) return;
    replaceState(`?${query}`, {});
    if (!used) {
      used = true;
      trackEvent('Bali Calculator Used');
    }
  });

  const related = [
    { href: siteHref('/bali-wedding-cost'), title: 'How much does a Bali wedding cost? The full guide' },
    { href: siteHref('/legally-married-in-bali'), title: 'Is a Bali wedding legal in Australia?' },
    {
      href: siteHref('/wedding-tools/bali-wedding-date-planner'),
      title: 'Bali wedding date planner: Nyepi, holy days and school holidays'
    }
  ];

  const FIELD =
    'h-11 w-full rounded-md border border-input bg-background px-3 text-base focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none md:text-[15px]';
  const LEGEND = 'text-[13px] font-semibold tracking-wide text-foreground';
  const CHOICE =
    'relative flex cursor-pointer rounded-xl border border-border bg-background px-3.5 py-2.5 text-sm transition hover:border-brand-gold/60 has-checked:border-brand-gold has-checked:bg-brand-gold-soft has-checked:shadow-[0_0_0_1px_var(--brand-gold)] has-focus-visible:ring-3 has-focus-visible:ring-ring/40';
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
    <div class="grid gap-7">
      <div class="grid gap-2">
        <label for="bc-guests" class={LEGEND}>Guests (including you two)</label>
        <div class="flex items-center gap-4">
          <input
            type="range"
            min="2"
            max={maxGuests}
            bind:value={guests}
            aria-label="Guests"
            class="w-full accent-[var(--brand-gold)]"
          />
          <input
            id="bc-guests"
            type="number"
            min="2"
            max={maxGuests}
            bind:value={guests}
            class="{FIELD} w-24 text-center tabular-nums"
          />
        </div>
      </div>

      <fieldset>
        <legend class={LEGEND}>Setting</legend>
        <div class="mt-3 grid gap-2 sm:grid-cols-2">
          {#each SETTINGS as option (option.key)}
            <label class={CHOICE}>
              <input type="radio" name="bc-setting" value={option.key} bind:group={setting} class="sr-only" />
              {option.label}
            </label>
          {/each}
        </div>
      </fieldset>

      <div class="grid gap-2">
        <label for="bc-month" class={LEGEND}>Month</label>
        <select id="bc-month" bind:value={monthKey} class={FIELD}>
          {#each months as option (`${option.year}-${option.month}`)}
            <option value={`${option.year}-${option.month}`}>{monthLabel(option.year, option.month)}</option>
          {/each}
        </select>
        <div class="mt-1 grid gap-1.5 rounded-lg bg-secondary p-3 text-[13px] leading-5">
          <p class="flex gap-2"><CalendarIcon size={15} class="mt-0.5 shrink-0 text-brand-gold-hover" />{SEASON_LABEL[estimate.flags.season]}</p>
          {#each estimate.flags.events as event (`${event.kind}-${event.name}-${event.start}`)}
            <p class="pl-6">
              <span class="font-medium">{event.name}</span>
              <span class="text-muted-foreground">· {formatDateRange(event.start, event.end)}</span>
              {#if event.provisional}<span class="text-muted-foreground"> (calculated)</span>{/if}
            </p>
          {/each}
          {#each estimate.flags.notices as notice (notice)}
            <p class="flex gap-2 font-medium"><InfoIcon size={15} class="mt-0.5 shrink-0" />{notice}</p>
          {/each}
          <a
            href={siteHref('/wedding-tools/bali-wedding-date-planner')}
            class="pl-6 text-brand-gold-hover underline underline-offset-2">Check a date in the planner</a
          >
        </div>
      </div>

      <fieldset>
        <legend class={LEGEND}>Style</legend>
        <div class="mt-3 grid grid-cols-3 gap-2">
          {#each STYLES as option (option.key)}
            <label class="{CHOICE} justify-center">
              <input type="radio" name="bc-style" value={option.key} bind:group={style} class="sr-only" />
              {option.label}
            </label>
          {/each}
        </div>
      </fieldset>

      <fieldset>
        <legend class={LEGEND}>Extras from our concierge</legend>
        <div class="mt-3 grid gap-4">
          {#each CONCIERGE_GROUPS as group (group.key)}
            {@const services = CALCULATOR_ADD_ONS.filter((service) => service.group === group.key)}
            {#if services.length}
              <div>
                <p class="text-xs font-semibold tracking-wide text-muted-foreground uppercase">{group.title}</p>
                <div class="mt-2 grid gap-1.5 sm:grid-cols-2">
                  {#each services as service (service.key)}
                    <label class="flex cursor-pointer items-start gap-2 text-sm">
                      <input type="checkbox" value={service.key} bind:group={addOns} class="mt-1 accent-[var(--brand-gold)]" />
                      {service.name}
                    </label>
                  {/each}
                </div>
              </div>
            {/if}
          {/each}
        </div>
      </fieldset>
    </div>
  {/snippet}

  {#snippet result()}
    <div class="grid gap-5">
      <div
        class="relative overflow-hidden rounded-2xl bg-brand-ink p-6 text-white shadow-[0_24px_60px_-30px_rgba(20,20,20,0.6)] md:p-7"
      >
        <div
          aria-hidden="true"
          class="pointer-events-none absolute -top-20 -right-16 size-56 rounded-full bg-brand-gold/25 blur-3xl"
        ></div>
        <p class="relative text-xs font-semibold tracking-[0.2em] text-brand-dark-accent uppercase">
          Typical market range
        </p>
        <div class="relative" aria-live="polite" aria-atomic="true">
          <p class="mt-3 font-display text-3xl leading-tight font-bold tabular-nums sm:text-4xl">
            {formatAudRange(estimate.total)}
          </p>
          <p class="mt-2 text-sm text-white/75">
            About {formatAudRange(estimate.perGuest)} per guest · {summary}
          </p>
          {#if estimate.excludes.length}
            <p class="mt-2 text-sm text-white/75">
              Excludes {estimate.excludes.join(', ')}: quoted on request.
            </p>
          {/if}
        </div>
        <p class="relative mt-4 border-t border-white/15 pt-3 text-xs text-white/60">
          Typical market range, not a 7Magic quote. Estimates checked {ESTIMATES_AS_OF}.
        </p>
      </div>

      <details class="group rounded-2xl border border-border bg-background p-5" open>
        <summary class="cursor-pointer list-none text-sm font-semibold [&::-webkit-details-marker]:hidden">
          Where the money goes
        </summary>
        <table class="mt-3 w-full text-sm">
          <tbody>
            {#each estimate.lines as line (line.key)}
              <tr class="border-t border-border">
                <td class="py-2 pr-3">{line.label}</td>
                <td class="py-2 text-right tabular-nums">
                  {line.range ? formatAudRange(line.range) : 'Quoted on request'}
                </td>
              </tr>
            {/each}
            <tr class="border-t-2 border-foreground/30 font-semibold">
              <td class="py-2 pr-3">Total</td>
              <td class="py-2 text-right tabular-nums">{formatAudRange(estimate.total)}</td>
            </tr>
          </tbody>
        </table>
      </details>

      <div class="rounded-2xl border border-border bg-background p-5">
        <p class="flex items-center gap-2 text-sm font-semibold">
          <PlaneIcon size={16} class="text-brand-gold-hover" />Your guests' flights (their cost, not your bill)
        </p>
        <ul class="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
          {#each CITIES as city (city.key)}
            <li class="flex justify-between gap-2">
              <span>{city.label}</span>
              <span class="tabular-nums text-muted-foreground">{formatAudRange(estimate.guestTravel[city.key])}</span>
            </li>
          {/each}
        </ul>
        <p class="mt-2 text-xs text-muted-foreground">Typical return economy fares; December and July cost more.</p>
      </div>

      <a
        href={siteHref('/bali-wedding-concierge')}
        class="text-sm text-brand-gold-hover underline underline-offset-2"
      >
        See everything our Bali concierge can arrange
      </a>
    </div>
  {/snippet}

  {#snippet explainer()}
    <section class="px-5 py-16 lg:px-8">
      <div class="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.4fr)]">
        <div class="lg:sticky lg:top-24 lg:self-start">
          <h2 class="font-display text-2xl font-bold md:text-3xl">How we estimate</h2>
          <p class="mt-3 text-[15px] leading-7 text-muted-foreground">
            Built only from prices that venues, planners and suppliers publish. Here is every step,
            so you can judge the number yourself.
          </p>
        </div>
        <div class="grid gap-6">
          <ul class="grid gap-3">
            {#each METHOD_NOTES as note (note)}
              <li class="border-l-2 border-brand-gold/40 pl-5 text-[15px] leading-7 text-foreground/80">{note}</li>
            {/each}
          </ul>
          <details class="rounded-xl border border-border p-5">
            <summary class="cursor-pointer text-sm font-semibold">Sources ({COST_SOURCES.length})</summary>
            <ol class="mt-3 grid list-decimal gap-2 pl-5 text-sm leading-6 text-muted-foreground">
              {#each COST_SOURCES as source (source.url)}
                <li>
                  <a href={source.url} target="_blank" rel="noopener noreferrer" class="underline underline-offset-2 hover:text-foreground">
                    {source.title}
                  </a>
                </li>
              {/each}
            </ol>
          </details>
          <p class="text-sm text-muted-foreground">
            A worked example: a classic villa wedding for 55 guests comes to {formatAudRange(
              estimateCost({ guests: 55, setting: 'villa', style: 'classic', year: 2027, month: 7, addOns: [] })
                .total
            )}. Easy Weddings' 2026 survey puts the average Australian destination wedding at {formatAud(
              32_060
            )} for about 55 guests.
          </p>
        </div>
      </div>
    </section>

    <section class="bg-secondary px-5 py-16 lg:px-8">
      <div class="mx-auto max-w-5xl">
        <BaliEnquiry
          sourcePath={TOOL_PATH}
          heading="Turn this estimate into a real quote"
          lead="Send us your numbers and a planner on our Bali team will come back with venues and real prices for your date."
          {context}
          {whatsappText}
          event="Bali Cost Quote Requested"
        />
      </div>
    </section>
  {/snippet}
</ToolShell>
