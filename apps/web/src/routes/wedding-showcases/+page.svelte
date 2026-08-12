<script lang="ts">
  import ArrowLeftIcon from '@lucide/svelte/icons/arrow-left';
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import ResponsiveImage from '$lib/components/ResponsiveImage.svelte';
  import { buttonVariants } from '$lib/components/ui/button';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale } from '$lib/paraglide/runtime';
  import { cn } from '$lib/utils';
  import { localizeHref } from '$lib/paraglide/runtime';

  let { data } = $props();

  const items = $derived(data.showcases.items);
  const total = $derived(data.showcases.total);
  const perPage = 24;
  const lastPage = $derived(Math.max(1, Math.ceil(total / perPage)));

  function formatDate(value: string | null) {
    if (!value) return '';
    return new Date(`${value}T00:00:00`).toLocaleDateString(
      getLocale() === 'id' ? 'id-ID' : 'en-GB',
      { day: 'numeric', month: 'long', year: 'numeric' }
    );
  }
</script>

<svelte:head>
  <title>{m.showcases_title()} | 7Magic</title>
  <meta name="description" content={m.showcases_subtitle()} />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <section class="mx-auto max-w-7xl px-5 py-14 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">
      {m.nav_showcases()}
    </p>
    <h1 class="mt-3 font-display text-4xl font-bold md:text-5xl">{m.showcases_title()}</h1>
    <p class="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
      {m.showcases_subtitle()}
    </p>

    {#if items.length === 0}
      <p class="mt-12 text-[15px] text-muted-foreground">{m.showcases_empty()}</p>
    {:else}
      <div class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {#each items as showcase (showcase.slug)}
          <a
            href={localizeHref(`/wedding-showcases/${showcase.slug}`)}
            class="group overflow-hidden rounded-md border border-border transition hover:border-brand-gold hover:shadow-lg"
          >
            <div class="aspect-[4/5] overflow-hidden bg-secondary">
              {#if showcase.image}
                <ResponsiveImage
                  image={showcase.image}
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                  class="h-full w-full object-cover transition duration-500 group-hover:scale-105"
                />
              {/if}
            </div>
            <div class="p-5">
              <h2 class="font-display text-lg font-semibold">{showcase.title}</h2>
              {#if showcase.showcase_date}
                <p class="mt-1 text-sm text-muted-foreground">
                  {formatDate(showcase.showcase_date)}
                </p>
              {/if}
            </div>
          </a>
        {/each}
      </div>

      {#if lastPage > 1}
        <div class="mt-12 flex items-center justify-between">
          {#if data.page > 1}
            <a
              href={localizeHref(`/wedding-showcases?page=${data.page - 1}`)}
              class={cn(buttonVariants({ variant: 'outline' }))}
            >
              <ArrowLeftIcon size={16} />
              {data.page - 1}
            </a>
          {:else}
            <span></span>
          {/if}

          <span class="text-sm text-muted-foreground">{data.page} / {lastPage}</span>

          {#if data.page < lastPage}
            <a
              href={localizeHref(`/wedding-showcases?page=${data.page + 1}`)}
              class={cn(buttonVariants({ variant: 'outline' }))}
            >
              {data.page + 1}
              <ArrowRightIcon size={16} />
            </a>
          {:else}
            <span></span>
          {/if}
        </div>
      {/if}
    {/if}
  </section>

  <PublicFooter />
</main>
