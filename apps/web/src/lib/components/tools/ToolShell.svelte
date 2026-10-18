<script lang="ts">
  import type { Snippet } from 'svelte';
  import ArrowUpRightIcon from '@lucide/svelte/icons/arrow-up-right';
  import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import { localizeHref } from '$lib/paraglide/runtime';

  /**
   * The frame every wedding tool shares: header, hero, the tool itself, then the
   * reading that makes the page worth linking to.
   *
   * The tool is two snippets rather than one so the shell owns the layout: one
   * column on a phone (inputs, then the result right under them), side by side
   * from `md` with the result sticky, so it stays in view while the inputs
   * change. Explainer, FAQ and related reading are server-rendered below it; the
   * FAQ is data, not a snippet, because the same array feeds the FAQPage JSON-LD.
   */

  type Crumb = { name: string; path?: string };
  type Faq = { q: string; a: string };
  type Related = { href: string; title: string };

  interface Props {
    eyebrow: string;
    title: string;
    lead: string;
    /** Unlocalized paths; the last crumb is the current page and has none. */
    crumbs: Crumb[];
    inputs: Snippet;
    result: Snippet;
    /** The lead gate dialog, or anything else that portals out of the layout. */
    gate?: Snippet;
    /** Sections between the tool and the FAQ: worked examples, the explainer. */
    explainer?: Snippet;
    faqs?: Faq[];
    /** Already-localized hrefs: article slugs differ per locale. */
    related?: Related[];
  }

  let {
    eyebrow,
    title,
    lead,
    crumbs,
    inputs,
    result,
    gate,
    explainer,
    faqs = [],
    related = []
  }: Props = $props();
</script>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <section class="relative overflow-hidden bg-secondary px-5 pt-8 pb-12 md:pt-10 md:pb-16 lg:px-8">
    <!-- Two soft gold glows, purely decorative: they give the cream band some
         depth without an image to load before the tool is usable. -->
    <div
      aria-hidden="true"
      class="pointer-events-none absolute -top-32 -right-24 size-[28rem] rounded-full bg-brand-warm-deep/70 blur-3xl"
    ></div>
    <div
      aria-hidden="true"
      class="pointer-events-none absolute -bottom-40 -left-32 size-[24rem] rounded-full bg-brand-gold/10 blur-3xl"
    ></div>

    <div class="relative mx-auto max-w-7xl">
      <nav aria-label={m.vd_breadcrumb()}>
        <ol class="flex flex-wrap items-center gap-1 text-xs text-muted-foreground">
          {#each crumbs as crumb, index (index)}
            <li class="flex items-center gap-1">
              {#if index > 0}<ChevronRightIcon size={13} aria-hidden="true" />{/if}
              {#if crumb.path}
                <a
                  href={localizeHref(crumb.path)}
                  class="rounded-sm transition hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
                >
                  {crumb.name}
                </a>
              {:else}
                <span aria-current="page" class="text-foreground/80">{crumb.name}</span>
              {/if}
            </li>
          {/each}
        </ol>
      </nav>

      <p class="mt-6 text-xs font-semibold tracking-[0.2em] text-brand-gold-hover uppercase">
        {eyebrow}
      </p>
      <h1 class="mt-3 max-w-3xl font-display text-3xl leading-tight font-bold md:text-5xl">
        {title}
      </h1>
      <p class="mt-4 max-w-2xl text-base leading-7 text-muted-foreground md:text-lg md:leading-8">
        {lead}
      </p>
    </div>
  </section>

  <section class="px-5 pb-16 lg:px-8">
    <div
      class="relative mx-auto -mt-6 grid max-w-7xl gap-6 md:-mt-8 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] md:items-start lg:gap-10"
    >
      <div
        class="rounded-2xl border border-border bg-background p-5 shadow-[0_18px_50px_-30px_rgba(138,101,36,0.45)] md:p-7"
      >
        {@render inputs()}
      </div>
      <div class="md:sticky md:top-20">
        {@render result()}
      </div>
    </div>
  </section>

  {@render gate?.()}

  {@render explainer?.()}

  {#if faqs.length}
    <section class="bg-secondary px-5 py-16 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <h2 class="font-display text-2xl font-bold md:text-3xl">{m.tools_faq_title()}</h2>
        <div class="mt-8 grid gap-3">
          {#each faqs as faq (faq.q)}
            <details
              class="group rounded-xl border border-border bg-background p-5 open:shadow-sm md:p-6"
            >
              <summary
                class="flex cursor-pointer list-none items-start justify-between gap-4 rounded-sm font-display text-base font-semibold focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none md:text-lg [&::-webkit-details-marker]:hidden"
              >
                {faq.q}
                <ChevronRightIcon
                  size={18}
                  aria-hidden="true"
                  class="mt-1 shrink-0 text-brand-gold transition group-open:rotate-90"
                />
              </summary>
              <p class="mt-3 text-[15px] leading-7 text-muted-foreground">{faq.a}</p>
            </details>
          {/each}
        </div>
      </div>
    </section>
  {/if}

  {#if related.length}
    <section class="px-5 py-14 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <h2 class="font-display text-2xl font-bold">{m.tools_related_title()}</h2>
        <ul class="mt-6 grid gap-4 md:grid-cols-3">
          {#each related as link (link.href)}
            <li>
              <a
                href={link.href}
                class="group flex h-full items-start justify-between gap-4 rounded-xl border border-border p-5 transition hover:border-brand-gold/60 hover:bg-brand-gold-soft focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
              >
                <span class="font-display text-[15px] leading-6 font-semibold">{link.title}</span>
                <ArrowUpRightIcon
                  size={18}
                  aria-hidden="true"
                  class="mt-0.5 shrink-0 text-brand-gold transition group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                />
              </a>
            </li>
          {/each}
        </ul>
      </div>
    </section>
  {/if}

  <PublicFooter />
</main>
