<script lang="ts">
  import ArrowRight from '@lucide/svelte/icons/arrow-right';
  import CalendarDays from '@lucide/svelte/icons/calendar-days';
  import Check from '@lucide/svelte/icons/check';
  import Compass from '@lucide/svelte/icons/compass';
  import Heart from '@lucide/svelte/icons/heart';
  import Sparkles from '@lucide/svelte/icons/sparkles';
  import Users from '@lucide/svelte/icons/users';
  import ArticleCard from '$lib/components/ArticleCard.svelte';
  import HeroVenueSearch from '$lib/components/HeroVenueSearch.svelte';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import VenueCard from '$lib/components/VenueCard.svelte';
  import { page } from '$app/state';
  import { getLocale } from '$lib/paraglide/runtime';
  import {
    ORGANIZATION_ID,
    graph,
    jsonLdScript,
    organization,
    venueItemList,
    webPageNode,
    website
  } from '$lib/seo/schema';
  import { m } from '$lib/paraglide/messages.js';

  let { data } = $props();
  let home = $derived(data.home);

  // The home page is where the site-wide Organization and WebSite nodes live —
  // the SearchAction on the latter is what lets the venue search surface as a
  // sitelinks search box. Every other page references them by @id.
  //
  // The page node is keyed on the request path, not on the site root: / and /en
  // are two pages, and giving them one @id would have the English home page
  // claiming to be the Indonesian one.
  const jsonLd = $derived(
    jsonLdScript(
      graph(
        organization(),
        website(),
        webPageNode({
          url: page.url.pathname,
          name: '7Magic Wedding | Venue Packages Jakarta Bali Singapore',
          locale: getLocale(),
          about: ORGANIZATION_ID
        }),
        venueItemList(home.featured_venues, {
          name: m.schema_home_venue_list(),
          url: page.url.pathname
        })
      )
    )
  );

  const quickLinks = [
    { label: 'Jakarta venues', href: '/wedding-venue/search?city=jakarta' },
    { label: 'Bali venues', href: '/wedding-venue/search?city=bali' },
    { label: '5-star hotels', href: '/wedding-venue/search?stars_min=5' },
    { label: 'Ballroom packages', href: '/wedding-venue/search?q=ballroom' },
    { label: 'Chapel & garden', href: '/wedding-venue/search?q=chapel' }
  ];

  const weddingStyles = [
    { title: 'Luxury ballroom', copy: 'Grand hotel receptions with complete vendor guidance.', href: '/wedding-venue/search?q=ballroom' },
    { title: 'Garden wedding', copy: 'Open-air celebrations, resort lawns, and softer scenery.', href: '/wedding-venue/search?q=garden' },
    { title: 'Chapel ceremony', copy: 'Ceremony-first venues for intimate destination moments.', href: '/wedding-venue/search?q=chapel' },
    { title: 'Hotel reception', copy: 'Practical packages with hospitality, rooms, and catering.', href: '/wedding-venue/search?stars_min=5' }
  ];

  const planningSteps = [
    { title: 'Choose a venue direction', copy: 'Shortlist by city, style, guest count, and atmosphere.' },
    { title: 'Share date and pax', copy: 'Tell us the wedding date, preferred package size, and must-haves.' },
    { title: 'Get package guidance', copy: 'A 7Magic planner helps confirm options before you visit.' }
  ];

  const packageLinks = [
    { label: '150 pax packages', href: '/wedding-venue/search?q=150' },
    { label: '200 pax packages', href: '/wedding-venue/search?q=200' },
    { label: '300+ pax packages', href: '/wedding-venue/search?q=300' },
    { label: 'Private pricing help', href: '/contact' }
  ];
</script>

<svelte:head>
  <title>7Magic Wedding | Venue Packages Jakarta Bali Singapore</title>
  <meta
    name="description"
    content="Curated wedding venue packages, wedding organizer support, and planning articles for Jakarta, Bali, and Singapore celebrations."
  />
  <!-- Svelte parses script contents as raw text, so JSON-LD has to arrive as
       pre-rendered markup rather than as an expression inside the tag. -->
  {@html jsonLd}
</svelte:head>

<main class="min-h-screen bg-background text-slate-900">
  <PublicHeader />
  <!-- Hero copy comes from Paraglide, not from `home.hero`: the API serves it
       from a static fixture in English only, so the Indonesian site was reading
       English headings. The image still comes from the payload. -->
  <HeroVenueSearch title={m.hero_title()} subtitle={m.hero_subtitle()} image={home.hero.image} />

  <section class="bg-brand-ink px-5 py-5 text-white lg:px-8">
    <div class="mx-auto flex max-w-7xl flex-wrap items-center gap-3">
      <span class="inline-flex items-center gap-2 text-sm font-semibold text-white/72">
        <Compass size={16} />
        Browse fast
      </span>
      {#each quickLinks as item}
        <a href={item.href} class="rounded-full border border-white/18 bg-white/8 px-4 py-2 text-sm font-semibold text-white/88 transition hover:bg-white hover:text-brand-ink">
          {item.label}
        </a>
      {/each}
    </div>
  </section>

  <section class="mx-auto max-w-7xl px-5 py-14 lg:px-8">
    <div class="flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">{m.home_popular_eyebrow()}</p>
        <h2 class="mt-3 text-3xl font-semibold md:text-4xl">{m.home_popular_title()}</h2>
        <p class="mt-3 max-w-2xl text-slate-600">
          {m.home_popular_body()}
        </p>
      </div>
      <a href="/wedding-venue/search" class="inline-flex items-center gap-2 font-semibold text-accent-foreground">
        View all packages
        <ArrowRight size={18} />
      </a>
    </div>

    <div class="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
      {#each home.featured_venues as venue}
        <VenueCard {venue} />
      {/each}
    </div>
  </section>

  {#snippet cityVenues(
    eyebrow: string,
    title: string,
    body: string,
    city: string,
    venues: typeof data.baliVenues
  )}
    <!-- Skipped rather than shown empty: a city with no venues yet would otherwise
         render a heading over a blank grid. -->
    {#if venues.length}
      <section class="mx-auto max-w-7xl px-5 py-14 lg:px-8">
        <div class="flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
              {eyebrow}
            </p>
            <h2 class="mt-3 text-3xl font-semibold md:text-4xl">{title}</h2>
            <p class="mt-3 max-w-2xl text-slate-600">{body}</p>
          </div>
          <a
            href="/wedding-venue/search?city={city}"
            class="inline-flex items-center gap-2 font-semibold text-accent-foreground"
          >
            {m.home_venues_view_all()}
            <ArrowRight size={18} />
          </a>
        </div>

        <div class="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {#each venues as venue}
            <VenueCard {venue} />
          {/each}
        </div>
      </section>
    {/if}
  {/snippet}

  {@render cityVenues(
    m.city_bali(),
    m.home_venues_bali_title(),
    m.home_venues_bali_body(),
    'bali',
    data.baliVenues
  )}

  {@render cityVenues(
    m.city_singapore(),
    m.home_venues_singapore_title(),
    m.home_venues_singapore_body(),
    'singapore',
    data.singaporeVenues
  )}

  <section class="bg-white px-5 py-14 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Browse by style</p>
          <h2 class="mt-3 text-3xl font-semibold">Find the right setting faster</h2>
        </div>
        <a href="/wedding-venue/search" class="inline-flex items-center gap-2 font-semibold text-accent-foreground">
          Explore venue search
          <ArrowRight size={18} />
        </a>
      </div>

      <div class="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {#each weddingStyles as style}
          <a href={style.href} class="group rounded-md border border-border bg-background p-5 transition hover:-translate-y-1 hover:border-primary hover:bg-white hover:shadow-xl">
            <div class="flex size-10 items-center justify-center rounded-md bg-brand-warm-deep text-accent-foreground">
              <Sparkles size={18} />
            </div>
            <h3 class="mt-5 text-xl font-semibold">{style.title}</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">{style.copy}</p>
            <span class="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-accent-foreground">
              Browse style
              <ArrowRight size={15} class="transition group-hover:translate-x-1" />
            </span>
          </a>
        {/each}
      </div>
    </div>
  </section>

  <section class="bg-brand-warm px-5 py-14 lg:px-8">
    <div class="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[0.8fr_1.2fr]">
      <div>
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">How 7Magic helps</p>
        <h2 class="mt-3 text-3xl font-semibold">From shortlist to package clarity</h2>
        <p class="mt-4 leading-7 text-slate-600">
          Move from browsing to a realistic venue plan with a planner who knows the package details.
        </p>
      </div>
      <div class="grid gap-4 md:grid-cols-3">
        {#each planningSteps as step, index}
          <div class="rounded-md border border-border bg-white p-5 shadow-sm">
            <div class="flex size-9 items-center justify-center rounded-full bg-primary text-sm font-bold text-white">
              {index + 1}
            </div>
            <h3 class="mt-4 font-semibold">{step.title}</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">{step.copy}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <section class="mx-auto max-w-7xl px-5 py-14 lg:px-8">
    <div class="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Couples</p>
        <h2 class="mt-3 text-3xl font-semibold">Real notes from couples who trusted 7Magic</h2>
      </div>
      <a href="/contact" class="inline-flex items-center gap-2 font-semibold text-accent-foreground">
        Ask for guidance
        <ArrowRight size={18} />
      </a>
    </div>
    <div class="grid gap-5 md:grid-cols-3">
      {#each home.testimonials as testimonial}
        <figure class="rounded-md border border-border bg-white p-5 shadow-sm">
          <img src={testimonial.image} alt={testimonial.couple} class="h-52 w-full rounded object-cover" />
          <blockquote class="mt-4 leading-7 text-slate-700">"{testimonial.message}"</blockquote>
          <figcaption class="mt-4 flex items-center gap-2 font-semibold">
            <Heart size={16} class="text-rose-500" />
            {testimonial.couple}
          </figcaption>
        </figure>
      {/each}
    </div>
  </section>

  <PublicFooter />
</main>
