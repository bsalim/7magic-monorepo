<script lang="ts">
  import SearchIcon from '@lucide/svelte/icons/search';
  import ArticleCard from '$lib/components/ArticleCard.svelte';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { m } from '$lib/paraglide/messages.js';
  import { pageWindow } from '$lib/pagination';

  let { data } = $props();

  const pagination = $derived(data.articles.pagination);
  const filtered = $derived(Boolean(data.category || data.q));

  // Every link on the page goes through here so a filter survives paging and a
  // page number never survives a filter change. basePath is already localized,
  // which keeps an English reader on /en/articles.
  function href(next: { category?: string; q?: string; page?: number }) {
    const params = new URLSearchParams();
    const category = next.category ?? data.category;
    const q = next.q ?? data.q;
    if (category) params.set('category', category);
    if (q) params.set('q', q);
    if (next.page && next.page > 1) params.set('page', String(next.page));
    const query = params.toString();
    return query ? `${data.basePath}?${query}` : data.basePath;
  }
</script>

<svelte:head>
  <title>{m.articles_meta_title()}</title>
  <meta name="description" content={m.articles_meta_description()} />
  <!-- A search result is a view of the index, not a page of its own. -->
  {#if data.q}
    <meta name="robots" content="noindex,follow" />
  {/if}
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
    <div class="mb-8 flex flex-col gap-5">
      <!-- A plain GET form: it works without JavaScript and the result is a URL
           that can be shared. The category rides along as a hidden field. -->
      <form method="GET" action={data.basePath} role="search" class="flex w-full max-w-3xl gap-2">
        {#if data.category}
          <input type="hidden" name="category" value={data.category} />
        {/if}
        <div class="relative flex-1">
          <SearchIcon
            size={18}
            class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            type="search"
            name="q"
            value={data.q}
            maxlength={80}
            placeholder={m.articles_search_placeholder()}
            aria-label={m.articles_search_label()}
            class="h-12 pl-11 text-base"
          />
        </div>
        <Button type="submit" class="h-12 px-6">{m.articles_search_submit()}</Button>
      </form>

      <nav aria-label={m.articles_categories_label()} class="flex flex-wrap gap-2">
        <a
          href={href({ category: '' })}
          aria-current={data.category ? undefined : 'page'}
          class="rounded-full border px-4 py-2 text-sm font-semibold transition {data.category
            ? 'border-input hover:bg-muted'
            : 'border-foreground bg-foreground text-background'}"
        >
          {m.articles_category_all()}
        </a>
        {#each data.categories as category (category.slug)}
          <a
            href={href({ category: category.slug })}
            aria-current={data.category === category.slug ? 'page' : undefined}
            class="rounded-full border px-4 py-2 text-sm font-semibold transition {data.category ===
            category.slug
              ? 'border-foreground bg-foreground text-background'
              : 'border-input hover:bg-muted'}"
          >
            {category.name}
            <span class="ml-1 font-normal opacity-70">{category.count}</span>
          </a>
        {/each}
      </nav>
    </div>

    {#if data.q}
      <p class="mb-6 text-sm text-muted-foreground">
        {m.articles_results_for({ count: pagination.total, query: data.q })}
        <a href={href({ q: '', category: '' })} class="ml-2 font-semibold text-foreground underline">
          {m.articles_clear_filters()}
        </a>
      </p>
    {/if}

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
                href={href({ page: pagination.page - 1 })}
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
                  href={href({ page: item })}
                  class="rounded-md border border-input px-3 py-2 text-sm hover:bg-muted"
                >
                  {item}
                </a>
              {/if}
            {/each}

            {#if pagination.page < pagination.total_pages}
              <a
                href={href({ page: pagination.page + 1 })}
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
    {:else if filtered}
      <div class="rounded-card border border-dashed border-input bg-background p-10 text-center">
        <h2 class="font-display text-2xl font-bold">{m.articles_no_results_title()}</h2>
        <p class="mt-3 text-muted-foreground">{m.articles_no_results_body()}</p>
        <a
          href={href({ q: '', category: '' })}
          class="mt-5 inline-block font-semibold text-foreground underline"
        >
          {m.articles_clear_filters()}
        </a>
      </div>
    {:else}
      <div class="rounded-card border border-dashed border-input bg-background p-10 text-center">
        <h2 class="font-display text-2xl font-bold">{m.articles_empty_title()}</h2>
        <p class="mt-3 text-muted-foreground">{m.articles_empty_body()}</p>
      </div>
    {/if}
  </section>
  <PublicFooter />
</main>
