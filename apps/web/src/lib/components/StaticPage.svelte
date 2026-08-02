<script lang="ts">
  import * as Card from '$lib/components/ui/card';
  import PublicFooter from './PublicFooter.svelte';
  import PublicHeader from './PublicHeader.svelte';

  let {
    eyebrow,
    title,
    body
  }: {
    eyebrow: string;
    title: string;
    body: string[];
  } = $props();
</script>

<main class="min-h-screen bg-background text-foreground">
  <PublicHeader />
  <section class="mx-auto max-w-4xl px-5 py-12 lg:px-8">
    <p class="text-sm font-semibold uppercase tracking-widest text-accent-foreground">{eyebrow}</p>
    <h1 class="mt-3 text-4xl font-semibold md:text-5xl">{title}</h1>
    <Card.Root class="mt-8 gap-0 py-0 shadow-sm">
      <Card.Content class="grid gap-5 p-6 leading-8 text-muted-foreground">
        {#each body as paragraph}
          <p>{paragraph}</p>
        {/each}
      </Card.Content>
    </Card.Root>
  </section>
  <PublicFooter />
</main>
