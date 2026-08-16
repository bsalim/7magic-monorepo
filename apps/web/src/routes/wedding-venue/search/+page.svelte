<script lang="ts">
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import VenueCard from '$lib/components/VenueCard.svelte';
  import VenueFilters from '$lib/components/VenueFilters.svelte';
  import { page } from '$app/state';
  import { getLocale, localizeHref } from '$lib/paraglide/runtime';
  import { m } from '$lib/paraglide/messages.js';
  import { pageWindow, paginationHref } from '$lib/pagination';
  import {
    breadcrumbList,
    graph,
    jsonLdScript,
    organization,
    venueItemList,
    webPageNode,
    website
  } from '$lib/seo/schema';

  let { data } = $props();

  const pagination = $derived(data.venues.pagination);
  // The filtered URL, so the described collection is the one actually rendered.
  const pagePath = $derived(page.url.pathname + page.url.search);

  // Reads page.url during render, so the links re-resolve when a filter changes
  // instead of pointing back at the query the page first loaded with.
  const hrefFor = (target: number) => paginationHref(page.url, target);

  // Shared with <title> and the meta description below. Structured data has to
  // agree with what the page shows, and this page's chrome is not translated
  // yet — deriving both from one constant means they localize together when it
  // is, instead of the JSON-LD quietly claiming a name the page never renders.
  const pageTitle = 'Wedding Venue Search';
  const pageDescription =
    'Search curated wedding venues by city, venue name, and hotel star rating.';

  // Positions run across the whole result set rather than restarting each page,
  // so the list on page 3 is not claiming to be the top three venues.
  const jsonLd = $derived(
    jsonLdScript(
      graph(
        organization(),
        website(),
        webPageNode({
          type: 'CollectionPage',
          url: pagePath,
          name: pageTitle,
          description: pageDescription,
          locale: getLocale(),
          mainEntity: venueItemList(data.venues.items, {
            name: m.schema_venue_list(),
            url: pagePath,
            startPosition: (pagination.page - 1) * pagination.page_size + 1
          })
        }),
        breadcrumbList([
          { name: m.breadcrumb_home(), path: '/' },
          { name: m.breadcrumb_venues() }
        ])
      )
    )
  );
</script>

<svelte:head>
  <title>{pageTitle} | 7Magic Wedding</title>
  <meta name="description" content={pageDescription} />
  <!-- Svelte parses script contents as raw text, so JSON-LD has to arrive as
       pre-rendered markup rather than as an expression inside the tag. -->
  {@html jsonLd}
</svelte:head>

<main class="min-h-screen bg-background text-slate-900">
  <PublicHeader />
  <section class="border-b border-border bg-white px-5 py-10 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Wedding venues</p>
      <h1 class="mt-3 text-4xl font-semibold">Find the right package shortlist</h1>
      <p class="mt-4 max-w-2xl leading-7 text-slate-600">
        Filter by city, rating, and venue name.
      </p>
    </div>
  </section>

  <section class="mx-auto grid max-w-7xl gap-6 px-5 py-10 lg:grid-cols-[280px_1fr] lg:px-8">
    <aside>
      <VenueFilters
        q={data.filters.q}
        city={data.filters.city}
        starsMin={data.filters.starsMin}
        stars={data.filters.stars}
      />
    </aside>

    <div>
      <!-- The page indicator lives with the pager below, which is also the only
           place it means anything: a single page of results has nothing to say. -->
      <div class="mb-5 flex items-center justify-between gap-4">
        <p class="text-sm text-slate-600">
          {pagination.total} venues found
        </p>
      </div>

      {#if data.venues.items.length}
        <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {#each data.venues.items as venue}
            <VenueCard {venue} />
          {/each}
        </div>

        <!-- Plain links, not buttons: paging is a navigation, so it stays
             shareable, crawlable, and works with JavaScript unavailable — the
             same reasoning as the tick-box filters. -->
        {#if pagination.total_pages > 1}
          <nav
            class="mt-10 flex flex-col items-center gap-4 border-t border-border pt-6 sm:flex-row sm:justify-between"
            aria-label="Venue search pages"
          >
            <p class="text-sm text-slate-500">
              Page {pagination.page} of {pagination.total_pages}
            </p>

            <div class="flex items-center gap-1">
              {#if pagination.page > 1}
                <a
                  href={hrefFor(pagination.page - 1)}
                  rel="prev"
                  class="rounded-md border border-input px-3 py-2 text-sm font-medium hover:bg-muted"
                >
                  Previous
                </a>
              {:else}
                <span
                  class="rounded-md border border-input px-3 py-2 text-sm font-medium text-slate-400 opacity-50"
                  aria-disabled="true"
                >
                  Previous
                </span>
              {/if}

              {#each pageWindow(pagination.page, pagination.total_pages) as item}
                {#if item === 'gap'}
                  <span class="px-2 text-sm text-slate-500" aria-hidden="true">…</span>
                {:else if item === pagination.page}
                  <span
                    class="rounded-md border border-primary bg-primary px-3 py-2 text-sm font-semibold text-white"
                    aria-current="page"
                  >
                    {item}
                  </span>
                {:else}
                  <a
                    href={hrefFor(item)}
                    class="rounded-md border border-input px-3 py-2 text-sm hover:bg-muted"
                  >
                    {item}
                  </a>
                {/if}
              {/each}

              {#if pagination.page < pagination.total_pages}
                <a
                  href={hrefFor(pagination.page + 1)}
                  rel="next"
                  class="rounded-md border border-input px-3 py-2 text-sm font-medium hover:bg-muted"
                >
                  Next
                </a>
              {:else}
                <span
                  class="rounded-md border border-input px-3 py-2 text-sm font-medium text-slate-400 opacity-50"
                  aria-disabled="true"
                >
                  Next
                </span>
              {/if}
            </div>
          </nav>
        {/if}
      {:else}
        <div class="rounded-md border border-dashed border-input bg-white p-10 text-center">
          <h2 class="text-2xl font-semibold">No venues match these filters</h2>
          <p class="mt-3 text-slate-600">Try a broader city or rating filter.</p>
          <a href={localizeHref('/wedding-venue/search')} class="mt-5 inline-flex rounded-md bg-primary px-5 py-3 font-semibold text-white">
            Reset search
          </a>
        </div>
      {/if}
    </div>
  </section>
  <PublicFooter />
</main>
