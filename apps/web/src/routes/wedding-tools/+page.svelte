<script lang="ts">
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import CalendarHeartIcon from '@lucide/svelte/icons/calendar-heart';
  import CalculatorIcon from '@lucide/svelte/icons/calculator';
  import CalendarRangeIcon from '@lucide/svelte/icons/calendar-range';
  import CompassIcon from '@lucide/svelte/icons/compass';
  import PalmtreeIcon from '@lucide/svelte/icons/palmtree';
  import HashIcon from '@lucide/svelte/icons/hash';
  import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
  import MoonStarIcon from '@lucide/svelte/icons/moon-star';
  import SparklesIcon from '@lucide/svelte/icons/sparkles';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import { siteHref } from '$lib/seo/english-only';
  import {
    absoluteUrl,
    breadcrumbList,
    canonicalUrl,
    graph,
    jsonLdScript,
    organization,
    webPageNode,
    website
  } from '$lib/seo/schema';
  import { hubCopy, type ToolCard } from './content';

  /**
   * The Wedding Tools hub. Three live tools today, three announced; the announced
   * ones are cards without links so the page can grow without a redesign and
   * without linking anywhere that does not exist yet.
   */

  const locale = $derived(getLocale());
  const copy = $derived(hubCopy(locale));
  const canonical = $derived(canonicalUrl(localizeHref('/wedding-tools')));

  const ICONS: Record<ToolCard['key'], typeof SparklesIcon> = {
    mahar: CalendarHeartIcon,
    hashtag: HashIcon,
    bazi: CompassIcon,
    'bali-cost': PalmtreeIcon,
    'bali-dates': CalendarRangeIcon,
    weton: SparklesIcon,
    tionghoa: MoonStarIcon,
    budget: CalculatorIcon
  };

  // Only live tools go in the ItemList: structured data has to match what a
  // reader can follow, and a "coming soon" card has nowhere to go.
  const jsonLd = $derived.by(() => {
    const live = copy.tools.filter((tool) => tool.path);
    return jsonLdScript(
      graph(
        organization(),
        website(),
        webPageNode({
          url: localizeHref('/wedding-tools'),
          name: copy.meta.title,
          description: copy.meta.description,
          locale,
          type: 'CollectionPage',
          mainEntity: {
            '@type': 'ItemList',
            itemListElement: live.map((tool, index) => ({
              '@type': 'ListItem',
              position: index + 1,
              name: tool.title,
              url: absoluteUrl(siteHref(tool.path!))
            }))
          }
        }),
        breadcrumbList([{ name: m.breadcrumb_home(), path: '/' }, { name: m.nav_wedding_tools() }])
      )
    );
  });
</script>

<svelte:head>
  <title>{copy.meta.title}</title>
  <meta name="description" content={copy.meta.description} />
  <link rel="canonical" href={canonical} />
  {@html jsonLd}
</svelte:head>

<SocialMeta title={copy.meta.title} description={copy.meta.description} url={canonical} />

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <section class="relative overflow-hidden bg-secondary px-5 pt-8 pb-14 md:pt-10 md:pb-20 lg:px-8">
    <div
      aria-hidden="true"
      class="pointer-events-none absolute -top-32 -right-24 size-[28rem] rounded-full bg-brand-warm-deep/70 blur-3xl"
    ></div>
    <div class="relative mx-auto max-w-7xl">
      <nav aria-label={m.vd_breadcrumb()}>
        <ol class="flex flex-wrap items-center gap-1 text-xs text-muted-foreground">
          <li>
            <a href={localizeHref('/')} class="transition hover:text-foreground">
              {m.breadcrumb_home()}
            </a>
          </li>
          <li class="flex items-center gap-1">
            <ChevronRightIcon size={13} aria-hidden="true" />
            <span aria-current="page" class="text-foreground/80">{m.nav_wedding_tools()}</span>
          </li>
        </ol>
      </nav>
      <p class="mt-6 text-xs font-semibold tracking-[0.2em] text-brand-gold-hover uppercase">
        {copy.hero.eyebrow}
      </p>
      <h1 class="mt-3 max-w-3xl font-display text-3xl leading-tight font-bold md:text-5xl">
        {copy.hero.title}
      </h1>
      <p class="mt-4 max-w-2xl text-base leading-7 text-muted-foreground md:text-lg md:leading-8">
        {copy.hero.lead}
      </p>
    </div>
  </section>

  <section class="px-5 pb-20 lg:px-8">
    <ul class="relative mx-auto -mt-8 grid max-w-7xl gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {#each copy.tools as tool (tool.key)}
        {@const Icon = ICONS[tool.key]}
        <li class="h-full">
          {#if tool.path}
            <a
              href={siteHref(tool.path)}
              class="group flex h-full flex-col rounded-2xl border border-brand-gold/50 bg-background p-6 shadow-[0_18px_50px_-30px_rgba(138,101,36,0.5)] transition hover:-translate-y-0.5 hover:border-brand-gold hover:shadow-[0_24px_60px_-28px_rgba(138,101,36,0.55)] focus-visible:ring-3 focus-visible:ring-ring/40 focus-visible:outline-none"
            >
              <div class="flex items-center justify-between">
                <span
                  class="flex size-11 items-center justify-center rounded-full bg-brand-gold-soft text-brand-gold-hover"
                >
                  <Icon size={20} aria-hidden="true" />
                </span>
                <span
                  class="rounded-full bg-brand-gold px-2.5 py-0.5 text-[11px] font-semibold tracking-wider text-white uppercase"
                >
                  {m.tools_free_badge()}
                </span>
              </div>
              <h2 class="mt-5 font-display text-lg leading-snug font-bold">{tool.title}</h2>
              <p class="mt-2 text-sm leading-6 text-muted-foreground">{tool.copy}</p>
              <span
                class="mt-auto flex items-center gap-1.5 pt-6 text-sm font-semibold text-brand-gold-hover"
              >
                {copy.open}
                <ArrowRightIcon
                  size={16}
                  aria-hidden="true"
                  class="transition group-hover:translate-x-0.5"
                />
              </span>
            </a>
          {:else}
            <div class="flex h-full flex-col rounded-2xl border border-dashed border-border bg-background/70 p-6">
              <div class="flex items-center justify-between">
                <span
                  class="flex size-11 items-center justify-center rounded-full bg-muted text-muted-foreground"
                >
                  <Icon size={20} aria-hidden="true" />
                </span>
                <span
                  class="rounded-full border border-border px-2.5 py-0.5 text-[11px] font-semibold tracking-wider text-muted-foreground uppercase"
                >
                  {m.tools_coming_soon()}
                </span>
              </div>
              <h2 class="mt-5 font-display text-lg leading-snug font-bold text-foreground/70">
                {tool.title}
              </h2>
              <p class="mt-2 text-sm leading-6 text-muted-foreground">{tool.copy}</p>
            </div>
          {/if}
        </li>
      {/each}
    </ul>
  </section>

  <PublicFooter />
</main>
