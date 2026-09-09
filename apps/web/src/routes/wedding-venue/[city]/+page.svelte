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
    graph,
    jsonLdScript,
    organization,
    venueItemList,
    webPageNode,
    website
  } from '$lib/seo/schema';
  import { formatMillions } from '$lib/utils';
  import { cityFloorPrice, groupByStars } from '$lib/venue-groups';

  let { data } = $props();

  const groups = $derived(groupByStars(data.venues));
  const floor = $derived(cityFloorPrice(data.venues));

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
        ])
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
