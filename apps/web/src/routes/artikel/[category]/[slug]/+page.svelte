<script lang="ts">
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import WhatsappCTA from '$lib/components/WhatsappCTA.svelte';
  import { page } from '$app/state';
  import { getLocale } from '$lib/paraglide/runtime';
  import { m } from '$lib/paraglide/messages.js';
  import {
    articleNode,
    breadcrumbList,
    graph,
    jsonLdScript,
    organization,
    website
  } from '$lib/seo/schema';

  let { data } = $props();
  let article = $derived(data.article);

  // page.url keeps the /en prefix that reroute strips before matching, so the
  // English copy of an article identifies itself by its own URL, not the
  // Indonesian one.
  const jsonLd = $derived(
    jsonLdScript(
      graph(
        organization(),
        website(),
        articleNode(article, page.url.pathname, getLocale()),
        // No category level: /artikel takes only ?page, so a category crumb
        // would link to the unfiltered index. The category rides on the
        // article's articleSection instead.
        breadcrumbList([
          { name: m.breadcrumb_home(), path: '/' },
          { name: m.breadcrumb_articles(), path: '/artikel' },
          { name: article.title }
        ])
      )
    )
  );
</script>

<svelte:head>
  <title>{article.title} | 7Magic Wedding</title>
  <meta name="description" content={article.summary} />
  <!-- Svelte parses script contents as raw text, so JSON-LD has to arrive as
       pre-rendered markup rather than as an expression inside the tag. -->
  {@html jsonLd}
</svelte:head>

<main class="min-h-screen bg-background text-slate-900">
  <PublicHeader />
  <article class="mx-auto grid max-w-7xl gap-8 px-5 py-10 lg:grid-cols-[1fr_340px] lg:px-8">
    <div>
      <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">{article.category}</p>
      <h1 class="mt-3 text-4xl font-semibold leading-tight md:text-5xl">{article.title}</h1>
      <p class="mt-4 max-w-3xl text-lg leading-8 text-slate-600">{article.summary}</p>
      <div class="mt-5 flex flex-wrap gap-3 text-sm text-slate-500">
        <span>{article.author}</span>
        <span>{article.word_count} words</span>
      </div>
      <img src={article.image_url || '/img/wedding-venue-deal-768.jpg'} alt="" class="mt-8 h-[360px] w-full rounded-md object-cover" />

      <div class="article-body mt-8 rounded-md border border-border bg-white p-6 text-lg leading-8 text-slate-700 shadow-sm md:p-8">
        {@html article.content}
      </div>
    </div>

    <aside class="space-y-5">
      <div class="rounded-md border border-border bg-white p-5">
        <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">Topics</p>
        <div class="mt-4 flex flex-wrap gap-2">
          {#each article.topic as topic}
            <span class="rounded-full bg-secondary px-3 py-1 text-sm font-semibold text-accent-foreground">{topic}</span>
          {/each}
        </div>
      </div>
      <WhatsappCTA />
    </aside>
  </article>
  <PublicFooter />
</main>

<style>
  /* Article bodies come from Quill, which wraps every list in <ol> and marks
     the intended type on each item via data-list. Styling the tag alone would
     number the ~2400 items that are meant to be bullets, so key off the
     attribute instead. :global is required because this HTML is injected. */
  :global(.article-body ol),
  :global(.article-body ul) {
    list-style: none;
    margin: 1.25em 0;
    padding: 0;
    counter-reset: article-list;
  }

  :global(.article-body li) {
    position: relative;
    padding-left: 2.5rem;
    margin-bottom: 0.65em;
  }

  /* Ordered items get a filled pink circle carrying the number. */
  :global(.article-body li[data-list='ordered']) {
    counter-increment: article-list;
  }

  :global(.article-body li[data-list='ordered'])::before {
    content: counter(article-list);
    position: absolute;
    left: 0;
    top: 0.15em;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1.65rem;
    height: 1.65rem;
    border-radius: 9999px;
    background: var(--brand-pink);
    color: #ffffff;
    font-size: 0.8rem;
    font-weight: 600;
    line-height: 1;
  }

  /* Bullets get a smaller pink dot, so both share the same visual family. */
  :global(.article-body li[data-list='bullet'])::before {
    content: '';
    position: absolute;
    left: 0.5rem;
    top: 0.72em;
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 9999px;
    background: var(--brand-pink);
  }

  /* Articles imported from Markdown use plain semantic <ul>/<ol> and carry no
     data-list attribute, so the Quill-specific rules above never match them and
     the list-style: none reset would leave them unmarked. These fallbacks give
     both sources the same markers. */
  :global(.article-body ol > li:not([data-list])) {
    counter-increment: article-list;
  }

  :global(.article-body ol > li:not([data-list]))::before {
    content: counter(article-list);
    position: absolute;
    left: 0;
    top: 0.15em;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1.65rem;
    height: 1.65rem;
    border-radius: 9999px;
    background: var(--brand-pink);
    color: #ffffff;
    font-size: 0.8rem;
    font-weight: 600;
    line-height: 1;
  }

  :global(.article-body ul > li:not([data-list]))::before {
    content: '';
    position: absolute;
    left: 0.5rem;
    top: 0.72em;
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 9999px;
    background: var(--brand-pink);
  }

  /* Quill leaves an empty span for its editor UI; it has no place on the site. */
  :global(.article-body .ql-ui) {
    display: none;
  }

  :global(.article-body p) {
    margin-bottom: 1em;
  }

  :global(.article-body h2),
  :global(.article-body h3),
  :global(.article-body h4) {
    margin-top: 1.6em;
    margin-bottom: 0.5em;
    font-weight: 600;
    line-height: 1.3;
    color: var(--foreground);
  }

  :global(.article-body h2) {
    font-size: 1.875rem;
  }

  :global(.article-body h3) {
    font-size: 1.4rem;
  }

  :global(.article-body h4) {
    font-size: 1.2rem;
  }

  :global(.article-body img) {
    max-width: 100%;
    height: auto;
    border-radius: 0.5rem;
    margin: 1.25em 0;
  }

  /* Markdown-imported articles carry comparison tables, which had no styling
     and fell back to cramped browser defaults. */
  :global(.article-body table) {
    width: 100%;
    margin: 1.5em 0;
    border-collapse: collapse;
    font-size: 0.95em;
    line-height: 1.5;
  }

  :global(.article-body th),
  :global(.article-body td) {
    padding: 0.6em 0.8em;
    border: 1px solid var(--border);
    text-align: left;
    vertical-align: top;
  }

  :global(.article-body th) {
    background: var(--secondary);
    font-weight: 600;
    color: var(--foreground);
  }

  /* A wide table must scroll inside itself rather than pushing the page sideways. */
  @media (max-width: 640px) {
    :global(.article-body table) {
      display: block;
      overflow-x: auto;
    }
  }

  :global(.article-body blockquote) {
    margin: 1.25em 0;
    padding-left: 1em;
    border-left: 3px solid var(--primary);
    color: var(--muted-foreground);
  }
</style>
