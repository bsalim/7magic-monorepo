<script lang="ts">
  import ArrowLeftIcon from '@lucide/svelte/icons/arrow-left';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import ResponsiveImage from '$lib/components/ResponsiveImage.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale } from '$lib/paraglide/runtime';

  let { data } = $props();

  const showcase = $derived(data.showcase);

  const formattedDate = $derived(
    showcase.showcase_date
      ? new Date(`${showcase.showcase_date}T00:00:00`).toLocaleDateString(
          getLocale() === 'id' ? 'id-ID' : 'en-GB',
          { day: 'numeric', month: 'long', year: 'numeric' }
        )
      : ''
  );
</script>

<svelte:head>
  <title>{showcase.title} | 7Magic</title>
  <meta name="description" content={showcase.body.slice(0, 160) || showcase.title} />
</svelte:head>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />

  <article class="mx-auto max-w-4xl px-5 py-12 lg:px-8">
    <a
      href="/wedding-showcases"
      class="inline-flex items-center gap-2 text-sm font-semibold text-accent-foreground hover:underline"
    >
      <ArrowLeftIcon size={16} />
      {m.showcases_back()}
    </a>

    <h1 class="mt-6 font-display text-3xl font-bold md:text-4xl">{showcase.title}</h1>
    {#if formattedDate}
      <p class="mt-2 text-sm text-muted-foreground">{formattedDate}</p>
    {/if}

    {#if showcase.image}
      <div class="mt-8 overflow-hidden rounded-md bg-secondary">
        <ResponsiveImage
          image={showcase.image}
          sizes="(max-width: 896px) 100vw, 896px"
          loading="eager"
          fetchpriority="high"
          class="w-full object-cover"
        />
      </div>
    {/if}

    {#if showcase.body}
      <div class="mt-8 grid gap-4 text-[15px] leading-8 text-muted-foreground">
        {#each showcase.body.split('\n').filter((line) => line.trim()) as paragraph}
          <p>{paragraph}</p>
        {/each}
      </div>
    {/if}
  </article>

  <PublicFooter />
</main>
