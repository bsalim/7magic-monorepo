<script lang="ts">
  import ArticleCard from '$lib/components/ArticleCard.svelte';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import SocialMeta from '$lib/components/SocialMeta.svelte';
  import { pageWindow } from '$lib/pagination';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale } from '$lib/paraglide/runtime';
  import { authorProfileJsonLd, canonicalUrl, jsonLdScript } from '$lib/seo/schema';

  let { data } = $props();

  const pagination = $derived(data.articles.pagination);
  // Fiona is the only profile; a second author needs their own copy here.
  const metaTitle = $derived(m.author_fiona_meta_title());
  const metaDescription = $derived(m.author_fiona_meta_description());

  function href(target: number): string {
    return target > 1 ? `${data.basePath}?page=${target}` : data.basePath;
  }

  // Each page of the list is its own view of the catalogue, not a copy of page 1.
  const canonical = $derived(canonicalUrl(href(pagination.page)));
  const jsonLd = $derived(
    jsonLdScript(
      authorProfileJsonLd({
        name: data.name,
        url: data.basePath,
        title: metaTitle,
        description: metaDescription,
        jobTitle: m.author_fiona_role(),
        locale: getLocale()
      })
    )
  );
</script>

<svelte:head>
  <title>{metaTitle}</title>
  <meta name="description" content={metaDescription} />
  <link rel="canonical" href={canonical} />
  {@html jsonLd}
</svelte:head>

<SocialMeta title={metaTitle} description={metaDescription} url={canonical} />

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />
  <section class="border-b border-border bg-background px-5 py-10 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
        {m.author_fiona_role()}
      </p>
      <h1 class="mt-3 font-display text-4xl font-bold">{data.name}</h1>
      <p class="mt-4 max-w-2xl leading-7 text-muted-foreground">{m.author_fiona_bio()}</p>
    </div>
  </section>

  <section class="mx-auto max-w-7xl px-5 py-10 lg:px-8">
    <h2 class="mb-6 text-xl font-semibold">
      {m.author_articles_heading({ name: data.name, count: pagination.total })}
    </h2>
    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      {#each data.articles.items as article (article.id)}
        <ArticleCard {article} />
      {/each}
    </div>

    {#if pagination.total_pages > 1}
      <nav
        class="mt-10 flex flex-wrap items-center justify-center gap-1 border-t border-border pt-6"
        aria-label={m.articles_pagination_label()}
      >
        {#if pagination.page > 1}
          <a
            href={href(pagination.page - 1)}
            rel="prev"
            class="rounded-md border border-input px-3 py-2 text-sm font-medium hover:bg-muted"
          >
            {m.articles_prev()}
          </a>
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
            <a href={href(item)} class="rounded-md border border-input px-3 py-2 text-sm hover:bg-muted">
              {item}
            </a>
          {/if}
        {/each}
        {#if pagination.page < pagination.total_pages}
          <a
            href={href(pagination.page + 1)}
            rel="next"
            class="rounded-md border border-input px-3 py-2 text-sm font-medium hover:bg-muted"
          >
            {m.articles_next()}
          </a>
        {/if}
      </nav>
    {/if}
  </section>
  <PublicFooter />
</main>
