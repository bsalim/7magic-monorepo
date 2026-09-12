<script lang="ts">
  import StarIcon from '@lucide/svelte/icons/star';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import VenueCard from '$lib/components/VenueCard.svelte';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import { m } from '$lib/paraglide/messages.js';
  import {
    breadcrumbList,
    canonicalUrl,
    faqPage,
    graph,
    jsonLdScript,
    organization,
    venueItemList,
    webPageNode,
    website
  } from '$lib/seo/schema';
  import { formatMillions, formatPrice } from '$lib/utils';
  import { cityFloorPrice, cityStats, groupByBudget, groupByStars } from '$lib/venue-groups';
  import { hubCopy } from './content';

  let { data } = $props();

  const groups = $derived(groupByStars(data.venues));
  const floor = $derived(cityFloorPrice(data.venues));
  const budget = $derived(groupByBudget(data.venues));
  const copy = $derived(hubCopy(getLocale(), data.cityName, cityStats(data.venues)));

  const path = $derived(`/wedding-venue/${data.citySlug}`);
  // Localized, for the same reason the venue detail page localizes its own: an
  // unprefixed canonical on /en names the Indonesian URL, which tells Google the
  // English page is a duplicate not to index while the hreflang tags beside it
  // say they are alternates. The canonical wins, and the page is dropped.
  const canonical = $derived(canonicalUrl(localizeHref(path)));

  const title = $derived(
    m.city_hub_meta_title({ city: data.cityName, count: data.venues.length })
  );
  const description = $derived(
    m.city_hub_meta_description({ city: data.cityName, count: data.venues.length })
  );

  // The floor is the whole reason this page can answer a "berapa harga" query,
  // but a city where every venue is priced on request has no floor to quote --
  // and quoting Rp 0 would be worse than saying nothing.
  const intro = $derived(
    floor
      ? m.city_hub_intro({
          city: data.cityName,
          count: data.venues.length,
          price: formatMillions(floor, m.currency_millions_unit())
        })
      : m.city_hub_intro_no_price({ city: data.cityName, count: data.venues.length })
  );

  const heading = (stars: number) =>
    stars > 0 ? m.city_hub_stars_heading({ stars }) : m.city_hub_unrated_heading();

  const jsonLd = $derived(
    jsonLdScript(
      graph(
        organization(),
        website(),
        webPageNode({
          type: 'CollectionPage',
          url: path,
          name: m.city_hub_title({ city: data.cityName }),
          description,
          locale: getLocale(),
          image: data.venues[0]?.cover_photo?.small_url,
          // Every venue in the city, in the order the page renders them, so the
          // list a crawler reads is the list a reader sees.
          mainEntity: venueItemList(
            groups.flatMap((group) => group.venues),
            { name: m.schema_city_venue_list({ city: data.cityName }), url: path }
          )
        }),
        // The middle crumb points at the search page: /wedding-venue itself is
        // not a route, and a breadcrumb naming a 404 is worse than a shorter trail.
        breadcrumbList([
          { name: m.breadcrumb_home(), path: '/' },
          { name: m.breadcrumb_venues(), path: '/wedding-venue/search' },
          { name: data.cityName }
        ]),
        faqPage(copy.faq.items)
      )
    )
  );
</script>

<svelte:head>
  <title>{title}</title>
  <meta name="description" content={description} />
  <link rel="canonical" href={canonical} />
  <!-- Svelte parses script contents as raw text, so JSON-LD has to arrive as
       pre-rendered markup rather than as an expression inside the tag. -->
  {@html jsonLd}
</svelte:head>

<main class="min-h-screen bg-background text-slate-900">
  <PublicHeader />

  <section class="border-b border-border bg-white px-5 py-10 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {m.city_hub_eyebrow()}
      </p>
      <h1 class="mt-3 text-4xl font-semibold">
        {m.city_hub_title({ city: data.cityName })}
      </h1>
      <p class="mt-4 max-w-2xl leading-7 text-slate-600">{intro}</p>
    </div>
  </section>

  <!-- The table is the answer to the query this page targets: one row per
       venue with its starting price, grouped by the budget bands couples
       search in. The same figures as the cards below, in the form a
       "berapa harga" query wants. -->
  <section class="mx-auto max-w-7xl px-5 pt-10 lg:px-8">
    <h2 class="text-2xl font-semibold">{copy.table.title}</h2>
    {#each budget as group (group.band.key)}
      <h3 class="mt-8 text-lg font-semibold">{copy.table.bands[group.band.key]}</h3>
      <div class="mt-3 overflow-x-auto rounded-md border border-border bg-white">
        <!-- Fixed widths so the stacked band tables line up as one table. -->
        <table class="w-full min-w-[40rem] table-fixed text-left text-sm">
          <thead class="border-b border-border text-xs uppercase tracking-wider text-slate-500">
            <tr>
              <th class="w-[40%] px-4 py-3 font-semibold">{copy.table.venue}</th>
              <th class="w-[25%] px-4 py-3 font-semibold">{copy.table.district}</th>
              <th class="w-[15%] px-4 py-3 font-semibold">{copy.table.guests}</th>
              <th class="w-[20%] px-4 py-3 text-right font-semibold">{copy.table.price}</th>
            </tr>
          </thead>
          <tbody>
            {#each group.venues as venue (venue.id)}
              <tr class="border-b border-border last:border-0">
                <td class="px-4 py-3 font-medium">
                  <a href={localizeHref(venue.path_url)} class="hover:underline">{venue.name}</a>
                </td>
                <td class="px-4 py-3 text-slate-600">{venue.district}</td>
                <td class="px-4 py-3 text-slate-600">
                  {venue.price_for_total_pax > 0 ? copy.table.guestsFor(venue.price_for_total_pax) : '—'}
                </td>
                <td class="px-4 py-3 text-right font-semibold">
                  {venue.price_start_from ? formatPrice(venue.price_start_from) : copy.table.priceOnRequest}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/each}
  </section>

  <section class="mx-auto max-w-7xl px-5 pt-10 lg:px-8">
    <div class="max-w-3xl space-y-4 leading-7 text-slate-700">
      {#each copy.prose as paragraph, index (index)}
        <p>{paragraph}</p>
      {/each}
    </div>
  </section>

  <div class="mx-auto max-w-7xl px-5 py-10 lg:px-8">
    {#each groups as group (group.stars)}
      <section class="mb-12 last:mb-0">
        <div class="mb-5 flex items-baseline justify-between gap-4 border-b border-border pb-3">
          <h2 class="flex items-center gap-2 text-2xl font-semibold">
            {#if group.stars > 0}
              <StarIcon size={20} fill="currentColor" class="text-amber-500" />
            {/if}
            {heading(group.stars)}
          </h2>
          <p class="text-sm text-slate-600">
            {m.city_hub_group_count({ count: group.venues.length })}
          </p>
        </div>

        <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {#each group.venues as venue (venue.id)}
            <VenueCard {venue} />
          {/each}
        </div>
      </section>
    {/each}

    <section class="mt-12 border-t border-border pt-10">
      <h2 class="text-2xl font-semibold">{copy.faq.title}</h2>
      <div class="mt-6 grid max-w-3xl gap-3">
        {#each copy.faq.items as faq (faq.q)}
          <details class="group rounded-md border border-border bg-white p-5">
            <summary class="cursor-pointer list-none font-semibold marker:hidden">{faq.q}</summary>
            <p class="mt-3 leading-7 text-slate-600">{faq.a}</p>
          </details>
        {/each}
      </div>
      <a
        href={localizeHref('/tour')}
        class="mt-6 inline-flex rounded-md bg-primary px-5 py-3 font-semibold text-primary-foreground hover:opacity-90"
      >
        {copy.faq.ctaLabel}
      </a>
    </section>

    <div class="mt-12 border-t border-border pt-6">
      <a
        href={localizeHref('/wedding-venue/search')}
        class="inline-flex rounded-md border border-input px-5 py-3 font-semibold hover:bg-muted"
      >
        {m.city_hub_all_venues()}
      </a>
    </div>
  </div>

  <PublicFooter />
</main>
