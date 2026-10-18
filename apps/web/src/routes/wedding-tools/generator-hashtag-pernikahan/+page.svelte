<script lang="ts">
  import { onMount } from 'svelte';
  import ArrowLeftRightIcon from '@lucide/svelte/icons/arrow-left-right';
  import CheckIcon from '@lucide/svelte/icons/check';
  import CopyIcon from '@lucide/svelte/icons/copy';
  import DownloadIcon from '@lucide/svelte/icons/download';
  import ExternalLinkIcon from '@lucide/svelte/icons/external-link';
  import InfoIcon from '@lucide/svelte/icons/info';
  import LockIcon from '@lucide/svelte/icons/lock';
  import PrinterIcon from '@lucide/svelte/icons/printer';
  import DateField from '$lib/components/DateField.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import HashtagCard from '$lib/components/tools/HashtagCard.svelte';
  import LeadGate from '$lib/components/tools/LeadGate.svelte';
  import ToolShell from '$lib/components/tools/ToolShell.svelte';
  import { Button } from '$lib/components/ui/button';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import { canonicalUrl, toolPageJsonLd } from '$lib/seo/schema';
  import {
    HASHTAG_EVENTS,
    generateHashtags,
    instagramTagUrl,
    type HashtagEvent
  } from '$lib/tools/hashtag';
  import { isUnlocked } from '$lib/tools/lead';
  import { formatMasehi } from '$lib/tools/mahar';
  import { TOOL_PATH, hashtagCopy } from './content';

  /**
   * The wedding hashtag generator: two names in, a few dozen hashtags out.
   *
   * Every tag is free and server-rendered with the explainer and FAQ; only the
   * designed sign sits behind the soft gate, as on the mahar page. The tags
   * come from `$lib/tools/hashtag`; this file wires inputs to it, keeps the
   * couple's pick, and copies to the clipboard.
   */

  const locale = $derived(getLocale());
  const copy = $derived(hashtagCopy(locale));
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

  let groom = $state('');
  let bride = $state('');
  let brideFirst = $state(false);
  let family = $state('');
  let date = $state('');
  let city = $state('');
  let events = $state<HashtagEvent[]>([]);
  // The tag the couple tapped, kept as text rather than an index so it
  // survives a change to the inputs that reorders the list but keeps the tag.
  let picked = $state('');

  let unlocked = $state(false);
  let gateOpen = $state(false);
  let exporting = $state(false);
  let exportError = $state('');
  let copied = $state<string | null>(null);
  let copyError = $state('');
  let copiedTimer: ReturnType<typeof setTimeout> | undefined;
  let card = $state<ReturnType<typeof HashtagCard>>();

  onMount(() => {
    unlocked = isUnlocked();
    return () => clearTimeout(copiedTimer);
  });

  const groups = $derived(
    generateHashtags({ groom, bride, family, date, city, events, brideFirst })
  );
  const allTags = $derived(groups.flatMap((group) => group.tags));
  // Falls back to the first tag when the pick is gone (a name was edited), so
  // there is always a tag on the card and nothing resets in an effect.
  const selected = $derived(allTags.find((item) => item.tag === picked) ?? allTags[0]);

  const orderLabels = $derived.by(() => {
    const g = groom.trim() || copy.form.groomPlaceholder;
    const b = bride.trim() || copy.form.bridePlaceholder;
    return [`${g} & ${b}`, `${b} & ${g}`];
  });

  const names = $derived.by(() => {
    const pair = [groom.trim(), bride.trim()].filter(Boolean);
    return (brideFirst ? pair.reverse() : pair).join(' & ');
  });
  const dateLine = $derived(formatMasehi(date, locale));
  const cardLabel = $derived(
    [copy.card.title, names || copy.card.fallbackTitle, dateLine, selected?.tag]
      .filter(Boolean)
      .join(', ')
  );

  const leadInputs = $derived.by(() => {
    const fields: Record<string, string | boolean> = { tag: selected?.tag ?? '' };
    if (family.trim()) fields.family = family.trim().slice(0, 60);
    if (date) fields.date = date;
    if (city.trim()) fields.city = city.trim().slice(0, 60);
    if (events.length) fields.events = events.join(',');
    if (brideFirst) fields.bride_first = true;
    return fields;
  });

  async function writeClipboard(text: string, key: string) {
    copyError = '';
    try {
      await navigator.clipboard.writeText(text);
      copied = key;
      clearTimeout(copiedTimer);
      copiedTimer = setTimeout(() => (copied = null), 2000);
    } catch {
      // Insecure origins and some in-app browsers refuse the clipboard; the tag
      // is plain selectable text, so the fallback is the visitor's own copy.
      copyError = copy.result.copyFailed;
    }
  }

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

  function toggleEvent(event: HashtagEvent, on: boolean) {
    events = on ? [...events, event] : events.filter((item) => item !== event);
  }

  const example = $derived(copy.example);
  const exampleTags = $derived.by(() => {
    const exampleGroups = generateHashtags(example);
    return exampleGroups.flatMap((group) => group.tags.slice(0, 2).map((item) => item.tag));
  });

  function tryExample() {
    groom = example.groom;
    bride = example.bride;
    brideFirst = false;
    family = '';
    date = example.date;
    city = example.city;
    events = [...example.events];
    picked = '';
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    document
      .getElementById('hashtag-result')
      ?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  }

  const FIELD =
    'h-11 w-full rounded-md border border-input bg-background px-3 text-base placeholder:text-muted-foreground/60 focus:border-ring focus:ring-3 focus:ring-ring/30 focus:outline-none md:text-[15px]';
  const LEGEND = 'text-[13px] font-semibold tracking-wide text-foreground';
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
        <legend class={LEGEND}>{copy.form.namesLegend}</legend>
        <div class="mt-3 grid gap-3 sm:grid-cols-2">
          <div class="grid gap-1.5">
            <label for="hashtag-groom" class="text-xs text-muted-foreground">{copy.form.groomLabel}</label>
            <input
              id="hashtag-groom"
              bind:value={groom}
              maxlength="20"
              autocomplete="off"
              autocapitalize="words"
              placeholder={copy.form.groomPlaceholder}
              class={FIELD}
            />
          </div>
          <div class="grid gap-1.5">
            <label for="hashtag-bride" class="text-xs text-muted-foreground">{copy.form.brideLabel}</label>
            <input
              id="hashtag-bride"
              bind:value={bride}
              maxlength="20"
              autocomplete="off"
              autocapitalize="words"
              placeholder={copy.form.bridePlaceholder}
              class={FIELD}
            />
          </div>
        </div>
        <p class="mt-2 text-xs leading-5 text-muted-foreground">{copy.form.namesHint}</p>
      </fieldset>

      <fieldset>
        <legend class="{LEGEND} flex items-center gap-1.5">
          <ArrowLeftRightIcon size={14} class="text-brand-gold" aria-hidden="true" />
          {copy.form.orderLegend}
        </legend>
        <div class="mt-3 flex flex-wrap gap-2">
          {#each [false, true] as option, index (index)}
            <label class="{CHOICE} rounded-full px-4 py-2 text-sm font-medium">
              <input
                type="radio"
                name="hashtag-order"
                value={option}
                checked={brideFirst === option}
                onchange={() => (brideFirst = option)}
                class="sr-only"
              />
              {orderLabels[index]}
            </label>
          {/each}
        </div>
      </fieldset>

      <fieldset class="grid gap-4">
        <legend class={LEGEND}>
          {copy.form.extrasLegend}
          <span class="font-normal text-muted-foreground">({copy.form.optional})</span>
        </legend>
        <div class="mt-3 grid gap-3 sm:grid-cols-2">
          <div class="grid gap-1.5">
            <label for="hashtag-date" class="text-xs text-muted-foreground">{copy.form.dateLabel}</label>
            <DateField
              id="hashtag-date"
              bind:value={date}
              {locale}
              placeholder={copy.form.datePlaceholder}
              class="h-11 w-full text-base md:text-[15px]"
            />
          </div>
          <div class="grid gap-1.5">
            <label for="hashtag-city" class="text-xs text-muted-foreground">{copy.form.cityLabel}</label>
            <input
              id="hashtag-city"
              bind:value={city}
              maxlength="24"
              autocomplete="off"
              placeholder={copy.form.cityPlaceholder}
              class={FIELD}
            />
          </div>
          <div class="grid gap-1.5 sm:col-span-2">
            <label for="hashtag-family" class="text-xs text-muted-foreground">
              {copy.form.familyLabel}
              <span class="text-muted-foreground/80">· {copy.form.familyHint}</span>
            </label>
            <input
              id="hashtag-family"
              bind:value={family}
              maxlength="24"
              autocomplete="off"
              autocapitalize="words"
              placeholder={copy.form.familyPlaceholder}
              class={FIELD}
            />
          </div>
        </div>
      </fieldset>

      <fieldset>
        <legend class={LEGEND}>{copy.form.eventsLegend}</legend>
        <div class="mt-3 flex flex-wrap gap-2">
          {#each HASHTAG_EVENTS as event (event)}
            <label class="{CHOICE} rounded-full px-4 py-2 text-sm font-medium">
              <input
                type="checkbox"
                checked={events.includes(event)}
                onchange={(change) => toggleEvent(event, change.currentTarget.checked)}
                class="sr-only"
              />
              {copy.form.events[event]}
            </label>
          {/each}
        </div>
      </fieldset>
    </div>
  {/snippet}

  {#snippet result()}
    <div id="hashtag-result" class="grid scroll-mt-24 gap-5">
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
            <p class="mt-3 font-display text-3xl leading-tight font-bold break-all sm:text-4xl">
              {selected.tag}
            </p>
            <div class="mt-4 flex flex-wrap items-center gap-2.5">
              <Button variant="gold" size="sm" onclick={() => writeClipboard(selected.tag, 'main')}>
                {#if copied === 'main'}
                  <CheckIcon size={15} aria-hidden="true" />{copy.result.copied}
                {:else}
                  <CopyIcon size={15} aria-hidden="true" />{copy.result.copy}
                {/if}
              </Button>
              <a
                href={instagramTagUrl(selected.tag)}
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1 text-sm text-white/80 underline decoration-white/30 underline-offset-2 transition hover:text-white"
              >
                {copy.result.check}<ExternalLinkIcon size={13} aria-hidden="true" />
              </a>
            </div>
            {#if selected.long}
              <p class="mt-3 flex gap-2 text-[13px] leading-6 text-white/75">
                <InfoIcon size={15} class="mt-1 shrink-0 text-brand-dark-accent" aria-hidden="true" />
                {copy.result.longNote}
              </p>
            {/if}
          {:else}
            <p class="mt-3 font-display text-3xl font-semibold text-white/40">{copy.result.emptyTag}</p>
            <p class="mt-3 text-sm text-white/70">{copy.result.empty}</p>
          {/if}
        </div>

        {#if groups.length}
          <div class="relative mt-6 border-t border-white/15 pt-5">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <p class="text-sm text-white/70">{copy.result.count(allTags.length)}</p>
              <button
                type="button"
                onclick={() => writeClipboard(allTags.map((item) => item.tag).join(' '), 'all')}
                class="inline-flex items-center gap-1.5 rounded-full border border-white/25 px-3.5 py-1.5 text-sm font-medium transition hover:border-brand-dark-accent hover:text-brand-dark-accent focus-visible:ring-3 focus-visible:ring-brand-dark-accent/40 focus-visible:outline-none"
              >
                {#if copied === 'all'}
                  <CheckIcon size={14} aria-hidden="true" />{copy.result.copiedAll}
                {:else}
                  <CopyIcon size={14} aria-hidden="true" />{copy.result.copyAll}
                {/if}
              </button>
            </div>
            <p class="mt-2 text-xs leading-5 text-white/55">{copy.result.pickHint}</p>
            {#if copyError}
              <p class="mt-2 text-sm text-brand-dark-accent" role="alert">{copyError}</p>
            {/if}

            <div class="mt-5 grid gap-5">
              {#each groups as group (group.id)}
                <div>
                  <p class="text-xs font-semibold tracking-wide text-brand-dark-accent">
                    {copy.result.groups[group.id].title}
                    <span class="font-normal text-white/50">· {copy.result.groups[group.id].hint}</span>
                  </p>
                  <ul class="mt-2.5 flex flex-wrap gap-2">
                    {#each group.tags as item (item.tag)}
                      <li>
                        <button
                          type="button"
                          aria-pressed={selected?.tag === item.tag}
                          onclick={() => (picked = item.tag)}
                          title={item.long ? copy.result.longNote : undefined}
                          class="rounded-full border px-3 py-1.5 text-left text-sm break-all transition focus-visible:ring-3 focus-visible:ring-brand-dark-accent/40 focus-visible:outline-none {selected?.tag ===
                          item.tag
                            ? 'border-brand-dark-accent bg-brand-dark-accent font-semibold text-brand-ink'
                            : 'border-white/15 bg-white/[0.06] text-white/90 hover:border-brand-dark-accent/60'} {item.long
                            ? 'border-dashed'
                            : ''}"
                        >
                          {item.tag}
                        </button>
                      </li>
                    {/each}
                  </ul>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>

      <div class="rounded-2xl border border-border bg-background p-5 md:p-6">
        <div class="flex items-baseline justify-between gap-3">
          <h2 class="font-display text-lg font-bold">{copy.card.title}</h2>
          <span class="text-xs text-muted-foreground">A5 · PNG</span>
        </div>
        <p class="mt-1 text-sm leading-6 text-muted-foreground">{copy.card.lead}</p>

        <div class="relative mt-4 overflow-hidden rounded-xl bg-brand-warm ring-1 ring-brand-gold/20">
          <HashtagCard
            bind:this={card}
            {names}
            {dateLine}
            tag={selected?.tag ?? ''}
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
            <Button variant="gold" size="lg" onclick={downloadPng} disabled={exporting || !selected}>
              <DownloadIcon size={17} aria-hidden="true" />
              {exporting ? copy.card.exporting : copy.card.downloadPng}
            </Button>
            <Button variant="outline" size="lg" onclick={() => card?.print()} disabled={!selected}>
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
      tool="hashtag"
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
        </div>
      </div>
    </section>

    <section class="bg-brand-ink px-5 py-16 text-white lg:px-8">
      <div class="mx-auto grid max-w-7xl gap-8 md:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)] md:items-center">
        <div>
          <span
            class="inline-block rounded-full border border-white/20 px-3 py-1 text-[11px] font-semibold tracking-wider text-white/70 uppercase"
          >
            {example.badge}
          </span>
          <h2 class="mt-4 font-display text-2xl font-bold md:text-3xl">{example.title}</h2>
          <p class="mt-3 max-w-xl text-[15px] leading-7 text-white/70">{example.lead}</p>
          <p class="mt-4 text-sm text-white/60">
            {formatMasehi(example.date, locale)} · {example.city}
          </p>
          <button
            type="button"
            onclick={tryExample}
            class="mt-6 rounded-full border border-brand-dark-accent/50 px-5 py-2 text-sm font-medium text-brand-dark-accent transition hover:bg-brand-dark-accent hover:text-brand-ink focus-visible:ring-3 focus-visible:ring-brand-dark-accent/40 focus-visible:outline-none"
          >
            {example.tryIt}
          </button>
        </div>
        <ul class="flex flex-wrap gap-2.5">
          {#each exampleTags as tag (tag)}
            <li
              class="rounded-full border border-white/10 bg-white/[0.05] px-4 py-2 font-display text-[15px] font-semibold text-white/90"
            >
              {tag}
            </li>
          {/each}
        </ul>
      </div>
    </section>
  {/snippet}
</ToolShell>
