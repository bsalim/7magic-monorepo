<script lang="ts">
  import ArticleCard from '$lib/components/ArticleCard.svelte';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import { pageWindow } from '$lib/pagination';

  let { data } = $props();

  const pagination = $derived(data.articles.pagination);
</script>

<svelte:head>
  <title>{m.articles_meta_title()}</title>
  <meta name="description" content={m.articles_meta_description()} />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />
  <section class="border-b border-border bg-background px-5 py-10 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {m.articles_eyebrow()}
      </p>
      <h1 class="mt-3 font-display text-4xl font-bold">{m.articles_title()}</h1>
      <p class="mt-4 max-w-2xl leading-7 text-muted-foreground">{m.articles_subtitle()}</p>
    </div>
  </section>

  <section class="mx-auto max-w-7xl px-5 py-10 lg:px-8">
    {#if data.articles.items.length}
      <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {#each data.articles.items as article}
          <ArticleCard {article} />
        {/each}
      </div>

      {#if pagination.total_pages > 1}
        <nav
          class="mt-10 flex flex-col items-center gap-4 border-t border-border pt-6 sm:flex-row sm:justify-between"
          aria-label={m.articles_pagination_label()}
        >
          <p class="text-sm text-muted-foreground">
            {m.articles_page_of({
              page: pagination.page,
              total: pagination.total_pages
            })}
          </p>

          <div class="flex items-center gap-1">
            {#if pagination.page > 1}
              <a
                href="?page={pagination.page - 1}"
                rel="prev"
                class="rounded-md border border-input px-3 py-2 text-sm font-medium hover:bg-muted"
              >
                {m.articles_prev()}
              </a>
            {:else}
              <span
                class="rounded-md border border-input px-3 py-2 text-sm font-medium text-muted-foreground opacity-50"
                aria-disabled="true"
              >
                {m.articles_prev()}
              </span>
            {/if}

            {#each pageWindow(pagination.page, pagination.total_pages) as item}
              {#if item === 'gap'}
                <span class="px-2 text-sm text-muted-foreground" aria-hidden="true">…</span>
              {:else if item === pagination.page}
                <span
                  class="rounded-md border border-foreground bg-foreground px-3 py-2 text-sm font-semibold text-background"
                  aria-current="page"
                >
                  {item}
                </span>
              {:else}
                <a
                  href="?page={item}"
                  class="rounded-md border border-input px-3 py-2 text-sm hover:bg-muted"
                >
                  {item}
                </a>
              {/if}
            {/each}

            {#if pagination.page < pagination.total_pages}
              <a
                href="?page={pagination.page + 1}"
                rel="next"
                class="rounded-md border border-input px-3 py-2 text-sm font-medium hover:bg-muted"
              >
                {m.articles_next()}
              </a>
            {:else}
              <span
                class="rounded-md border border-input px-3 py-2 text-sm font-medium text-muted-foreground opacity-50"
                aria-disabled="true"
              >
                {m.articles_next()}
              </span>
            {/if}
          </div>
        </nav>
      {/if}
    {:else}
      <div class="rounded-card border border-dashed border-input bg-background p-10 text-center">
        <h2 class="font-display text-2xl font-bold">{m.articles_empty_title()}</h2>
        <p class="mt-3 text-muted-foreground">{m.articles_empty_body()}</p>
      </div>
    {/if}
  </section>
  <PublicFooter />
</main>
